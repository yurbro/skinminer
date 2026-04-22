"""VLM-based direct value reading for locked-subplot figure rows."""

from __future__ import annotations

import base64
import random
import re
import time
from pathlib import Path
from typing import Any, Literal

import cv2
import fitz
from pydantic import BaseModel, Field

from extractors.common import resolve_stage_model
from extractors.figure.models import DigitizedEndpointArtifact, FigureTriageArtifact, FigureVLMReadingArtifact
from extractors.figure.triage import TRIAGE_RENDER_DPI
from schemas.models import ExtractorRunContext, Record
from utils.llm_client import parse_structured, resolve_provider_from_context
from utils.long_run import record_openai_attempt_failure, record_openai_usage

FIGURE_VLM_PROMPT_ASSET_ID = "extractors.figure.vlm_digitize"
FIGURE_VLM_PROMPT_VERSION = "2026-04-11.v1"

SYSTEM_PROMPT = (
    "You are a strict scientific vision extraction assistant for dermal ibuprofen figure reading. "
    "You are given one locked subplot crop that should already isolate the target panel. "
    "Use only the supplied crop and structured context. Do not invent labels or values. "
    "Return visual series identity first, before any downstream grounding. "
    "If the subplot is unreadable or the series identity cannot be grounded confidently, say so. "
    "Prefer conservative structured output over guesses."
)


class VLMReading(BaseModel):
    series_marker_raw: str = ""
    series_label_raw: str = ""
    series_rank_hint: str = ""
    endpoint_time: float | None = None
    endpoint_time_unit: str = ""
    endpoint_value: float | None = None
    endpoint_unit: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""


class VLMFigureResult(BaseModel):
    subplot_semantic_type: Literal[
        "permeation_plot",
        "release_plot",
        "calibration_curve",
        "formulation_schematic",
        "other",
    ] = "other"
    axis_summary: str = ""
    legend_summary: str = ""
    readability_status: Literal["readable", "partially_readable", "unreadable"] = "unreadable"
    quality_flags: list[str] = Field(default_factory=list)
    readings: list[VLMReading] = Field(default_factory=list)


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


def _normalize_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _canonicalize_label(value: str) -> str:
    text = (value or "").strip().lower()
    text = text.replace("®", "").replace("™", "")
    text = text.replace("µ", "u").replace("μ", "u")
    text = re.sub(r"[^a-z0-9#+]+", " ", text)
    return " ".join(text.split())


def _extract_preparation_index(value: str) -> str:
    match = re.search(r"(?:preparation|prep)\s*#?\s*(\d+)|#\s*(\d+)", value or "", flags=re.IGNORECASE)
    if not match:
        return ""
    return next(group for group in match.groups() if group)


def _image_to_data_url(path: str) -> str:
    image_bytes = Path(path).read_bytes()
    return f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"


def _coerce_endpoint_rows(endpoint_rows: list[DigitizedEndpointArtifact | dict[str, Any]]) -> list[DigitizedEndpointArtifact]:
    return [row if isinstance(row, DigitizedEndpointArtifact) else DigitizedEndpointArtifact.model_validate(row) for row in endpoint_rows]


def _select_locked_direct_endpoint(endpoint_rows: list[DigitizedEndpointArtifact]) -> DigitizedEndpointArtifact | None:
    for row in endpoint_rows:
        if (
            row.status == "ok"
            and row.candidate_tier == "triage_primary"
            and not row.subplot_lock_failed
            and str(row.crop_path or "").strip()
            and Path(str(row.crop_path)).exists()
        ):
            return row
    return None


def _match_label_to_space(candidate: str, label_space: list[str]) -> tuple[str, str]:
    normalized = _canonicalize_label(candidate)
    if not normalized:
        return "", ""
    label_space = list(dict.fromkeys(label for label in label_space if label))

    exact_matches = [label for label in label_space if _canonicalize_label(label) == normalized]
    if len(exact_matches) == 1:
        return exact_matches[0], "exact"

    contains_matches = [label for label in label_space if normalized in _canonicalize_label(label)]
    if len(contains_matches) == 1:
        return contains_matches[0], "contains"

    reverse_matches = [label for label in label_space if _canonicalize_label(label) in normalized]
    if len(reverse_matches) == 1:
        return reverse_matches[0], "reverse_contains"

    candidate_index = _extract_preparation_index(candidate)
    if candidate_index:
        indexed_matches = []
        for label in label_space:
            label_index = _extract_preparation_index(label)
            if label_index and label_index == candidate_index:
                indexed_matches.append(label)
        if len(indexed_matches) == 1:
            return indexed_matches[0], "preparation_index"

    return "", ""


