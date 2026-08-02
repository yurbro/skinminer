from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
SUMMARY_CSV = OUT / "ratio_sweep_summary.csv"
FIG_PDF = OUT / "figure_ratio_sweep_lines.pdf"
FIG_PNG = OUT / "figure_ratio_sweep_lines.png"
REPORT = OUT / "demo2_figure_report.md"

LIT_VALUES = [0, 2, 4, 6, 8]
N_VALUES = [8, 12, 16, 20, 24]
REPORT_START = "<!-- RATIO_LINES_REDRAW_START -->"
REPORT_END = "<!-- RATIO_LINES_REDRAW_END -->"

LINE_STYLES = {
    0: {
        "color": "#0072B2",
        "linestyle": "-",
        "marker": "o",
        "label": "lit=0 (pure in-house)",
    },
    2: {
        "color": "#56B4E9",
        "linestyle": "-.",
        "marker": "s",
        "label": "lit=2",
    },
    4: {
        "color": "#E69F00",
        "linestyle": "--",
        "marker": "^",
        "label": "lit=4",
    },
    6: {
        "color": "#F4A261",
        "linestyle": "-.",
        "marker": "v",
        "label": "lit=6",
    },
    8: {
        "color": "#D55E00",
        "linestyle": "--",
        "marker": "D",
        "label": "lit=8 (pure literature)",
    },
}


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.5,
            "axes.titlesize": 8.7,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.5,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def read_and_validate_summary() -> pd.DataFrame:
    frame = pd.read_csv(SUMMARY_CSV)
    required = {
        "lit",
        "n",
        "R2_conv_mean",
        "R2_conv_std",
        "spearman_mean",
        "spearman_std",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing ratio-sweep summary columns: {sorted(missing)}")
    if len(frame) != 25:
        raise ValueError(f"Expected 25 summary rows, found {len(frame)}")
    if frame[list(required)].isna().any().any():
        raise ValueError("The plotting columns contain missing values")

    observed = set(zip(frame["lit"].astype(int), frame["n"].astype(int)))
    expected = {(lit, n) for lit in LIT_VALUES for n in N_VALUES}
    if observed != expected:
        raise ValueError(
            f"Unexpected ratio grid: missing={sorted(expected-observed)}, "
            f"extra={sorted(observed-expected)}"
        )
    if frame.duplicated(["lit", "n"]).any():
        raise ValueError("Duplicate (lit, n) cells in ratio_sweep_summary.csv")
    return frame.sort_values(["lit", "n"]).reset_index(drop=True)


def marginal_value_per_literature_record(frame: pd.DataFrame) -> float:
    changes: list[float] = []
    for n in N_VALUES:
        section = frame.loc[frame["n"] == n].sort_values("lit")
        means = section["R2_conv_mean"].to_numpy(dtype=float)
        changes.extend(((means[1:] - means[:-1]) / 2.0).tolist())
    if len(changes) != 20:
        raise RuntimeError(f"Expected 20 adjacent marginal changes, found {len(changes)}")
    return float(np.mean(changes))


def draw_series(
    axis: plt.Axes,
    x: np.ndarray,
    mean: np.ndarray,
    std: np.ndarray,
    style: dict,
) -> Line2D:
    axis.fill_between(
        x,
        mean - std,
        mean + std,
        color=style["color"],
        alpha=0.17,
        linewidth=0,
        interpolate=True,
        zorder=1,
    )
    (line,) = axis.plot(
        x,
        mean,
        color=style["color"],
        linestyle=style["linestyle"],
        marker=style["marker"],
        markersize=4.5,
        markerfacecolor=style["color"],
        markeredgecolor=style["color"],
        markeredgewidth=0.6,
        linewidth=1.15,
        label=style["label"],
        zorder=3,
    )
    return line


def add_break_marks(upper: plt.Axes, lower: plt.Axes) -> None:
    diagonal = 0.012
    upper_kwargs = {
        "transform": upper.transAxes,
        "color": "#222222",
        "clip_on": False,
        "linewidth": 0.8,
    }
    upper.plot((-diagonal, +diagonal), (-diagonal, +diagonal), **upper_kwargs)
    upper.plot((1 - diagonal, 1 + diagonal), (-diagonal, +diagonal), **upper_kwargs)

    lower_kwargs = {
        "transform": lower.transAxes,
        "color": "#222222",
        "clip_on": False,
        "linewidth": 0.8,
    }
    lower.plot((-diagonal, +diagonal), (1 - diagonal, 1 + diagonal), **lower_kwargs)
    lower.plot((1 - diagonal, 1 + diagonal), (1 - diagonal, 1 + diagonal), **lower_kwargs)


def make_figure(frame: pd.DataFrame, marginal_value: float) -> None:
    configure_matplotlib()
    lookup = {
        (int(row.lit), int(row.n)): row
        for row in frame.itertuples(index=False)
    }

    fig = plt.figure(figsize=(7.65, 3.75), constrained_layout=False)
    grid = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.04, 1.0],
        height_ratios=[3.15, 1.0],
        left=0.08,
        right=0.985,
        bottom=0.27,
        top=0.90,
        wspace=0.36,
        hspace=0.055,
    )
    r2_upper = fig.add_subplot(grid[0, 0])
    r2_lower = fig.add_subplot(grid[1, 0], sharex=r2_upper)
    rho_axis = fig.add_subplot(grid[:, 1])

    x = np.asarray(N_VALUES, dtype=float)
    legend_handles: list[Line2D] = []
    for lit in LIT_VALUES:
        style = LINE_STYLES[lit]
        r2_mean = np.asarray(
            [lookup[(lit, n)].R2_conv_mean for n in N_VALUES],
            dtype=float,
        )
        r2_std = np.asarray(
            [lookup[(lit, n)].R2_conv_std for n in N_VALUES],
            dtype=float,
        )
        rho_mean = np.asarray(
            [lookup[(lit, n)].spearman_mean for n in N_VALUES],
            dtype=float,
        )
        rho_std = np.asarray(
            [lookup[(lit, n)].spearman_std for n in N_VALUES],
            dtype=float,
        )

        legend_handles.append(draw_series(r2_upper, x, r2_mean, r2_std, style))
        draw_series(r2_lower, x, r2_mean, r2_std, style)
        draw_series(rho_axis, x, rho_mean, rho_std, style)

    r2_upper.set_ylim(-5.7, 0.65)
    r2_lower.set_ylim(-17.0, -6.0)
    rho_axis.set_ylim(-0.48, 0.62)
    for axis in (r2_upper, r2_lower, rho_axis):
        axis.set_xlim(7.2, 24.8)
        axis.set_xticks(N_VALUES)
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.45, zorder=0)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.tick_params(direction="out", length=3, width=0.8)

    r2_upper.axhline(
        0,
        color="#222222",
        linewidth=0.8,
        linestyle=(0, (3, 3)),
        zorder=2,
    )
    rho_axis.axhline(
        0,
        color="#222222",
        linewidth=0.8,
        linestyle=(0, (3, 3)),
        zorder=2,
    )

    r2_upper.spines["bottom"].set_visible(False)
    r2_lower.spines["top"].set_visible(False)
    r2_upper.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    r2_lower.tick_params(axis="x", top=False)
    add_break_marks(r2_upper, r2_lower)

    r2_upper.set_title(
        "A  R$^2_{conv}$ vs total training size,\n"
        "mixed at varying literature fractions",
        loc="left",
        fontweight="bold",
        pad=6,
    )
    rho_axis.set_title(
        "B  Spearman $\\rho$ vs total training size",
        loc="left",
        fontweight="bold",
        pad=7,
    )
    r2_lower.set_xlabel("Total training size, n")
    rho_axis.set_xlabel("Total training size, n")
    rho_axis.set_ylabel("Mean Spearman $\\rho$")
    fig.text(
        0.026,
        0.475,
        "Mean R$^2_{conv}$",
        rotation=90,
        ha="center",
        va="center",
        fontsize=8.5,
    )

    r2_upper.text(
        0.975,
        0.055,
        "Mean marginal change per added\n"
        f"literature record: {marginal_value:.2f} R$^2_{{conv}}$",
        transform=r2_upper.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.7,
        linespacing=1.15,
        bbox={
            "boxstyle": "round,pad=0.28",
            "facecolor": "white",
            "edgecolor": "#777777",
            "linewidth": 0.55,
            "alpha": 0.94,
        },
        zorder=5,
    )

    fig.legend(
        legend_handles,
        [LINE_STYLES[lit]["label"] for lit in LIT_VALUES],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.025),
        ncol=5,
        frameon=False,
        handlelength=2.35,
        columnspacing=1.15,
        labelspacing=0.4,
        borderaxespad=0,
    )

    fig.savefig(
        FIG_PDF,
        metadata={"Creator": "SkinMiner", "CreationDate": None, "ModDate": None},
    )
    fig.savefig(FIG_PNG, dpi=450, metadata={"Software": "SkinMiner"})
    plt.close(fig)


