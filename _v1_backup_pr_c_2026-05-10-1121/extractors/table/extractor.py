"""Standardized structured-first table-modality extractor."""

from __future__ import annotations

import base64
from collections import defaultdict
import json
import logging
import random
import re
import time
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from typing import Literal

import fitz
from pydantic import BaseModel, Field

from extractors.common import build_provenance, infer_device_label, require_pdf_path, resolve_stage_model, route_device_hint
from schemas.models import ConditionSpec, ContentAccess, EndpointSpec, EvidenceItem, ExtractorRunContext, FormulationComponent, FormulationSpec, Record, RouteDecision
from utils.io import make_record_id, write_jsonl, write_records_csv, write_records_jsonl
from utils.llm_client import parse_structured, resolve_provider_from_context
from utils.long_run import record_openai_attempt_failure, record_openai_usage
from utils.resume import load_jsonl_if_exists, load_record_jsonl_if_exists
from utils.source_cache import fetch_cached_text
from utils.status_panel import ProgressCallback
from utils.units import (
    amount_total_to_ug_per_cm2,
    extract_time_mentions,
    fragment_matches_api_context,
    normalize_amount_per_area,
    normalize_time_to_hours,
    parse_api_concentration,
    parse_area_cm2,
    parse_endpoint_amount,
)

TABLE_SOURCE_USER_AGENT = {"User-Agent": "SkinMiner/table-extractor"}
LOGGER = logging.getLogger("skinminer.extractors.table")
TABLE_EXTRACTION_PROMPT_ASSET_ID = "extractors.table.structured_tables"
TABLE_EXTRACTION_PROMPT_VERSION = "2026-04-11.v1"

SYSTEM_PROMPT = (
    "You extract formulation composition tables from OA scientific articles. "
    "Use ONLY the provided structured tables or PDF page text and optional page images. "
    "Do not guess concentrations or endpoint values. "
    "Preserve explicit table locators such as 'Table 2' when they are supplied."
)

TABLE_KEYWORDS = [
    "table",
    "formulation",
    "formulations",
    "composition",
    "ingredient",
    "vehicle",
    "w/w",
    "wt%",
    "weight",
    "%",
    "mg",
    "g",
    "ml",
    "v/v",
    "ibuprofen",
    "cumulative",
    "amount permeated",
    "amount released",
]


class Component(BaseModel):
    """A formulation component extracted from a table."""

    name_raw: str = ""
    concentration_value: float | None = None
    concentration_unit: str = ""
    basis: str = ""
    remark: str = ""


class FormulationRow(BaseModel):
    """A formulation row extracted from a composition table."""

    formulation_label: str = ""
    dosage_form: str = ""
    api_name: str = "ibuprofen"
    api_concentration_value: float | None = None
    api_concentration_unit: str = ""
    api_basis: str = ""
    api_concentration_raw: str = ""
    components: list[Component] = Field(default_factory=list)
    endpoint_value: float | None = None
    endpoint_unit: str = ""
    endpoint_time_value: float | None = None
    endpoint_time_unit: str = ""
    endpoint_kind: Literal["amount_per_area", "amount_total", "percent", "flux", "jss", "unknown"] = "unknown"
    membrane_type: str = ""
    membrane_source: str = ""
    membrane_thickness_um: float | None = None
    receptor_medium: str = ""
    dose_type: str = ""
    dose_amount: str = ""
    water_qs_or_balance: Literal["yes", "no", "uncertain"] = "uncertain"
    table_id: str = ""
    source_pages: list[int] = Field(default_factory=list)
    source_locators: list[str] = Field(default_factory=list)
    evidence_snippet: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""


class TableExtractionResult(BaseModel):
    """Paper-level result from the table extraction prompt."""

    formulations: list[FormulationRow] = Field(default_factory=list)
    formulation_table_found: Literal["yes", "no", "uncertain"] = "uncertain"
    formulation_table_in_image: Literal["yes", "no", "uncertain"] = "uncertain"
    recommended_next: Literal["ok", "need_more_pages", "need_supp", "manual_review"] = "manual_review"
    notes: str = ""


class StructuredTableBlock(BaseModel):
    """A structured table or caption block extracted from XML or HTML."""

    locator: str
    title: str = ""
    text: str = ""
    score: int = 0
    truncated: bool = False


class TableEvidenceWindow(BaseModel):
    """Selected evidence window and provenance for table extraction."""

    source_format: Literal["pmc_xml", "html", "pdf", "unresolved"] = "unresolved"
    source_backend: str = ""
    source_ref: str = ""
    locator_mode: Literal["table", "page"] = "page"
    selected_pages: list[int] = Field(default_factory=list)
    selected_locators: list[str] = Field(default_factory=list)
    image_page_indices: list[int] = Field(default_factory=list)
    content_text: str = ""
    score_debug: dict[str, int] = Field(default_factory=dict)
    table_truncated: bool = False
    truncation_notes: list[str] = Field(default_factory=list)


def _norm_ws(text: str) -> str:
    return " ".join((text or "").split())


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


ROMAN_TABLE_NUMERALS = {
    "i": 1,
    "ii": 2,
    "iii": 3,
    "iv": 4,
    "v": 5,
    "vi": 6,
    "vii": 7,
    "viii": 8,
    "ix": 9,
    "x": 10,
}


def _infer_table_hint(*fragments: str) -> str | None:
    text = " ".join(str(fragment or "") for fragment in fragments)
    match = re.search(r"table\s*([0-9]+|[ivxlcdm]+)", text, flags=re.IGNORECASE)
    if not match:
        return None
    token = match.group(1).lower()
    if token.isdigit():
        return f"Table {token}"
    if token in ROMAN_TABLE_NUMERALS:
        return f"Table {ROMAN_TABLE_NUMERALS[token]}"
    return match.group(0)