def _ground_series_identity(
    *,
    series_label_raw: str,
    figure_label_space: list[str],
    source_label_space: list[str],
) -> tuple[str, str, str]:
    if figure_label_space:
        match, basis = _match_label_to_space(series_label_raw, figure_label_space)
        if match:
            source_match, source_basis = _match_label_to_space(match, source_label_space)
            if source_match:
                return source_match, f"figure:{basis}|source:{source_basis}", "figure_label_space"
            return match, f"figure:{basis}", "figure_label_space_only"

    if source_label_space:
        match, basis = _match_label_to_space(series_label_raw, source_label_space)
        if match:
            canonical_source = _canonicalize_label(match)
            if (
                len(source_label_space) == 1
                and any(token in canonical_source for token in ("preparations", "series", "all"))
                and _extract_preparation_index(series_label_raw)
            ):
                return "", "", "aggregate_source_only"
            return match, basis, "source_label_space"

    if not series_label_raw:
        return "", "", "none"
    return "", "", "ungrounded"


def _extract_page_text_snippet(pdf_path: str, page_number: int | None, max_chars: int = 800) -> str:
    if page_number is None or page_number <= 0:
        return ""
    try:
        document = fitz.open(pdf_path)
        page = document.load_page(page_number - 1)
        text = page.get_text("text") or ""
        document.close()
    except Exception:
        return ""
    collapsed = " ".join(text.split())
    return collapsed[:max_chars]


def _known_condition_context(table_records: list[Record]) -> str:
    rows: list[str] = []
    seen: set[str] = set()
    for record in table_records:
        condition = record.conditions
        bits = [
            f"label={record.formulation.label}" if record.formulation.label else "",
            f"membrane_type={condition.membrane_type}" if condition.membrane_type else "",
            f"membrane_source={condition.membrane_source}" if condition.membrane_source else "",
            f"membrane_thickness_um={condition.membrane_thickness_um}" if condition.membrane_thickness_um is not None else "",
            f"receptor_medium={condition.receptor_medium}" if condition.receptor_medium else "",
            f"dose_type={condition.dose_type}" if condition.dose_type else "",
            f"dose_amount={condition.dose_amount}" if condition.dose_amount else "",
        ]
        line = "; ".join(bit for bit in bits if bit)
        if line and line not in seen:
            rows.append(f"- {line}")
            seen.add(line)
    return "\n".join(rows)


def _build_context_packet(
    triage: FigureTriageArtifact,
    source_endpoint: DigitizedEndpointArtifact,
    table_records: list[Record],
    crop_width_px: int,
    crop_height_px: int,
) -> str:
    source_label_space = list(dict.fromkeys(record.formulation.label for record in table_records if record.formulation.label))
    figure_label_space = [entry.label for entry in triage.legend if entry.label]
    target_timepoint = source_endpoint.endpoint_time if source_endpoint.endpoint_time is not None else triage.x_max
    expected_unit = source_endpoint.endpoint_unit or triage.axes_y_unit
    expected_kind = source_endpoint.y_kind or triage.y_kind
    page_text_snippet = _extract_page_text_snippet(triage.pdf_path, triage.page_number)
    known_conditions = _known_condition_context(table_records)
    return (
        f"PAPER_ID: {triage.paper_id}\n"
        f"DOI: {triage.doi}\n"
        f"FIGURE_ID: {triage.figure_id}\n"
        f"PAGE_NUMBER: {triage.page_number}\n"
        f"SUBPLOT: {triage.subplot or '(single-panel)'}\n"
        f"FIGURE_SEMANTIC_TYPE: {triage.figure_semantic_type}\n"
        f"CANDIDATE_TIER: {source_endpoint.candidate_tier}\n"
        f"SUBPLOT_LOCK_FAILED: {source_endpoint.subplot_lock_failed}\n"
        f"CROP_WIDTH_PX: {crop_width_px}\n"
        f"CROP_HEIGHT_PX: {crop_height_px}\n"
        f"SOURCE_RENDER_DPI: {TRIAGE_RENDER_DPI}\n"
        f"AXES_X_LABEL: {triage.axes_x_label}\n"
        f"AXES_X_UNIT: {triage.axes_x_unit}\n"
        f"AXES_X_RANGE: {triage.x_min} to {triage.x_max}\n"
        f"AXES_Y_LABEL: {triage.axes_y_label}\n"
        f"AXES_Y_UNIT: {triage.axes_y_unit}\n"
        f"AXES_Y_RANGE: {triage.y_min} to {triage.y_max}\n"
        f"TARGET_TIMEPOINT_H: {target_timepoint}\n"
        f"EXPECTED_ENDPOINT_KIND: {expected_kind}\n"
        f"EXPECTED_ENDPOINT_UNIT: {expected_unit}\n"
        f"FIGURE_LABEL_SPACE: {figure_label_space}\n"
        f"SOURCE_LABEL_SPACE: {source_label_space}\n"
        f"KNOWN_CONDITION_CONTEXT:\n{known_conditions or '- none'}\n"
        f"PAGE_TEXT_SNIPPET: {page_text_snippet}\n"
    )


