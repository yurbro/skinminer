"""Standardized figure-route extractor interface."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
from typing import Iterable

from extractors.common import build_provenance
from extractors.figure.digitize import digitize_figure_curves
from extractors.figure.map_curves import map_curves_to_formulations
from extractors.figure.models import DigitizedEndpointArtifact, FigureMappingArtifact, FigureTriageArtifact, FigureVLMReadingArtifact
from extractors.figure.triage import triage_figure_content
from extractors.figure.vlm_digitize import extract_vlm_readings
from schemas.models import ConditionSpec, ContentAccess, EndpointSpec, EvidenceItem, ExtractorRunContext, Record, RouteDecision
from utils.io import make_record_id, write_jsonl, write_records_csv, write_records_jsonl
from utils.resume import load_jsonl_if_exists, load_record_jsonl_if_exists
from utils.status_panel import ProgressCallback
from utils.units import normalize_amount_per_area, normalize_time_to_hours


def _normalize_note_token(value: str) -> str:
    return "_".join(str(value or "").strip().lower().split())[:80]


def _capture_figure_failures(
    run_context: ExtractorRunContext,
    content_handle: ContentAccess,
    triage_artifact: FigureTriageArtifact,
    endpoints: list[DigitizedEndpointArtifact | dict],
    mappings: list[FigureMappingArtifact],
) -> None:
    """Persist paper-level figure failure notes for later assembly and verification."""

    notes = run_context.shared_state.setdefault("figure_failures_by_paper", {})
    paper_notes = notes.setdefault(content_handle.paper_id, [])

    def add(note: str) -> None:
        if note and note not in paper_notes:
            paper_notes.append(note)

    if triage_artifact.recommended_route != "digitize":
        add(f"figure_triage_route:{triage_artifact.recommended_route}")
    if triage_artifact.why_not_digitizable:
        add(f"figure_why_not_digitizable:{_normalize_note_token(triage_artifact.why_not_digitizable)}")

    endpoint_status_counts: dict[str, int] = defaultdict(int)
    ok_endpoints = 0
    for endpoint_row in endpoints:
        artifact = _coerce_endpoint_artifact(endpoint_row)
        endpoint_status_counts[artifact.status] += 1
        if artifact.status == "ok":
            ok_endpoints += 1
    for status, count in sorted(endpoint_status_counts.items()):
        if status != "ok":
            add(f"figure_digitization_failure:{status}:{count}")
            if status == "fail_missing_plot_context":
                add("figure_plot_context_missing")
    if ok_endpoints == 0:
        add("figure_no_digitized_endpoint")

    mapped = sum(1 for mapping in mappings if mapping.mapping_status == "vision_mapped" and mapping.mapped_formulation_label)
    if mappings and mapped == 0:
        add("figure_mapping_unresolved")


def _build_record_from_mapping(
    endpoint_row: DigitizedEndpointArtifact,
    mapping: FigureMappingArtifact,
    source_record: Record,
    triage_artifact: FigureTriageArtifact,
) -> Record:
    normalized_value, normalized_unit = normalize_amount_per_area(
        endpoint_row.endpoint_value,
        endpoint_row.endpoint_unit,
    )
    evidence_items = list(source_record.evidence_items)
    evidence_items.append(
        EvidenceItem(
            field_name="endpoint",
            modality="figure",
            locator=f"{endpoint_row.figure_id} p.{endpoint_row.page_number}",
            page=endpoint_row.page_number,
            snippet=f"curve_id={endpoint_row.curve_id}; color={endpoint_row.curve_color}; trace_id={endpoint_row.trace_id}",
            source_ref=endpoint_row.overlay_path or endpoint_row.image_path,
            confidence=mapping.mapping_confidence,
        )
    )
    artifact_paths = [
        path
        for path in dict.fromkeys(
            [
                *triage_artifact.selected_image_paths,
                endpoint_row.image_path,
                endpoint_row.crop_path,
                endpoint_row.mask_path,
                endpoint_row.overlay_path,
                mapping.mapping_image_path,
            ]
        )
        if path
    ]
    source_pages = sorted({*triage_artifact.selected_pages, *source_record.provenance.source_pages})
    conditions = _figure_grounded_conditions(
        source_record,
        triage_artifact,
        endpoint_time=endpoint_row.endpoint_time,
        endpoint_time_unit=endpoint_row.endpoint_time_unit,
    )
    evidence_items.extend(_figure_condition_evidence_items(conditions, source_record, triage_artifact))
    return Record(
        record_id=make_record_id(source_record.paper_id, "figure", source_record.formulation.label, suffix=endpoint_row.curve_id),
        paper_id=source_record.paper_id,
        doi=source_record.doi,
        route="figure",
        route_confidence=source_record.route_confidence,
        extractor_confidence=triage_artifact.confidence,
        mapping_confidence=mapping.mapping_confidence,
        study_type=source_record.study_type,
        device=source_record.device,
        barrier=source_record.barrier,
        formulation=source_record.formulation,
        endpoint=EndpointSpec(
            field_name="amount",
            kind=endpoint_row.y_kind or "unknown",
            value=endpoint_row.endpoint_value,
            unit=endpoint_row.endpoint_unit,
            time_value=endpoint_row.endpoint_time,
            time_unit=endpoint_row.endpoint_time_unit,
            normalized_value=normalized_value,
            normalized_unit=normalized_unit,
        ),
        conditions=conditions,
        evidence_items=evidence_items,
        provenance=build_provenance(
            extractor_name="figure",
            content_handle=ContentAccess(
                paper_id=source_record.paper_id,
                doi=source_record.doi,
                title=triage_artifact.title,
                preferred_format="pdf",
                available_formats=["pdf"],
                local_paths={"pdf": triage_artifact.pdf_path},
                status="downloaded",
            ),
            route_decision=RouteDecision(
                paper_id=source_record.paper_id,
                doi=source_record.doi,
                title=triage_artifact.title,
                route="figure",
                route_confidence=source_record.route_confidence,
                anchor_evidence=list(source_record.provenance.metadata.get("route_anchor_evidence", [])),
                raw_labels=dict(source_record.provenance.metadata.get("route_raw_labels", {})),
            ),
            source_format="pdf",
            source_path=triage_artifact.pdf_path,
            source_pages=source_pages,
            artifact_paths=artifact_paths,
            metadata={
                "figure_id": triage_artifact.figure_id,
                "triage_trace_id": triage_artifact.trace_id,
                "curve_trace_id": endpoint_row.trace_id,
                "curve_id": endpoint_row.curve_id,
                "mapping_rationale": mapping.mapping_rationale,
                "mapping_trace_id": mapping.trace_id,
                "mapping_status": mapping.mapping_status,
                "mapping_label_space_status": mapping.mapping_label_space_status,
                "mapping_image_path": mapping.mapping_image_path,
                "allowed_formulation_labels": mapping.allowed_formulation_labels,
                "source_table_record_ids": mapping.source_table_record_ids,
                "figure_condition_grounding": "figure_context_only",
                "triage_retry_triggered": triage_artifact.triage_retry_triggered,
                "triage_retry_reason": triage_artifact.triage_retry_reason,
                "triage_retry_source_trace_id": triage_artifact.triage_retry_source_trace_id,
                "triage_retry_source_figure_id": triage_artifact.triage_retry_source_figure_id,
                "triage_retry_source_page": triage_artifact.triage_retry_source_page,
                "triage_retry_candidate_pages": triage_artifact.triage_retry_candidate_pages,
                "triage_retry_candidate_page": triage_artifact.triage_retry_candidate_page,
                "triage_retry_result": triage_artifact.triage_retry_result,
                "page_scores": triage_artifact.page_scores,
            },
        ),
        source_notes=source_record.source_notes + [
            "Figure endpoint built from triage + CV digitization + curve mapping.",
            f"figure_trace_id={triage_artifact.trace_id}",
            f"curve_trace_id={endpoint_row.trace_id}",
        ],
    )


def _coerce_endpoint_artifact(value: DigitizedEndpointArtifact | dict) -> DigitizedEndpointArtifact:
    return value if isinstance(value, DigitizedEndpointArtifact) else DigitizedEndpointArtifact.model_validate(value)


def _coerce_vlm_artifact(value: FigureVLMReadingArtifact | dict) -> FigureVLMReadingArtifact:
    return value if isinstance(value, FigureVLMReadingArtifact) else FigureVLMReadingArtifact.model_validate(value)


def _figure_vlm_enabled(run_context: ExtractorRunContext) -> bool:
    return bool(run_context.shared_state.get("figure_vlm_enabled", True))


def _normalized_unit(value: str) -> str:
    return "".join(str(value or "").strip().lower().split())


def _relative_delta_pct(
    left_value: float | None,
    left_unit: str,
    right_value: float | None,
    right_unit: str,
) -> float | None:
    if left_value is None or right_value is None:
        return None
    left_normalized_value, left_normalized_unit = normalize_amount_per_area(left_value, left_unit)
    right_normalized_value, right_normalized_unit = normalize_amount_per_area(right_value, right_unit)

    comparable_left = left_normalized_value if left_normalized_value is not None else left_value
    comparable_right = right_normalized_value if right_normalized_value is not None else right_value
    comparable_left_unit = left_normalized_unit or _normalized_unit(left_unit)
    comparable_right_unit = right_normalized_unit or _normalized_unit(right_unit)

    if comparable_left_unit != comparable_right_unit:
        return None

    denominator = max(abs(float(comparable_right)), 1e-6)
    return abs(float(comparable_left) - float(comparable_right)) / denominator * 100.0


def _condition_context_fragments(source_record: Record) -> list[str]:
    metadata = source_record.provenance.metadata
    fragments = [
        source_record.provenance.route_notes,
        source_record.barrier,
        *source_record.source_notes,
        *(item.snippet for item in source_record.evidence_items if item.snippet),
        *(item.locator for item in source_record.evidence_items if item.locator),
    ]
    raw_labels = metadata.get("route_raw_labels", {})
    if isinstance(raw_labels, dict):
        for key in (
            "where_endpoint",
            "endpoint_carrier_snippet",
            "formulation_carrier_snippet",
            "barrier_name_raw",
            "notes",
        ):
            value = raw_labels.get(key)
            if value:
                fragments.append(str(value))
    for item in metadata.get("route_anchor_evidence", []):
        if isinstance(item, dict):
            for key in ("snippet", "locator"):
                value = item.get(key)
                if value:
                    fragments.append(str(value))
    return fragments


def _normalize_subplot(value: str) -> str:
    return (value or "").strip().upper()[:1]


def _infer_membrane_from_subplot(source_record: Record, triage_artifact: FigureTriageArtifact) -> tuple[str, str]:
    subplot = _normalize_subplot(triage_artifact.subplot)
    if not subplot:
        return "", ""
    text = " ".join(_condition_context_fragments(source_record)).lower()
    direct_patterns = {
        "A": [("human skin", "human skin", "human")],
        "B": [("porcine skin", "porcine skin", "porcine"), ("porcine ear skin", "porcine ear skin", "porcine")],
        "C": [("silicone membrane", "silicone membrane", "synthetic"), ("silicone", "silicone membrane", "synthetic")],
        "D": [("pampa", "PAMPA", "synthetic"), ("parallel artificial membrane", "PAMPA", "synthetic")],
    }
    for phrase, membrane_type, membrane_source in direct_patterns.get(subplot, []):
        if re.search(rf"{re.escape(phrase)}\s*\({re.escape(subplot.lower())}\)", text):
            return membrane_type, membrane_source
        if re.search(rf"{re.escape(phrase)}\s*\({re.escape(subplot)}\)", text, flags=re.IGNORECASE):
            return membrane_type, membrane_source
    return "", ""


def _infer_dose_from_subplot(source_record: Record, triage_artifact: FigureTriageArtifact) -> tuple[str, str]:
    subplot = _normalize_subplot(triage_artifact.subplot)
    if not subplot:
        return "", ""
    text = " ".join(_condition_context_fragments(source_record)).lower()
    if subplot == "D" and "pampa" in text:
        match = re.search(r"dosed\s+at\s+([0-9.]+\s*(?:u|µ|μ)?l\s*/?\s*cm\s*\^?2)", text, flags=re.IGNORECASE)
        if match:
            return "finite", match.group(1).replace("μ", "u").replace("µ", "u")
    figure3_match = re.search(
        rf"([0-9.]+\s*(?:u|µ|μ)?l)\s*\([^)]*{re.escape(subplot.lower())}[^)]*\)",
        text,
        flags=re.IGNORECASE,
    )
    if figure3_match:
        return "finite", figure3_match.group(1).replace("μ", "u").replace("µ", "u")
    return "", ""


def _figure_grounded_conditions(
    source_record: Record,
    triage_artifact: FigureTriageArtifact,
    *,
    endpoint_time: float | None,
    endpoint_time_unit: str,
) -> ConditionSpec:
    """Build figure-record conditions without copying table-specific context blindly."""

    membrane_type, membrane_source = _infer_membrane_from_subplot(source_record, triage_artifact)
    dose_type, dose_amount = _infer_dose_from_subplot(source_record, triage_artifact)
    notes: list[str] = []
    if membrane_type or dose_amount:
        notes.append(
            "figure_condition_grounded:"
            + ";".join(
                part
                for part in (
                    f"subplot={triage_artifact.subplot}" if triage_artifact.subplot else "",
                    f"membrane_type={membrane_type}" if membrane_type else "",
                    f"dose_amount={dose_amount}" if dose_amount else "",
                )
                if part
            )
        )

    return ConditionSpec(
        temperature_c=source_record.conditions.temperature_c,
        duration_h=normalize_time_to_hours(endpoint_time, endpoint_time_unit),
        diffusion_area_cm2=source_record.conditions.diffusion_area_cm2,
        receptor_volume_ml=source_record.conditions.receptor_volume_ml,
        membrane_type=membrane_type,
        membrane_source=membrane_source,
        dose_type=dose_type,
        dose_amount=dose_amount,
        replicate_count=source_record.conditions.replicate_count,
        notes=notes,
    )


def _condition_value_pairs(conditions: ConditionSpec) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if conditions.membrane_type:
        pairs.append(("membrane_type", conditions.membrane_type))
    if conditions.membrane_source:
        pairs.append(("membrane_source", conditions.membrane_source))
    if conditions.membrane_thickness_um is not None:
        pairs.append(("membrane_thickness_um", f"{conditions.membrane_thickness_um:g} um"))
    if conditions.receptor_medium:
        pairs.append(("receptor_medium", conditions.receptor_medium))
    if conditions.dose_type:
        pairs.append(("dose_type", conditions.dose_type))
    if conditions.dose_amount:
        pairs.append(("dose_amount", conditions.dose_amount))
    return pairs


def _figure_condition_evidence_items(
    conditions: ConditionSpec,
    source_record: Record,
    triage_artifact: FigureTriageArtifact,
) -> list[EvidenceItem]:
    pairs = _condition_value_pairs(conditions)
    if not pairs:
        return []
    context = " ".join(_condition_context_fragments(source_record))
    context = " ".join(context.split())[:520]
    locator_parts = [str(triage_artifact.figure_id or ""), f"p.{triage_artifact.page_number}"]
    if triage_artifact.subplot:
        locator_parts.append(f"subplot {triage_artifact.subplot}")
    locator = " ".join(part for part in locator_parts if part).strip()
    return [
        EvidenceItem(
            field_name=field_name,
            modality="figure",
            locator=locator,
            page=triage_artifact.page_number,
            snippet=context,
            source_ref=triage_artifact.selected_image_path or triage_artifact.pdf_path,
            confidence=0.62,
        )
        for field_name, _value in pairs
    ]


def _annotate_record_with_vlm(
    record: Record,
    *,
    vlm_reading: FigureVLMReadingArtifact,
    reconciliation_status: str,
    delta_pct: float | None = None,
) -> Record:
    annotated = record.model_copy(deep=True)
    annotated.provenance.metadata["figure_extraction_method"] = reconciliation_status
    annotated.provenance.metadata["vlm_trace_id"] = vlm_reading.trace_id
    annotated.provenance.metadata["vlm_model"] = vlm_reading.vlm_model
    annotated.provenance.metadata["vlm_prompt_asset_id"] = vlm_reading.vlm_prompt_asset_id
    annotated.provenance.metadata["vlm_prompt_version"] = vlm_reading.vlm_prompt_version
    annotated.provenance.metadata["vlm_readability_status"] = vlm_reading.readability_status
    annotated.provenance.metadata["vlm_quality_flags"] = list(vlm_reading.quality_flags)
    annotated.provenance.metadata["vlm_series_marker_raw"] = vlm_reading.series_marker_raw
    annotated.provenance.metadata["vlm_series_label_raw"] = vlm_reading.series_label_raw
    annotated.provenance.metadata["vlm_series_rank_hint"] = vlm_reading.series_rank_hint
    annotated.provenance.metadata["vlm_grounding_status"] = vlm_reading.grounding_status
    annotated.provenance.metadata["vlm_candidate_tier"] = vlm_reading.candidate_tier
    annotated.provenance.metadata["vlm_subplot_lock_failed"] = vlm_reading.subplot_lock_failed
    annotated.provenance.metadata["vlm_crop_width_px"] = vlm_reading.crop_width_px
    annotated.provenance.metadata["vlm_crop_height_px"] = vlm_reading.crop_height_px
    annotated.provenance.metadata["vlm_source_render_dpi"] = vlm_reading.source_render_dpi
    if delta_pct is not None:
        annotated.provenance.metadata["cv_vlm_delta_pct"] = round(delta_pct, 3)
    note = (
        f"figure_value_reconciliation={reconciliation_status}; "
        f"vlm_marker={vlm_reading.series_marker_raw}; "
        f"vlm_series_label={vlm_reading.series_label_raw}; "
        f"vlm_grounded_label={vlm_reading.formulation_label or vlm_reading.legend_label_raw}; "
        f"vlm_grounding_status={vlm_reading.grounding_status}; "
        f"vlm_value={vlm_reading.endpoint_value} {vlm_reading.endpoint_unit}; "
        f"vlm_confidence={vlm_reading.confidence}"
    )
    if delta_pct is not None:
        note += f"; cv_vlm_delta_pct={delta_pct:.3f}"
    annotated.source_notes.append(note)
    return annotated


def _build_record_from_vlm_reading(
    vlm_reading: FigureVLMReadingArtifact,
    source_record: Record,
    triage_artifact: FigureTriageArtifact,
) -> Record:
    normalized_value, normalized_unit = normalize_amount_per_area(
        vlm_reading.endpoint_value,
        vlm_reading.endpoint_unit,
    )
    evidence_items = list(source_record.evidence_items)
    evidence_items.append(
        EvidenceItem(
            field_name="endpoint",
            modality="figure",
            locator=f"{triage_artifact.figure_id} p.{vlm_reading.page_number or triage_artifact.page_number}",
            page=vlm_reading.page_number or triage_artifact.page_number,
            snippet=(
                f"vlm_label={vlm_reading.formulation_label}; legend={vlm_reading.legend_label_raw}; "
                f"quality_flags={','.join(vlm_reading.quality_flags)}"
            ),
            source_ref=vlm_reading.crop_path or vlm_reading.image_path,
            confidence=vlm_reading.confidence,
        )
    )
    artifact_paths = [
        path
        for path in dict.fromkeys(
            [
                *triage_artifact.selected_image_paths,
                vlm_reading.image_path,
                vlm_reading.crop_path,
            ]
        )
        if path
    ]
    source_pages = sorted({*triage_artifact.selected_pages, *source_record.provenance.source_pages})
    conditions = _figure_grounded_conditions(
        source_record,
        triage_artifact,
        endpoint_time=vlm_reading.endpoint_time,
        endpoint_time_unit=vlm_reading.endpoint_time_unit,
    )
    evidence_items.extend(_figure_condition_evidence_items(conditions, source_record, triage_artifact))
    return Record(
        record_id=make_record_id(
            source_record.paper_id,
            "figure",
            source_record.formulation.label,
            suffix=f"vlm_{vlm_reading.formulation_label or vlm_reading.legend_label_raw}",
        ),
        paper_id=source_record.paper_id,
        doi=source_record.doi,
        route="figure",
        route_confidence=source_record.route_confidence,
        extractor_confidence=source_record.extractor_confidence,
        mapping_confidence=vlm_reading.confidence,
        study_type=source_record.study_type,
        device=source_record.device,
        barrier=source_record.barrier,
        formulation=source_record.formulation,
        endpoint=EndpointSpec(
            field_name="amount",
            kind=(
                triage_artifact.y_kind
                if triage_artifact.y_kind and triage_artifact.y_kind != "unknown"
                else (source_record.endpoint.kind if source_record.endpoint.kind != "unknown" else "amount_per_area")
            ),
            value=vlm_reading.endpoint_value,
            unit=vlm_reading.endpoint_unit,
            time_value=vlm_reading.endpoint_time,
            time_unit=vlm_reading.endpoint_time_unit,
            normalized_value=normalized_value,
            normalized_unit=normalized_unit,
        ),
        conditions=conditions,
        evidence_items=evidence_items,
        provenance=build_provenance(
            extractor_name="figure",
            content_handle=ContentAccess(
                paper_id=source_record.paper_id,
                doi=source_record.doi,
                title=triage_artifact.title,
                preferred_format="pdf",
                available_formats=["pdf"],
                local_paths={"pdf": triage_artifact.pdf_path},
                status="downloaded",
            ),
            route_decision=RouteDecision(
                paper_id=source_record.paper_id,
                doi=source_record.doi,
                title=triage_artifact.title,
                route="figure",
                route_confidence=source_record.route_confidence,
                anchor_evidence=list(source_record.provenance.metadata.get("route_anchor_evidence", [])),
                raw_labels=dict(source_record.provenance.metadata.get("route_raw_labels", {})),
            ),
            source_format="pdf",
            source_path=triage_artifact.pdf_path,
            source_pages=source_pages,
            artifact_paths=artifact_paths,
            metadata={
                "figure_id": triage_artifact.figure_id,
                "triage_trace_id": triage_artifact.trace_id,
                "figure_extraction_method": "vlm_only",
                "vlm_trace_id": vlm_reading.trace_id,
                "vlm_model": vlm_reading.vlm_model,
                "vlm_prompt_asset_id": vlm_reading.vlm_prompt_asset_id,
                "vlm_prompt_version": vlm_reading.vlm_prompt_version,
                "vlm_readability_status": vlm_reading.readability_status,
                "vlm_quality_flags": list(vlm_reading.quality_flags),
                "vlm_series_marker_raw": vlm_reading.series_marker_raw,
                "vlm_series_label_raw": vlm_reading.series_label_raw,
                "vlm_series_rank_hint": vlm_reading.series_rank_hint,
                "vlm_grounding_status": vlm_reading.grounding_status,
                "vlm_candidate_tier": vlm_reading.candidate_tier,
                "vlm_subplot_lock_failed": vlm_reading.subplot_lock_failed,
                "vlm_crop_width_px": vlm_reading.crop_width_px,
                "vlm_crop_height_px": vlm_reading.crop_height_px,
                "vlm_source_render_dpi": vlm_reading.source_render_dpi,
                "figure_condition_grounding": "figure_context_only",
                "triage_retry_triggered": triage_artifact.triage_retry_triggered,
                "triage_retry_reason": triage_artifact.triage_retry_reason,
                "triage_retry_source_trace_id": triage_artifact.triage_retry_source_trace_id,
                "triage_retry_source_figure_id": triage_artifact.triage_retry_source_figure_id,
                "triage_retry_source_page": triage_artifact.triage_retry_source_page,
                "triage_retry_candidate_pages": triage_artifact.triage_retry_candidate_pages,
                "triage_retry_candidate_page": triage_artifact.triage_retry_candidate_page,
                "triage_retry_result": triage_artifact.triage_retry_result,
                "page_scores": triage_artifact.page_scores,
            },
        ),
        source_notes=source_record.source_notes
        + [
            "Figure endpoint built from locked-subplot VLM value extraction.",
            f"figure_trace_id={triage_artifact.trace_id}",
            f"vlm_trace_id={vlm_reading.trace_id}",
            f"vlm_marker={vlm_reading.series_marker_raw}",
            f"vlm_series_label={vlm_reading.series_label_raw}",
            f"vlm_grounding_status={vlm_reading.grounding_status}",
        ],
    )


def _prefer_retry_vlm_final(triage_artifact: FigureTriageArtifact, vlm_reading: FigureVLMReadingArtifact) -> bool:
    if not (
        triage_artifact.triage_retry_triggered
        and triage_artifact.triage_retry_reason == "calibration_curve_not_target"
        and triage_artifact.triage_retry_result == "recovered_digitizable"
    ):
        return False
    unique_source_labels = {label for label in vlm_reading.source_label_space if label}
    return (
        len(unique_source_labels) == 1
        and vlm_reading.readability_status == "readable"
        and vlm_reading.grounding_status in {"source_label_space", "figure_label_space"}
        and (vlm_reading.confidence or 0.0) >= 0.85
        and vlm_reading.endpoint_value is not None
        and vlm_reading.endpoint_time is not None
    )


def _reconcile_direct_figure_records(
    content_handle: ContentAccess,
    triage_artifact: FigureTriageArtifact,
    digitized_endpoints: list[DigitizedEndpointArtifact | dict],
    mappings: list[FigureMappingArtifact],
    table_records: list[Record],
    vlm_artifacts: list[FigureVLMReadingArtifact | dict],
) -> tuple[list[Record], list[FigureVLMReadingArtifact]]:
    table_lookup = {(record.paper_id, record.formulation.label): record for record in table_records if record.formulation.label}
    mapping_lookup = {(mapping.paper_id, mapping.curve_id): mapping for mapping in mappings}

    cv_candidates: dict[str, tuple[Record, DigitizedEndpointArtifact, FigureMappingArtifact]] = {}
    for endpoint_row in digitized_endpoints:
        endpoint_artifact = _coerce_endpoint_artifact(endpoint_row)
        if endpoint_artifact.status != "ok":
            continue
        mapping = mapping_lookup.get((endpoint_artifact.paper_id, endpoint_artifact.curve_id))
        if not mapping or not mapping.mapped_formulation_label:
            continue
        source_record = table_lookup.get((content_handle.paper_id, mapping.mapped_formulation_label))
        if source_record is None:
            continue
        record = _build_record_from_mapping(endpoint_artifact, mapping, source_record, triage_artifact)
        existing = cv_candidates.get(mapping.mapped_formulation_label)
        if existing is None or float(mapping.mapping_confidence or 0.0) > float(existing[2].mapping_confidence or 0.0):
            cv_candidates[mapping.mapped_formulation_label] = (record, endpoint_artifact, mapping)

    vlm_candidates: dict[str, FigureVLMReadingArtifact] = {}
    updated_vlm_artifacts: list[FigureVLMReadingArtifact] = []
    readable_statuses = {"readable", "partially_readable"}
    for artifact_row in vlm_artifacts:
        artifact = _coerce_vlm_artifact(artifact_row)
        if artifact.reconciliation_status == "pending" and artifact.readability_status == "unreadable":
            artifact = artifact.model_copy(update={"reconciliation_status": "unreadable"})
        if (
            artifact.formulation_label
            and artifact.endpoint_value is not None
            and artifact.readability_status in readable_statuses
        ):
            existing = vlm_candidates.get(artifact.formulation_label)
            if existing is None or float(artifact.confidence or 0.0) > float(existing.confidence or 0.0):
                vlm_candidates[artifact.formulation_label] = artifact
        updated_vlm_artifacts.append(artifact)

    final_records: list[Record] = []
    used_vlm_trace_ids: set[str] = set()
    cv_labels = set(cv_candidates)
    vlm_labels = set(vlm_candidates)

    for label in sorted(cv_labels | vlm_labels):
        cv_entry = cv_candidates.get(label)
        vlm_entry = vlm_candidates.get(label)
        source_record = table_lookup.get((content_handle.paper_id, label))

        if cv_entry and vlm_entry:
            cv_record, _endpoint_artifact, _mapping = cv_entry
            delta_pct = _relative_delta_pct(
                cv_record.endpoint.value,
                cv_record.endpoint.unit,
                vlm_entry.endpoint_value,
                vlm_entry.endpoint_unit,
            )
            if delta_pct is not None and delta_pct <= 15.0:
                final_records.append(
                    _annotate_record_with_vlm(
                        cv_record,
                        vlm_reading=vlm_entry,
                        reconciliation_status="cv_vlm_agree",
                        delta_pct=delta_pct,
                    )
                )
                used_vlm_trace_ids.add(vlm_entry.trace_id)
                continue
            if source_record is not None and _prefer_retry_vlm_final(triage_artifact, vlm_entry):
                vlm_record = _build_record_from_vlm_reading(vlm_entry, source_record, triage_artifact)
                vlm_record.provenance.metadata["figure_extraction_method"] = "vlm_retry_cv_disagreement"
                vlm_record.provenance.metadata["cv_vlm_delta_pct"] = round(delta_pct, 3) if delta_pct is not None else None
                vlm_record.source_notes.append(
                    "figure_value_reconciliation=vlm_retry_cv_disagreement; "
                    "calibration_retry_single_source_label; "
                    f"cv_value={cv_record.endpoint.value} {cv_record.endpoint.unit}; "
                    f"vlm_value={vlm_entry.endpoint_value} {vlm_entry.endpoint_unit}"
                )
                final_records.append(vlm_record)
                used_vlm_trace_ids.add(vlm_entry.trace_id)
                continue
            used_vlm_trace_ids.add(vlm_entry.trace_id)
            continue

        if cv_entry:
            final_records.append(cv_entry[0])
            continue

        if vlm_entry and source_record is not None:
            final_records.append(_build_record_from_vlm_reading(vlm_entry, source_record, triage_artifact))
            used_vlm_trace_ids.add(vlm_entry.trace_id)
            continue

        if vlm_entry and source_record is None:
            used_vlm_trace_ids.add(vlm_entry.trace_id)

    finalized_vlm_artifacts: list[FigureVLMReadingArtifact] = []
    for artifact in updated_vlm_artifacts:
        if artifact.trace_id in used_vlm_trace_ids:
            label = artifact.formulation_label
            if label in cv_candidates and label in vlm_candidates:
                cv_record = cv_candidates[label][0]
                delta_pct = _relative_delta_pct(
                    cv_record.endpoint.value,
                    cv_record.endpoint.unit,
                    artifact.endpoint_value,
                    artifact.endpoint_unit,
                )
                if delta_pct is not None and delta_pct <= 15.0:
                    artifact = artifact.model_copy(
                        update={
                            "reconciliation_status": "cv_vlm_agree",
                            "cv_vlm_delta_pct": round(delta_pct, 3),
                            "vlm_used_as_final": False,
                        }
                    )
                else:
                    vlm_used_as_final = _prefer_retry_vlm_final(triage_artifact, artifact)
                    artifact = artifact.model_copy(
                        update={
                            "reconciliation_status": "cv_vlm_disagreement",
                            "cv_vlm_delta_pct": round(delta_pct, 3) if delta_pct is not None else None,
                            "vlm_used_as_final": vlm_used_as_final,
                        }
                    )
            else:
                artifact = artifact.model_copy(
                    update={
                        "reconciliation_status": "vlm_only",
                        "vlm_used_as_final": True,
                    }
                )
        elif artifact.readability_status == "unreadable":
            artifact = artifact.model_copy(update={"reconciliation_status": "unreadable", "vlm_used_as_final": False})
        elif artifact.formulation_label and (content_handle.paper_id, artifact.formulation_label) not in table_lookup:
            artifact = artifact.model_copy(update={"reconciliation_status": "no_source_record", "vlm_used_as_final": False})
        else:
            artifact = artifact.model_copy(update={"reconciliation_status": "cv_only", "vlm_used_as_final": False})
        finalized_vlm_artifacts.append(artifact)

    return final_records, finalized_vlm_artifacts


def extract(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    policy: object | None,
    run_context: ExtractorRunContext,
) -> list[Record]:
    """Extract figure-route candidate records for a single paper."""

    if route_decision.route not in {"figure", "mixed"}:
        return []

    table_records_by_paper = run_context.shared_state.get("table_records_by_paper", {})
    table_records = list(table_records_by_paper.get(content_handle.paper_id, []))
    if not table_records:
        return []

    triage_artifact = triage_figure_content(content_handle, route_decision, run_context)
    digitized = digitize_figure_curves([triage_artifact], run_context)
    vlm_artifacts = []
    if _figure_vlm_enabled(run_context):
        vlm_artifacts = extract_vlm_readings(triage_artifact, digitized["endpoints"], table_records, run_context)
    mappings = map_curves_to_formulations([triage_artifact], digitized["endpoints"], table_records, run_context)
    records, _resolved_vlm_artifacts = _reconcile_direct_figure_records(
        content_handle,
        triage_artifact,
        digitized["endpoints"],
        mappings,
        table_records,
        vlm_artifacts,
    )
    return records


def extract_batch(
    content_route_pairs: Iterable[tuple[ContentAccess, RouteDecision]],
    policy: object | None,
    run_context: ExtractorRunContext,
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    triage_jsonl: str | Path | None = None,
    digitized_curves_jsonl: str | Path | None = None,
    digitized_endpoints_jsonl: str | Path | None = None,
    vlm_jsonl: str | Path | None = None,
    mapping_jsonl: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
    checkpoint_every: int = 25,
) -> list[Record]:
    """Extract figure-route records across a batch of routed papers."""

    checkpoint_every = max(1, checkpoint_every)
    existing_triage_rows = load_jsonl_if_exists(triage_jsonl)
    existing_curves = load_jsonl_if_exists(digitized_curves_jsonl)
    existing_endpoints = load_jsonl_if_exists(digitized_endpoints_jsonl)
    existing_mappings = load_jsonl_if_exists(mapping_jsonl)
    processed_paper_ids = {str(row.get("paper_id", "") or "") for row in existing_triage_rows}
    existing_records = load_record_jsonl_if_exists(output_jsonl)
    records_by_paper: dict[str, list[Record]] = defaultdict(list)
    for record in existing_records:
        records_by_paper[record.paper_id].append(record)

    triage_rows = list(existing_triage_rows)
    all_curves = list(existing_curves)
    all_endpoints = list(existing_endpoints)
    all_vlm = list(load_jsonl_if_exists(vlm_jsonl))
    all_mappings = list(existing_mappings)

    table_records_by_paper = run_context.shared_state.get("table_records_by_paper", {})
    selected_pairs = [
        (content_handle, route_decision)
        for content_handle, route_decision in content_route_pairs
        if route_decision.route in {"figure", "mixed"}
    ]
    completed_before = sum(1 for content_handle, _ in selected_pairs if content_handle.paper_id in processed_paper_ids)
    if progress_callback and completed_before:
        progress_callback(completed_before, "resume", f"loaded={completed_before}")

    remaining_pairs = [(content_handle, route_decision) for content_handle, route_decision in selected_pairs if content_handle.paper_id not in processed_paper_ids]
    for remaining_index, (content_handle, route_decision) in enumerate(remaining_pairs, start=1):
        completed_so_far = completed_before + remaining_index - 1
        current_item = content_handle.paper_id or content_handle.doi or route_decision.title[:60] or f"paper_{completed_so_far + 1}"
        if progress_callback:
            progress_callback(completed_so_far, current_item, "extracting figure evidence")
        table_records = list(table_records_by_paper.get(content_handle.paper_id, []))
        if not table_records:
            if progress_callback:
                progress_callback(completed_so_far + 1, current_item, "skipped:no_table_records")
            continue

        triage_artifact = triage_figure_content(content_handle, route_decision, run_context)
        triage_rows.append(triage_artifact.model_dump(mode="json"))
        digitized = digitize_figure_curves([triage_artifact], run_context)
        all_curves.extend(curve.model_dump(mode="json") for curve in digitized["curves"])
        all_endpoints.extend(endpoint.model_dump(mode="json") for endpoint in digitized["endpoints"])
        vlm_artifacts = []
        if _figure_vlm_enabled(run_context):
            vlm_artifacts = extract_vlm_readings(triage_artifact, digitized["endpoints"], table_records, run_context)
        mappings = map_curves_to_formulations([triage_artifact], digitized["endpoints"], table_records, run_context)
        _capture_figure_failures(run_context, content_handle, triage_artifact, digitized["endpoints"], mappings)
        all_mappings.extend(mapping.model_dump(mode="json") for mapping in mappings)
        paper_records, resolved_vlm_artifacts = _reconcile_direct_figure_records(
            content_handle,
            triage_artifact,
            digitized["endpoints"],
            mappings,
            table_records,
            vlm_artifacts,
        )
        all_vlm.extend(artifact.model_dump(mode="json") for artifact in resolved_vlm_artifacts)
        records_by_paper[content_handle.paper_id].extend(paper_records)
        if progress_callback:
            total_records = sum(len(items) for items in records_by_paper.values())
            progress_callback(completed_so_far + 1, current_item, f"records={total_records} total")

        completed_total = completed_so_far + 1
        if completed_total % checkpoint_every == 0 or completed_total == len(selected_pairs):
            ordered_records = [
                record
                for content_handle, _route_decision in selected_pairs
                for record in records_by_paper.get(content_handle.paper_id, [])
            ]
            if triage_jsonl:
                write_jsonl(triage_rows, triage_jsonl)
            if digitized_curves_jsonl:
                write_jsonl(all_curves, digitized_curves_jsonl)
            if digitized_endpoints_jsonl:
                write_jsonl(all_endpoints, digitized_endpoints_jsonl)
            if vlm_jsonl:
                write_jsonl(all_vlm, vlm_jsonl)
            if mapping_jsonl:
                write_jsonl(all_mappings, mapping_jsonl)
            if output_jsonl:
                write_records_jsonl(ordered_records, output_jsonl)

    records = [
        record
        for content_handle, _route_decision in selected_pairs
        for record in records_by_paper.get(content_handle.paper_id, [])
    ]
    if triage_jsonl:
        write_jsonl(triage_rows, triage_jsonl)
    if digitized_curves_jsonl:
        write_jsonl(all_curves, digitized_curves_jsonl)
    if digitized_endpoints_jsonl:
        write_jsonl(all_endpoints, digitized_endpoints_jsonl)
    if vlm_jsonl:
        write_jsonl(all_vlm, vlm_jsonl)
    if mapping_jsonl:
        write_jsonl(all_mappings, mapping_jsonl)
    if output_jsonl:
        write_records_jsonl(records, output_jsonl)
    if output_csv:
        write_records_csv(records, output_csv)
    return records


def build_figure_records(
    endpoint_rows: list[dict],
    mapping_rows: list[dict],
    table_records: list[Record],
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
) -> list[Record]:
    """Backward-compatible helper preserved for Round 1 compatibility."""

    table_lookup = {(record.paper_id, record.formulation.label): record for record in table_records if record.formulation.label}
    mapping_lookup = {
        (str(row.get("paper_id", "")), str(row.get("curve_id", ""))): row
        for row in mapping_rows
    }
    records: list[Record] = []
    for endpoint_row in endpoint_rows:
        endpoint_artifact = _coerce_endpoint_artifact(endpoint_row)
        if endpoint_artifact.status != "ok":
            continue
        mapping = mapping_lookup.get((endpoint_artifact.paper_id, endpoint_artifact.curve_id))
        if not mapping or not mapping.get("mapped_formulation_label"):
            continue
        source_record = table_lookup.get((endpoint_artifact.paper_id, str(mapping["mapped_formulation_label"])))
        if source_record is None:
            continue
        triage_artifact = FigureTriageArtifact(
            paper_id=source_record.paper_id,
            doi=source_record.doi,
            title=source_record.provenance.metadata.get("title", ""),
            pdf_path=source_record.provenance.source_path,
            selected_pages=source_record.provenance.source_pages,
            selected_image_path=endpoint_artifact.image_path,
            selected_image_paths=[endpoint_artifact.image_path],
            trace_id=str(source_record.provenance.metadata.get("triage_trace_id", "") or endpoint_artifact.triage_trace_id),
            figure_id=endpoint_artifact.figure_id,
            page_number=endpoint_artifact.page_number,
            subplot=endpoint_artifact.subplot,
            confidence=source_record.extractor_confidence,
        )
        records.append(
            _build_record_from_mapping(
                endpoint_artifact,
                FigureMappingArtifact.model_validate(mapping),
                source_record,
                triage_artifact,
            )
        )

    if output_jsonl:
        write_records_jsonl(records, output_jsonl)
    if output_csv:
        write_records_csv(records, output_csv)
    return records
