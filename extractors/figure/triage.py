"""Figure triage with explicit intermediate artifacts."""

from __future__ import annotations

import base64
import hashlib
import random
import re
import time
from pathlib import Path
from typing import Literal

import fitz
from openai import OpenAI
from pydantic import BaseModel, Field

from extractors.common import artifact_path, require_pdf_path, resolve_stage_model
from extractors.figure.models import FigureTriageArtifact, LegendEntry
from schemas.models import ContentAccess, ExtractorRunContext, RouteDecision
from utils.io import sanitize_filename, write_jsonl, write_optional_csv
from utils.long_run import record_openai_attempt_failure, record_openai_usage

FIGURE_TRIAGE_PROMPT_ASSET_ID = "extractors.figure.triage"
FIGURE_TRIAGE_PROMPT_VERSION = "2026-03-28.v1"

SYSTEM_PROMPT = (
    "You are a strict scientific figure triage assistant. "
    "Use ONLY the provided page images. If axis ranges or the plot bounding box cannot be read, keep them null."
)

FIGURE_KEYWORDS = [
    "figure",
    "fig.",
    "cumulative",
    "permeat",
    "release",
    "ibuprofen",
    "flux",
    "jss",
    "profile",
    "time",
    "hours",
    "ug/cm",
    "mg/cm",
    "ng/cm",
]


class FigureTriageResult(BaseModel):
    """Structured output requested from the figure triage prompt."""

    endpoint_curve_present: Literal["yes", "no", "uncertain"]
    likely_endpoint_type: Literal["cumulative_amount", "flux", "jss", "unknown"]
    figure_id: str = ""
    page_number: int | None = None
    subplot: str = ""
    digitizable: Literal["yes", "no", "uncertain"]
    why_not_digitizable: str = ""
    ticks_readable: Literal["yes", "no", "uncertain"]
    legend_present: Literal["yes", "no", "uncertain"]
    approx_curves_count: int | None = None
    legend: list[LegendEntry] = Field(default_factory=list)
    suggests_table_exists: Literal["yes", "no", "uncertain"]
    suggests_supp_exists: Literal["yes", "no", "uncertain"]
    recommended_route: Literal["digitize", "supp_needed", "text_table_maybe", "skip"] = "skip"
    plot_bbox: list[float] | None = None
    axes_x_label: str = ""
    axes_x_unit: str = ""
    x_min: float | None = None
    x_max: float | None = None
    axes_y_label: str = ""
    axes_y_unit: str = ""
    y_min: float | None = None
    y_max: float | None = None
    y_kind: Literal["amount_per_area", "amount_total", "percent", "unknown"] = "unknown"
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""


def _parse_anchor_pages(text: str) -> list[int]:
    pages: set[int] = set()
    for match in re.finditer(r"\b(?:page|p\.?)\s*(\d+)\b", text or "", flags=re.IGNORECASE):
        page_no = int(match.group(1))
        if page_no > 0:
            pages.add(page_no - 1)
    return sorted(pages)


def _score_text(text: str) -> int:
    lowered = f" {text.lower()} "
    score = 0
    for keyword in FIGURE_KEYWORDS:
        if keyword in lowered:
            score += 3 if keyword in {"figure", "fig.", "cumulative", "permeat", "release"} else 1
    return score


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


def _pick_candidate_pages(
    pdf_path: str,
    anchors: list[int],
    max_pages_to_send: int = 3,
    anchor_neighbor: int = 2,
    allow_text_only_pages: int = 1,
) -> tuple[list[int], str, dict[str, float]]:
    document = fitz.open(pdf_path)
    candidates: list[tuple[float, int, int, int, float, int]] = []
    for index in range(min(document.page_count, 160)):
        page = document.load_page(index)
        text = page.get_text("text") or ""
        text_score = _score_text(text)
        has_img, draw_ratio = _page_graphics_flags(page)
        fig_mention = 1 if ("fig." in text.lower() or "figure" in text.lower()) else 0
        score_total = text_score + 7 * has_img + (5 if draw_ratio >= 0.02 else 0) + 2 * fig_mention
        if score_total > 0:
            candidates.append((score_total, index, text_score, has_img, draw_ratio, fig_mention))

    anchor_window: set[int] = set()
    for anchor in anchors:
        for page_index in range(anchor - anchor_neighbor, anchor + anchor_neighbor + 1):
            if 0 <= page_index < document.page_count:
                anchor_window.add(page_index)

    candidates.sort(reverse=True, key=lambda item: item[0])
    selected: list[int] = []
    selected_set: set[int] = set()
    text_only_used = 0

    for score_total, page_index, text_score, has_img, draw_ratio, fig_mention in candidates:
        if len(selected) >= max_pages_to_send:
            break
        if page_index in selected_set:
            continue
        if has_img or draw_ratio >= 0.02:
            selected.append(page_index)
            selected_set.add(page_index)

    if len(selected) < max_pages_to_send and anchor_window:
        for page_index in sorted(anchor_window):
            if len(selected) >= max_pages_to_send:
                break
            if page_index in selected_set:
                continue
            page = document.load_page(page_index)
            has_img, draw_ratio = _page_graphics_flags(page)
            if not (has_img or draw_ratio >= 0.02):
                if text_only_used >= allow_text_only_pages:
                    continue
                text_only_used += 1
            selected.append(page_index)
            selected_set.add(page_index)

    for score_total, page_index, text_score, has_img, draw_ratio, fig_mention in candidates:
        if len(selected) >= max_pages_to_send:
            break
        if page_index in selected_set:
            continue
        if not (has_img or draw_ratio >= 0.02):
            if text_only_used >= allow_text_only_pages:
                continue
            text_only_used += 1
        selected.append(page_index)
        selected_set.add(page_index)

    if not selected:
        selected = [0]

    debug = " | ".join(
        f"p{page_index + 1}:score={score_total:.1f},text={text_score},img={has_img},draw={draw_ratio:.3f},fig={fig_mention}"
        for score_total, page_index, text_score, has_img, draw_ratio, fig_mention in candidates[:8]
    )
    page_scores = {f"page_{page_index + 1}": float(score_total) for score_total, page_index, *_rest in candidates[:24]}
    document.close()
    return sorted(selected), debug, page_scores


