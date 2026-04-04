"""Targeted API concentration recovery for unresolved records."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from patchers.common import append_patch, collect_source_fragments, collect_text_fragments, is_patchable
from schemas.models import EvidenceItem, Record
from utils.io import write_records_jsonl
from utils.status_panel import ProgressCallback
from utils.units import api_concentration_quality, infer_api_concentration_from_fragments, is_strict_api_concentration_hint

STRICT_SHARED_API_HINT_MIN_QUALITY = 12


def _label_key(record: Record) -> str:
    return " ".join((record.formulation.label or "").strip().lower().split())


def _component_fragments(record: Record) -> list[str]:
    fragments: list[str] = []
    for component in record.formulation.components:
        if component.name:
            fragments.append(
                " ".join(
                    part
                    for part in (
                        component.name,
                        f"{component.concentration_value:g}" if component.concentration_value is not None else "",
                        component.concentration_unit,
                        component.basis,
                        component.raw,
                        component.note,
                    )
                    if part
                )
            )
            if component.raw:
                fragments.append(
                    " ".join(part for part in (component.name, component.raw) if part)
                )
            if component.note:
                fragments.append(
                    " ".join(part for part in (component.name, component.note) if part)
                )
        if component.raw:
            fragments.append(component.raw)
        if component.note:
            fragments.append(component.note)
    return fragments


def _api_search_keywords(record: Record) -> list[str]:
    keywords = [
        "ibuprofen",
        "%",
        "w/w",
        "wt",
        "mg/g",
        "g/100 g",
        "mg/ml",
        "concentration",
        "drug loading",
        "active ingredient",
        "drug content",
        "composition",
        "table i",
        "table 1",
        "preparation",
    ]
    if record.formulation.label:
        keywords.append(record.formulation.label)
    if record.formulation.dosage_form:
        keywords.append(record.formulation.dosage_form)
    table_id = str(record.provenance.metadata.get("table_id", "") or "").strip()
    if table_id:
        keywords.append(table_id)
    return keywords


def _existing_api_support(record: Record, fallback_text: str) -> str:
    for item in record.evidence_items:
        if item.field_name == "api_concentration" and item.snippet:
            return item.snippet
    return fallback_text


def _collect_api_hints(
    records: list[Record],
) -> tuple[dict[tuple[str, str], tuple[float, str, str, str]], dict[str, tuple[float, str, str, str]]]:
    grouped_by_label: dict[tuple[str, str], list[tuple[float, str, str, str, int]]] = {}
    grouped_by_paper: dict[str, list[tuple[float, str, str, str, int]]] = {}
    for record in records:
        value = record.formulation.api_concentration_value
        if value is None:
            continue
        unit = record.formulation.api_concentration_unit
        basis = record.formulation.api_basis
        fallback_text = " ".join(part for part in (f"{float(value):g}", unit, basis, record.formulation.api_concentration_raw) if part)
        support = _existing_api_support(record, fallback_text)
        quality = api_concentration_quality(
            float(value),
            unit,
            basis,
            record.formulation.api_concentration_raw or support,
            prefer_strict_scope=True,
        )
        payload = (float(value), unit, basis, support, quality)
        label_key = _label_key(record)
        if label_key:
            grouped_by_label.setdefault((record.paper_id, label_key), []).append(payload)
        grouped_by_paper.setdefault(record.paper_id, []).append(payload)

    hints_by_label: dict[tuple[str, str], tuple[float, str, str, str]] = {}
    for key, entries in grouped_by_label.items():
        best = max(entries, key=lambda item: item[4])
        if best[4] >= STRICT_SHARED_API_HINT_MIN_QUALITY:
            hints_by_label[key] = best[:4]

    hints_by_paper: dict[str, tuple[float, str, str, str]] = {}
    for paper_id, entries in grouped_by_paper.items():
        best = max(entries, key=lambda item: item[4])
        if best[4] >= STRICT_SHARED_API_HINT_MIN_QUALITY:
            hints_by_paper[paper_id] = best[:4]

    return hints_by_label, hints_by_paper


def patch_api_concentration(
    records: Iterable[Record],
    output_jsonl: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Record]:
    """Patch missing API concentration fields from source fragments and shared hints."""

    patched: list[Record] = []
    record_list = list(records)
    api_hints_by_label, api_hints_by_paper = _collect_api_hints(record_list)
    for index, record in enumerate(record_list, start=1):
        if progress_callback:
            progress_callback(index - 1, record.paper_id, "patching api concentration")
        candidate = record.model_copy(deep=True)
        failure_codes = set(candidate.failure_reasons)
        needs_recovery = candidate.formulation.api_concentration_value is None or bool(
            failure_codes
            & {
                "missing_api_concentration",
                "ambiguous_api_concentration",
                "not_target_api_concentration",
            }
        )
        if not is_patchable(candidate) or not needs_recovery:
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        previous_signature = (
            candidate.formulation.api_concentration_value,
            candidate.formulation.api_concentration_unit,
            candidate.formulation.api_basis,
        )
        match_text = ""
        value = None
        unit = ""
        basis = ""
        label_key = _label_key(candidate)
        shared_hint = None
        if label_key:
            shared_hint = api_hints_by_label.get((candidate.paper_id, label_key))
        if shared_hint is None:
            shared_hint = api_hints_by_paper.get(candidate.paper_id)

        search_fragments = collect_text_fragments(candidate) + _component_fragments(candidate) + collect_source_fragments(
            candidate,
            keywords=_api_search_keywords(candidate),
            max_fragments=14,
        )
        value, unit, basis, match_text = infer_api_concentration_from_fragments(
            search_fragments,
            api_name=candidate.formulation.api_name or "ibuprofen",
            formulation_label=candidate.formulation.label,
            dosage_form=candidate.formulation.dosage_form,
            prefer_strict_scope=bool(
                failure_codes & {"ambiguous_api_concentration", "not_target_api_concentration"}
            ),
        )
        if value is None and shared_hint is not None:
            value, unit, basis, match_text = shared_hint

        if value is not None and not is_strict_api_concentration_hint(
            value,
            unit,
            basis,
            match_text,
            min_quality=STRICT_SHARED_API_HINT_MIN_QUALITY,
        ):
            value = None

        if value is None:
            append_patch(candidate, "patch_api_concentration", ["formulation.api_concentration"], "skipped", notes="no recoverable concentration fragment")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue
        current_quality = api_concentration_quality(
            candidate.formulation.api_concentration_value,
            candidate.formulation.api_concentration_unit,
            candidate.formulation.api_basis,
            candidate.formulation.api_concentration_raw,
            prefer_strict_scope=True,
        )
        new_quality = api_concentration_quality(
            value,
            unit,
            basis,
            match_text,
            prefer_strict_scope=True,
        )
        if previous_signature == (value, unit, basis):
            append_patch(candidate, "patch_api_concentration", ["formulation.api_concentration"], "skipped", notes="recovered concentration matches existing value")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue
        if candidate.formulation.api_concentration_value is not None and new_quality <= current_quality:
            append_patch(candidate, "patch_api_concentration", ["formulation.api_concentration"], "skipped", notes="recovered concentration is not stronger than existing value")
            patched.append(candidate)
            if progress_callback:
                progress_callback(index, record.paper_id, "skipped")
            continue

        candidate.formulation.api_concentration_value = value
        candidate.formulation.api_concentration_unit = unit
        candidate.formulation.api_basis = basis
        evidence = EvidenceItem(
            field_name="api_concentration",
            modality="metadata" if candidate.route == "unresolved" else candidate.route,  # type: ignore[arg-type]
            locator="patcher:patch_api_concentration:shared_hint" if shared_hint is not None else "patcher:patch_api_concentration",
            snippet=match_text,
            source_ref=candidate.doi or candidate.paper_id,
            confidence=0.7,
        )
        append_patch(
            candidate,
            "patch_api_concentration",
            ["formulation.api_concentration"],
            "applied",
            [evidence],
            notes="Recovered API concentration from shared hints." if shared_hint is not None else "Recovered API concentration from raw text.",
        )
        patched.append(candidate)
        if progress_callback:
            progress_callback(index, record.paper_id, "applied")

    if output_jsonl:
        write_records_jsonl(patched, output_jsonl)
    return patched
