"""Standardized figure-route extractor interface."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from extractors.common import build_provenance
from extractors.figure.digitize import digitize_figure_curves
from extractors.figure.map_curves import map_curves_to_formulations
from extractors.figure.models import DigitizedEndpointArtifact, FigureMappingArtifact, FigureTriageArtifact
from extractors.figure.triage import triage_figure_content
from schemas.models import ContentAccess, EndpointSpec, EvidenceItem, ExtractorRunContext, Record, RouteDecision
from utils.io import make_record_id, write_jsonl, write_records_csv, write_records_jsonl
from utils.resume import load_jsonl_if_exists, load_record_jsonl_if_exists
from utils.status_panel import ProgressCallback
from utils.units import normalize_amount_per_area


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
        conditions=source_record.conditions,
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
            ),
            source_format="pdf",
            source_path=triage_artifact.pdf_path,
            source_pages=triage_artifact.selected_pages,
            artifact_paths=artifact_paths,
            metadata={
                "figure_id": triage_artifact.figure_id,
                "triage_trace_id": triage_artifact.trace_id,
                "curve_trace_id": endpoint_row.trace_id,
                "curve_id": endpoint_row.curve_id,
                "mapping_rationale": mapping.mapping_rationale,
                "mapping_trace_id": mapping.trace_id,
                "mapping_image_path": mapping.mapping_image_path,
                "allowed_formulation_labels": mapping.allowed_formulation_labels,
                "source_table_record_ids": mapping.source_table_record_ids,
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
    mappings = map_curves_to_formulations([triage_artifact], digitized["endpoints"], table_records, run_context)
    table_lookup = {(record.paper_id, record.formulation.label): record for record in table_records if record.formulation.label}
    mapping_lookup = {(mapping.paper_id, mapping.curve_id): mapping for mapping in mappings}

    records: list[Record] = []
    for endpoint_row in digitized["endpoints"]:
        endpoint_artifact = _coerce_endpoint_artifact(endpoint_row)
        if endpoint_artifact.status != "ok":
            continue
        mapping = mapping_lookup.get((endpoint_artifact.paper_id, endpoint_artifact.curve_id))
        if not mapping or not mapping.mapped_formulation_label:
            continue
        source_record = table_lookup.get((content_handle.paper_id, mapping.mapped_formulation_label))
        if source_record is None:
            continue
        records.append(_build_record_from_mapping(endpoint_artifact, mapping, source_record, triage_artifact))
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
        mappings = map_curves_to_formulations([triage_artifact], digitized["endpoints"], table_records, run_context)
        _capture_figure_failures(run_context, content_handle, triage_artifact, digitized["endpoints"], mappings)
        all_mappings.extend(mapping.model_dump(mode="json") for mapping in mappings)

        table_lookup = {(record.paper_id, record.formulation.label): record for record in table_records if record.formulation.label}
        mapping_lookup = {(mapping.paper_id, mapping.curve_id): mapping for mapping in mappings}
        for endpoint_row in digitized["endpoints"]:
            endpoint_artifact = _coerce_endpoint_artifact(endpoint_row)
            if endpoint_artifact.status != "ok":
                continue
            mapping = mapping_lookup.get((endpoint_artifact.paper_id, endpoint_artifact.curve_id))
            if not mapping or not mapping.mapped_formulation_label:
                continue
            source_record = table_lookup.get((content_handle.paper_id, mapping.mapped_formulation_label))
            if source_record is None:
                continue
            records_by_paper[content_handle.paper_id].append(
                _build_record_from_mapping(endpoint_artifact, mapping, source_record, triage_artifact)
            )
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
