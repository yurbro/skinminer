"""Helpers for annotated gold-audit CSV files."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Iterable

from evaluation.models import GoldAuditCsvRow

MAIN_SCOPE_GATES = [
    "gold_target_api_ok",
    "gold_5pct_ww_ok",
    "gold_franz_ok",
    "gold_ivpt_ivrt_ok",
    "gold_amount_endpoint_ok",
    "gold_endpoint_time_ok",
]

ALL_GOLD_DIMENSIONS = [
    "gold_target_api_ok",
    "gold_5pct_ww_ok",
    "gold_franz_ok",
    "gold_ivpt_ivrt_ok",
    "gold_amount_endpoint_ok",
    "gold_endpoint_time_ok",
    "gold_endpoint_value_correct",
    "gold_area_ok",
]


def load_gold_audit_csv(path: str | Path) -> list[GoldAuditCsvRow]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [GoldAuditCsvRow.model_validate(row) for row in reader]


def compute_annotation_quality_issues(rows: Iterable[GoldAuditCsvRow]) -> dict[str, list[dict[str, object]]]:
    keep_yes_with_no: list[dict[str, object]] = []
    keep_no_all_main_yes: list[dict[str, object]] = []
    incomplete_rows: list[dict[str, object]] = []

    for row in rows:
        values = {field: getattr(row, field) for field in MAIN_SCOPE_GATES}
        blanks = [field for field, value in values.items() if not value]
        if blanks or not row.gold_keep_record:
            incomplete_rows.append(
                {
                    "record_id": row.record_id,
                    "doi": row.doi,
                    "missing_fields": blanks + (["gold_keep_record"] if not row.gold_keep_record else []),
                }
            )
        if row.gold_keep_record == "yes" and any(value == "no" for value in values.values()):
            keep_yes_with_no.append(
                {
                    "record_id": row.record_id,
                    "doi": row.doi,
                    "route": row.route,
                    "verification_status": row.verification_status,
                    "failing_fields": [field for field, value in values.items() if value == "no"],
                }
            )
        if row.gold_keep_record == "no" and all(value == "yes" for value in values.values()):
            keep_no_all_main_yes.append(
                {
                    "record_id": row.record_id,
                    "doi": row.doi,
                    "route": row.route,
                    "verification_status": row.verification_status,
                    "endpoint_value_correct": row.gold_endpoint_value_correct,
                    "area_ok": row.gold_area_ok,
                    "gold_notes": row.gold_notes,
                }
            )

    return {
        "keep_yes_with_no": keep_yes_with_no,
        "keep_no_all_main_yes": keep_no_all_main_yes,
        "incomplete_rows": incomplete_rows,
    }


def _metric_dict(tp: int, fp: int, fn: int, tn: int) -> dict[str, float | int]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "predicted_positive": tp + fp,
        "gold_positive": tp + fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def score_gold_audit_rows(rows: Iterable[GoldAuditCsvRow]) -> dict[str, object]:
    rows = list(rows)

    def scope_correct(row: GoldAuditCsvRow) -> bool:
        return row.gold_scope_correct == "yes"

    def value_correct_or_approx(row: GoldAuditCsvRow) -> bool:
        return row.gold_value_correct in {"yes", "approximate"}

    def predicted_positive(row: GoldAuditCsvRow) -> bool:
        return row.verification_status == "verified"

    def gold_positive(row: GoldAuditCsvRow) -> bool:
        return row.gold_keep_record == "yes"

    tp = sum(1 for row in rows if predicted_positive(row) and gold_positive(row))
    fp = sum(1 for row in rows if predicted_positive(row) and not gold_positive(row))
    fn = sum(1 for row in rows if not predicted_positive(row) and gold_positive(row))
    tn = sum(1 for row in rows if not predicted_positive(row) and not gold_positive(row))

    by_route: dict[str, dict[str, object]] = {}
    for route in ["table", "text", "mixed", "figure"]:
        subset = [row for row in rows if row.route == route]
        route_tp = sum(1 for row in subset if predicted_positive(row) and gold_positive(row))
        route_fp = sum(1 for row in subset if predicted_positive(row) and not gold_positive(row))
        route_fn = sum(1 for row in subset if not predicted_positive(row) and gold_positive(row))
        route_tn = sum(1 for row in subset if not predicted_positive(row) and not gold_positive(row))
        by_route[route] = {"count": len(subset), **_metric_dict(route_tp, route_fp, route_fn, route_tn)}

    by_status: dict[str, dict[str, int | float]] = {}
    for status in ["verified", "unresolved", "rejected"]:
        subset = [row for row in rows if row.verification_status == status]
        keep_yes = sum(1 for row in subset if row.gold_keep_record == "yes")
        keep_no = sum(1 for row in subset if row.gold_keep_record == "no")
        by_status[status] = {
            "count": len(subset),
            "gold_keep_yes": keep_yes,
            "gold_keep_no": keep_no,
            "yes_rate": (keep_yes / len(subset) if subset else 0.0),
        }

    route_status: dict[str, dict[str, int]] = {}
    for route in ["table", "text", "mixed", "figure"]:
        subset = [row for row in rows if row.route == route]
        route_status[route] = {
            "verified_keep_yes": sum(
                1
                for row in subset
                if row.verification_status == "verified" and row.gold_keep_record == "yes"
            ),
            "verified_keep_no": sum(
                1
                for row in subset
                if row.verification_status == "verified" and row.gold_keep_record == "no"
            ),
            "unresolved_keep_yes": sum(
                1
                for row in subset
                if row.verification_status == "unresolved" and row.gold_keep_record == "yes"
            ),
            "unresolved_keep_no": sum(
                1
                for row in subset
                if row.verification_status == "unresolved" and row.gold_keep_record == "no"
            ),
        }

    dimension_pass_rates: dict[str, dict[str, int | float]] = {}
    for field in ALL_GOLD_DIMENSIONS:
        counter = Counter(getattr(row, field) for row in rows)
        yes = counter.get("yes", 0)
        no = counter.get("no", 0)
        uncertain = counter.get("uncertain", 0)
        approximate = counter.get("approximate", 0)
        na = counter.get("n_a", 0)
        dimension_pass_rates[field] = {
            "yes": yes,
            "no": no,
            "uncertain": uncertain,
            "approximate": approximate,
            "n_a": na,
            "pass_rate": yes / len(rows) if rows else 0.0,
        }

    false_negatives = [
        row for row in rows if row.verification_status == "unresolved" and row.gold_keep_record == "yes"
    ]
    false_positives = [
        row for row in rows if row.verification_status == "verified" and row.gold_keep_record == "no"
    ]
    rejected_rows = [row for row in rows if row.verification_status == "rejected"]

    false_negative_failure_counts: Counter[str] = Counter()
    for row in false_negatives:
        for reason in row.failure_reasons:
            false_negative_failure_counts[reason] += 1

    false_positive_failure_dim_counts: Counter[str] = Counter()
    for row in false_positives:
        failing_dims = [field for field in ALL_GOLD_DIMENSIONS if getattr(row, field) == "no"]
        if not failing_dims:
            false_positive_failure_dim_counts["none_but_keep_no"] += 1
        for field in failing_dims:
            false_positive_failure_dim_counts[field] += 1

    recoverable_failure_rates: dict[str, dict[str, int | float]] = {}
    unresolved_rows = [row for row in rows if row.verification_status == "unresolved"]
    unresolved_failure_totals: Counter[str] = Counter()
    unresolved_failure_kept: Counter[str] = Counter()
    for row in unresolved_rows:
        for reason in row.failure_reasons:
            unresolved_failure_totals[reason] += 1
            if row.gold_keep_record == "yes":
                unresolved_failure_kept[reason] += 1
    for reason, total in unresolved_failure_totals.items():
        keep_yes = unresolved_failure_kept.get(reason, 0)
        recoverable_failure_rates[reason] = {
            "count": total,
            "gold_keep_yes": keep_yes,
            "recoverable_rate": keep_yes / total if total else 0.0,
        }

    verified_rows = [row for row in rows if row.verification_status == "verified"]
    verified_scope_yes = [row for row in verified_rows if scope_correct(row)]
    verified_scope_and_value_yes = [row for row in verified_rows if scope_correct(row) and value_correct_or_approx(row)]
    verified_scope_yes_value_no = [row for row in verified_rows if scope_correct(row) and row.gold_value_correct == "no"]
    verified_scope_no = [row for row in verified_rows if row.gold_scope_correct == "no"]

    value_error_rows = [
        {
            "record_id": row.record_id,
            "paper_id": row.paper_id,
            "doi": row.doi,
            "route": row.route,
            "endpoint_kind": row.endpoint_kind,
            "endpoint_value": row.endpoint_value,
            "endpoint_unit": row.endpoint_unit,
            "gold_notes": row.gold_notes,
        }
        for row in rows
        if row.gold_scope_correct == "yes" and row.gold_value_correct == "no"
    ]
    value_error_route_counts = Counter(row["route"] for row in value_error_rows)

    return {
        "total_rows": len(rows),
        "unique_papers": len({row.paper_id for row in rows}),
        "overall": _metric_dict(tp, fp, fn, tn),
        "by_status": by_status,
        "by_route": by_route,
        "route_status": route_status,
        "dimension_pass_rates": dimension_pass_rates,
        "false_negative_rows": [
            {
                "record_id": row.record_id,
                "paper_id": row.paper_id,
                "doi": row.doi,
                "route": row.route,
                "failure_reasons": row.failure_reasons,
                "scope_tags": row.scope_tags,
                "all_main_scope_yes": all(getattr(row, field) == "yes" for field in MAIN_SCOPE_GATES),
                "gold_notes": row.gold_notes,
            }
            for row in false_negatives
        ],
        "false_negative_failure_counts": dict(false_negative_failure_counts),
        "false_positive_rows": [
            {
                "record_id": row.record_id,
                "paper_id": row.paper_id,
                "doi": row.doi,
                "route": row.route,
                "failing_dimensions": [field for field in ALL_GOLD_DIMENSIONS if getattr(row, field) == "no"],
                "gold_notes": row.gold_notes,
            }
            for row in false_positives
        ],
        "false_positive_failure_dimensions": dict(false_positive_failure_dim_counts),
        "rejected_rows": [
            {
                "record_id": row.record_id,
                "paper_id": row.paper_id,
                "doi": row.doi,
                "gold_keep_record": row.gold_keep_record,
                "gold_notes": row.gold_notes,
            }
            for row in rejected_rows
        ],
        "recoverable_failure_rates": recoverable_failure_rates,
        "scope_value_metrics": {
            "verified_count": len(verified_rows),
            "scope_correct_yes": len(verified_scope_yes),
            "scope_precision": (len(verified_scope_yes) / len(verified_rows) if verified_rows else 0.0),
            "scope_and_value_yes_or_approx": len(verified_scope_and_value_yes),
            "end_to_end_precision": (
                len(verified_scope_and_value_yes) / len(verified_rows) if verified_rows else 0.0
            ),
            "scope_yes_value_no": len(verified_scope_yes_value_no),
            "scope_no": len(verified_scope_no),
        },
        "value_error_rows": value_error_rows,
        "value_error_route_counts": dict(value_error_route_counts),
    }
