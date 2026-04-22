"""PDF-based single-pass extraction experiments for the Round 2 gold set.

The script is independent from the modular pipeline. It sends one raw PDF per
paper to a model, asks for the same JSON schema used by SP-1, and reuses the
SP-1 evaluator for DOI + formulation label + endpoint time matching.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import fitz
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from single_pass_extract import (  # noqa: E402
    SYSTEM_PROMPT,
    PaperScope,
    SinglePassExtraction,
    evaluate_results,
    load_content_access,
    load_gold_dois,
)


PDF_USER_PROMPT_TEMPLATE = """Paper DOI: {doi}
Paper title: {title}

The complete PDF of this paper is attached as an image/document input.
Please read the full paper including all tables, figures, and supplementary content visible in the PDF.

Please extract all in vitro permeation/release data records from this paper.
Return JSON matching this schema:
{schema_json}
"""


SOURCE_POOR_DOIS = {
    "10.1007/s11095-024-03747-6",
    "10.1016/j.ijpharm.2019.118975",
}


@dataclass(frozen=True)
class PdfPacket:
    """Prepared raw-PDF input packet for one DOI."""

    doi: str
    title: str
    pdf_path: str
    pdf_status: Literal["ok", "missing", "invalid_js_page", "image_or_no_text", "open_error"]
    paper_status: Literal["ok", "no_pdf_available"]
    file_size_bytes: int
    page_count: int | None
    text_chars: int
    notes: list[str]


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _pdf_diagnostics(pdf_path: Path) -> tuple[str, int | None, int, list[str]]:
    notes: list[str] = []
    try:
        document = fitz.open(str(pdf_path))
    except Exception as exc:
        return "open_error", None, 0, [f"open_error:{type(exc).__name__}"]
    try:
        page_count = document.page_count
        page_texts = [document.load_page(index).get_text("text") or "" for index in range(page_count)]
    finally:
        document.close()
    text_chars = sum(len(text) for text in page_texts)
    sample = _norm_ws(" ".join(page_texts[:3]))[:1000].lower()
    if "requires javascript to function effectively" in sample or "orcid claiming tool has been temporarily disabled" in sample:
        notes.append("pdf_is_europepmc_js_or_placeholder_page")
        return "invalid_js_page", page_count, text_chars, notes
    if text_chars == 0:
        notes.append("pdf_has_no_extractable_text")
        return "image_or_no_text", page_count, text_chars, notes
    return "ok", page_count, text_chars, notes


def _doi_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _pdf_candidates_for_doi(doi: str, content_access_pdf: str) -> list[Path]:
    """Return local PDF candidates, preferring user-supplied/manual PDFs."""

    doi_key = _doi_key(doi)
    candidates: list[Path] = []
    pdf_dir = ROOT / "papers" / "pdf"
    if pdf_dir.exists():
        for path in sorted(pdf_dir.glob("*.pdf")):
            if doi_key and doi_key in _doi_key(path.name):
                candidates.append(path)
    if content_access_pdf:
        path = Path(content_access_pdf)
        if path.exists() and path not in candidates:
            candidates.append(path)
    candidates = list(dict.fromkeys(candidates))
    candidates.sort(
        key=lambda path: (
            0 if "manual" in path.name.lower() else 1,
            -path.stat().st_size if path.exists() else 0,
            path.name.lower(),
        )
    )
    return candidates


def build_pdf_packets(annotation_path: Path, content_access_path: Path) -> list[PdfPacket]:
    dois = load_gold_dois(annotation_path)
    access_by_doi = load_content_access(content_access_path)
    packets: list[PdfPacket] = []
    for doi in dois:
        access = access_by_doi.get(doi, {})
        title = str(access.get("title") or "")
        content_pdf_path = str((access.get("local_paths") or {}).get("pdf") or "")
        notes: list[str] = []
        candidates = _pdf_candidates_for_doi(doi, content_pdf_path)
        if not candidates:
            packets.append(
                PdfPacket(
                    doi=doi,
                    title=title,
                    pdf_path=content_pdf_path,
                    pdf_status="missing",
                    paper_status="no_pdf_available",
                    file_size_bytes=0,
                    page_count=None,
                    text_chars=0,
                    notes=["pdf_missing"],
                )
            )
            continue

        selected_path: Path | None = None
        selected_status = "missing"
        selected_page_count: int | None = None
        selected_text_chars = 0
        selected_notes: list[str] = []
        diagnostics: list[str] = []
        for candidate in candidates:
            pdf_status, page_count, text_chars, diag_notes = _pdf_diagnostics(candidate)
            diagnostics.append(f"{candidate}:{pdf_status}")
            if pdf_status == "ok":
                selected_path = candidate
                selected_status = pdf_status
                selected_page_count = page_count
                selected_text_chars = text_chars
                selected_notes = diag_notes
                break
            if selected_path is None:
                selected_path = candidate
                selected_status = pdf_status
                selected_page_count = page_count
                selected_text_chars = text_chars
                selected_notes = diag_notes
        if selected_path is None:
            selected_path = candidates[0]
        path = selected_path
        pdf_status = selected_status
        page_count = selected_page_count
        text_chars = selected_text_chars
        diag_notes = selected_notes
        notes.extend(diag_notes)
        if len(candidates) > 1:
            notes.append(f"candidate_diagnostics={' | '.join(diagnostics)}")
        paper_status: Literal["ok", "no_pdf_available"] = "ok"
        if pdf_status != "ok":
            paper_status = "no_pdf_available"
        packets.append(
            PdfPacket(
                doi=doi,
                title=title,
                pdf_path=str(path),
                pdf_status=pdf_status,  # type: ignore[arg-type]
                paper_status=paper_status,
                file_size_bytes=path.stat().st_size,
                page_count=page_count,
                text_chars=text_chars,
                notes=list(dict.fromkeys(notes)),
            )
        )
    return packets


def _write_jsonl(path: Path, rows: list[dict[str, Any]], *, append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a" if append else "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _completed_dois(path: Path) -> set[str]:
    completed: set[str] = set()
    for row in _load_jsonl(path):
        doi = str(row.get("doi") or "")
        status = str(row.get("status") or "")
        paper_status = str(row.get("paper_status") or "")
        if not doi:
            continue
        if status == "ok" or paper_status == "no_pdf_available":
            completed.add(doi)
    return completed


def _response_text_from_openai(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text)
    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(str(text))
    return "\n".join(chunks)


def _response_text_from_anthropic(response: Any) -> str:
    chunks: list[str] = []
    for block in getattr(response, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            chunks.append(str(text))
    return "\n".join(chunks)


def _extract_json_object(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


STRING_RECORD_FIELDS = {
    "formulation_label",
    "formulation_name",
    "api_name",
    "api_concentration_unit",
    "api_basis",
    "api_concentration_raw",
    "endpoint_kind",
    "endpoint_unit",
    "endpoint_time_unit",
    "device",
    "study_type",
    "membrane_type",
    "membrane_source",
    "receptor_medium",
    "dose_type",
    "dose_amount",
    "source_evidence",
    "notes",
}

STRING_EXCIPIENT_FIELDS = {"name", "concentration_unit", "basis", "raw"}


def _sanitize_for_schema(obj: dict[str, Any]) -> dict[str, Any]:
    """Coerce common LLM nulls to the SP-1 schema's empty-string convention."""

    records = obj.get("records")
    if not isinstance(records, list):
        obj["records"] = []
        return obj
    for record in records:
        if not isinstance(record, dict):
            continue
        for field in STRING_RECORD_FIELDS:
            if record.get(field) is None:
                record[field] = ""
        excipients = record.get("excipient_composition")
        if excipients is None:
            record["excipient_composition"] = []
            continue
        if not isinstance(excipients, list):
            record["excipient_composition"] = []
            continue
        for excipient in excipients:
            if not isinstance(excipient, dict):
                continue
            for field in STRING_EXCIPIENT_FIELDS:
                if excipient.get(field) is None:
                    excipient[field] = ""
    paper_scope = obj.get("paper_scope")
    if isinstance(paper_scope, dict):
        if paper_scope.get("scope_notes") is None:
            paper_scope["scope_notes"] = ""
    return obj


