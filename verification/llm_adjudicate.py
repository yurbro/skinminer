"""Optional audit-only LLM adjudication prototype for recoverable unresolved ranking."""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path
from typing import Iterable, Literal

from openai import OpenAI
from pydantic import BaseModel, Field

from patchers.common import collect_source_fragments
from schemas.models import Record
from utils.io import load_records_jsonl, write_jsonl, write_optional_csv
from utils.long_run import LongRunMonitor, record_openai_attempt_failure, record_openai_usage
from utils.status_panel import ProgressCallback

ADJUDICATION_PROMPT_ASSET_ID = "verification.llm_adjudication"
ADJUDICATION_PROMPT_VERSION = "2026-04-03.v1"

SYSTEM_PROMPT = (
    "You are a strict scientific adjudicator for a dermal ibuprofen evidence-mining pipeline. "
    "You are NOT doing open-ended extraction. You are reviewing pre-extracted records that are currently "
    "recoverable unresolved candidates under a strict scope: ibuprofen, 5% w/w, Franz diffusion cell, IVPT/IVRT, "
    "amount endpoint, endpoint time required. Use ONLY the supplied structured record fields and evidence packet. "
    "If evidence is missing or conflicting, prefer unresolved rather than verified. "
    "If the record is scientifically useful but outside the strict scope, recommend rejected and mark the scope bucket as useful_but_out_of_scope."
)


class AdjudicationVerdict(BaseModel):
    should_keep_strict: Literal["yes", "no", "uncertain"]
    recommended_status: Literal["verified", "unresolved", "rejected"]
    scope_bucket: Literal["strict_in_scope", "recoverable_unresolved", "useful_but_out_of_scope", "out_of_scope"]
    target_api_ok: Literal["yes", "no", "uncertain"]
    concentration_5pct_ww_ok: Literal["yes", "no", "uncertain"]
    franz_ok: Literal["yes", "no", "uncertain"]
    ivpt_ivrt_ok: Literal["yes", "no", "uncertain"]
    amount_endpoint_ok: Literal["yes", "no", "uncertain"]
    endpoint_time_ok: Literal["yes", "no", "uncertain"]
    area_ok: Literal["yes", "no", "uncertain", "n_a"]
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str


class AdjudicationRow(BaseModel):
    record_id: str
    paper_id: str
    doi: str = ""
    route: str = ""
    original_status: str = ""
    original_scope_bucket: str = ""
    candidate_reason: str = ""
    priority_score: float = 0.0
    priority_bucket: Literal["high", "medium", "low"] = "low"
    review_focus: str = ""
    adjudication: AdjudicationVerdict


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, (2**attempt) * 0.6) + random.random() * 0.4)


def _candidate_reason(record: Record) -> str:
    if "ambiguous_api_concentration" in record.failure_reasons:
        return "recoverable_unresolved:ambiguous_api_concentration"
    if "missing_area" in record.failure_reasons:
        return "recoverable_unresolved:missing_area"
    if "missing_endpoint" in record.failure_reasons:
        return "recoverable_unresolved:missing_endpoint"
    if "unit_normalization_failed" in record.failure_reasons:
        return "recoverable_unresolved:unit_normalization_failed"
    if "missing_endpoint_time" in record.failure_reasons:
        return "recoverable_unresolved:missing_endpoint_time"
    return "recoverable_unresolved:other"


def _priority_score(record: Record) -> float:
    score = 0.0
    if "ambiguous_api_concentration" in record.failure_reasons:
        score += 6.0
    if "missing_area" in record.failure_reasons:
        score += 4.0
    if "missing_endpoint" in record.failure_reasons:
        score += 3.0
    if "unit_normalization_failed" in record.failure_reasons:
        score += 4.0
    if "missing_endpoint_time" in record.failure_reasons:
        score += 2.0
    score += float(record.verification_support_rate or 0.0) * 5.0
    if record.route == "table":
        score += 1.5
    elif record.route == "figure":
        score += 1.0
    elif record.route == "mixed":
        score += 0.5
    return round(score, 3)


