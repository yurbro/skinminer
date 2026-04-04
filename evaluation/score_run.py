"""Lightweight scoring utility for comparing pipeline outputs against gold labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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

    summary = {
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
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Score SkinMiner pipeline outputs against gold labels.")
    parser.add_argument("--gold-jsonl", type=Path, required=True)
    parser.add_argument("--predicted-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    gold_entries = [GoldLabelEntry.model_validate(row) for row in load_jsonl(args.gold_jsonl)]
    predicted_records = load_records_jsonl(args.predicted_jsonl)
    summary = score_predictions(gold_entries, predicted_records)

    if args.output_json:
        ensure_parent(args.output_json).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({key: value for key, value in summary.items() if key != "paper_rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
