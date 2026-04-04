from __future__ import annotations

import logging
import random
import re
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping

import fitz
from openai import OpenAI
from pydantic import BaseModel, Field

from schemas.models import EvidenceItem, RouteDecision
from utils.io import write_jsonl, write_optional_csv
from utils.long_run import LongRunMonitor, record_openai_attempt_failure, record_openai_usage
from utils.resume import load_typed_jsonl_if_exists
from utils.source_cache import fetch_cached_text
from utils.status_panel import ProgressCallback

LOGGER = logging.getLogger("skinminer.router")
ROUTER_USER_AGENT = {"User-Agent": "SkinMiner/structured-first-router"}
ROUTER_PROMPT_ASSET_ID = "routing.structured_first"
ROUTER_PROMPT_VERSION = "2026-03-28.v1"

KEYWORDS = [
    "ibuprofen",
    "franz",
    "diffusion cell",
    "permeation cell",
    "vertical diffusion",
    "ivpt",
    "ivrt",
    "cumulative",
    "amount permeated",
    "amount released",
    "table",
    "figure",
    "supplement",
    "formulation",
    "% w/w",
    "mg/g",
    "skin",
    "membrane",
]
TABLE_HINT_KEYWORDS = ["table", "table_locator", "formulation", "composition", "ingredient", "% w/w", "mg/g"]
FIGURE_HINT_KEYWORDS = ["figure", "fig.", "curve", "plot", "profile", "graph"]
ENDPOINT_HINT_KEYWORDS = ["amount permeated", "amount released", "cumulative", "permeation", "release", "flux", "jss", "ug/cm", "mg/cm", "ng/cm"]
FORMULATION_HINT_KEYWORDS = ["formulation", "composition", "vehicle", "gel", "cream", "ointment", "solution", "% w/w", "mg/g"]
BLOCKED_SOURCE_PATTERNS = (
    "enable javascript",
    "javascript is disabled",
    "javascript required",
    "access through your institution",
    "purchase this article",
    "buy this article",
    "sign in to view",
    "subscribe to read",
    "access denied",
    "not available in your region",
    "checking if the site connection is secure",
    "security check",
    "captcha",
)


class RouterLLMResponse(BaseModel):
    paper_type: Literal["primary_experiment", "review", "clinical", "other", "uncertain"]
    mentions_ibuprofen: Literal["yes", "no", "uncertain"]
    mentions_diffusion_cell: Literal["yes", "no", "uncertain"]
    franz_confirmed: Literal["yes", "no", "uncertain"]
    where_diffusion_cell: str = ""
    where_franz: str = ""
    study_type: Literal["IVPT", "IVRT", "both", "uncertain"]
    barrier_category: Literal["skin", "synthetic_membrane", "both", "uncertain"]
    barrier_name_raw: str = ""
    endpoint_found: Literal["yes", "no", "uncertain"]
    endpoint_time_found: Literal["yes", "no", "uncertain"]
    where_endpoint: str = ""
    endpoint_carrier: Literal["table_text", "narrative", "figure", "supplement", "unknown"]
    endpoint_carrier_snippet: str = ""
    formulation_carrier: Literal["table_text", "narrative", "supplement", "unknown"]
    formulation_carrier_snippet: str = ""
    endpoint_likely_in_supp: Literal["yes", "no", "uncertain"]
    formulation_table_missing: Literal["yes", "no", "uncertain"]
    notes: str = ""


class RouterDocument(BaseModel):
    source_backend: Literal["pmc_xml_local", "pmc_xml_remote", "html_local", "html_remote", "pdf_local", "missing"]
    source_ref: str = ""
    content: str = ""
    diagnostics: list[str] = Field(default_factory=list)


SYSTEM_PROMPT = (
    "You are an evidence routing assistant for an OA-only ibuprofen dermal formulation mining framework. "
    "Use ONLY the supplied document text. Identify where extractable evidence appears, but do not apply the strict v1 policy here. "
    "When the content comes from structured XML or HTML, locators may refer to blocks, sections, captions, or headings rather than page numbers. "
    "Prefer assigning text, table, figure, or mixed whenever the carrier is explicit enough. "
    "Use unresolved only when the carrier really cannot be determined from the supplied text."
)