def _priority_bucket(score: float) -> Literal["high", "medium", "low"]:
    if score >= 9.0:
        return "high"
    if score >= 5.0:
        return "medium"
    return "low"


def _review_focus(record: Record) -> str:
    if "ambiguous_api_concentration" in record.failure_reasons:
        return "api_concentration_basis"
    if "missing_area" in record.failure_reasons:
        return "diffusion_area"
    if "missing_endpoint" in record.failure_reasons:
        return "endpoint_value"
    if "unit_normalization_failed" in record.failure_reasons:
        return "unit_normalization"
    if "missing_endpoint_time" in record.failure_reasons:
        return "endpoint_time"
    return "strict_scope_check"


def _candidate_sort_key(record: Record) -> tuple[float, float]:
    return (_priority_score(record), float(record.verification_support_rate or 0.0))


def _should_adjudicate(record: Record) -> bool:
    return (
        record.verification_status == "unresolved"
        and record.scope_bucket == "recoverable_unresolved"
        and any(
            code in {
                "missing_area",
                "missing_endpoint",
                "ambiguous_api_concentration",
                "unit_normalization_failed",
                "missing_endpoint_time",
            }
            for code in record.failure_reasons
        )
    )


def select_adjudication_candidates(records: Iterable[Record], limit: int | None = None) -> list[Record]:
    """Return recoverable unresolved records sorted by rescue priority."""

    candidates = [record for record in records if _should_adjudicate(record)]
    candidates.sort(key=_candidate_sort_key, reverse=True)
    if limit is not None:
        candidates = candidates[: max(0, limit)]
    return candidates


def _build_evidence_packet(record: Record, max_fragments: int = 8) -> str:
    evidence_lines: list[str] = []
    for item in record.evidence_items[:10]:
        locator = item.locator or "no_locator"
        evidence_lines.append(
            f"- field={item.field_name} modality={item.modality} locator={locator} snippet={item.snippet}"
        )
    source_fragments = collect_source_fragments(
        record,
        keywords=[
            "ibuprofen",
            "franz",
            "diffusion cell",
            "ivpt",
            "ivrt",
            "permeation",
            "release",
            "flux",
            "jss",
            "% w/w",
            "% w/v",
            "mg/g",
            "mg/ml",
            "mM",
            "effective area",
            "diffusion area",
            "24 h",
            "hours",
        ],
        max_fragments=max_fragments,
    )
    source_lines = [f"- {fragment}" for fragment in source_fragments]
    return "\n".join(
        [
            "RECORD_FIELDS",
            f"- route={record.route}",
            f"- original_status={record.verification_status}",
            f"- original_scope_bucket={record.scope_bucket}",
            f"- study_type={record.study_type}",
            f"- device={record.device}",
            f"- api_name={record.formulation.api_name}",
            f"- api_concentration_value={record.formulation.api_concentration_value}",
            f"- api_concentration_unit={record.formulation.api_concentration_unit}",
            f"- api_basis={record.formulation.api_basis}",
            f"- api_concentration_raw={record.formulation.api_concentration_raw}",
            f"- endpoint_kind={record.endpoint.kind}",
            f"- endpoint_value={record.endpoint.value}",
            f"- endpoint_unit={record.endpoint.unit}",
            f"- endpoint_time_value={record.endpoint.time_value}",
            f"- endpoint_time_unit={record.endpoint.time_unit}",
            f"- diffusion_area_cm2={record.conditions.diffusion_area_cm2}",
            f"- failure_reasons={record.failure_reasons}",
            "",
            "EVIDENCE_ITEMS",
            *(evidence_lines or ["- none"]),
            "",
            "SOURCE_FRAGMENTS",
            *(source_lines or ["- none"]),
        ]
    )


