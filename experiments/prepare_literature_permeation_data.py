from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SOURCE_RUNS = {
    ("gpt", "v2"): ROOT / "outputs/full_run_16_post_all_fixes/v2_rescore/verified_records.jsonl",
    ("gpt", "v3"): ROOT / "outputs/full_run_16_post_all_fixes/v3_rescore/verified_records.jsonl",
    ("gpt", "v4"): ROOT / "outputs/full_run_16_post_all_fixes/v4_rescore/verified_records.jsonl",
    ("claude", "v2"): ROOT / "outputs/experiment_E3_claude_v2/v2_rescore/verified_records.jsonl",
    ("claude", "v3"): ROOT / "outputs/experiment_E3_claude_v2/v3_rescore/verified_records.jsonl",
    ("claude", "v4"): ROOT / "outputs/experiment_E3_claude_v2/v4_rescore/verified_records.jsonl",
}

ALLOWED_ENDPOINT_KINDS = {"amount_total", "amount_per_area", "amount"}
TIME_TO_HOURS = {
    "h": 1.0,
    "hr": 1.0,
    "hrs": 1.0,
    "hour": 1.0,
    "hours": 1.0,
    "min": 1.0 / 60.0,
    "mins": 1.0 / 60.0,
    "minute": 1.0 / 60.0,
    "minutes": 1.0 / 60.0,
}
POLICY_RANK = {"v2": 0, "v3": 1, "v4": 2}
BASELINE_RANK = {"gpt": 0, "claude": 1}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def stringify_component(component: dict[str, Any]) -> str:
    name = normalize_ws(str(component.get("name") or ""))
    value = component.get("concentration_value")
    unit = normalize_ws(str(component.get("concentration_unit") or ""))
    basis = normalize_ws(str(component.get("basis") or ""))
    raw = normalize_ws(str(component.get("raw") or ""))
    note = normalize_ws(str(component.get("note") or ""))
    parts = [name] if name else []
    if value not in [None, ""]:
        parts.append(str(value))
    if unit:
        parts.append(unit)
    if basis:
        parts.append(f"[{basis}]")
    if raw:
        parts.append(f"raw={raw}")
    if note:
        parts.append(f"note={note}")
    return " ".join(parts).strip()


def build_excipient_string(record: dict[str, Any]) -> str:
    components = (record.get("formulation") or {}).get("components") or []
    items = [stringify_component(component) for component in components]
    items = [item for item in items if item]
    return "; ".join(items)


def build_source_evidence(record: dict[str, Any], max_items: int = 6) -> str:
    rendered: list[str] = []
    for evidence in (record.get("evidence_items") or [])[:max_items]:
        field_name = evidence.get("field_name") or "field"
        locator = evidence.get("locator") or "unknown"
        snippet = normalize_ws(str(evidence.get("snippet") or ""))
        if len(snippet) > 180:
            snippet = snippet[:177] + "..."
        rendered.append(f"{field_name}@{locator}: {snippet}")
    return " | ".join(rendered)


def parse_pct_value(formulation: dict[str, Any]) -> float | None:
    value = formulation.get("api_concentration_value")
    if value in [None, ""]:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    unit = str(formulation.get("api_concentration_unit") or "").strip().lower()
    basis = str(formulation.get("api_basis") or "").strip().lower()
    if "%" in unit or "percent" in unit:
        return numeric
    if unit in {"mg/ml", "mg/mL".lower()} and basis == "w/v":
        return numeric / 10.0
    return None


def to_hours(value: Any, unit: str) -> float | None:
    if value in [None, ""]:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    factor = TIME_TO_HOURS.get(unit.strip().lower())
    if factor is None:
        return None
    return numeric * factor


def filter_verified_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_verified: list[dict[str, Any]] = []
    filtered: list[dict[str, Any]] = []

    for (baseline, policy), path in SOURCE_RUNS.items():
        rows = load_jsonl(path)
        for row in rows:
            if row.get("verification_status") != "verified":
                continue
            row["_baseline"] = baseline
            row["_policy"] = policy
            all_verified.append(row)

            formulation = row.get("formulation") or {}
            endpoint = row.get("endpoint") or {}
            api_name = str(formulation.get("api_name") or "").lower()
            endpoint_kind = str(endpoint.get("kind") or "").lower()
            device = str(row.get("device") or "").lower()
            endpoint_value = endpoint.get("value")
            endpoint_time = endpoint.get("time_value")

            if "ibuprofen" not in api_name:
                continue
            if endpoint_kind not in ALLOWED_ENDPOINT_KINDS:
                continue
            if endpoint_value in [None, ""] or float(endpoint_value) <= 0:
                continue
            if endpoint_time in [None, ""] or float(endpoint_time) <= 0:
                continue
            if "franz" not in device and "diffusion cell" not in device:
                continue

            filtered.append(row)

    return all_verified, filtered


