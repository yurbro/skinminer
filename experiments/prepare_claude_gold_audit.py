from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_DIR = ROOT / "outputs" / "experiment_E3_claude_v2"
GPT_DIR = ROOT / "outputs" / "full_run_16_post_all_fixes"
ROUND2_ANNOTATION = ROOT / "outputs" / "gold_audit_set" / "round2" / "gold_set_round2_annotation.csv"
OUTPUT_DIR = ROOT / "outputs" / "claude_gold_audit"
POLICIES = ["v2", "v3", "v4"]
TIME_TOLERANCE_H = 0.5
VALUE_REL_TOLERANCE = 0.05


@dataclass(frozen=True)
class MatchResult:
    record: dict[str, Any] | None
    reason: str


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_excel_value(value: Any) -> Any:
    if isinstance(value, str):
        return ILLEGAL_CHARACTERS_RE.sub("", value)
    return value


def clean_excel_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.map(clean_excel_value)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def normalize_formulation(value: Any) -> str:
    text = str(value or "").lower()
    text = text.replace("μ", "u").replace("µ", "u")
    text = text.replace("–", "-").replace("—", "-").replace("−", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"[^a-z0-9]+", "", text)


def normalize_doi(value: Any) -> str:
    return str(value or "").strip().lower()


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, str) and not value.strip():
            return None
        result = float(value)
    except Exception:
        return None
    if math.isnan(result):
        return None
    return result


def endpoint_time_h(record: dict[str, Any]) -> float | None:
    endpoint = record.get("endpoint") or {}
    value = as_float(endpoint.get("time_value"))
    unit = str(endpoint.get("time_unit") or "").lower()
    if value is None:
        return None
    if unit.startswith("min"):
        return value / 60.0
    if unit.startswith("day") or unit == "d":
        return value * 24.0
    return value


def endpoint_value(record: dict[str, Any]) -> float | None:
    return as_float((record.get("endpoint") or {}).get("value"))


def formulation_label(record: dict[str, Any]) -> str:
    return str((record.get("formulation") or {}).get("label") or "")


def api_concentration(record: dict[str, Any]) -> str:
    formulation = record.get("formulation") or {}
    parts = [
        formulation.get("api_concentration_value"),
        formulation.get("api_concentration_unit"),
        formulation.get("api_basis"),
        formulation.get("api_concentration_raw"),
    ]
    return " ".join(str(part) for part in parts if part not in [None, ""]).strip()


def source_evidence(record: dict[str, Any], full: bool = False) -> str:
    evidence = record.get("evidence_items") or []
    snippets: list[str] = []
    for item in evidence:
        field = item.get("field_name") or "evidence"
        locator = item.get("locator") or ""
        snippet = str(item.get("snippet") or "").strip()
        if not snippet:
            continue
        snippets.append(f"[{field}; {locator}] {snippet}")
    text = "\n\n".join(snippets)
    if full:
        return text
    text = re.sub(r"\s+", " ", text).strip()
    return text[:200]


def policy_path(run_dir: Path, policy: str) -> Path:
    return run_dir / f"{policy}_rescore" / "verified_records.jsonl"


