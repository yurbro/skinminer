"""Targeted diffusion-area recovery for unresolved records."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from patchers.common import append_patch, collect_source_fragments, collect_text_fragments, is_patchable
from schemas.models import EvidenceItem, Record
from utils.io import write_records_jsonl
from utils.status_panel import ProgressCallback
from utils.units import parse_area_cm2


def _label_key(record: Record) -> str:
    return " ".join((record.formulation.label or "").strip().lower().split())


def _existing_area_support(record: Record, fallback_area: float) -> str:
    for item in record.evidence_items:
        if item.field_name == "area" and item.snippet:
            return item.snippet
    return f"{fallback_area:g} cm2"


def _collect_area_hints(records: list[Record]) -> tuple[dict[tuple[str, str], tuple[float, str]], dict[str, tuple[float, str]]]:
    grouped_by_label: dict[tuple[str, str], list[tuple[float, str]]] = {}
    grouped_by_paper: dict[str, list[tuple[float, str]]] = {}
    for record in records:
        area = record.conditions.diffusion_area_cm2
        if area is None:
            continue
        rounded = round(float(area), 4)
        payload = (rounded, _existing_area_support(record, rounded))
        label_key = _label_key(record)
        if label_key:
            grouped_by_label.setdefault((record.paper_id, label_key), []).append(payload)
        grouped_by_paper.setdefault(record.paper_id, []).append(payload)

    hints_by_label: dict[tuple[str, str], tuple[float, str]] = {}
    for key, entries in grouped_by_label.items():
        unique_values = {value for value, _support in entries}
        if len(unique_values) == 1:
            area_value = entries[0][0]
            support = next((support for value, support in entries if value == area_value and support), f"{area_value:g} cm2")
            hints_by_label[key] = (area_value, support)

    hints_by_paper: dict[str, tuple[float, str]] = {}
    for paper_id, entries in grouped_by_paper.items():
        unique_values = {value for value, _support in entries}
        if len(unique_values) == 1:
            area_value = entries[0][0]
            support = next((support for value, support in entries if value == area_value and support), f"{area_value:g} cm2")
            hints_by_paper[paper_id] = (area_value, support)

    return hints_by_label, hints_by_paper


def patch_area(
    records: Iterable[Record],
    output_jsonl: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Record]:
    """Patch missing diffusion area fields from evidence snippets and shared hints."""

    patched: list[Record] = []
    record_list = list(records)
    area_hints_by_label, area_hints_by_paper = _collect_area_hints(record_list)
    for index, record in enumerate(record_list, start=1):
        if progress_callback:
            progress_callback(index - 1, record.paper_id, "patching area")
        candidate = record.model_copy(deep=True)
        if not is_patchable(candidate) or candidate.conditions.diffusion_area_cm2 is not None:
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        matched_text = ""
        matched_area = None
        label_key = _label_key(candidate)
        shared_hint = None
        if label_key:
            shared_hint = area_hints_by_label.get((candidate.paper_id, label_key))
        if shared_hint is None:
            shared_hint = area_hints_by_paper.get(candidate.paper_id)
        if shared_hint is not None:
            matched_area, matched_text = shared_hint

        search_fragments = collect_text_fragments(candidate) + collect_source_fragments(
            candidate,
            keywords=[
                "diffusion area",
                "effective area",
                "exposed area",
                "surface area",
                "membrane area",
                "available area",
                "cm2",
                "cm^2",
                "mm2",
                "mm^2",
                "diameter",
                "radius",
                "orifice",
                "x",
                "×",
            ],
            max_fragments=16,
        )
        if matched_area is None:
            for fragment in search_fragments:
                matched_area = parse_area_cm2(fragment)
                if matched_area is not None:
                    matched_text = fragment
                    break

        if matched_area is None:
            append_patch(candidate, "patch_area", ["conditions.diffusion_area_cm2"], "skipped", notes="no recoverable area fragment")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        candidate.conditions.diffusion_area_cm2 = matched_area
        evidence = EvidenceItem(
            field_name="area",
            modality="metadata" if candidate.route == "unresolved" else candidate.route,  # type: ignore[arg-type]
            locator="patcher:patch_area:shared_hint" if shared_hint is not None else "patcher:patch_area",
            snippet=matched_text,
            source_ref=candidate.doi or candidate.paper_id,
            confidence=0.65,
        )
        append_patch(
            candidate,
            "patch_area",
            ["conditions.diffusion_area_cm2"],
            "applied",
            [evidence],
            notes="Recovered diffusion area from shared hints." if shared_hint is not None else "Recovered diffusion area from evidence fragments.",
        )
        patched.append(candidate)
        if progress_callback:
            progress_callback(index, record.paper_id, "applied")

    if output_jsonl:
        write_records_jsonl(patched, output_jsonl)
    return patched
