"""Validate JSONL gold labels or annotated gold-audit CSVs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluation.gold_audit import compute_annotation_quality_issues, load_gold_audit_csv
from evaluation.models import GoldLabelEntry
from utils.io import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SkinMiner gold-label files.")
    parser.add_argument("--gold-jsonl", type=Path, default=None)
    parser.add_argument("--gold-csv", type=Path, default=None)
    args = parser.parse_args()

    if args.gold_csv:
        rows = load_gold_audit_csv(args.gold_csv)
        issues = compute_annotation_quality_issues(rows)
        summary = {
            "mode": "gold_audit_csv",
            "rows": len(rows),
            "keep_yes_with_no": len(issues["keep_yes_with_no"]),
            "keep_no_all_main_yes": len(issues["keep_no_all_main_yes"]),
            "incomplete_rows": len(issues["incomplete_rows"]),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if args.gold_jsonl is None:
        raise SystemExit("Use --gold-csv for annotated audit CSVs, or --gold-jsonl for fixture JSONL.")

    raw_rows = load_jsonl(args.gold_jsonl)
    entries = [GoldLabelEntry.model_validate(row) for row in raw_rows]
    print(f"Validated gold-label entries: {len(entries)}")
    print(f"Source: {args.gold_jsonl}")


if __name__ == "__main__":
    main()
