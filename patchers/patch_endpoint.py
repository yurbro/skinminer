"""Targeted endpoint-value recovery for unresolved records."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from patchers.common import append_patch, collect_source_fragments, collect_text_fragments, is_patchable
from schemas.models import EvidenceItem, Record
from utils.io import write_records_jsonl
from utils.status_panel import ProgressCallback
from utils.units import endpoint_unit_quality, parse_endpoint_amount, parse_endpoint_unit_hint

ENDPOINT_KEYWORDS = [
    "amount permeated",
    "amount released",
    "cumulative",
    "permeation",
    "release",
    "ug/cm",
    "mg/cm",
    "ng/cm",
    "ug/ml",
    "mg/ml",
    "ng/ml",
    "permeated vs time",
    "amount in",
]


def _label_key(record: Record) -> str:
    return " ".join((record.formulation.label or "").strip().lower().split())


def _collect_endpoint_hints(
    records: list[Record],
) -> tuple[dict[tuple[str, str], tuple[float, str, str, str]], dict[str, tuple[float, str, str, str]]]:
    grouped_by_label: dict[tuple[str, str], list[tuple[float, str, str, str, int]]] = {}
    grouped_by_paper: dict[str, list[tuple[float, str, str, str, int]]] = {}
    for record in records:
        if record.endpoint.value is None or not record.endpoint.unit:
            continue
        support = next(
            (item.snippet for item in record.evidence_items if item.field_name == "endpoint" and item.snippet),
            f"{record.endpoint.value:g} {record.endpoint.unit}".strip(),
        )
        payload = (float(record.endpoint.value), record.endpoint.unit, record.endpoint.kind, support, endpoint_unit_quality(record.endpoint.unit))
        label_key = _label_key(record)
        if label_key:
            grouped_by_label.setdefault((record.paper_id, label_key), []).append(payload)
        grouped_by_paper.setdefault(record.paper_id, []).append(payload)

    hints_by_label: dict[tuple[str, str], tuple[float, str, str, str]] = {}
    for key, entries in grouped_by_label.items():
        best = max(entries, key=lambda item: item[4])
        if best[4] > 0:
            hints_by_label[key] = best[:4]

    hints_by_paper: dict[str, tuple[float, str, str, str]] = {}
    for paper_id, entries in grouped_by_paper.items():
        best = max(entries, key=lambda item: item[4])
        if best[4] > 0:
            hints_by_paper[paper_id] = best[:4]

    return hints_by_label, hints_by_paper


def _patch_endpoint_pass(
    records: list[Record],
    *,
    progress_callback: ProgressCallback | None = None,
    progress_prefix: str = "patching endpoint",
) -> list[Record]:
    patched: list[Record] = []
    endpoint_hints_by_label, endpoint_hints_by_paper = _collect_endpoint_hints(records)
    for index, record in enumerate(records, start=1):
        if progress_callback:
            progress_callback(index - 1, record.paper_id, progress_prefix)
        candidate = record.model_copy(deep=True)
        failure_codes = set(candidate.failure_reasons)
        needs_recovery = candidate.endpoint.value is None or bool(
            failure_codes
            & {
                "missing_endpoint",
                "not_target_endpoint",
                "percent_only",
                "unit_normalization_failed",
            }
        )
        if not is_patchable(candidate) or not needs_recovery:
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        previous_signature = (
            candidate.endpoint.value,
            candidate.endpoint.unit,
            candidate.endpoint.kind,
        )
        label_key = _label_key(candidate)
        shared_hint = None
        if label_key:
            shared_hint = endpoint_hints_by_label.get((candidate.paper_id, label_key))
        if shared_hint is None:
            shared_hint = endpoint_hints_by_paper.get(candidate.paper_id)

        matched_text = ""
        matched_value = None
        matched_unit = ""
        matched_kind = ""
        unit_hint = ""
        kind_hint = "unknown"

        search_fragments = collect_text_fragments(candidate) + collect_source_fragments(
            candidate,
            keywords=ENDPOINT_KEYWORDS,
            max_fragments=10,
        )
        for fragment in search_fragments:
            value, unit, kind = parse_endpoint_amount(fragment)
            if value is not None:
                matched_text = fragment
                matched_value = value
                matched_unit = unit
                matched_kind = kind
                break
            if not unit_hint:
                parsed_unit, parsed_kind = parse_endpoint_unit_hint(fragment)
                if parsed_unit:
                    unit_hint = parsed_unit
                    kind_hint = parsed_kind
                    if not matched_text:
                        matched_text = fragment
        if matched_value is None and candidate.endpoint.value is not None and unit_hint:
            matched_value = candidate.endpoint.value
            matched_unit = unit_hint
            matched_kind = candidate.endpoint.kind if candidate.endpoint.kind != "unknown" else kind_hint
        if matched_value is None and shared_hint is not None:
            matched_value, matched_unit, matched_kind, matched_text = shared_hint
            if endpoint_unit_quality(matched_unit) <= 0 and unit_hint:
                matched_unit = unit_hint
                if matched_kind == "unknown":
                    matched_kind = kind_hint

        if matched_value is None:
            append_patch(candidate, "patch_endpoint_value", ["endpoint.value"], "skipped", notes="no recoverable endpoint fragment")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue
        if previous_signature == (matched_value, matched_unit or candidate.endpoint.unit, matched_kind or candidate.endpoint.kind):
            append_patch(candidate, "patch_endpoint_value", ["endpoint.value"], "skipped", notes="recovered endpoint matches existing value")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue
        current_quality = endpoint_unit_quality(candidate.endpoint.unit)
        new_quality = endpoint_unit_quality(matched_unit or candidate.endpoint.unit)
        if candidate.endpoint.value is not None and matched_value == candidate.endpoint.value and new_quality < current_quality:
            append_patch(candidate, "patch_endpoint_value", ["endpoint.value"], "skipped", notes="recovered endpoint unit is weaker than existing unit")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        candidate.endpoint.value = matched_value
        candidate.endpoint.unit = matched_unit or candidate.endpoint.unit
        if matched_kind and matched_kind != "unknown":
            candidate.endpoint.kind = matched_kind  # type: ignore[assignment]
        evidence = EvidenceItem(
            field_name="endpoint",
            modality="metadata" if candidate.route == "unresolved" else candidate.route,  # type: ignore[arg-type]
            locator="patcher:patch_endpoint_value:shared_hint" if shared_hint is not None else "patcher:patch_endpoint_value",
            snippet=matched_text,
            source_ref=candidate.doi or candidate.paper_id,
            confidence=0.6,
        )
        append_patch(
            candidate,
            "patch_endpoint_value",
            ["endpoint.value", "endpoint.unit", "endpoint.kind"],
            "applied",
            [evidence],
            notes="Recovered endpoint value from shared hints." if shared_hint is not None else "Recovered endpoint value from evidence or source fragments.",
        )
        patched.append(candidate)
        if progress_callback:
            progress_callback(index, record.paper_id, "applied")
    return patched


def patch_endpoint_value(
    records: Iterable[Record],
    output_jsonl: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Record]:
    """Patch missing endpoint values from evidence snippets and source fragments."""

    record_list = list(records)
    first_pass = _patch_endpoint_pass(record_list, progress_callback=progress_callback, progress_prefix="patching endpoint")
    second_pass = _patch_endpoint_pass(first_pass, progress_callback=progress_callback, progress_prefix="replaying endpoint hints")

    if output_jsonl:
        write_records_jsonl(second_pass, output_jsonl)
    return second_pass
