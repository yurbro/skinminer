from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).resolve().parent
PANEL_A_CSV = OUT / "transfer_4feature_xiao_to_bolla.csv"
FIG_PDF = OUT / "figure_demo2_main.pdf"
FIG_PNG = OUT / "figure_demo2_main.png"
REPORT = OUT / "demo2_figure_report.md"
LOG10_2 = math.log10(2.0)

PALETTE = {
    "inside": "#0072B2",
    "outside": "#D55E00",
    "band": "#BDBDBD",
    "flag": "#C44E52",
    "compatible": "#C9D3E6",
    "line": "#111111",
    "fit": "#5F6F7A",
}

EXPECTED_PANEL_A = {
    "F1A": (0.431, 1.066, 0),
    "F1B": (0.352, 1.053, 0),
    "F2A": (0.872, 1.117, 1),
    "F2B": (0.560, 1.114, 0),
    "F3": (1.326, 1.150, 1),
    "F4": (0.732, 1.134, 0),
    "F5": (0.870, 0.970, 1),
    "F6": (1.571, 1.114, 0),
}

RED_FLAG_ROWS = [
    {
        "dimension": "Composition paradigm",
        "red_flag": 1,
        "rationale": "different coarse class",
        "grouping": "flagged",
    },
    {
        "dimension": "Diffusion-cell class",
        "red_flag": 1,
        "rationale": "static vs dynamic (different coarse class)",
        "grouping": "flagged",
    },
    {
        "dimension": "Receptor medium",
        "red_flag": 1,
        "rationale": "aqueous vs ethanolic (different coarse class)",
        "grouping": "flagged",
    },
    {
        "dimension": "Donor dose",
        "red_flag": 1,
        "rationale": "30x ratio (>2x threshold)",
        "grouping": "flagged",
    },
    {
        "dimension": "Effective diffusion area",
        "red_flag": 1,
        "rationale": "2.56x ratio (>2x threshold)",
        "grouping": "flagged",
    },
    {
        "dimension": "Run duration",
        "red_flag": 0,
        "rationale": "1.25x ratio (<2x)",
        "grouping": "compatible",
    },
    {
        "dimension": "Active substance",
        "red_flag": 0,
        "rationale": "same molecule and salt form",
        "grouping": "compatible",
    },
    {
        "dimension": "Membrane",
        "red_flag": 0,
        "rationale": "identical (Strat-M)",
        "grouping": "compatible",
    },
]


def read_panel_a_rows() -> list[dict]:
    with PANEL_A_CSV.open(newline="", encoding="utf-8") as handle:
        rows = []
        for row in csv.DictReader(handle):
            record_id = row["record_id"]
            actual = float(row["logJ_actual"])
            pred = float(row["logJ_pred"])
            within = int(row["within_2x"])
            exp_actual, exp_pred, exp_within = EXPECTED_PANEL_A[record_id]
            if abs(actual - exp_actual) > 0.005 or abs(pred - exp_pred) > 0.005 or within != exp_within:
                raise ValueError(
                    f"Panel A coordinate mismatch for {record_id}: "
                    f"got ({actual:.6f}, {pred:.6f}, {within}), "
                    f"expected approx ({exp_actual:.3f}, {exp_pred:.3f}, {exp_within})"
                )
            rows.append(
                {
                    "record_id": record_id,
                    "logJ_actual": actual,
                    "logJ_pred": pred,
                    "within_2x": bool(within),
                }
            )
    if len(rows) != 8:
        raise ValueError(f"Expected 8 Panel A rows, found {len(rows)}")
    return rows


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


