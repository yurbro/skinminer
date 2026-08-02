"""Validate that staged text/provenance changes preserve all scoring metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .round2_gold import load_round2_gold_csv, score_round2_gold


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    before = load_round2_gold_csv(args.before)
    after = load_round2_gold_csv(args.after)
    before_by_id = {row.sample_id: row for row in before}
    after_by_id = {row.sample_id: row for row in after}
    if set(before_by_id) != set(after_by_id):
        raise ValueError("before/after sample_id sets differ")
    scoring_columns = {
        "source_baseline",
        "policy_level",
        "pipeline_status_v4",
        "gold_scope_correct",
        "gold_value_correct",
        "gold_keep_record",
    }
    altered_scoring_cells: list[str] = []
    for sample_id in sorted(before_by_id):
        for column in scoring_columns:
            if before_by_id[sample_id].raw[column] != after_by_id[sample_id].raw[column]:
                altered_scoring_cells.append(f"{sample_id}:{column}")
    if altered_scoring_cells:
        raise ValueError(f"scoring columns changed: {altered_scoring_cells}")
    comparisons: dict[str, object] = {}
    for level in ("v1", "v2", "v3", "v4"):
        old = score_round2_gold(before, provider="gpt", policy_level=level).as_dict()
        new = score_round2_gold(after, provider="gpt", policy_level=level).as_dict()
        comparisons[level] = {"before": old, "after": new, "unchanged": old == new}
        if old != new:
            raise ValueError(f"metrics changed at {level}")
    v4 = comparisons["v4"]["after"]
    checks = {
        "all_four_policy_levels_unchanged": all(item["unchanged"] for item in comparisons.values()),
        "extended_25_70_12": comparisons["v2"]["after"]["verified"] == 25
        and comparisons["v2"]["after"]["unresolved"] == 70
        and comparisons["v2"]["after"]["rejected"] == 12,
        "extended_scope_value_24_of_25": comparisons["v2"]["after"]["scope_value_TP"] == 24
        and comparisons["v2"]["after"]["end_to_end_precision"] == 0.96,
        "v4_unresolved_keep_yes_0_of_44": v4["unresolved"] == 44 and v4["unresolved_keep_yes"] == 0,
        "rejected_keep_no_12_of_12": v4["rejected"] == 12 and v4["rejected_keep_no"] == 12,
    }
    if not all(checks.values()):
        raise ValueError(f"acceptance checks failed: {checks}")
    payload = {
        "before": str(args.before),
        "after": str(args.after),
        "altered_scoring_cells": altered_scoring_cells,
        "policy_comparisons": comparisons,
        "checks": checks,
        "status": "PASS",
    }
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