def _parse_output(text: str) -> SinglePassExtraction:
    obj = _extract_json_object(text)
    obj = _sanitize_for_schema(obj)
    return SinglePassExtraction.model_validate(obj)


def _usage_dict(usage: Any) -> dict[str, int]:
    if usage is None:
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    def value(*names: str) -> int:
        for name in names:
            if isinstance(usage, dict) and usage.get(name) is not None:
                return int(usage[name])
            if hasattr(usage, name) and getattr(usage, name) is not None:
                return int(getattr(usage, name))
        return 0

    input_tokens = value("input_tokens", "prompt_tokens")
    output_tokens = value("output_tokens", "completion_tokens")
    total_tokens = value("total_tokens")
    if total_tokens == 0:
        total_tokens = input_tokens + output_tokens
    return {"input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens}


def _raw_response_summary(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        dumped = response.model_dump(mode="json")
        return {
            "id": dumped.get("id"),
            "model": dumped.get("model"),
            "status": dumped.get("status"),
            "usage": dumped.get("usage"),
            "output": dumped.get("output"),
        }
    if hasattr(response, "to_dict"):
        dumped = response.to_dict()
        return {
            "id": dumped.get("id"),
            "model": dumped.get("model"),
            "usage": dumped.get("usage"),
            "content": dumped.get("content"),
        }
    return {"repr": repr(response)}


def _backoff(attempt: int, exc: Exception | None = None) -> None:
    if exc is not None and type(exc).__name__ == "RateLimitError":
        time.sleep(65.0)
        return
    time.sleep(min(30.0, 1.0 * (2**attempt)))


def _empty_result(packet: PdfPacket, provider: str, model: str, status: str) -> dict[str, Any]:
    parsed = SinglePassExtraction(
        records=[],
        paper_scope=PaperScope(
            has_in_scope_ivpt_or_release=False,
            scope_notes=f"PDF unavailable for PDF single-pass experiment: {packet.pdf_status}.",
        ),
    )
    return {
        "doi": packet.doi,
        "title": packet.title,
        "status": status,
        "paper_status": "no_pdf_available",
        "model_skipped": True,
        "provider": provider,
        "model": model,
        "pdf_path": packet.pdf_path,
        "pdf_status": packet.pdf_status,
        "pdf_notes": packet.notes,
        "pdf_file_size_bytes": packet.file_size_bytes,
        "pdf_page_count": packet.page_count,
        "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "raw_output_text": "",
        "output": parsed.model_dump(mode="json"),
    }


def call_openai_pdf(packet: PdfPacket, *, model: str, max_output_tokens: int) -> tuple[SinglePassExtraction, str, dict[str, int], dict[str, Any]]:
    from openai import OpenAI

    client = OpenAI(timeout=300)
    pdf_base64 = base64.b64encode(Path(packet.pdf_path).read_bytes()).decode("utf-8")
    pdf_data = f"data:application/pdf;base64,{pdf_base64}"
    prompt = PDF_USER_PROMPT_TEMPLATE.format(
        doi=packet.doi,
        title=packet.title,
        schema_json=json.dumps(SinglePassExtraction.model_json_schema(), ensure_ascii=False, indent=2),
    )
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": Path(packet.pdf_path).name,
                        "file_data": pdf_data,
                    },
                    {"type": "input_text", "text": prompt},
                ],
            }
        ],
        max_output_tokens=max_output_tokens,
        store=False,
    )
    text = _response_text_from_openai(response)
    parsed = _parse_output(text)
    return parsed, text, _usage_dict(getattr(response, "usage", None)), _raw_response_summary(response)


