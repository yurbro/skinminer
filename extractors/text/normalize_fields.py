"""Normalization from text extraction prompt outputs into canonical records."""

from __future__ import annotations

from extractors.common import build_provenance, infer_device_label, route_device_hint
from extractors.text.extract_fields import LegacyEndpoint, LegacyExtractedRecord
from extractors.text.page_selection import TextEvidenceWindow, parse_anchor_pages
from schemas.models import (
    ConditionSpec,
    ContentAccess,
    EndpointSpec,
    EvidenceItem,
    ExtractorRunContext,
    FormulationComponent,
    FormulationSpec,
    Record,
    RouteDecision,
)
from utils.io import make_record_id
from utils.units import amount_total_to_ug_per_cm2, normalize_amount_per_area, normalize_time_to_hours, parse_api_concentration, parse_area_cm2


def infer_endpoint_kind(endpoint: LegacyEndpoint) -> str:
    """Infer endpoint kind from the extracted endpoint type and units."""

    endpoint_type = endpoint.endpoint_type
    unit = (endpoint.unit or "").lower().replace("µ", "u")
    if endpoint_type.lower() == "flux":
        return "flux"
    if endpoint_type.lower() == "jss":
        return "jss"
    if "/cm" in unit:
        return "amount_per_area"
    if "%" in unit:
        return "percent"
    if any(token in unit for token in ["mg", "ug", "ng"]):
        return "amount_total"
    return "unknown"


def _device_from_cell_type(cell_type: str) -> str:
    if cell_type == "Franz":
        return "Franz diffusion cell"
    if cell_type == "diffusion_cell_unspecified":
        return "diffusion cell"
    return cell_type


def _page_from_locator(locator: str) -> int | None:
    pages = parse_anchor_pages(locator)
    return pages[0] + 1 if pages else None


def normalize_text_record(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    run_context: ExtractorRunContext,
    window: TextEvidenceWindow,
    legacy: LegacyExtractedRecord,
    record_index: int,
) -> Record:
    """Normalize a legacy text extraction record into a canonical `Record`."""

    api_value, api_unit, api_basis = parse_api_concentration(legacy.api_conc_raw)
    endpoint_kind = infer_endpoint_kind(legacy.endpoint_main)
    normalized_value = None
    normalized_unit = ""
    if endpoint_kind == "amount_per_area":
        normalized_value, normalized_unit = normalize_amount_per_area(legacy.endpoint_main.value, legacy.endpoint_main.unit)
    elif endpoint_kind == "amount_total":
        normalized_value, normalized_unit = amount_total_to_ug_per_cm2(
            legacy.endpoint_main.value,
            legacy.endpoint_main.unit,
            legacy.diffusion_area_cm2,
        )

    inferred_device = infer_device_label(
        _device_from_cell_type(legacy.cell_type),
        route_decision.notes,
        str(route_decision.raw_labels.get("where_franz", "") or ""),
        str(route_decision.raw_labels.get("where_diffusion_cell", "") or ""),
        *(item.snippet for item in legacy.evidence),
    )
    diffusion_area_cm2 = legacy.diffusion_area_cm2
    if diffusion_area_cm2 is None:
        for fragment in [
            route_decision.notes,
            str(route_decision.raw_labels.get("where_diffusion_cell", "") or ""),
            str(route_decision.raw_labels.get("where_endpoint", "") or ""),
            *(item.snippet for item in legacy.evidence),
        ]:
            diffusion_area_cm2 = parse_area_cm2(fragment)
            if diffusion_area_cm2 is not None:
                break

    evidence_items = [
        EvidenceItem(
            field_name=item.field,
            modality="text",
            locator=item.locator,
            page=_page_from_locator(item.locator) if window.locator_mode == "page" else None,
            snippet=item.snippet,
            source_ref=window.source_ref or content_handle.doi or content_handle.paper_id,
            confidence=legacy.confidence,
        )
        for item in legacy.evidence
    ]
    source_notes = [legacy.notes] if legacy.notes else []
    if legacy.needs_supp != "no":
        source_notes.append(f"needs_supp={legacy.needs_supp}")

    return Record(
        record_id=make_record_id(content_handle.paper_id, "text", f"text_{record_index}", suffix=str(record_index)),
        paper_id=content_handle.paper_id,
        doi=content_handle.doi,
        route=route_decision.route if route_decision.route in {"text", "mixed"} else "text",
        route_confidence=route_decision.route_confidence,
        extractor_confidence=legacy.confidence,
        study_type=legacy.study_type,
        device=inferred_device or route_device_hint(route_decision) or _device_from_cell_type(legacy.cell_type),
        barrier=legacy.barrier_name or legacy.barrier_category,
        formulation=FormulationSpec(
            label=f"text_{record_index}",
            api_name=legacy.api_name,
            api_concentration_value=api_value,
            api_concentration_unit=api_unit,
            api_basis=api_basis,
            api_concentration_raw=legacy.api_conc_raw,
            dosage_form=legacy.dosage_form,
            components=[FormulationComponent(name=item.name, raw=item.concentration_raw) for item in legacy.ingredients],
        ),
        endpoint=EndpointSpec(
            field_name=legacy.endpoint_main.endpoint_type,
            kind=endpoint_kind,
            value=legacy.endpoint_main.value,
            unit=legacy.endpoint_main.unit,
            time_value=legacy.endpoint_main.time_value,
            time_unit=legacy.endpoint_main.time_unit,
            normalized_value=normalized_value,
            normalized_unit=normalized_unit,
        ),
        conditions=ConditionSpec(
            diffusion_area_cm2=diffusion_area_cm2,
            duration_h=normalize_time_to_hours(legacy.endpoint_main.time_value, legacy.endpoint_main.time_unit),
        ),
        evidence_items=evidence_items,
        provenance=build_provenance(
            extractor_name="text",
            content_handle=content_handle,
            route_decision=route_decision,
            source_format=window.source_format,
            source_path=window.source_ref,
            source_pages=window.selected_pages,
            metadata={
                "source_backend": window.source_backend,
                "locator_mode": window.locator_mode,
                "anchor_locators": window.anchor_locators,
                "selected_locators": window.selected_locators,
                "table_hint": window.table_hint,
                "score_debug": window.score_debug,
            },
        ),
        source_notes=source_notes,
    )