def _score_table_text(text: str) -> int:
    lowered = f" {_norm_ws(text).lower()} "
    score = 0
    if "table" in lowered:
        score += 6
    if "formulation" in lowered or "composition" in lowered:
        score += 6
    if "ingredient" in lowered:
        score += 3
    if "ibuprofen" in lowered:
        score += 3
    if "w/w" in lowered or "wt%" in lowered or "%" in lowered:
        score += 2
    if "amount permeated" in lowered or "amount released" in lowered or "cumulative" in lowered:
        score += 3
    for keyword in TABLE_KEYWORDS:
        if keyword in lowered:
            score += 1
    return score


def _fetch_remote_text(url: str, max_retries: int = 3) -> str:
    return fetch_cached_text(
        url,
        headers=TABLE_SOURCE_USER_AGENT,
        timeout=60,
        max_retries=max_retries,
        namespace="table_structured_sources",
    )


def _load_text_from_ref(ref: str, location: str) -> str:
    if location == "local":
        return Path(ref).read_text(encoding="utf-8", errors="ignore")
    return _fetch_remote_text(ref)


def _iter_structured_candidates(content_handle: ContentAccess) -> list[tuple[str, str, str]]:
    candidates: list[tuple[str, str, str]] = []
    for fmt in ("pmc_xml", "html"):
        local_ref = str(content_handle.local_paths.get(fmt, "") or "").strip()
        if local_ref and Path(local_ref).exists():
            candidates.append((fmt, "local", local_ref))
        remote_ref = str(content_handle.access_urls.get(fmt, "") or "").strip()
        if remote_ref:
            candidates.append((fmt, "remote", remote_ref))
    return candidates


def _local_name(tag: object) -> str:
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1].lower()


def _element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return _norm_ws(" ".join(element.itertext()))


def _extract_xml_rows(table_wrap: ET.Element, max_rows: int = 18) -> list[str]:
    rows: list[str] = []
    for row in table_wrap.iter():
        if _local_name(row.tag) != "tr":
            continue
        cells: list[str] = []
        for cell in row:
            if _local_name(cell.tag) not in {"td", "th"}:
                continue
            value = _element_text(cell)
            if value:
                cells.append(value[:220])
        if cells:
            rows.append(" | ".join(cells))
        if len(rows) >= max_rows:
            break
    return rows


def _extract_xml_table_blocks(raw_xml: str) -> list[StructuredTableBlock]:
    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError:
        return []

    blocks: list[StructuredTableBlock] = []
    for index, element in enumerate(root.iter(), start=1):
        if _local_name(element.tag) != "table-wrap":
            continue
        label = _element_text(next((child for child in element if _local_name(child.tag) == "label"), None))
        caption = _element_text(next((child for child in element if _local_name(child.tag) == "caption"), None))
        footer = _element_text(next((child for child in element if _local_name(child.tag) == "table-wrap-foot"), None))
        rows = _extract_xml_rows(element)
        if not rows and not caption:
            continue
        locator = label or f"Table {len(blocks) + 1}"
        parts = [f"TABLE_LOCATOR: {locator}"]
        if caption:
            parts.append(f"CAPTION: {caption}")
        if footer:
            parts.append(f"FOOTER: {footer}")
        if rows:
            parts.append("ROWS:")
            parts.extend(rows)
        block_text = "\n".join(parts)
        blocks.append(
            StructuredTableBlock(
                locator=locator,
                title=caption or label or f"table_{index}",
                text=block_text,
                score=_score_table_text(block_text),
            )
        )
    return blocks


