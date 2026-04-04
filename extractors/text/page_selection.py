"""Evidence-window selection for structured-first text extraction."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from typing import Literal

import fitz
from pydantic import BaseModel, Field

from extractors.common import has_local_pdf, require_pdf_path
from schemas.models import ContentAccess, RouteDecision
from utils.source_cache import fetch_cached_text

STRUCTURED_SOURCE_USER_AGENT = {"User-Agent": "SkinMiner/text-extractor"}

FORM_KW = [
    "formulation",
    "composition",
    "ingredients",
    "vehicle",
    "base",
    "gel",
    "cream",
    "ointment",
    "emulsion",
    "microemulsion",
    "hydrogel",
    "% w/w",
    "w/w",
    "mg/g",
    "table",
]
END_KW = [
    "cumulative",
    "amount permeated",
    "amount released",
    "permeation",
    "release",
    "flux",
    "jss",
    "steady-state",
    "ug/cm",
    "mg/cm",
    "ng/cm",
    "table",
    "results",
    "after",
    "hour",
    "hours",
    "time",
]
CELL_KW = ["franz", "diffusion cell", "permeation cell", "vertical diffusion", "donor", "receptor"]
AREA_KW = ["diffusion area", "effective area", "exposed area", "cm2", "cm^2", "cm2"]


class TextEvidenceWindow(BaseModel):
    """Selected evidence window and diagnostics for text extraction."""

    source_format: Literal["pmc_xml", "html", "pdf", "unresolved"] = "unresolved"
    source_backend: str = ""
    source_ref: str = ""
    locator_mode: Literal["page", "block"] = "page"
    anchor_locators: list[str] = Field(default_factory=list)
    selected_pages: list[int] = Field(default_factory=list)
    selected_locators: list[str] = Field(default_factory=list)
    table_hint: str = ""
    content_text: str = ""
    score_debug: dict[str, int] = Field(default_factory=dict)


def parse_anchor_pages(text: str) -> list[int]:
    """Parse 0-indexed anchor pages from locator text."""

    pages: set[int] = set()
    for match in re.finditer(r"\b(?:page|p\.?)\s*(\d+)\b", text or "", flags=re.IGNORECASE):
        page_no = int(match.group(1))
        if page_no > 0:
            pages.add(page_no - 1)
    return sorted(pages)


def parse_anchor_blocks(text: str) -> list[int]:
    """Parse 0-indexed anchor blocks from locator text."""

    blocks: set[int] = set()
    for match in re.finditer(r"\bblock\s*(\d+)\b", text or "", flags=re.IGNORECASE):
        block_no = int(match.group(1))
        if block_no > 0:
            blocks.add(block_no - 1)
    return sorted(blocks)


def infer_table_hint(where_endpoint: str) -> str | None:
    """Infer a table reference hint from router endpoint locator text."""

    match = re.search(r"(table\s*\d+)", where_endpoint or "", flags=re.IGNORECASE)
    return match.group(1) if match else None


def _normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def _score(text: str, keywords: list[str]) -> int:
    lowered = f" {text.lower()} "
    score = 0
    for keyword in keywords:
        if keyword in lowered:
            score += 2 if keyword in {"table", "% w/w", "mg/g", "cumulative", "diffusion area", "franz"} else 1
    return score


def _content_score(text: str) -> int:
    return _score(text, FORM_KW) + _score(text, END_KW) + _score(text, CELL_KW) + _score(text, AREA_KW)


def _fetch_remote_text(url: str, max_retries: int = 3) -> str:
    return fetch_cached_text(
        url,
        headers=STRUCTURED_SOURCE_USER_AGENT,
        timeout=60,
        max_retries=max_retries,
        namespace="text_structured_sources",
    )


def _load_text_from_ref(ref: str, location: str) -> str:
    if location == "local":
        return Path(ref).read_text(encoding="utf-8", errors="ignore")
    return _fetch_remote_text(ref)


def _extract_html_blocks(raw_html: str) -> list[str]:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw_html)
    cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"(?i)</(p|div|li|section|article|h1|h2|h3|h4|h5|h6|tr|caption|figcaption|table)>", "\n", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    text = unescape(cleaned)
    blocks = [_normalize_text(chunk) for chunk in re.split(r"\n+", text)]
    return [block for block in blocks if len(block) >= 20]


def _extract_xml_blocks(raw_xml: str) -> list[str]:
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError:
        fallback = re.sub(r"(?s)<[^>]+>", " ", raw_xml)
        blocks = [_normalize_text(chunk) for chunk in re.split(r"\n+", unescape(fallback))]
        return [block for block in blocks if len(block) >= 20]

    blocks: list[str] = []
    relevant_tags = {
        "article-title",
        "abstract",
        "title",
        "p",
        "caption",
        "label",
        "td",
        "th",
    }
    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        tag = element.tag.rsplit("}", 1)[-1].lower()
        if tag not in relevant_tags:
            continue
        text = _normalize_text(" ".join(element.itertext()))
        if len(text) < 20:
            continue
        if tag in {"article-title", "title", "caption", "label"}:
            blocks.append(f"{tag.upper()}: {text}")
        else:
            blocks.append(text)

    deduped: list[str] = []
    seen: set[str] = set()
    for block in blocks:
        if block not in seen:
            deduped.append(block)
            seen.add(block)
    return deduped


def _structured_candidates(content_handle: ContentAccess) -> list[tuple[str, str, str]]:
    candidates: list[tuple[str, str, str]] = []
    for fmt in ("pmc_xml", "html"):
        local_ref = str(content_handle.local_paths.get(fmt, "") or "").strip()
        if local_ref and Path(local_ref).exists():
            candidates.append((fmt, "local", local_ref))
        remote_ref = str(content_handle.access_urls.get(fmt, "") or "").strip()
        if remote_ref:
            candidates.append((fmt, "remote", remote_ref))
    return candidates


def _truncate_content(parts: list[str], max_chars_total: int) -> str:
    if not parts:
        return ""
    text = "\n\n".join(parts)
    return text[:max_chars_total].strip()


def _build_structured_window(
    blocks: list[str],
    *,
    fmt: str,
    location: str,
    ref: str,
    anchor_blocks: list[int],
    table_hint: str,
    max_blocks_total: int,
    always_include_first_blocks: int,
    anchor_neighbor: int,
    max_chars_total: int,
) -> TextEvidenceWindow | None:
    if not blocks:
        return None

    scores = [_content_score(block) for block in blocks]
    has_table_tag = [table_hint.lower() in block.lower() if table_hint else False for block in blocks]

    selected: set[int] = set(range(min(always_include_first_blocks, len(blocks))))
    for anchor in anchor_blocks:
        for block_index in range(anchor - anchor_neighbor, anchor + anchor_neighbor + 1):
            if 0 <= block_index < len(blocks):
                selected.add(block_index)

    if table_hint:
        for index, present in enumerate(has_table_tag):
            if present:
                for block_index in range(index - 2, index + 3):
                    if 0 <= block_index < len(blocks):
                        selected.add(block_index)

    ranked = sorted(((scores[index], index) for index in range(len(blocks)) if scores[index] > 0), reverse=True)
    for _, index in ranked:
        selected.add(index)
        if len(selected) >= max_blocks_total:
            break

    if not selected:
        selected = set(range(min(6, len(blocks))))

    ordered_blocks = sorted(selected)
    parts = [
        f"--- BLOCK {index + 1} (score={scores[index]}, source={fmt}_{location}) ---\n{blocks[index]}"
        for index in ordered_blocks
    ]
    return TextEvidenceWindow(
        source_format=fmt,
        source_backend=f"{fmt}_{location}",
        source_ref=ref,
        locator_mode="block",
        anchor_locators=[f"block {index + 1}" for index in anchor_blocks],
        selected_locators=[f"block {index + 1}" for index in ordered_blocks],
        table_hint=table_hint,
        content_text=_truncate_content(parts, max_chars_total),
        score_debug={f"block {index + 1}": scores[index] for index in ordered_blocks},
    )


def _select_structured_evidence_window(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    *,
    max_blocks_total: int,
    always_include_first_blocks: int,
    anchor_neighbor: int,
    max_chars_total: int,
) -> TextEvidenceWindow | None:
    raw_labels = route_decision.raw_labels
    anchor_blocks = sorted(
        set(
            parse_anchor_blocks(str(raw_labels.get("where_endpoint", "")))
            + parse_anchor_blocks(str(raw_labels.get("where_franz", "")))
            + parse_anchor_blocks(str(raw_labels.get("where_diffusion_cell", "")))
        )
    )
    table_hint = infer_table_hint(str(raw_labels.get("where_endpoint", ""))) or ""

    for fmt, location, ref in _structured_candidates(content_handle):
        try:
            raw_text = _load_text_from_ref(ref, location)
            blocks = _extract_xml_blocks(raw_text) if fmt == "pmc_xml" else _extract_html_blocks(raw_text)
            window = _build_structured_window(
                blocks,
                fmt=fmt,
                location=location,
                ref=ref,
                anchor_blocks=anchor_blocks,
                table_hint=table_hint,
                max_blocks_total=max_blocks_total,
                always_include_first_blocks=always_include_first_blocks,
                anchor_neighbor=anchor_neighbor,
                max_chars_total=max_chars_total,
            )
            if window:
                return window
        except Exception:
            continue
    return None


def _select_pdf_evidence_window(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    *,
    max_pages_total: int,
    always_include_first_pages: int,
    anchor_neighbor: int,
    max_chars_total: int,
) -> TextEvidenceWindow:
    pdf_path = require_pdf_path(content_handle)
    raw_labels = route_decision.raw_labels
    anchors = sorted(
        set(
            parse_anchor_pages(str(raw_labels.get("where_endpoint", "")))
            + parse_anchor_pages(str(raw_labels.get("where_franz", "")))
            + parse_anchor_pages(str(raw_labels.get("where_diffusion_cell", "")))
        )
    )
    table_hint = infer_table_hint(str(raw_labels.get("where_endpoint", ""))) or ""

    document = fitz.open(pdf_path)
    scores: list[int] = []
    page_texts: list[str] = []
    has_table_tag: list[bool] = []
    for index in range(document.page_count):
        text = document.load_page(index).get_text("text") or ""
        page_texts.append(text)
        score = _content_score(text)
        scores.append(score)
        has_table_tag.append(table_hint.lower() in text.lower() if table_hint else False)

    selected: set[int] = set(range(min(always_include_first_pages, document.page_count)))
    for anchor in anchors:
        for page_index in range(anchor - anchor_neighbor, anchor + anchor_neighbor + 1):
            if 0 <= page_index < document.page_count:
                selected.add(page_index)

    if table_hint:
        for index, present in enumerate(has_table_tag):
            if present:
                for page_index in range(index - 2, index + 3):
                    if 0 <= page_index < document.page_count:
                        selected.add(page_index)

    ranked = sorted(((scores[index], index) for index in range(document.page_count) if scores[index] > 0), reverse=True)
    for _, index in ranked:
        selected.add(index)
        if len(selected) >= max_pages_total:
            break

    if not selected:
        selected = set(range(min(3, document.page_count)))

    ordered_pages = sorted(selected)
    parts = [f"--- PAGE {index + 1} (score={scores[index]}) ---\n{page_texts[index]}" for index in ordered_pages]
    document.close()
    return TextEvidenceWindow(
        source_format="pdf",
        source_backend="pdf_local",
        source_ref=pdf_path,
        locator_mode="page",
        anchor_locators=[f"page {index + 1}" for index in anchors],
        selected_pages=[page + 1 for page in ordered_pages],
        selected_locators=[f"page {index + 1}" for index in ordered_pages],
        table_hint=table_hint,
        content_text=_truncate_content(parts, max_chars_total),
        score_debug={f"page {page + 1}": scores[page] for page in ordered_pages},
    )


def select_text_evidence_window(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    max_pages_total: int = 18,
    always_include_first_pages: int = 2,
    anchor_neighbor: int = 2,
    max_chars_total: int = 32_000,
    max_blocks_total: int = 24,
    always_include_first_blocks: int = 4,
) -> TextEvidenceWindow:
    """Select a structured-first evidence window, with PDF fallback."""

    structured_window = _select_structured_evidence_window(
        content_handle,
        route_decision,
        max_blocks_total=max_blocks_total,
        always_include_first_blocks=always_include_first_blocks,
        anchor_neighbor=anchor_neighbor,
        max_chars_total=max_chars_total,
    )
    if structured_window:
        return structured_window
    if not has_local_pdf(content_handle):
        raise FileNotFoundError(
            "No usable structured text source could be loaded and no local PDF is available "
            f"for paper_id={content_handle.paper_id}"
        )
    return _select_pdf_evidence_window(
        content_handle,
        route_decision,
        max_pages_total=max_pages_total,
        always_include_first_pages=always_include_first_pages,
        anchor_neighbor=anchor_neighbor,
        max_chars_total=max_chars_total,
    )