def _normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def _score_text(text: str) -> int:
    lowered = f" {_normalize_text(text).lower()} "
    return sum(3 if keyword in {"ibuprofen", "franz", "table", "figure"} and keyword in lowered else int(keyword in lowered) for keyword in KEYWORDS)


def _extract_relevant_pages(
    pdf_path: str,
    max_pages_for_llm: int = 12,
    always_include_first_pages: int = 2,
    max_chars_total: int = 26_000,
) -> str:
    document = fitz.open(pdf_path)
    page_texts: list[str] = []
    scores: list[int] = []

    for page_index in range(document.page_count):
        text = document.load_page(page_index).get_text("text") or ""
        page_texts.append(text)
        scores.append(_score_text(text))

    selected: list[tuple[int, int, str]] = []
    used: set[int] = set()

    for page_index in range(min(always_include_first_pages, document.page_count)):
        selected.append((999, page_index, page_texts[page_index]))
        used.add(page_index)

    ranked = sorted(((score, index) for index, score in enumerate(scores) if score > 0), reverse=True)
    for score, page_index in ranked:
        if page_index in used:
            continue
        selected.append((score, page_index, page_texts[page_index]))
        used.add(page_index)
        if len(selected) >= max_pages_for_llm:
            break

    if not selected:
        for page_index in range(min(3, document.page_count)):
            selected.append((0, page_index, page_texts[page_index]))

    document.close()
    parts = [f"--- PAGE {page_index + 1} (kw_score={score}) ---\n{text}" for score, page_index, text in sorted(selected, key=lambda item: item[1])]
    return " ".join("\n".join(parts).split())[:max_chars_total]


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


def _blocked_source_reason(raw_text: str) -> str:
    lowered = _normalize_text(raw_text).lower()
    if not lowered:
        return ""
    for pattern in BLOCKED_SOURCE_PATTERNS:
        if pattern in lowered:
            return pattern.replace(" ", "_")
    return ""


def _build_structured_context(
    blocks: list[str],
    *,
    source_backend: str,
    max_blocks_for_llm: int = 24,
    always_include_first_blocks: int = 4,
    max_chars_total: int = 26_000,
) -> str:
    if not blocks:
        return ""

    selected: list[tuple[int, int, str]] = []
    used: set[int] = set()

    for block_index in range(min(always_include_first_blocks, len(blocks))):
        block = blocks[block_index]
        selected.append((999, block_index, block))
        used.add(block_index)

    ranked = sorted(((_score_text(block), index) for index, block in enumerate(blocks) if _score_text(block) > 0), reverse=True)
    for score, block_index in ranked:
        if block_index in used:
            continue
        selected.append((score, block_index, blocks[block_index]))
        used.add(block_index)
        if len(selected) >= max_blocks_for_llm:
            break

    if not selected:
        for block_index in range(min(6, len(blocks))):
            selected.append((0, block_index, blocks[block_index]))

    parts = [
        f"--- BLOCK {block_index + 1} (kw_score={score}, source={source_backend}) ---\n{block}"
        for score, block_index, block in sorted(selected, key=lambda item: item[1])
    ]
    return "\n\n".join(parts)[:max_chars_total]


def _fetch_remote_text(url: str, max_retries: int = 3) -> str:
    return fetch_cached_text(
        url,
        headers=ROUTER_USER_AGENT,
        timeout=60,
        max_retries=max_retries,
        namespace="router_structured_sources",
    )


def _load_text_from_ref(ref: str, location: str) -> str:
    if location == "local":
        return Path(ref).read_text(encoding="utf-8", errors="ignore")
    return _fetch_remote_text(ref)


def _structured_candidates(row: Mapping[str, Any]) -> list[tuple[str, str, str]]:
    local_paths = row.get("local_paths", {}) or {}
    access_urls = row.get("access_urls", {}) or {}
    candidates: list[tuple[str, str, str]] = []
    for fmt in ("pmc_xml", "html"):
        local_ref = str(local_paths.get(fmt, "") or "").strip()
        if local_ref and Path(local_ref).exists():
            candidates.append((fmt, "local", local_ref))
        remote_ref = str(access_urls.get(fmt, "") or "").strip()
        if remote_ref:
            candidates.append((fmt, "remote", remote_ref))
    return candidates


