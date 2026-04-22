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
from pydantic import BaseModel, Field

from extractors.common import artifact_path, require_pdf_path, resolve_stage_model
from extractors.figure.models import FigureTriageArtifact, LegendEntry
from schemas.models import ContentAccess, ExtractorRunContext, RouteDecision
from utils.io import sanitize_filename, write_jsonl, write_optional_csv
from utils.llm_client import LLMProvider, parse_structured, resolve_provider_from_context
from utils.long_run import record_openai_attempt_failure, record_openai_usage

FIGURE_TRIAGE_PROMPT_ASSET_ID = "extractors.figure.triage"
FIGURE_TRIAGE_PROMPT_VERSION = "2026-04-06.v1"
TRIAGE_RENDER_DPI = 170
CALIBRATION_RETRY_REASON = "calibration_curve_not_target"
TRIAGE_RETRY_MAX_CANDIDATE_PAGES = 3

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


def _derive_figure_semantic_type(result: FigureTriageResult) -> str:
    """Derive a stable high-level figure semantic type from existing triage fields."""

    x_text = f"{result.axes_x_label} {result.axes_x_unit}".strip().lower()
    y_text = f"{result.axes_y_label} {result.axes_y_unit}".strip().lower()
    notes = (result.notes or "").strip().lower()
    figure_id = (result.figure_id or "").strip().lower()

    if (
        ("concentration" in x_text and ("absorbance" in y_text or "mau" in y_text))
        or "calibration" in notes
        or "calibration" in figure_id
    ):
        return "calibration_curve"

    if any(
        token in notes
        for token in (
            "schematic",
            "cad model",
            "exploded view",
            "front view",
            "top view",
            "isometric view",
            "device diagram",
        )
    ):
        return "formulation_schematic"

    if result.y_kind == "percent" or any(token in y_text for token in ("percent", "% permeated", "% released")):
        return "release_plot"

    if (
        result.endpoint_curve_present == "yes"
        or result.recommended_route == "digitize"
        or any(token in notes for token in ("permeation", "permeated", "cumulative amount", "amount permeated"))
    ):
        return "permeation_plot"

    return "other"


def _derive_has_permeation_plot(result: FigureTriageResult) -> bool:
    """Derive a stable aggregate flag from existing triage decisions without changing triage logic."""

    if result.recommended_route == "digitize":
        return True
    if result.endpoint_curve_present == "yes":
        return True
    if result.endpoint_curve_present == "no":
        return False
    if result.likely_endpoint_type in {"cumulative_amount", "flux", "jss"}:
        return True
    return False


def _normalize_subplot_selection(raw_value: str) -> tuple[str, str]:
    """Normalize triage subplot output into a single actionable panel when possible."""

    raw = (raw_value or "").strip()
    if not raw:
        return "", "single"

    normalized = raw.upper()
    panel_matches = re.findall(r"(?<![A-Z])([ABCD])(?![A-Z])", normalized)
    ordered_unique = [panel for panel in ("A", "B", "C", "D") if panel in panel_matches]

    if len(ordered_unique) == 1:
        return ordered_unique[0], "single"
    if len(ordered_unique) > 1:
        return ordered_unique[0], "coerced_from_multi"
    return "", "ambiguous_none"


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


def _route_endpoint_hint_text(route_decision: RouteDecision) -> str:
    raw_labels = route_decision.raw_labels if isinstance(route_decision.raw_labels, dict) else {}
    parts = [
        route_decision.notes,
        str(raw_labels.get("where_endpoint", "") or ""),
        str(raw_labels.get("endpoint_carrier_snippet", "") or ""),
        str(raw_labels.get("notes", "") or ""),
    ]
    for item in route_decision.anchor_evidence:
        parts.extend([item.field_name, item.locator or "", item.snippet or ""])
    return "\n".join(part for part in parts if part)


def _parse_figure_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    for match in re.finditer(r"\bfig(?:ure)?\.?\s*(\d+)\s*[a-z]?\b", text or "", flags=re.IGNORECASE):
        number = int(match.group(1))
        if number not in numbers:
            numbers.append(number)
    return numbers


def _page_retry_score(document: fitz.Document, page_index: int, base_score: float) -> float:
    page = document.load_page(page_index)
    text = page.get_text("text") or ""
    has_img, draw_ratio = _page_graphics_flags(page)
    score = base_score + _score_text(text)
    if has_img:
        score += 12.0
    if draw_ratio >= 0.02:
        score += 8.0
    lowered = text.lower()
    if any(token in lowered for token in ("permeation profile", "amount permeated", "permeated vs time")):
        score += 18.0
    if "calibration" in lowered and not any(token in lowered for token in ("figure 11", "fig. 11")):
        score -= 20.0
    return score