def canonical_key(record: dict[str, Any]) -> tuple[Any, ...]:
    record_id = record.get("record_id")
    if record_id:
        return ("record_id", record_id)

    formulation = record.get("formulation") or {}
    endpoint = record.get("endpoint") or {}
    conditions = record.get("conditions") or {}
    return (
        "content",
        record.get("doi"),
        normalize_ws(str(formulation.get("label") or "")).lower(),
        normalize_ws(str(conditions.get("membrane_type") or "")).lower(),
        normalize_ws(str(conditions.get("membrane_source") or "")).lower(),
        endpoint.get("time_value"),
        normalize_ws(str(endpoint.get("time_unit") or "")).lower(),
        endpoint.get("normalized_value"),
        normalize_ws(str(endpoint.get("normalized_unit") or "")).lower(),
        formulation.get("api_concentration_value"),
        normalize_ws(str(formulation.get("api_concentration_unit") or "")).lower(),
        normalize_ws(str(formulation.get("api_basis") or "")).lower(),
    )


def choose_canonical_records(filtered_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[tuple[Any, ...], list[str]]]:
    selected: dict[tuple[Any, ...], tuple[tuple[int, int], dict[str, Any]]] = {}
    provenance_map: dict[tuple[Any, ...], list[str]] = defaultdict(list)
    for row in filtered_rows:
        key = canonical_key(row)
        provenance_map[key].append(f"{row['_baseline']}:{row['_policy']}:{row.get('record_id')}")
        rank = (POLICY_RANK[row["_policy"]], BASELINE_RANK[row["_baseline"]])
        prev = selected.get(key)
        if prev is None or rank < prev[0]:
            selected[key] = (rank, row)
    return [payload[1] for payload in selected.values()], provenance_map


def full_row(record: dict[str, Any]) -> dict[str, Any]:
    formulation = record.get("formulation") or {}
    endpoint = record.get("endpoint") or {}
    conditions = record.get("conditions") or {}
    return {
        "record_id": record.get("record_id"),
        "doi": record.get("doi"),
        "source_baseline": record.get("_baseline"),
        "policy_level": record.get("_policy"),
        "formulation_label": formulation.get("label") or "",
        "formulation_name": formulation.get("label") or "",
        "api_name": formulation.get("api_name") or "",
        "api_concentration_value": formulation.get("api_concentration_value"),
        "api_concentration_unit": formulation.get("api_concentration_unit") or "",
        "api_basis": formulation.get("api_basis") or "",
        "excipient_composition": build_excipient_string(record),
        "endpoint_kind": endpoint.get("kind") or "",
        "endpoint_value": endpoint.get("value"),
        "endpoint_unit": endpoint.get("unit") or "",
        "endpoint_time": endpoint.get("time_value"),
        "endpoint_time_unit": endpoint.get("time_unit") or "",
        "normalized_value_ug_cm2": endpoint.get("normalized_value"),
        "device": record.get("device") or "",
        "membrane_type": conditions.get("membrane_type") or "",
        "membrane_source": conditions.get("membrane_source") or "",
        "membrane_thickness_um": conditions.get("membrane_thickness_um"),
        "receptor_medium": conditions.get("receptor_medium") or "",
        "dose_type": conditions.get("dose_type") or "",
        "dose_amount": conditions.get("dose_amount") or "",
        "diffusion_area_cm2": conditions.get("diffusion_area_cm2"),
        "source_evidence": build_source_evidence(record),
    }


