"""Targeted endpoint-time recovery for unresolved records."""

from __future__ import annotations
from pathlib import Path
from typing import Iterable

from patchers.common import append_patch, collect_source_fragments, collect_text_fragments, is_patchable
from schemas.models import EvidenceItem, Record
from utils.io import write_records_jsonl
from utils.status_panel import ProgressCallback
from utils.units import extract_time_mentions, normalize_time_to_hours


def patch_endpoint_time(
    records: Iterable[Record],
    output_jsonl: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Record]:
    """Patch missing endpoint time fields from duration or nearby evidence snippets."""

    patched: list[Record] = []
    record_list = list(records)
    for index, record in enumerate(record_list, start=1):
        if progress_callback:
            progress_callback(index - 1, record.paper_id, "patching endpoint time")
        candidate = record.model_copy(deep=True)
        if not is_patchable(candidate) or candidate.conditions.duration_h is not None:
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        matched_text = ""
        matched_value = None
        matched_unit = ""
        search_fragments = collect_text_fragments(candidate) + collect_source_fragments(
            candidate,
            keywords=["after", "at", "hour", "hours", "time", "duration", "sampling"],
            max_fragments=12,
        )
        for fragment in search_fragments:
            mentions = extract_time_mentions(fragment)
            if mentions:
                matched_text = fragment
                matched_value, matched_unit = max(
                    mentions,
                    key=lambda item: normalize_time_to_hours(item[0], item[1]) or float(item[0]),
                )
                break

        if matched_value is None:
            append_patch(candidate, "patch_endpoint_time", ["conditions.duration_h"], "skipped", notes="no recoverable endpoint-time fragment")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        normalized_duration = normalize_time_to_hours(matched_value, matched_unit)
        if normalized_duration is None:
            append_patch(candidate, "patch_endpoint_time", ["conditions.duration_h"], "skipped", notes="unrecognized endpoint-time unit")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        candidate.conditions.duration_h = normalized_duration
        evidence = EvidenceItem(
            field_name="endpoint_time",
            modality="metadata" if candidate.route == "unresolved" else candidate.route,  # type: ignore[arg-type]
            locator="patcher:patch_endpoint_time",
            snippet=matched_text,
            source_ref=candidate.doi or candidate.paper_id,
            confidence=0.65,
        )
        append_patch(candidate, "patch_endpoint_time", ["conditions.duration_h"], "applied", [evidence], notes="Recovered endpoint time from evidence fragments.")
        patched.append(candidate)
        if progress_callback:
            progress_callback(index, record.paper_id, "applied")

    if output_jsonl:
        write_records_jsonl(patched, output_jsonl)
    return patched
