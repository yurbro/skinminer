from __future__ import annotations

import csv
import json
import math
import re
import textwrap
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.path import Path as MplPath
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
OUTPUT_DIR = ROOT / "outputs" / "paper_figures"
DEMO_DIR = ROOT / "outputs" / "demonstration"

MM_TO_IN = 1.0 / 25.4
SINGLE_COL_IN = 89 * MM_TO_IN
DOUBLE_COL_IN = 180 * MM_TO_IN

COLORS = {
    "input_gray": "#B8B8B8",
    "llm_blue": "#4C78A8",
    "extract_green": "#59A14F",
    "verify_orange": "#F28E2B",
    "output_blue": "#1F4E79",
    "red": "#D62728",
    "light_blue": "#9ECAE1",
    "light_gray": "#D9D9D9",
    "dark_gray": "#4D4D4D",
    "purple": "#B07AA1",
    "teal": "#76B7B2",
    "soft_green": "#8CD17D",
    "soft_orange": "#FFBE7D",
}

POLICY_LABELS = {
    "v1": "Strict (5% w/w)",
    "v2": "Extended (+ w/v)",
    "v3": "Any concentration",
    "v4": "+ Flux/Jss endpoints",
}
POLICY_SHORT_LABELS = {
    "v1": "Strict\n(5% w/w)",
    "v2": "Extended\n(+ w/v)",
    "v3": "Any\nconcentration",
    "v4": "+ Flux/Jss\nendpoints",
}
EXPERIMENT_DISPLAY = {
    "Baseline v1": "Baseline\n(strict policy)",
    "Baseline v2": "Baseline\n(extended policy)",
    "E2": "GPT-5.4\nupgrade",
    "E3 v2": "Claude Sonnet\n(extended)",
    "E4": "CV-only\n(no VLM)",
    "E6": "Patching\nablation",
    "E7": "Promotion\nablation",
    "E8": "Relaxed\nscope",
}
SINGLE_PASS_DISPLAY = {
    "Pipeline": "Modular\npipeline",
    "SP-1": "Single-pass\n(text,\nGPT-4o-mini)",
    "SP-2": "Single-pass\n(PDF,\nGPT-4o-mini)",
    "SP-3": "Single-pass\n(PDF,\nGPT-5.4-mini)",
    "SP-4": "Single-pass\n(PDF,\nClaude Sonnet)",
}
REPRO_RUN_LABELS = ["Run 1", "Run 2", "Run 3", "Run 4", "Run 5"]
TOKEN_PRICE_USD_PER_MILLION = {
    ("openai", "gpt-4o-mini"): (0.15, 0.60),
    ("openai", "gpt-5.4-mini"): (0.75, 4.50),
    ("anthropic", "claude-sonnet-4-6"): (3.00, 15.00),
}


@dataclass
class PaperMetrics:
    corpus_rows: int
    rule_pass_rows: int
    gpt_assembled: int
    claude_assembled: int
    llm_retained: int
    assembled_route_counts: dict[str, int]
    extractor_output_counts: dict[str, int]
    v2_status_counts: dict[str, int]
    gpt_policy_verified: dict[str, int]
    claude_policy_verified: dict[str, int]
    gpt_policy_precision: dict[str, float]
    claude_policy_precision: dict[str, float]
    round2_rows: int
    v2_e2e_precision: float
    unresolved_sample_size: int
    unresolved_false_negatives: int
    rejected_sample_size: int
    rejected_correct: int
    single_pass_rows: list[dict[str, object]]
    pipeline_cost_usd: float
    reproducibility_runs_v1: list[int]
    reproducibility_runs_v2: list[int]
    reproducibility_v1_mean: float
    reproducibility_v1_sd: float
    reproducibility_v1_cv: float
    reproducibility_v2_mean: float
    reproducibility_v2_sd: float
    reproducibility_v2_cv: float
    stable_v2_core: int
    experiment_verified: dict[str, int]
    comparability_rows: list[dict[str, str]]
    value_accuracy_rows: list[dict[str, object]]
    dataflow_counts: dict[str, int]
    failure_heatmap_rows: list[dict[str, object]]
    waterfall_rows: list[dict[str, object]]
    resource_rows: list[dict[str, object]]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_match(pattern: str, text: str, label: str, flags: int = 0) -> re.Match[str]:
    match = re.search(pattern, text, flags)
    if not match:
        raise ValueError(f"Could not parse {label}")
    return match


def line_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def clean_md_value(value: str) -> str:
    return value.replace("`", "").replace(",", "").strip()


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "legend.frameon": False,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def parse_baseline_metrics() -> tuple[int, int, int, int]:
    text = read_text(REPORTS_DIR / "baseline_definition.md")
    corpus_rows = int(require_match(r"Corpus: .*?\((\d+) rows\)", text, "corpus rows").group(1))
    rule_pass_rows = int(require_match(r"Rule-pass rows: (\d+)", text, "rule-pass rows").group(1))
    gpt_block = require_match(
        r"### GPT Baseline(.*?)### Claude Baseline",
        text,
        "GPT baseline block",
        flags=re.S,
    ).group(1)
    claude_block = require_match(
        r"### Claude Baseline(.*?)(?:## Freeze Rules)",
        text,
        "Claude baseline block",
        flags=re.S,
    ).group(1)
    gpt_assembled = int(
        require_match(
            r"Post-patch rescore input: .*?\((\d+) records\)",
            gpt_block,
            "GPT assembled",
        ).group(1)
    )
    claude_assembled = int(
        require_match(
            r"Post-patch rescore input: .*?\((\d+) records\)",
            claude_block,
            "Claude assembled",
        ).group(1)
    )
    return corpus_rows, rule_pass_rows, gpt_assembled, claude_assembled


def parse_gpt_run_counts() -> tuple[int, dict[str, int], dict[str, int], dict[str, int]]:
    route_decisions = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "route_decisions.csv")
    assembled = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "assembled_records.csv")
    v2_rescore = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "v2_rescore" / "verified_records.csv")
    table_records = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "table_records.csv")
    figure_records = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "figure_records.csv")
    text_records = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "text_records.csv")

    llm_retained = len(route_decisions)
    assembled_route_counts = {key: int(value) for key, value in assembled["route"].value_counts().to_dict().items()}
    v2_status_counts = {
        key: int(value) for key, value in v2_rescore["verification_status"].value_counts().to_dict().items()
    }
    extractor_output_counts = {
        "table": len(table_records),
        "figure": len(figure_records),
        "text": len(text_records),
    }
    return llm_retained, assembled_route_counts, extractor_output_counts, v2_status_counts


def parse_policy_verified() -> tuple[dict[str, int], dict[str, int]]:
    text = read_text(REPORTS_DIR / "policy_sensitivity_analysis.md")
    gpt_block = require_match(
        r"## GPT Baseline \(full_run_16\)(.*?)## Claude Baseline",
        text,
        "GPT policy table",
        flags=re.S,
    ).group(1)
    claude_block = require_match(
        r"## Claude Baseline \(E3_claude_v2\)(.*?)## Cross-Policy Progression",
        text,
        "Claude policy table",
        flags=re.S,
    ).group(1)

    def parse_block(block: str) -> dict[str, int]:
        policy_map: dict[str, int] = {}
        name_map = {
            "v1 strict": "v1",
            "v2 accept_wv": "v2",
            "v3 any_conc": "v3",
            "v4 accept_flux": "v4",
        }
        for line in block.splitlines():
            if not line.strip().startswith("| v"):
                continue
            cells = line_cells(line)
            if cells[0] in name_map:
                policy_map[name_map[cells[0]]] = int(cells[2])
        return policy_map

    return parse_block(gpt_block), parse_block(claude_block)


