"""Typed intermediate artifacts for the figure extraction subsystem."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LegendEntry(BaseModel):
    """Legend entry detected during figure triage."""

    label: str = ""
    color_hint: str = ""


class FigureTriageArtifact(BaseModel):
    """Figure triage output for a single paper."""

    paper_id: str
    doi: str = ""
    title: str = ""
    trace_id: str = ""
    pdf_path: str = ""
    anchor_pages: list[int] = Field(default_factory=list)
    selected_pages: list[int] = Field(default_factory=list)
    selected_image_path: str = ""
    selected_image_paths: list[str] = Field(default_factory=list)
    page_debug: str = ""
    page_scores: dict[str, float] = Field(default_factory=dict)
    endpoint_curve_present: Literal["yes", "no", "uncertain"] = "uncertain"
    likely_endpoint_type: Literal["cumulative_amount", "flux", "jss", "unknown"] = "unknown"
    figure_id: str = ""
    page_number: int | None = None
    subplot: str = ""
    digitizable: Literal["yes", "no", "uncertain"] = "uncertain"
    why_not_digitizable: str = ""
    ticks_readable: Literal["yes", "no", "uncertain"] = "uncertain"
    legend_present: Literal["yes", "no", "uncertain"] = "uncertain"
    approx_curves_count: int | None = None
    legend: list[LegendEntry] = Field(default_factory=list)
    suggests_table_exists: Literal["yes", "no", "uncertain"] = "uncertain"
    suggests_supp_exists: Literal["yes", "no", "uncertain"] = "uncertain"
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
    confidence: float | None = None
    notes: str = ""


class DigitizedCurveArtifact(BaseModel):
    """Curve-level output produced by figure digitization."""

    paper_id: str
    doi: str = ""
    title: str = ""
    trace_id: str = ""
    triage_trace_id: str = ""
    figure_id: str = ""
    page_number: int | None = None
    subplot: str = ""
    image_path: str = ""
    crop_path: str = ""
    mask_path: str = ""
    overlay_path: str = ""
    preprocessed_path: str = ""
    bbox_overlay_path: str = ""
    bbox_source: str = ""
    bbox_used: list[float] = Field(default_factory=list)
    curve_id: str = ""
    curve_color: str = ""
    x_unit: str = ""
    y_unit: str = ""
    y_kind: str = "unknown"
    x_min: float | None = None
    x_max: float | None = None
    y_min: float | None = None
    y_max: float | None = None
    t_last: float | None = None
    q_final: float | None = None
    curve_xy: list[list[float]] = Field(default_factory=list)
    status: str = "ok"
    diagnostics: dict[str, str | int | float] = Field(default_factory=dict)


class DigitizedEndpointArtifact(BaseModel):
    """Endpoint-level output produced from a digitized figure curve."""

    paper_id: str
    doi: str = ""
    title: str = ""
    trace_id: str = ""
    triage_trace_id: str = ""
    figure_id: str = ""
    page_number: int | None = None
    subplot: str = ""
    image_path: str = ""
    crop_path: str = ""
    mask_path: str = ""
    overlay_path: str = ""
    preprocessed_path: str = ""
    bbox_overlay_path: str = ""
    bbox_source: str = ""
    bbox_used: list[float] = Field(default_factory=list)
    status: str = "ok"
    curve_id: str = ""
    curve_color: str = ""
    endpoint_time: float | None = None
    endpoint_time_unit: str = ""
    endpoint_value: float | None = None
    endpoint_unit: str = ""
    y_kind: str = "unknown"
    diagnostics: dict[str, str | int | float] = Field(default_factory=dict)


class FigureMappingArtifact(BaseModel):
    """Mapping output aligning a digitized curve to a formulation label."""

    paper_id: str
    doi: str = ""
    trace_id: str = ""
    triage_trace_id: str = ""
    figure_id: str = ""
    page_number: int | None = None
    subplot: str = ""
    curve_id: str
    curve_color: str = ""
    curve_label: str = ""
    mapping_image_path: str = ""
    allowed_formulation_labels: list[str] = Field(default_factory=list)
    source_table_record_ids: list[str] = Field(default_factory=list)
    mapped_formulation_label: str | None = None
    mapping_status: Literal["vision_mapped", "unmapped"] = "unmapped"
    mapping_rationale: str = ""
    mapping_confidence: float | None = None
