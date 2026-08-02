from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
LOOCV_JSON = OUT / "bolla_internal_loocv_results.json"
FEWSHOT_CSV = OUT / "fewshot_summary_table.csv"
X2B_JSON = OUT / "fewshot_xiao_to_bolla_results.json"
B2X_JSON = OUT / "fewshot_bolla_to_xiao_results.json"
FIGURE_REPORT = OUT / "demo2_figure_report.md"

LOOCV_PDF = OUT / "figure_bolla_internal_loocv.pdf"
LOOCV_PNG = OUT / "figure_bolla_internal_loocv.png"
FEWSHOT_PDF = OUT / "figure_fewshot_trajectory.pdf"
FEWSHOT_PNG = OUT / "figure_fewshot_trajectory.png"

LOG10_2 = math.log10(2.0)
REPORT_START = "<!-- SUPPLEMENTARY_FIGURES_START -->"
REPORT_END = "<!-- SUPPLEMENTARY_FIGURES_END -->"

PALETTE = {
    "inside": "#0072B2",
    "outside": "#D55E00",
    "x2b": "#0072B2",
    "b2x": "#D55E00",
    "line": "#111111",
    "fit": "#5F6F7A",
    "band": "#BDBDBD",
    "grid": "#D9D9D9",
}

EXPECTED_LOOCV = {
    "F1A": (0.431, 0.593, 0.162, True),
    "F1B": (0.352, 0.537, 0.185, True),
    "F2A": (0.872, 0.581, 0.291, True),
    "F2B": (0.560, 0.687, 0.127, True),
    "F3": (1.326, 0.945, 0.381, False),
    "F4": (0.732, 1.057, 0.325, False),
    "F5": (0.870, 1.847, 0.977, False),
    "F6": (1.571, 1.400, 0.171, True),
}

EXPECTED_FEWSHOT = {
    "xiao_to_bolla": {
        "k": [0, 1, 2, 3, 4],
        "R2_conv_mean": [-0.32, -0.66, -0.55, -0.47, -0.55],
        "R2_conv_std": [0.00, 0.68, 1.25, 1.58, 2.14],
        "spearman_mean": [0.43, 0.21, 0.21, 0.36, 0.53],
        "spearman_std": [0.00, 0.39, 0.36, 0.41, 0.44],
    },
    "bolla_to_xiao": {
        "k": [0, 1, 2, 4, 8, 12],
        "R2_conv_mean": [-16.0, -9.0, -6.5, -5.0, -4.0, -3.6],
        "R2_conv_std": [0.0, 4.1, 3.4, 2.4, 2.0, 1.9],
        "spearman_mean": [0.07, 0.03, 0.01, 0.00, -0.02, -0.02],
        "spearman_std": [0.00, 0.05, 0.06, 0.08, 0.13, 0.18],
    },
}


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.5,
            "axes.titlesize": 9.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.8,
        }
    )


def read_loocv() -> tuple[list[dict], dict]:
    payload = json.loads(LOOCV_JSON.read_text(encoding="utf-8"))
    ridge = payload["models"]["ridge"]
    rows = ridge["predictions"]
    metrics = ridge["aggregate_metrics"]
    if len(rows) != 8:
        raise ValueError(f"Expected 8 Ridge LOOCV predictions, found {len(rows)}")
    if {row["record_id"] for row in rows} != set(EXPECTED_LOOCV):
        raise ValueError("Bolla LOOCV record IDs differ from the expected eight formulations")
    for row in rows:
        expected = EXPECTED_LOOCV[row["record_id"]]
        actual = (
            float(row["logJ_actual"]),
            float(row["logJ_pred"]),
            float(row["abs_residual"]),
            bool(row["within_2x"]),
        )
        for index in range(3):
            if abs(actual[index] - expected[index]) > 0.0006:
                raise ValueError(
                    f"LOOCV prompt/source mismatch for {row['record_id']} field {index}: "
                    f"source={actual[index]}, prompt={expected[index]}"
                )
        if actual[3] != expected[3]:
            raise ValueError(f"LOOCV within-2x mismatch for {row['record_id']}")
    expected_metrics = {
        "R2_conv": -0.10095816734186136,
        "spearman_rho": 0.5714285714285715,
        "within_2x_count": 5,
    }
    for key, expected in expected_metrics.items():
        if abs(float(metrics[key]) - expected) > 1e-12:
            raise ValueError(f"LOOCV aggregate metric mismatch for {key}")
    return rows, metrics