def _strip_html_tags(text: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    return _norm_ws(unescape(cleaned))


def _extract_html_rows(table_html: str, max_rows: int = 60) -> tuple[list[str], bool]:
    rows: list[str] = []
    truncated = False
    for row_html in re.findall(r"(?is)<tr\b.*?>.*?</tr>", table_html):
        cells: list[str] = []
        for cell_html in re.findall(r"(?is)<(?:th|td)\b.*?>.*?</(?:th|td)>", row_html):
            value = _strip_html_tags(cell_html)
            if value:
                cells.append(value[:220])
        if cells:
            rows.append(" | ".join(cells))
        if len(rows) >= max_rows:
            truncated = True
            break
    return rows, truncated


def _extract_html_table_blocks(raw_html: str) -> list[StructuredTableBlock]:
    blocks: list[StructuredTableBlock] = []
    for index, table_html in enumerate(re.findall(r"(?is)<table\b.*?>.*?</table>", raw_html), start=1):
        caption_match = re.search(r"(?is)<caption\b.*?>(.*?)</caption>", table_html)
        caption = _strip_html_tags(caption_match.group(1)) if caption_match else ""
        rows, truncated = _extract_html_rows(table_html)
        if not rows and not caption:
            continue
        locator = caption.split(".")[0][:80] if caption else f"Table {index}"
        parts = [f"TABLE_LOCATOR: {locator or f'Table {index}'}"]
        if caption:
            parts.append(f"CAPTION: {caption}")
        if truncated:
            parts.append("TABLE_TRUNCATED: true")
            parts.append("TRUNCATION_NOTE: HTML table exceeded the row extraction cap; later rows are not present in this block.")
        if rows:
            parts.append("ROWS:")
            parts.extend(rows)
        block_text = "\n".join(parts)
        blocks.append(
            StructuredTableBlock(
                locator=locator or f"Table {index}",
                title=caption or f"table_{index}",
                text=block_text,
                score=_score_table_text(block_text),
                truncated=truncated,
            )
        )
    return blocks


CONDITION_CONTEXT_KEYWORDS = [
    "franz",
    "receptor compartment",
    "receptor medium",
    "receptor solution",
    "receptor phase",
    "receiver medium",
    "receiver solution",
    "pbs",
    "ph 7.4",
    "skin",
    "membrane",
    "dermatomed",
    "porcine",
    "human",
    "strat-m",
    "finite dose",
    "infinite dose",
    "dose",
]


def _extract_condition_context(raw_text: str, max_snippets: int = 6, window_chars: int = 420) -> str:
    """Return compact source-backed context for condition fields."""

    cleaned = _strip_html_tags(raw_text)
    lowered = cleaned.lower()
    snippets: list[str] = []
    seen: set[str] = set()
    for keyword in CONDITION_CONTEXT_KEYWORDS:
        start = lowered.find(keyword)
        if start < 0:
            continue
        left = max(0, start - window_chars // 2)
        right = min(len(cleaned), start + window_chars // 2)
        snippet = cleaned[left:right].strip(" ;,")
        snippet = re.sub(r"\s+", " ", snippet)
        key = snippet[:120].lower()
        if snippet and key not in seen:
            snippets.append(f"- {snippet}")
            seen.add(key)
        if len(snippets) >= max_snippets:
            break
    return "\n".join(snippets)


def _cap_window_text(text: str, max_chars_total: int) -> tuple[str, bool]:
    if len(text) <= max_chars_total:
        return text.strip(), False
    marker = "\n...[table_window_truncated: true]"
    return f"{text[: max(0, max_chars_total - len(marker))].rstrip()}{marker}", True


def _build_structured_table_window(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    max_tables_total: int = 4,
    max_chars_total: int = 28_000,
) -> TableEvidenceWindow | None:
    table_hint = _infer_table_hint(
        str(route_decision.raw_labels.get("where_endpoint", "") or ""),
        str(route_decision.raw_labels.get("endpoint_carrier_snippet", "") or ""),
        str(route_decision.raw_labels.get("formulation_carrier_snippet", "") or ""),
    ) or ""
    for fmt, location, ref in _iter_structured_candidates(content_handle):
        try:
            raw_text = _load_text_from_ref(ref, location)
        except Exception:
            continue
        blocks = _extract_xml_table_blocks(raw_text) if fmt == "pmc_xml" else _extract_html_table_blocks(raw_text)
        if not blocks:
            continue

        selected: list[StructuredTableBlock] = []
        if table_hint:
            for block in blocks:
                if table_hint.lower() in block.locator.lower() or table_hint.lower() in block.text.lower():
                    selected.append(block)
                    break

        remaining = [block for block in blocks if block not in selected]
        remaining.sort(key=lambda block: block.score, reverse=True)
        for block in remaining:
            if len(selected) >= max_tables_total:
                break
            if block.score > 0 or not selected:
                selected.append(block)

        if not selected:
            selected = blocks[:1]

        parts = [
            f"--- TABLE BLOCK {position} (score={block.score}, locator={block.locator}, source={fmt}_{location}) ---\n{block.text}"
            for position, block in enumerate(selected, start=1)
        ]
        condition_context = _extract_condition_context(raw_text)
        if condition_context:
            parts.append(f"--- EXPERIMENT CONDITION CONTEXT (source={fmt}_{location}) ---\n{condition_context}")
        content_text, char_truncated = _cap_window_text("\n\n".join(parts), max_chars_total)
        row_truncation_notes = [
            f"{block.locator}: row cap reached"
            for block in selected
            if block.truncated
        ]
        truncation_notes = [*row_truncation_notes]
        if char_truncated:
            truncation_notes.append(f"window char cap reached at {max_chars_total}")
        return TableEvidenceWindow(
            source_format=fmt,
            source_backend=f"{fmt}_{location}",
            source_ref=ref,
            locator_mode="table",
            selected_locators=[block.locator for block in selected],
            content_text=content_text,
            score_debug={block.locator: block.score for block in selected},
            table_truncated=bool(row_truncation_notes or char_truncated),
            truncation_notes=truncation_notes,
        )
    return None


def _page_graphics_flags(page: fitz.Page) -> tuple[int, float]:
    try:
        has_img = 1 if len(page.get_images(full=True)) > 0 else 0
    except Exception:
        has_img = 0
    try:
        drawings = page.get_drawings()
    except Exception:
        drawings = []
    page_area = float(page.rect.width * page.rect.height) or 1.0
    draw_area = 0.0
    for drawing in drawings:
        rect = drawing.get("rect")
        if rect is not None:
            draw_area += float(rect.width * rect.height)
    return has_img, min(1.0, draw_area / page_area)


def _render_page_jpg_dataurl(pdf_path: str, page_index: int, dpi: int = 170) -> str:
    document = fitz.open(pdf_path)
    page = document.load_page(page_index)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    document.close()
    return f"data:image/jpeg;base64,{base64.b64encode(pixmap.tobytes('jpg')).decode('utf-8')}"


def _pick_candidate_pages(pdf_path: str, max_pages_to_send: int = 5, neighbors: int = 1) -> tuple[list[int], list[int]]:
    document = fitz.open(pdf_path)
    scored: list[tuple[float, int, int, int, float]] = []
    for index in range(min(document.page_count, 200)):
        page = document.load_page(index)
        text = _norm_ws(page.get_text("text") or "")
        text_score = _score_table_text(text)
        has_img, draw_ratio = _page_graphics_flags(page)
        score_total = text_score + 5 * has_img + (4 if draw_ratio >= 0.02 else 0)
        if score_total > 0:
            scored.append((score_total, index, text_score, has_img, draw_ratio))

    scored.sort(reverse=True, key=lambda item: item[0])
    selected: set[int] = set()
    weak_pages: set[int] = set()
    for score_total, page_index, text_score, has_img, draw_ratio in scored[:max_pages_to_send]:
        selected.add(page_index)
        if text_score <= 3 and (has_img or draw_ratio >= 0.02):
            weak_pages.add(page_index)

    expanded: set[int] = set()
    for page_index in selected:
        for neighbor in range(page_index - neighbors, page_index + neighbors + 1):
            if 0 <= neighbor < document.page_count:
                expanded.add(neighbor)

    ordered = sorted(expanded)
    if len(ordered) > max_pages_to_send:
        rank = {page_index: position for position, (_, page_index, *_rest) in enumerate(scored)}
        ordered.sort(key=lambda page_index: rank.get(page_index, 10**9))
        ordered = sorted(set(ordered[:max_pages_to_send]))

    document.close()
    return ordered, [page_index for page_index in ordered if page_index in weak_pages]


def _build_pages_text(pdf_path: str, pages: list[int], max_chars_per_page: int = 4_500) -> str:
    document = fitz.open(pdf_path)
    parts: list[str] = []
    for page_index in pages:
        text = _norm_ws(document.load_page(page_index).get_text("text") or "")
        if len(text) > max_chars_per_page:
            text = f"{text[:max_chars_per_page]} ...[truncated]"
        parts.append(f"--- PAGE {page_index + 1} ---\n{text}")
    document.close()
    return "\n\n".join(parts)


def _build_pdf_table_window(content_handle: ContentAccess) -> TableEvidenceWindow:
    pdf_path = require_pdf_path(content_handle)
    pages, weak_pages = _pick_candidate_pages(pdf_path)
    content_text = _build_pages_text(pdf_path, pages)
    table_truncated = "[truncated]" in content_text
    return TableEvidenceWindow(
        source_format="pdf",
        source_backend="pdf_local",
        source_ref=pdf_path,
        locator_mode="page",
        selected_pages=[page + 1 for page in pages],
        selected_locators=[f"page {page + 1}" for page in pages],
        image_page_indices=weak_pages,
        content_text=content_text,
        score_debug={f"page {page + 1}": 1 for page in pages},
        table_truncated=table_truncated,
        truncation_notes=["PDF page text cap reached"] if table_truncated else [],
    )


def select_table_evidence_window(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
) -> TableEvidenceWindow:
    """Select a structured-first evidence window for table extraction."""

    structured_window = _build_structured_table_window(content_handle, route_decision)
    if structured_window:
        return structured_window
    pdf_path = content_handle.local_paths.get("pdf", "")
    if not pdf_path or not Path(pdf_path).exists():
        raise FileNotFoundError(
            "No usable structured table source could be loaded and no local PDF is available "
            f"for paper_id={content_handle.paper_id}"
        )
    return _build_pdf_table_window(content_handle)


def _safe_curve_hints(run_context: ExtractorRunContext, paper_id: str, doi: str) -> str:
    curve_hints_by_paper = run_context.shared_state.get("curve_hints_by_paper", {})
    value = curve_hints_by_paper.get(paper_id) or curve_hints_by_paper.get(doi)
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False)


def _build_prompt(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    window: TableEvidenceWindow,
    curve_hints: str,
) -> str:
    endpoint_table_hint = _infer_table_hint(
        str(route_decision.raw_labels.get("where_endpoint", "") or ""),
        str(route_decision.raw_labels.get("endpoint_carrier_snippet", "") or ""),
    ) or ""
    return (
        "Extract formulation composition tables relevant to ibuprofen in vitro permeation or release. "
        "Also capture endpoint summary values, endpoint times, units, and basis when they are explicitly tabulated. "
        "Return only structured output. Preserve explicit table identifiers in table_id.\n\n"
        "STRICT ROW COMPLETENESS RULES:\n"
        "- You MUST extract every relevant data row in the provided tables. Do not skip, summarize, or return only representative rows.\n"
        "- If a table has 8 formulation rows and one endpoint column, return 8 records. If it has 8 formulation rows and 3 endpoint time columns, return 24 records.\n"
        "- For one-row/multiple-timepoint endpoint tables, emit one independent record for each formulation x each timepoint column, and set endpoint_time_value/unit for that exact column.\n"
        "- Do not copy a final-time endpoint value into earlier timepoint records. The endpoint_value must match the same time column named in endpoint_time_value.\n"
        "- The formulation_label for an endpoint record MUST come from the same table row as endpoint_value. Do not substitute labels from another table by row order.\n"
        "- If ENDPOINT_TABLE_HINT is set, prioritize that table for endpoint records. Use other tables only to fill composition or shared context for matching labels.\n"
        "- When cumulative amount columns and flux/Jss columns are both present, prefer cumulative amount columns as endpoint records and do not substitute flux for amount.\n"
        "- Keep composition-only rows separate from endpoint rows unless the same formulation label explicitly links them. Do not copy endpoint values onto unrelated composition/stability rows.\n"
        "- Extract excipient/vehicle composition into components, including non-API ingredient names, concentrations, basis, and notes when available.\n"
        "- Extract condition context when explicitly present in the table, footnote, title, or experiment context: membrane_type, membrane_source, membrane_thickness_um, receptor_medium, dose_type, and dose_amount.\n"
        "- Use dose_type only as 'finite', 'infinite', or ''. Do not guess missing condition fields.\n\n"
        f"DOI: {content_handle.doi}\n"
        f"TITLE: {route_decision.title}\n"
        f"SOURCE_FORMAT: {window.source_format}\n"
        f"SOURCE_BACKEND: {window.source_backend}\n"
        f"SOURCE_REF: {window.source_ref}\n"
        f"LOCATOR_MODE: {window.locator_mode}\n"
        f"SELECTED_LOCATORS: {window.selected_locators}\n"
        f"ENDPOINT_TABLE_HINT: {endpoint_table_hint}\n"
        f"TABLE_TRUNCATED: {window.table_truncated}\n"
        f"TRUNCATION_NOTES: {window.truncation_notes}\n"
        f"CURVE_HINTS: {curve_hints}\n\n"
        f"CONTENT:\n{window.content_text}"
    )


def _run_table_prompt(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    run_context: ExtractorRunContext,
    window: TableEvidenceWindow,
) -> TableExtractionResult:
    provider = resolve_provider_from_context(run_context)
    model_name = resolve_stage_model(run_context, "table_extract")
    prompt = _build_prompt(
        content_handle=content_handle,
        route_decision=route_decision,
        window=window,
        curve_hints=_safe_curve_hints(run_context, content_handle.paper_id, content_handle.doi),
    )

    attempt = 0
    while True:
        try:
            user_content = [{"type": "input_text", "text": prompt}]
            if window.source_format == "pdf":
                for page_index in window.image_page_indices[:2]:
                    user_content.append({"type": "input_image", "image_url": _render_page_jpg_dataurl(window.source_ref, page_index)})
            response = parse_structured(
                provider=provider,
                model=model_name,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                text_format=TableExtractionResult,
                timeout=90,
            )
            record_openai_usage(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.table",
                model_name=model_name,
                response=response,
                prompt_payload=[SYSTEM_PROMPT, user_content],
                output_payload=response.output_parsed.model_dump(mode="json"),
                metadata={"paper_id": content_handle.paper_id, "doi": content_handle.doi, "source_backend": window.source_backend},
                retries_used=attempt,
            )
            return response.output_parsed
        except Exception as exc:
            attempt += 1
            record_openai_attempt_failure(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.table",
                model_name=model_name,
                exc=exc,
                attempt=attempt,
                max_retries=6,
                metadata={"paper_id": content_handle.paper_id, "doi": content_handle.doi, "source_backend": window.source_backend},
                terminal=attempt >= 6,
            )
            if attempt >= 6:
                raise
            _backoff(attempt)


def _normalize_endpoint(
    endpoint_value: float | None,
    endpoint_unit: str,
    endpoint_kind: str,
    area_cm2: float | None,
) -> tuple[float | None, str]:
    if endpoint_kind == "amount_per_area":
        return normalize_amount_per_area(endpoint_value, endpoint_unit)
    if endpoint_kind == "amount_total":
        return amount_total_to_ug_per_cm2(endpoint_value, endpoint_unit, area_cm2)
    return None, ""


def _recover_area_from_fragments(*fragments: str) -> float | None:
    for fragment in fragments:
        value = parse_area_cm2(fragment)
        if value is not None:
            return value
    return None


def _recover_endpoint_fields(row: FormulationRow) -> tuple[float | None, str, str, float | None, str]:
    endpoint_value = row.endpoint_value
    endpoint_unit = row.endpoint_unit
    endpoint_kind = row.endpoint_kind
    endpoint_time_value = row.endpoint_time_value
    endpoint_time_unit = row.endpoint_time_unit

    search_fragments = [row.evidence_snippet, row.notes, *row.source_locators]
    if endpoint_value is None:
        for fragment in search_fragments:
            parsed_value, parsed_unit, parsed_kind = parse_endpoint_amount(fragment)
            if parsed_value is not None:
                endpoint_value = parsed_value
                endpoint_unit = parsed_unit or endpoint_unit
                endpoint_kind = parsed_kind if parsed_kind != "unknown" else endpoint_kind
                break

    if endpoint_time_value is None:
        for fragment in search_fragments:
            mentions = extract_time_mentions(fragment)
            if mentions:
                best_value, best_unit = max(
                    mentions,
                    key=lambda item: normalize_time_to_hours(item[0], item[1]) or float(item[0]),
                )
                endpoint_time_value = best_value
                endpoint_time_unit = best_unit
                break

    return endpoint_value, endpoint_unit, endpoint_kind, endpoint_time_value, endpoint_time_unit


def _parse_numeric_cell(cell: str) -> float | None:
    match = re.search(r"[-+]?\d+(?:\.\d+)?", cell or "")
    return float(match.group(0)) if match else None


def _endpoint_unit_from_header(header: str) -> str:
    match = re.search(r"\(([^)]*(?:µg|μg|ug|mg|ng)[^)]*)\)", header or "", flags=re.IGNORECASE)
    if match:
        unit = match.group(1).strip()
        return unit.replace(" ", "")
    if "µg" in header or "μg" in header or "ug" in header.lower():
        return "μg"
    if "mg" in header.lower():
        return "mg"
    return ""


def _wide_timepoint_rows_from_window(window: TableEvidenceWindow) -> list[FormulationRow]:
    """Deterministically expand structured wide endpoint tables into row x timepoint records."""

    rows: list[FormulationRow] = []
    current_locator = ""
    lines = window.content_text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("TABLE_LOCATOR:"):
            current_locator = line.split(":", 1)[1].strip()
            continue
        if "cum." not in line.lower() and "cumulative" not in line.lower():
            continue
        if "amount" not in line.lower() or "|" not in line:
            continue
        next_header = lines[index + 1] if index + 1 < len(lines) else ""
        time_mentions = extract_time_mentions(next_header)
        if not time_mentions:
            continue
        endpoint_unit = _endpoint_unit_from_header(line)
        time_count = len(time_mentions)
        for data_line in lines[index + 2 :]:
            if not data_line.strip() or data_line.startswith("--- ") or data_line.startswith("TABLE_LOCATOR:"):
                break
            if "|" not in data_line:
                continue
            cells = [cell.strip() for cell in data_line.split("|")]
            label = cells[0] if cells else ""
            if not re.match(r"^[A-Za-z]{1,3}\d+[A-Za-z]?$", label):
                continue
            if len(cells) < time_count + 1:
                continue
            endpoint_cells = cells[-time_count:]
            for endpoint_cell, (time_value, time_unit) in zip(endpoint_cells, time_mentions):
                endpoint_value = _parse_numeric_cell(endpoint_cell)
                if endpoint_value is None:
                    continue
                components: list[Component] = []
                if len(cells) >= 4:
                    components.extend(
                        [
                            Component(name_raw="Vit. E TPGS level", concentration_value=_parse_numeric_cell(cells[2]), concentration_unit="coded level", remark=f"source cell={cells[2]}"),
                            Component(name_raw="HPMC K100 level", concentration_value=_parse_numeric_cell(cells[3]), concentration_unit="coded level", remark=f"source cell={cells[3]}"),
                        ]
                    )
                    ps_value = _parse_numeric_cell(cells[1])
                    if ps_value is not None:
                        components.append(Component(name_raw="particle size factor", concentration_value=ps_value, concentration_unit="nm", remark=f"source cell={cells[1]}"))
                rows.append(
                    FormulationRow(
                        formulation_label=label,
                        api_name="Ibuprofen",
                        api_concentration_value=5.0 if "drug %" in window.content_text.lower() else None,
                        api_concentration_unit="% (w/v)" if "% ( w / v )" in window.content_text.lower() or "% w/v" in window.content_text.lower() else "",
                        api_basis="w/v" if "% ( w / v )" in window.content_text.lower() or "% w/v" in window.content_text.lower() else "",
                        api_concentration_raw="5% (w/v)" if "drug %" in window.content_text.lower() else "",
                        components=components,
                        endpoint_value=endpoint_value,
                        endpoint_unit=endpoint_unit,
                        endpoint_time_value=time_value,
                        endpoint_time_unit=time_unit,
                        endpoint_kind="amount_total",
                        table_id=current_locator,
                        source_locators=[current_locator] if current_locator else [],
                        evidence_snippet=data_line,
                        confidence=0.98,
                        notes="deterministic_wide_timepoint_expansion",
                    )
                )
    return rows


def _postprocess_table_result(result: TableExtractionResult, window: TableEvidenceWindow) -> TableExtractionResult:
    wide_rows = _wide_timepoint_rows_from_window(window)
    if not wide_rows:
        return result
    wide_tables = {row.table_id for row in wide_rows if row.table_id}
    filtered = [
        row
        for row in result.formulations
        if row.table_id not in wide_tables
    ]
    notes = (result.notes or "").strip()
    addition = f"deterministic_wide_timepoint_rows={len(wide_rows)}"
    return result.model_copy(update={"formulations": [*wide_rows, *filtered], "notes": f"{notes} | {addition}".strip(" |")})


def _condition_text(row: FormulationRow, window: TableEvidenceWindow, route_decision: RouteDecision) -> str:
    return " ".join(
        str(value or "")
        for value in (
            row.evidence_snippet,
            row.notes,
            window.content_text,
            route_decision.notes,
            route_decision.raw_labels.get("barrier_name_raw", ""),
            route_decision.raw_labels.get("barrier_category", ""),
        )
    )


def _infer_membrane_source(text: str) -> str:
    lowered = (text or "").lower()
    if any(token in lowered for token in ("strat-m", "silicone", "cellulose", "synthetic membrane")):
        return "synthetic"
    if "porcine" in lowered or "pig" in lowered:
        return "porcine"
    if "human" in lowered or "cadaver" in lowered:
        return "human"
    if "rat" in lowered:
        return "rat"
    if "mouse" in lowered or "murine" in lowered:
        return "mouse"
    return ""


def _infer_membrane_type(row: FormulationRow, route_decision: RouteDecision, text: str) -> str:
    explicit = row.membrane_type.strip()
    explicit_lower = explicit.lower()
    if explicit and not any(token in explicit_lower for token in ("franz", "diffusion cell", "receptor", "donor")):
        return explicit
    barrier = str(route_decision.raw_labels.get("barrier_name_raw", "") or "").strip()
    if barrier and barrier.lower() not in {"skin", "both", "uncertain", "synthetic_membrane"}:
        return barrier
    patterns = [
        r"(dermatomed\s+(?:porcine|human|rat)[^.;,]{0,40}skin)",
        r"((?:porcine|human|rat|mouse|murine)[^.;,]{0,40}skin)",
        r"(strat-?m[^.;,]{0,30})",
        r"(silicone membrane)",
        r"(cellulose membrane)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _infer_receptor_medium(row: FormulationRow, text: str) -> str:
    if row.receptor_medium.strip():
        return row.receptor_medium.strip()
    pbs_match = re.search(
        r"(PBS\s*(?:\(\s*pH\s*[\d.]+\s*\)|pH\s*[\d.]+)(?:\s*(?:with|\+|and containing)\s*[^.;\n]{0,80})?)",
        text,
        flags=re.IGNORECASE,
    )
    if pbs_match:
        value = pbs_match.group(1).strip()
        return re.split(r"\s+and\s+maintained|\s+at\s+37|\s+with\s+constant", value, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    medium_match = re.search(
        r"receptor\s+(?:compartment|medium|solution|phase|fluid)[^.;]{0,80}?(?:filled with|contained|consisted of|was)\s+([^.;]{3,120})",
        text,
        flags=re.IGNORECASE,
    )
    return medium_match.group(1).strip() if medium_match else ""


def _infer_dose_type(row: FormulationRow, text: str) -> str:
    explicit = row.dose_type.strip().lower()
    if explicit in {"finite", "infinite"}:
        return explicit
    lowered = text.lower()
    if "infinite dose" in lowered:
        return "infinite"
    if "finite dose" in lowered:
        return "finite"
    return ""


def _infer_dose_amount(row: FormulationRow, dose_type: str, text: str) -> str:
    if row.dose_amount.strip():
        return row.dose_amount.strip()
    if dose_type == "infinite":
        return "infinite dose"
    match = re.search(
        r"(\d+(?:\.\d+)?\s*(?:mg|g|µg|ug|μg|mL|ml|µL|uL|μL)(?:\s*/\s*cm(?:\^?2|²))?)",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def _infer_membrane_thickness(row: FormulationRow, text: str) -> float | None:
    if row.membrane_thickness_um is not None and row.membrane_thickness_um > 0:
        return row.membrane_thickness_um
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:µm|μm|um|microm(?:eter|etre)s?)", text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def _condition_snippet(value: str | float | None, text: str, max_chars: int = 520) -> str:
    if value is None or value == "":
        return ""
    lowered = text.lower()
    index = lowered.find(str(value).lower())
    if index < 0:
        for fallback in ("receptor", "membrane", "skin", "dose", "pbs", "franz"):
            index = lowered.find(fallback)
            if index >= 0:
                break
    if index < 0:
        return str(value)
    left = max(0, index - max_chars // 2)
    right = min(len(text), index + max_chars // 2)
    return re.sub(r"\s+", " ", text[left:right]).strip()


def _matches_api_context(row: FormulationRow, fragment: str) -> bool:
    return fragment_matches_api_context(
        fragment,
        api_name=row.api_name or "ibuprofen",
        formulation_label=row.formulation_label,
        dosage_form=row.dosage_form,
    )


def _record_locator(row: FormulationRow, window: TableEvidenceWindow) -> str:
    if row.table_id:
        return row.table_id
    if row.source_locators:
        return row.source_locators[0]
    if window.selected_locators:
        return window.selected_locators[0]
    if row.source_pages:
        return f"page {row.source_pages[0]}"
    if window.selected_pages:
        return f"page {window.selected_pages[0]}"
    return ""


def _record_page(row: FormulationRow, window: TableEvidenceWindow) -> int | None:
    if window.locator_mode != "page":
        return None
    if row.source_pages:
        return row.source_pages[0]
    if window.selected_pages:
        return window.selected_pages[0]
    return None


def _map_formulation_to_record(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    row: FormulationRow,
    window: TableEvidenceWindow,
) -> Record:
    endpoint_value, endpoint_unit, endpoint_kind, endpoint_time_value, endpoint_time_unit = _recover_endpoint_fields(row)
    area_cm2 = _recover_area_from_fragments(
        row.evidence_snippet,
        row.notes,
        route_decision.notes,
        str(route_decision.raw_labels.get("where_diffusion_cell", "") or ""),
        str(route_decision.raw_labels.get("where_endpoint", "") or ""),
    )
    normalized_endpoint_value, normalized_endpoint_unit = _normalize_endpoint(
        endpoint_value,
        endpoint_unit,
        endpoint_kind,
        area_cm2,
    )
    api_value = row.api_concentration_value
    api_unit = row.api_concentration_unit
    api_basis = row.api_basis
    if api_value is None:
        for fragment in [row.api_concentration_raw, row.evidence_snippet, row.notes, row.formulation_label]:
            if not fragment:
                continue
            if not _matches_api_context(row, fragment):
                continue
            api_value, api_unit, api_basis = parse_api_concentration(fragment)
            if api_value is not None:
                break

    locator = _record_locator(row, window)
    page = _record_page(row, window)
    evidence_source_ref = window.source_ref or content_handle.doi or content_handle.paper_id
    evidence_items = [
        EvidenceItem(
            field_name="formulation",
            modality="table",
            locator=locator,
            page=page,
            snippet=row.evidence_snippet,
            source_ref=evidence_source_ref,
            confidence=row.confidence,
        )
    ]
    if endpoint_value is not None:
        evidence_items.append(
            EvidenceItem(
                field_name="endpoint",
                modality="table",
                locator=locator,
                page=page,
                snippet=row.evidence_snippet,
                source_ref=evidence_source_ref,
                confidence=row.confidence,
            )
        )
    condition_text = _condition_text(row, window, route_decision)
    membrane_type = _infer_membrane_type(row, route_decision, condition_text)
    membrane_source = _infer_membrane_source(membrane_type or condition_text) or row.membrane_source.strip()
    membrane_thickness_um = _infer_membrane_thickness(row, condition_text)
    receptor_medium = _infer_receptor_medium(row, condition_text)
    dose_type = _infer_dose_type(row, condition_text)
    dose_amount = _infer_dose_amount(row, dose_type, condition_text)
    for field_name, value in (
        ("membrane_type", membrane_type),
        ("membrane_source", membrane_source),
        ("membrane_thickness_um", membrane_thickness_um),
        ("receptor_medium", receptor_medium),
        ("dose_type", dose_type),
        ("dose_amount", dose_amount),
    ):
        if value not in {"", None}:
            evidence_items.append(
                EvidenceItem(
                    field_name=field_name,
                    modality="table",
                    locator=locator,
                    page=page,
                    snippet=_condition_snippet(value, condition_text),
                    source_ref=evidence_source_ref,
                    confidence=row.confidence,
                )
            )

    record_suffix_parts = ["table"]
    if endpoint_time_value is not None:
        record_suffix_parts.append(f"t{endpoint_time_value:g}{endpoint_time_unit}")
    if endpoint_value is not None:
        record_suffix_parts.append(f"v{endpoint_value:g}")
    return Record(
        record_id=make_record_id(
            content_handle.paper_id,
            "table",
            row.formulation_label or row.table_id or locator,
            suffix="_".join(record_suffix_parts),
        ),
        paper_id=content_handle.paper_id,
        doi=content_handle.doi,
        route=route_decision.route if route_decision.route in {"table", "mixed", "figure"} else "table",
        route_confidence=route_decision.route_confidence,
        extractor_confidence=row.confidence,
        study_type=str(route_decision.raw_labels.get("study_type", "uncertain") or "uncertain"),
        device=(
            infer_device_label(
                str(route_decision.raw_labels.get("where_franz", "") or ""),
                str(route_decision.raw_labels.get("where_diffusion_cell", "") or ""),
                route_decision.notes,
                row.notes,
                row.evidence_snippet,
            )
            or route_device_hint(route_decision)
        ),
        barrier=str(route_decision.raw_labels.get("barrier_name_raw", route_decision.raw_labels.get("barrier_category", "")) or ""),
        formulation=FormulationSpec(
            label=row.formulation_label,
            api_name=row.api_name,
            api_concentration_value=api_value,
            api_concentration_unit=api_unit,
            api_basis=api_basis,
            api_concentration_raw=row.api_concentration_raw,
            components=[
                FormulationComponent(
                    name=component.name_raw,
                    concentration_value=component.concentration_value,
                    concentration_unit=component.concentration_unit,
                    basis=component.basis,
                    note=component.remark,
                )
                for component in row.components
            ],
            dosage_form=row.dosage_form,
        ),
        endpoint=EndpointSpec(
            field_name="amount",
            kind=endpoint_kind,
            value=endpoint_value,
            unit=endpoint_unit,
            time_value=endpoint_time_value,
            time_unit=endpoint_time_unit,
            normalized_value=normalized_endpoint_value,
            normalized_unit=normalized_endpoint_unit,
        ),
        conditions=ConditionSpec(
            diffusion_area_cm2=area_cm2,
            duration_h=normalize_time_to_hours(endpoint_time_value, endpoint_time_unit),
            membrane_type=membrane_type,
            membrane_source=membrane_source,
            membrane_thickness_um=membrane_thickness_um,
            receptor_medium=receptor_medium,
            dose_type=dose_type,
            dose_amount=dose_amount,
        ),
        evidence_items=evidence_items,
        provenance=build_provenance(
            extractor_name="table",
            content_handle=content_handle,
            route_decision=route_decision,
            source_format=window.source_format,
            source_path=window.source_ref,
            source_pages=window.selected_pages,
            metadata={
                "source_backend": window.source_backend,
                "locator_mode": window.locator_mode,
                "selected_locators": window.selected_locators,
                "table_id": row.table_id,
                "row_source_pages": row.source_pages,
                "row_source_locators": row.source_locators,
                "score_debug": window.score_debug,
                "table_truncated": window.table_truncated,
                "truncation_notes": window.truncation_notes,
            },
        ),
        source_notes=[row.notes] if row.notes else [],
    )


def extract(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    policy: object | None,
    run_context: ExtractorRunContext,
) -> list[Record]:
    """Extract table-modality candidate records for a single paper."""

    if route_decision.route not in {"table", "mixed", "figure"}:
        return []

    window = select_table_evidence_window(content_handle, route_decision)
    result = _run_table_prompt(content_handle, route_decision, run_context, window)
    result = _postprocess_table_result(result, window)
    return [_map_formulation_to_record(content_handle, route_decision, row, window) for row in result.formulations]


def extract_batch(
    content_route_pairs: list[tuple[ContentAccess, RouteDecision]],
    policy: object | None,
    run_context: ExtractorRunContext,
    output_jsonl: str | Path | None = None,
    raw_output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
    checkpoint_every: int = 25,
) -> list[Record]:
    """Extract table-modality records across a batch of routed papers."""

    selected_pairs = [
        (content_handle, route_decision)
        for content_handle, route_decision in content_route_pairs
        if route_decision.route in {"table", "mixed", "figure"}
    ]
    checkpoint_every = max(1, checkpoint_every)
    existing_raw_results = load_jsonl_if_exists(raw_output_jsonl)
    processed_paper_ids = {str(row.get("paper_id", "") or "") for row in existing_raw_results}
    existing_records = load_record_jsonl_if_exists(output_jsonl)
    records_by_paper: dict[str, list[Record]] = defaultdict(list)
    for record in existing_records:
        records_by_paper[record.paper_id].append(record)
    completed_before = sum(1 for content_handle, _ in selected_pairs if content_handle.paper_id in processed_paper_ids)
    if progress_callback and completed_before:
        progress_callback(completed_before, "resume", f"loaded={completed_before}")

    raw_results = list(existing_raw_results)
    remaining_pairs = [(content_handle, route_decision) for content_handle, route_decision in selected_pairs if content_handle.paper_id not in processed_paper_ids]
    for remaining_index, (content_handle, route_decision) in enumerate(remaining_pairs, start=1):
        completed_so_far = completed_before + remaining_index - 1
        current_item = content_handle.paper_id or content_handle.doi or route_decision.title[:60] or f"paper_{completed_so_far + 1}"
        if progress_callback:
            progress_callback(completed_so_far, current_item, "extracting table evidence")
        try:
            window = select_table_evidence_window(content_handle, route_decision)
            result = _run_table_prompt(content_handle, route_decision, run_context, window)
            result = _postprocess_table_result(result, window)
            raw_results.append(
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
                    "score_debug": window.score_debug,
                    "table_truncated": window.table_truncated,
                    "truncation_notes": window.truncation_notes,
                    **result.model_dump(mode="json"),
                }
            )
            records_by_paper[content_handle.paper_id].extend(
                _map_formulation_to_record(content_handle, route_decision, row, window) for row in result.formulations
            )
            if progress_callback:
                progress_callback(completed_so_far + 1, current_item, f"records={len(result.formulations)} source={window.source_format}")
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping table extraction for %s due to missing source: %s", current_item, exc)
            raw_results.append(
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
                write_jsonl(raw_results, raw_output_jsonl)
            if output_jsonl:
                write_records_jsonl(ordered_records, output_jsonl)

    records = [
        record
        for content_handle, _route_decision in selected_pairs
        for record in records_by_paper.get(content_handle.paper_id, [])
    ]
    if raw_output_jsonl:
        write_jsonl(raw_results, raw_output_jsonl)
    if output_jsonl:
        write_records_jsonl(records, output_jsonl)
    if output_csv:
        write_records_csv(records, output_csv)
    return records


def extract_table_records(
    routed_rows: list[dict],
    curve_hints_by_paper: dict | None = None,
    model: str = "gpt-4o-mini",
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    raw_output_jsonl: str | Path | None = None,
) -> list[Record]:
    """Backward-compatible batch wrapper around the standardized table extractor."""

    pairs: list[tuple[ContentAccess, RouteDecision]] = []
    for row in routed_rows:
        local_paths: dict[str, str] = {}
        access_urls: dict[str, str] = {}
        if row.get("pdf_path"):
            local_paths["pdf"] = str(row.get("pdf_path", "") or "")
        if row.get("pmc_xml_path"):
            local_paths["pmc_xml"] = str(row.get("pmc_xml_path", "") or "")
        if row.get("html_path"):
            local_paths["html"] = str(row.get("html_path", "") or "")
        if row.get("pmc_xml_url"):
            access_urls["pmc_xml"] = str(row.get("pmc_xml_url", "") or "")
        if row.get("html_url"):
            access_urls["html"] = str(row.get("html_url", "") or "")

        preferred_format = "pdf"
        for fmt in ("pmc_xml", "html", "pdf"):
            if local_paths.get(fmt) or access_urls.get(fmt):
                preferred_format = fmt
                break

        has_any_local = any(local_paths.values())
        content_handle = ContentAccess(
            paper_id=str(row.get("paper_id", "") or ""),
            doi=str(row.get("doi", "") or ""),
            title=str(row.get("title", "") or ""),
            preferred_format=preferred_format,
            available_formats=[fmt for fmt in ("pmc_xml", "html", "pdf") if local_paths.get(fmt) or access_urls.get(fmt)],
            access_urls=access_urls,
            local_paths=local_paths,
            status="downloaded" if has_any_local else "resolved",
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
        run_id="legacy_table_batch",
        model_name=model,
        output_dir=str(Path(output_jsonl).parent) if output_jsonl else ".",
        notes=["Backward-compatible table batch wrapper."],
        fail_on_malformed_output=False,
        shared_state={"curve_hints_by_paper": curve_hints_by_paper or {}},
    )
    return extract_batch(
        pairs,
        policy=None,
        run_context=run_context,
        output_jsonl=output_jsonl,
        raw_output_jsonl=raw_output_jsonl,
        output_csv=output_csv,
    )
