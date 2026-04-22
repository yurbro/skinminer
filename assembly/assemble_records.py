"""Record assembly and normalization across extraction modalities."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Iterable

from schemas.models import EvidenceItem, Record
from utils.io import write_records_csv, write_records_jsonl
from utils.status_panel import ProgressCallback
from utils.units import (
    coerce_endpoint_kind_from_unit,
    amount_total_to_ug_per_cm2,
    normalize_amount_per_area,
    normalize_api_concentration_fields,
    normalize_time_to_hours,
    parse_api_concentration,
)


def _is_generic_label(label: str) -> bool:
    return not label or label.startswith("text_")


def _normalize_label_key(label: str) -> str:
    return " ".join((label or "").strip().lower().split())


def _normalize_api_key(api_name: str) -> str:
    return " ".join((api_name or "").strip().lower().split())


def _table_support_score(record: Record) -> float:
    score = 0.0
    if record.route == "table":
        score += 4.0
    if record.formulation.label and not _is_generic_label(record.formulation.label):
        score += 3.0
    if record.formulation.api_concentration_value is not None or record.formulation.api_concentration_raw:
        score += 2.5
    if record.conditions.diffusion_area_cm2 is not None:
        score += 1.5
    if record.conditions.receptor_volume_ml is not None:
        score += 1.0
    if record.endpoint.time_value is not None:
        score += 1.0
    if record.endpoint.value is not None:
        score += 0.5
    score += min(3.0, len(record.evidence_items) * 0.2)
    return score


def _normalize_record(candidate: Record) -> Record:
    normalized = candidate.model_copy(deep=True)
    normalized.endpoint.kind = coerce_endpoint_kind_from_unit(normalized.endpoint.kind, normalized.endpoint.unit)
    if normalized.conditions.duration_h is None and normalized.endpoint.time_value is not None:
        normalized.conditions.duration_h = normalize_time_to_hours(normalized.endpoint.time_value, normalized.endpoint.time_unit)
    if normalized.formulation.api_concentration_value is None and normalized.formulation.api_concentration_raw:
        value, unit, basis = parse_api_concentration(normalized.formulation.api_concentration_raw)
        normalized.formulation.api_concentration_value = value
        normalized.formulation.api_concentration_unit = unit or normalized.formulation.api_concentration_unit
        normalized.formulation.api_basis = basis or normalized.formulation.api_basis
    (
        normalized.formulation.api_concentration_value,
        normalized.formulation.api_concentration_unit,
        normalized.formulation.api_basis,
    ) = normalize_api_concentration_fields(
        normalized.formulation.api_concentration_value,
        normalized.formulation.api_concentration_unit,
        normalized.formulation.api_basis,
        normalized.formulation.api_concentration_raw,
    )
    if normalized.endpoint.kind == "amount_per_area" and normalized.endpoint.normalized_value is None:
        value, unit = normalize_amount_per_area(normalized.endpoint.value, normalized.endpoint.unit)
        normalized.endpoint.normalized_value = value
        normalized.endpoint.normalized_unit = unit
    elif normalized.endpoint.kind == "amount_total" and normalized.endpoint.normalized_value is None:
        value, unit = amount_total_to_ug_per_cm2(
            normalized.endpoint.value,
            normalized.endpoint.unit,
            normalized.conditions.diffusion_area_cm2,
        )
        normalized.endpoint.normalized_value = value
        normalized.endpoint.normalized_unit = unit
    return normalized


def _merge_in_place(target: Record, incoming: Record) -> Record:
    merged = target.model_copy(deep=True)
    seen_evidence = {(item.field_name, item.locator, item.snippet) for item in merged.evidence_items}
    for item in incoming.evidence_items:
        key = (item.field_name, item.locator, item.snippet)
        if key not in seen_evidence:
            merged.evidence_items.append(item)
            seen_evidence.add(key)

    for note in incoming.source_notes:
        if note and note not in merged.source_notes:
            merged.source_notes.append(note)

    if merged.route != incoming.route:
        merged.route = "mixed"

    for path in incoming.provenance.artifact_paths:
        if path and path not in merged.provenance.artifact_paths:
            merged.provenance.artifact_paths.append(path)
    merged.provenance.metadata.update({k: v for k, v in incoming.provenance.metadata.items() if v is not None})

    if (
        (not merged.formulation.label or _is_generic_label(merged.formulation.label))
        and incoming.formulation.label
        and not _is_generic_label(incoming.formulation.label)
    ):
        merged.formulation.label = incoming.formulation.label
    if not merged.formulation.components and incoming.formulation.components:
        merged.formulation.components = incoming.formulation.components
    if merged.formulation.api_concentration_value is None and incoming.formulation.api_concentration_value is not None:
        merged.formulation.api_concentration_value = incoming.formulation.api_concentration_value
        merged.formulation.api_concentration_unit = incoming.formulation.api_concentration_unit
        merged.formulation.api_basis = incoming.formulation.api_basis
    if not merged.formulation.api_concentration_raw and incoming.formulation.api_concentration_raw:
        merged.formulation.api_concentration_raw = incoming.formulation.api_concentration_raw

    if merged.endpoint.value is None and incoming.endpoint.value is not None:
        merged.endpoint = incoming.endpoint
    elif merged.endpoint.time_value is None and incoming.endpoint.time_value is not None:
        merged.endpoint.time_value = incoming.endpoint.time_value
        merged.endpoint.time_unit = incoming.endpoint.time_unit
    if merged.conditions.diffusion_area_cm2 is None and incoming.conditions.diffusion_area_cm2 is not None:
        merged.conditions.diffusion_area_cm2 = incoming.conditions.diffusion_area_cm2
    if merged.conditions.receptor_volume_ml is None and incoming.conditions.receptor_volume_ml is not None:
        merged.conditions.receptor_volume_ml = incoming.conditions.receptor_volume_ml
    if not merged.conditions.membrane_type and incoming.conditions.membrane_type:
        merged.conditions.membrane_type = incoming.conditions.membrane_type
    if not merged.conditions.membrane_source and incoming.conditions.membrane_source:
        merged.conditions.membrane_source = incoming.conditions.membrane_source
    if merged.conditions.membrane_thickness_um is None and incoming.conditions.membrane_thickness_um is not None:
        merged.conditions.membrane_thickness_um = incoming.conditions.membrane_thickness_um
    if not merged.conditions.receptor_medium and incoming.conditions.receptor_medium:
        merged.conditions.receptor_medium = incoming.conditions.receptor_medium
    if not merged.conditions.dose_type and incoming.conditions.dose_type:
        merged.conditions.dose_type = incoming.conditions.dose_type
    if not merged.conditions.dose_amount and incoming.conditions.dose_amount:
        merged.conditions.dose_amount = incoming.conditions.dose_amount
    if merged.extractor_confidence is None or (incoming.extractor_confidence or 0.0) > (merged.extractor_confidence or 0.0):
        merged.extractor_confidence = incoming.extractor_confidence
    if merged.mapping_confidence is None or (incoming.mapping_confidence or 0.0) > (merged.mapping_confidence or 0.0):
        merged.mapping_confidence = incoming.mapping_confidence
    return _normalize_record(merged)


def _record_key(record: Record) -> tuple[str, str, str, float | None, float | None]:
    return (
        record.doi,
        record.formulation.label,
        record.endpoint.kind,
        record.endpoint.time_value,
        record.endpoint.value,
    )


def _build_table_support_indexes(records: list[Record]) -> tuple[dict[str, list[Record]], dict[tuple[str, str], list[Record]]]:
    by_paper: dict[str, list[Record]] = {}
    by_label: dict[tuple[str, str], list[Record]] = {}
    for record in records:
        if record.route != "table":
            continue
        by_paper.setdefault(record.paper_id, []).append(record)
        label_key = _normalize_label_key(record.formulation.label)
        if label_key:
            by_label.setdefault((record.paper_id, label_key), []).append(record)
    return by_paper, by_label


def _best_table_support(records: list[Record]) -> Record | None:
    if not records:
        return None
    return max(records, key=_table_support_score)


def _api_concentration_signature(record: Record) -> tuple[float, str, str] | None:
    value = record.formulation.api_concentration_value
    if value is None:
        return None
    return (
        round(float(value), 9),
        " ".join((record.formulation.api_concentration_unit or "").strip().lower().split()),
        " ".join((record.formulation.api_basis or "").strip().lower().split()),
    )


def _build_table_api_support_hints(records: list[Record]) -> dict[tuple[str, str], Record]:
    """Return unique same-paper table API concentration support from partial rows."""

    grouped: dict[tuple[str, str], list[Record]] = {}
    for record in records:
        if record.route != "table" or record.endpoint.value is not None:
            continue
        if _api_concentration_signature(record) is None:
            continue
        api_key = _normalize_api_key(record.formulation.api_name)
        if not api_key:
            continue
        grouped.setdefault((record.paper_id, api_key), []).append(record)

    hints: dict[tuple[str, str], Record] = {}
    for key, candidates in grouped.items():
        signatures = {_api_concentration_signature(candidate) for candidate in candidates}
        signatures.discard(None)
        if len(signatures) == 1:
            best = _best_table_support(candidates)
            if best is not None:
                hints[key] = best
    return hints


def _api_support_fragment(record: Record) -> str:
    for item in record.evidence_items:
        if item.field_name == "api_concentration" and item.snippet:
            return item.snippet
    if record.formulation.api_concentration_raw:
        return record.formulation.api_concentration_raw
    for item in record.evidence_items:
        if item.field_name == "formulation" and item.snippet:
            return item.snippet
    value = record.formulation.api_concentration_value
    if value is None:
        return ""
    return " ".join(
        part
        for part in (
            f"{float(value):g}",
            record.formulation.api_concentration_unit,
            record.formulation.api_basis,
        )
        if part
    )


def _api_support_locator(record: Record) -> str:
    for field_name in ("api_concentration", "formulation"):
        for item in record.evidence_items:
            if item.field_name == field_name and item.locator:
                return item.locator
    return str(record.provenance.metadata.get("table_id", "") or "")


def _add_api_support_evidence(target: Record, support_record: Record) -> None:
    snippet = _api_support_fragment(support_record)
    if not snippet:
        return
    locator = _api_support_locator(support_record)
    seen = {(item.field_name, item.locator, item.snippet) for item in target.evidence_items}
    key = ("api_concentration", locator, snippet)
    if key in seen:
        return
    target.evidence_items.append(
        EvidenceItem(
            field_name="api_concentration",
            modality="table",
            locator=locator,
            snippet=snippet,
            source_ref=support_record.doi or target.doi or support_record.paper_id,
            confidence=support_record.extractor_confidence or 0.7,
        )
    )


def _apply_table_api_support(record: Record, support_record: Record) -> Record:
    """Copy only same-paper table API concentration support into an endpoint row."""

    if record.formulation.api_concentration_value is not None:
        return record
    api_key = _normalize_api_key(record.formulation.api_name)
    support_api_key = _normalize_api_key(support_record.formulation.api_name)
    if not api_key or api_key != support_api_key:
        return record

    merged = record.model_copy(deep=True)
    merged.formulation.api_concentration_value = support_record.formulation.api_concentration_value
    merged.formulation.api_concentration_unit = support_record.formulation.api_concentration_unit
    merged.formulation.api_basis = support_record.formulation.api_basis
    if not merged.formulation.api_concentration_raw and support_record.formulation.api_concentration_raw:
        merged.formulation.api_concentration_raw = support_record.formulation.api_concentration_raw

    support_ids = list(merged.provenance.metadata.get("table_api_support_record_ids", []))
    if support_record.record_id not in support_ids:
        support_ids.append(support_record.record_id)
    merged.provenance.metadata["table_api_support_record_ids"] = support_ids

    support_note = (
        f"assembly_table_api_support:{support_record.formulation.label}"
        if support_record.formulation.label
        else f"assembly_table_api_support:{support_record.record_id}"
    )
    if support_note not in merged.source_notes:
        merged.source_notes.append(support_note)
    _add_api_support_evidence(merged, support_record)
    return _normalize_record(merged)


def _select_table_support_records(
    record: Record,
    table_support_by_paper: dict[str, list[Record]],
    table_support_by_label: dict[tuple[str, str], list[Record]],
) -> list[Record]:
    if record.route == "table":
        return []

    supports: list[Record] = []
    seen: set[str] = set()
    label_key = _normalize_label_key(record.formulation.label)
    if label_key:
        best = _best_table_support(table_support_by_label.get((record.paper_id, label_key), []))
        if best is not None:
            supports.append(best)
            seen.add(best.record_id)

    if not supports:
        paper_candidates = table_support_by_paper.get(record.paper_id, [])
        non_generic = [candidate for candidate in paper_candidates if not _is_generic_label(candidate.formulation.label)]
        unique_labels = {_normalize_label_key(candidate.formulation.label) for candidate in non_generic}
        if len(unique_labels) == 1 and non_generic:
            best = _best_table_support(non_generic)
            if best is not None and best.record_id not in seen:
                supports.append(best)
                seen.add(best.record_id)

    if not supports and record.route in {"figure", "mixed"}:
        best = _best_table_support(table_support_by_paper.get(record.paper_id, []))
        if best is not None and best.record_id not in seen:
            supports.append(best)

    return supports


def assemble_records(
    record_groups: Iterable[Iterable[Record]],
    include_table_partials: bool = False,
    enable_table_promotion: bool = True,
    shared_state: dict[str, Any] | None = None,
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Record]:
    """Assemble and normalize candidate records across modalities without verifying them."""

    all_records = [_normalize_record(record) for group in record_groups for record in group]
    figure_failures_by_paper = dict((shared_state or {}).get("figure_failures_by_paper", {}))
    assembled_lookup: dict[tuple[str, str, str, float | None, float | None], Record] = {}
    table_partials_by_doi: dict[str, list[Record]] = {}
    table_support_by_paper, table_support_by_label = _build_table_support_indexes(all_records)
    table_api_support_by_paper_api = _build_table_api_support_hints(all_records)

    total = len(all_records)
    for index, record in enumerate(all_records, start=1):
        if progress_callback:
            progress_callback(index - 1, record.paper_id, "assembling records")
        if record.route in {"figure", "mixed"}:
            for note in figure_failures_by_paper.get(record.paper_id, []):
                if note and note not in record.source_notes:
                    record.source_notes.append(note)
        if record.route == "table" and record.endpoint.value is None:
            table_partials_by_doi.setdefault(record.doi, []).append(record)

    for index, record in enumerate(all_records, start=1):
        if record.route == "table" and record.endpoint.value is None and not include_table_partials:
            if progress_callback:
                progress_callback(index, record.paper_id, "skip table partial")
            continue

        if record.route == "table" and record.endpoint.value is not None and record.formulation.api_concentration_value is None:
            api_key = _normalize_api_key(record.formulation.api_name)
            support_record = table_api_support_by_paper_api.get((record.paper_id, api_key))
            if support_record is not None:
                record = _apply_table_api_support(record, support_record)

        support_records = (
            _select_table_support_records(record, table_support_by_paper, table_support_by_label)
            if enable_table_promotion
            else []
        )
        for support_record in support_records:
            record = _merge_in_place(record, support_record)
            support_ids = list(record.provenance.metadata.get("table_support_record_ids", []))
            if support_record.record_id not in support_ids:
                support_ids.append(support_record.record_id)
            record.provenance.metadata["table_support_record_ids"] = support_ids
            support_note = (
                f"assembly_table_support:{support_record.formulation.label}"
                if support_record.formulation.label
                else f"assembly_table_support:{support_record.record_id}"
            )
            if support_note not in record.source_notes:
                record.source_notes.append(support_note)

        candidates = table_partials_by_doi.get(record.doi, [])
        if _is_generic_label(record.formulation.label) and len(candidates) == 1:
            record.formulation.label = candidates[0].formulation.label
            record = _merge_in_place(record, candidates[0])
        elif record.formulation.label:
            for candidate in candidates:
                if candidate.formulation.label == record.formulation.label:
                    record = _merge_in_place(record, candidate)
                    break

        key = _record_key(record)
        if key in assembled_lookup:
            assembled_lookup[key] = _merge_in_place(assembled_lookup[key], record)
        else:
            assembled_lookup[key] = record.model_copy(deep=True)
        if progress_callback:
            progress_callback(index, record.paper_id, f"assembled={len(assembled_lookup)}")

    assembled = list(assembled_lookup.values())
    if include_table_partials:
        for doi, partials in table_partials_by_doi.items():
            for partial in partials:
                key = _record_key(partial)
                if key not in assembled_lookup:
                    assembled.append(partial)

    if output_jsonl:
        write_records_jsonl(assembled, output_jsonl)
    if output_csv:
        write_records_csv(assembled, output_csv)
    return assembled
