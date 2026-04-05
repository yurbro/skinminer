"""Curve-to-formulation mapping with typed traceability artifacts."""

from __future__ import annotations

import base64
import random
import time
from pathlib import Path
from typing import Any

import cv2
from openai import OpenAI
from pydantic import BaseModel, Field

from extractors.common import artifact_path, resolve_stage_model
from extractors.figure.models import DigitizedEndpointArtifact, FigureMappingArtifact, FigureTriageArtifact
from schemas.models import ExtractorRunContext, Record
from utils.io import write_jsonl, write_optional_csv
from utils.long_run import record_openai_attempt_failure, record_openai_usage

FIGURE_MAPPING_PROMPT_ASSET_ID = "extractors.figure.curve_map"
FIGURE_MAPPING_PROMPT_VERSION = "2026-03-28.v1"

SYSTEM_PROMPT = (
    "You align digitized endpoint curves to formulation labels using the supplied zoomed plot image and formulation labels. "
    "Choose only from the provided formulation labels. If unclear, leave the assignment null."
)


class MapItem(BaseModel):
    """Single curve mapping result from the vision mapping prompt."""

    curve_id: str
    curve_color: str = ""
    assigned_formulation_label: str | None = None
    evidence_from_legend: str = ""
    rationale: str = ""
    confidence: float = Field(ge=0.0, le=1.0)


class MapResult(BaseModel):
    """Structured mapping response for a paper's digitized curves."""

    mappings: list[MapItem] = Field(default_factory=list)
    notes: str = ""


def _crop_zoom(image_path: str, bbox: list[float], margin: float = 0.10) -> Any:
    image = cv2.imread(image_path)
    if image is None:
        return None
    height, width = image.shape[:2]
    x0, y0, x1, y1 = [float(item) for item in bbox]
    dx = (x1 - x0) * margin
    dy = (y1 - y0) * margin
    x0 = max(0.0, x0 - dx)
    x1 = min(1.0, x1 + dx)
    y0 = max(0.0, y0 - dy)
    y1 = min(1.0, y1 + dy)
    left = int(round(x0 * width))
    right = int(round(x1 * width))
    top = int(round(y0 * height))
    bottom = int(round(y1 * height))
    crop = image[top:bottom, left:right].copy()
    if crop.size == 0 or crop.shape[0] < 2 or crop.shape[1] < 2:
        return None
    return cv2.resize(crop, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)


def _load_existing_image(path: str) -> Any:
    candidate = str(path or "").strip()
    if not candidate or not Path(candidate).exists():
        return None
    return cv2.imread(candidate)


def _build_mapping_zoom(
    endpoint: DigitizedEndpointArtifact,
    triage_artifact: FigureTriageArtifact,
) -> tuple[Any, str]:
    """Resolve the best available zoom image for figure mapping.

    Mapping now prefers the digitizer-selected crop because the digitizer may have
    switched page image or bbox during multi-image / multi-bbox fallback.
    """

    crop = _load_existing_image(endpoint.crop_path)
    if crop is not None and crop.size > 0:
        return cv2.resize(crop, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC), "digitized_crop"

    preprocessed = _load_existing_image(endpoint.preprocessed_path)
    if preprocessed is not None and preprocessed.size > 0:
        return cv2.resize(preprocessed, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC), "digitized_preprocessed"

    bbox = endpoint.bbox_used or triage_artifact.plot_bbox
    image_path = endpoint.image_path or triage_artifact.selected_image_path
    if bbox and image_path and Path(image_path).exists():
        crop = _crop_zoom(image_path, bbox)
        if crop is not None:
            source = "endpoint_bbox" if endpoint.bbox_used else "triage_bbox"
            return crop, source

    return None, "missing_image_or_bbox"


def _img_to_data_url(image: Any) -> str:
    ok, encoded = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        raise RuntimeError("Failed to encode crop")
    return f"data:image/jpeg;base64,{base64.b64encode(encoded.tobytes()).decode('utf-8')}"


def _write_mapping_zoom(run_context: ExtractorRunContext, triage_artifact: FigureTriageArtifact, crop: Any) -> str:
    path = artifact_path(
        run_context,
        "figure",
        "mapping_zooms",
        f"{triage_artifact.trace_id or triage_artifact.paper_id}.jpg",
    )
    ok = cv2.imwrite(str(path), crop)
    if not ok:
        raise RuntimeError("Failed to write mapping zoom image")
    return str(path)


def _component_summary(record: Record) -> str:
    names = [component.name for component in record.formulation.components if component.name]
    return "; ".join(names[:10])


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


def _coerce_endpoint_rows(endpoint_rows: list[DigitizedEndpointArtifact | dict[str, Any]]) -> list[DigitizedEndpointArtifact]:
    return [row if isinstance(row, DigitizedEndpointArtifact) else DigitizedEndpointArtifact.model_validate(row) for row in endpoint_rows]