def mean_std(values: list[float]) -> tuple[float, float]:
    array = np.asarray(values, dtype=float)
    return float(np.mean(array)), float(np.std(array, ddof=0))


def validate_summary_against_json(summary: pd.DataFrame) -> dict:
    sources = {
        "xiao_to_bolla": json.loads(X2B_JSON.read_text(encoding="utf-8")),
        "bolla_to_xiao": json.loads(B2X_JSON.read_text(encoding="utf-8")),
    }
    maximum_difference = 0.0
    cells_compared = 0
    metric_map = {
        "R2_conv": "R2_conv",
        "spearman": "spearman",
        "pearson": "pearson",
        "rmse_logJ": "rmse_logJ",
        "within_2x": "within_2x",
    }
    for direction, records in sources.items():
        direction_summary = summary[summary["direction"] == direction]
        for k_value, k_rows in direction_summary.groupby("k"):
            subset_records = [row for row in records if int(row["k"]) == int(k_value)]
            if len(subset_records) != int(k_rows.iloc[0]["n_subsets"]):
                raise ValueError(f"Subset count mismatch for {direction} k={k_value}")
            for json_key, csv_prefix in metric_map.items():
                values = [float(row[json_key]) for row in subset_records if row[json_key] is not None]
                recomputed_mean, recomputed_std = mean_std(values)
                source_mean = float(k_rows.iloc[0][f"{csv_prefix}_mean"])
                source_std = float(k_rows.iloc[0][f"{csv_prefix}_std"])
                maximum_difference = max(
                    maximum_difference,
                    abs(recomputed_mean - source_mean),
                    abs(recomputed_std - source_std),
                )
                cells_compared += 2
                if abs(recomputed_mean - source_mean) > 5e-12 or abs(recomputed_std - source_std) > 5e-12:
                    raise ValueError(
                        f"Few-shot summary mismatch for {direction} k={k_value} {json_key}: "
                        f"recomputed=({recomputed_mean}, {recomputed_std}), "
                        f"csv=({source_mean}, {source_std})"
                    )
    return {
        "status": "PASS",
        "cells_compared": cells_compared,
        "maximum_absolute_difference": maximum_difference,
    }


def read_fewshot() -> tuple[pd.DataFrame, dict]:
    summary = pd.read_csv(FEWSHOT_CSV)
    expected_columns = {
        "direction",
        "k",
        "n_subsets",
        "R2_conv_mean",
        "R2_conv_std",
        "spearman_mean",
        "spearman_std",
    }
    if not expected_columns.issubset(summary.columns):
        raise ValueError("fewshot_summary_table.csv is missing required columns")
    for direction, expected in EXPECTED_FEWSHOT.items():
        frame = summary[summary["direction"] == direction].sort_values("k")
        if frame["k"].astype(int).tolist() != expected["k"]:
            raise ValueError(f"Unexpected k values for {direction}")
        for metric in ["R2_conv_mean", "R2_conv_std", "spearman_mean", "spearman_std"]:
            source_values = frame[metric].to_numpy(dtype=float)
            expected_values = np.asarray(expected[metric], dtype=float)
            if np.any(np.abs(source_values - expected_values) > 0.055):
                raise ValueError(
                    f"Few-shot prompt/source mismatch for {direction}/{metric}: "
                    f"source={source_values.tolist()}, prompt={expected_values.tolist()}"
                )
    audit = validate_summary_against_json(summary)
    return summary, audit


