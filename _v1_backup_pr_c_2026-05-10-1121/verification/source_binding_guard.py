"""Record-level source-context consistency checks."""

from __future__ import annotations

from schemas.models import Record
from verification.failure_taxonomy import FailureCode


CONDITION_FIELDS = {
    "membrane_type",
    "membrane_source",
    "membrane_thickness_um",
    "receptor_medium",
    "dose_type",
    "dose_amount",
}


def _compact(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _evidence_text(record: Record, field_name: str | None = None) -> str:
    items = [
        " ".join(
            part
            for part in (
                item.field_name,
                item.modality,
                item.locator,
                item.snippet,
                item.source_ref,
            )
            if part
        )
        for item in record.evidence_items
        if field_name is None or item.field_name == field_name
    ]
    return _compact(" | ".join(items))


def _metadata_text(record: Record) -> str:
    metadata = record.provenance.metadata
    parts = [
        str(metadata.get("figure_extraction_method", "") or ""),
        str(metadata.get("mapping_rationale", "") or ""),
        str(metadata.get("mapping_label_space_status", "") or ""),
        str(metadata.get("mapping_status", "") or ""),
        str(metadata.get("vlm_grounding_status", "") or ""),
        *record.source_notes,
    ]
    route_raw = metadata.get("route_raw_labels", {})
    if isinstance(route_raw, dict):
        parts.extend(str(value) for value in route_raw.values() if value)
    return _compact(" | ".join(parts))


def _has_endpoint_shared_hint(record: Record) -> bool:
    return "patcher:patch_endpoint_value:shared_hint" in _evidence_text(record, "endpoint")


def _has_endpoint_time_patch(record: Record) -> bool:
    return "patcher:patch_endpoint_time" in _evidence_text(record, "endpoint_time")


def _has_figure_endpoint_context(record: Record) -> bool:
    endpoint_text = _evidence_text(record, "endpoint")
    note_text = _compact(" | ".join(record.source_notes))
    return (
        " figure " in f" {endpoint_text} "
        or "curve_trace_id=" in note_text
        or "figure_trace_id=" in note_text
        or "patcher:patch_endpoint_value:shared_hint" in endpoint_text
    )


def _route_raw_endpoint_carrier(record: Record) -> str:
    raw = record.provenance.metadata.get("route_raw_labels", {})
    if not isinstance(raw, dict):
        return ""
    return _compact(str(raw.get("endpoint_carrier", "") or ""))


def _has_figure_condition_values(record: Record) -> bool:
    conditions = record.conditions
    return any(
        [
            bool(conditions.membrane_type),
            bool(conditions.membrane_source),
            conditions.membrane_thickness_um is not None,
            bool(conditions.receptor_medium),
            bool(conditions.dose_type),
            bool(conditions.dose_amount),
        ]
    )


def _has_figure_condition_evidence(record: Record) -> bool:
    return any(item.field_name in CONDITION_FIELDS and item.modality == "figure" for item in record.evidence_items)


def _mapping_is_weak(record: Record) -> bool:
    metadata = record.provenance.metadata
    extraction_method = _compact(str(metadata.get("figure_extraction_method", "") or ""))
    if extraction_method == "cv_vlm_agree" or "figure_value_reconciliation=cv_vlm_agree" in _metadata_text(record):
        return False

    grounding = _compact(str(metadata.get("vlm_grounding_status", "") or ""))
    if extraction_method in {"vlm_only", "vlm_retry_cv_disagreement"} and grounding in {"source_label_space", "figure_label_space"}:
        return False

    rationale = _compact(str(metadata.get("mapping_rationale", "") or ""))
    strong_terms = ("legend", "marker", "symbol", "exact match", "source label", "source_label")
    if any(term in rationale for term in strong_terms):
        return False

    return True


def source_context_inconsistency_reasons(record: Record) -> list[str]:
    """Return deterministic source-binding guard reasons for a canonical record."""

    if record.route != "figure":
        return []

    reasons: list[str] = []
    extractor_name = _compact(record.provenance.extractor_name)

    if (
        extractor_name != "figure"
        and record.endpoint.value is not None
        and (_has_figure_endpoint_context(record) or _route_raw_endpoint_carrier(record) == "figure")
    ):
        reasons.append("figure_route_table_endpoint")

    if _has_endpoint_shared_hint(record):
        reasons.append("endpoint_value_from_shared_hint")

    if _has_endpoint_shared_hint(record) and _has_endpoint_time_patch(record):
        reasons.append("endpoint_value_time_context_mismatch")

    if extractor_name == "figure":
        if _mapping_is_weak(record):
            reasons.append("weak_figure_mapping_grounding")
        if _has_figure_condition_values(record) and not _has_figure_condition_evidence(record):
            reasons.append("figure_condition_not_source_grounded")

    deduped: list[str] = []
    for reason in reasons:
        if reason not in deduped:
            deduped.append(reason)
    return deduped


def apply_source_context_guard(record: Record) -> list[str]:
    """Mutate record notes and return failure codes for source-context inconsistencies."""

    reasons = source_context_inconsistency_reasons(record)
    if not reasons:
        return []
    for reason in reasons:
        note = f"source_context_inconsistent:{reason}"
        if note not in record.source_notes:
            record.source_notes.append(note)
    return [FailureCode.SOURCE_CONTEXT_INCONSISTENT.value]