def _pick_calibration_retry_pages(
    pdf_path: str,
    route_decision: RouteDecision,
    primary_artifact: FigureTriageArtifact,
    max_pages_to_send: int = TRIAGE_RETRY_MAX_CANDIDATE_PAGES,
) -> tuple[list[int], str, list[int]]:
    """Pick alternate pages after the primary page was rejected as a calibration curve."""

    document = fitz.open(pdf_path)
    primary_page_index = (primary_artifact.page_number - 1) if primary_artifact.page_number else None
    hint_text = _route_endpoint_hint_text(route_decision)
    figure_numbers = [
        number
        for number in _parse_figure_numbers(hint_text)
        if str(number) != str(primary_artifact.figure_id or "").strip()
    ]
    candidate_scores: dict[int, float] = {}

    for page_index in range(min(document.page_count, 160)):
        page_text = document.load_page(page_index).get_text("text") or ""
        for figure_number in figure_numbers:
            if re.search(rf"\bfig(?:ure)?\.?\s*{figure_number}\s*[a-z]?\b", page_text, flags=re.IGNORECASE):
                for offset in (-1, 0, 1):
                    neighbor = page_index + offset
                    if 0 <= neighbor < document.page_count:
                        base_score = 100.0 - abs(offset) * 12.0
                        candidate_scores[neighbor] = max(
                            candidate_scores.get(neighbor, 0.0),
                            _page_retry_score(document, neighbor, base_score),
                        )

    if not candidate_scores:
        for key, score in primary_artifact.page_scores.items():
            match = re.search(r"page_(\d+)", key)
            if not match:
                continue
            page_index = int(match.group(1)) - 1
            if 0 <= page_index < document.page_count:
                candidate_scores[page_index] = max(
                    candidate_scores.get(page_index, 0.0),
                    _page_retry_score(document, page_index, float(score)),
                )

    if primary_page_index is not None:
        candidate_scores.pop(primary_page_index, None)

    ranked = sorted(candidate_scores.items(), key=lambda item: (-item[1], item[0]))
    selected = [page_index for page_index, _score in ranked[:max_pages_to_send]]
    debug = " | ".join(f"p{page_index + 1}:retry_score={score:.1f}" for page_index, score in ranked[:8])
    document.close()
    return selected, debug, [page + 1 for page in selected]


def _render_page_image_bytes(pdf_path: str, page_index: int, dpi: int = TRIAGE_RENDER_DPI) -> bytes:
    document = fitz.open(pdf_path)
    page = document.load_page(page_index)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    document.close()
    return pixmap.tobytes("jpg")


def _render_triage_page_map(
    pdf_path: str,
    page_indexes: list[int],
    content_handle: ContentAccess,
    run_context: ExtractorRunContext,
) -> tuple[list[tuple[int, str]], dict[int, str]]:
    page_map: list[tuple[int, str]] = []
    saved_paths: dict[int, str] = {}
    for page_index in page_indexes:
        image_bytes = _render_page_image_bytes(pdf_path, page_index, dpi=TRIAGE_RENDER_DPI)
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
    return page_map, saved_paths


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


def _normalize_triage_payload(result: FigureTriageResult) -> dict:
    payload = result.model_dump(mode="json")
    subplot_raw = str(payload.get("subplot", "") or "")
    normalized_subplot, subplot_selection_status = _normalize_subplot_selection(subplot_raw)
    payload["subplot"] = normalized_subplot
    payload["subplot_raw"] = subplot_raw
    payload["subplot_selection_status"] = subplot_selection_status
    if subplot_selection_status == "coerced_from_multi":
        payload["notes"] = (
            ((payload.get("notes") or "").strip() + " | " if payload.get("notes") else "")
            + f"subplot_coerced_from_multi:{subplot_raw}"
        )
    elif subplot_selection_status == "ambiguous_none":
        payload["notes"] = (
            ((payload.get("notes") or "").strip() + " | " if payload.get("notes") else "")
            + f"subplot_ambiguous:{subplot_raw}"
        )
    figure_semantic_type = _derive_figure_semantic_type(result)
    payload["figure_semantic_type"] = figure_semantic_type
    payload["has_permeation_plot"] = _derive_has_permeation_plot(result)
    if figure_semantic_type == "calibration_curve":
        payload["has_permeation_plot"] = False
        payload["digitizable"] = "no"
        payload["recommended_route"] = "skip"
        payload["why_not_digitizable"] = payload.get("why_not_digitizable") or CALIBRATION_RETRY_REASON
        payload["notes"] = (
            ((payload.get("notes") or "").strip() + " | " if payload.get("notes") else "")
            + "semantic_gate=calibration_curve"
        )
    return payload


