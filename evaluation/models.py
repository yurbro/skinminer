"""Typed evaluation fixtures and gold-label models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GoldRecordLabel(BaseModel):
    """Gold label for a single expected structured record."""

    model_config = ConfigDict(extra="forbid")

    record_label: str = ""
    study_type: str = ""
    device: str = ""
    barrier: str = ""
    api_name: str = ""
    api_concentration_value: float | None = None
    api_concentration_unit: str = ""
    api_basis: str = ""
    endpoint_kind: str = ""
    endpoint_value: float | None = None
    endpoint_unit: str = ""
    endpoint_time_value: float | None = None
    endpoint_time_unit: str = ""
    area_cm2: float | None = None
    support_locators: list[str] = Field(default_factory=list)
    review_notes: str = ""


class GoldLabelEntry(BaseModel):
    """Gold label entry for one evaluation fixture paper."""

    model_config = ConfigDict(extra="forbid")

    fixture_id: str
    paper_id: str
    doi: str = ""
    title: str = ""
    fixture_bucket: Literal["text_only", "table_only", "figure_only", "mixed", "other"] = "other"
    route_gold: Literal["text", "table", "figure", "mixed", "unresolved"]
    verification_gold: Literal["verified", "unresolved", "rejected", "uncertain"] = "uncertain"
    records_gold: list[GoldRecordLabel] = Field(default_factory=list)
    annotation_notes: str = ""
