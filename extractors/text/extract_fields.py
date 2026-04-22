"""Structured field extraction for text-route candidate records."""

from __future__ import annotations

import random
import time
from typing import Literal

from pydantic import BaseModel, Field

from extractors.common import resolve_stage_model
from extractors.text.page_selection import TextEvidenceWindow
from schemas.models import ExtractorRunContext, RouteDecision
from utils.llm_client import parse_structured, resolve_provider_from_context
from utils.long_run import record_openai_attempt_failure, record_openai_usage

TEXT_EXTRACTION_PROMPT_ASSET_ID = "extractors.text.structured_fields"
TEXT_EXTRACTION_PROMPT_VERSION = "2026-04-11.v1"

SYSTEM_PROMPT = (
    "You are a careful scientific extraction assistant. "
    "Use ONLY the supplied structured content blocks or PDF page text with explicit locators. "
    "Do not guess. Prefer numeric tables when available. "
    "When citing evidence, keep the provided locator style such as 'block 7' or 'page 12'."
)


class LegacyEvidenceItem(BaseModel):
    """Evidence item emitted by the text-route extraction prompt."""

    field: str
    locator: str
    snippet: str


class Ingredient(BaseModel):
    """A formulation ingredient as read from text or tables in the selected pages."""

    name: str
    concentration_raw: str = ""


class LegacyEndpoint(BaseModel):
    """Endpoint structure emitted by the text-route extraction prompt."""

    endpoint_type: Literal["Q_final", "flux", "Jss"]
    value: float | None = None
    unit: str = ""
    time_value: float | None = None
    time_unit: str = ""


class LegacyExtractedRecord(BaseModel):
    """Raw record payload emitted by the text-route extraction prompt."""

    study_type: Literal["IVPT", "IVRT", "both", "uncertain"]
    cell_type: Literal["Franz", "diffusion_cell_unspecified", "other", "uncertain"]
    dosage_form: str = ""
    barrier_category: Literal["skin", "synthetic_membrane", "both", "uncertain"]
    barrier_name: str = ""
    api_name: Literal["ibuprofen"] = "ibuprofen"
    api_conc_raw: str = ""
    diffusion_area_cm2: float | None = None
    membrane_type: str = ""
    membrane_source: str = ""
    membrane_thickness_um: float | None = None
    receptor_medium: str = ""
    dose_type: str = ""
    dose_amount: str = ""
    endpoint_main: LegacyEndpoint
    endpoint_optional: list[LegacyEndpoint] = Field(default_factory=list)
    ingredients: list[Ingredient] = Field(default_factory=list)
    evidence: list[LegacyEvidenceItem] = Field(default_factory=list)
    needs_supp: Literal["yes", "no", "uncertain"] = "uncertain"
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""


class PaperExtraction(BaseModel):
    """Paper-level extraction wrapper for text-route extraction."""

    doi: str = ""
    title: str = ""
    records: list[LegacyExtractedRecord] = Field(default_factory=list, max_length=5)
    extraction_notes: str = ""


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


def extract_text_fields(
    window: TextEvidenceWindow,
    route_decision: RouteDecision,
    run_context: ExtractorRunContext,
    max_retries: int = 6,
) -> PaperExtraction:
    """Run the text extraction prompt over a selected evidence window."""

    provider = resolve_provider_from_context(run_context)
    model_name = resolve_stage_model(run_context, "text_extract")
    doi = route_decision.doi
    title = route_decision.title or str(route_decision.raw_labels.get("title", "") or "")
    prompt = (
        "Extract structured records for ibuprofen diffusion-cell IVPT/IVRT text-route evidence. "
        "Return up to five explicit records only when multiple formulations are clearly reported.\n\n"
        "Extraction requirements:\n"
        "- Extract vehicle/excipient composition into ingredients, including non-API ingredient names and raw concentration text.\n"
        "- Extract membrane_type, membrane_source, and membrane_thickness_um when explicitly reported.\n"
        "- Extract receptor_medium when explicitly reported, including pH and surfactants/cosolvents.\n"
        "- Extract dose_type as finite or infinite when explicitly reported, plus dose_amount as the source text amount.\n"
        "- Include evidence items for membrane, receptor medium, dose, excipients, API concentration, endpoint, time, area, and device when present.\n"
        "- Do not guess missing fields and do not treat receptor-medium drug concentration as formulation API concentration.\n\n"
        f"DOI: {doi}\n"
        f"TITLE: {title}\n"
        f"SOURCE_FORMAT: {window.source_format}\n"
        f"SOURCE_BACKEND: {window.source_backend}\n"
        f"SOURCE_REF: {window.source_ref}\n"
        f"LOCATOR_MODE: {window.locator_mode}\n"
        f"ANCHOR_LOCATORS: {window.anchor_locators}\n"
        f"SELECTED_LOCATORS: {window.selected_locators}\n"
        f"TABLE_HINT: {window.table_hint}\n\n"
        f"CONTENT:\n{window.content_text}"
    )

    attempt = 0
    while True:
        try:
            response = parse_structured(
                provider=provider,
                model=model_name,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                text_format=PaperExtraction,
                timeout=90,
            )
            record_openai_usage(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.text",
                model_name=model_name,
                response=response,
                prompt_payload=[SYSTEM_PROMPT, prompt],
                output_payload=response.output_parsed.model_dump(mode="json"),
                metadata={"doi": doi, "source_backend": window.source_backend},
                retries_used=attempt,
            )
            return response.output_parsed
        except Exception as exc:
            attempt += 1
            record_openai_attempt_failure(
                run_context.shared_state.get("long_run_monitor"),
                module_name="extractors.text",
                model_name=model_name,
                exc=exc,
                attempt=attempt,
                max_retries=max_retries,
                metadata={"doi": doi, "source_backend": window.source_backend},
                terminal=attempt >= max_retries,
            )
            if attempt >= max_retries:
                raise
            _backoff(attempt)
