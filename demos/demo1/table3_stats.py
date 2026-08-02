"""Rebuild and verify the ten rows of the manuscript Watkinson Table 3.

The manuscript reports whole-number J ranges. The archived 47-row export has
integer values for Part I and two-decimal extraction values for Parts II/III,
so observed minima and maxima are compared after manuscript-equivalent
rounding to the nearest integer. Raw extrema remain in the output for audit.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def display_integer(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-csv", type=Path, required=True)
    parser.add_argument("--reference-csv", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    args = parser.parse_args()

    with args.records_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        records = list(csv.DictReader(handle))
    if len(records) != 47:
        raise ValueError(f"expected the 47-row Watkinson export; found {len(records)} rows")
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in records:
        groups[(row["doi"].strip().lower(), row["source_table"].strip())].append(float(row["J_mean"]))

    with args.reference_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        reference = list(csv.DictReader(handle))
    if len(reference) != 10:
        raise ValueError(f"expected ten manuscript rows; found {len(reference)}")
    results: list[dict[str, object]] = []
    for expected in reference:
        key = (expected["doi"].strip().lower(), expected["source_table"].strip())
        values = groups.get(key, [])
        raw_min = min(values) if values else None
        raw_max = max(values) if values else None
        observed_min = display_integer(raw_min) if raw_min is not None else None
        observed_max = display_integer(raw_max) if raw_max is not None else None
        n_match = len(values) == int(expected["expected_records"])
        min_match = observed_min == int(expected["expected_j_min"])
        max_match = observed_max == int(expected["expected_j_max"])
        results.append(
            {
                "paper": expected["paper"],
                "doi": expected["doi"],
                "source_table": expected["source_table"],
                "expected_records": expected["expected_records"],
                "observed_records": len(values),
                "expected_j_min": expected["expected_j_min"],
                "observed_j_min_raw": "" if raw_min is None else f"{raw_min:g}",
                "observed_j_min_display": "" if observed_min is None else observed_min,
                "expected_j_max": expected["expected_j_max"],
                "observed_j_max_raw": "" if raw_max is None else f"{raw_max:g}",
                "observed_j_max_display": "" if observed_max is None else observed_max,
                "record_count_status": "MATCH" if n_match else "MISMATCH",
                "j_range_status": "MATCH" if min_match and max_match else "MISMATCH",
                "overall_status": "VERIFIED" if n_match and min_match and max_match else "MISMATCH",
            }
        )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(results[0])
    with args.output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    failures = [row for row in results if row["overall_status"] != "VERIFIED"]
    summary = {
        "records_input": len(records),
        "groups_observed": len(groups),
        "manuscript_rows": len(reference),
        "verified_rows": len(results) - len(failures),
        "mismatched_rows": len(failures),
        "comparison_rule": "record count exact; J range min/max rounded half-up to manuscript whole-number display",
        "status": "VERIFIED" if not failures else "FAILED",
        "failures": failures,
    }
    args.summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
    if failures:
        raise SystemExit("Table 3 verification failed; stop before later Stage 5A tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