def adjudicate_records(
    records: Iterable[Record],
    *,
    model: str = "gpt-4o-mini",
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
    long_run_monitor: LongRunMonitor | None = None,
    max_retries: int = 6,
    limit: int | None = None,
) -> list[dict]:
    """Run an audit-only LLM ranking pass over recoverable unresolved records."""

    client = OpenAI(timeout=90)
    candidates = select_adjudication_candidates(records, limit=limit)

    rows: list[dict] = []
    for index, record in enumerate(candidates, start=1):
        if progress_callback:
            progress_callback(index - 1, record.record_id, "requesting adjudication")
        prompt = (
            "Review the following recoverable-unresolved candidate record and evidence packet. "
            "Decide whether it should likely remain unresolved, be rejected as out of scope, or be promoted to strict verified.\n\n"
            f"RECORD_ID: {record.record_id}\n"
            f"PAPER_ID: {record.paper_id}\n"
            f"DOI: {record.doi}\n"
            f"CANDIDATE_REASON: {_candidate_reason(record)}\n\n"
            f"PRIORITY_SCORE: {_priority_score(record)}\n"
            f"REVIEW_FOCUS: {_review_focus(record)}\n\n"
            f"{_build_evidence_packet(record)}"
        )

        attempt = 0
        while True:
            try:
                response = client.responses.parse(
                    model=model,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    text_format=AdjudicationVerdict,
                )
                verdict = response.output_parsed
                row = AdjudicationRow(
                    record_id=record.record_id,
                    paper_id=record.paper_id,
                    doi=record.doi,
                    route=record.route,
                    original_status=record.verification_status,
                    original_scope_bucket=record.scope_bucket,
                    candidate_reason=_candidate_reason(record),
                    priority_score=_priority_score(record),
                    priority_bucket=_priority_bucket(_priority_score(record)),
                    review_focus=_review_focus(record),
                    adjudication=verdict,
                )
                record_openai_usage(
                    long_run_monitor,
                    module_name="verification.llm_adjudicate",
                    model_name=model,
                    response=response,
                    prompt_payload=[SYSTEM_PROMPT, prompt],
                    output_payload=row.model_dump(mode="json"),
                    metadata={"record_id": record.record_id, "doi": record.doi},
                    retries_used=attempt,
                )
                rows.append(row.model_dump(mode="json"))
                if progress_callback:
                    progress_callback(index, record.record_id, f"status={verdict.recommended_status}")
                break
            except Exception as exc:
                attempt += 1
                record_openai_attempt_failure(
                    long_run_monitor,
                    module_name="verification.llm_adjudicate",
                    model_name=model,
                    exc=exc,
                    attempt=attempt,
                    max_retries=max_retries,
                    metadata={"record_id": record.record_id, "doi": record.doi},
                    terminal=attempt >= max_retries,
                )
                if attempt >= max_retries:
                    rows.append(
                        {
                            "record_id": record.record_id,
                            "paper_id": record.paper_id,
                            "doi": record.doi,
                            "route": record.route,
                            "original_status": record.verification_status,
                            "original_scope_bucket": record.scope_bucket,
                            "candidate_reason": _candidate_reason(record),
                            "priority_score": _priority_score(record),
                            "priority_bucket": _priority_bucket(_priority_score(record)),
                            "review_focus": _review_focus(record),
                            "adjudication": {
                                "should_keep_strict": "uncertain",
                                "recommended_status": "unresolved",
                                "scope_bucket": "recoverable_unresolved",
                                "target_api_ok": "uncertain",
                                "concentration_5pct_ww_ok": "uncertain",
                                "franz_ok": "uncertain",
                                "ivpt_ivrt_ok": "uncertain",
                                "amount_endpoint_ok": "uncertain",
                                "endpoint_time_ok": "uncertain",
                                "area_ok": "uncertain",
                                "confidence": 0.0,
                                "rationale": f"error:{type(exc).__name__}",
                            },
                        }
                    )
                    if progress_callback:
                        progress_callback(index, record.record_id, f"failed:{type(exc).__name__}")
                    break
                _backoff(attempt)

    if output_jsonl:
        write_jsonl(rows, output_jsonl)
    write_optional_csv(rows, output_csv)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an optional audit-only LLM adjudication pass over recoverable unresolved SkinMiner records.")
    parser.add_argument("--records-jsonl", type=Path, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    records = load_records_jsonl(args.records_jsonl)
    adjudicate_records(
        records,
        model=args.model,
        output_jsonl=args.output_jsonl,
        output_csv=args.output_csv,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