def parse_gold_metrics() -> tuple[dict[str, float], int, float, int, int, int, int]:
    text = read_text(REPORTS_DIR / "gold_evaluation_round2.md")
    round2_rows = int(
        require_match(
            r"Round 2 manual annotation contains (\d+) rows",
            text,
            "round2 rows",
        ).group(1)
    )
    precision_map: dict[str, float] = {}
    end_to_end_v2 = None

    precision_block = require_match(
        r"## 2\. Precision By Policy Level(.*?)## 3\. Scope Precision vs End-to-End Precision",
        text,
        "gold precision block",
        flags=re.S,
    ).group(1)
    scope_block = require_match(
        r"## 3\. Scope Precision vs End-to-End Precision(.*?)## 4\. Recall Estimation",
        text,
        "gold scope block",
        flags=re.S,
    ).group(1)

    for line in precision_block.splitlines():
        if not line.strip().startswith("| v"):
            continue
        cells = line_cells(line)
        label = cells[0]
        if label == "v1 only":
            precision_map["v1"] = float(cells[4].rstrip("%"))
        elif label == "v1+v2":
            precision_map["v2"] = float(cells[4].rstrip("%"))
        elif label == "v1+v2+v3":
            precision_map["v3"] = float(cells[4].rstrip("%"))
        elif label == "v1+v2+v3+v4 (all)":
            precision_map["v4"] = float(cells[4].rstrip("%"))

    for line in scope_block.splitlines():
        if line.strip().startswith("| v1+v2 |"):
            cells = line_cells(line)
            end_to_end_v2 = float(cells[5].rstrip("%"))
            break

    unresolved_sample_size = int(
        require_match(
            r"Tier 2 unresolved sample size: `(\d+)`",
            text,
            "unresolved sample size",
        ).group(1)
    )
    unresolved_false_negatives = int(
        require_match(
            r"Gold keep records in unresolved sample: `(\d+)`",
            text,
            "unresolved false negatives",
        ).group(1)
    )
    rejected_sample_size = int(
        require_match(
            r"Tier 3 rejected sample size: `(\d+)`",
            text,
            "rejected sample size",
        ).group(1)
    )
    rejected_correct = int(
        require_match(
            r"Correct rejections .*?: `(\d+)`",
            text,
            "rejected correct",
        ).group(1)
    )
    if end_to_end_v2 is None:
        raise ValueError("Could not parse v2 end-to-end precision")
    return (
        precision_map,
        round2_rows,
        end_to_end_v2,
        unresolved_sample_size,
        unresolved_false_negatives,
        rejected_sample_size,
        rejected_correct,
    )


def parse_claude_policy_precision() -> dict[str, float]:
    path = ROOT / "outputs" / "claude_gold_audit" / "claude_per_policy_precision.csv"
    precision = {"v1": math.nan}
    if not path.exists():
        precision.update({"v2": math.nan, "v3": math.nan, "v4": math.nan})
        return precision
    frame = pd.read_csv(path)
    for _, row in frame.iterrows():
        precision[str(row["policy"])] = float(row["precision_pct"])
    for policy in ["v2", "v3", "v4"]:
        precision.setdefault(policy, math.nan)
    return precision


def parse_single_pass_metrics() -> tuple[list[dict[str, object]], float]:
    report_text = read_text(REPORTS_DIR / "single_pass_architecture_comparison.md")
    pipeline_cmp_text = read_text(
        ROOT / "outputs" / "experiment_single_pass" / "single_pass_vs_pipeline_comparison.md"
    )
    rows: list[dict[str, object]] = [
        {
            "method": "Pipeline",
            "input_mode": "modular",
            "model": "gpt-4o-mini",
            "coverage_pct": 100.0,
            "coverage_num": "25/25",
            "value_pct": 96.0,
            "value_num": "24/25",
        }
    ]
    pipeline_cost = float(
        require_match(
            r"Modular Pipeline \(full run reference\) \| ~3\.8M \| ~\$(\d+\.\d+)",
            pipeline_cmp_text,
            "pipeline cost",
        ).group(1)
    )
    mapping = {
        "SP-1": ("text + HTML tables", "gpt-4o-mini"),
        "SP-2": ("raw PDF", "gpt-4o-mini"),
        "SP-3": ("raw PDF", "gpt-5.4-mini"),
        "SP-4": ("raw PDF", "claude-sonnet-4-6"),
    }
    for line in report_text.splitlines():
        if not line.startswith("| SP-"):
            continue
        cells = line_cells(line)
        method = cells[0]
        coverage_num, coverage_pct = [part.strip() for part in cells[5].split("=")]
        value_num, value_pct = [part.strip() for part in cells[6].split("=")]
        rows.append(
            {
                "method": method,
                "input_mode": mapping[method][0],
                "model": mapping[method][1],
                "coverage_pct": float(clean_md_value(coverage_pct).rstrip("%")),
                "coverage_num": clean_md_value(coverage_num),
                "value_pct": float(clean_md_value(value_pct).rstrip("%")),
                "value_num": clean_md_value(value_num),
                "cost_usd": float(clean_md_value(cells[11]).replace("$", "")),
            }
        )
    rows[0]["cost_usd"] = pipeline_cost
    return rows, pipeline_cost


def parse_reproducibility_metrics() -> tuple[list[int], list[int], float, float, float, float, float, float, int]:
    text = read_text(REPORTS_DIR / "reproducibility_analysis.md")

    def find_row(prefix: str) -> list[str]:
        for line in text.splitlines():
            if line.startswith(prefix):
                return line_cells(line)
        raise ValueError(f"Could not parse row: {prefix}")

    v1_row = find_row("| verified (v1) |")
    v2_row = find_row("| verified (v2) |")
    stable_core = int(
        require_match(
            r"the intersection of v2-verified records is `(\d+)` records",
            text,
            "stable v2 core",
        ).group(1)
    )
    v1_runs = [int(v1_row[index]) for index in range(1, 6)]
    v2_runs = [int(v2_row[index]) for index in range(1, 6)]
    return (
        v1_runs,
        v2_runs,
        float(v1_row[6]),
        float(v1_row[7]),
        float(v1_row[8]),
        float(v2_row[6]),
        float(v2_row[7]),
        float(v2_row[8]),
        stable_core,
    )


def parse_experiment_verified() -> dict[str, int]:
    text = read_text(REPORTS_DIR / "experiment_summary_all.md")
    result: dict[str, int] = {}
    patterns = {
        "E2": r"\| E2 .*?\| .*?\| (\d+) \|",
        "E4": r"\| E4 .*?\| .*?\| (\d+) \|",
        "E8": r"\| E8 .*?\| .*?\| (\d+) \|",
        "E6": r"\| E6 .*?\| .*?\| (\d+) \|",
        "E7": r"\| E7 .*?\| .*?\| (\d+) \|",
    }
    for key, pattern in patterns.items():
        result[key] = int(require_match(pattern, text, f"{key} verified").group(1))
    return result


def parse_demo_metrics() -> list[dict[str, str]]:
    comp_df = pd.read_csv(DEMO_DIR / "fig_comparability_table.csv")
    return comp_df.to_dict("records")


def parse_value_accuracy_rows() -> list[dict[str, object]]:
    gold = pd.read_csv(ROOT / "outputs" / "gold_audit_set" / "round2" / "gold_set_round2_annotation.csv")
    subset = gold[(gold["gold_keep_record"] == "yes") & (gold["gold_endpoint_value_correct"].isin(["yes", "near"]))].copy()
    rows: list[dict[str, object]] = []
    for _, row in subset.iterrows():
        pipeline_value = float(row["endpoint_normalized_value"])
        gold_value = pipeline_value
        gold_note = row["gold_endpoint_value_note"] if isinstance(row["gold_endpoint_value_note"], str) else ""
        if row["gold_endpoint_value_correct"] == "near":
            note_match = re.search(r"(\d+(?:\.\d+)?)", gold_note)
            if note_match and row["endpoint_value"]:
                raw_gold_value = float(note_match.group(1))
                ratio = float(row["endpoint_normalized_value"]) / float(row["endpoint_value"])
                gold_value = raw_gold_value * ratio
        label = f"{row['formulation_label']} @ {clean_md_value(str(row['endpoint_time']))}{row['endpoint_time_unit']}"
        rows.append(
            {
                "sample_id": row["sample_id"],
                "doi": row["doi"],
                "label": label,
                "gold_value_ug_cm2": gold_value,
                "pipeline_value_ug_cm2": pipeline_value,
                "is_near": row["gold_endpoint_value_correct"] == "near",
                "note": gold_note,
            }
        )
    return rows


def parse_dataflow_counts(rule_pass_rows: int) -> dict[str, int]:
    route_decisions = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "route_decisions.csv")
    assembled = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "assembled_records.csv")
    v2_rescore = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "v2_rescore" / "verified_records.csv")

    llm_retained = len(route_decisions)
    routed_papers = int((route_decisions["route"] != "unresolved").sum())
    assembled_papers = int(assembled["paper_id"].nunique())
    verified_rows = v2_rescore[v2_rescore["verification_status"] == "verified"].copy()
    verified_papers = int(verified_rows["paper_id"].nunique())

    return {
        "corpus_rows": 1828,
        "rule_pass_rows": rule_pass_rows,
        "rule_filtered_rows": 1828 - rule_pass_rows,
        "llm_retained_rows": llm_retained,
        "llm_dropped_rows": rule_pass_rows - llm_retained,
        "routed_papers": routed_papers,
        "routing_unresolved_rows": int((route_decisions["route"] == "unresolved").sum()),
        "assembled_papers": assembled_papers,
        "no_record_papers": routed_papers - assembled_papers,
        "verified_papers": verified_papers,
        "nonverified_assembled_papers": assembled_papers - verified_papers,
        "verified_records": len(verified_rows),
    }


