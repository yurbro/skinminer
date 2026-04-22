"""Single-pass end-to-end extraction baseline for Round 2 gold-set papers.

This experiment is intentionally separate from the modular pipeline. It builds a
source packet from local paper text/source-cache HTML, runs one structured LLM
call per source-available DOI, and evaluates the results against the Round 2
manual annotation.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import fitz
import pandas as pd
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.llm_client import parse_structured  # noqa: E402


SYSTEM_PROMPT = """You are a pharmaceutical data extraction specialist. You read a complete scientific paper about dermal/transdermal drug delivery and extract all permeation/release experimental data records.

For each experiment reported in the paper, extract:
- Formulation: name, API (drug), API concentration, excipient composition
- Endpoint: type (cumulative amount / flux / Jss / permeability coefficient / percent released), value, unit, timepoint
- Conditions: device (Franz cell / IVPT / diffusion cell / other), membrane type and source, membrane thickness, receptor medium, dose type (finite/infinite), dose amount, diffusion area
- Evidence: specific table/figure/text section where the value and conditions come from

Rules:
1. Extract ALL formulations and ALL timepoints reported. Do not skip, summarize, average, or return only representative rows.
2. For a table with formulation rows and multiple timepoint columns, output one record per formulation x timepoint cell.
3. Only extract actual in vitro permeation/release experiments. Exclude formulation characterization, analytical method validation, stability, anti-inflammatory assays, cell assays, animal PK/PD, human dermatopharmacokinetic/tape-stripping, and clinical studies unless they directly report in vitro Franz/IVPT/release measurements.
4. Distinguish in vitro skin/membrane permeation from in vivo DPK or tape stripping. Only in vitro records are in scope.
5. Prefer table values over figure-digitized values when the same endpoint appears in both.
6. Do not infer missing numeric values. Use null for fields that are not explicitly reported.
7. Preserve the reported concentration basis. Do not convert % w/v to % w/w.
8. Include source evidence for every record. If the source context is ambiguous, mark confidence low and explain in notes.
9. Return only valid JSON matching the schema; no prose outside JSON.
"""


USER_PROMPT_TEMPLATE = """Paper DOI: {doi}
Paper title: {title}

Full text extracted from local source:
```text
{full_text_content}
```

Structured tables extracted from source HTML, if available:
```text
{table_text_content}
```