def extract_vlm_readings(
    triage: FigureTriageArtifact,
    endpoint_rows: list[DigitizedEndpointArtifact | dict[str, Any]],
    table_records: list[Record],
    run_context: ExtractorRunContext,
    *,
    max_retries: int = 6,
) -> list[FigureVLMReadingArtifact]:
    """Run a conservative VLM value-reading pass on a locked direct subplot crop."""

    endpoints = _coerce_endpoint_rows(endpoint_rows)
    source_endpoint = _select_locked_direct_endpoint(endpoints)
    if source_endpoint is None:
        return []

    crop_path = str(source_endpoint.crop_path)
    crop = cv2.imread(crop_path)
    if crop is None:
        return []
    crop_height_px, crop_width_px = crop.shape[:2]

    source_label_space = [record.formulation.label for record in table_records if record.formulation.label]
    figure_label_space = [entry.label for entry in triage.legend if entry.label]
    if not source_label_space and not figure_label_space:
        return []

    prompt_text = (
        "Read the locked subplot crop and extract endpoint values for visually distinct series.\n\n"
        "Rules:\n"
        "1. Return one reading per visible series only.\n"
        "2. Return visual series identity first: series_marker_raw and/or series_label_raw.\n"
        "3. Use FIGURE_LABEL_SPACE as the preferred grounding hint if the crop itself lacks a readable legend.\n"
        "4. Use SOURCE_LABEL_SPACE only as a secondary hint; do not force a match if it does not fit the visible series.\n"
        "5. Do not collapse multiple series onto the same top curve or reuse the same endpoint value across different markers unless visually obvious.\n"
        "6. Read values at TARGET_TIMEPOINT_H.\n"
        "7. Use KNOWN_CONDITION_CONTEXT only as source-backed experiment context; do not infer new membrane, receptor, or dose fields from the figure crop.\n"
        "8. If the subplot is not a permeation/release plot, return readability_status=unreadable.\n"
        "9. If you are uncertain, prefer fewer readings with lower confidence over guessing.\n\n"
        f"{_build_context_packet(triage, source_endpoint, table_records, crop_width_px, crop_height_px)}"
    )

    data_url = _image_to_data_url(crop_path)
    provider = resolve_provider_from_context(run_context)
    model_name = resolve_stage_model(run_context, "figure_vlm")
    attempt = 0
    while True:
        try:
            user_content = [
                {"type": "input_text", "text": prompt_text},
                {"type": "input_image", "image_url": data_url},
            ]
            response = parse_structured(
                provider=provider,
                model=model_name,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                text_format=VLMFigureResult,
                timeout=90,
            )
            parsed = response.output_parsed
            record_openai_usage(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.figure.vlm_digitize",
                model_name=model_name,
                response=response,
                prompt_payload=[SYSTEM_PROMPT, user_content],
                output_payload=parsed.model_dump(mode="json"),
                metadata={"paper_id": triage.paper_id, "doi": triage.doi, "trace_id": triage.trace_id},
                retries_used=attempt,
            )
            artifacts: list[FigureVLMReadingArtifact] = []
            if not parsed.readings:
                artifacts.append(
                    FigureVLMReadingArtifact(
                        paper_id=triage.paper_id,
                        doi=triage.doi,
                        title=triage.title,
                        trace_id=f"{triage.trace_id}::vlm",
                        triage_trace_id=triage.trace_id,
                        figure_id=triage.figure_id,
                        page_number=triage.page_number,
                        subplot=triage.subplot,
                        image_path=source_endpoint.image_path,
                        crop_path=crop_path,
                        candidate_tier=source_endpoint.candidate_tier,
                        subplot_lock_failed=source_endpoint.subplot_lock_failed,
                        crop_width_px=crop_width_px,
                        crop_height_px=crop_height_px,
                        source_render_dpi=TRIAGE_RENDER_DPI,
                        vlm_model=model_name,
                        vlm_prompt_asset_id=FIGURE_VLM_PROMPT_ASSET_ID,
                        vlm_prompt_version=FIGURE_VLM_PROMPT_VERSION,
                        subplot_semantic_type=parsed.subplot_semantic_type,
                        readability_status=parsed.readability_status,
                        quality_flags=list(parsed.quality_flags),
                        series_marker_raw="",
                        series_label_raw="",
                        series_rank_hint="",
                        source_endpoint_trace_id=source_endpoint.trace_id,
                        notes=parsed.legend_summary or parsed.axis_summary,
                        grounding_status="none",
                        figure_label_space=figure_label_space,
                        source_label_space=source_label_space,
                        reconciliation_status="unreadable" if parsed.readability_status == "unreadable" else "pending",
                        raw_response=parsed.model_dump(mode="json"),
                    )
                )
                return artifacts

            for index, reading in enumerate(parsed.readings, start=1):
                candidate_label = reading.series_label_raw
                matched_label, match_basis, grounding_status = _ground_series_identity(
                    series_label_raw=candidate_label,
                    figure_label_space=figure_label_space,
                    source_label_space=source_label_space,
                )
                artifacts.append(
                    FigureVLMReadingArtifact(
                        paper_id=triage.paper_id,
                        doi=triage.doi,
                        title=triage.title,
                        trace_id=f"{triage.trace_id}::vlm::{index}",
                        triage_trace_id=triage.trace_id,
                        figure_id=triage.figure_id,
                        page_number=triage.page_number,
                        subplot=triage.subplot,
                        image_path=source_endpoint.image_path,
                        crop_path=crop_path,
                        candidate_tier=source_endpoint.candidate_tier,
                        subplot_lock_failed=source_endpoint.subplot_lock_failed,
                        crop_width_px=crop_width_px,
                        crop_height_px=crop_height_px,
                        source_render_dpi=TRIAGE_RENDER_DPI,
                        vlm_model=model_name,
                        vlm_prompt_asset_id=FIGURE_VLM_PROMPT_ASSET_ID,
                        vlm_prompt_version=FIGURE_VLM_PROMPT_VERSION,
                        subplot_semantic_type=parsed.subplot_semantic_type,
                        readability_status=parsed.readability_status,
                        quality_flags=list(parsed.quality_flags),
                        series_marker_raw=reading.series_marker_raw,
                        series_label_raw=reading.series_label_raw,
                        series_rank_hint=reading.series_rank_hint,
                        formulation_label=matched_label,
                        legend_label_raw=reading.series_marker_raw or reading.series_label_raw,
                        legend_match_basis=match_basis,
                        grounding_status=grounding_status,
                        figure_label_space=figure_label_space,
                        source_label_space=source_label_space,
                        endpoint_time=reading.endpoint_time,
                        endpoint_time_unit=reading.endpoint_time_unit,
                        endpoint_value=reading.endpoint_value,
                        endpoint_unit=reading.endpoint_unit,
                        confidence=reading.confidence,
                        notes=reading.notes,
                        source_endpoint_trace_id=source_endpoint.trace_id,
                        raw_response=parsed.model_dump(mode="json"),
                    )
                )
            return artifacts
        except Exception as exc:
            attempt += 1
            record_openai_attempt_failure(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.figure.vlm_digitize",
                model_name=model_name,
                exc=exc,
                attempt=attempt,
                max_retries=max_retries,
                metadata={"paper_id": triage.paper_id, "doi": triage.doi, "trace_id": triage.trace_id},
                terminal=attempt >= max_retries,
            )
            if attempt >= max_retries:
                return [
                    FigureVLMReadingArtifact(
                        paper_id=triage.paper_id,
                        doi=triage.doi,
                        title=triage.title,
                        trace_id=f"{triage.trace_id}::vlm_error",
                        triage_trace_id=triage.trace_id,
                        figure_id=triage.figure_id,
                        page_number=triage.page_number,
                        subplot=triage.subplot,
                        image_path=source_endpoint.image_path,
                        crop_path=crop_path,
                        candidate_tier=source_endpoint.candidate_tier,
                        subplot_lock_failed=source_endpoint.subplot_lock_failed,
                        crop_width_px=crop_width_px,
                        crop_height_px=crop_height_px,
                        source_render_dpi=TRIAGE_RENDER_DPI,
                        vlm_model=model_name,
                        vlm_prompt_asset_id=FIGURE_VLM_PROMPT_ASSET_ID,
                        vlm_prompt_version=FIGURE_VLM_PROMPT_VERSION,
                        subplot_semantic_type=triage.figure_semantic_type,
                        readability_status="unreadable",
                        quality_flags=["vlm_error"],
                        series_marker_raw="",
                        series_label_raw="",
                        series_rank_hint="",
                        source_endpoint_trace_id=source_endpoint.trace_id,
                        notes=f"error:{type(exc).__name__}",
                        grounding_status="none",
                        figure_label_space=figure_label_space,
                        source_label_space=source_label_space,
                        reconciliation_status="unreadable",
                        raw_response={"error": type(exc).__name__, "message": str(exc)},
                    )
                ]
            _backoff(attempt)