def parse_failure_heatmap_rows() -> list[dict[str, object]]:
    verified_records = pd.read_csv(ROOT / "outputs" / "full_run_16_post_all_fixes" / "v2_rescore" / "verified_records.csv")
    subset = verified_records[verified_records["verification_status"] != "verified"].copy()
    route_order = ["table", "figure", "mixed", "text"]
    route_totals = {route: int((subset["route"] == route).sum()) for route in route_order}
    reason_by_route: defaultdict[str, Counter[str]] = defaultdict(Counter)
    reason_totals: Counter[str] = Counter()

    for _, row in subset.iterrows():
        route = str(row.get("route", ""))
        if route not in route_order:
            continue
        raw = row.get("failure_reasons_json")
        reasons: list[str] = []
        if isinstance(raw, str) and raw.strip():
            try:
                reasons = json.loads(raw)
            except json.JSONDecodeError:
                reasons = []
        for reason in reasons:
            reason_by_route[reason][route] += 1
            reason_totals[reason] += 1

    top_reasons = [reason for reason, _ in reason_totals.most_common(10)]
    rows: list[dict[str, object]] = []
    for reason in top_reasons:
        for route in route_order:
            count = int(reason_by_route[reason][route])
            route_total = route_totals[route]
            rows.append(
                {
                    "reason": reason,
                    "route": route,
                    "count": count,
                    "pct_of_route": 100.0 * count / route_total if route_total else 0.0,
                    "route_total": route_total,
                    "reason_total": int(reason_totals[reason]),
                }
            )
    return rows


def parse_waterfall_rows() -> list[dict[str, object]]:
    sequence = [
        ("Baseline", "validation_observability_run", "starting point"),
        ("Fix 1", "validation_observability_run_fix1", "tiered search"),
        ("Fix 2", "validation_observability_run_fix2", "calibration gate"),
        ("Fix 3a", "validation_observability_run_fix3a", "subplot contract"),
        ("Fix 4", "validation_observability_run_fix4", "mapping gate"),
        ("Fix 5", "validation_observability_run_fix5", "VLM grounding"),
    ]
    rows: list[dict[str, object]] = []
    previous: int | None = None
    for step, dirname, detail in sequence:
        report_path = ROOT / "outputs" / dirname / "report" / "run_report.md"
        text = read_text(report_path)
        verified = int(require_match(r"Actually verified: `(\d+)`", text, f"{step} verified").group(1))
        rows.append(
            {
                "step": step,
                "detail": detail,
                "verified": verified,
                "delta_from_previous": 0 if previous is None else verified - previous,
                "run_dir": dirname,
            }
        )
        previous = verified
    return rows


def sum_usage(summary: dict[str, object]) -> dict[str, int]:
    usage = summary.get("llm_usage") or {}
    if not isinstance(usage, dict):
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0}
    return {
        "input_tokens": sum(int(stage.get("input_tokens") or 0) for stage in usage.values() if isinstance(stage, dict)),
        "output_tokens": sum(int(stage.get("output_tokens") or 0) for stage in usage.values() if isinstance(stage, dict)),
        "total_tokens": sum(int(stage.get("total_tokens") or 0) for stage in usage.values() if isinstance(stage, dict)),
        "requests": sum(int(stage.get("requests") or 0) for stage in usage.values() if isinstance(stage, dict)),
    }


def estimate_cost_usd(provider: str, model: str, input_tokens: int, output_tokens: int) -> float | None:
    prices = TOKEN_PRICE_USD_PER_MILLION.get((provider, model))
    if not prices:
        return None
    input_price, output_price = prices
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def estimate_summary_cost_usd(provider: str, summary: dict[str, object]) -> tuple[float | None, list[str]]:
    usage = summary.get("llm_usage") or {}
    if not isinstance(usage, dict):
        return None, []
    total = 0.0
    unknown_models: set[str] = set()
    for stage_usage in usage.values():
        if not isinstance(stage_usage, dict):
            continue
        model = str(stage_usage.get("model_name") or "")
        input_tokens = int(stage_usage.get("input_tokens") or 0)
        output_tokens = int(stage_usage.get("output_tokens") or 0)
        cost = estimate_cost_usd(provider, model, input_tokens, output_tokens)
        if cost is None:
            unknown_models.add(model)
            continue
        total += cost
    return total, sorted(model for model in unknown_models if model)


def parse_v2_verified_count(run_dir: Path) -> int:
    summary_path = run_dir / "v2_rescore" / "summary.json"
    if summary_path.exists():
        summary = json.loads(read_text(summary_path))
        status_counts = summary.get("status_counts") or summary.get("verification_status_counts") or {}
        if isinstance(status_counts, dict) and "verified" in status_counts:
            return int(status_counts["verified"])
    verified_path = run_dir / "v2_rescore" / "verified_records.csv"
    if verified_path.exists():
        frame = pd.read_csv(verified_path)
        return int((frame["verification_status"] == "verified").sum())
    return 0


def parse_resource_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    modular_specs = [
        {
            "method": "Modular pipeline (GPT)",
            "run_dir": ROOT / "outputs" / "full_run_16_post_all_fixes",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "scope": "Full corpus",
            "verified_count": None,
        },
        {
            "method": "Modular pipeline (GPT-5.4)",
            "run_dir": ROOT / "outputs" / "experiment_E2_gpt54",
            "provider": "openai",
            "model": "gpt-5.4-mini + gpt-5.4 VLM",
            "scope": "Full corpus (historical E2)",
            "verified_count": 4,
        },
        {
            "method": "Modular pipeline (Claude)",
            "run_dir": ROOT / "outputs" / "experiment_E3_claude_v2",
            "provider": "anthropic",
            "model": "claude-sonnet-4-6",
            "scope": "Full corpus",
            "verified_count": None,
        },
    ]
    for spec in modular_specs:
        summary = json.loads(read_text(spec["run_dir"] / "long_run" / "summary.json"))
        usage = sum_usage(summary)
        assembled_path = spec["run_dir"] / "assembled_records.csv"
        assembled_count = len(pd.read_csv(assembled_path)) if assembled_path.exists() else ""
        cost, unknown_models = estimate_summary_cost_usd(str(spec["provider"]), summary)
        cost_basis = "estimated from configured provider/model token rates"
        if unknown_models:
            cost_basis = f"partial estimate; no encoded token rate for {', '.join(unknown_models)}"
        rows.append(
            {
                "method": spec["method"],
                "scope": spec["scope"],
                "provider": spec["provider"],
                "model": spec["model"],
                "successful_papers": "",
                "records_emitted": assembled_count,
                "verified_or_covered_tp": (
                    spec["verified_count"]
                    if spec["verified_count"] is not None
                    else parse_v2_verified_count(spec["run_dir"])
                ),
                "requests": usage["requests"],
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "total_tokens": usage["total_tokens"],
                "elapsed_seconds": float(summary.get("elapsed_seconds") or 0.0),
                "elapsed_minutes": float(summary.get("elapsed_seconds") or 0.0) / 60.0,
                "cost_usd": cost,
                "cost_basis": cost_basis,
                "source": str((spec["run_dir"] / "long_run" / "summary.json").relative_to(ROOT)),
            }
        )

    single_pass_specs = [
        ("SP-1 text", ROOT / "outputs" / "experiment_single_pass", "openai", "gpt-4o-mini"),
        ("SP-2 PDF", ROOT / "outputs" / "experiment_single_pass_pdf_4omini", "openai", "gpt-4o-mini"),
        ("SP-3 PDF", ROOT / "outputs" / "experiment_single_pass_pdf_gpt54", "openai", "gpt-5.4-mini"),
        ("SP-4 PDF", ROOT / "outputs" / "experiment_single_pass_pdf_claude", "anthropic", "claude-sonnet-4-6"),
    ]
    for method, run_dir, provider, model in single_pass_specs:
        summary = json.loads(read_text(run_dir / "summary.json"))
        usage = summary.get("actual_usage") or summary.get("usage") or {}
        status_counts = summary.get("run_status_counts") or summary.get("status_counts") or {}
        successful = int(status_counts.get("ok", 0)) if isinstance(status_counts, dict) else ""
        cost = summary.get("actual_cost_usd") or summary.get("estimated_actual_cost_usd")
        rows.append(
            {
                "method": method,
                "scope": "Round2 DOI subset",
                "provider": provider,
                "model": model,
                "successful_papers": successful,
                "records_emitted": int(summary.get("raw_records") or summary.get("single_pass_records") or 0),
                "verified_or_covered_tp": int(summary.get("covered_gold_tp") or 0),
                "requests": successful,
                "input_tokens": int(usage.get("input_tokens") or 0),
                "output_tokens": int(usage.get("output_tokens") or 0),
                "total_tokens": int(usage.get("total_tokens") or 0),
                "elapsed_seconds": "",
                "elapsed_minutes": "",
                "cost_usd": cost,
                "cost_basis": "actual/estimated cost stored in single-pass summary",
                "source": str((run_dir / "summary.json").relative_to(ROOT)),
            }
        )
    return rows