def call_anthropic_pdf(packet: PdfPacket, *, model: str, max_output_tokens: int) -> tuple[SinglePassExtraction, str, dict[str, int], dict[str, Any]]:
    from anthropic import Anthropic

    client = Anthropic()
    pdf_data = base64.b64encode(Path(packet.pdf_path).read_bytes()).decode("utf-8")
    prompt = PDF_USER_PROMPT_TEMPLATE.format(
        doi=packet.doi,
        title=packet.title,
        schema_json=json.dumps(SinglePassExtraction.model_json_schema(), ensure_ascii=False, indent=2),
    )
    response = client.messages.create(
        model=model,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        max_tokens=max_output_tokens,
        timeout=300,
    )
    text = _response_text_from_anthropic(response)
    parsed = _parse_output(text)
    return parsed, text, _usage_dict(getattr(response, "usage", None)), _raw_response_summary(response)


def run_pdf_extraction(
    packets: list[PdfPacket],
    output_dir: Path,
    *,
    provider: str,
    model: str,
    max_retries: int,
    max_output_tokens: int,
    resume: bool,
    request_delay_seconds: float,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = [packet.__dict__ for packet in packets]
    _write_jsonl(output_dir / "pdf_manifest.jsonl", manifest_rows)
    pd.DataFrame(manifest_rows).to_csv(output_dir / "pdf_manifest.csv", index=False)

    results_path = output_dir / "single_pass_results.jsonl"
    if not resume and results_path.exists():
        results_path.unlink()
    elif resume and results_path.exists():
        existing_rows = _load_jsonl(results_path)
        retained_rows = [
            row
            for row in existing_rows
            if str(row.get("status") or "") == "ok" or str(row.get("paper_status") or "") == "no_pdf_available"
        ]
        if len(retained_rows) != len(existing_rows):
            _write_jsonl(results_path, retained_rows)
    completed = _completed_dois(results_path) if resume else set()

    for index, packet in enumerate(packets, start=1):
        if packet.doi in completed:
            print(f"[{index}/{len(packets)}] skip completed {packet.doi}", flush=True)
            continue
        if packet.paper_status != "ok":
            row = _empty_result(packet, provider, model, "no_pdf_available")
            _write_jsonl(results_path, [row], append=True)
            print(f"[{index}/{len(packets)}] no_pdf_available {packet.doi}: {packet.pdf_status}", flush=True)
            continue

        attempt = 0
        while True:
            try:
                if request_delay_seconds > 0 and attempt == 0:
                    time.sleep(request_delay_seconds)
                if provider == "openai":
                    parsed, raw_text, usage, raw_response = call_openai_pdf(packet, model=model, max_output_tokens=max_output_tokens)
                elif provider == "anthropic":
                    parsed, raw_text, usage, raw_response = call_anthropic_pdf(packet, model=model, max_output_tokens=max_output_tokens)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
                row = {
                    "doi": packet.doi,
                    "title": packet.title,
                    "status": "ok",
                    "paper_status": "ok",
                    "model_skipped": False,
                    "provider": provider,
                    "model": model,
                    "pdf_path": packet.pdf_path,
                    "pdf_status": packet.pdf_status,
                    "pdf_notes": packet.notes,
                    "pdf_file_size_bytes": packet.file_size_bytes,
                    "pdf_page_count": packet.page_count,
                    "usage": usage,
                    "raw_output_text": raw_text,
                    "raw_response": raw_response,
                    "output": parsed.model_dump(mode="json"),
                }
                _write_jsonl(results_path, [row], append=True)
                print(f"[{index}/{len(packets)}] ok {packet.doi}: {len(parsed.records)} records", flush=True)
                break
            except Exception as exc:
                attempt += 1
                if attempt >= max_retries:
                    parsed = SinglePassExtraction(
                        records=[],
                        paper_scope=PaperScope(scope_notes=f"PDF extraction error: {type(exc).__name__}: {exc}"),
                    )
                    row = {
                        "doi": packet.doi,
                        "title": packet.title,
                        "status": "error",
                        "paper_status": "ok",
                        "model_skipped": False,
                        "provider": provider,
                        "model": model,
                        "pdf_path": packet.pdf_path,
                        "pdf_status": packet.pdf_status,
                        "pdf_notes": packet.notes,
                        "pdf_file_size_bytes": packet.file_size_bytes,
                        "pdf_page_count": packet.page_count,
                        "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "raw_output_text": "",
                        "output": parsed.model_dump(mode="json"),
                    }
                    _write_jsonl(results_path, [row], append=True)
                print(f"[{index}/{len(packets)}] error {packet.doi}: {type(exc).__name__}: {exc}", flush=True)
                break
            print(f"[{index}/{len(packets)}] retry {attempt} {packet.doi}: {type(exc).__name__}: {exc}", flush=True)
            _backoff(attempt, exc)


def _price_for(provider: str, model: str) -> tuple[float | None, float | None]:
    normalized = model.lower()
    if provider == "openai" and normalized == "gpt-4o-mini":
        return 0.15, 0.60
    if provider == "openai" and normalized == "gpt-5.4-mini":
        return 0.75, 4.50
    if provider == "anthropic" and normalized == "claude-sonnet-4-6":
        return 3.00, 15.00
    return None, None


def write_pdf_run_report(output_dir: Path, *, provider: str, model: str) -> None:
    results = _load_jsonl(output_dir / "single_pass_results.jsonl")
    manifest = _load_jsonl(output_dir / "pdf_manifest.jsonl")
    status_counts = Counter(str(row.get("status") or "") for row in results)
    pdf_status_counts = Counter(str(row.get("pdf_status") or "") for row in manifest)
    usage = Counter()
    total_records = 0
    for row in results:
        row_usage = row.get("usage") or {}
        usage["input_tokens"] += int(row_usage.get("input_tokens") or 0)
        usage["output_tokens"] += int(row_usage.get("output_tokens") or 0)
        usage["total_tokens"] += int(row_usage.get("total_tokens") or 0)
        total_records += len((row.get("output") or {}).get("records") or [])
    input_price, output_price = _price_for(provider, model)
    cost = None
    if input_price is not None and output_price is not None:
        cost = (usage["input_tokens"] * input_price + usage["output_tokens"] * output_price) / 1_000_000

    summary_path = output_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    summary.update(
        {
            "provider": provider,
            "model": model,
            "pdf_status_counts": dict(pdf_status_counts),
            "run_status_counts": dict(status_counts),
            "actual_usage": dict(usage),
            "actual_cost_usd": cost,
            "raw_records": total_records,
        }
    )
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    experiment_name = output_dir.name
    report = [
        f"# PDF Single-Pass Run Report: {experiment_name}",
        "",
        "## 1. Setup",
        f"- Provider/model: `{provider}` / `{model}`",
        "- Input mode: raw PDF via Responses API `input_file`.",
        "- Prompt/schema: same extraction instructions and output schema as SP-1, with the user prompt changed to reference the attached PDF.",
        "",
        "## 2. PDF Availability",
        f"- DOI count: `{len(manifest)}`",
        f"- PDF status counts: `{dict(pdf_status_counts)}`",
        f"- Model-callable PDF count: `{pdf_status_counts.get('ok', 0)}`",
    ]
    if pdf_status_counts.get("ok", 0) == len(manifest):
        report.append("- All 29 papers had callable PDFs in this run.")
    else:
        report.append("- Non-callable papers were written as empty records with `paper_status=no_pdf_available`.")
    report.extend(
        [
            "",
            "## 3. Run Summary",
            f"- Run status counts: `{dict(status_counts)}`",
            f"- Raw records emitted: `{total_records}`",
            f"- Actual input tokens: `{usage['input_tokens']:,}`",
            f"- Actual output tokens: `{usage['output_tokens']:,}`",
            f"- Actual total tokens: `{usage['total_tokens']:,}`",
        ]
    )
    if cost is not None:
        report.append(f"- Estimated actual API cost: `${cost:.4f}` using the configured provider/model token rates.")
    else:
        report.append("- Estimated actual API cost: not computed because no price table is encoded for this model/provider.")
    report.extend(
        [
            "",
            "## 4. Gold Evaluation Pointers",
            "- Gold evaluation: `single_pass_vs_gold_evaluation.md`",
            "- Pipeline comparison for this run: `single_pass_vs_pipeline_comparison.md`",
            "- Match audit: `single_pass_gold_matches.csv`",
        ]
    )
    report_text = "\n".join(report) + "\n"
    (output_dir / "pdf_single_pass_run_report.md").write_text(report_text, encoding="utf-8")
    if output_dir.name == "experiment_single_pass_pdf_4omini":
        (output_dir / "sp2_run_report.md").write_text(report_text, encoding="utf-8")


def patch_pdf_evaluation_wording(output_dir: Path, *, provider: str, model: str) -> None:
    """Replace SP-1 text-input wording in reused reports with PDF-specific wording."""

    results = _load_jsonl(output_dir / "single_pass_results.jsonl")
    manifest = _load_jsonl(output_dir / "pdf_manifest.jsonl")
    all_callable = all(str(row.get("paper_status") or "") == "ok" for row in results) if results else False
    pdf_ok = sum(1 for row in manifest if str(row.get("pdf_status") or "") == "ok")
    run_ok = sum(1 for row in results if str(row.get("status") or "") == "ok")
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in results:
        row_usage = row.get("usage") or {}
        usage["input_tokens"] += int(row_usage.get("input_tokens") or 0)
        usage["output_tokens"] += int(row_usage.get("output_tokens") or 0)
        usage["total_tokens"] += int(row_usage.get("total_tokens") or 0)
    input_price, output_price = _price_for(provider, model)
    actual_cost = None
    if input_price is not None and output_price is not None:
        actual_cost = (usage["input_tokens"] * input_price + usage["output_tokens"] * output_price) / 1_000_000

    gold_report = output_dir / "single_pass_vs_gold_evaluation.md"
    if gold_report.exists():
        lines = gold_report.read_text(encoding="utf-8").splitlines()
        patched: list[str] = []
        for line in lines:
            if line.startswith("- Input mode:"):
                patched.append("- Input mode: raw PDF via document/file input; no extracted text/table appendix was supplied.")
            elif line.startswith("- Model:"):
                patched.append(f"- Model: `{model}`")
            elif line.startswith("- Source-poor DOI handling:") or line.startswith("- No-PDF handling:"):
                if all_callable:
                    patched.append("- PDF availability: all 29 papers had callable PDFs in this run.")
                else:
                    patched.append(
                        "- No-PDF handling: papers with missing, placeholder, or non-readable PDFs were set to empty records with `paper_status=no_pdf_available`."
                    )
            else:
                patched.append(line)
        gold_report.write_text("\n".join(patched) + "\n", encoding="utf-8")

    comparison_report = output_dir / "single_pass_vs_pipeline_comparison.md"
    if comparison_report.exists():
        text = comparison_report.read_text(encoding="utf-8")
        text = text.replace(
            "- Single-pass baseline: one end-to-end extraction prompt per source-available DOI, using `gpt-4o-mini`.",
            f"- Single-pass baseline: one end-to-end PDF extraction prompt per model-callable DOI, using `{model}`.",
        )
        text = text.replace(
            "- Figure images were not included in the single-pass input, so figure-only recovery is expected to be limited.",
            "- The model received raw PDF inputs, which include PDF text and page/image context available to the API. No separate extracted text/table appendix was supplied.",
        )
        if pdf_ok and run_ok and run_ok != pdf_ok:
            marker = "- The model received raw PDF inputs, which include PDF text and page/image context available to the API. No separate extracted text/table appendix was supplied."
            addition = (
                f"{marker}\n- Structured-output success: `{run_ok}/{pdf_ok}` callable PDFs returned parseable JSON; the remaining "
                f"`{pdf_ok - run_ok}` papers failed at JSON parsing and are excluded from the single-pass match metrics."
            )
            text = text.replace(marker, addition, 1)
        if usage["total_tokens"] and actual_cost is not None:
            text = re.sub(
                r"\| Single-pass \(Round2 DOI subset\) \| .*? \| .*? \| not benchmarked \|",
                f"| Single-pass (Round2 DOI subset) | {usage['total_tokens']:,} actual billed tokens | ${float(actual_cost):.4f} actual API cost | not benchmarked |",
                text,
                count=1,
            )
        comparison_report.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation", default="outputs/gold_audit_set/round2/gold_set_round2_annotation.csv")
    parser.add_argument("--content-access", default="outputs/full_run_16_post_all_fixes/content_access.jsonl")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--provider", choices=["openai", "anthropic"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--max-output-tokens", type=int, default=16_000)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--request-delay-seconds", type=float, default=0.0)
    parser.add_argument("--evaluate-only", action="store_true")
    parser.add_argument("--manifest-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    annotation_path = Path(args.annotation)
    content_access_path = Path(args.content_access)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    packets = build_pdf_packets(annotation_path, content_access_path)
    if args.manifest_only:
        rows = [packet.__dict__ for packet in packets]
        _write_jsonl(output_dir / "pdf_manifest.jsonl", rows)
        pd.DataFrame(rows).to_csv(output_dir / "pdf_manifest.csv", index=False)
        counts = Counter(packet.pdf_status for packet in packets)
        print(f"wrote PDF manifest to {output_dir}; status_counts={dict(counts)}", flush=True)
        return

    if not args.evaluate_only:
        run_pdf_extraction(
            packets,
            output_dir,
            provider=args.provider,
            model=args.model,
            max_retries=args.max_retries,
            max_output_tokens=args.max_output_tokens,
            resume=args.resume,
            request_delay_seconds=args.request_delay_seconds,
        )
    evaluate_results(annotation_path, output_dir / "single_pass_results.jsonl", output_dir)
    write_pdf_run_report(output_dir, provider=args.provider, model=args.model)
    patch_pdf_evaluation_wording(output_dir, provider=args.provider, model=args.model)
    print(f"wrote PDF single-pass outputs under {output_dir}", flush=True)


if __name__ == "__main__":
    main()