def _triage_user_content(
    *,
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    page_map: list[tuple[int, str]],
    retry_context: str = "",
) -> list[dict]:
    page_desc = ", ".join(f"Image {index + 1} = PAGE {page_number}" for index, (page_number, _) in enumerate(page_map))
    base_text = (
        "Triage the following figure pages for digitizable ibuprofen endpoint curves.\n\n"
        f"DOI: {content_handle.doi}\nTITLE: {route_decision.title}\nIMAGES: {page_desc}\n\n"
        "If the selected figure page contains multiple subplots, return exactly one target subplot "
        "as a single capital letter A/B/C/D. Never return comma-separated or semicolon-separated "
        "subplot lists. If several panels are plausible, choose the single best panel in reading "
        "order and explain ambiguity in notes. If the figure is single-panel, leave subplot empty.\n\n"
        "Return structured output only."
    )
    if retry_context:
        base_text = (
            "Second-pass figure triage after the primary candidate was rejected as a calibration curve.\n\n"
            f"{retry_context}\n\n"
            "Find a non-calibration ibuprofen permeation, release, cumulative amount, flux, or Jss endpoint plot. "
            "Do not select a calibration curve, standard curve, schematic, device photo, or UV image panel. "
            "If a page contains a plot panel plus image panels, select the plot panel only.\n\n"
            + base_text
        )
    content: list[dict] = [{"type": "input_text", "text": base_text}]
    for _, image_url in page_map:
        content.append({"type": "input_image", "image_url": image_url})
    return content