def load_metrics() -> PaperMetrics:
    corpus_rows, rule_pass_rows, gpt_assembled, claude_assembled = parse_baseline_metrics()
    llm_retained, assembled_route_counts, extractor_output_counts, v2_status_counts = parse_gpt_run_counts()
    gpt_policy_verified, claude_policy_verified = parse_policy_verified()
    (
        gpt_policy_precision,
        round2_rows,
        v2_e2e_precision,
        unresolved_sample_size,
        unresolved_false_negatives,
        rejected_sample_size,
        rejected_correct,
    ) = parse_gold_metrics()
    claude_policy_precision = parse_claude_policy_precision()
    single_pass_rows, pipeline_cost = parse_single_pass_metrics()
    (
        reproducibility_runs_v1,
        reproducibility_runs_v2,
        reproducibility_v1_mean,
        reproducibility_v1_sd,
        reproducibility_v1_cv,
        reproducibility_v2_mean,
        reproducibility_v2_sd,
        reproducibility_v2_cv,
        stable_v2_core,
    ) = parse_reproducibility_metrics()
    experiment_verified = parse_experiment_verified()
    experiment_verified["Baseline v1"] = gpt_policy_verified["v1"]
    experiment_verified["Baseline v2"] = gpt_policy_verified["v2"]
    experiment_verified["E3 v2"] = claude_policy_verified["v2"]
    dataflow_counts = parse_dataflow_counts(rule_pass_rows)

    return PaperMetrics(
        corpus_rows=corpus_rows,
        rule_pass_rows=rule_pass_rows,
        gpt_assembled=gpt_assembled,
        claude_assembled=claude_assembled,
        llm_retained=llm_retained,
        assembled_route_counts=assembled_route_counts,
        extractor_output_counts=extractor_output_counts,
        v2_status_counts=v2_status_counts,
        gpt_policy_verified=gpt_policy_verified,
        claude_policy_verified=claude_policy_verified,
        gpt_policy_precision=gpt_policy_precision,
        claude_policy_precision=claude_policy_precision,
        round2_rows=round2_rows,
        v2_e2e_precision=v2_e2e_precision,
        unresolved_sample_size=unresolved_sample_size,
        unresolved_false_negatives=unresolved_false_negatives,
        rejected_sample_size=rejected_sample_size,
        rejected_correct=rejected_correct,
        single_pass_rows=single_pass_rows,
        pipeline_cost_usd=pipeline_cost,
        reproducibility_runs_v1=reproducibility_runs_v1,
        reproducibility_runs_v2=reproducibility_runs_v2,
        reproducibility_v1_mean=reproducibility_v1_mean,
        reproducibility_v1_sd=reproducibility_v1_sd,
        reproducibility_v1_cv=reproducibility_v1_cv,
        reproducibility_v2_mean=reproducibility_v2_mean,
        reproducibility_v2_sd=reproducibility_v2_sd,
        reproducibility_v2_cv=reproducibility_v2_cv,
        stable_v2_core=stable_v2_core,
        experiment_verified=experiment_verified,
        comparability_rows=parse_demo_metrics(),
        value_accuracy_rows=parse_value_accuracy_rows(),
        dataflow_counts=dataflow_counts,
        failure_heatmap_rows=parse_failure_heatmap_rows(),
        waterfall_rows=parse_waterfall_rows(),
        resource_rows=parse_resource_rows(),
    )


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUTPUT_DIR / f"{stem}.pdf")
    fig.savefig(OUTPUT_DIR / f"{stem}.png")
    plt.close(fig)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_table_evaluation_summary(metrics: PaperMetrics) -> None:
    rows = [
        {"metric": "Corpus rows", "value": metrics.corpus_rows, "source": "reports/baseline_definition.md"},
        {"metric": "Rule-pass rows", "value": metrics.rule_pass_rows, "source": "reports/baseline_definition.md"},
        {"metric": "GPT assembled records", "value": metrics.gpt_assembled, "source": "reports/baseline_definition.md"},
        {"metric": "Claude assembled records", "value": metrics.claude_assembled, "source": "reports/baseline_definition.md"},
        {
            "metric": "GPT verified under extended policy",
            "value": metrics.gpt_policy_verified["v2"],
            "source": "reports/policy_sensitivity_analysis.md",
        },
        {
            "metric": "Claude verified under extended policy",
            "value": metrics.claude_policy_verified["v2"],
            "source": "reports/policy_sensitivity_analysis.md",
        },
        {"metric": "Round 2 annotation rows", "value": metrics.round2_rows, "source": "reports/gold_evaluation_round2.md"},
        {
            "metric": "Extended-policy keep-record precision (%)",
            "value": metrics.gpt_policy_precision["v2"],
            "source": "reports/gold_evaluation_round2.md",
        },
        {
            "metric": "Extended-policy end-to-end precision (%)",
            "value": metrics.v2_e2e_precision,
            "source": "reports/gold_evaluation_round2.md",
        },
        {
            "metric": "Unresolved false negatives",
            "value": f"{metrics.unresolved_false_negatives}/{metrics.unresolved_sample_size}",
            "source": "reports/gold_evaluation_round2.md",
        },
        {
            "metric": "Correct rejections",
            "value": f"{metrics.rejected_correct}/{metrics.rejected_sample_size}",
            "source": "reports/gold_evaluation_round2.md",
        },
    ]
    write_csv(OUTPUT_DIR / "table_evaluation_summary.csv", ["metric", "value", "source"], rows)


def build_table_single_pass(metrics: PaperMetrics) -> None:
    rows = []
    for row in metrics.single_pass_rows:
        rows.append(
            {
                "method": SINGLE_PASS_DISPLAY[row["method"]].replace("\n", " "),
                "input_mode": row["input_mode"],
                "model": row["model"],
                "gold_tp_coverage_num": row["coverage_num"],
                "gold_tp_coverage_pct": row["coverage_pct"],
                "value_correct_num": row["value_num"],
                "value_correct_pct": row["value_pct"],
                "cost_usd": row["cost_usd"],
                "source": (
                    "outputs/experiment_single_pass/single_pass_vs_pipeline_comparison.md"
                    if row["method"] == "Pipeline"
                    else "reports/single_pass_architecture_comparison.md"
                ),
            }
        )
    write_csv(
        OUTPUT_DIR / "table_single_pass.csv",
        [
            "method",
            "input_mode",
            "model",
            "gold_tp_coverage_num",
            "gold_tp_coverage_pct",
            "value_correct_num",
            "value_correct_pct",
            "cost_usd",
            "source",
        ],
        rows,
    )


def build_table_reproducibility(metrics: PaperMetrics) -> None:
    rows = [
        {
            "scope": "Strict policy verified",
            "mean": metrics.reproducibility_v1_mean,
            "sd": metrics.reproducibility_v1_sd,
            "cv_pct": metrics.reproducibility_v1_cv,
            "runs": ",".join(str(value) for value in metrics.reproducibility_runs_v1),
            "source": "reports/reproducibility_analysis.md",
        },
        {
            "scope": "Extended policy verified",
            "mean": metrics.reproducibility_v2_mean,
            "sd": metrics.reproducibility_v2_sd,
            "cv_pct": metrics.reproducibility_v2_cv,
            "runs": ",".join(str(value) for value in metrics.reproducibility_runs_v2),
            "source": "reports/reproducibility_analysis.md",
        },
        {
            "scope": "Extended-policy stable core",
            "mean": metrics.stable_v2_core,
            "sd": 0.0,
            "cv_pct": 0.0,
            "runs": ",".join(str(metrics.stable_v2_core) for _ in metrics.reproducibility_runs_v2),
            "source": "reports/reproducibility_analysis.md",
        },
    ]
    write_csv(OUTPUT_DIR / "table_reproducibility.csv", ["scope", "mean", "sd", "cv_pct", "runs", "source"], rows)