def _prepare_router_document(row: Mapping[str, Any]) -> RouterDocument:
    diagnostics: list[str] = []

    for fmt, location, ref in _structured_candidates(row):
        try:
            raw_text = _load_text_from_ref(ref, location)
            blocked_reason = _blocked_source_reason(raw_text)
            if blocked_reason:
                diagnostics.append(f"blocked:{fmt}_{location}:{blocked_reason}")
                continue
            blocks = _extract_xml_blocks(raw_text) if fmt == "pmc_xml" else _extract_html_blocks(raw_text)
            if len(blocks) < 2 and _score_text(" ".join(blocks)) == 0:
                diagnostics.append(f"low_signal:{fmt}_{location}")
                continue
            content = _build_structured_context(blocks, source_backend=f"{fmt}_{location}")
            if content:
                return RouterDocument(
                    source_backend=f"{fmt}_{location}",
                    source_ref=ref,
                    content=content,
                    diagnostics=diagnostics,
                )
            diagnostics.append(f"empty:{fmt}_{location}")
        except Exception as exc:
            diagnostics.append(f"{fmt}_{location}:{type(exc).__name__}")

    pdf_path = str(row.get("pdf_path") or row.get("local_paths", {}).get("pdf", "")).strip()
    if pdf_path and Path(pdf_path).exists():
        return RouterDocument(
            source_backend="pdf_local",
            source_ref=pdf_path,
            content=_extract_relevant_pages(pdf_path),
            diagnostics=diagnostics,
        )

    return RouterDocument(source_backend="missing", diagnostics=diagnostics)


