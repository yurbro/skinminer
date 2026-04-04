"""Validate JSONL gold labels against the typed evaluation model."""

from __future__ import annotations

import argparse
from pathlib import Path

from evaluation.models import GoldLabelEntry
from utils.io import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SkinMiner gold-label JSONL files.")
    parser.add_argument("--gold-jsonl", type=Path, required=True)
    args = parser.parse_args()

    rows = load_jsonl(args.gold_jsonl)
    entries = [GoldLabelEntry.model_validate(row) for row in rows]
    print(f"Validated gold-label entries: {len(entries)}")
    print(f"Source: {args.gold_jsonl}")


if __name__ == "__main__":
    main()