def build_table_policy_sensitivity(metrics: PaperMetrics) -> None:
    rows = []
    for policy in ["v1", "v2", "v3", "v4"]:
        rows.append(
            {
                "policy": POLICY_LABELS[policy],
                "gpt_verified": metrics.gpt_policy_verified[policy],
                "gpt_precision_pct": metrics.gpt_policy_precision[policy],
                "claude_verified": metrics.claude_policy_verified[policy],
                "claude_precision_pct": metrics.claude_policy_precision[policy],
                "source_verified": "reports/policy_sensitivity_analysis.md",
                "source_precision": "reports/gold_evaluation_round2.md; outputs/claude_gold_audit/claude_per_policy_precision.csv",
            }
        )
    write_csv(
        OUTPUT_DIR / "table_policy_sensitivity.csv",
        [
            "policy",
            "gpt_verified",
            "gpt_precision_pct",
            "claude_verified",
            "claude_precision_pct",
            "source_verified",
            "source_precision",
        ],
        rows,
    )


def build_table_condition_comparability(metrics: PaperMetrics) -> None:
    write_csv(
        OUTPUT_DIR / "table_condition_comparability.csv",
        ["dimension", "paper1", "literature", "match_symbol", "match_label", "extracted"],
        metrics.comparability_rows,
    )


def build_table_resource_comparison(metrics: PaperMetrics) -> None:
    write_csv(
        OUTPUT_DIR / "table_resource_comparison.csv",
        [
            "method",
            "scope",
            "provider",
            "model",
            "successful_papers",
            "records_emitted",
            "verified_or_covered_tp",
            "requests",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "elapsed_seconds",
            "elapsed_minutes",
            "cost_usd",
            "cost_basis",
            "source",
        ],
        metrics.resource_rows,
    )


def build_figf_data(metrics: PaperMetrics) -> None:
    write_csv(
        OUTPUT_DIR / "figF_value_accuracy_data.csv",
        ["sample_id", "doi", "label", "gold_value_ug_cm2", "pipeline_value_ug_cm2", "is_near", "note"],
        metrics.value_accuracy_rows,
    )


def build_figa_sankey_data(metrics: PaperMetrics) -> None:
    rows = [
        {"stage": "Corpus", "node": "Corpus rows", "count": metrics.dataflow_counts["corpus_rows"]},
        {"stage": "Rule pre-filter", "node": "Rule pass", "count": metrics.dataflow_counts["rule_pass_rows"]},
        {"stage": "Rule pre-filter", "node": "Filtered out", "count": metrics.dataflow_counts["rule_filtered_rows"]},
        {"stage": "Full-text triage", "node": "Retained", "count": metrics.dataflow_counts["llm_retained_rows"]},
        {"stage": "Full-text triage", "node": "Dropped", "count": metrics.dataflow_counts["llm_dropped_rows"]},
        {"stage": "Routing", "node": "Routeable papers", "count": metrics.dataflow_counts["routed_papers"]},
        {"stage": "Routing", "node": "Routing unresolved", "count": metrics.dataflow_counts["routing_unresolved_rows"]},
        {"stage": "Assembly", "node": "Assembled papers", "count": metrics.dataflow_counts["assembled_papers"]},
        {"stage": "Assembly", "node": "No extracted record", "count": metrics.dataflow_counts["no_record_papers"]},
        {"stage": "Verified output", "node": "Verified papers", "count": metrics.dataflow_counts["verified_papers"]},
        {
            "stage": "Verified output",
            "node": "No verified output",
            "count": metrics.dataflow_counts["nonverified_assembled_papers"],
        },
    ]
    write_csv(OUTPUT_DIR / "figA_sankey_data.csv", ["stage", "node", "count"], rows)


def build_figg_heatmap_data(metrics: PaperMetrics) -> None:
    write_csv(
        OUTPUT_DIR / "figG_failure_heatmap_data.csv",
        ["reason", "route", "count", "pct_of_route", "route_total", "reason_total"],
        metrics.failure_heatmap_rows,
    )


def build_figh_radar_data(metrics: PaperMetrics) -> None:
    pipeline_row = next(row for row in metrics.single_pass_rows if row["method"] == "Pipeline")
    sp3_row = next(row for row in metrics.single_pass_rows if row["method"] == "SP-3")
    pipeline_tp_per_dollar = 25.0 / metrics.pipeline_cost_usd
    sp3_tp_per_dollar = 24.0 / float(sp3_row["cost_usd"])
    rows = [
        {
            "metric": "TP coverage",
            "pipeline_score": float(pipeline_row["coverage_pct"]),
            "sp3_score": float(sp3_row["coverage_pct"]),
            "definition": "Gold keep-record recovery",
        },
        {
            "metric": "Value recovery",
            "pipeline_score": float(pipeline_row["value_pct"]),
            "sp3_score": float(sp3_row["value_pct"]),
            "definition": "Value-correct recovery on gold-positive rows",
        },
        {
            "metric": "Output purity",
            "pipeline_score": 100.0,
            "sp3_score": 100.0 * 24.0 / 288.0,
            "definition": "True positives divided by emitted output records",
        },
        {
            "metric": "Negative-space control",
            "pipeline_score": 100.0,
            "sp3_score": 100.0 * (1.0 - 18.0 / 27.0),
            "definition": "One minus gold-negative DOI with output rate",
        },
        {
            "metric": "Cost efficiency",
            "pipeline_score": 100.0,
            "sp3_score": 100.0 * sp3_tp_per_dollar / pipeline_tp_per_dollar,
            "definition": "TP per USD, normalized to pipeline = 100",
        },
    ]
    write_csv(OUTPUT_DIR / "figH_radar_data.csv", ["metric", "pipeline_score", "sp3_score", "definition"], rows)


def build_figi_waterfall_data(metrics: PaperMetrics) -> None:
    write_csv(
        OUTPUT_DIR / "figI_waterfall_data.csv",
        ["step", "detail", "verified", "delta_from_previous", "run_dir"],
        metrics.waterfall_rows,
    )


def add_callout(ax: plt.Axes, x: float, y: float, text: str) -> None:
    ax.text(
        x,
        y,
        text,
        ha="left",
        va="center",
        fontsize=6.7,
        color=COLORS["dark_gray"],
        bbox={"boxstyle": "round,pad=0.28", "facecolor": "#F6F6F6", "edgecolor": "#DDDDDD", "linewidth": 0.5},
    )


