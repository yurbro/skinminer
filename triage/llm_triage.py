from __future__ import annotations

import logging
import random
import time
from typing import Any, Iterable, Literal, Mapping

from openai import OpenAI
from pydantic import BaseModel, Field

from triage.prompts import DEFAULT_TRIAGE_SYSTEM_PROMPT, build_triage_user_prompt
from utils.io import write_jsonl, write_optional_csv
from utils.long_run import LongRunMonitor, record_openai_attempt_failure, record_openai_usage
from utils.resume import load_jsonl_if_exists
from utils.status_panel import ProgressCallback

LOGGER = logging.getLogger("skinminer.triage.llm")


class LLMTriageResult(BaseModel):
    queue: Literal["now", "later", "park"]
    relevance_label: Literal["relevant", "maybe", "not_relevant"]
    mentions_franz_in_abstract: Literal["yes", "no"]
    likely_study_type: Literal["IVPT", "IVRT", "both", "uncertain"]
    likely_has_measurable_endpoint: Literal["yes", "no", "uncertain"]
    likely_has_formulation_info: Literal["yes", "no", "uncertain"]
    likely_barrier_category: Literal["skin", "synthetic_membrane", "both", "uncertain"]
    what_to_check_in_fulltext: list[str] = Field(default_factory=list, min_length=1, max_length=5)
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


def _truncate(text: str, max_chars: int = 2_000) -> str:
    cleaned = (text or "").strip()
    return cleaned if len(cleaned) <= max_chars else f"{cleaned[:max_chars]} ...[truncated]"


def _backoff_sleep(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


def _record_resume_key(record: Mapping[str, Any]) -> str:
    paper_id = str(record.get("paper_id", "") or "").strip()
    doi = str(record.get("doi", "") or "").strip().lower()
    title = str(record.get("title", "") or "").strip().lower()
    if paper_id:
        return f"paper_id:{paper_id}"
    if doi:
        return f"doi:{doi}"
    return f"title:{title}"


def triage_records_with_llm(
    records: Iterable[Mapping[str, Any]],
    model: str = "gpt-4o-mini",
    system_prompt: str = DEFAULT_TRIAGE_SYSTEM_PROMPT,
    output_jsonl: str | None = None,
    output_csv: str | None = None,
    max_retries: int = 6,
    progress_every: int = 25,
    checkpoint_every: int = 25,
    progress_callback: ProgressCallback | None = None,
    long_run_monitor: LongRunMonitor | None = None,
    resume_jsonl: str | None = None,
) -> list[dict[str, Any]]:
    client = OpenAI()
    record_list = list(records)
    progress_every = max(1, progress_every)
    checkpoint_every = max(1, checkpoint_every)
    existing_rows = load_jsonl_if_exists(resume_jsonl)
    existing_map = {
        _record_resume_key(row): dict(row)
        for row in existing_rows
    }
    triaged_map: dict[str, dict[str, Any]] = {}
    for row in record_list:
        key = _record_resume_key(row)
        if key in existing_map and key not in triaged_map:
            triaged_map[key] = existing_map[key]
    completed_before = len(triaged_map)

    LOGGER.info("Starting LLM triage for %s abstracts with model=%s", len(record_list), model)
    if progress_callback and completed_before:
        progress_callback(completed_before, "resume", f"loaded={completed_before}")

    remaining_records = [dict(row) for row in record_list if _record_resume_key(row) not in triaged_map]
    for remaining_index, row in enumerate(remaining_records, start=1):
        record = dict(row)
        title = str(record.get("title", "") or "")
        abstract = _truncate(str(record.get("abstract", "") or ""))
        completed_so_far = completed_before + remaining_index - 1
        current_item = str(record.get("paper_id", "") or record.get("doi", "") or title[:60] or f"row_{completed_so_far + 1}")
        attempt = 0

        if progress_callback:
            progress_callback(completed_so_far, current_item, "requesting LLM triage")

        while True:
            try:
                user_prompt = build_triage_user_prompt(title, abstract)
                response = client.responses.parse(
                    model=model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    text_format=LLMTriageResult,
                )
                record_openai_usage(
                    long_run_monitor,
                    module_name="triage.llm_triage",
                    model_name=model,
                    response=response,
                    prompt_payload=[system_prompt, user_prompt],
                    output_payload=response.output_parsed.model_dump(mode="json"),
                    metadata={"paper_id": current_item, "doi": str(record.get("doi", "") or "")},
                    retries_used=attempt,
                )
                result = response.output_parsed.model_dump()
                record.update(result)
                triaged_map[_record_resume_key(record)] = record
                if progress_callback:
                    progress_callback(completed_so_far + 1, current_item, f"queue={record.get('queue', '')}")
                break
            except Exception as exc:
                attempt += 1
                record_openai_attempt_failure(
                    long_run_monitor,
                    module_name="triage.llm_triage",
                    model_name=model,
                    exc=exc,
                    attempt=attempt,
                    max_retries=max_retries,
                    metadata={"paper_id": current_item, "doi": str(record.get("doi", "") or "")},
                    terminal=attempt >= max_retries,
                )
                if attempt >= max_retries:
                    record.update(
                        {
                            "queue": "park",
                            "relevance_label": "not_relevant",
                            "mentions_franz_in_abstract": "no",
                            "likely_study_type": "uncertain",
                            "likely_has_measurable_endpoint": "uncertain",
                            "likely_has_formulation_info": "uncertain",
                            "likely_barrier_category": "uncertain",
                            "what_to_check_in_fulltext": ["LLM triage failed; re-run this record."],
                            "rationale": f"error:{type(exc).__name__}",
                            "confidence": 0.0,
                        }
                    )
                    triaged_map[_record_resume_key(record)] = record
                    if progress_callback:
                        progress_callback(completed_so_far + 1, current_item, f"failed:{type(exc).__name__}")
                    break
                _backoff_sleep(attempt)

        completed_total = completed_so_far + 1
        if output_jsonl and (completed_total % checkpoint_every == 0 or completed_total == len(record_list)):
            ordered_triaged = [triaged_map[_record_resume_key(record)] for record in record_list if _record_resume_key(record) in triaged_map]
            write_jsonl(ordered_triaged, output_jsonl)

        if completed_total % progress_every == 0 or completed_total == len(record_list):
            LOGGER.info("LLM triage progress %s/%s", completed_total, len(record_list))

    ordered_triaged = [triaged_map[_record_resume_key(record)] for record in record_list if _record_resume_key(record) in triaged_map]

    if output_jsonl:
        write_jsonl(ordered_triaged, output_jsonl)
    write_optional_csv(ordered_triaged, output_csv)
    return ordered_triaged