def _parse_page(locator: str) -> int | None:
    match = re.search(r"\b(?:page|p\.?)\s*(\d+)\b", locator or "", flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _carrier_to_modality(carrier: str) -> Literal["metadata", "text", "table", "figure", "mixed"]:
    if carrier == "table_text":
        return "table"
    if carrier == "figure":
        return "figure"
    if carrier == "unknown":
        return "metadata"
    return "text"


def _compute_route(payload: RouterLLMResponse) -> Literal["text", "table", "figure", "mixed", "unresolved"]:
    endpoint = payload.endpoint_carrier
    formulation = payload.formulation_carrier

    if endpoint == "figure":
        return "figure"
    if endpoint == "supplement" or formulation == "supplement":
        return "unresolved"
    if endpoint == "table_text" and formulation in {"table_text", "unknown"}:
        return "table"
    if endpoint == "narrative" and formulation in {"narrative", "unknown"}:
        return "text"
    if endpoint in {"table_text", "narrative"} and formulation in {"table_text", "narrative"}:
        return "mixed" if endpoint != formulation else ("table" if endpoint == "table_text" else "text")
    return "unresolved"


def _count_keyword_hits(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(keyword in lowered for keyword in keywords)


def _heuristic_route_fallback(
    payload: RouterLLMResponse,
    router_document: RouterDocument,
) -> tuple[Literal["text", "table", "figure", "mixed", "unresolved"], dict[str, int]]:
    content = router_document.content.lower()
    signals = {
        "table_hits": _count_keyword_hits(content, TABLE_HINT_KEYWORDS),
        "figure_hits": _count_keyword_hits(content, FIGURE_HINT_KEYWORDS),
        "endpoint_hits": _count_keyword_hits(content, ENDPOINT_HINT_KEYWORDS),
        "formulation_hits": _count_keyword_hits(content, FORMULATION_HINT_KEYWORDS),
    }
    if payload.paper_type in {"review", "clinical", "other"}:
        return "unresolved", signals
    if payload.mentions_ibuprofen == "no" or payload.endpoint_likely_in_supp == "yes":
        return "unresolved", signals

    table_like = signals["table_hits"] >= 2 and signals["formulation_hits"] >= 1
    figure_like = signals["figure_hits"] >= 2 and signals["endpoint_hits"] >= 1
    text_like = signals["endpoint_hits"] >= 2 and signals["formulation_hits"] >= 1

    if table_like and figure_like:
        return "mixed", signals
    if figure_like:
        return "figure", signals
    if table_like:
        return "table", signals
    if text_like or (
        payload.endpoint_found == "yes"
        and payload.formulation_table_missing == "yes"
        and payload.formulation_carrier in {"narrative", "unknown"}
    ):
        return "text", signals
    return "unresolved", signals


def _build_anchor_evidence(payload: RouterLLMResponse, paper_id: str, doi: str) -> list[EvidenceItem]:
    anchor_evidence: list[EvidenceItem] = []
    if payload.where_franz:
        anchor_evidence.append(
            EvidenceItem(
                field_name="device",
                modality="text",
                locator=payload.where_franz,
                page=_parse_page(payload.where_franz),
                snippet=payload.where_franz,
                source_ref=doi or paper_id,
                confidence=0.7,
            )
        )
    if payload.where_endpoint:
        anchor_evidence.append(
            EvidenceItem(
                field_name="endpoint",
                modality=_carrier_to_modality(payload.endpoint_carrier),
                locator=payload.where_endpoint,
                page=_parse_page(payload.where_endpoint),
                snippet=payload.endpoint_carrier_snippet or payload.where_endpoint,
                source_ref=doi or paper_id,
                confidence=0.8,
            )
        )
    if payload.formulation_carrier_snippet:
        anchor_evidence.append(
            EvidenceItem(
                field_name="formulation",
                modality=_carrier_to_modality(payload.formulation_carrier),
                locator=payload.formulation_carrier,
                snippet=payload.formulation_carrier_snippet,
                source_ref=doi or paper_id,
                confidence=0.7,
            )
        )
    return anchor_evidence


def _route_confidence(route: str, anchor_evidence: list[EvidenceItem]) -> float | None:
    if route == "unresolved":
        return 0.2 if anchor_evidence else 0.0
    return min(0.95, 0.45 + (0.12 * len(anchor_evidence)))


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


def route_papers(
    papers: Iterable[Mapping[str, Any]],
    model: str = "gpt-4o-mini",
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    max_retries: int = 6,
    progress_every: int = 25,
    progress_callback: ProgressCallback | None = None,
    long_run_monitor: LongRunMonitor | None = None,
    checkpoint_every: int = 25,
    resume_jsonl: str | Path | None = None,
) -> list[RouteDecision]:
    client = OpenAI(timeout=60)
    paper_list = list(papers)
    progress_every = max(1, progress_every)
    checkpoint_every = max(1, checkpoint_every)
    existing_decisions = load_typed_jsonl_if_exists(resume_jsonl, RouteDecision)
    existing_map = {decision.paper_id: decision for decision in existing_decisions if decision.paper_id}
    ordered_paper_ids = [str(row.get("paper_id", "") or "") for row in paper_list]
    decision_map: dict[str, RouteDecision] = {
        paper_id: existing_map[paper_id]
        for paper_id in ordered_paper_ids
        if paper_id in existing_map
    }
    completed_before = len(decision_map)

    LOGGER.info("Starting evidence routing for %s papers with model=%s", len(paper_list), model)
    if progress_callback and completed_before:
        progress_callback(completed_before, "resume", f"loaded={completed_before}")

    remaining_rows = [row for row in paper_list if str(row.get("paper_id", "") or "") not in decision_map]
    for remaining_index, row in enumerate(remaining_rows, start=1):
        paper_id = str(row.get("paper_id", "") or "")
        doi = str(row.get("doi", "") or "")
        title = str(row.get("title", "") or "")
        completed_so_far = completed_before + remaining_index - 1
        current_item = paper_id or doi or title[:60] or f"row_{completed_so_far + 1}"

        if progress_callback:
            progress_callback(completed_so_far, current_item, "routing evidence")

        router_document = _prepare_router_document(row)
        if not router_document.content:
            notes = "missing_structured_and_pdf_router_source"
            if router_document.diagnostics:
                notes = f"{notes}:{';'.join(router_document.diagnostics[:3])}"
            decision_map[paper_id] = RouteDecision(
                paper_id=paper_id,
                doi=doi,
                title=title,
                route="unresolved",
                route_confidence=0.0,
                notes=notes,
                raw_labels={
                    "title": title,
                    "router_source_backend": router_document.source_backend,
                    "router_source_ref": router_document.source_ref,
                    "router_source_diagnostics": router_document.diagnostics,
                },
            )
            if progress_callback:
                progress_callback(completed_so_far + 1, current_item, "missing_router_source")
            continue

        attempt = 0
        while True:
            try:
                user_prompt = (
                    "Determine the best extraction route for this OA paper.\n\n"
                    f"SOURCE_BACKEND: {router_document.source_backend}\n"
                    f"SOURCE_REF: {router_document.source_ref}\n"
                    f"DOI: {doi}\n"
                    f"TITLE: {title}\n\n"
                    f"DOCUMENT:\n{router_document.content}"
                )
                response = client.responses.parse(
                    model=model,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    text_format=RouterLLMResponse,
                )
                record_openai_usage(
                    long_run_monitor,
                    module_name="detection.router",
                    model_name=model,
                    response=response,
                    prompt_payload=[SYSTEM_PROMPT, user_prompt],
                    output_payload=response.output_parsed.model_dump(mode="json"),
                    metadata={
                        "paper_id": paper_id,
                        "doi": doi,
                        "source_backend": router_document.source_backend,
                    },
                    retries_used=attempt,
                )
                payload = response.output_parsed
                anchor_evidence = _build_anchor_evidence(payload, paper_id, doi)
                route = _compute_route(payload)
                route_notes = payload.notes
                heuristic_signals: dict[str, int] = {}
                if route == "unresolved":
                    heuristic_route, heuristic_signals = _heuristic_route_fallback(payload, router_document)
                    if heuristic_route != "unresolved":
                        route = heuristic_route
                        route_notes = f"{payload.notes} | heuristic_route={heuristic_route}".strip(" |")
                raw_labels = payload.model_dump(mode="json")
                raw_labels.update(
                    {
                        "router_source_backend": router_document.source_backend,
                        "router_source_ref": router_document.source_ref,
                        "router_source_diagnostics": router_document.diagnostics,
                        "router_heuristic_signals": heuristic_signals,
                    }
                )
                decision_map[paper_id] = RouteDecision(
                    paper_id=paper_id,
                    doi=doi,
                    title=title,
                    route=route,
                    route_confidence=_route_confidence(route, anchor_evidence),
                    endpoint_carrier=payload.endpoint_carrier,
                    formulation_carrier=payload.formulation_carrier,
                    anchor_evidence=anchor_evidence,
                    notes=route_notes,
                    raw_labels=raw_labels,
                )
                if progress_callback:
                    progress_callback(completed_so_far + 1, current_item, f"route={route} via {router_document.source_backend}")
                break
            except Exception as exc:
                attempt += 1
                record_openai_attempt_failure(
                    long_run_monitor,
                    module_name="detection.router",
                    model_name=model,
                    exc=exc,
                    attempt=attempt,
                    max_retries=max_retries,
                    metadata={
                        "paper_id": paper_id,
                        "doi": doi,
                        "source_backend": router_document.source_backend,
                    },
                    terminal=attempt >= max_retries,
                )
                if attempt >= max_retries:
                    decision_map[paper_id] = RouteDecision(
                        paper_id=paper_id,
                        doi=doi,
                        title=title,
                        route="unresolved",
                        route_confidence=0.0,
                        notes=f"router_error:{type(exc).__name__}",
                        raw_labels={
                            "title": title,
                            "router_source_backend": router_document.source_backend,
                            "router_source_ref": router_document.source_ref,
                            "router_source_diagnostics": router_document.diagnostics,
                        },
                    )
                    if progress_callback:
                        progress_callback(completed_so_far + 1, current_item, f"failed:{type(exc).__name__}")
                    break
                _backoff(attempt)

        completed_total = completed_so_far + 1
        if output_jsonl and (completed_total % checkpoint_every == 0 or completed_total == len(paper_list)):
            ordered_decisions = [decision_map[paper_id] for paper_id in ordered_paper_ids if paper_id in decision_map]
            write_jsonl(ordered_decisions, output_jsonl)

        if completed_total % progress_every == 0 or completed_total == len(paper_list):
            unresolved_count = sum(decision.route == "unresolved" for decision in decision_map.values())
            LOGGER.info(
                "Evidence routing progress %s/%s (unresolved=%s)",
                completed_total,
                len(paper_list),
                unresolved_count,
            )

    ordered_decisions = [decision_map[paper_id] for paper_id in ordered_paper_ids if paper_id in decision_map]
    if output_jsonl:
        write_jsonl(ordered_decisions, output_jsonl)
    if output_csv:
        write_optional_csv([decision.model_dump(mode="json") for decision in ordered_decisions], output_csv)
    return ordered_decisions