def draw_ribbon(
    ax: plt.Axes,
    x0: float,
    left_top: float,
    left_bottom: float,
    x1: float,
    right_top: float,
    right_bottom: float,
    color: str,
    alpha: float = 0.72,
) -> None:
    ctrl = (x1 - x0) * 0.38
    verts = [
        (x0, left_top),
        (x0 + ctrl, left_top),
        (x1 - ctrl, right_top),
        (x1, right_top),
        (x1, right_bottom),
        (x1 - ctrl, right_bottom),
        (x0 + ctrl, left_bottom),
        (x0, left_bottom),
        (x0, left_top),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    patch = patches.PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", alpha=alpha)
    ax.add_patch(patch)


def pretty_reason(reason: str) -> str:
    return textwrap.fill(reason.replace("_", " "), width=18)


def plot_pipeline_architecture(metrics: PaperMetrics) -> None:
    counts = metrics.dataflow_counts
    fig, ax = plt.subplots(figsize=(DOUBLE_COL_IN, 3.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    x_positions = [0.06, 0.22, 0.38, 0.54, 0.70, 0.86]
    bar_w = 0.028
    gap = 0.02
    top = 0.86
    bottom = 0.14
    stage_span = top - bottom

    stages = [
        [("Corpus rows", counts["corpus_rows"], COLORS["llm_blue"])],
        [("Filtered out", counts["rule_filtered_rows"], COLORS["light_gray"]), ("Rule pass", counts["rule_pass_rows"], COLORS["light_blue"])],
        [("LLM drop", counts["llm_dropped_rows"], COLORS["light_gray"]), ("Retained", counts["llm_retained_rows"], COLORS["llm_blue"])],
        [
            ("Routing unresolved", counts["routing_unresolved_rows"], COLORS["light_gray"]),
            ("Routeable papers", counts["routed_papers"], COLORS["extract_green"]),
        ],
        [("No extracted record", counts["no_record_papers"], COLORS["light_gray"]), ("Assembled papers", counts["assembled_papers"], COLORS["verify_orange"])],
        [
            ("No verified output", counts["nonverified_assembled_papers"], COLORS["light_gray"]),
            ("Verified papers", counts["verified_papers"], COLORS["output_blue"]),
        ],
    ]
    stage_titles = ["Corpus", "Rule pre-filter", "Full-text triage", "Routing", "Assembly", "Verified output"]
    layouts: list[list[dict[str, float | str | int]]] = []
    for stage in stages:
        weights = [math.sqrt(max(item[1], 1)) for item in stage]
        available = stage_span - gap * (len(stage) - 1)
        weight_total = sum(weights)
        current_top = top
        entries: list[dict[str, float | str | int]] = []
        for (label, count, color), weight in zip(stage, weights):
            height = available * weight / weight_total
            entry = {
                "label": label,
                "count": count,
                "color": color,
                "top": current_top,
                "bottom": current_top - height,
                "center": current_top - height / 2.0,
            }
            entries.append(entry)
            current_top -= height + gap
        layouts.append(entries)

    # corpus -> rule pre-filter
    corpus = layouts[0][0]
    corpus_total = counts["corpus_rows"]
    filtered_height = (float(corpus["top"]) - float(corpus["bottom"])) * counts["rule_filtered_rows"] / corpus_total
    filtered_src = (float(corpus["top"]), float(corpus["top"]) - filtered_height)
    pass_src = (float(filtered_src[1]), float(corpus["bottom"]))
    draw_ribbon(ax, x_positions[0] + bar_w, filtered_src[0], filtered_src[1], x_positions[1], float(layouts[1][0]["top"]), float(layouts[1][0]["bottom"]), COLORS["light_gray"], alpha=0.55)
    draw_ribbon(ax, x_positions[0] + bar_w, pass_src[0], pass_src[1], x_positions[1], float(layouts[1][1]["top"]), float(layouts[1][1]["bottom"]), COLORS["light_blue"], alpha=0.72)

    # rule pass -> triage retained / dropped
    rule_pass = layouts[1][1]
    rule_pass_total = counts["rule_pass_rows"]
    triage_drop_height = (float(rule_pass["top"]) - float(rule_pass["bottom"])) * counts["llm_dropped_rows"] / rule_pass_total
    triage_drop_src = (float(rule_pass["top"]), float(rule_pass["top"]) - triage_drop_height)
    triage_keep_src = (float(triage_drop_src[1]), float(rule_pass["bottom"]))
    draw_ribbon(ax, x_positions[1] + bar_w, triage_drop_src[0], triage_drop_src[1], x_positions[2], float(layouts[2][0]["top"]), float(layouts[2][0]["bottom"]), COLORS["light_gray"], alpha=0.55)
    draw_ribbon(ax, x_positions[1] + bar_w, triage_keep_src[0], triage_keep_src[1], x_positions[2], float(layouts[2][1]["top"]), float(layouts[2][1]["bottom"]), COLORS["llm_blue"], alpha=0.72)

    # retained -> routing unresolved / routeable papers
    retained = layouts[2][1]
    retained_total = counts["llm_retained_rows"]
    routing_drop_height = (float(retained["top"]) - float(retained["bottom"])) * counts["routing_unresolved_rows"] / retained_total
    routing_drop_src = (float(retained["top"]), float(retained["top"]) - routing_drop_height)
    routed_src = (float(routing_drop_src[1]), float(retained["bottom"]))
    draw_ribbon(ax, x_positions[2] + bar_w, routing_drop_src[0], routing_drop_src[1], x_positions[3], float(layouts[3][0]["top"]), float(layouts[3][0]["bottom"]), COLORS["light_gray"], alpha=0.55)
    draw_ribbon(ax, x_positions[2] + bar_w, routed_src[0], routed_src[1], x_positions[3], float(layouts[3][1]["top"]), float(layouts[3][1]["bottom"]), COLORS["extract_green"], alpha=0.78)

    # routeable papers -> assembled / no record
    routeable = layouts[3][1]
    routeable_total = counts["routed_papers"]
    no_record_height = (float(routeable["top"]) - float(routeable["bottom"])) * counts["no_record_papers"] / routeable_total
    no_record_src = (float(routeable["top"]), float(routeable["top"]) - no_record_height)
    assembled_src = (float(no_record_src[1]), float(routeable["bottom"]))
    draw_ribbon(ax, x_positions[3] + bar_w, no_record_src[0], no_record_src[1], x_positions[4], float(layouts[4][0]["top"]), float(layouts[4][0]["bottom"]), COLORS["light_gray"], alpha=0.55)
    draw_ribbon(ax, x_positions[3] + bar_w, assembled_src[0], assembled_src[1], x_positions[4], float(layouts[4][1]["top"]), float(layouts[4][1]["bottom"]), COLORS["verify_orange"], alpha=0.78)

    # assembled papers -> verified / not verified
    assembled = layouts[4][1]
    assembled_total = counts["assembled_papers"]
    no_verified_height = (float(assembled["top"]) - float(assembled["bottom"])) * counts["nonverified_assembled_papers"] / assembled_total
    no_verified_src = (float(assembled["top"]), float(assembled["top"]) - no_verified_height)
    verified_src = (float(no_verified_src[1]), float(assembled["bottom"]))
    draw_ribbon(ax, x_positions[4] + bar_w, no_verified_src[0], no_verified_src[1], x_positions[5], float(layouts[5][0]["top"]), float(layouts[5][0]["bottom"]), COLORS["light_gray"], alpha=0.55)
    draw_ribbon(ax, x_positions[4] + bar_w, verified_src[0], verified_src[1], x_positions[5], float(layouts[5][1]["top"]), float(layouts[5][1]["bottom"]), COLORS["output_blue"], alpha=0.85)

    for xpos, title, stage_layout in zip(x_positions, stage_titles, layouts):
        ax.text(xpos + bar_w / 2, 0.93, title, ha="center", va="bottom", fontsize=7.3, color=COLORS["dark_gray"], fontweight="bold")
        for entry in stage_layout:
            rect = patches.FancyBboxPatch(
                (xpos, float(entry["bottom"])),
                bar_w,
                float(entry["top"]) - float(entry["bottom"]),
                boxstyle="round,pad=0.001,rounding_size=0.004",
                linewidth=0.6,
                facecolor=str(entry["color"]),
                edgecolor="white",
            )
            ax.add_patch(rect)
            count = int(entry["count"])
            label = str(entry["label"])
            y = float(entry["center"])
            if label == "Verified papers":
                text = f"Verified papers\n{count}\n({counts['verified_records']} records)"
            else:
                text = f"{label}\n{count}"
            ha = "left"
            x_text = xpos + bar_w + 0.008
            ax.text(x_text, y, text, ha=ha, va="center", fontsize=6.6, color=COLORS["dark_gray"])

    ax.text(
        0.01,
        0.02,
        "Labels show exact counts. The final node is paper-level, with verified record count shown in parentheses.",
        ha="left",
        va="bottom",
        fontsize=6.5,
        color=COLORS["dark_gray"],
    )
    ax.set_title("Corpus-to-verified dataflow", pad=8, loc="left")
    save_figure(fig, "figA_pipeline_architecture")


def plot_experiment_comparison(metrics: PaperMetrics) -> None:
    experiments = [
        ("Baseline strict", metrics.experiment_verified["Baseline v1"], COLORS["input_gray"]),
        ("Baseline extended", metrics.experiment_verified["Baseline v2"], COLORS["output_blue"]),
        ("GPT-5.4", metrics.experiment_verified["E2"], COLORS["llm_blue"]),
        ("Claude", metrics.experiment_verified["E3 v2"], COLORS["purple"]),
        ("CV-only", metrics.experiment_verified["E4"], COLORS["extract_green"]),
        ("No patching", metrics.experiment_verified["E6"], COLORS["verify_orange"]),
        ("No promotion", metrics.experiment_verified["E7"], COLORS["teal"]),
        ("Relaxed scope", metrics.experiment_verified["E8"], COLORS["red"]),
    ]
    fig, ax = plt.subplots(figsize=(SINGLE_COL_IN, 2.8))
    x = list(range(len(experiments)))
    ax.bar(x, [value for _, value, _ in experiments], color=[color for _, _, color in experiments], width=0.72)
    ax.axhline(metrics.experiment_verified["Baseline v2"], color=COLORS["dark_gray"], linestyle="--", linewidth=0.8)
    ax.text(
        len(experiments) - 0.35,
        metrics.experiment_verified["Baseline v2"] + 0.5,
        "Baseline extended = 25",
        ha="right",
        va="bottom",
        fontsize=7,
        color=COLORS["dark_gray"],
    )
    for xpos, (_, value, _) in zip(x, experiments):
        ax.text(xpos, value + 0.4, str(value), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([label for label, _, _ in experiments], rotation=35, ha="right")
    ax.set_ylabel("Verified records")
    ax.set_ylim(0, 28)
    ax.set_title("Experiment Comparison", loc="left")
    save_figure(fig, "figB_experiment_comparison")


def plot_single_pass_comparison(metrics: PaperMetrics) -> None:
    rows = metrics.single_pass_rows
    labels = ["Pipeline", "SP-1", "SP-2", "SP-3", "SP-4"]
    coverage = [float(row["coverage_pct"]) for row in rows]
    cost = [float(row["cost_usd"]) for row in rows]
    colors = [COLORS["output_blue"], COLORS["light_gray"], COLORS["light_gray"], COLORS["extract_green"], COLORS["red"]]

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COL_IN, 2.8), constrained_layout=True)
    axes[0].bar(labels, coverage, color=colors, width=0.7)
    axes[0].set_ylabel("Gold TP coverage (%)")
    axes[0].set_ylim(0, 110)
    axes[0].set_title("Coverage", loc="left", fontsize=8.5, fontweight="bold")
    for xpos, value in enumerate(coverage):
        y_text = value + 2.0 if value > 0 else 2.0
        axes[0].text(xpos, y_text, f"{value:.0f}%", ha="center", va="bottom", fontsize=6.9)

    axes[1].bar(labels, cost, color=colors, width=0.7)
    axes[1].set_ylabel("Cost (USD)")
    axes[1].set_ylim(0, 4.6)
    axes[1].set_title("Cost", loc="left", fontsize=8.5, fontweight="bold")
    for xpos, value in enumerate(cost):
        prefix = "~" if rows[xpos]["method"] == "Pipeline" else ""
        axes[1].text(xpos, value + 0.08, f"{prefix}${value:.2f}", ha="center", va="bottom", fontsize=6.9)

    fig.suptitle("Single-Pass vs Modular Pipeline", x=0.02, ha="left", fontsize=9, fontweight="bold")
    save_figure(fig, "figC_single_pass_comparison")


def plot_policy_sensitivity(metrics: PaperMetrics) -> None:
    policies = ["v1", "v2", "v3", "v4"]
    x = list(range(len(policies)))
    width = 0.34
    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(SINGLE_COL_IN * 1.25, 4.8),
        gridspec_kw={"height_ratios": [2.2, 1.4], "hspace": 0.08},
    )

    gpt_vals = [metrics.gpt_policy_verified[policy] for policy in policies]
    claude_vals = [metrics.claude_policy_verified[policy] for policy in policies]
    precision_vals = [metrics.gpt_policy_precision[policy] for policy in policies]
    claude_precision_vals = [metrics.claude_policy_precision[policy] for policy in policies]

    ax_top.bar([value - width / 2 for value in x], gpt_vals, width=width, color=COLORS["output_blue"], label="GPT")
    ax_top.bar([value + width / 2 for value in x], claude_vals, width=width, color=COLORS["purple"], label="Claude")
    for xpos, gpt, claude in zip(x, gpt_vals, claude_vals):
        ax_top.text(xpos - width / 2, gpt + 1.0, str(gpt), ha="center", va="bottom", fontsize=6.9)
        ax_top.text(xpos + width / 2, claude + 1.0, str(claude), ha="center", va="bottom", fontsize=6.9)
    ax_top.set_ylabel("Verified records")
    ax_top.set_ylim(0, 60)
    ax_top.set_title("Policy Sensitivity", loc="left")
    ax_top.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2)

    ax_bottom.plot(
        x,
        precision_vals,
        color=COLORS["output_blue"],
        marker="o",
        linewidth=1.5,
        markersize=4.2,
        label="GPT precision",
    )
    ax_bottom.plot(
        x,
        claude_precision_vals,
        color=COLORS["purple"],
        marker="^",
        linestyle="--",
        linewidth=1.3,
        markersize=4.2,
        label="Claude precision",
    )
    for xpos, precision in zip(x, precision_vals):
        ax_bottom.text(xpos, precision + 3.0, f"{precision:.1f}%", ha="center", va="bottom", fontsize=6.8, color=COLORS["output_blue"])
    ax_bottom.annotate(
        "Precision elbow",
        xy=(1, precision_vals[1]),
        xytext=(1.55, 103),
        fontsize=6.8,
        color=COLORS["dark_gray"],
        arrowprops={"arrowstyle": "->", "color": COLORS["dark_gray"], "linewidth": 0.7},
    )
    ax_bottom.legend(loc="lower left")
    ax_bottom.set_ylabel("Precision (%)")
    ax_bottom.set_ylim(0, 110)
    ax_bottom.set_xticks(x)
    ax_bottom.set_xticklabels([POLICY_SHORT_LABELS[policy] for policy in policies])
    save_figure(fig, "figD_policy_sensitivity")


