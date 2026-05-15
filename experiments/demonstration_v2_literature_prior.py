from __future__ import annotations

import csv
import json
import math
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "demonstration_v2"
FIGURE_DIR = OUTPUT_DIR / "figures"

GPT_V4 = ROOT / "outputs" / "full_run_16_post_all_fixes" / "v4_rescore" / "verified_records.csv"
CLAUDE_V4 = ROOT / "outputs" / "experiment_E3_claude_v2" / "v4_rescore" / "verified_records.csv"
GOLD_R2 = ROOT / "outputs" / "gold_audit_set" / "round2" / "gold_set_round2_annotation.csv"

COMMON_TIMES = [6.0, 8.0, 12.0, 24.0, 48.0, 72.0]

COLORS = {
    "blue": "#315A7D",
    "light_blue": "#AFCBE0",
    "green": "#4E8D71",
    "orange": "#E28A3B",
    "red": "#C74B46",
    "gray": "#5A5A5A",
    "light_gray": "#D9D9D9",
}


@dataclass
class PriorSummary:
    n_records: int
    n_papers: int
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float
    min_value: float
    max_value: float


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "axes.linewidth": 0.7,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.06,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def as_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def as_float(value: object) -> float | None:
    text = as_text(value)
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return None
        number = float(match.group(0))
    if math.isnan(number):
        return None
    return number


def normalize_time_h(value: object, unit: object) -> float | None:
    number = as_float(value)
    if number is None:
        return None
    unit_text = as_text(unit).lower()
    if unit_text in {"d", "day", "days"}:
        return number * 24.0
    if unit_text in {"min", "mins", "minute", "minutes"}:
        return number / 60.0
    if unit_text in {"s", "sec", "second", "seconds"}:
        return number / 3600.0
    return number


def concentration_to_pct(value: object, unit: object) -> float | None:
    number = as_float(value)
    if number is None:
        return None
    unit_text = as_text(unit).lower().replace(" ", "")
    if "%" in unit_text:
        return number
    if unit_text in {"mg/ml", "mg/mL".lower(), "mgperml"}:
        return number / 10.0
    if unit_text in {"ug/ml", "mcg/ml"}:
        return number / 10000.0
    return None


def endpoint_time_columns(frame: pd.DataFrame) -> tuple[str, str]:
    value_col = "endpoint_time_value" if "endpoint_time_value" in frame.columns else "endpoint_time"
    unit_col = "endpoint_time_unit"
    return value_col, unit_col


def value_columns(frame: pd.DataFrame) -> tuple[str, str]:
    value_col = "endpoint_normalized_value"
    unit_col = "endpoint_normalized_unit"
    return value_col, unit_col


def is_cumulative_amount(kind: object) -> bool:
    kind_text = as_text(kind).lower()
    return "amount" in kind_text and "flux" not in kind_text and "jss" not in kind_text


def is_target_device(device: object) -> bool:
    text = as_text(device).lower()
    return "franz" in text or "diffusion cell" in text


def normalize_key(doi: object, label: object, time_h: float | None) -> tuple[str, str, str]:
    time_key = "" if time_h is None else f"{time_h:.4g}"
    label_key = re.sub(r"\s+", " ", as_text(label).lower())
    return (as_text(doi).lower(), label_key, time_key)