def panel_a(ax, rows: list[dict]) -> None:
    x = np.array([row["logJ_actual"] for row in rows], dtype=float)
    y = np.array([row["logJ_pred"] for row in rows], dtype=float)
    within = np.array([row["within_2x"] for row in rows], dtype=bool)
    low, high = 0.30, 1.70
    grid = np.linspace(low, high, 200)

    ax.fill_between(grid, grid - LOG10_2, grid + LOG10_2, color=PALETTE["band"], alpha=0.28, linewidth=0, zorder=0)
    ax.plot(grid, grid, color=PALETTE["line"], linewidth=1.1, zorder=1)

    slope, intercept = np.polyfit(x, y, 1)
    if slope <= 0:
        raise ValueError(f"Expected positive OLS slope for v3.4 Panel A, got {slope}")
    fit_x = np.linspace(float(np.min(x)), float(np.max(x)), 80)
    ax.plot(
        fit_x,
        slope * fit_x + intercept,
        color=PALETTE["fit"],
        linewidth=0.9,
        linestyle=(0, (4, 3)),
        alpha=0.50,
        label="OLS fit (slope > 0)",
        zorder=2,
    )

    ax.scatter(
        x[within],
        y[within],
        s=34,
        marker="o",
        facecolor=PALETTE["inside"],
        edgecolor=PALETTE["line"],
        linewidth=0.6,
        label="within 2x",
        zorder=3,
    )
    ax.scatter(
        x[~within],
        y[~within],
        s=34,
        marker="o",
        facecolor="white",
        edgecolor=PALETTE["outside"],
        linewidth=1.2,
        label="outside 2x",
        zorder=3,
    )

    offsets = {
        "F1A": (0.025, 0.045),
        "F1B": (0.025, -0.045),
        "F2A": (0.030, 0.050),
        "F2B": (0.030, -0.055),
        "F3": (-0.130, -0.035),
        "F4": (0.025, 0.050),
        "F5": (0.025, -0.060),
        "F6": (-0.120, 0.045),
    }
    for row in rows:
        dx, dy = offsets.get(row["record_id"], (0.02, 0.02))
        ax.annotate(
            row["record_id"],
            (row["logJ_actual"], row["logJ_pred"]),
            xytext=(row["logJ_actual"] + dx, row["logJ_pred"] + dy),
            textcoords="data",
            fontsize=7.4,
            ha="left",
            va="center",
            arrowprops={"arrowstyle": "-", "linewidth": 0.35, "color": "#555555", "shrinkA": 2, "shrinkB": 2},
            zorder=4,
        )

    ax.text(
        0.965,
        0.055,
        "in-house $\\rightarrow$ literature (zero-shot, 4-feature)\n"
        "Spearman $\\rho$ = +0.43\n"
        "R$^2_{conv}$ = -0.32\n"
        "within-2x = 3/8",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.8,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#777777", "linewidth": 0.6, "alpha": 0.94},
    )

    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Measured log$_{10}$ J (literature)")
    ax.set_ylabel("Predicted log$_{10}$ J")
    ax.set_title("A  Cross-protocol transfer (in-house $\\rightarrow$ literature)", loc="left", fontweight="bold", pad=7)
    ax.legend(loc="upper left", frameon=False, handletextpad=0.4, borderpad=0.1)
    ax.tick_params(direction="out", length=3, width=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def panel_b(ax) -> None:
    y = np.arange(len(RED_FLAG_ROWS))
    colors = [PALETTE["flag"] if row["red_flag"] else PALETTE["compatible"] for row in RED_FLAG_ROWS]
    edge_colors = ["#333333" if row["red_flag"] else "#555555" for row in RED_FLAG_ROWS]

    ax.barh(y, np.ones(len(RED_FLAG_ROWS)), color=colors, edgecolor=edge_colors, linewidth=0.55, height=0.66)
    ax.axhline(4.5, color="#333333", linewidth=0.7, alpha=0.7)

    for yi, row in zip(y, RED_FLAG_ROWS):
        if row["red_flag"]:
            ax.scatter(0.045, yi, marker="^", s=36, color="white", edgecolor="#333333", linewidth=0.45, zorder=3)
            text_color = "white"
            rationale_x = 0.105
            weight = "bold"
        else:
            ax.scatter(0.045, yi, marker="o", s=28, color="white", edgecolor="#555555", linewidth=0.7, zorder=3)
            text_color = "#222222"
            rationale_x = 0.105
            weight = "normal"
        ax.text(rationale_x, yi, row["rationale"], va="center", ha="left", fontsize=7.3, color=text_color, fontweight=weight)
        ax.text(1.035, yi, str(row["red_flag"]), va="center", ha="left", fontsize=8.2, color="#111111", fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([row["dimension"] for row in RED_FLAG_ROWS])
    for tick, row in zip(ax.get_yticklabels(), RED_FLAG_ROWS):
        if row["red_flag"]:
            tick.set_fontweight("bold")
    ax.invert_yaxis()
    ax.set_xlim(0, 1.13)
    ax.set_xticks([])
    ax.set_xlabel("")
    ax.set_title("B  Protocol-distance red-flag vector", loc="left", fontweight="bold", pad=7)
    ax.text(
        0.0,
        -0.095,
        "Continuous dimensions flagged when source/target ratio > 2x;\n"
        "categorical dimensions flagged when coarse classes differ.\n"
        "5 of 8 dimensions flagged.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=6.35,
        color="#333333",
    )
    ax.tick_params(axis="y", length=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)


def make_figure(panel_a_rows: list[dict]) -> None:
    configure_matplotlib()
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.65, 3.56),
        gridspec_kw={"width_ratios": [1.0, 1.16], "wspace": 0.60},
        constrained_layout=False,
    )
    panel_a(axes[0], panel_a_rows)
    panel_b(axes[1])
    fig.subplots_adjust(left=0.074, right=0.985, bottom=0.20, top=0.88)
    fig.savefig(FIG_PDF)
    fig.savefig(FIG_PNG, dpi=450)
    plt.close(fig)


