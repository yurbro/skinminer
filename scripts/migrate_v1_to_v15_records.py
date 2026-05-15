"""Migrate v1 single-endpoint JSONL artifacts to the PR-C v1.5 endpoint-list schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schemas.models import Record


OLD_TO_NEW_KIND = {
    "amount_per_area": "cumulative_amount",
    "amount_total": "cumulative_amount",
    "percent": "permeated_fraction",
    "percentage": "permeated_fraction",
    "flux": "flux",
    "jss": "flux",
    "unknown": "unknown",
}


def _time_to_hours(value: Any, unit: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    lowered = str(unit or "").strip().lower()
    if lowered in {"h", "hr", "hrs", "hour", "hours"}:
        return numeric
    if lowered in {"min", "mins", "minute", "minutes"}:
        return numeric / 60.0
    if lowered in {"s", "sec", "secs", "second", "seconds"}:
        return numeric / 3600.0
    if lowered in {"d", "day", "days"}:
        return numeric * 24.0
    return None


def _endpoint_kind(old_endpoint: dict[str, Any], record: dict[str, Any]) -> str:
    metadata = ((record.get("provenance") or {}).get("metadata") or {})
    if metadata.get("verification_reclassification_reason") == "unit_implies_flux":
        return "flux"
    old_kind = str(old_endpoint.get("kind") or "unknown").strip().lower()
    return OLD_TO_NEW_KIND.get(old_kind, "unknown")


def _endpoint_measurement(old_endpoint: dict[str, Any], record: dict[str, Any]) -> dict[str, Any] | None:
    value = old_endpoint.get("value")
    if value is None:
        return None
    conditions = record.get("conditions") or {}
    return {
        "kind": _endpoint_kind(old_endpoint, record),
        "mean": value,
        "sd": None,
        "unit": old_endpoint.get("unit") or "",
        "n_replicates": conditions.get("replicate_count"),
        "normalized_mean": old_endpoint.get("normalized_value"),
        "normalized_unit": old_endpoint.get("normalized_unit") or "",
    }


def migrate_row(row: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if "endpoint" not in row:
        return row, False

    migrated = dict(row)
    old_endpoint = migrated.pop("endpoint") or {}
    endpoint = _endpoint_measurement(old_endpoint, migrated)
    migrated["endpoints"] = [endpoint] if endpoint is not None else []

    conditions = dict(migrated.get("conditions") or {})
    if conditions.get("duration_h") is None:
        duration_h = _time_to_hours(old_endpoint.get("time_value"), old_endpoint.get("time_unit"))
        if duration_h is not None:
            conditions["duration_h"] = duration_h
    migrated["conditions"] = conditions
    return migrated, True


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def migrate_directory(input_dir: Path, output_dir: Path, *, validate_records: bool = True) -> dict[str, int]:
    if input_dir.resolve() == output_dir.resolve():
        raise ValueError("Refusing to migrate in place; output directory must differ from input directory.")

    stats = {
        "files": 0,
        "rows": 0,
        "records_migrated": 0,
        "records_validated": 0,
        "validation_errors": 0,
    }
    for input_path in sorted(input_dir.rglob("*.jsonl")):
        rel_path = input_path.relative_to(input_dir)
        output_path = output_dir / rel_path
        migrated_rows: list[dict[str, Any]] = []
        for row in _iter_jsonl(input_path):
            migrated, changed = migrate_row(row)
            stats["rows"] += 1
            if changed:
                stats["records_migrated"] += 1
            if validate_records and "record_id" in migrated and "paper_id" in migrated and "formulation" in migrated and "endpoints" in migrated:
                try:
                    Record.model_validate(migrated)
                    stats["records_validated"] += 1
                except Exception:
                    stats["validation_errors"] += 1
                    raise
            migrated_rows.append(migrated)
        _write_jsonl(output_path, migrated_rows)
        stats["files"] += 1
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate SkinMiner v1 JSONL outputs to PR-C v1.5 endpoint-list records.")
    parser.add_argument("--input-dir", type=Path, default=Path("outputs/full_run_16_post_all_fixes"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/full_run_16_post_all_fixes_v15_migrated"))
    parser.add_argument("--no-validate-records", action="store_true")
    args = parser.parse_args()

    stats = migrate_directory(args.input_dir, args.output_dir, validate_records=not args.no_validate_records)
    print(json.dumps(stats, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