def _call_triage_model(
    *,
    llm_provider: str | LLMProvider,
    model_name: str,
    run_context: ExtractorRunContext,
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    page_map: list[tuple[int, str]],
    module_name: str,
    retry_context: str = "",
    max_retries: int = 6,
) -> dict:
    provider = LLMProvider.parse(llm_provider)
    attempt = 0
    while True:
        try:
            content = _triage_user_content(
                content_handle=content_handle,
                route_decision=route_decision,
                page_map=page_map,
                retry_context=retry_context,
            )
            response = parse_structured(
                provider=provider,
                model=model_name,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                text_format=FigureTriageResult,
                timeout=90,
            )
            record_openai_usage(
                run_context.shared_state.get("long_run_monitor"),
                module_name=module_name,
                model_name=model_name,
                response=response,
                prompt_payload=[SYSTEM_PROMPT, content],
                output_payload=response.output_parsed.model_dump(mode="json"),
                metadata={"paper_id": content_handle.paper_id, "doi": content_handle.doi},
                retries_used=attempt,
            )
            return _normalize_triage_payload(response.output_parsed)
        except Exception as exc:
            attempt += 1
            record_openai_attempt_failure(
                run_context.shared_state.get("long_run_monitor"),
                module_name=module_name,
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


def _build_triage_artifact(
    *,
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    pdf_path: str,
    anchors: list[int],
    page_map: list[tuple[int, str]],
    saved_paths: dict[int, str],
    page_debug: str,
    page_scores: dict[str, float],
    payload: dict,
    retry_metadata: dict | None = None,
) -> FigureTriageArtifact:
    page_number = payload.get("page_number")
    trace_id = _make_trace_id(
        content_handle=content_handle,
        figure_id=str(payload.get("figure_id", "") or ""),
        page_number=page_number if isinstance(page_number, int) else None,
        subplot=str(payload.get("subplot", "") or ""),
    )
    artifact_payload = {
        "paper_id": content_handle.paper_id,
        "doi": content_handle.doi,
        "title": route_decision.title,
        "trace_id": trace_id,
        "pdf_path": pdf_path,
        "anchor_pages": [page + 1 for page in anchors],
        "selected_pages": [page for page, _ in page_map],
        "selected_image_path": saved_paths.get(page_number, "") if isinstance(page_number, int) else "",
        "selected_image_paths": [saved_paths[page] for page, _ in page_map if page in saved_paths],
        "page_debug": page_debug,
        "page_scores": page_scores,
        **payload,
    }
    if retry_metadata:
        artifact_payload.update(retry_metadata)
    return FigureTriageArtifact(**artifact_payload)


def _is_calibration_gate(artifact: FigureTriageArtifact) -> bool:
    return (
        artifact.figure_semantic_type == "calibration_curve"
        and artifact.recommended_route == "skip"
        and artifact.why_not_digitizable == CALIBRATION_RETRY_REASON
    )


def _retry_after_calibration_gate(
    *,
    primary_artifact: FigureTriageArtifact,
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    run_context: ExtractorRunContext,
    pdf_path: str,
    anchors: list[int],
    llm_provider: str | LLMProvider,
    model_name: str,
    max_retries: int,
) -> FigureTriageArtifact:
    retry_pages, retry_debug, retry_page_numbers = _pick_calibration_retry_pages(
        pdf_path,
        route_decision,
        primary_artifact,
    )
    retry_base_metadata = {
        "triage_retry_triggered": True,
        "triage_retry_reason": CALIBRATION_RETRY_REASON,
        "triage_retry_source_trace_id": primary_artifact.trace_id,
        "triage_retry_source_figure_id": primary_artifact.figure_id,
        "triage_retry_source_page": primary_artifact.page_number,
        "triage_retry_candidate_pages": retry_page_numbers,
    }
    if not retry_pages:
        return primary_artifact.model_copy(
            update={
                **retry_base_metadata,
                "triage_retry_result": "no_permeation_candidate",
                "triage_retry_notes": "No alternate page candidates after excluding calibration primary page.",
            }
        )

    page_map, saved_paths = _render_triage_page_map(pdf_path, retry_pages, content_handle, run_context)
    retry_context = (
        f"PRIMARY_REJECTED_FIGURE_ID: {primary_artifact.figure_id}\n"
        f"PRIMARY_REJECTED_PAGE: {primary_artifact.page_number}\n"
        f"PRIMARY_REJECTED_REASON: {CALIBRATION_RETRY_REASON}\n"
        f"ENDPOINT_HINTS: {_route_endpoint_hint_text(route_decision)[:1200]}\n"
        f"RETRY_CANDIDATE_PAGES: {retry_page_numbers}"
    )
    try:
        payload = _call_triage_model(
            llm_provider=llm_provider,
            model_name=model_name,
            run_context=run_context,
            content_handle=content_handle,
            route_decision=route_decision,
            page_map=page_map,
            module_name="extractors.figure.triage.retry",
            retry_context=retry_context,
            max_retries=max_retries,
        )
    except Exception as exc:
        return primary_artifact.model_copy(
            update={
                **retry_base_metadata,
                "triage_retry_result": "retry_failed",
                "triage_retry_notes": str(exc)[:500],
            }
        )

    result = "recovered_digitizable" if payload.get("recommended_route") == "digitize" else "retry_not_digitizable"
    retry_artifact = _build_triage_artifact(
        content_handle=content_handle,
        route_decision=route_decision,
        pdf_path=pdf_path,
        anchors=anchors,
        page_map=page_map,
        saved_paths=saved_paths,
        page_debug=(retry_debug or primary_artifact.page_debug),
        page_scores=primary_artifact.page_scores,
        payload=payload,
        retry_metadata={
            **retry_base_metadata,
            "triage_retry_candidate_page": payload.get("page_number") if isinstance(payload.get("page_number"), int) else None,
            "triage_retry_result": result,
            "triage_retry_notes": "Second-pass calibration retry.",
        },
    )
    if result == "recovered_digitizable":
        return retry_artifact
    return primary_artifact.model_copy(
        update={
            **retry_base_metadata,
            "triage_retry_candidate_page": retry_artifact.page_number,
            "triage_retry_result": result,
            "triage_retry_notes": retry_artifact.why_not_digitizable or retry_artifact.notes,
        }
    )


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
    page_map, saved_paths = _render_triage_page_map(pdf_path, selected_pages, content_handle, run_context)
    provider = resolve_provider_from_context(run_context)
    model_name = resolve_stage_model(run_context, "figure_triage")
    payload = _call_triage_model(
        llm_provider=provider,
        model_name=model_name,
        run_context=run_context,
        content_handle=content_handle,
        route_decision=route_decision,
        page_map=page_map,
        module_name="extractors.figure.triage",
        max_retries=max_retries,
    )
    primary_artifact = _build_triage_artifact(
        content_handle=content_handle,
        route_decision=route_decision,
        pdf_path=pdf_path,
        anchors=anchors,
        page_map=page_map,
        saved_paths=saved_paths,
        page_debug=page_debug,
        page_scores=page_scores,
        payload=payload,
    )
    if _is_calibration_gate(primary_artifact):
        return _retry_after_calibration_gate(
            primary_artifact=primary_artifact,
            content_handle=content_handle,
            route_decision=route_decision,
            run_context=run_context,
            pdf_path=pdf_path,
            anchors=anchors,
            llm_provider=provider,
            model_name=model_name,
            max_retries=max_retries,
        )
    return primary_artifact


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
