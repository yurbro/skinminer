"""Typed evaluation fixtures, gold-label models, and annotated-gold CSV rows."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Mapping

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


# Round-2 release adapter models. These coexist with the original Pydantic
# fixture/audit models so legacy evaluation imports remain valid.
POLICY_LEVELS = ("v1", "v2", "v3", "v4")
FIRST_LEVELS = (*POLICY_LEVELS, "never")


def _required(row: Mapping[str, str], name: str) -> str:
    if name not in row:
        raise ValueError(f"missing required column: {name}")
    return str(row[name]).strip()


@dataclass(frozen=True)
class Round2GoldCsvRow:
    sample_id: str
    source_baseline: str
    policy_level: str
    pipeline_status_v4: str
    gold_scope_correct: str
    gold_value_correct: str
    gold_keep_record: str
    raw: Mapping[str, str]

    @classmethod
    def from_mapping(cls, row: Mapping[str, str]) -> "Round2GoldCsvRow":
        sample_id = _required(row, "sample_id")
        provider = _required(row, "source_baseline").lower()
        provider = {"openai": "gpt", "anthropic": "claude"}.get(provider, provider)
        if provider not in {"gpt", "claude"}:
            raise ValueError(f"{sample_id}: unsupported source_baseline={provider!r}")
        level = _required(row, "policy_level").lower()
        if level not in FIRST_LEVELS:
            raise ValueError(f"{sample_id}: unsupported policy_level={level!r}")
        return cls(
            sample_id=sample_id,
            source_baseline=provider,
            policy_level=level,
            pipeline_status_v4=_required(row, "pipeline_status_v4").lower(),
            gold_scope_correct=_required(row, "gold_scope_correct").lower(),
            gold_value_correct=_required(row, "gold_value_correct").lower(),
            gold_keep_record=_required(row, "gold_keep_record").lower(),
            raw=dict(row),
        )


@dataclass(frozen=True)
class PolicyScore:
    provider: str
    policy_level: str
    verified: int
    unresolved: int
    rejected: int
    scope_tp: int
    scope_fp: int
    scope_precision: float | None
    scope_value_tp: int
    end_to_end_precision: float | None
    unresolved_keep_yes: int | None
    rejected_keep_no: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "policy_level": self.policy_level,
            "verified": self.verified,
            "unresolved": self.unresolved,
            "rejected": self.rejected,
            "scope_TP": self.scope_tp,
            "scope_FP": self.scope_fp,
            "scope_precision": self.scope_precision,
            "scope_value_TP": self.scope_value_tp,
            "end_to_end_precision": self.end_to_end_precision,
            "unresolved_keep_yes": self.unresolved_keep_yes,
            "rejected_keep_no": self.rejected_keep_no,
        }