def map_curves_to_formulations(
    triage_artifacts: list[FigureTriageArtifact],
    endpoint_rows: list[DigitizedEndpointArtifact | dict[str, Any]],
    table_records: list[Record],
    run_context: ExtractorRunContext,
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
) -> list[FigureMappingArtifact]:
    """Map digitized curves to formulation labels for figure-route assembly."""

    client = OpenAI(timeout=90)
    model_name = resolve_stage_model(run_context, "figure_map")
    triage_by_paper = {artifact.paper_id: artifact for artifact in triage_artifacts}
    tables_by_paper: dict[str, list[Record]] = {}
    for record in table_records:
        tables_by_paper.setdefault(record.paper_id, []).append(record)

    endpoints_by_paper: dict[str, list[DigitizedEndpointArtifact]] = {}
    for row in _coerce_endpoint_rows(endpoint_rows):
        if row.status == "ok":
            endpoints_by_paper.setdefault(row.paper_id, []).append(row)

    mappings: list[FigureMappingArtifact] = []
    for paper_id, endpoints in endpoints_by_paper.items():
        triage_artifact = triage_by_paper.get(paper_id)
        table_group = tables_by_paper.get(paper_id, [])
        allowed_labels = [record.formulation.label for record in table_group if record.formulation.label]
        if not triage_artifact or not allowed_labels:
            mappings.extend(
                FigureMappingArtifact(
                    paper_id=paper_id,
                    doi=endpoint.doi,
                    trace_id=endpoint.trace_id,
                    triage_trace_id=endpoint.triage_trace_id,
                    figure_id=endpoint.figure_id,
                    page_number=endpoint.page_number,
                    subplot=endpoint.subplot,
                    curve_id=endpoint.curve_id,
                    curve_color=endpoint.curve_color,
                    allowed_formulation_labels=allowed_labels,
                    source_table_record_ids=[record.record_id for record in table_group],
                    mapped_formulation_label=None,
                    mapping_status="unmapped",
                    mapping_rationale="missing_triage_or_table_records",
                    mapping_confidence=0.0,
                )
                for endpoint in endpoints
            )
            continue

        zoom_endpoint = endpoints[0]
        crop, crop_source = _build_mapping_zoom(zoom_endpoint, triage_artifact)
        if crop is None:
            mappings.extend(
                FigureMappingArtifact(
                    paper_id=paper_id,
                    doi=endpoint.doi,
                    trace_id=endpoint.trace_id,
                    triage_trace_id=endpoint.triage_trace_id,
                    figure_id=endpoint.figure_id,
                    page_number=endpoint.page_number,
                    subplot=endpoint.subplot,
                    curve_id=endpoint.curve_id,
                    curve_color=endpoint.curve_color,
                    allowed_formulation_labels=allowed_labels,
                    source_table_record_ids=[record.record_id for record in table_group],
                    mapped_formulation_label=None,
                    mapping_status="unmapped",
                    mapping_rationale=f"failed_zoom_crop:{crop_source}",
                    mapping_confidence=0.0,
                )
                for endpoint in endpoints
            )
            continue
        mapping_image_path = _write_mapping_zoom(run_context, triage_artifact, crop)
        plot_data_url = _img_to_data_url(crop)
        curve_text = "\n".join(
            f"- curve_id={row.curve_id}, curve_color={row.curve_color}, endpoint~{row.endpoint_value} {row.endpoint_unit}"
            for row in endpoints
        )
        formulation_text = "\n".join(
            f"- {record.formulation.label} | api={record.formulation.api_name} {record.formulation.api_concentration_value} {record.formulation.api_concentration_unit} | comps: {_component_summary(record)}"
            for record in table_group
        )

        attempt = 0
        while True:
            try:
                user_content = [
                    {
                        "type": "input_text",
                        "text": (
                            "Map each curve_id to one formulation label.\n\n"
                            f"Allowed labels:\n{chr(10).join(f'- {label}' for label in allowed_labels)}\n\n"
                            f"Curves:\n{curve_text}\n\nFormulations:\n{formulation_text}"
                        ),
                    },
                    {"type": "input_image", "image_url": plot_data_url},
                ]
                response = client.responses.parse(
                    model=model_name,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    text_format=MapResult,
                )
                record_openai_usage(
                    run_context.shared_state.get("long_run_monitor"),
                    module_name="extractors.figure.map_curves",
                    model_name=model_name,
                    response=response,
                    prompt_payload=[SYSTEM_PROMPT, user_content],
                    output_payload=response.output_parsed.model_dump(mode="json"),
                    metadata={"paper_id": paper_id, "doi": triage_artifact.doi},
                    retries_used=attempt,
                )
                mapping_lookup = {item.curve_id: item for item in response.output_parsed.mappings}
                for endpoint in endpoints:
                    mapping = mapping_lookup.get(endpoint.curve_id)
                    mappings.append(
                        FigureMappingArtifact(
                            paper_id=paper_id,
                            doi=endpoint.doi,
                            trace_id=endpoint.trace_id,
                            triage_trace_id=endpoint.triage_trace_id,
                            figure_id=endpoint.figure_id,
                            page_number=endpoint.page_number,
                            subplot=endpoint.subplot,
                            curve_id=endpoint.curve_id,
                            curve_color=endpoint.curve_color,
                            curve_label=mapping.evidence_from_legend if mapping else "",
                            mapping_image_path=mapping_image_path,
                            allowed_formulation_labels=allowed_labels,
                            source_table_record_ids=[record.record_id for record in table_group],
                            mapped_formulation_label=mapping.assigned_formulation_label if mapping else None,
                            mapping_status="vision_mapped" if mapping and mapping.assigned_formulation_label else "unmapped",
                            mapping_rationale=((mapping.rationale if mapping else "") + f" | zoom_source={crop_source}").strip(" |"),
                            mapping_confidence=mapping.confidence if mapping else 0.0,
                        )
                    )
                break
            except Exception as exc:
                attempt += 1
                record_openai_attempt_failure(
                    run_context.shared_state.get("long_run_monitor"),
                    module_name="extractors.figure.map_curves",
                    model_name=model_name,
                    exc=exc,
                    attempt=attempt,
                    max_retries=6,
                    metadata={"paper_id": paper_id, "doi": triage_artifact.doi},
                    terminal=attempt >= 6,
                )
                if attempt >= 6:
                    raise
                _backoff(attempt)

    if output_jsonl:
        write_jsonl(mappings, output_jsonl)
    if output_csv:
        write_optional_csv([mapping.model_dump(mode="json") for mapping in mappings], output_csv)
    return mappings