def make_loocv_figure(rows: list[dict], metrics: dict) -> None:
    configure_matplotlib()
    fig, ax = plt.subplots(figsize=(3.55, 3.55))
    actual = np.array([float(row["logJ_actual"]) for row in rows])
    predicted = np.array([float(row["logJ_pred"]) for row in rows])
    within = np.array([bool(row["within_2x"]) for row in rows])
    low, high = 0.25, 2.02
    grid = np.linspace(low, high, 200)

    ax.fill_between(
        grid,
        grid - LOG10_2,
        grid + LOG10_2,
        color=PALETTE["band"],
        alpha=0.28,
        linewidth=0,
        zorder=0,
    )
    ax.plot(grid, grid, color=PALETTE["line"], linewidth=1.0, zorder=1)

    slope, intercept = np.polyfit(actual, predicted, 1)
    if slope <= 0:
        raise ValueError(f"Expected a positive Bolla LOOCV OLS slope, got {slope}")
    fit_x = np.linspace(float(np.min(actual)), float(np.max(actual)), 100)
    ax.plot(
        fit_x,
        slope * fit_x + intercept,
        color=PALETTE["fit"],
        linewidth=0.9,
        linestyle=(0, (4, 3)),
        alpha=0.60,
        label=f"OLS fit (positive slope, $\\rho$={metrics['spearman_rho']:+.2f})",
        zorder=2,
    )

    ax.scatter(
        actual[within],
        predicted[within],
        s=34,
        marker="o",
        facecolor=PALETTE["inside"],
        edgecolor=PALETTE["line"],
        linewidth=0.6,
        label="within 2x",
        zorder=3,
    )
    ax.scatter(
        actual[~within],
        predicted[~within],
        s=34,
        marker="o",
        facecolor="white",
        edgecolor=PALETTE["outside"],
        linewidth=1.2,
        label="outside 2x",
        zorder=3,
    )

    label_offsets = {
        "F1A": (6, 7),
        "F1B": (5, -12),
        "F2A": (-24, -12),
        "F2B": (6, 7),
        "F3": (6, -12),
        "F4": (-24, 7),
        "F5": (-22, 8),
        "F6": (6, 7),
    }
    for row in rows:
        record_id = str(row["record_id"])
        ax.annotate(
            record_id,
            (row["logJ_actual"], row["logJ_pred"]),
            xytext=label_offsets[record_id],
            textcoords="offset points",
            fontsize=7.2,
            zorder=4,
        )

    f5 = next(row for row in rows if row["record_id"] == "F5")
    ax.annotate(
        "F5: sole 30% ethanol sample\nisolated composition\n$\\rightarrow$ LOOCV extrapolation",
        (f5["logJ_actual"], f5["logJ_pred"]),
        xytext=(1.12, 1.89),
        textcoords="data",
        ha="left",
        va="top",
        fontsize=5.8,
        color="#333333",
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 0.55,
            "color": "#555555",
            "shrinkA": 2,
            "shrinkB": 3,
        },
        zorder=5,
    )

    ax.text(
        0.965,
        0.035,
        "literature internal LOOCV\n"
        "(Ridge, 4-feature)\n"
        f"Spearman $\\rho$ = {metrics['spearman_rho']:+.2f}\n"
        f"R$^2_{{conv}}$ = {metrics['R2_conv']:.2f}\n"
        f"within-2x = {metrics['within_2x_count']}/{metrics['n']}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.2,
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": "#777777",
            "linewidth": 0.55,
            "alpha": 0.94,
        },
    )

    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Measured log$_{10}$ J (literature)")
    ax.set_ylabel("Predicted log$_{10}$ J (literature LOOCV)")
    ax.set_title("Figure S3.A  literature internal LOOCV", loc="left", fontweight="bold", fontsize=8.5, pad=31)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.005),
        ncol=3,
        frameon=False,
        fontsize=5.8,
        handletextpad=0.35,
        columnspacing=0.8,
        borderpad=0.1,
    )
    ax.tick_params(direction="out", length=3, width=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.15, top=0.82)
    fig.savefig(
        LOOCV_PDF,
        metadata={
            "Creator": "SkinMiner Demo 2",
            "Producer": "Matplotlib",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    fig.savefig(LOOCV_PNG, dpi=450)
    plt.close(fig)


def plot_trajectory(
    ax,
    frame: pd.DataFrame,
    mean_col: str,
    std_col: str,
    color: str,
    marker: str,
    label: str,
) -> None:
    ax.errorbar(
        frame["k"].to_numpy(dtype=float),
        frame[mean_col].to_numpy(dtype=float),
        yerr=frame[std_col].to_numpy(dtype=float),
        color=color,
        marker=marker,
        markersize=4.6,
        markerfacecolor="white" if marker == "s" else color,
        markeredgecolor=color,
        markeredgewidth=0.9,
        linewidth=1.0,
        elinewidth=0.7,
        capsize=2.2,
        label=label,
        zorder=3,
    )


def style_trajectory_axis(ax) -> None:
    ax.axhline(0, color="#555555", linewidth=0.7, linestyle=(0, (4, 3)), zorder=1)
    ax.grid(axis="y", color=PALETTE["grid"], linewidth=0.45, zorder=0)
    ax.tick_params(direction="out", length=3, width=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def make_fewshot_figure(summary: pd.DataFrame) -> None:
    configure_matplotlib()
    x2b = summary[summary["direction"] == "xiao_to_bolla"].sort_values("k")
    b2x = summary[summary["direction"] == "bolla_to_xiao"].sort_values("k")

    fig = plt.figure(figsize=(7.1, 3.65))
    outer = fig.add_gridspec(1, 2, width_ratios=[0.92, 1.08], wspace=0.40)
    left = outer[0].subgridspec(2, 1, height_ratios=[1, 1], hspace=0.18)
    ax_a1 = fig.add_subplot(left[0])
    ax_a2 = fig.add_subplot(left[1], sharex=ax_a1)
    ax_b = fig.add_subplot(outer[1])

    plot_trajectory(
        ax_a1,
        x2b,
        "R2_conv_mean",
        "R2_conv_std",
        PALETTE["x2b"],
        "o",
        "in-house $\\rightarrow$ literature",
    )
    ax_a1.set_ylim(-3.0, 1.85)
    ax_a1.set_ylabel("Mean R$^2_{conv}$")
    ax_a1.set_title("A  R$^2_{conv}$ vs k (neither crosses zero)", loc="left", fontweight="bold", pad=6)
    ax_a1.legend(loc="lower left", frameon=False, fontsize=7)
    ax_a1.tick_params(labelbottom=False)
    style_trajectory_axis(ax_a1)

    plot_trajectory(
        ax_a2,
        b2x,
        "R2_conv_mean",
        "R2_conv_std",
        PALETTE["b2x"],
        "s",
        "literature $\\rightarrow$ in-house",
    )
    ax_a2.set_ylim(-20.5, 0.8)
    ax_a2.set_xlabel("k in-domain anchors")
    ax_a2.set_ylabel("Mean R$^2_{conv}$")
    ax_a2.legend(loc="lower right", frameon=False, fontsize=7)
    style_trajectory_axis(ax_a2)

    plot_trajectory(
        ax_b,
        x2b,
        "spearman_mean",
        "spearman_std",
        PALETTE["x2b"],
        "o",
        "in-house $\\rightarrow$ literature",
    )
    plot_trajectory(
        ax_b,
        b2x,
        "spearman_mean",
        "spearman_std",
        PALETTE["b2x"],
        "s",
        "literature $\\rightarrow$ in-house",
    )
    ax_b.set_xlim(-0.45, 12.6)
    ax_b.set_ylim(-0.27, 1.05)
    ax_b.set_xticks([0, 1, 2, 3, 4, 8, 12])
    ax_b.set_xlabel("k in-domain anchors")
    ax_b.set_ylabel("Mean Spearman $\\rho$")
    ax_b.set_title("B  Spearman $\\rho$ vs k", loc="left", fontweight="bold", pad=6)
    ax_b.legend(loc="upper right", frameon=False, fontsize=7)
    style_trajectory_axis(ax_b)

    end_row = b2x.iloc[-1]
    ax_b.annotate(
        "$\\rho$ degrades with k\n(anchors fit in-house noise floor)",
        (float(end_row["k"]), float(end_row["spearman_mean"])),
        xytext=(6.1, 0.23),
        textcoords="data",
        ha="left",
        va="center",
        fontsize=6.8,
        color="#333333",
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 0.55,
            "color": "#555555",
            "shrinkA": 2,
            "shrinkB": 3,
        },
    )
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.88)
    fig.savefig(
        FEWSHOT_PDF,
        metadata={
            "Creator": "SkinMiner Demo 2",
            "Producer": "Matplotlib",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    fig.savefig(FEWSHOT_PNG, dpi=450)
    plt.close(fig)


def supplementary_report_section(loocv_metrics: dict, fewshot_audit: dict) -> str:
    return "\n".join(
        [
            REPORT_START,
            "",
            "## Supplementary Figures for Note S3",
            "",
            "### Figure S3.A: Bolla Internal LOOCV",
            "",
            "Source: `bolla_internal_loocv_results.json`, Ridge predictions only. No modelling was rerun.",
            "",
            f"Source verification: R2_conv={loocv_metrics['R2_conv']:.6f}, "
            f"Spearman rho={loocv_metrics['spearman_rho']:.6f}, "
            f"within-2x={loocv_metrics['within_2x_count']}/{loocv_metrics['n']}.",
            "",
            "**Caption.** Bolla internal LOOCV shows partial ordering recovery "
            f"(Spearman rho={loocv_metrics['spearman_rho']:+.2f}) but no magnitude recovery "
            f"(R2_conv={loocv_metrics['R2_conv']:.2f}). F5, the only Bolla formulation with "
            "30% ethanol, is an isolated composition and produces the dominant LOOCV residual. "
            "Together with n=8 and four input features, this means Bolla is not internally "
            "modellable in a stable sense, although Ridge retains some learnable ordering structure.",
            "",
            "Outputs:",
            "",
            "- `figure_bolla_internal_loocv.pdf`",
            "- `figure_bolla_internal_loocv.png`",
            "",
            "### Figure S3.B: Few-Shot k-Trajectory",
            "",
            "Sources: `fewshot_summary_table.csv`, `fewshot_xiao_to_bolla_results.json`, and "
            "`fewshot_bolla_to_xiao_results.json`. No modelling was rerun.",
            "",
            f"Per-subset reaggregation check: {fewshot_audit['status']}; "
            f"{fewshot_audit['cells_compared']} mean/std cells compared; maximum absolute "
            f"difference={fewshot_audit['maximum_absolute_difference']:.3e}.",
            "",
            "**Caption.** Both R2_conv and Spearman trajectories confirm that adding in-domain "
            "anchors does not recover transfer. The R2_conv scales differ strongly between "
            "directions and are therefore shown on vertically split axes. Xiao-to-Bolla mean "
            "R2_conv remains negative through k=4, while Bolla-to-Xiao remains negative through "
            "k=12. Bolla-to-Xiao Spearman rho drifts from +0.07 toward zero and slightly negative "
            "values as k increases, consistent with anchors fitting the narrow-range Xiao noise "
            "floor rather than recovering transferable structure.",
            "",
            "Outputs:",
            "",
            "- `figure_fewshot_trajectory.pdf`",
            "- `figure_fewshot_trajectory.png`",
            "",
            REPORT_END,
        ]
    )


def update_figure_report(loocv_metrics: dict, fewshot_audit: dict) -> None:
    report = FIGURE_REPORT.read_text(encoding="utf-8")
    if REPORT_START in report:
        before = report.split(REPORT_START, 1)[0].rstrip()
        after = report.split(REPORT_END, 1)[1].lstrip() if REPORT_END in report else ""
        report = before + ("\n\n" + after if after else "")
    section = supplementary_report_section(loocv_metrics, fewshot_audit)
    FIGURE_REPORT.write_text(report.rstrip() + "\n\n" + section + "\n", encoding="utf-8")


def main() -> None:
    loocv_rows, loocv_metrics = read_loocv()
    fewshot_summary, fewshot_audit = read_fewshot()
    make_loocv_figure(loocv_rows, loocv_metrics)
    make_fewshot_figure(fewshot_summary)
    update_figure_report(loocv_metrics, fewshot_audit)

    print("[DEMO2 SUPPLEMENTARY FIGURES] Done")
    print(
        f"LOOCV sanity: R2={loocv_metrics['R2_conv']:.3f} "
        f"rho={loocv_metrics['spearman_rho']:.3f} "
        f"within={loocv_metrics['within_2x_count']}/{loocv_metrics['n']}"
    )
    print(
        f"Few-shot reaggregation: {fewshot_audit['status']} "
        f"max_abs_diff={fewshot_audit['maximum_absolute_difference']:.3e}"
    )
    print(f"Figure S3.A: {LOOCV_PDF}")
    print(f"Figure S3.B: {FEWSHOT_PDF}")
    print(f"Report updated: {FIGURE_REPORT}")


if __name__ == "__main__":
    main()
