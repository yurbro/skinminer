"""Typed evaluation fixtures, gold-label models, and annotated-gold CSV rows."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


BinaryGoldFlag = Literal["yes", "no", "uncertain", ""]
EndpointValueFlag = Literal["yes", "no", "approximate", "uncertain", ""]
AreaFlag = Literal["yes", "no", "n_a", "uncertain", ""]
KeepFlag = Literal["yes", "no", ""]


class GoldAuditCsvRow(BaseModel):
    """Annotated round-level audit row stored in CSV form."""

    model_config = ConfigDict(extra="forbid")

    record_id: str
    paper_id: str
    doi: str = ""
    paper_url: str = ""
    route: Literal["text", "table", "figure", "mixed"]
    verification_status: Literal["verified", "unresolved", "rejected"]
    failure_reasons: list[str] = Field(default_factory=list)
    scope_tags: list[str] = Field(default_factory=list)
    api_name: str = ""
    api_concentration_value: str = ""
    api_concentration_unit: str = ""
    api_basis: str = ""
    endpoint_kind: str = ""
    endpoint_value: str = ""
    endpoint_unit: str = ""
    endpoint_time_value: str = ""
    endpoint_time_unit: str = ""
    device: str = ""
    study_type: str = ""
    diffusion_area_cm2: str = ""
    evidence_preview: str = ""

    gold_target_api_ok: BinaryGoldFlag = ""
    gold_5pct_ww_ok: BinaryGoldFlag = ""
    gold_franz_ok: BinaryGoldFlag = ""
    gold_ivpt_ivrt_ok: BinaryGoldFlag = ""
    gold_amount_endpoint_ok: BinaryGoldFlag = ""
    gold_endpoint_time_ok: BinaryGoldFlag = ""
    gold_endpoint_value_correct: EndpointValueFlag = ""
    gold_area_ok: AreaFlag = ""
    gold_keep_record: KeepFlag = ""
    gold_scope_correct: BinaryGoldFlag = ""
    gold_value_correct: EndpointValueFlag = ""
    gold_notes: str = ""

    @field_validator("failure_reasons", "scope_tags", mode="before")
    @classmethod
    def _split_semicolon_list(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        text = str(value).strip()
        if not text:
            return []
        return [item.strip() for item in re.split(r"[;|]", text) if item.strip()]