def _render_page_image_bytes(pdf_path: str, page_index: int, dpi: int = 170) -> bytes:
    document = fitz.open(pdf_path)
    page = document.load_page(page_index)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    document.close()
    return pixmap.tobytes("jpg")


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


def _make_trace_id(content_handle: ContentAccess, figure_id: str, page_number: int | None, subplot: str) -> str:
    base = "::".join(
        [
            content_handle.paper_id,
            content_handle.doi or "",
            figure_id or "figure_candidate",
            str(page_number or 0),
            subplot or "main",
        ]
    )
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    label = sanitize_filename(f"{content_handle.paper_id}_{figure_id or 'figure'}_{page_number or 0}_{subplot or 'main'}", max_len=80)
    return f"figure_trace_{label}_{digest}"


def triage_figure_content(
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    run_context: ExtractorRunContext,
    max_retries: int = 6,
) -> FigureTriageArtifact:
    """Triage figure-route content for a single paper and return a typed artifact."""

    pdf_path = require_pdf_path(content_handle)
    anchors = _parse_anchor_pages(str(route_decision.raw_labels.get("where_endpoint", "")))
    selected_pages, page_debug, page_scores = _pick_candidate_pages(pdf_path, anchors)
    page_map: list[tuple[int, str]] = []
    saved_paths: dict[int, str] = {}
    for page_index in selected_pages:
        image_bytes = _render_page_image_bytes(pdf_path, page_index)
        page_number = page_index + 1
        image_path = artifact_path(
            run_context,
            "figure",
            "triage_images",
            f"{sanitize_filename(content_handle.doi or content_handle.paper_id)}__p{page_number}.jpg",
        )
        image_path.write_bytes(image_bytes)
        saved_paths[page_number] = str(image_path)
        data_url = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
        page_map.append((page_number, data_url))

    client = OpenAI(timeout=90)
    model_name = resolve_stage_model(run_context, "figure_triage")
    attempt = 0
    while True:
        try:
            page_desc = ", ".join(f"Image {index + 1} = PAGE {page_number}" for index, (page_number, _) in enumerate(page_map))
            content = [
                {
                    "type": "input_text",
                    "text": (
                        "Triage the following figure pages for digitizable ibuprofen endpoint curves.\n\n"
                        f"DOI: {content_handle.doi}\nTITLE: {route_decision.title}\nIMAGES: {page_desc}\n\n"
                        "Return structured output only."
                    ),
                }
            ]
            for _, image_url in page_map:
                content.append({"type": "input_image", "image_url": image_url})

            response = client.responses.parse(
                model=model_name,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                text_format=FigureTriageResult,
            )
            record_openai_usage(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.figure.triage",
                model_name=model_name,
                response=response,
                prompt_payload=[SYSTEM_PROMPT, content],
                output_payload=response.output_parsed.model_dump(mode="json"),
                metadata={"paper_id": content_handle.paper_id, "doi": content_handle.doi},
                retries_used=attempt,
            )
            payload = response.output_parsed.model_dump(mode="json")
            page_number = payload.get("page_number")
            trace_id = _make_trace_id(
                content_handle=content_handle,
                figure_id=str(payload.get("figure_id", "") or ""),
                page_number=page_number if isinstance(page_number, int) else None,
                subplot=str(payload.get("subplot", "") or ""),
            )
            return FigureTriageArtifact(
                paper_id=content_handle.paper_id,
                doi=content_handle.doi,
                title=route_decision.title,
                trace_id=trace_id,
                pdf_path=pdf_path,
                anchor_pages=[page + 1 for page in anchors],
                selected_pages=[page for page, _ in page_map],
                selected_image_path=saved_paths.get(page_number, ""),
                selected_image_paths=[saved_paths[page] for page, _ in page_map if page in saved_paths],
                page_debug=page_debug,
                page_scores=page_scores,
                **payload,
            )
        except Exception as exc:
            attempt += 1
            record_openai_attempt_failure(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.figure.triage",
                model_name=model_name,
                exc=exc,
                attempt=attempt,
                max_retries=max_retries,
                metadata={"paper_id": content_handle.paper_id, "doi": content_handle.doi},
                terminal=attempt >= max_retries,
            )
            if attempt >= max_retries:
                raise
            _backoff(attempt)


def triage_figure_routes(
    routed_rows: list[dict],
    image_dir: str | Path = "outputs/figure_triage_images",
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    model: str = "gpt-4o-mini",
) -> list[dict]:
    """Backward-compatible batch wrapper for figure triage."""

    run_context = ExtractorRunContext(
        run_id="legacy_figure_triage_batch",
        model_name=model,
        output_dir=str(Path(image_dir).parent),
        fail_on_malformed_output=False,
    )
    artifacts: list[FigureTriageArtifact] = []
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
        if route_decision.route not in {"figure", "mixed"}:
            continue
        artifacts.append(triage_figure_content(content_handle, route_decision, run_context))

    rows = [artifact.model_dump(mode="json") for artifact in artifacts]
    if output_jsonl:
        write_jsonl(rows, output_jsonl)
    if output_csv:
        write_optional_csv(rows, output_csv)
    return rows
