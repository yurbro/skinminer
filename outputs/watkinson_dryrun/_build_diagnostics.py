from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "outputs" / "watkinson_dryrun"
REPORT_PATH = ROOT / "reports" / "watkinson_dryrun.md"
MASTER_PATH = OUTPUT_ROOT / "master_table_draft.csv"
DIAG_PATH = OUTPUT_ROOT / "per_paper_diagnostics.json"

PAPERS = {
    "Watkinson_2009_I": {
        "doi": "10.1159/000183922",
        "year": 2009,
        "domain": "hydrophilic_cosolvent",
        "expected": 13,
    },
    "Watkinson_2009_II": {
        "doi": "10.1159/000231528",
        "year": 2009,
        "domain": "hydrophilic_cosolvent",
        "expected": 20,
    },
    "Watkinson_2011_III": {
        "doi": "10.1159/000315139",
        "year": 2011,
        "domain": "lipophilic_vehicle",
        "expected": 14,
    },
}

COMPOSITION_ANCHORS = [
    ("Watkinson_2009_I", "Table 3", "0:100", {"ethanol_vv": 0, "water_vv": 100}),
    ("Watkinson_2009_I", "Table 3", "100:0", {"ethanol_vv": 100, "water_vv": 0}),
    ("Watkinson_2009_II", "Table 2", "70:30", {"PG_vv": 70, "water_vv": 30}),
    ("Watkinson_2009_II", "Table 3", "25:25:50", {"ethanol_vv": 25, "PG_vv": 25, "water_vv": 50}),
    ("Watkinson_2009_II", "Table 3", "50:25:25", {"ethanol_vv": 50, "PG_vv": 25, "water_vv": 25}),
    ("Watkinson_2011_III", "Table 3", "60/40", {"MO_vv": 60, "MG_vv": 40}),
]

