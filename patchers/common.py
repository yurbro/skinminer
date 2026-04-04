"""Shared helpers for targeted evidence patchers."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from typing import Any

import fitz

from schemas.models import EvidenceItem, PatchMetadata, Record
from utils.source_cache import fetch_cached_text

PATCHER_USER_AGENT = {"User-Agent": "SkinMiner/patchers"}


def is_patchable(record: Record) -> bool:
    """Return whether a record should be considered for targeted patching."""

    return record.verification_status in {"unresolved", "rejected"} or bool(record.failure_reasons)


def _metadata_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (int, float, bool)):
        return [str(value)]
    if isinstance(value, dict):
        fragments: list[str] = []
        for item in value.values():
            fragments.extend(_metadata_strings(item))
        return fragments
    if isinstance(value, (list, tuple, set)):
        fragments = []
        for item in value:
            fragments.extend(_metadata_strings(item))
        return fragments
    return [str(value)]


def _dedupe_fragments(fragments: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for fragment in fragments:
        text = " ".join((fragment or "").split())
        if not text or text in seen:
            continue
        seen.add(text)
        deduped.append(text)
    return deduped


def collect_text_fragments(record: Record) -> list[str]:
    """Collect text fragments that patchers can search for recoverable evidence."""

    fragments = list(record.source_notes)
    fragments.append(record.provenance.route_notes)
    fragments.extend(_metadata_strings(record.provenance.metadata))
    if record.device:
        fragments.append(record.device)
    if record.barrier:
        fragments.append(record.barrier)
    if record.formulation.label:
        fragments.append(record.formulation.label)
    if record.formulation.api_name:
        fragments.append(record.formulation.api_name)
    if record.formulation.api_concentration_raw:
        fragments.append(record.formulation.api_concentration_raw)
    for component in record.formulation.components:
        if component.raw:
            fragments.append(component.raw)
        if component.note:
            fragments.append(component.note)
        if component.name:
            fragments.append(component.name)
    for item in record.evidence_items:
        if item.snippet:
            fragments.append(item.snippet)
        if item.locator:
            fragments.append(item.locator)
    return _dedupe_fragments(fragments)


def _fetch_remote_text(url: str, max_retries: int = 2) -> str:
    return fetch_cached_text(
        url,
        headers=PATCHER_USER_AGENT,
        timeout=45,
        max_retries=max_retries,
        namespace="patcher_structured_sources",
    )


def _html_blocks(text: str) -> list[str]:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"(?i)</(p|div|li|section|article|h1|h2|h3|h4|h5|h6|tr|caption|figcaption|table)>", "\n", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    blocks = [" ".join(chunk.split()) for chunk in re.split(r"\n+", unescape(cleaned))]
    return [block for block in blocks if len(block) >= 20]


def _xml_blocks(text: str) -> list[str]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return _html_blocks(text)

    relevant_tags = {"article-title", "abstract", "title", "p", "caption", "label", "td", "th"}
    blocks: list[str] = []
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        tag = element.tag.rsplit("}", 1)[-1].lower()
        if tag not in relevant_tags:
            continue
        value = " ".join(" ".join(element.itertext()).split())
        if len(value) >= 20:
            blocks.append(value)
    return _dedupe_fragments(blocks)


def _pdf_candidate_pages(record: Record, max_pages: int = 10) -> list[int]:
    pages = {page - 1 for page in record.provenance.source_pages if page and page > 0}
    pages.update(item.page - 1 for item in record.evidence_items if item.page and item.page > 0)
    expanded: set[int] = set()
    for page in pages:
        for neighbor in range(page - 1, page + 2):
            if neighbor >= 0:
                expanded.add(neighbor)
    ordered = sorted(expanded)
    if ordered:
        return ordered[:max_pages]
    return list(range(min(max_pages, 6)))


def _filter_fragments(blocks: list[str], keywords: list[str] | None, max_fragments: int) -> list[str]:
    if not keywords:
        return _dedupe_fragments(blocks)[:max_fragments]

    lowered_keywords = [keyword.lower() for keyword in keywords if keyword]
    scored: list[tuple[int, str]] = []
    for block in blocks:
        lowered = block.lower()
        score = sum(keyword in lowered for keyword in lowered_keywords)
        if score > 0:
            scored.append((score, block))
    scored.sort(key=lambda item: (-item[0], len(item[1])))
    return _dedupe_fragments([block for _, block in scored])[:max_fragments]


def collect_source_fragments(record: Record, keywords: list[str] | None = None, max_fragments: int = 12) -> list[str]:
    """Collect fragments directly from the underlying source document when available."""

    source_path = record.provenance.source_path or ""
    if not source_path:
        return []

    try:
        if record.provenance.source_format == "pdf" and Path(source_path).exists():
            document = fitz.open(source_path)
            blocks = [
                " ".join((document.load_page(page_index).get_text("text") or "").split())
                for page_index in _pdf_candidate_pages(record)
                if 0 <= page_index < document.page_count
            ]
            document.close()
            return _filter_fragments(blocks, keywords, max_fragments)

        if Path(source_path).exists():
            text = Path(source_path).read_text(encoding="utf-8", errors="ignore")
        elif source_path.startswith(("http://", "https://")):
            text = _fetch_remote_text(source_path)
        else:
            return []

        blocks = _xml_blocks(text) if record.provenance.source_format == "pmc_xml" else _html_blocks(text)
        return _filter_fragments(blocks, keywords, max_fragments)
    except Exception:
        return []


def append_patch(
    record: Record,
    patcher_name: str,
    patched_fields: list[str],
    status: str,
    evidence_items: list[EvidenceItem] | None = None,
    notes: str = "",
) -> None:
    """Append patch metadata and any new evidence to a record in place."""

    evidence_added = 0
    for item in evidence_items or []:
        record.evidence_items.append(item)
        evidence_added += 1
    record.patches.append(
        PatchMetadata(
            patcher_name=patcher_name,
            patched_fields=patched_fields,
            status=status,  # type: ignore[arg-type]
            evidence_added=evidence_added,
            notes=notes,
        )
    )