def make_report(panel_a_rows: list[dict]) -> None:
    lines = [
        "# Demo 2 Figure 3.6.1 Report",
        "",
        "## Data Sources Read",
        "",
        f"- Panel A predictions: `{PANEL_A_CSV.name}`",
        "- Panel B red-flag values: hardcoded binary v3.4 protocol-distance rule from `codex_prompt_demo2_figure_v34.md`",
        "",
        "No modelling was rerun; the figure uses existing 4-feature predictions and the specified binary red-flag vector.",
        "",
        "## Panel A Coordinates Verified Against CSV",
        "",
        "| record_id | logJ_actual | logJ_pred | within_2x |",
        "|---|---:|---:|---:|",
    ]
    for row in panel_a_rows:
        lines.append(f"| {row['record_id']} | {row['logJ_actual']:.12f} | {row['logJ_pred']:.12f} | {int(row['within_2x'])} |")

    lines += [
        "",
        "Headline metrics annotated: Spearman rho = +0.43, R2_conv = -0.32, within-2x = 3/8.",
        "Panel A includes a faint OLS fit line for logJ_pred ~ logJ_actual, clipped to the observed literature x-range.",
        "",
        "## Panel B Red-Flag List",
        "",
        "| dimension | red_flag | rationale | grouping |",
        "|---|---:|---|---|",
    ]
    for row in RED_FLAG_ROWS:
        lines.append(f"| {row['dimension']} | {row['red_flag']} | {row['rationale']} | {row['grouping']} |")

    lines += [
        "",
        "Panel B was redesigned from a continuous protocol-distance bar chart into a categorical red-flag list. No mean line or continuous distance score is shown. Summary: 5 of 8 dimensions flagged.",
        "",
        "## Outputs",
        "",
        f"- `{FIG_PDF.name}`",
        f"- `{FIG_PNG.name}`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel_a_rows = read_panel_a_rows()
    make_figure(panel_a_rows)
    make_report(panel_a_rows)
    within_count = sum(row["within_2x"] for row in panel_a_rows)
    print("[DEMO2 FIGURE V3.4] Done")
    print(f"Panel A source: {PANEL_A_CSV}")
    print(f"Panel A rows={len(panel_a_rows)} within_2x={within_count}/{len(panel_a_rows)}")
    print("Panel B red flags=5/8")
    print(f"PDF: {FIG_PDF}")
    print(f"PNG: {FIG_PNG}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
