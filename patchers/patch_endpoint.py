"""Targeted endpoint-value recovery for unresolved records."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from patchers.common import append_patch, collect_source_fragments, collect_text_fragments, is_patchable
from schemas.models import EndpointMeasurement, EvidenceItem, Record, sorted_endpoints
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


def _coerce_endpoint_kind(kind: str) -> str:
    lowered = (kind or "").strip().lower()
    if lowered in {"amount_per_area", "amount_total"}:
        return "cumulative_amount"
    if lowered in {"percent", "percentage"}:
        return "permeated_fraction"
    if lowered in {"jss", "j_ss"}:
        return "flux"
    if lowered in {
        "flux",
        "cumulative_amount",
        "permeability_coefficient",
        "partition_parameter",
        "diffusion_parameter",
        "lag_time",
        "permeated_fraction",
    }:
        return lowered
    return "unknown"


def _primary_endpoint(record: Record) -> EndpointMeasurement | None:
    return record.primary_endpoint()


def _endpoint_signature(endpoint: EndpointMeasurement | None) -> tuple[float | None, str, str]:
    if endpoint is None:
        return None, "", "unknown"
    return endpoint.mean, endpoint.unit, endpoint.kind


def _set_primary_endpoint(candidate: Record, value: float, unit: str, kind: str) -> None:
    endpoint = _primary_endpoint(candidate)
    if endpoint is None:
        candidate.endpoints.append(EndpointMeasurement(kind=_coerce_endpoint_kind(kind), mean=value, unit=unit))
    else:
        endpoint.mean = value
        endpoint.unit = unit or endpoint.unit
        if kind and kind != "unknown":
            endpoint.kind = _coerce_endpoint_kind(kind)  # type: ignore[assignment]
    candidate.endpoints = sorted_endpoints(candidate.endpoints)


def _collect_endpoint_hints(
    records: list[Record],
) -> tuple[dict[tuple[str, str], tuple[float, str, str, str]], dict[str, tuple[float, str, str, str]]]:
    grouped_by_label: dict[tuple[str, str], list[tuple[float, str, str, str, int]]] = {}
    grouped_by_paper: dict[str, list[tuple[float, str, str, str, int]]] = {}
    for record in records:
        endpoint = _primary_endpoint(record)
        if endpoint is None or endpoint.mean is None or not endpoint.unit:
            continue
        support = next(
            (item.snippet for item in record.evidence_items if item.field_name == "endpoint" and item.snippet),
            f"{endpoint.mean:g} {endpoint.unit}".strip(),
        )
        payload = (float(endpoint.mean), endpoint.unit, endpoint.kind, support, endpoint_unit_quality(endpoint.unit))
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
        endpoint = _primary_endpoint(candidate)
        failure_codes = set(candidate.failure_reasons)
        needs_recovery = endpoint is None or endpoint.mean is None or bool(
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

        previous_signature = _endpoint_signature(endpoint)
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
        current_endpoint = _primary_endpoint(candidate)
        if matched_value is None and current_endpoint is not None and current_endpoint.mean is not None and unit_hint:
            matched_value = current_endpoint.mean
            matched_unit = unit_hint
            matched_kind = current_endpoint.kind if current_endpoint.kind != "unknown" else kind_hint
        if matched_value is None and shared_hint is not None:
            matched_value, matched_unit, matched_kind, matched_text = shared_hint
            if endpoint_unit_quality(matched_unit) <= 0 and unit_hint:
                matched_unit = unit_hint
                if matched_kind == "unknown":
                    matched_kind = kind_hint

        if matched_value is None:
            append_patch(candidate, "patch_endpoint_value", ["endpoints[0].mean"], "skipped", notes="no recoverable endpoint fragment")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue
        current_endpoint = _primary_endpoint(candidate)
        current_unit = current_endpoint.unit if current_endpoint is not None else ""
        current_kind = current_endpoint.kind if current_endpoint is not None else "unknown"
        coerced_matched_kind = _coerce_endpoint_kind(matched_kind or current_kind)
        if previous_signature == (matched_value, matched_unit or current_unit, coerced_matched_kind):
            append_patch(candidate, "patch_endpoint_value", ["endpoints[0].mean"], "skipped", notes="recovered endpoint matches existing value")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue
        current_quality = endpoint_unit_quality(current_unit)
        new_quality = endpoint_unit_quality(matched_unit or current_unit)
        if current_endpoint is not None and current_endpoint.mean is not None and matched_value == current_endpoint.mean and new_quality < current_quality:
            append_patch(candidate, "patch_endpoint_value", ["endpoints[0].mean"], "skipped", notes="recovered endpoint unit is weaker than existing unit")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        _set_primary_endpoint(candidate, matched_value, matched_unit or current_unit, matched_kind or current_kind)
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
            ["endpoints[0].mean", "endpoints[0].unit", "endpoints[0].kind"],
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