Please extract all in vitro permeation/release data records from this paper.
Return JSON matching the required schema.
"""


SOURCE_POOR_DOIS = {
    "10.1007/s11095-024-03747-6",
    "10.1016/j.ijpharm.2019.118975",
}


class SinglePassExcipient(BaseModel):
    """Excipient/component item emitted by the single-pass extractor."""

    name: str = ""
    concentration_value: float | None = None
    concentration_unit: str = ""
    basis: str = ""
    raw: str = ""


class SinglePassRecord(BaseModel):
    """Flat record schema aligned with the fields needed for gold evaluation."""

    formulation_label: str = ""
    formulation_name: str = ""
    api_name: str = ""
    api_concentration_value: float | None = None
    api_concentration_unit: str = ""
    api_basis: str = ""
    api_concentration_raw: str = ""
    excipient_composition: list[SinglePassExcipient] = Field(default_factory=list)
    endpoint_kind: str = ""
    endpoint_value: float | None = None
    endpoint_unit: str = ""
    endpoint_time: float | None = None
    endpoint_time_unit: str = ""
    device: str = ""
    study_type: str = ""
    membrane_type: str = ""
    membrane_source: str = ""
    membrane_thickness_um: float | None = None
    receptor_medium: str = ""
    dose_type: str = ""
    dose_amount: str = ""
    diffusion_area_cm2: float | None = None
    source_evidence: str = ""
    confidence: float | None = None
    notes: str = ""


class PaperScope(BaseModel):
    """Paper-level scope judgment emitted by the single-pass extractor."""

    has_in_scope_ivpt_or_release: bool = False
    scope_notes: str = ""


class SinglePassExtraction(BaseModel):
    """Structured response wrapper."""

    records: list[SinglePassRecord] = Field(default_factory=list)
    paper_scope: PaperScope = Field(default_factory=PaperScope)


@dataclass(frozen=True)
class SourcePacket:
    """Prepared single-pass input packet for a DOI."""

    doi: str
    title: str
    source_status: Literal["ok", "source_poor"]
    source_kind: str
    source_notes: list[str]
    full_text: str
    table_text: str
    text_chars: int
    table_chars: int
    html_table_count: int
    estimated_input_tokens: int


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _strip_html_tags(text: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text or "")
    cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(
        r"(?i)</(p|div|li|section|article|h1|h2|h3|h4|h5|h6|tr|caption|figcaption|table)>",
        "\n",
        cleaned,
    )
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    return html.unescape(cleaned)


def _is_invalid_source_text(text: str) -> bool:
    lowered = _norm_ws(text[:4000]).lower()
    if not lowered:
        return True
    bad_markers = [
        "requires javascript to function effectively",
        "google.com/recaptcha",
        "recaptchachallengepage",
        "orcid claiming tool has been temporarily disabled",
    ]
    return any(marker in lowered for marker in bad_markers)


def _clean_html_text(raw_html: str) -> str:
    stripped = _strip_html_tags(raw_html)
    blocks = [_norm_ws(part) for part in re.split(r"\n+", stripped)]
    return "\n".join(block for block in blocks if len(block) >= 20)


def _extract_html_tables(raw_html: str, max_rows_per_table: int = 120) -> tuple[str, int, int]:
    if _is_invalid_source_text(_strip_html_tags(raw_html)):
        return "", 0, 0

    blocks: list[str] = []
    table_count = 0
    truncated_count = 0
    for table_index, table_html in enumerate(re.findall(r"(?is)<table\b.*?</table>", raw_html), start=1):
        table_count += 1
        caption_match = re.search(r"(?is)<caption\b.*?>(.*?)</caption>", table_html)
        caption = _norm_ws(_strip_html_tags(caption_match.group(1))) if caption_match else ""
        rows: list[str] = []
        for row_html in re.findall(r"(?is)<tr\b.*?</tr>", table_html):
            cells: list[str] = []
            for cell_html in re.findall(r"(?is)<(?:th|td)\b.*?</(?:th|td)>", row_html):
                value = _norm_ws(_strip_html_tags(cell_html))
                if value:
                    cells.append(value[:400])
            if cells:
                rows.append(" | ".join(cells))
            if len(rows) >= max_rows_per_table:
                truncated_count += 1
                break
        if not caption and not rows:
            continue
        block = [f"TABLE {table_index}"]
        if caption:
            block.append(f"CAPTION: {caption}")
        if rows:
            block.append("ROWS:")
            block.extend(rows)
        if len(rows) >= max_rows_per_table:
            block.append("TABLE_TRUNCATED: true")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks), table_count, truncated_count


def _extract_pdf_text(path: Path) -> tuple[str, int | None]:
    document = fitz.open(str(path))
    try:
        parts: list[str] = []
        for page_index in range(document.page_count):
            page_text = document.load_page(page_index).get_text("text") or ""
            if page_text.strip():
                parts.append(f"--- PAGE {page_index + 1} ---\n{page_text.strip()}")
        return "\n\n".join(parts), document.page_count
    finally:
        document.close()


def _estimate_tokens(text: str | int) -> int:
    if isinstance(text, int):
        return math.ceil(text / 4)
    return math.ceil(len(text or "") / 4)


def _source_cache_by_url(cache_root: Path) -> dict[str, list[Path]]:
    by_url: dict[str, list[Path]] = defaultdict(list)
    if not cache_root.exists():
        return by_url
    for meta_path in cache_root.rglob("*.json"):
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        url = str(metadata.get("url") or "")
        if not url:
            continue
        for candidate in meta_path.parent.glob(f"{meta_path.stem}.*"):
            if candidate.suffix.lower() != ".json" and candidate.is_file() and candidate.stat().st_size > 0:
                by_url[url].append(candidate)
    for url, paths in list(by_url.items()):
        by_url[url] = sorted(paths, key=lambda path: path.stat().st_size, reverse=True)
    return by_url


def _best_html_source(local_paths: dict[str, Any], access_urls: dict[str, Any], cache_by_url: dict[str, list[Path]]) -> tuple[Path | None, str, str]:
    candidates: list[Path] = []
    for key in ("pmc_xml", "html"):
        url = str(access_urls.get(key) or "")
        candidates.extend(cache_by_url.get(url, []))
    local_html = str(local_paths.get("html") or "")
    if local_html and Path(local_html).exists():
        candidates.append(Path(local_html))

    best_path: Path | None = None
    best_raw = ""
    best_clean = ""
    for candidate in candidates:
        try:
            raw_html = candidate.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        clean = _clean_html_text(raw_html)
        if _is_invalid_source_text(clean):
            continue
        if len(clean) > len(best_clean):
            best_path = candidate
            best_raw = raw_html
            best_clean = clean
    return best_path, best_raw, best_clean


def load_content_access(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            obj = json.loads(line)
            doi = str(obj.get("doi") or "")
            if doi and doi.lower() != "nan":
                rows[doi] = obj
    return rows


def load_gold_dois(annotation_path: Path) -> list[str]:
    annotation = pd.read_csv(annotation_path)
    return sorted(annotation["doi"].dropna().astype(str).unique())


def build_source_packets(annotation_path: Path, content_access_path: Path) -> list[SourcePacket]:
    dois = load_gold_dois(annotation_path)
    access_by_doi = load_content_access(content_access_path)
    cache_by_url = _source_cache_by_url(ROOT / "papers" / "source_cache")
    schema_tokens = _estimate_tokens(SYSTEM_PROMPT + USER_PROMPT_TEMPLATE + json.dumps(SinglePassExtraction.model_json_schema()))

    packets: list[SourcePacket] = []
    for doi in dois:
        access = access_by_doi.get(doi, {})
        title = str(access.get("title") or "")
        local_paths = access.get("local_paths") or {}
        access_urls = access.get("access_urls") or {}
        notes: list[str] = []

        html_path, raw_html, html_text = _best_html_source(local_paths, access_urls, cache_by_url)
        source_kind = "none"
        full_text = ""
        table_text = ""
        table_count = 0

        if html_path is not None and len(html_text) >= 5000:
            full_text = html_text
            source_kind = f"html_cache:{html_path.parent.name}" if "source_cache" in str(html_path) else "html_local"
            table_text, table_count, _ = _extract_html_tables(raw_html)
        else:
            if html_path is not None:
                notes.append("html_source_short_or_metadata_only")
                full_text = html_text
                source_kind = f"html_cache:{html_path.parent.name}" if "source_cache" in str(html_path) else "html_local"
                table_text, table_count, _ = _extract_html_tables(raw_html)

            pdf_path_raw = str(local_paths.get("pdf") or "")
            if pdf_path_raw and Path(pdf_path_raw).exists():
                try:
                    pdf_text, _ = _extract_pdf_text(Path(pdf_path_raw))
                except Exception as exc:
                    notes.append(f"local_pdf_extract_failed:{type(exc).__name__}")
                    pdf_text = ""
                if pdf_text and not _is_invalid_source_text(pdf_text) and len(pdf_text) > len(full_text):
                    full_text = pdf_text
                    source_kind = "pdf_text"
                elif pdf_text and _is_invalid_source_text(pdf_text):
                    notes.append("local_pdf_is_js_or_challenge_page")
                elif not pdf_text:
                    notes.append("local_pdf_has_no_extractable_text")

        if len(full_text) < 5000:
            notes.append("source_text_under_5k_chars")
        if not full_text or doi in SOURCE_POOR_DOIS:
            if doi in SOURCE_POOR_DOIS:
                full_text = ""
                table_text = ""
                source_kind = "source_poor"
            notes.append("source_poor_allowed_records_empty")
            source_status: Literal["ok", "source_poor"] = "source_poor"
        else:
            source_status = "ok"

        estimated_tokens = (
            schema_tokens
            + _estimate_tokens(full_text)
            + _estimate_tokens(table_text)
            + _estimate_tokens(len(doi) + len(title) + 200)
        )
        packets.append(
            SourcePacket(
                doi=doi,
                title=title,
                source_status=source_status,
                source_kind=source_kind,
                source_notes=list(dict.fromkeys(notes)),
                full_text=full_text,
                table_text=table_text,
                text_chars=len(full_text),
                table_chars=len(table_text),
                html_table_count=table_count,
                estimated_input_tokens=estimated_tokens,
            )
        )
    return packets


def _write_jsonl(path: Path, rows: list[dict[str, Any]], *, append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as handle:
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


def _completed_dois(results_path: Path) -> set[str]:
    return {str(row.get("doi") or "") for row in _load_jsonl(results_path)}


def _backoff(attempt: int) -> None:
    time.sleep(min(20.0, 0.8 * (2**attempt)))


def run_extraction(
    packets: list[SourcePacket],
    output_dir: Path,
    *,
    provider: str,
    model: str,
    max_retries: int,
    resume: bool,
) -> None:
    results_path = output_dir / "single_pass_results.jsonl"
    if not resume and results_path.exists():
        results_path.unlink()
    completed = _completed_dois(results_path) if resume else set()
    source_rows = [
        {
            "doi": packet.doi,
            "title": packet.title,
            "source_status": packet.source_status,
            "source_kind": packet.source_kind,
            "source_notes": packet.source_notes,
            "text_chars": packet.text_chars,
            "table_chars": packet.table_chars,
            "html_table_count": packet.html_table_count,
            "estimated_input_tokens": packet.estimated_input_tokens,
        }
        for packet in packets
    ]
    _write_jsonl(output_dir / "single_pass_source_packets.jsonl", source_rows)

    for index, packet in enumerate(packets, start=1):
        if packet.doi in completed:
            print(f"[{index}/{len(packets)}] skip completed {packet.doi}", flush=True)
            continue
        if packet.source_status == "source_poor":
            row = {
                "doi": packet.doi,
                "title": packet.title,
                "status": "source_poor_empty",
                "model_skipped": True,
                "provider": provider,
                "model": model,
                "source_kind": packet.source_kind,
                "source_notes": packet.source_notes,
                "text_chars": packet.text_chars,
                "table_chars": packet.table_chars,
                "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
                "output": SinglePassExtraction(
                    records=[],
                    paper_scope=PaperScope(
                        has_in_scope_ivpt_or_release=False,
                        scope_notes="Source-poor paper; no full text was available, so extraction was skipped and records are empty.",
                    ),
                ).model_dump(mode="json"),
            }
            _write_jsonl(results_path, [row], append=True)
            print(f"[{index}/{len(packets)}] source-poor empty {packet.doi}", flush=True)
            continue

        prompt = USER_PROMPT_TEMPLATE.format(
            doi=packet.doi,
            title=packet.title,
            full_text_content=packet.full_text,
            table_text_content=packet.table_text,
        )
        attempt = 0
        while True:
            try:
                response = parse_structured(
                    provider=provider,
                    model=model,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    text_format=SinglePassExtraction,
                    timeout=240,
                    max_output_tokens=16_000,
                )
                parsed = response.output_parsed
                usage = response.usage
                row = {
                    "doi": packet.doi,
                    "title": packet.title,
                    "status": "ok",
                    "model_skipped": False,
                    "provider": response.provider,
                    "model": response.model,
                    "source_kind": packet.source_kind,
                    "source_notes": packet.source_notes,
                    "text_chars": packet.text_chars,
                    "table_chars": packet.table_chars,
                    "usage": usage.__dict__ if usage is not None else {},
                    "output": parsed.model_dump(mode="json"),
                }
                _write_jsonl(results_path, [row], append=True)
                print(f"[{index}/{len(packets)}] ok {packet.doi}: {len(parsed.records)} records", flush=True)
                break
            except Exception as exc:
                attempt += 1
                if attempt >= max_retries:
                    row = {
                        "doi": packet.doi,
                        "title": packet.title,
                        "status": "error",
                        "model_skipped": False,
                        "provider": provider,
                        "model": model,
                        "source_kind": packet.source_kind,
                        "source_notes": packet.source_notes,
                        "text_chars": packet.text_chars,
                        "table_chars": packet.table_chars,
                        "usage": {},
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "output": SinglePassExtraction(records=[], paper_scope=PaperScope(scope_notes=f"Extraction error: {exc}")).model_dump(mode="json"),
                    }
                    _write_jsonl(results_path, [row], append=True)
                    print(f"[{index}/{len(packets)}] error {packet.doi}: {type(exc).__name__}: {exc}", flush=True)
                    break
                print(f"[{index}/{len(packets)}] retry {attempt} {packet.doi}: {type(exc).__name__}: {exc}", flush=True)
                _backoff(attempt)


def _normalize_label(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("formulation", "f")
    match = re.search(r"\bf\s*[-_ ]?(\d+)\b", text)
    if match:
        return f"f{int(match.group(1))}"
    text = re.sub(r"[^a-z0-9#]+", "", text)
    return text


def _time_to_hours(value: Any, unit: Any) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        numeric = float(value)
    except Exception:
        return None
    unit_text = str(unit or "").strip().lower()
    if unit_text in {"", "h", "hr", "hrs", "hour", "hours"}:
        return numeric
    if unit_text in {"min", "mins", "minute", "minutes"}:
        return numeric / 60.0
    if unit_text in {"d", "day", "days"}:
        return numeric * 24.0
    return numeric


def _canon_unit(unit: Any) -> str:
    text = str(unit or "").strip().lower()
    text = text.replace("µ", "u").replace("μ", "u")
    text = text.replace("^2", "2").replace("²", "2")
    text = re.sub(r"\s+", "", text)
    text = text.replace("microgram", "ug").replace("mcg", "ug")
    text = text.replace("ug/cm^2", "ug/cm2").replace("ugcm-2", "ug/cm2")
    text = text.replace("mg/cm^2", "mg/cm2").replace("mgcm-2", "mg/cm2")
    return text


def _convert_value(value: Any, source_unit: Any, target_unit: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except Exception:
        return None
    source = _canon_unit(source_unit)
    target = _canon_unit(target_unit)
    if source == target or not source or not target:
        return numeric
    conversions = {
        ("mg", "ug"): 1000.0,
        ("ng", "ug"): 0.001,
        ("ug", "mg"): 0.001,
        ("ug", "ng"): 1000.0,
        ("mg/cm2", "ug/cm2"): 1000.0,
        ("ng/cm2", "ug/cm2"): 0.001,
        ("ug/cm2", "mg/cm2"): 0.001,
        ("ug/cm2", "ng/cm2"): 1000.0,
    }
    factor = conversions.get((source, target))
    if factor is None:
        return None
    return numeric * factor


def _value_close(observed: Any, observed_unit: Any, expected: Any, expected_unit: Any) -> bool:
    converted = _convert_value(observed, observed_unit, expected_unit)
    if converted is None:
        return False
    try:
        expected_float = float(expected)
    except Exception:
        return False
    tolerance = max(0.05 * abs(expected_float), 0.5)
    return abs(converted - expected_float) <= tolerance


def flatten_single_pass_records(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    for paper in results:
        output = paper.get("output") or {}
        for record_index, record in enumerate(output.get("records") or [], start=1):
            row = {
                "single_pass_record_id": f"{paper.get('doi')}::sp{record_index:04d}",
                "doi": paper.get("doi"),
                "paper_title": paper.get("title"),
                "paper_status": paper.get("status"),
                "source_kind": paper.get("source_kind"),
                **record,
            }
            row["label_norm"] = _normalize_label(record.get("formulation_label") or record.get("formulation_name"))
            row["time_h"] = _time_to_hours(record.get("endpoint_time"), record.get("endpoint_time_unit"))
            flat.append(row)
    return flat


def _find_matching_record(gold_row: pd.Series, single_records: list[dict[str, Any]], used_ids: set[str] | None = None) -> dict[str, Any] | None:
    doi = str(gold_row.get("doi") or "")
    label = _normalize_label(gold_row.get("formulation_label"))
    time_h = _time_to_hours(gold_row.get("endpoint_time"), gold_row.get("endpoint_time_unit"))
    candidates: list[dict[str, Any]] = []
    for record in single_records:
        if used_ids and record["single_pass_record_id"] in used_ids:
            continue
        if str(record.get("doi") or "") != doi:
            continue
        if label and record.get("label_norm") != label:
            continue
        rec_time = record.get("time_h")
        if time_h is not None and rec_time is not None and abs(float(rec_time) - float(time_h)) <= 0.25:
            candidates.append(record)
    if not candidates:
        return None
    expected_value = gold_row.get("endpoint_value")
    expected_unit = gold_row.get("endpoint_unit")
    candidates.sort(
        key=lambda record: (
            0
            if _value_close(record.get("endpoint_value"), record.get("endpoint_unit"), expected_value, expected_unit)
            else 1,
            abs((record.get("time_h") or 0) - (time_h or 0)),
        )
    )
    return candidates[0]


def _record_matches_gold_row(record: dict[str, Any], gold_row: pd.Series) -> bool:
    if str(record.get("doi") or "") != str(gold_row.get("doi") or ""):
        return False
    if record.get("label_norm") != _normalize_label(gold_row.get("formulation_label")):
        return False
    gold_time = _time_to_hours(gold_row.get("endpoint_time"), gold_row.get("endpoint_time_unit"))
    rec_time = record.get("time_h")
    return gold_time is not None and rec_time is not None and abs(float(rec_time) - float(gold_time)) <= 0.25


def _yn(value: Any) -> str:
    return str(value or "").strip().lower()


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    if isinstance(value, list):
        return len(value) > 0
    return bool(str(value).strip())


def _format_pct(num: int, den: int) -> str:
    return "n/a" if den == 0 else f"{100.0 * num / den:.1f}%"


def evaluate_results(annotation_path: Path, results_path: Path, output_dir: Path) -> None:
    annotation = pd.read_csv(annotation_path)
    results = _load_jsonl(results_path)
    flat_records = flatten_single_pass_records(results)
    pd.DataFrame(flat_records).to_csv(output_dir / "single_pass_records_flat.csv", index=False)

    sampling_tier = annotation["sampling_tier"].astype(str)
    gpt_verified = annotation[
        sampling_tier.str.startswith("tier1_gpt_v4_verified")
        & (annotation["source_baseline"].astype(str).str.lower() == "gpt")
    ].copy()
    gold_tp = annotation[annotation["gold_keep_record"].map(_yn) == "yes"].copy()
    value_anchored_tp = gold_tp[gold_tp["gold_value_correct"].map(_yn) == "yes"].copy()

    used_sp_ids: set[str] = set()
    match_rows: list[dict[str, Any]] = []
    for _, gold_row in gold_tp.iterrows():
        matched = _find_matching_record(gold_row, flat_records, used_sp_ids)
        if matched is not None:
            used_sp_ids.add(matched["single_pass_record_id"])
        value_evaluable = _yn(gold_row.get("gold_value_correct")) == "yes"
        value_correct = (
            matched is not None
            and value_evaluable
            and _value_close(
                matched.get("endpoint_value"),
                matched.get("endpoint_unit"),
                gold_row.get("endpoint_value"),
                gold_row.get("endpoint_unit"),
            )
        )
        match_rows.append(
            {
                "sample_id": gold_row.get("sample_id"),
                "doi": gold_row.get("doi"),
                "formulation_label": gold_row.get("formulation_label"),
                "endpoint_time": gold_row.get("endpoint_time"),
                "gold_endpoint_value": gold_row.get("endpoint_value"),
                "gold_endpoint_unit": gold_row.get("endpoint_unit"),
                "gold_value_anchor": value_evaluable,
                "single_pass_matched": matched is not None,
                "single_pass_record_id": matched.get("single_pass_record_id") if matched else "",
                "single_pass_endpoint_value": matched.get("endpoint_value") if matched else "",
                "single_pass_endpoint_unit": matched.get("endpoint_unit") if matched else "",
                "single_pass_source_evidence": matched.get("source_evidence") if matched else "",
                "single_pass_value_correct": value_correct,
            }
        )
    matches_df = pd.DataFrame(match_rows)
    matches_df.to_csv(output_dir / "single_pass_gold_matches.csv", index=False)

    fp_gold = annotation[annotation["gold_keep_record"].map(_yn) == "no"].copy()
    fp_match_rows: list[dict[str, Any]] = []
    for _, gold_row in fp_gold.iterrows():
        matched = _find_matching_record(gold_row, flat_records)
        if matched is not None:
            fp_match_rows.append(
                {
                    "sample_id": gold_row.get("sample_id"),
                    "doi": gold_row.get("doi"),
                    "formulation_label": gold_row.get("formulation_label"),
                    "endpoint_time": gold_row.get("endpoint_time"),
                    "single_pass_record_id": matched.get("single_pass_record_id"),
                    "single_pass_endpoint_value": matched.get("endpoint_value"),
                    "single_pass_endpoint_unit": matched.get("endpoint_unit"),
                    "gold_notes": gold_row.get("gold_notes"),
                }
            )
    fp_matches_df = pd.DataFrame(fp_match_rows)
    fp_matches_df.to_csv(output_dir / "single_pass_annotated_fp_matches.csv", index=False)

    matched_any_ids = set()
    for record in flat_records:
        for _, gold_row in annotation.iterrows():
            if _record_matches_gold_row(record, gold_row):
                matched_any_ids.add(record["single_pass_record_id"])
                break
    extra_records = [record for record in flat_records if record["single_pass_record_id"] not in matched_any_ids]
    pd.DataFrame(extra_records).to_csv(output_dir / "single_pass_extra_records.csv", index=False)

    usage = Counter()
    status_counts = Counter()
    for row in results:
        status_counts[str(row.get("status") or "")] += 1
        row_usage = row.get("usage") or {}
        usage["input_tokens"] += int(row_usage.get("input_tokens") or 0)
        usage["output_tokens"] += int(row_usage.get("output_tokens") or 0)
        usage["total_tokens"] += int(row_usage.get("total_tokens") or 0)

    covered = int(matches_df["single_pass_matched"].sum()) if not matches_df.empty else 0
    value_correct = int(matches_df["single_pass_value_correct"].sum()) if not matches_df.empty else 0
    value_covered = int(matches_df[matches_df["gold_value_anchor"]]["single_pass_matched"].sum()) if not matches_df.empty else 0
    value_anchor_total = len(value_anchored_tp)

    matched_tp_records = [
        record
        for record in flat_records
        if record["single_pass_record_id"] in set(matches_df.loc[matches_df["single_pass_matched"], "single_pass_record_id"])
    ]
    field_counts = {
        "membrane": sum(_nonempty(r.get("membrane_type")) or _nonempty(r.get("membrane_source")) for r in matched_tp_records),
        "receptor_medium": sum(_nonempty(r.get("receptor_medium")) for r in matched_tp_records),
        "dose_type": sum(_nonempty(r.get("dose_type")) or _nonempty(r.get("dose_amount")) for r in matched_tp_records),
        "excipient": sum(_nonempty(r.get("excipient_composition")) for r in matched_tp_records),
    }

    paper_record_counts = Counter(str(record.get("doi") or "") for record in flat_records)
    gold_negative_dois = sorted(
        doi
        for doi, group in annotation.groupby("doi")
        if not any(group["gold_keep_record"].map(_yn) == "yes")
    )
    gold_negative_with_output = [doi for doi in gold_negative_dois if paper_record_counts.get(doi, 0) > 0]

    pipeline_total = len(gpt_verified)
    pipeline_tp = int((gpt_verified["gold_keep_record"].map(_yn) == "yes").sum())
    pipeline_fp = int((gpt_verified["gold_keep_record"].map(_yn) == "no").sum())
    pipeline_e2e = int(
        (
            (gpt_verified["gold_scope_correct"].map(_yn) == "yes")
            & (gpt_verified["gold_value_correct"].map(_yn) == "yes")
        ).sum()
    )

    source_status_summary = Counter(str(row.get("status") or "") for row in results)
    total_records = len(flat_records)
    matched_fp = len(fp_matches_df)
    matched_any = len(matched_any_ids)

    gold_report = [
        "# Single-Pass vs Gold Set Evaluation",
        "",
        "## 1. Setup",
        f"- Annotation file: `{annotation_path}`",
        f"- Results file: `{results_path}`",
        "- Model: `gpt-4o-mini`",
        "- Input mode: paper text plus raw source HTML table blocks when available; no figure images.",
        "- Source-poor DOI handling: records were set to empty for `10.1007/s11095-024-03747-6` and `10.1016/j.ijpharm.2019.118975`.",
        "",
        "## 2. Run Summary",
        f"- Papers in scope: `{len(results)}`",
        f"- Paper status counts: `{dict(source_status_summary)}`",
        f"- Single-pass records emitted: `{total_records}`",
        f"- Actual usage from completed LLM calls: input `{usage['input_tokens']:,}`, output `{usage['output_tokens']:,}`, total `{usage['total_tokens']:,}` tokens.",
        "",
        "## 3. Gold True Positive Coverage",
        f"- Gold keep-record rows: `{len(gold_tp)}`",
        f"- Covered by single-pass match on DOI + formulation label + endpoint time: `{covered}/{len(gold_tp)} = {_format_pct(covered, len(gold_tp))}`",
        f"- Value-anchored gold TP rows: `{value_anchor_total}`. One keep-record has `gold_value_correct=no`, so it is excluded from value-accuracy denominator.",
        f"- Covered value-anchored rows: `{value_covered}/{value_anchor_total} = {_format_pct(value_covered, value_anchor_total)}`",
        f"- Value-correct among all value-anchored gold rows: `{value_correct}/{value_anchor_total} = {_format_pct(value_correct, value_anchor_total)}`",
        f"- Value-correct among covered value-anchored rows: `{value_correct}/{value_covered} = {_format_pct(value_correct, value_covered)}`",
        "",
        "## 4. Annotated False Positive Interaction",
        f"- Annotated `gold_keep_record=no` rows matched by single-pass: `{matched_fp}/{len(fp_gold)}`",
        f"- Single-pass extra records not matched to any Round2 annotation row: `{len(extra_records)}`",
        "- Extra records are not automatically counted as false positives because the Round2 annotation set is a sample, not an exhaustive paper-level gold database.",
        "",
        "## 5. Scope Signal",
        f"- Gold-negative DOI count in Round2 annotation: `{len(gold_negative_dois)}`",
        f"- Gold-negative DOI with at least one single-pass record: `{len(gold_negative_with_output)}`",
        f"- Gold-negative DOI emitting records: `{gold_negative_with_output}`",
        "",
        "## 6. Field Completeness On Matched Gold TP",
        f"- Matched gold TP records: `{len(matched_tp_records)}`",
        f"- Membrane field non-empty: `{field_counts['membrane']}/{len(matched_tp_records)} = {_format_pct(field_counts['membrane'], len(matched_tp_records))}`",
        f"- Receptor medium non-empty: `{field_counts['receptor_medium']}/{len(matched_tp_records)} = {_format_pct(field_counts['receptor_medium'], len(matched_tp_records))}`",
        f"- Dose field non-empty: `{field_counts['dose_type']}/{len(matched_tp_records)} = {_format_pct(field_counts['dose_type'], len(matched_tp_records))}`",
        f"- Excipient composition non-empty: `{field_counts['excipient']}/{len(matched_tp_records)} = {_format_pct(field_counts['excipient'], len(matched_tp_records))}`",
        "",
        "## 7. Evaluation Caveats",
        "- Endpoint value accuracy is computed only for gold keep-record rows whose pipeline value was manually marked correct. The Round2 CSV does not contain an independent normalized gold numeric field for every row.",
        "- The matching key follows the task specification: DOI + formulation label + endpoint time. Source evidence and units are retained in `single_pass_gold_matches.csv` for manual audit.",
    ]
    (output_dir / "single_pass_vs_gold_evaluation.md").write_text("\n".join(gold_report) + "\n", encoding="utf-8")

    comparison_report = [
        "# Single-Pass vs Modular Pipeline Comparison",
        "",
        "## 1. Experiment Setup",
        "- Modular baseline: Round2 GPT v4 verified annotation from the post-fix modular pipeline.",
        "- Single-pass baseline: one end-to-end extraction prompt per source-available DOI, using `gpt-4o-mini`.",
        "- Same Round2 DOI subset: `29` unique papers.",
        "- Figure images were not included in the single-pass input, so figure-only recovery is expected to be limited.",
        "",
        "## 2. Coverage Comparison",
        "| Method | Gold TP denominator | Covered TP | Coverage |",
        "| --- | ---: | ---: | ---: |",
        f"| Modular pipeline | {len(gold_tp)} | {len(gold_tp)} | 100.0% |",
        f"| Single-pass | {len(gold_tp)} | {covered} | {_format_pct(covered, len(gold_tp))} |",
        "",
        "## 3. Value Accuracy Comparison",
        "| Method | Records compared | Value correct | Value incorrect/missing | Accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| Modular pipeline | {len(gold_tp)} | {int((gold_tp['gold_value_correct'].map(_yn) == 'yes').sum())} | {len(gold_tp) - int((gold_tp['gold_value_correct'].map(_yn) == 'yes').sum())} | {_format_pct(int((gold_tp['gold_value_correct'].map(_yn) == 'yes').sum()), len(gold_tp))} |",
        f"| Single-pass | {value_anchor_total} value-anchored gold TP | {value_correct} | {value_anchor_total - value_correct} | {_format_pct(value_correct, value_anchor_total)} |",
        "",
        "## 4. Scope Accuracy",
        f"- Modular pipeline GPT v4 verified precision on Tier1 annotation: `{pipeline_tp}/{pipeline_total} = {_format_pct(pipeline_tp, pipeline_total)}`.",
        f"- Modular pipeline end-to-end precision on Tier1 annotation: `{pipeline_e2e}/{pipeline_total} = {_format_pct(pipeline_e2e, pipeline_total)}`.",
        f"- Single-pass emitted `{total_records}` raw records. It matched `{matched_fp}` annotated false-positive rows and emitted records for `{len(gold_negative_with_output)}` gold-negative DOI.",
        "- Single-pass has no verification gate, so raw output precision cannot be estimated exactly from the sampled gold set; unmatched extra records require manual review.",
        "",
        "## 5. False Positive Analysis",
        f"- Annotated FP matches: `{matched_fp}` rows. Details are in `single_pass_annotated_fp_matches.csv`.",
        f"- Extra unmatched single-pass records: `{len(extra_records)}` rows. Details are in `single_pass_extra_records.csv`.",
        "",
        "## 6. Field Completeness",
        "| Field | Modular pipeline TP quality from Round2 | Single-pass matched TP fill rate |",
        "| --- | --- | ---: |",
        f"| membrane | 25/25 correct | {field_counts['membrane']}/{len(matched_tp_records)} = {_format_pct(field_counts['membrane'], len(matched_tp_records))} |",
        f"| receptor medium | 24/25 correct | {field_counts['receptor_medium']}/{len(matched_tp_records)} = {_format_pct(field_counts['receptor_medium'], len(matched_tp_records))} |",
        f"| dose | 24/25 correct | {field_counts['dose_type']}/{len(matched_tp_records)} = {_format_pct(field_counts['dose_type'], len(matched_tp_records))} |",
        f"| excipient | 24/25 partial, 1 uncertain | {field_counts['excipient']}/{len(matched_tp_records)} = {_format_pct(field_counts['excipient'], len(matched_tp_records))} |",
        "",
        "## 7. Cost Comparison",
        "| Method | Total Tokens | Estimated / Actual Cost | Time |",
        "| --- | ---: | ---: | ---: |",
        "| Modular Pipeline (full run reference) | ~3.8M | ~$0.71 | ~5000s |",
        f"| Single-pass (Round2 DOI subset) | {usage['total_tokens']:,} actual billed tokens | ${(usage['input_tokens'] * 0.15 + usage['output_tokens'] * 0.60) / 1_000_000:.4f} estimated from actual usage | not benchmarked |",
        "",
        "## 8. Traceability Comparison",
        "- Modular pipeline has field-level evidence items, route provenance, verification status, and failure reasons.",
        "- Single-pass has one free-text `source_evidence` field per record. This is useful but weaker for automated source binding and gate-level diagnosis.",
        "",
        "## 9. Key Findings",
        f"1. Single-pass covered `{covered}/{len(gold_tp)}` Round2 gold keep-records under the DOI+label+time matching rule.",
        f"2. Single-pass value accuracy on value-anchored gold TP rows was `{value_correct}/{value_anchor_total} = {_format_pct(value_correct, value_anchor_total)}`.",
        f"3. Single-pass produced `{matched_fp}` matches to annotated false-positive rows and `{len(extra_records)}` unmatched extras, so it still needs a verification/gating layer for precision.",
        "4. The modular pipeline remains stronger for traceability because every accepted field carries structured evidence and verifier status.",
    ]
    (output_dir / "single_pass_vs_pipeline_comparison.md").write_text("\n".join(comparison_report) + "\n", encoding="utf-8")

    summary = {
        "papers": len(results),
        "status_counts": dict(status_counts),
        "single_pass_records": total_records,
        "gold_tp": len(gold_tp),
        "covered_gold_tp": covered,
        "value_anchor_total": value_anchor_total,
        "value_correct": value_correct,
        "annotated_fp_matches": matched_fp,
        "extra_records": len(extra_records),
        "usage": dict(usage),
        "estimated_actual_cost_usd": (usage["input_tokens"] * 0.15 + usage["output_tokens"] * 0.60) / 1_000_000,
        "gold_negative_dois_with_output": gold_negative_with_output,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation", default="outputs/gold_audit_set/round2/gold_set_round2_annotation.csv")
    parser.add_argument("--content-access", default="outputs/full_run_16_post_all_fixes/content_access.jsonl")
    parser.add_argument("--output-dir", default="outputs/experiment_single_pass")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--evaluate-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    annotation_path = Path(args.annotation)
    content_access_path = Path(args.content_access)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "single_pass_results.jsonl"

    if not args.evaluate_only:
        packets = build_source_packets(annotation_path, content_access_path)
        run_extraction(
            packets,
            output_dir,
            provider=args.provider,
            model=args.model,
            max_retries=args.max_retries,
            resume=args.resume,
        )
    evaluate_results(annotation_path, results_path, output_dir)
    print(f"wrote reports under {output_dir}", flush=True)


if __name__ == "__main__":
    main()