def plot_reproducibility(metrics: PaperMetrics) -> None:
    totals = metrics.reproducibility_runs_v2
    stable = [metrics.stable_v2_core for _ in totals]
    variable = [total - metrics.stable_v2_core for total in totals]
    x = list(range(len(REPRO_RUN_LABELS)))

    fig, ax = plt.subplots(figsize=(SINGLE_COL_IN, 2.9))
    ax.bar(x, stable, color=COLORS["output_blue"], width=0.7, label="Stable core")
    ax.bar(x, variable, bottom=stable, color=COLORS["light_blue"], width=0.7, label="Variable component")
    ax.scatter(x, totals, color=COLORS["dark_gray"], s=16, zorder=3)
    ax.axhline(metrics.stable_v2_core, color=COLORS["dark_gray"], linestyle="--", linewidth=0.8)
    for xpos, total in zip(x, totals):
        ax.text(xpos, total + 0.4, str(total), ha="center", va="bottom", fontsize=7)
    ax.text(
        0.98,
        0.93,
        f"Mean {metrics.reproducibility_v2_mean:.2f} ± {metrics.reproducibility_v2_sd:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7,
        color=COLORS["dark_gray"],
    )
    ax.set_xticks(x)
    ax.set_xticklabels(REPRO_RUN_LABELS)
    ax.set_ylabel("Verified records\n(extended policy)")
    ax.set_ylim(0, 36)
    ax.set_title("Reproducibility Across 5 Runs", loc="left")
    ax.legend(loc="upper left", frameon=False)
    save_figure(fig, "figE_reproducibility")