NUMERIC_ANCHORS = [
    ("Watkinson_2009_I", "Table 3", "0:100", "silicone", 186.0, 11.0),
    ("Watkinson_2009_I", "Table 3", "100:0", "silicone", 1495.0, 116.0),
    ("Watkinson_2009_I", "Table 5", "0:100", "human_epidermis", 24.0, 2.7),
    ("Watkinson_2009_II", "Table 2", "50:50", "silicone", 277.1, 31.22),
    ("Watkinson_2009_II", "Table 2", "70:30", "silicone", 443.3, 19.86),
    ("Watkinson_2009_II", "Table 3", "25:25:50", "silicone", 525.8, 37.3),
    ("Watkinson_2009_II", "Table 5", "100:0", "human_epidermis", 133.8, 36.1),
    ("Watkinson_2011_III", "Table 3", "0/100", "silicone", 623.8, 67.7),
    ("Watkinson_2011_III", "Table 3", "100/0", "silicone", 579.4, 35.3),
    ("Watkinson_2011_III", "Table 4", "100/0", "human_epidermis", 83.1, 9.2),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def table_id(record: dict[str, Any]) -> str:
    return str(record.get("provenance", {}).get("metadata", {}).get("table_id", "") or "")


def clean_label(label: str) -> str:
    label = re.sub(r"\s*\((?:skin|human|silicone)[^)]*\)\s*", "", label or "", flags=re.I)
    return label.strip()


def classify_barrier(record: dict[str, Any]) -> str:
    membrane = str(record.get("conditions", {}).get("membrane_type", "") or "").lower()
    barrier = str(record.get("barrier", "") or "").lower()
    haystack = f"{membrane} {barrier}"
    if "silicone" in haystack:
        return "silicone"
    if "epiderm" in haystack or "human skin" in haystack or re.search(r"\bskin\b", haystack):
        return "human_epidermis"
    return ""


def normalize_unit(unit: str) -> str:
    unit = (unit or "").replace("μ", "u").replace("µ", "u")
    unit = unit.replace("Â²", "2").replace("²", "2")
    unit = unit.replace("^2", "2").replace(" ", "")
    unit = unit.replace("cm2", "cm2")
    return unit or ""


def parse_composition(record: dict[str, Any]) -> dict[str, float | None]:
    values: dict[str, float | None] = {
        "ethanol_vv": None,
        "PG_vv": None,
        "water_vv": None,
        "MO_vv": None,
        "MG_vv": None,
    }
    formulation = record.get("formulation", {}) or {}
    for component in formulation.get("components", []) or []:
        name = str(component.get("name", "") or component.get("name_raw", "") or "").lower()
        value = component.get("concentration_value")
        if value is None:
            continue
        value = float(value)
        if "ethanol" in name:
            values["ethanol_vv"] = value
        elif name in {"pg"} or "propylene glycol" in name:
            values["PG_vv"] = value
        elif "water" in name:
            values["water_vv"] = value
        elif "mineral oil" in name or name == "mo":
            values["MO_vv"] = value
        elif "miglyol" in name or name == "mg":
            values["MG_vv"] = value

    label = clean_label(str(formulation.get("label", "") or ""))
    numbers = [float(item) for item in re.findall(r"\d+(?:\.\d+)?", label)]
    paper_id = record.get("paper_id", "")
    t_id = table_id(record)
    if paper_id == "Watkinson_2009_I" and len(numbers) >= 2:
        values["ethanol_vv"] = values["ethanol_vv"] if values["ethanol_vv"] is not None else numbers[0]
        values["water_vv"] = values["water_vv"] if values["water_vv"] is not None else numbers[1]
    elif paper_id == "Watkinson_2009_II":
        if len(numbers) >= 3:
            values["ethanol_vv"] = values["ethanol_vv"] if values["ethanol_vv"] is not None else numbers[0]
            values["PG_vv"] = values["PG_vv"] if values["PG_vv"] is not None else numbers[1]
            values["water_vv"] = values["water_vv"] if values["water_vv"] is not None else numbers[2]
        elif len(numbers) >= 2:
            values["PG_vv"] = values["PG_vv"] if values["PG_vv"] is not None else numbers[0]
            values["water_vv"] = values["water_vv"] if values["water_vv"] is not None else numbers[1]
    elif paper_id == "Watkinson_2011_III" and len(numbers) >= 2:
        values["MO_vv"] = values["MO_vv"] if values["MO_vv"] is not None else numbers[0]
        values["MG_vv"] = values["MG_vv"] if values["MG_vv"] is not None else numbers[1]
    if paper_id == "Watkinson_2009_II" and t_id in {"Table 3", "Table 4", "Table 6"} and len(numbers) == 3:
        values["ethanol_vv"], values["PG_vv"], values["water_vv"] = numbers[:3]
    return values


def find_record(records: list[dict[str, Any]], expected_table: str, expected_label: str) -> dict[str, Any] | None:
    for record in records:
        if table_id(record) != expected_table:
            continue
        label = clean_label(str(record.get("formulation", {}).get("label", "") or ""))
        if label == expected_label:
            return record
    return None


def close_enough(actual: float | None, expected: float, tolerance: float = 0.01) -> bool:
    if actual is None or expected == 0:
        return False
    return abs(actual - expected) / abs(expected) <= tolerance


def unique(records: list[dict[str, Any]], getter) -> list[str]:
    values = sorted({str(getter(record)) for record in records if getter(record) not in {None, ""}})
    return values or ["MISSING"]


def build_master_rows(all_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in all_records:
        paper = PAPERS[record["paper_id"]]
        comp = parse_composition(record)
        endpoint = record.get("endpoint", {}) or {}
        conditions = record.get("conditions", {}) or {}
        barrier = classify_barrier(record)
        occlusion = ""
        include = barrier == "silicone" and occlusion == "occluded"
        row = {
            "paper_id": record["paper_id"],
            "paper_year": paper["year"],
            "doi": paper["doi"],
            "domain": paper["domain"],
            "barrier": barrier,
            "occlusion": occlusion,
            "vehicle_raw_string": str(record.get("formulation", {}).get("label", "") or ""),
            "ethanol_vv": comp["ethanol_vv"],
            "PG_vv": comp["PG_vv"],
            "water_vv": comp["water_vv"],
            "MO_vv": comp["MO_vv"],
            "MG_vv": comp["MG_vv"],
            "J_mean": endpoint.get("value"),
            "J_sd": None,
            "J_unit": normalize_unit(str(endpoint.get("unit", "") or "")),
            "replicates": conditions.get("replicate_count"),
            "kp_mean": None,
            "kp_sd": None,
            "kp_unit": "",
            "include_in_main_task": include,
        }
        rows.append(row)
    return rows


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def main() -> None:
    per_paper: dict[str, Any] = {}
    all_records: list[dict[str, Any]] = []
    stage_rows = {row["paper_id"]: row for row in load_jsonl(OUTPUT_ROOT / "stage_run_summary.jsonl")}

    for paper_id in PAPERS:
        paper_dir = OUTPUT_ROOT / paper_id
        route = load_jsonl(paper_dir / "route_decisions.jsonl")
        table = load_jsonl(paper_dir / "table_records.jsonl")
        text = load_jsonl(paper_dir / "text_records.jsonl")
        figure = load_jsonl(paper_dir / "figure_records.jsonl")
        assembled = load_jsonl(paper_dir / "assembled_records.jsonl")
        verified = load_jsonl(paper_dir / "verified_records.jsonl")
        all_records.extend(verified)

        composition_results = []
        for anchor_paper, anchor_table, anchor_label, expected in COMPOSITION_ANCHORS:
            if anchor_paper != paper_id:
                continue
            record = find_record(verified, anchor_table, anchor_label)
            parsed = parse_composition(record) if record else {}
            ok = bool(record) and all(parsed.get(key) == float(value) for key, value in expected.items())
            composition_results.append(
                {
                    "table": anchor_table,
                    "vehicle": anchor_label,
                    "expected": expected,
                    "extracted_record_id": record.get("record_id") if record else None,
                    "parsed": parsed or None,
                    "correct": ok,
                }
            )

        numeric_results = []
        for anchor_paper, anchor_table, anchor_label, expected_barrier, expected_j, expected_sd in NUMERIC_ANCHORS:
            if anchor_paper != paper_id:
                continue
            record = find_record(verified, anchor_table, anchor_label)
            extracted = None if record is None else record.get("endpoint", {}).get("value")
            ratio = None
            if extracted is not None:
                ratio = float(extracted) / expected_j
            numeric_results.append(
                {
                    "table": anchor_table,
                    "vehicle": anchor_label,
                    "expected_barrier": expected_barrier,
                    "extracted_barrier": classify_barrier(record) if record else None,
                    "expected_J": expected_j,
                    "expected_SD": expected_sd,
                    "extracted_J": extracted,
                    "extracted_SD": None,
                    "ratio": ratio,
                    "within_1pct": close_enough(float(extracted) if extracted is not None else None, expected_j),
                    "record_id": record.get("record_id") if record else None,
                }
            )

        per_paper[paper_id] = {
            "doi": PAPERS[paper_id]["doi"],
            "expected_permeation_records": PAPERS[paper_id]["expected"],
            "route": route[0]["route"] if route else "missing",
            "route_raw_labels": route[0].get("raw_labels", {}) if route else {},
            "stage_counts": {
                "table_records": len(table),
                "text_records": len(text),
                "figure_records": len(figure),
                "assembled_records": len(assembled),
                "verified_records": len(verified),
                "verified_status_counts": dict(Counter(row.get("verification_status", "") for row in verified)),
            },
            "unique_units": unique(verified, lambda r: normalize_unit(str(r.get("endpoint", {}).get("unit", "") or ""))),
            "unique_endpoint_kinds": unique(verified, lambda r: r.get("endpoint", {}).get("kind")),
            "unique_devices": unique(verified, lambda r: r.get("device")),
            "unique_membrane_types": unique(verified, lambda r: r.get("conditions", {}).get("membrane_type")),
            "unique_temperatures": unique(verified, lambda r: r.get("conditions", {}).get("temperature_c")),
            "unique_receptor_media": unique(verified, lambda r: r.get("conditions", {}).get("receptor_medium")),
            "unique_receptor_volumes": unique(verified, lambda r: r.get("conditions", {}).get("receptor_volume_ml")),
            "unique_replicates": unique(verified, lambda r: r.get("conditions", {}).get("replicate_count")),
            "api_state_or_concentration": sorted(
                {
                    "|".join(
                        str(value)
                        for value in (
                            row.get("formulation", {}).get("dosage_form"),
                            row.get("formulation", {}).get("api_concentration_value"),
                            row.get("formulation", {}).get("api_concentration_unit"),
                            row.get("formulation", {}).get("api_concentration_raw"),
                        )
                    )
                    for row in verified
                }
            ),
            "composition_parsed_to_columns_in_skinminer_schema": False,
            "composition_anchor_results": composition_results,
            "numeric_anchor_results": numeric_results,
            "protocol_modifier_capture": {
                "structured_occlusion_field_present": False,
                "structured_pretreatment_field_present": False,
                "occlusion_or_pretreatment_only_in_free_text_evidence": any(
                    re.search(r"occlud|pretreat", json.dumps(row, ensure_ascii=False), flags=re.I)
                    for row in verified
                ),
            },
        }

    master_rows = build_master_rows(all_records)
    with MASTER_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(master_rows[0].keys()))
        writer.writeheader()
        writer.writerows(master_rows)

    n_total = len(master_rows)
    n_main = sum(1 for row in master_rows if row["include_in_main_task"])
    complete_cols = ["J_mean", "J_sd", "occlusion", "vehicle_raw_string", "J_unit"]
    composition_cols = ["ethanol_vv", "PG_vv", "water_vv", "MO_vv", "MG_vv"]
    n_complete = 0
    for row in master_rows:
        if not row["include_in_main_task"]:
            continue
        if not all(row.get(col) not in {None, ""} for col in complete_cols):
            continue
        if not any(row.get(col) not in {None, ""} for col in composition_cols):
            continue
        n_complete += 1
    coverage_ratio = n_complete / 28
    decision = "GREEN" if coverage_ratio >= 0.8 else ("YELLOW" if coverage_ratio >= 0.5 else "RED")

    comp_total = 0
    comp_pass = 0
    numeric_total = 0
    numeric_pass = 0
    for item in per_paper.values():
        for result in item["composition_anchor_results"]:
            comp_total += 1
            comp_pass += int(result["correct"])
        for result in item["numeric_anchor_results"]:
            numeric_total += 1
            numeric_pass += int(result["within_1pct"])

    diagnostics = {
        "entry_point": {
            "manual_corpus_workaround": True,
            "description": "No run_pipeline.py --pdf/--input-pdf flag exists. The dry-run constructed ContentAccess objects with local_paths.pdf pointing at papers/uploaded_external/*.pdf and invoked SkinMiner router/extractor/assembly/patch/verification modules from the router stage.",
            "policy": "v4_accept_flux",
            "llm_provider": "openai",
            "model": "gpt-4o-mini",
        },
        "per_paper": per_paper,
        "master_summary": {
            "n_total_extracted_permeation_records": n_total,
            "n_silicone_occluded_main_task": n_main,
            "n_with_complete_main_task_fields": n_complete,
            "coverage_ratio": coverage_ratio,
            "decision": decision,
            "composition_anchor_accuracy": f"{comp_pass}/{comp_total}",
            "numerical_anchor_accuracy": f"{numeric_pass}/{numeric_total}",
        },
    }
    DIAG_PATH.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")

    report_lines: list[str] = []
    report_lines.append("# Watkinson Three-PDF SkinMiner Extraction Dry-Run\n")
    report_lines.append("## 1. Executive Summary")
    report_lines.append(
        f"Decision: **{decision}**. The aggregate verified-record count is {n_total}/47 (83%), but this is not modelling-ready. "
        f"The main-task complete-field coverage is {n_complete}/28 = {coverage_ratio:.3f}; composition anchors pass {comp_pass}/{comp_total}; "
        f"numeric J spot-checks pass {numeric_pass}/{numeric_total}. The verifier accepted all final records, but key table values, SDs, barrier/protocol fields, and replicate fields are not reliable."
    )
    report_lines.append(
        "Entry point used: manual ContentAccess local PDF workaround from the router stage (`manual_corpus_workaround=true`), using policy `v4_accept_flux`."
    )
    report_lines.append("\n## 2. SkinMiner PDF Entry Point Used")
    report_lines.append(
        "`run_pipeline.py --help` exposes `--input-csv`, `--policy`, content download flags, and model flags, but no direct `--pdf` or `--input-pdf` upload flag. "
        "`scripts/` is absent. `access/resolve_content.py` resolves OA URLs and downloads into `papers/`, but does not consume `papers/uploaded_external/*.pdf` from the input CSV. "
        "Therefore this run used the documented fallback strategy: a minimal manual corpus and explicit `ContentAccess(local_paths={'pdf': ...})`, then direct invocation of the router, extractor, assembly, patching, and verifier modules. SkinMiner source code was not changed."
    )
    report_lines.append("\n## 3. Watkinson_2009_I Diagnostic")
    report_lines.extend(paper_section("Watkinson_2009_I", per_paper["Watkinson_2009_I"]))
    report_lines.append("\n## 4. Watkinson_2009_II Diagnostic")
    report_lines.extend(paper_section("Watkinson_2009_II", per_paper["Watkinson_2009_II"]))
    report_lines.append("\n## 5. Watkinson_2011_III Diagnostic")
    report_lines.extend(paper_section("Watkinson_2011_III", per_paper["Watkinson_2011_III"]))
    report_lines.append("\n## 6. Cross-Paper Consistency")
    cross_rows = []
    for field, key in [
        ("device", "unique_devices"),
        ("membrane_type", "unique_membrane_types"),
        ("temperature_c", "unique_temperatures"),
        ("receptor_medium", "unique_receptor_media"),
        ("receptor_volume_ml", "unique_receptor_volumes"),
    ]:
        cross_rows.append([field] + ["; ".join(per_paper[pid][key]) for pid in PAPERS])
    report_lines.append(markdown_table(["field", *PAPERS.keys()], cross_rows))
    report_lines.append(
        "The device label is consistent, but membrane/barrier, temperature, receptor medium, and receptor volume require manual normalization. Temperature is missing in all structured records; receptor volume is absent for Part III."
    )
    report_lines.append("\n## 7. Master Table Draft Summary")
    report_lines.append(markdown_table(
        ["metric", "value"],
        [
            ["n_total_extracted_permeation_records", n_total],
            ["n_silicone_occluded_main_task", n_main],
            ["n_with_complete_main_task_fields", n_complete],
            ["coverage_ratio", f"{n_complete}/28 = {coverage_ratio:.3f}"],
            ["decision", decision],
        ],
    ))
    report_lines.append(
        f"`{MASTER_PATH.relative_to(ROOT)}` contains {n_total} rows. `include_in_main_task` is false for all rows because no structured occlusion field was captured; `J_sd` is also empty for all rows."
    )
    report_lines.append("\n## 8. Failure Modes Inventory")
    report_lines.append("- No formal user-uploaded PDF entry point; dry-run required manual `ContentAccess` construction.")
    report_lines.append("- PDF table text concatenates mean and SD values; the table extractor often selected SD or adjacent-column values as J.")
    report_lines.append("- Part II Table 3/4/6 ternary records were not extracted; Part III Table 3 silicone records were not extracted.")
    report_lines.append("- Part III Table 4 values were repeated/misaligned, and a silicone 100/0 J value appears under the human epidermis table.")
    report_lines.append("- All final records were marked `verified`, so verifier acceptance did not catch row/column misalignment.")
    report_lines.append("- `endpoint.kind` was usually normalized to `amount_per_area` despite flux units; v4 accepted the flux-like unit string.")
    report_lines.append("- Occlusion, non-occlusion, ethanol pretreatment, and replicate count were not represented as structured fields.")
    report_lines.append("- `patch_endpoint_time` can recover irrelevant analytical times; Part II records received 5 min from HPLC retention context.")
    report_lines.append("\n## 9. Recommendations for Phase 1")
    report_lines.append("- Treat this dry-run as RED; do not proceed to modelling from these records without a table-extraction fix or manual curation.")
    report_lines.append("- Add a first-class local PDF upload/input entry point before production demonstrations.")
    report_lines.append("- Extend the table schema for paired mean/SD columns and explicit endpoint families (`J`, `kp`, `Kh`, `D/h2`) instead of a single endpoint value.")
    report_lines.append("- Add structured fields for `occlusion`, `pretreatment`, `replicates`, `temperature`, `receptor_medium`, and `receptor_volume`.")
    report_lines.append("- Tighten verification so flux units set `endpoint.kind=flux` and table row/column alignment is checked before `verified` status.")
    report_lines.append("\n## 10. Known Limitations")
    report_lines.append("- Ground truth counts and anchor values were taken from the supplied task; this report did not re-count the PDFs.")
    report_lines.append("- This is one LLM run with the repository default OpenAI baseline (`gpt-4o-mini`); stochastic extraction may vary.")
    report_lines.append("- The master table parser only parses vehicle composition from extracted labels/components; it does not repair missing records or numeric values.")
    report_lines.append("- Figure extraction was not triggered because no paper routed as `figure`; empty figure stage JSONL files are present.")
    REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("[WATKINSON DRY-RUN] Finished.")
    print("  Entry point used: manual ContentAccess local_paths.pdf workaround from router stage")
    print("")
    print("  Per-paper extraction:")
    label_map = {
        "Watkinson_2009_I": "Part I",
        "Watkinson_2009_II": "Part II",
        "Watkinson_2011_III": "Part III",
    }
    for pid, meta in PAPERS.items():
        row = stage_rows[pid]
        print(f"    {label_map[pid]:<8} ({meta['doi']}): expected {meta['expected']} / extracted {row['final_records_evaluated']} / verified {row['verified']}")
    print("")
    print(f"  Composition parsing accuracy: {comp_pass}/{comp_total} anchor records parsed correctly")
    print(f"  Numerical spot-check accuracy: {numeric_pass}/{numeric_total} anchor J values within 1%")
    print("")
    print("  Master table:")
    print(f"    n_silicone_occluded_main_task: {n_main}")
    print(f"    n_with_complete_main_task_fields: {n_complete}")
    print(f"    coverage_ratio: {n_complete} / 28 = {coverage_ratio:.3f}")
    print("")
    print(f"  Decision: {decision}")
    print("")
    print("  Output files written:")
    print("    reports/watkinson_dryrun.md")
    print("    outputs/watkinson_dryrun/master_table_draft.csv")
    print("    outputs/watkinson_dryrun/per_paper_diagnostics.json")
    for pid in PAPERS:
        print(f"    outputs/watkinson_dryrun/{pid}/")


def paper_section(paper_id: str, item: dict[str, Any]) -> list[str]:
    counts = item["stage_counts"]
    lines = [
        markdown_table(
            ["field", "value"],
            [
                ["DOI", item["doi"]],
                ["route", item["route"]],
                ["expected permeation records", item["expected_permeation_records"]],
                ["table/text/figure records", f"{counts['table_records']} / {counts['text_records']} / {counts['figure_records']}"],
                ["assembled records", counts["assembled_records"]],
                ["verified records", counts["verified_records"]],
                ["verification status counts", json.dumps(counts["verified_status_counts"], ensure_ascii=False)],
                ["unique endpoint kinds", "; ".join(item["unique_endpoint_kinds"])],
                ["unique J units", "; ".join(item["unique_units"])],
                ["unique membranes", "; ".join(item["unique_membrane_types"])],
                ["replicates", "; ".join(item["unique_replicates"])],
            ],
        )
    ]
    lines.append("\nComposition anchors:")
    lines.append(markdown_table(
        ["table", "vehicle", "record", "parsed", "correct"],
        [
            [
                result["table"],
                result["vehicle"],
                result["extracted_record_id"] or "null",
                json.dumps(result["parsed"], ensure_ascii=False) if result["parsed"] else "null",
                result["correct"],
            ]
            for result in item["composition_anchor_results"]
        ],
    ))
    lines.append("\nNumerical J anchors:")
    lines.append(markdown_table(
        ["table", "vehicle", "expected_J", "extracted_J", "ratio", "within_1pct", "record"],
        [
            [
                result["table"],
                result["vehicle"],
                result["expected_J"],
                "null" if result["extracted_J"] is None else result["extracted_J"],
                "null" if result["ratio"] is None else f"{result['ratio']:.4f}",
                result["within_1pct"],
                result["record_id"] or "null",
            ]
            for result in item["numeric_anchor_results"]
        ],
    ))
    lines.append(
        "\nProtocol/API/replicates: no structured occlusion, pretreatment, or replicate-count field was captured. "
        f"API state/concentration values: `{'; '.join(item['api_state_or_concentration'])}`."
    )
    return lines


if __name__ == "__main__":
    main()