def gpr_row(record: dict[str, Any]) -> dict[str, Any]:
    formulation = record.get("formulation") or {}
    endpoint = record.get("endpoint") or {}
    conditions = record.get("conditions") or {}
    endpoint_time_h = to_hours(endpoint.get("time_value"), str(endpoint.get("time_unit") or ""))
    pct_value = parse_pct_value(formulation)
    return {
        "doi": record.get("doi"),
        "formulation_label": formulation.get("label") or "",
        "membrane_type": conditions.get("membrane_type") or "",
        "membrane_source": conditions.get("membrane_source") or "",
        "endpoint_time_h": endpoint_time_h,
        "cumulative_amount_ug_cm2": endpoint.get("normalized_value"),
        "api_concentration_pct": pct_value,
        "data_source": "literature",
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def compute_summary(
    all_verified: list[dict[str, Any]],
    filtered_rows: list[dict[str, Any]],
    canonical_rows: list[dict[str, Any]],
    gpr_rows: list[dict[str, Any]],
) -> str:
    unique_doi = len({row.get("doi") for row in canonical_rows})
    unique_formulations = len({(row.get("doi"), normalize_ws(str((row.get("formulation") or {}).get("label") or ""))) for row in canonical_rows})

    pct_values = [row["api_concentration_pct"] for row in gpr_rows if row["api_concentration_pct"] is not None]
    time_values = [row["endpoint_time_h"] for row in gpr_rows if row["endpoint_time_h"] is not None]
    response_values = [row["cumulative_amount_ug_cm2"] for row in gpr_rows if row["cumulative_amount_ug_cm2"] is not None]
    membrane_counts = Counter(normalize_ws(str(row["membrane_type"])) or "(missing)" for row in gpr_rows)
    canonical_by_doi = Counter(row.get("doi") for row in canonical_rows)
    pct_nonnull = sum(1 for row in gpr_rows if row["api_concentration_pct"] is not None)

    source_lines = [
        "- GPT baseline: `full_run_16_post_all_fixes` from `v2`, `v3`, `v4` rescore verified records",
        "- Claude baseline: `experiment_E3_claude_v2` from `v2`, `v3`, `v4` rescore verified records",
    ]
    filter_lines = [
        "- `verification_status = verified`",
        "- `api_name` contains `ibuprofen`",
        "- `endpoint.kind in {amount_total, amount_per_area, amount}`",
        "- `endpoint.value > 0` and `endpoint.time > 0`",
        "- `device` contains `Franz` or `diffusion cell`",
        "- `literature_permeation_data_gpr.csv` additionally canonical-deduplicates repeated GPT/Claude/policy observations",
    ]

    membrane_text = ", ".join(f"`{name}` ({count})" for name, count in membrane_counts.most_common(8))
    doi_text = ", ".join(f"`{doi}` ({count})" for doi, count in canonical_by_doi.most_common())

    lines = [
        "# Literature Permeation Data Summary",
        "",
        "## Source",
        "",
        *source_lines,
        "",
        "## Filtering",
        "",
        *filter_lines,
        "",
        f"- Verified rows before task filtering: `{len(all_verified)}`",
        f"- Rows after task filtering: `{len(filtered_rows)}`",
        f"- Canonical literature observations after GPT/Claude/policy dedupe: `{len(canonical_rows)}`",
        f"- GPR rows written: `{len(gpr_rows)}` (`api_concentration_pct` parseable in `{pct_nonnull}` rows)",
        "",
        "## Statistics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total records after filtering | {len(filtered_rows)} provenance rows; {len(canonical_rows)} canonical rows |",
        f"| Unique DOI | {unique_doi} |",
        f"| Unique formulations | {unique_formulations} |",
        f"| API concentration range | {min(pct_values):.3f} to {max(pct_values):.1f} % among parseable rows; many other rows use non-percent concentration descriptions |" if pct_values else "| API concentration range | n/a |",
        f"| Endpoint time range | {min(time_values):.1f} to {max(time_values):.1f} h |" if time_values else "| Endpoint time range | n/a |",
        f"| Cumulative amount range (ug/cm2) | {min(response_values):.3f} to {max(response_values):.3f} |" if response_values else "| Cumulative amount range (ug/cm2) | n/a |",
        f"| Membrane types | {membrane_text} |",
        f"| DOI distribution | {doi_text} |",
        "",
        "## Comparison With Paper 1 Self-Generated Data",
        "",
        "| Dimension | Paper 1 Data | Literature Data | Overlap |",
        "|---|---|---|---|",
        "| API | 5% w/w ibuprofen | ibuprofen only; parseable `%` rows are dominated by 5.0% plus one 0.383% w/v row | partial |",
        "| Membrane | Strat-M | mostly porcine skin / dermatomed porcine skin; no stable verified Strat-M block | low |",
        "| Device | Franz cell | all selected rows are Franz diffusion cell records | high |",
        "| Excipients | Poloxamer 407 / Ethanol / PG | mostly TPGS/HPMC nanosuspension systems, ionic-liquid systems, and other non-matching vehicles | low |",
        "| Endpoint time | 28 h | 0.5 to 72 h; no exact 28 h anchor in the current verified set | low |",
        "| Response range (ug/cm2) | ~150-350 | {:.3f} to {:.3f} | partial |".format(min(response_values), max(response_values)) if response_values else "| Response range (ug/cm2) | ~150-350 | n/a | unknown |",
        "",
        "## Heterogeneity Assessment",
        "",
        "The literature set is heterogeneous in exactly the dimensions that matter for direct formulation-space transfer. Membrane type is mostly porcine rather than Strat-M, endpoint times are much longer than the Paper 1 28 h target, and the excipient systems are usually unrelated to the Poloxamer 407 / ethanol / PG design space.",
        "",
        "The duplication analysis also shows that the apparent volume of evidence is inflated by policy and provider overlap. After removing repeated GPT/Claude/policy views of the same observation, only the canonical rows remain. The data are therefore useful as a noisy response prior, but not as a clean matched covariate dataset.",
        "",
        "## Usability Judgment",
        "",
        "This literature set is usable for a demonstration-grade GPR augmentation experiment only under a weak-prior interpretation. It is not strong enough for direct supervised transfer in the original Paper 1 excipient space.",
        "",
        "Recommended use:",
        "",
        "- Use response-only augmentation as the default (`scheme A`) with high literature noise weighting.",
        "- Start with `alpha_factor` around `10` to `20` because domain mismatch is large.",
        "- Treat any improvement as proof-of-concept evidence that literature responses can regularize early sparse-data GPR, not as evidence of exact formulation transfer.",
        "",
        "If a stronger augmentation claim is needed later, the next step is not to reuse unresolved rows under the current task constraints; it is to expand the verified pool with more matched Franz / 5% ibuprofen / membrane-compatible literature.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare literature permeation data for the PhD closed-loop demonstration.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "outputs/demonstration",
        help="Directory for output CSV/summary files.",
    )
    args = parser.parse_args()

    all_verified, filtered_rows = filter_verified_records()
    canonical_rows, _ = choose_canonical_records(filtered_rows)

    full_rows = [full_row(record) for record in filtered_rows]
    gpr_rows = [gpr_row(record) for record in canonical_rows]

    full_path = args.output_dir / "literature_permeation_data_full.csv"
    gpr_path = args.output_dir / "literature_permeation_data_gpr.csv"
    summary_path = args.output_dir / "literature_data_summary.md"

    write_csv(
        full_path,
        full_rows,
        [
            "record_id",
            "doi",
            "source_baseline",
            "policy_level",
            "formulation_label",
            "formulation_name",
            "api_name",
            "api_concentration_value",
            "api_concentration_unit",
            "api_basis",
            "excipient_composition",
            "endpoint_kind",
            "endpoint_value",
            "endpoint_unit",
            "endpoint_time",
            "endpoint_time_unit",
            "normalized_value_ug_cm2",
            "device",
            "membrane_type",
            "membrane_source",
            "membrane_thickness_um",
            "receptor_medium",
            "dose_type",
            "dose_amount",
            "diffusion_area_cm2",
            "source_evidence",
        ],
    )
    write_csv(
        gpr_path,
        gpr_rows,
        [
            "doi",
            "formulation_label",
            "membrane_type",
            "membrane_source",
            "endpoint_time_h",
            "cumulative_amount_ug_cm2",
            "api_concentration_pct",
            "data_source",
        ],
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        compute_summary(all_verified, filtered_rows, canonical_rows, gpr_rows),
        encoding="utf-8",
    )

    payload = {
        "all_verified_rows": len(all_verified),
        "filtered_rows": len(filtered_rows),
        "canonical_rows": len(canonical_rows),
        "gpr_rows": len(gpr_rows),
        "full_csv": str(full_path),
        "gpr_csv": str(gpr_path),
        "summary_md": str(summary_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
