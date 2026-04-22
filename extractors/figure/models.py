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
    triage_retry_triggered: bool = False
    triage_retry_reason: str = ""
    triage_retry_source_trace_id: str = ""
    triage_retry_source_figure_id: str = ""
    triage_retry_source_page: int | None = None
    triage_retry_candidate_pages: list[int] = Field(default_factory=list)
    triage_retry_candidate_page: int | None = None
    triage_retry_result: Literal[
        "",
        "recovered_digitizable",
        "no_permeation_candidate",
        "retry_not_digitizable",
        "retry_failed",
    ] = ""
    triage_retry_notes: str = ""
    subplot_raw: str = ""
    subplot_selection_status: Literal["single", "coerced_from_multi", "ambiguous_none"] = "single"
    figure_semantic_type: Literal[
        "permeation_plot",
        "release_plot",
        "calibration_curve",
        "formulation_schematic",
        "other",
    ] = "other"
    has_permeation_plot: bool = False
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
    candidate_tier: str = ""
    subplot_lock_failed: bool = False
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
    curve_point_count_raw: int = 0
    curve_point_count_sanitized: int = 0
    endpoint_value_raw: float | None = None
    endpoint_value_sanitized: float | None = None
    endpoint_sampling_status: Literal["stable_tail", "unstable_tail", "too_sparse"] = "stable_tail"
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
    candidate_tier: str = ""
    subplot_lock_failed: bool = False
    bbox_used: list[float] = Field(default_factory=list)
    status: str = "ok"
    triage_decision: str = ""
    failure_reason: str = ""
    source_path: str = ""
    curve_id: str = ""
    curve_color: str = ""
    endpoint_time: float | None = None
    endpoint_time_unit: str = ""
    endpoint_value: float | None = None
    endpoint_unit: str = ""
    y_kind: str = "unknown"
    curve_point_count_raw: int = 0
    curve_point_count_sanitized: int = 0
    endpoint_value_raw: float | None = None
    endpoint_value_sanitized: float | None = None
    endpoint_sampling_status: Literal["stable_tail", "unstable_tail", "too_sparse"] = "stable_tail"
    diagnostics: dict[str, str | int | float] = Field(default_factory=dict)


class FigureVLMReadingArtifact(BaseModel):
    """VLM-derived direct figure reading for a locked subplot crop."""

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
    candidate_tier: str = ""
    subplot_lock_failed: bool = False
    crop_width_px: int = 0
    crop_height_px: int = 0
    source_render_dpi: int | None = None
    vlm_model: str = ""
    vlm_prompt_asset_id: str = ""
    vlm_prompt_version: str = ""
    subplot_semantic_type: str = "other"
    readability_status: Literal["readable", "partially_readable", "unreadable"] = "unreadable"
    quality_flags: list[str] = Field(default_factory=list)
    series_marker_raw: str = ""
    series_label_raw: str = ""
    series_rank_hint: str = ""
    formulation_label: str = ""
    legend_label_raw: str = ""
    legend_match_basis: str = ""
    grounding_status: Literal[
        "pending",
        "figure_label_space",
        "source_label_space",
        "figure_label_space_only",
        "aggregate_source_only",
        "ungrounded",
        "none",
    ] = "pending"
    figure_label_space: list[str] = Field(default_factory=list)
    source_label_space: list[str] = Field(default_factory=list)
    endpoint_time: float | None = None
    endpoint_time_unit: str = ""
    endpoint_value: float | None = None
    endpoint_unit: str = ""
    confidence: float | None = None
    notes: str = ""
    source_endpoint_trace_id: str = ""
    reconciliation_status: Literal[
        "pending",
        "vlm_only",
        "cv_vlm_agree",
        "cv_vlm_disagreement",
        "cv_only",
        "unreadable",
        "no_source_record",
    ] = "pending"
    vlm_used_as_final: bool = False
    cv_vlm_delta_pct: float | None = None
    raw_response: dict = Field(default_factory=dict)


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
    mapping_status: Literal["vision_mapped", "unmapped", "underconstrained_labels"] = "unmapped"
    mapping_label_space_status: Literal["complete", "underconstrained"] = "complete"
    detected_curve_count: int = 0
    allowed_label_count: int = 0
    mapping_rationale: str = ""
    mapping_confidence: float | None = None