def compute_accuracy_metrics(rows: list[dict[str, object]]) -> tuple[float, float, float]:
    gold = pd.Series([float(row["gold_value_ug_cm2"]) for row in rows], dtype=float)
    pred = pd.Series([float(row["pipeline_value_ug_cm2"]) for row in rows], dtype=float)
    errors = pred - gold
    mae = float(errors.abs().mean())
    rmse = math.sqrt(float((errors.pow(2)).mean()))
    ss_res = float((errors.pow(2)).sum())
    ss_tot = float(((gold - gold.mean()).pow(2)).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return r2, rmse, mae


def plot_value_accuracy(metrics: PaperMetrics) -> tuple[float, float, float]:
    rows = metrics.value_accuracy_rows
    r2, rmse, mae = compute_accuracy_metrics(rows)
    gold = [float(row["gold_value_ug_cm2"]) for row in rows]
    pred = [float(row["pipeline_value_ug_cm2"]) for row in rows]
    near_mask = [bool(row["is_near"]) for row in rows]
    max_axis = max(max(gold), max(pred)) * 1.06

    fig, ax = plt.subplots(figsize=(SINGLE_COL_IN, 3.2))
    ax.scatter(
        [value for value, near in zip(gold, near_mask) if not near],
        [value for value, near in zip(pred, near_mask) if not near],
        color=COLORS["output_blue"],
        s=20,
        alpha=0.9,
    )
    ax.scatter(
        [value for value, near in zip(gold, near_mask) if near],
        [value for value, near in zip(pred, near_mask) if near],
        color=COLORS["verify_orange"],
        s=28,
        alpha=0.95,
    )
    ax.plot([0, max_axis], [0, max_axis], linestyle="--", linewidth=0.8, color=COLORS["dark_gray"])
    near_points = [row for row in rows if row["is_near"]]
    if near_points:
        near_row = near_points[0]
        ax.annotate(
            "Figure 11 gel",
            xy=(near_row["gold_value_ug_cm2"], near_row["pipeline_value_ug_cm2"]),
            xytext=(near_row["gold_value_ug_cm2"] * 0.56, near_row["pipeline_value_ug_cm2"] * 1.05),
            fontsize=6.8,
            color=COLORS["verify_orange"],
            arrowprops={"arrowstyle": "->", "color": COLORS["verify_orange"], "linewidth": 0.7},
        )
    ax.text(
        0.04,
        0.96,
        f"R² = {r2:.3f}\nRMSE = {rmse:.1f} μg/cm²\nMAE = {mae:.1f} μg/cm²",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=6.9,
        color=COLORS["dark_gray"],
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#DDDDDD", "linewidth": 0.5},
    )
    ax.set_xlim(0, max_axis)
    ax.set_ylim(0, max_axis)
    ax.set_xlabel("Gold standard value (normalized, μg/cm²)")
    ax.set_ylabel("SkinMiner extracted value (normalized, μg/cm²)")
    ax.set_title("Extraction Value Accuracy", loc="left")
    save_figure(fig, "figF_value_accuracy")
    return r2, rmse, mae


def plot_failure_heatmap(metrics: PaperMetrics) -> None:
    rows = metrics.failure_heatmap_rows
    route_order = ["table", "figure", "mixed", "text"]
    reason_order = []
    seen = set()
    for row in rows:
        reason = str(row["reason"])
        if reason not in seen:
            seen.add(reason)
            reason_order.append(reason)

    count_matrix = []
    pct_matrix = []
    route_totals = {route: 0 for route in route_order}
    for row in rows:
        route_totals[str(row["route"])] = int(row["route_total"])
    for reason in reason_order:
        count_row = []
        pct_row = []
        for route in route_order:
            match = next(item for item in rows if item["reason"] == reason and item["route"] == route)
            count_row.append(int(match["count"]))
            pct_row.append(float(match["pct_of_route"]))
        count_matrix.append(count_row)
        pct_matrix.append(pct_row)

    fig, ax = plt.subplots(figsize=(DOUBLE_COL_IN, 3.8))
    image = ax.imshow(pct_matrix, cmap="YlOrRd", aspect="auto", vmin=0, vmax=max(max(row) for row in pct_matrix))
    ax.set_xticks(range(len(route_order)))
    ax.set_xticklabels([f"{route.title()}\n(n={route_totals[route]})" for route in route_order])
    ax.set_yticks(range(len(reason_order)))
    ax.set_yticklabels([pretty_reason(reason) for reason in reason_order])
    for y_index, count_row in enumerate(count_matrix):
        for x_index, count in enumerate(count_row):
            pct = pct_matrix[y_index][x_index]
            text_color = "white" if pct >= 40 else COLORS["dark_gray"]
            ax.text(x_index, y_index, str(count), ha="center", va="center", fontsize=6.8, color=text_color)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02)
    colorbar.set_label("% of route-specific non-verified records", fontsize=7)
    ax.set_title("Failure taxonomy by route (GPT baseline, v2)", loc="left")
    ax.text(
        1.01,
        -0.12,
        "Cell text = count",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.5,
        color=COLORS["dark_gray"],
    )
    save_figure(fig, "figG_failure_heatmap")


def plot_pipeline_vs_single_pass_radar(metrics: PaperMetrics) -> None:
    radar_rows = pd.read_csv(OUTPUT_DIR / "figH_radar_data.csv")
    labels = radar_rows["metric"].tolist()
    pipeline_scores = radar_rows["pipeline_score"].tolist()
    sp3_scores = radar_rows["sp3_score"].tolist()
    angles = [index / len(labels) * 2 * math.pi for index in range(len(labels))]
    angles += angles[:1]
    pipeline_scores += pipeline_scores[:1]
    sp3_scores += sp3_scores[:1]

    fig = plt.figure(figsize=(SINGLE_COL_IN * 1.18, 3.45))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([textwrap.fill(label, width=14) for label in labels], fontsize=7)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], fontsize=6.5, color=COLORS["dark_gray"])
    ax.set_ylim(0, 100)
    ax.grid(color="#DDDDDD", linewidth=0.6)

    ax.plot(angles, pipeline_scores, color=COLORS["output_blue"], linewidth=1.6, label="Modular pipeline (v2)")
    ax.fill(angles, pipeline_scores, color=COLORS["output_blue"], alpha=0.12)
    ax.plot(angles, sp3_scores, color=COLORS["extract_green"], linewidth=1.6, label="Best single-pass (SP-3)")
    ax.fill(angles, sp3_scores, color=COLORS["extract_green"], alpha=0.14)

    ax.set_title("Pipeline vs best single-pass", loc="left", pad=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2)
    fig.text(
        0.02,
        0.02,
        "Purity = TP / emitted output. Negative-space control = 1 - gold-negative DOI with output rate.",
        ha="left",
        va="bottom",
        fontsize=6.4,
        color=COLORS["dark_gray"],
    )
    save_figure(fig, "figH_pipeline_vs_singlepass_radar")


def plot_fix_waterfall(metrics: PaperMetrics) -> None:
    rows = metrics.waterfall_rows
    labels = [row["step"] for row in rows]
    verified = [int(row["verified"]) for row in rows]
    deltas = [int(row["delta_from_previous"]) for row in rows]
    fig, ax = plt.subplots(figsize=(DOUBLE_COL_IN * 0.9, 3.0))

    x_positions = list(range(len(rows) + 1))
    baseline_color = COLORS["llm_blue"]
    final_color = COLORS["output_blue"]
    positive_color = COLORS["soft_green"]
    negative_color = COLORS["soft_orange"]

    ax.bar(x_positions[0], verified[0], color=baseline_color, width=0.72)
    ax.text(x_positions[0], verified[0] + 0.25, str(verified[0]), ha="center", va="bottom", fontsize=7)

    cumulative = verified[0]
    connector_positions = [verified[0]]
    for index, delta in enumerate(deltas[1:], start=1):
        start_value = cumulative
        end_value = cumulative + delta
        bottom = min(start_value, end_value)
        height = abs(delta)
        color = positive_color if delta >= 0 else negative_color
        ax.bar(x_positions[index], height, bottom=bottom, color=color, width=0.72)
        ax.text(
            x_positions[index],
            max(start_value, end_value) + 0.25,
            f"{delta:+d}",
            ha="center",
            va="bottom",
            fontsize=7,
            color=COLORS["dark_gray"],
        )
        ax.plot([x_positions[index - 1] + 0.36, x_positions[index] - 0.36], [start_value, start_value], color="#BBBBBB", linewidth=0.8)
        cumulative = end_value
        connector_positions.append(cumulative)

    ax.bar(x_positions[-1], cumulative, color=final_color, width=0.72)
    ax.text(x_positions[-1], cumulative + 0.25, str(cumulative), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels + ["Final"])
    ax.set_ylabel("Verified records")
    ax.set_ylim(0, max(verified) + 4)
    ax.set_title("Fix contribution waterfall", loc="left")
    ax.text(
        0.99,
        0.97,
        "Validation subset, v1 strict",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.7,
        color=COLORS["dark_gray"],
    )
    save_figure(fig, "figI_fix_waterfall")


def main() -> None:
    configure_style()
    ensure_output_dir()
    metrics = load_metrics()
    build_table_evaluation_summary(metrics)
    build_table_single_pass(metrics)
    build_table_reproducibility(metrics)
    build_table_policy_sensitivity(metrics)
    build_table_condition_comparability(metrics)
    build_table_resource_comparison(metrics)
    build_figa_sankey_data(metrics)
    build_figf_data(metrics)
    build_figg_heatmap_data(metrics)
    build_figh_radar_data(metrics)
    build_figi_waterfall_data(metrics)
    plot_pipeline_architecture(metrics)
    plot_experiment_comparison(metrics)
    plot_single_pass_comparison(metrics)
    plot_policy_sensitivity(metrics)
    plot_reproducibility(metrics)
    plot_value_accuracy(metrics)
    plot_failure_heatmap(metrics)
    plot_pipeline_vs_single_pass_radar(metrics)
    plot_fix_waterfall(metrics)


if __name__ == "__main__":
    main()