def update_report(frame: pd.DataFrame, marginal_value: float) -> None:
    source_hash = hashlib.sha256(SUMMARY_CSV.read_bytes()).hexdigest()
    block = "\n".join(
        [
            REPORT_START,
            "",
            "## Ratio-Sweep Line Figure Redraw",
            "",
            "The ratio-sweep line figure was redrawn from `ratio_sweep_summary.csv` only; no model fitting or analysis was rerun.",
            "",
            "Published figure rendering:",
            "",
            "- error bars replaced by same-colour shaded +/-SD bands;",
            "- Panel A uses a broken y-axis to separate the extreme lit=8, n=8 cell from the main -5.7 to 0.65 region;",
            "- a single horizontal legend is placed below both panels;",
            f"- the source-derived marginal annotation reports {marginal_value:.3f} R2_conv per added literature record;",
            "- the global suptitle was removed and the panel dimensions match the published figure size;",
            "- panel titles, fonts, palette, line styles, and filled markers were revised for main-paper readability.",
            "",
            f"Data verification: all {len(frame)} unique `(lit, n)` cells were read unchanged from `ratio_sweep_summary.csv`; source SHA-256 `{source_hash}`.",
            "",
            "The release package regenerates `figure_ratio_sweep_lines.pdf` and `figure_ratio_sweep_lines.png` directly. Legacy figure variants are not required or distributed.",
            "",
            REPORT_END,
        ]
    )

    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if REPORT_START in report_text and REPORT_END in report_text:
        prefix, remainder = report_text.split(REPORT_START, 1)
        _, suffix = remainder.split(REPORT_END, 1)
        report_text = prefix.rstrip() + "\n\n" + block + suffix
    else:
        report_text = report_text.rstrip() + "\n\n" + block + "\n"
    REPORT.write_text(report_text, encoding="utf-8")


def main() -> None:
    frame = read_and_validate_summary()
    marginal_value = marginal_value_per_literature_record(frame)
    make_figure(frame, marginal_value)
    update_report(frame, marginal_value)

    print("[DEMO2 RATIO LINES REDRAW] Done")
    print(f"Source rows: {len(frame)}")
    print(f"Mean marginal R2 per added literature record: {marginal_value:.6f}")
    print(f"PDF: {FIG_PDF}")
    print(f"PNG: {FIG_PNG}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
