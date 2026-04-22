"""Scoring utilities for SkinMiner evaluation assets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evaluation.gold_audit import load_gold_audit_csv, score_gold_audit_rows
from evaluation.models import GoldLabelEntry, GoldRecordLabel
from schemas.models import Record
from utils.io import ensure_parent, load_jsonl, load_records_jsonl


def _norm(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _float_match(left: float | None, right: float | None, tolerance: float = 1e-6) -> bool:
    if left is None or right is None:
        return left is None and right is None
    return abs(float(left) - float(right)) <= tolerance


def _text_match(left: str, right: str) -> bool:
    if not left and not right:
        return True
    return _norm(left) == _norm(right)


def _match_record_score(predicted: Record, gold: GoldRecordLabel) -> int:
    score = 0
    if _text_match(predicted.formulation.label, gold.record_label):
        score += 4
    if _text_match(predicted.device, gold.device):
        score += 2
    if _text_match(predicted.study_type, gold.study_type):
        score += 1
    if _text_match(predicted.barrier, gold.barrier):
        score += 1
    if _text_match(predicted.formulation.api_name, gold.api_name):
        score += 1
    if _float_match(predicted.formulation.api_concentration_value, gold.api_concentration_value):
        score += 2
    if _text_match(predicted.formulation.api_concentration_unit, gold.api_concentration_unit):
        score += 1
    if _text_match(predicted.endpoint.kind, gold.endpoint_kind):
        score += 1
    if _float_match(predicted.endpoint.value, gold.endpoint_value):
        score += 2
    if _float_match(predicted.endpoint.time_value, gold.endpoint_time_value):
        score += 2
    return score


def _best_match(predicted_records: list[Record], gold_record: GoldRecordLabel) -> Record | None:
    if not predicted_records:
        return None
    ranked = sorted(predicted_records, key=lambda row: _match_record_score(row, gold_record), reverse=True)
    return ranked[0]


def score_predictions(gold_entries: list[GoldLabelEntry], predicted_records: list[Record]) -> dict[str, object]:
    """Compute lightweight exact-match metrics for a scored run."""

    predicted_by_paper: dict[str, list[Record]] = {}
    for record in predicted_records:
        predicted_by_paper.setdefault(record.paper_id, []).append(record)

    route_matches = 0
    verification_matches = 0
    total_gold_records = 0
    field_match_counts = {
        "device": 0,
        "study_type": 0,
        "api_concentration_value": 0,
        "api_concentration_unit": 0,
        "endpoint_value": 0,
        "endpoint_time_value": 0,
        "endpoint_kind": 0,
        "area_cm2": 0,
    }
    paper_rows: list[dict[str, object]] = []

    for entry in gold_entries:
        predictions = predicted_by_paper.get(entry.paper_id, [])
        route_ok = any(record.route == entry.route_gold for record in predictions)
        if route_ok:
            route_matches += 1
        if entry.verification_gold != "uncertain":
            verification_ok = any(record.verification_status == entry.verification_gold for record in predictions)
            if verification_ok:
                verification_matches += 1
        else:
            verification_ok = None

        for gold_record in entry.records_gold:
            total_gold_records += 1
            best = _best_match(predictions, gold_record)
            if best is None:
                continue
            if _text_match(best.device, gold_record.device):
                field_match_counts["device"] += 1
            if _text_match(best.study_type, gold_record.study_type):
                field_match_counts["study_type"] += 1
            if _float_match(best.formulation.api_concentration_value, gold_record.api_concentration_value):
                field_match_counts["api_concentration_value"] += 1
            if _text_match(best.formulation.api_concentration_unit, gold_record.api_concentration_unit):
                field_match_counts["api_concentration_unit"] += 1
            if _float_match(best.endpoint.value, gold_record.endpoint_value):
                field_match_counts["endpoint_value"] += 1
            if _float_match(best.endpoint.time_value, gold_record.endpoint_time_value):
                field_match_counts["endpoint_time_value"] += 1
            if _text_match(best.endpoint.kind, gold_record.endpoint_kind):
                field_match_counts["endpoint_kind"] += 1
            if _float_match(best.conditions.diffusion_area_cm2, gold_record.area_cm2):
                field_match_counts["area_cm2"] += 1

        paper_rows.append(
            {
                "fixture_id": entry.fixture_id,
                "paper_id": entry.paper_id,
                "route_gold": entry.route_gold,
                "route_matched": route_ok,
                "verification_gold": entry.verification_gold,
                "verification_matched": verification_ok,
                "predicted_records": len(predictions),
            }
        )

    return {
        "mode": "jsonl_fixture",
        "gold_entries": len(gold_entries),
        "route_accuracy": route_matches / len(gold_entries) if gold_entries else 0.0,
        "verification_accuracy": verification_matches / max(
            1, sum(1 for entry in gold_entries if entry.verification_gold != "uncertain")
        ),
        "gold_record_count": total_gold_records,
        "field_match_counts": field_match_counts,
        "field_match_rates": {
            field: count / total_gold_records if total_gold_records else 0.0
            for field, count in field_match_counts.items()
        },
        "paper_rows": paper_rows,
    }


def _write_markdown_summary(summary: dict[str, object], path: Path) -> Path:
    out_path = ensure_parent(path)
    if summary.get("mode") == "gold_audit_csv":
        overall = summary["overall"]
        by_route = summary["by_route"]
        recoverable = summary["recoverable_failure_rates"]
        scope_value = summary["scope_value_metrics"]
        lines = [
            "# Round-1 Gold Audit Scoring Summary",
            "",
            f"- Total labeled rows: `{summary['total_rows']}`",
            f"- Unique papers: `{summary['unique_papers']}`",
            f"- Predicted positives (`verified`): `{overall['predicted_positive']}`",
            f"- Gold positives (`gold_keep_record = yes`): `{overall['gold_positive']}`",
            f"- Precision: `{overall['precision']:.3f}`",
            f"- Recall: `{overall['recall']:.3f}`",
            f"- F1: `{overall['f1']:.3f}`",
            f"- Scope precision: `{scope_value['scope_precision']:.3f}`",
            f"- End-to-end precision: `{scope_value['end_to_end_precision']:.3f}`",
            "",
            "## By Route",
            "",
            "| Route | Count | Precision | Recall | F1 |",
            "|---|---:|---:|---:|---:|",
        ]
        for route in ["table", "text", "mixed", "figure"]:
            row = by_route[route]
            lines.append(
                f"| {route} | {row['count']} | {row['precision']:.3f} | {row['recall']:.3f} | {row['f1']:.3f} |"
            )
        lines.extend(
            [
                "",
                "## Recoverable Failure Rates In Unresolved",
                "",
                "| failure_reason | count | gold_keep=yes | recoverable_rate |",
                "|---|---:|---:|---:|",
            ]
        )
        for reason, row in sorted(
            recoverable.items(),
            key=lambda item: (item[1]["recoverable_rate"], item[1]["count"]),
            reverse=True,
        ):
            lines.append(
                f"| {reason} | {row['count']} | {row['gold_keep_yes']} | {row['recoverable_rate']:.3f} |"
            )
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path

    lines = [
        "# Score Summary",
        "",
        f"- Gold entries: `{summary['gold_entries']}`",
        f"- Route accuracy: `{summary['route_accuracy']:.3f}`",
        f"- Verification accuracy: `{summary['verification_accuracy']:.3f}`",
        f"- Gold record count: `{summary['gold_record_count']}`",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Score SkinMiner outputs against evaluation assets.")
    parser.add_argument("--gold-jsonl", type=Path, default=None)
    parser.add_argument("--predicted-jsonl", type=Path, default=None)
    parser.add_argument("--gold-csv", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    args = parser.parse_args()

    if args.gold_csv:
        rows = load_gold_audit_csv(args.gold_csv)
        summary = {"mode": "gold_audit_csv", **score_gold_audit_rows(rows)}
    else:
        if args.gold_jsonl is None or args.predicted_jsonl is None:
            raise SystemExit("Use --gold-csv for annotated audit CSVs, or --gold-jsonl with --predicted-jsonl.")
        gold_entries = [GoldLabelEntry.model_validate(row) for row in load_jsonl(args.gold_jsonl)]
        predicted_records = load_records_jsonl(args.predicted_jsonl)
        summary = score_predictions(gold_entries, predicted_records)

    if args.output_json:
        ensure_parent(args.output_json).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.output_md:
        _write_markdown_summary(summary, args.output_md)

    payload = json.dumps(
        {key: value for key, value in summary.items() if key not in {"paper_rows"}},
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.buffer.write((payload + "\n").encode("utf-8", errors="backslashreplace"))


if __name__ == "__main__":
    main()