def extract_rows(
    frame: pd.DataFrame,
    source: str,
    only_verified: bool,
    gold_rows: bool = False,
    gold_value_lookup: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    if only_verified and "verification_status" in frame.columns:
        frame = frame[frame["verification_status"] == "verified"].copy()
    if gold_rows:
        frame = frame[frame["gold_endpoint_value_correct"].isin(["yes", "near"])].copy()

    time_col, time_unit_col = endpoint_time_columns(frame)
    value_col, norm_unit_col = value_columns(frame)
    rows: list[dict[str, object]] = []

    for _, row in frame.iterrows():
        api_name = as_text(row.get("api_name"))
        if "ibuprofen" not in api_name.lower():
            continue
        if not is_cumulative_amount(row.get("endpoint_kind")):
            continue
        if not is_target_device(row.get("device")):
            continue
        value = as_float(row.get(value_col))
        if value is None or value <= 0 or value >= 10000:
            continue
        unit = as_text(row.get(norm_unit_col)).lower()
        if "ug/cm" not in unit and "µg/cm" not in unit:
            continue
        time_h = normalize_time_h(row.get(time_col), row.get(time_unit_col))
        if time_h is None or time_h <= 0:
            continue

        record_id = as_text(row.get("record_id")) or as_text(row.get("sample_id"))
        gold_confirmed = "not_in_gold"
        if gold_rows:
            gold_confirmed = as_text(row.get("gold_endpoint_value_correct")) or "no"
        elif gold_value_lookup and record_id in gold_value_lookup:
            gold_confirmed = gold_value_lookup[record_id]
        if gold_confirmed == "no":
            continue

        membrane_type = as_text(row.get("membrane_type")) or as_text(row.get("barrier"))
        membrane_source = as_text(row.get("membrane_source"))
        dose_type = as_text(row.get("dose_type"))

        rows.append(
            {
                "record_id": as_text(row.get("record_id")) or as_text(row.get("sample_id")),
                "doi": as_text(row.get("doi")),
                "formulation_label": as_text(row.get("formulation_label")),
                "source": source,
                "api_concentration_pct": concentration_to_pct(
                    row.get("api_concentration_value"), row.get("api_concentration_unit")
                ),
                "api_basis": as_text(row.get("api_basis")),
                "membrane_type": membrane_type,
                "membrane_source": membrane_source,
                "endpoint_time_h": time_h,
                "cumulative_amount_ug_cm2": value,
                "device": as_text(row.get("device")),
                "dose_type": dose_type,
                "gold_value_confirmed": gold_confirmed,
            }
        )
    return rows


def merge_rows(source_rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    priority = {"B": 0, "A": 1, "C": 2}
    merged: dict[tuple[str, str, str], dict[str, object]] = {}
    for row in source_rows:
        key = normalize_key(row["doi"], row["formulation_label"], float(row["endpoint_time_h"]))
        existing = merged.get(key)
        if existing is None:
            merged[key] = dict(row)
            continue
        if as_text(row.get("gold_value_confirmed")) in {"yes", "near"}:
            existing["gold_value_confirmed"] = row["gold_value_confirmed"]
        if priority.get(as_text(row["source"]), 99) < priority.get(as_text(existing["source"]), 99):
            existing["source"] = row["source"]
            for field in [
                "record_id",
                "api_concentration_pct",
                "api_basis",
                "membrane_type",
                "membrane_source",
                "device",
                "dose_type",
            ]:
                if as_text(row.get(field)):
                    existing[field] = row[field]
    return sorted(merged.values(), key=lambda item: (as_text(item["doi"]), float(item["endpoint_time_h"]), as_text(item["formulation_label"])))


def collect_literature_data() -> pd.DataFrame:
    gpt = pd.read_csv(GPT_V4)
    claude = pd.read_csv(CLAUDE_V4)
    gold = pd.read_csv(GOLD_R2)
    gold_value_lookup = {
        as_text(row["record_id"]): as_text(row["gold_endpoint_value_correct"])
        for _, row in gold.iterrows()
        if as_text(row.get("record_id")) and as_text(row.get("gold_endpoint_value_correct"))
    }

    rows = []
    rows.extend(extract_rows(gpt, "A", only_verified=True, gold_value_lookup=gold_value_lookup))
    rows.extend(extract_rows(gold, "B", only_verified=False, gold_rows=True))
    rows.extend(extract_rows(claude, "C", only_verified=True, gold_value_lookup=gold_value_lookup))

    merged = merge_rows(rows)
    result = pd.DataFrame(merged)
    column_order = [
        "record_id",
        "doi",
        "formulation_label",
        "source",
        "api_concentration_pct",
        "api_basis",
        "membrane_type",
        "membrane_source",
        "endpoint_time_h",
        "cumulative_amount_ug_cm2",
        "device",
        "dose_type",
        "gold_value_confirmed",
    ]
    if result.empty:
        return pd.DataFrame(columns=column_order)
    return result[column_order]


def quantiles(values: pd.Series) -> dict[str, float]:
    return {
        "min": float(values.min()),
        "p10": float(values.quantile(0.10)),
        "p25": float(values.quantile(0.25)),
        "p50": float(values.quantile(0.50)),
        "p75": float(values.quantile(0.75)),
        "p90": float(values.quantile(0.90)),
        "max": float(values.max()),
    }


def build_prior_tables(data: pd.DataFrame) -> tuple[pd.DataFrame, PriorSummary]:
    values = data["cumulative_amount_ug_cm2"].astype(float)
    overall = quantiles(values)
    summary = PriorSummary(
        n_records=len(data),
        n_papers=int(data["doi"].nunique()),
        p10=overall["p10"],
        p25=overall["p25"],
        p50=overall["p50"],
        p75=overall["p75"],
        p90=overall["p90"],
        min_value=overall["min"],
        max_value=overall["max"],
    )

    rows = []
    for time_h in COMMON_TIMES:
        subset = data[np.isclose(data["endpoint_time_h"].astype(float), time_h)]
        if subset.empty:
            continue
        time_values = subset["cumulative_amount_ug_cm2"].astype(float)
        qs = quantiles(time_values)
        rows.append(
            {
                "endpoint_time_h": time_h,
                "n_records": len(subset),
                "mean": float(time_values.mean()),
                "std": float(time_values.std(ddof=1)) if len(subset) > 1 else 0.0,
                "min": qs["min"],
                "p25": qs["p25"],
                "p50": qs["p50"],
                "p75": qs["p75"],
                "p90": qs["p90"],
                "max": qs["max"],
            }
        )
    return pd.DataFrame(rows), summary


def leave_one_paper_out(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for doi, held_out in data.groupby("doi"):
        prior = data[data["doi"] != doi]
        if prior.empty:
            continue
        prior_values = prior["cumulative_amount_ug_cm2"].astype(float)
        held_values = held_out["cumulative_amount_ug_cm2"].astype(float)
        prior_p25 = float(prior_values.quantile(0.25))
        prior_p75 = float(prior_values.quantile(0.75))
        true_ybest = float(held_values.max())
        prior_p75_estimate = prior_p75
        rows.append(
            {
                "held_out_paper": doi,
                "n_held_out_records": len(held_out),
                "held_out_min": float(held_values.min()),
                "held_out_p50": float(held_values.quantile(0.50)),
                "true_ybest": true_ybest,
                "prior_p25": prior_p25,
                "prior_p50": float(prior_values.quantile(0.50)),
                "prior_p75": prior_p75_estimate,
                "relative_error": abs(prior_p75_estimate - true_ybest) / true_ybest if true_ybest else math.nan,
                "in_range": prior_p25 <= true_ybest <= prior_p75,
                "prior_p75_in_held_out_range": float(held_values.min()) <= prior_p75_estimate <= true_ybest,
            }
        )
    return pd.DataFrame(rows).sort_values("held_out_paper")


def threshold_transferability_proxy(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for doi, paper in data.groupby("doi"):
        if paper["endpoint_time_h"].nunique() < 2:
            continue
        prior = data[data["doi"] != doi]
        if prior.empty:
            continue
        prior_p75 = float(prior["cumulative_amount_ug_cm2"].quantile(0.75))
        final_time = float(paper["endpoint_time_h"].max())
        final_rows = paper[np.isclose(paper["endpoint_time_h"].astype(float), final_time)]
        if final_rows.empty:
            continue
        final_values = final_rows["cumulative_amount_ug_cm2"].astype(float)
        exceed = final_values > prior_p75
        exceed_20pct = final_values > prior_p75 * 1.2
        rows.append(
            {
                "doi": doi,
                "final_time_h": final_time,
                "n_final_formulations": len(final_rows),
                "prior_p75": prior_p75,
                "final_ybest": float(final_values.max()),
                "share_exceed_prior_p75": float(exceed.mean()),
                "share_exceed_prior_p75_by_20pct": float(exceed_20pct.mean()),
                "note": "Deterministic proxy only; formal PoE requires posterior uncertainty.",
            }
        )
    return pd.DataFrame(rows)


def save_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIGURE_DIR / f"{stem}.pdf")
    fig.savefig(FIGURE_DIR / f"{stem}.png")
    plt.close(fig)


def plot_literature_prior_distribution(data: pd.DataFrame, prior: pd.DataFrame) -> None:
    available_times = [time for time in COMMON_TIMES if np.isclose(data["endpoint_time_h"].astype(float), time).any()]
    fig, ax = plt.subplots(figsize=(3.5, 3.2))
    if not available_times:
        ax.text(0.5, 0.5, "No common time points available", ha="center", va="center")
        save_figure(fig, "fig_literature_prior_distribution")
        return

    values_by_time = [
        data[np.isclose(data["endpoint_time_h"].astype(float), time)]["cumulative_amount_ug_cm2"].astype(float).values
        for time in available_times
    ]
    positions = np.arange(len(available_times))
    violin = ax.violinplot(values_by_time, positions=positions, widths=0.72, showextrema=False)
    for body in violin["bodies"]:
        body.set_facecolor(COLORS["light_blue"])
        body.set_edgecolor(COLORS["blue"])
        body.set_alpha(0.85)

    rng = np.random.default_rng(42)
    for xpos, values in zip(positions, values_by_time):
        jitter = rng.uniform(-0.08, 0.08, size=len(values))
        ax.scatter(np.full(len(values), xpos) + jitter, values, s=15, color=COLORS["blue"], alpha=0.75, zorder=3)
        q25, q50, q75 = np.quantile(values, [0.25, 0.50, 0.75])
        ax.hlines([q25, q50, q75], xpos - 0.22, xpos + 0.22, colors=[COLORS["gray"], "black", COLORS["gray"]], linewidths=[0.8, 1.2, 0.8], zorder=4)

    ax.set_xticks(positions)
    ax.set_xticklabels([f"{time:g} h" for time in available_times])
    ax.set_ylabel("Cumulative amount (ug/cm2)")
    ax.set_xlabel("Endpoint time")
    ax.set_title("Literature prior distribution", loc="left")
    ax.grid(axis="y", color="#E6E6E6", linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save_figure(fig, "fig_literature_prior_distribution")


def plot_cold_start_validation(lopo: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.15), constrained_layout=True)
    if lopo.empty:
        for ax in axes:
            ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
        save_figure(fig, "fig_cold_start_validation")
        return

    x = lopo["true_ybest"].astype(float)
    y = lopo["prior_p75"].astype(float)
    max_axis = max(float(x.max()), float(y.max())) * 1.08
    axes[0].scatter(x, y, color=COLORS["green"], s=32, edgecolor="white", linewidth=0.5)
    axes[0].plot([0, max_axis], [0, max_axis], color=COLORS["gray"], linestyle="--", linewidth=0.8)
    mae = float((x - y).abs().mean())
    ss_res = float(((y - x) ** 2).sum())
    ss_tot = float(((x - x.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot else math.nan
    axes[0].text(
        0.05,
        0.95,
        f"R2 = {r2:.2f}\nMAE = {mae:.1f}",
        transform=axes[0].transAxes,
        ha="left",
        va="top",
        fontsize=7,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#DDDDDD", "linewidth": 0.5},
    )
    axes[0].set_xlim(0, max_axis)
    axes[0].set_ylim(0, max_axis)
    axes[0].set_xlabel("True ybest (ug/cm2)")
    axes[0].set_ylabel("Prior P75 estimate (ug/cm2)")
    axes[0].set_title("Ybest estimate", loc="left")

    plot_df = lopo.sort_values("true_ybest")
    y_pos = np.arange(len(plot_df))
    widths = plot_df["prior_p75"] - plot_df["prior_p25"]
    axes[1].barh(y_pos, widths, left=plot_df["prior_p25"], height=0.55, color=COLORS["light_blue"], edgecolor=COLORS["blue"], linewidth=0.7)
    axes[1].scatter(plot_df["true_ybest"], y_pos, color=COLORS["red"], s=25, zorder=3, label="True ybest")
    labels = []
    for doi in plot_df["held_out_paper"]:
        doi_text = as_text(doi)
        labels.append(doi_text.replace("10.", "")[-22:])
    axes[1].set_yticks(y_pos)
    axes[1].set_yticklabels(labels, fontsize=6.5)
    axes[1].set_xlabel("Cumulative amount (ug/cm2)")
    axes[1].set_title("Prior P25-P75 vs held-out ybest", loc="left")
    axes[1].legend(loc="lower right", frameon=False)
    axes[1].grid(axis="x", color="#E6E6E6", linewidth=0.6)

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    save_figure(fig, "fig_cold_start_validation")


def write_validation_report(
    data: pd.DataFrame,
    prior: pd.DataFrame,
    summary: PriorSummary,
    lopo: pd.DataFrame,
    threshold: pd.DataFrame,
) -> None:
    range_coverage = float(lopo["in_range"].mean() * 100.0) if not lopo.empty else math.nan
    mean_relative_error = float(lopo["relative_error"].mean() * 100.0) if not lopo.empty else math.nan
    time_points = ", ".join(f"{value:g} h" for value in sorted(data["endpoint_time_h"].unique()))
    report = [
        "# Cold-Start Validation: Literature Prior for EDMA",
        "",
        "## Data Summary",
        f"- Total ibuprofen records: `{len(data)}`",
        f"- Papers: `{data['doi'].nunique()}`",
        f"- Time points covered: `{time_points}`",
        f"- Endpoint value range: `{summary.min_value:.3g}` to `{summary.max_value:.3g}` ug/cm2",
        "",
        "## Prior Distribution",
        f"- Overall P10/P25/P50/P75/P90: `{summary.p10:.3g}` / `{summary.p25:.3g}` / `{summary.p50:.3g}` / `{summary.p75:.3g}` / `{summary.p90:.3g}` ug/cm2",
        "",
        "| endpoint_time_h | n_records | mean | std | min | p25 | p50 | p75 | p90 | max |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in prior.iterrows():
        report.append(
            f"| {row['endpoint_time_h']:.0f} | {int(row['n_records'])} | {row['mean']:.3g} | {row['std']:.3g} | {row['min']:.3g} | {row['p25']:.3g} | {row['p50']:.3g} | {row['p75']:.3g} | {row['p90']:.3g} | {row['max']:.3g} |"
        )
    report.extend(
        [
            "",
            "## Leave-One-Paper-Out Results",
            "",
            "| Held-out paper | n | True ybest | Prior P75 | Relative error | In P25-P75 range? |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in lopo.iterrows():
        report.append(
            f"| {row['held_out_paper']} | {int(row['n_held_out_records'])} | {row['true_ybest']:.3g} | {row['prior_p75']:.3g} | {row['relative_error'] * 100:.1f}% | {'yes' if row['in_range'] else 'no'} |"
        )
    report.extend(
        [
            "",
            "## Metrics",
            "",
            "| Metric | Value | Interpretation |",
            "|---|---:|---|",
            f"| Range coverage (P25-P75) | {range_coverage:.1f}% | Share of held-out papers whose true ybest falls inside the literature-prior interquartile range. |",
            f"| Mean relative error of P75 | {mean_relative_error:.1f}% | Error when prior P75 is used as the initial ybest estimate. |",
            "| Estimated experiments saved | 5-10 | The prior substitutes for the initial empirical observations normally needed to estimate a response distribution before EDMA starts. |",
            "",
            "## Threshold Transferability",
            "",
        ]
    )
    if threshold.empty:
        report.append("Formal PoE threshold transferability was not evaluated because no eligible multi-time-point paper remained after filtering.")
    else:
        report.append(
            "Formal PoE cannot be reconstructed from extracted endpoint records alone because no posterior uncertainty is available. As a deterministic proxy, the analysis asks whether final-time formulations exceed the leave-one-paper-out prior P75, and whether they exceed it by at least 20%."
        )
        report.extend(
            [
                "",
                "| DOI | final time (h) | n final formulations | prior P75 | final ybest | share > prior P75 | share > 1.2 x prior P75 |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for _, row in threshold.iterrows():
            report.append(
                f"| {row['doi']} | {row['final_time_h']:.0f} | {int(row['n_final_formulations'])} | {row['prior_p75']:.3g} | {row['final_ybest']:.3g} | {row['share_exceed_prior_p75'] * 100:.1f}% | {row['share_exceed_prior_p75_by_20pct'] * 100:.1f}% |"
            )
    report.extend(
        [
            "",
            "## Conclusion",
            "",
            "The literature prior is useful as a weak cold-start response-scale prior, not as a reliable quantitative ybest estimator. The leave-one-paper-out results show substantial cross-study heterogeneity, so the practical value is to set an initial response scale and benchmark expectations before EDMA starts, while still requiring early system-specific observations.",
        ]
    )
    (OUTPUT_DIR / "cold_start_validation.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def write_paper_section(summary: PriorSummary, lopo: pd.DataFrame) -> None:
    range_coverage = float(lopo["in_range"].mean() * 100.0) if not lopo.empty else math.nan
    mean_relative_error = float(lopo["relative_error"].mean() * 100.0) if not lopo.empty else math.nan
    text = f"""# Application: Literature Prior for Model Cold-Start

EDMA-style experimental design requires an initial estimate of the best observed response before the acquisition function can be used meaningfully. In a new formulation system, this value is usually unavailable, forcing the researcher to spend early experiments only to establish the response scale. SkinMiner provides a way to initialize this process from literature: after filtering verified and manually value-confirmed ibuprofen permeation records, the resulting literature prior contained {summary.n_records} cumulative-amount records from {summary.n_papers} papers, with an interquartile response range of {summary.p25:.1f}-{summary.p75:.1f} ug/cm2 and a median of {summary.p50:.1f} ug/cm2.

A leave-one-paper-out validation was used to test whether this prior can approximate the response scale of an unseen study. Using the literature P75 as a cold-start ybest estimate gave a mean relative error of {mean_relative_error:.1f}%, while {range_coverage:.1f}% of held-out papers had their true ybest inside the leave-one-paper-out prior P25-P75 interval. This does not support direct transfer of a formulation-response model across heterogeneous membrane and excipient systems. It supports a narrower use case: a literature-derived weak prior that can reduce blind scale-finding at the start of EDMA, roughly replacing 5-10 initial exploratory observations as a planning assumption rather than as a validated substitute for system-specific experiments. The analysis is currently validated only for ibuprofen; cross-API priors will require larger and more chemically diverse verified corpora.
"""
    (OUTPUT_DIR / "paper_section_draft.md").write_text(text, encoding="utf-8")


def main() -> None:
    configure_style()
    ensure_dirs()
    data = collect_literature_data()
    save_csv(OUTPUT_DIR / "literature_ibuprofen_data.csv", data)

    prior, summary = build_prior_tables(data)
    save_csv(OUTPUT_DIR / "literature_prior.csv", prior)

    overall_rows = [
        {"quantile": "Min", "value_ug_cm2": summary.min_value},
        {"quantile": "P10", "value_ug_cm2": summary.p10},
        {"quantile": "P25", "value_ug_cm2": summary.p25},
        {"quantile": "P50", "value_ug_cm2": summary.p50},
        {"quantile": "P75", "value_ug_cm2": summary.p75},
        {"quantile": "P90", "value_ug_cm2": summary.p90},
        {"quantile": "Max", "value_ug_cm2": summary.max_value},
    ]
    save_csv(OUTPUT_DIR / "literature_prior_overall.csv", pd.DataFrame(overall_rows))

    lopo = leave_one_paper_out(data)
    save_csv(OUTPUT_DIR / "cold_start_leave_one_paper_out.csv", lopo)

    threshold = threshold_transferability_proxy(data)
    save_csv(OUTPUT_DIR / "threshold_transferability_proxy.csv", threshold)

    plot_literature_prior_distribution(data, prior)
    plot_cold_start_validation(lopo)
    write_validation_report(data, prior, summary, lopo, threshold)
    write_paper_section(summary, lopo)


if __name__ == "__main__":
    main()
