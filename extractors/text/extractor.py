"""Standardized text-route extractor interface."""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from extractors.text.extract_fields import extract_text_fields
from extractors.text.normalize_fields import normalize_text_record
from extractors.text.page_selection import select_text_evidence_window
from schemas.models import ContentAccess, ExtractorRunContext, Record, RouteDecision
from utils.io import write_jsonl, write_records_csv, write_records_jsonl
from utils.resume import load_jsonl_if_exists, load_record_jsonl_if_exists
from utils.status_panel import ProgressCallback

LOGGER = logging.getLogger("skinminer.extractors.text")


def extract(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    policy: object | None,
    run_context: ExtractorRunContext,
) -> list[Record]:
    """Extract text-route candidate records for a single paper."""

    if route_decision.route not in {"text", "mixed"}:
        return []

    window = select_text_evidence_window(content_handle, route_decision)
    paper_extraction = extract_text_fields(window, route_decision, run_context)
    return [
        normalize_text_record(content_handle, route_decision, run_context, window, legacy_record, index)
        for index, legacy_record in enumerate(paper_extraction.records, start=1)
    ]


def extract_batch(
    content_route_pairs: Iterable[tuple[ContentAccess, RouteDecision]],
    policy: object | None,
    run_context: ExtractorRunContext,
    output_jsonl: str | Path | None = None,
    raw_output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
    checkpoint_every: int = 25,
) -> list[Record]:
    """Extract text-route records across a batch of routed papers."""

    selected_pairs = [
        (content_handle, route_decision)
        for content_handle, route_decision in content_route_pairs
        if route_decision.route in {"text", "mixed"}
    ]
    checkpoint_every = max(1, checkpoint_every)
    existing_raw_rows = load_jsonl_if_exists(raw_output_jsonl)
    processed_paper_ids = {str(row.get("paper_id", "") or "") for row in existing_raw_rows}
    existing_records = load_record_jsonl_if_exists(output_jsonl)
    records_by_paper: dict[str, list[Record]] = defaultdict(list)
    for record in existing_records:
        records_by_paper[record.paper_id].append(record)
    completed_before = sum(1 for content_handle, _ in selected_pairs if content_handle.paper_id in processed_paper_ids)
    if progress_callback and completed_before:
        progress_callback(completed_before, "resume", f"loaded={completed_before}")

    raw_rows = list(existing_raw_rows)
    remaining_pairs = [(content_handle, route_decision) for content_handle, route_decision in selected_pairs if content_handle.paper_id not in processed_paper_ids]
    for remaining_index, (content_handle, route_decision) in enumerate(remaining_pairs, start=1):
        completed_so_far = completed_before + remaining_index - 1
        current_item = content_handle.paper_id or content_handle.doi or route_decision.title[:60] or f"paper_{completed_so_far + 1}"
        if progress_callback:
            progress_callback(completed_so_far, current_item, "extracting text evidence")
        try:
            window = select_text_evidence_window(content_handle, route_decision)
            paper_extraction = extract_text_fields(window, route_decision, run_context)
            raw_rows.append(
                {
                    "paper_id": content_handle.paper_id,
                    "doi": content_handle.doi,
                    "title": route_decision.title,
                    "status": "ok",
                    "source_format": window.source_format,
                    "source_backend": window.source_backend,
                    "source_ref": window.source_ref,
                    "locator_mode": window.locator_mode,
                    "selected_pages": window.selected_pages,
                    "selected_locators": window.selected_locators,
                    "anchor_locators": window.anchor_locators,
                    "table_hint": window.table_hint,
                    **paper_extraction.model_dump(mode="json"),
                }
            )
            for record_index, legacy_record in enumerate(paper_extraction.records, start=1):
                records_by_paper[content_handle.paper_id].append(
                    normalize_text_record(content_handle, route_decision, run_context, window, legacy_record, record_index)
                )
            if progress_callback:
                progress_callback(completed_so_far + 1, current_item, f"records={len(paper_extraction.records)}")
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping text extraction for %s due to missing source: %s", current_item, exc)
            raw_rows.append(
                {
                    "paper_id": content_handle.paper_id,
                    "doi": content_handle.doi,
                    "title": route_decision.title,
                    "status": "source_error",
                    "error_type": type(exc).__name__,
                    "error_detail": str(exc),
                }
            )
            if progress_callback:
                progress_callback(completed_so_far + 1, current_item, f"skipped:{type(exc).__name__}")

        completed_total = completed_so_far + 1
        if completed_total % checkpoint_every == 0 or completed_total == len(selected_pairs):
            ordered_records = [
                record
                for content_handle, _route_decision in selected_pairs
                for record in records_by_paper.get(content_handle.paper_id, [])
            ]
            if raw_output_jsonl:
                write_jsonl(raw_rows, raw_output_jsonl)
            if output_jsonl:
                write_records_jsonl(ordered_records, output_jsonl)

    records = [
        record
        for content_handle, _route_decision in selected_pairs
        for record in records_by_paper.get(content_handle.paper_id, [])
    ]
    if raw_output_jsonl:
        write_jsonl(raw_rows, raw_output_jsonl)
    if output_jsonl:
        write_records_jsonl(records, output_jsonl)
    if output_csv:
        write_records_csv(records, output_csv)
    return records


def extract_text_records(
    routed_rows: Iterable[dict],
    model: str = "gpt-4o-mini",
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    raw_output_jsonl: str | Path | None = None,
) -> list[Record]:
    """Backward-compatible batch wrapper around the standardized text extractor."""

    pairs: list[tuple[ContentAccess, RouteDecision]] = []
    for row in routed_rows:
        content_handle = ContentAccess(
            paper_id=str(row.get("paper_id", "") or ""),
            doi=str(row.get("doi", "") or ""),
            title=str(row.get("title", "") or ""),
            preferred_format="pdf",
            available_formats=["pdf"],
            local_paths={"pdf": str(row.get("pdf_path", "") or "")},
            status="downloaded" if row.get("pdf_path") else "resolved",
        )
        route_decision = RouteDecision.model_validate(
            {
                "paper_id": content_handle.paper_id,
                "doi": content_handle.doi,
                "title": content_handle.title,
                "route": row.get("route", "unresolved"),
                "route_confidence": row.get("route_confidence"),
                "endpoint_carrier": row.get("endpoint_carrier", "unknown"),
                "formulation_carrier": row.get("formulation_carrier", "unknown"),
                "anchor_evidence": row.get("anchor_evidence", []),
                "notes": row.get("notes", ""),
                "raw_labels": row.get("raw_labels", {}),
            }
        )
        pairs.append((content_handle, route_decision))

    run_context = ExtractorRunContext(
        run_id="legacy_text_batch",
        model_name=model,
        output_dir=str(Path(output_jsonl).parent) if output_jsonl else ".",
        notes=["Backward-compatible text batch wrapper."],
        fail_on_malformed_output=False,
    )
    return extract_batch(
        pairs,
        policy=None,
        run_context=run_context,
        output_jsonl=output_jsonl,
        raw_output_jsonl=raw_output_jsonl,
        output_csv=output_csv,
    )