def load_verified_union(run_dir: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for policy in POLICIES:
        for record in read_jsonl(policy_path(run_dir, policy)):
            if record.get("verification_status") != "verified":
                continue
            record_id = str(record.get("record_id"))
            item = records.setdefault(record_id, record)
            item.setdefault("policy_membership", {p: "no" for p in POLICIES})
            item["policy_membership"][policy] = "yes"
    return records


def make_match_key_fields(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "doi_norm": normalize_doi(record.get("doi")),
        "formulation_norm": normalize_formulation(formulation_label(record)),
        "endpoint_time_h": endpoint_time_h(record),
        "endpoint_value": endpoint_value(record),
    }


def value_matches(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return False
    tolerance = max(abs(b) * VALUE_REL_TOLERANCE, 1e-12)
    return abs(a - b) <= tolerance


def time_matches(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= TIME_TOLERANCE_H


def find_gpt_match(claude_record: dict[str, Any], gpt_records: list[dict[str, Any]]) -> MatchResult:
    c = make_match_key_fields(claude_record)
    candidates = [record for record in gpt_records if normalize_doi(record.get("doi")) == c["doi_norm"]]
    if not candidates:
        return MatchResult(None, "no_gpt_record_same_doi")

    same_form = [
        record for record in candidates if normalize_formulation(formulation_label(record)) == c["formulation_norm"]
    ]
    if not same_form:
        return MatchResult(None, "same_doi_no_formulation_match")

    same_time = [record for record in same_form if time_matches(endpoint_time_h(record), c["endpoint_time_h"])]
    if not same_time:
        return MatchResult(None, "same_doi_formulation_no_time_match")

    same_value = [record for record in same_time if value_matches(endpoint_value(record), c["endpoint_value"])]
    if not same_value:
        return MatchResult(None, "same_doi_formulation_time_no_value_match")

    def score(record: dict[str, Any]) -> tuple[float, float]:
        time_delta = abs((endpoint_time_h(record) or 0.0) - (c["endpoint_time_h"] or 0.0))
        value_delta = abs((endpoint_value(record) or 0.0) - (c["endpoint_value"] or 0.0))
        return time_delta, value_delta

    best = sorted(same_value, key=score)[0]
    return MatchResult(best, "doi_formulation_time_value_match")


def annotation_lookup() -> dict[str, dict[str, Any]]:
    annotations = pd.read_csv(ROUND2_ANNOTATION)
    return {str(row["record_id"]): row.to_dict() for _, row in annotations.iterrows()}


def annotation_packet_row(record: dict[str, Any]) -> dict[str, Any]:
    formulation = record.get("formulation") or {}
    endpoint = record.get("endpoint") or {}
    conditions = record.get("conditions") or {}
    membership = record.get("policy_membership") or {}
    doi = str(record.get("doi") or "")
    return {
        "record_id": record.get("record_id"),
        "doi": doi,
        "paper_link": f"https://doi.org/{doi}" if doi else "",
        "formulation_label": formulation.get("label"),
        "api_name": formulation.get("api_name"),
        "api_concentration": api_concentration(record),
        "endpoint_type": endpoint.get("kind") or endpoint.get("field_name"),
        "endpoint_value": endpoint.get("value"),
        "endpoint_unit": endpoint.get("unit"),
        "endpoint_time_h": endpoint_time_h(record),
        "device": record.get("device"),
        "membrane_type": conditions.get("membrane_type") or record.get("barrier"),
        "receptor_medium": conditions.get("receptor_medium"),
        "dose_type": conditions.get("dose_type"),
        "source_evidence_text": source_evidence(record, full=False),
        "policy_membership": ", ".join(policy for policy in POLICIES if membership.get(policy) == "yes"),
        "gold_keep_record": "",
        "gold_endpoint_value_correct": "",
        "gold_endpoint_value_note": "",
        "gold_notes": "",
    }


def reference_row(record: dict[str, Any]) -> dict[str, Any]:
    provenance = record.get("provenance") or {}
    metadata = provenance.get("metadata") or {}
    return {
        "record_id": record.get("record_id"),
        "doi": record.get("doi"),
        "route": record.get("route"),
        "source_path": provenance.get("source_path"),
        "source_pages": ", ".join(str(item) for item in provenance.get("source_pages") or []),
        "table_or_figure": metadata.get("table_id") or metadata.get("figure_label") or "",
        "full_source_evidence_text": source_evidence(record, full=True),
    }


def write_annotation_packet(records: list[dict[str, Any]]) -> None:
    path = OUTPUT_DIR / "claude_annotation_packet.xlsx"
    instructions = pd.DataFrame(
        [
            {
                "field": "gold_keep_record",
                "allowed_values": "yes / no / uncertain",
                "instruction": "Mark yes only if this Claude verified record should remain in the verification scope after human audit.",
            },
            {
                "field": "gold_endpoint_value_correct",
                "allowed_values": "yes / near / no",
                "instruction": "Judge only the endpoint value. Use near for small rounding/reading differences that do not change the scientific interpretation.",
            },
            {
                "field": "gold_endpoint_value_note",
                "allowed_values": "free text",
                "instruction": "If endpoint value is no, enter the correct value and unit when identifiable from the paper.",
            },
            {
                "field": "gold_notes",
                "allowed_values": "free text",
                "instruction": "Optional notes about scope, paper evidence, ambiguity, or why a record should not be kept.",
            },
        ]
    )
    annotate = clean_excel_frame(pd.DataFrame([annotation_packet_row(record) for record in records]))
    reference = clean_excel_frame(pd.DataFrame([reference_row(record) for record in records]))
    instructions = clean_excel_frame(instructions)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        instructions.to_excel(writer, sheet_name="Instructions", index=False)
        annotate.to_excel(writer, sheet_name="Records to Annotate", index=False)
        reference.to_excel(writer, sheet_name="Reference", index=False)
        for sheet in writer.sheets.values():
            sheet.freeze_panes = "A2"
            for column_cells in sheet.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells[:80])
                sheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 60)


def main() -> None:
    ensure_output_dir()
    claude_by_id = load_verified_union(CLAUDE_DIR)
    gpt_by_id = load_verified_union(GPT_DIR)
    gpt_records = list(gpt_by_id.values())
    annotations = annotation_lookup()

    overlap_rows: list[dict[str, Any]] = []
    needs_annotation: dict[str, dict[str, Any]] = {}
    for record_id, record in sorted(claude_by_id.items()):
        membership = record.get("policy_membership") or {}
        match = find_gpt_match(record, gpt_records)
        matched_id = str(match.record.get("record_id")) if match.record else ""
        annotation = annotations.get(matched_id)
        inherited = ""
        if annotation is not None:
            inherited = str(annotation.get("gold_keep_record") or "").strip()
        needs_new = inherited == ""
        if needs_new:
            needs_annotation[record_id] = record

        row = {
            "claude_record_id": record_id,
            "doi": record.get("doi"),
            "formulation_label": formulation_label(record),
            "endpoint_time_h": endpoint_time_h(record),
            "endpoint_value": endpoint_value(record),
            "policy_v2": membership.get("v2", "no"),
            "policy_v3": membership.get("v3", "no"),
            "policy_v4": membership.get("v4", "no"),
            "matched_gpt_record_id": matched_id,
            "gpt_in_round2_gold": bool(annotation is not None),
            "gold_label_inherited": inherited,
            "gold_endpoint_value_correct_inherited": str(annotation.get("gold_endpoint_value_correct") or "").strip() if annotation else "",
            "needs_new_annotation": bool(needs_new),
            "match_reason": match.reason,
        }
        overlap_rows.append(row)

    overlap = pd.DataFrame(overlap_rows)
    overlap.to_csv(OUTPUT_DIR / "overlap_analysis.csv", index=False, encoding="utf-8-sig")

    summary_rows = []
    for policy in POLICIES:
        policy_col = f"policy_{policy}"
        subset = overlap[overlap[policy_col] == "yes"]
        inherited_count = int((subset["gold_label_inherited"].astype(str).str.len() > 0).sum())
        need_count = int(subset["needs_new_annotation"].sum())
        summary_rows.append(
            {
                "Policy": policy,
                "Claude verified": len(subset),
                "Inheritable from GPT gold": inherited_count,
                "Need new annotation": need_count,
            }
        )

    new_records = [needs_annotation[key] for key in sorted(needs_annotation)]
    write_annotation_packet(new_records)

    total_minutes_low = len(new_records) * 3
    total_minutes_high = len(new_records) * 5
    match_counts = overlap["match_reason"].value_counts().to_dict()
    summary = pd.DataFrame(summary_rows)
    lines = [
        "# Claude Gold Audit: Overlap Summary",
        "",
        "## Policy Buckets",
        "",
        summary.to_markdown(index=False),
        "",
        "## New Annotation Effort",
        "",
        f"- Unique Claude records requiring new annotation: {len(new_records)}",
        f"- Estimated effort at 3-5 minutes per record: {total_minutes_low}-{total_minutes_high} minutes ({total_minutes_low / 60:.1f}-{total_minutes_high / 60:.1f} hours)",
        "",
        "## Match Reason Counts",
        "",
    ]
    for reason, count in match_counts.items():
        lines.append(f"- `{reason}`: {count}")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `outputs/claude_gold_audit/overlap_analysis.csv`",
            "- `outputs/claude_gold_audit/claude_annotation_packet.xlsx`",
            "",
            "Phase 3/4 are intentionally not run until `claude_annotation_packet_FILLED.xlsx` is available.",
        ]
    )
    (OUTPUT_DIR / "overlap_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(summary.to_string(index=False))
    print(f"Unique records requiring annotation: {len(new_records)}")
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
