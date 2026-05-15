"""Shared typed models for the SkinMiner research pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FormulationComponent(BaseModel):
    """A formulation component and its reported concentration."""

    model_config = ConfigDict(extra="forbid")

    name: str = ""
    concentration_value: float | None = None
    concentration_unit: str = ""
    basis: str = ""
    raw: str = ""
    note: str = ""


class FormulationSpec(BaseModel):
    """Structured formulation data for a candidate record."""

    model_config = ConfigDict(extra="forbid")

    label: str = ""
    api_name: str = "ibuprofen"
    api_concentration_value: float | None = None
    api_concentration_unit: str = ""
    api_basis: str = ""
    api_concentration_raw: str = ""
    dosage_form: str = ""
    components: list[FormulationComponent] = Field(default_factory=list)


class EndpointSpec(BaseModel):
    """Structured endpoint information extracted from text, tables, or figures."""

    model_config = ConfigDict(extra="forbid")

    field_name: str = "amount"
    kind: Literal["amount_per_area", "amount_total", "percent", "flux", "jss", "unknown"] = "unknown"
    value: float | None = None
    unit: str = ""
    time_value: float | None = None
    time_unit: str = ""
    normalized_value: float | None = None
    normalized_unit: str = ""


class ConditionSpec(BaseModel):
    """Experimental condition information attached to a candidate record."""

    model_config = ConfigDict(extra="forbid")

    temperature_c: float | None = None
    duration_h: float | None = None
    diffusion_area_cm2: float | None = None
    receptor_volume_ml: float | None = None
    membrane_type: str = ""
    membrane_source: str = ""
    membrane_thickness_um: float | None = None
    receptor_medium: str = ""
    dose_type: str = ""
    dose_amount: str = ""
    replicate_count: int | None = None
    notes: list[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    """Evidence snippet and locator supporting a structured field."""

    model_config = ConfigDict(extra="forbid")

    field_name: str
    modality: Literal["metadata", "text", "table", "figure", "mixed"]
    locator: str = ""
    page: int | None = None
    bbox: list[float] | None = None
    snippet: str = ""
    source_ref: str = ""
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class RecordProvenance(BaseModel):
    """Extractor provenance, artifact references, and route metadata."""

    model_config = ConfigDict(extra="forbid")

    extractor_name: str = ""
    source_format: str = ""
    source_path: str = ""
    source_pages: list[int] = Field(default_factory=list)
    route_label: str = ""
    route_notes: str = ""
    artifact_paths: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PatchMetadata(BaseModel):
    """Metadata describing a targeted evidence patch."""

    model_config = ConfigDict(extra="forbid")

    patcher_name: str
    patched_fields: list[str] = Field(default_factory=list)
    status: Literal["applied", "skipped", "failed"] = "skipped"
    evidence_added: int = 0
    notes: str = ""
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Record(BaseModel):
    """Canonical JSONL-first record used across extraction, assembly, and verification."""

    model_config = ConfigDict(extra="forbid")

    record_id: str
    paper_id: str
    doi: str = ""
    route: Literal["text", "table", "figure", "mixed", "unresolved"] = "unresolved"
    study_type: str = "uncertain"
    device: str = ""
    barrier: str = ""
    occlusion: Literal["occluded", "non_occluded", "pretreated", "unknown"] = Field(
        default="unknown",
        description="Donor compartment protocol modifier. 'occluded' = sealed; "
        "'non_occluded' = open; 'pretreated' = membrane pretreated with vehicle "
        "(e.g. ethanol pretreatment); 'unknown' = not captured.",
    )
    formulation: FormulationSpec = Field(default_factory=FormulationSpec)
    endpoint: EndpointSpec = Field(default_factory=EndpointSpec)
    conditions: ConditionSpec = Field(default_factory=ConditionSpec)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    provenance: RecordProvenance = Field(default_factory=RecordProvenance)
    patches: list[PatchMetadata] = Field(default_factory=list)
    route_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    extractor_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    mapping_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    verification_support_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    verification_status: Literal["pending", "verified", "unresolved", "rejected"] = "pending"
    scope_bucket: str = "unknown"
    scope_tags: list[str] = Field(default_factory=list)
    failure_reason: str | None = None
    failure_reasons: list[str] = Field(default_factory=list)
    source_notes: list[str] = Field(default_factory=list)


class ContentAccess(BaseModel):
    """Normalized OA content access handle used by extractors."""

    model_config = ConfigDict(extra="forbid")

    paper_id: str
    doi: str = ""
    pmid: str = ""
    pmcid: str = ""
    title: str = ""
    preferred_format: Literal["pmc_xml", "html", "pdf", "unresolved"] = "unresolved"
    available_formats: list[str] = Field(default_factory=list)
    access_urls: dict[str, str] = Field(default_factory=dict)
    local_paths: dict[str, str] = Field(default_factory=dict)
    status: Literal["resolved", "downloaded", "unresolved", "error"] = "unresolved"
    notes: list[str] = Field(default_factory=list)


class RouteDecision(BaseModel):
    """Route selection output for a paper-level evidence extraction strategy."""

    model_config = ConfigDict(extra="forbid")

    paper_id: str
    doi: str = ""
    title: str = ""
    route: Literal["text", "table", "figure", "mixed", "unresolved"] = "unresolved"
    route_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    endpoint_carrier: str = "unknown"
    formulation_carrier: str = "unknown"
    anchor_evidence: list[EvidenceItem] = Field(default_factory=list)
    notes: str = ""
    raw_labels: dict[str, Any] = Field(default_factory=dict)


class ExtractorRunContext(BaseModel):
    """Runtime context shared across extractor calls in a single pipeline run."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    run_id: str
    model_name: str = ""
    stage_models: dict[str, str] = Field(default_factory=dict)
    output_dir: str = ""
    prompt_paths: list[str] = Field(default_factory=list)
    config_paths: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    fail_on_malformed_output: bool = True
    shared_state: dict[str, Any] = Field(default_factory=dict)


class RunManifest(BaseModel):
    """Minimal reproducibility metadata for a pipeline run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_name: str = ""
    llm_provider: str = "openai"
    policy_name: str = ""
    input_paths: list[str] = Field(default_factory=list)
    prompt_paths: list[str] = Field(default_factory=list)
    config_paths: list[str] = Field(default_factory=list)
    stage_outputs: dict[str, str] = Field(default_factory=dict)
    stage_metrics: dict[str, Any] = Field(default_factory=dict)
    module_notes: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
