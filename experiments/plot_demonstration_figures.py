from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "outputs" / "demonstration"
DEFAULT_OUTPUT_DIR = DEFAULT_DATA_DIR / "figures"

COLOR_TEXT = "#1F2933"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#D1D5DB"
COLOR_BBD = "#A9BCD0"
COLOR_LHS = "#2A9D8F"
COLOR_BO = "#E9C46A"
COLOR_OPT = "#245A8D"
COLOR_LITERATURE = "#D97B1E"
COLOR_MATCH = "#4DAA57"
COLOR_PARTIAL = "#D8A31A"
COLOR_MISMATCH = "#C44E52"
FUNNEL_COLORS = ["#DCE6F1", "#B7CCE1", "#7FA7C9", "#245A8D"]


def choose_font() -> str:
    for candidate in ["Arial", "Helvetica", "DejaVu Sans"]:
        try:
            path = font_manager.findfont(candidate, fallback_to_default=False)
        except Exception:
            continue
        if path:
            return candidate
    return "DejaVu Sans"


def apply_publication_style(dpi: int) -> str:
    font_name = choose_font()
    mpl.rcParams.update(
        {
            "font.family": font_name,
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "figure.dpi": dpi,
            "savefig.dpi": dpi,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    return font_name


def wrap(text: object, width: int) -> str:
    return textwrap.fill(str(text), width=width, break_long_words=False, break_on_hyphens=False)


def save_pdf_png(fig: plt.Figure, output_dir: Path, stem: str) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for suffix in ["pdf", "png"]:
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path)
        paths.append(str(path))
    plt.close(fig)
    return paths


def despine(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="out")


def draw_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    facecolor: str,
    title: str,
    body: str,
    title_color: str = "white",
    title_size: float = 8.8,
    body_size: float = 7.0,
    title_wrap: int = 18,
    body_wrap: int = 20,
) -> None:
    x, y = xy
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            linewidth=0.0,
            facecolor=facecolor,
        )
    )
    ax.text(
        x + width / 2,
        y + height * 0.70,
        wrap(title, title_wrap),
        ha="center",
        va="center",
        fontsize=title_size,
        fontweight="bold",
        color=title_color,
    )
    ax.text(
        x + width / 2,
        y + height * 0.34,
        wrap(body, body_wrap),
        ha="center",
        va="center",
        fontsize=body_size,
        color=title_color,
    )


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = COLOR_MUTED,
    lw: float = 1.0,
    style: str = "-|>",
) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=10, linewidth=lw, color=color))


def plot_condition_funnel(data_dir: Path, output_dir: Path) -> list[str]:
    df = pd.read_csv(data_dir / "fig_condition_funnel.csv")
    order = ["Level 4", "Level 3", "Level 2", "Level 1"]
    df["level"] = pd.Categorical(df["level"], categories=order, ordered=True)
    df = df.sort_values("level").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    y = np.arange(len(df))
    ax.barh(y, df["count"], color=FUNNEL_COLORS[::-1], edgecolor="none", height=0.58)

    for idx, row in df.iterrows():
        ax.text(row["count"] + 0.6, idx, f"{int(row['count'])}", va="center", ha="left", fontsize=8, color=COLOR_TEXT)

    ax.set_yticks(y)
    ax.set_yticklabels(
        [
            "Level 4  Same API + device",
            "Level 3  Partial excipient overlap",
            "Level 2  Same excipient system",
            "Level 1  Exact match",
        ]
    )
    ax.invert_yaxis()
    ax.set_xlabel("Matching assembled records")
    ax.set_title("Condition-matched literature search for Poloxamer 407 / Ethanol / PG ibuprofen formulations", pad=8)
    ax.set_xlim(0, max(df["count"].max() + 8, 10))
    ax.text(0.01, 0.06, "Higher levels apply stricter condition matching.", transform=ax.transAxes, fontsize=7, color=COLOR_MUTED)
    despine(ax)
    return save_pdf_png(fig, output_dir, "fig1_condition_funnel")


def plot_comparability_table(data_dir: Path, output_dir: Path) -> list[str]:
    df = pd.read_csv(data_dir / "fig_comparability_table.csv")
    color_map = {"Match": COLOR_MATCH, "Partial": COLOR_PARTIAL, "Mismatch": COLOR_MISMATCH}

    fig, ax = plt.subplots(figsize=(7.2, 4.25))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    col_x = [0.02, 0.20, 0.49, 0.80, 0.90]
    col_w = [0.16, 0.27, 0.29, 0.09, 0.08]
    header_y = 0.91
    row_h = 0.105

    headers = ["Dimension", "Paper 1 condition", "Literature F1-F8 condition", "Match", "Extracted"]
    for x, w, header in zip(col_x, col_w, headers):
        ax.add_patch(Rectangle((x, header_y), w, 0.07, facecolor="#F3F4F6", edgecolor=COLOR_BORDER, linewidth=0.6))
        ax.text(x + w / 2, header_y + 0.035, header, ha="center", va="center", fontsize=8, fontweight="bold", color=COLOR_TEXT)

    for idx, row in df.iterrows():
        y = header_y - (idx + 1) * row_h
        fill = "#FFFFFF" if idx % 2 == 0 else "#FAFAFA"
        for x, w in zip(col_x, col_w):
            ax.add_patch(Rectangle((x, y), w, row_h, facecolor=fill, edgecolor=COLOR_BORDER, linewidth=0.5))

        ax.text(col_x[0] + 0.01, y + row_h / 2, row["dimension"], ha="left", va="center", fontsize=8, color=COLOR_TEXT, fontweight="bold")
        ax.text(col_x[1] + 0.01, y + row_h / 2, wrap(row["paper1"], 22), ha="left", va="center", fontsize=6.8, color=COLOR_TEXT)
        ax.text(col_x[2] + 0.01, y + row_h / 2, wrap(row["literature"], 24), ha="left", va="center", fontsize=6.8, color=COLOR_TEXT)

        match_color = color_map[row["match_label"]]
        ax.add_patch(
            FancyBboxPatch(
                (col_x[3] + 0.012, y + row_h / 2 - 0.018),
                col_w[3] - 0.024,
                0.036,
                boxstyle="round,pad=0.008,rounding_size=0.012",
                linewidth=0,
                facecolor=match_color,
                alpha=0.94,
            )
        )
        ax.text(col_x[3] + col_w[3] / 2, y + row_h / 2, row["match_label"], ha="center", va="center", fontsize=6.5, color="white", fontweight="bold")

        ax.add_patch(
            FancyBboxPatch(
                (col_x[4] + 0.006, y + row_h / 2 - 0.018),
                col_w[4] - 0.012,
                0.036,
                boxstyle="round,pad=0.008,rounding_size=0.012",
                linewidth=0,
                facecolor=COLOR_MATCH,
                alpha=0.94,
            )
        )
        ax.text(col_x[4] + col_w[4] / 2, y + row_h / 2, "Yes", ha="center", va="center", fontsize=6.6, color="white", fontweight="bold")

    ax.set_title("Automated comparability assessment via SkinMiner structured extraction", loc="left", pad=8)
    ax.text(
        0.02,
        0.06,
        "The rightmost column reflects whether SkinMiner structured that condition field automatically from the literature side.",
        fontsize=6.6,
        color=COLOR_MUTED,
    )
    return save_pdf_png(fig, output_dir, "fig2_comparability_table")


def plot_phd_overview(output_dir: Path) -> list[str]:
    fig, ax = plt.subplots(figsize=(7.2, 3.95))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    boxes = [
        ((0.05, 0.56), COLOR_OPT, "Paper 1\nEDMA", "Accelerate each IVPT"),
        ((0.29, 0.56), COLOR_LHS, "Paper 2\nActive learning", "Reduce experiments"),
        ((0.53, 0.56), "#8B6BB8", "Paper 3\nSymbolic regression", "Interpretable models"),
        ((0.77, 0.56), COLOR_LITERATURE, "Paper 4\nSkinMiner", "Literature data reconnaissance"),
    ]
    box_w = 0.17
    box_h = 0.22
    for (x, y), color, title, body in boxes:
        draw_box(ax, (x, y), box_w, box_h, color, title, body, title_wrap=16, body_wrap=18)

    for start_x in [0.22, 0.46, 0.70]:
        arrow(ax, (start_x, 0.67), (start_x + 0.07, 0.67), color=COLOR_MUTED, lw=1.1)

    central = FancyBboxPatch(
        (0.25, 0.14),
        0.50,
        0.16,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        linewidth=0.0,
        facecolor="#EEF2F7",
    )
    ax.add_patch(central)
    ax.text(0.50, 0.24, "Closed-loop formulation methodology", ha="center", va="center", fontsize=9.5, fontweight="bold", color=COLOR_TEXT)
    ax.text(0.50, 0.19, "optimize, interpret, and assess literature context", ha="center", va="center", fontsize=8.0, color=COLOR_TEXT)

    for center_x in [0.135, 0.375, 0.615, 0.855]:
        arrow(ax, (center_x, 0.56), (center_x, 0.32), color=COLOR_MUTED, lw=1.0)
    arrow(ax, (0.85, 0.56), (0.35, 0.46), color=COLOR_LITERATURE, lw=1.0)
    ax.text(
        0.60,
        0.49,
        "Literature intelligence informs:\ndata availability, condition comparability,\nlandscape awareness",
        fontsize=6.8,
        color=COLOR_LITERATURE,
        ha="center",
        va="center",
    )

    ax.text(0.03, 0.95, "PhD methodological chain", fontsize=10, fontweight="bold", color=COLOR_TEXT)
    ax.text(0.03, 0.90, "From efficient IVPT optimization to automated literature reconnaissance", fontsize=7.2, color=COLOR_MUTED)
    return save_pdf_png(fig, output_dir, "fig3_phd_overview")


def plot_data_distribution(data_dir: Path, output_dir: Path) -> list[str]:
    df = pd.read_csv(data_dir / "fig_permeation_landscape.csv")
    value_column = "cumulative_amount_ug_cm2" if "cumulative_amount_ug_cm2" in df.columns else "cumulative_amount_24h_ug_cm2"
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")
    df = df.dropna(subset=[value_column]).copy()

    paper = df[df["source"] == "Paper 1 (this study)"].copy()
    literature = df[df["source"] == "Literature (SkinMiner extracted)"].copy()

    group_order = ["BBD", "LHS", "BO", "OPT"]
    group_colors = {"BBD": COLOR_BBD, "LHS": COLOR_LHS, "BO": COLOR_BO, "OPT": COLOR_OPT}
    rng = np.random.default_rng(20260424)

    fig, (ax_left, ax_right) = plt.subplots(
        1,
        2,
        figsize=(7.2, 3.8),
        sharey=True,
        gridspec_kw={"width_ratios": [4.0, 1.7], "wspace": 0.22},
    )

    values = [paper.loc[paper["design_group"] == group, value_column].to_numpy() for group in group_order]
    box = ax_left.boxplot(
        values,
        positions=np.arange(1, len(group_order) + 1),
        widths=0.52,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#111111", "linewidth": 1.0},
        whiskerprops={"color": "#444444", "linewidth": 0.7},
        capprops={"color": "#444444", "linewidth": 0.7},
        boxprops={"edgecolor": "#333333", "linewidth": 0.7},
    )
    for patch, group in zip(box["boxes"], group_order):
        patch.set_facecolor(group_colors[group])
        patch.set_alpha(0.18)

    for idx, group in enumerate(group_order, start=1):
        block = paper[paper["design_group"] == group]
        jitter = rng.normal(0.0, 0.055, size=len(block))
        ax_left.scatter(
            np.full(len(block), idx) + jitter,
            block[value_column],
            s=20,
            color=group_colors[group],
            edgecolor="white",
            linewidth=0.45,
            zorder=3,
        )

    ax_left.set_xticks(np.arange(1, len(group_order) + 1))
    ax_left.set_xticklabels([f"{group}\n(n={int((paper['design_group'] == group).sum())})" for group in group_order])
    ax_left.set_ylabel(r"24 h cumulative permeation ($\mu$g cm$^{-2}$)")
    ax_left.set_title("Paper 1 formulations", pad=8)
    ax_left.text(
        0.03,
        0.95,
        "Strat-M, finite dose 300 mg,\nPoloxamer 407 gel",
        transform=ax_left.transAxes,
        ha="left",
        va="top",
        fontsize=6.8,
        color=COLOR_MUTED,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "#F8FAFC", "edgecolor": COLOR_BORDER, "linewidth": 0.5},
    )
    despine(ax_left)

    lit_values = literature[value_column].to_numpy()
    lit_box = ax_right.boxplot(
        [lit_values],
        positions=[1],
        widths=0.5,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#111111", "linewidth": 1.0},
        whiskerprops={"color": "#444444", "linewidth": 0.7},
        capprops={"color": "#444444", "linewidth": 0.7},
        boxprops={"edgecolor": "#333333", "linewidth": 0.7},
    )
    lit_box["boxes"][0].set_facecolor(COLOR_LITERATURE)
    lit_box["boxes"][0].set_alpha(0.18)
    jitter = rng.normal(0.0, 0.035, size=len(lit_values))
    ax_right.scatter(
        np.full(len(lit_values), 1.0) + jitter,
        lit_values,
        s=22,
        color=COLOR_LITERATURE,
        edgecolor="white",
        linewidth=0.45,
        zorder=3,
    )
    for _, row in literature.iterrows():
        if row[value_column] > 300:
            ax_right.text(0.92, row[value_column], row["formulation_label"], fontsize=6.5, color=COLOR_LITERATURE, va="center", ha="right")
        else:
            ax_right.text(1.08, row[value_column], row["formulation_label"], fontsize=6.5, color=COLOR_LITERATURE, va="center", ha="left")

    ax_right.set_xticks([1])
    ax_right.set_xticklabels([f"F1-F8\n(n={len(literature)})"])
    ax_right.set_title("Literature block", pad=8)
    ax_right.text(
        0.04,
        0.82,
        "Porcine skin, infinite dose,\nTPGS/HPMC nanosuspension",
        transform=ax_right.transAxes,
        ha="left",
        va="top",
        fontsize=6.8,
        color=COLOR_MUTED,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "#F8FAFC", "edgecolor": COLOR_BORDER, "linewidth": 0.5},
    )
    ax_right.tick_params(axis="y", left=False, labelleft=False)
    despine(ax_right)
    ax_right.spines["left"].set_visible(False)

    ymin = min(df[value_column].min() - 12, 150)
    ymax = df[value_column].max() + 20
    ax_left.set_ylim(ymin, ymax)

    fig.text(0.502, 0.52, "Different conditions\nnot directly comparable", ha="center", va="center", fontsize=7.2, color=COLOR_MUTED)
    fig.lines.append(Line2D([0.50, 0.50], [0.18, 0.88], transform=fig.transFigure, linestyle=(0, (3, 2)), linewidth=0.8, color=COLOR_BORDER))

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_BBD, markeredgecolor="white", markersize=6.0, label="BBD"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_LHS, markeredgecolor="white", markersize=6.0, label="LHS"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_BO, markeredgecolor="white", markersize=6.0, label="BO"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_OPT, markeredgecolor="white", markersize=6.0, label="OPT"),
    ]
    ax_left.legend(handles=legend_handles, frameon=False, loc="lower left", ncol=4, bbox_to_anchor=(0.0, -0.22))
    fig.suptitle("24 h literature and self-generated data distribution under different conditions", y=0.98, fontsize=10, fontweight="bold")
    return save_pdf_png(fig, output_dir, "fig4_data_distribution")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot revised SkinMiner demonstration figures.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing support CSVs.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for figure outputs.")
    parser.add_argument("--dpi", type=int, default=300, help="Export DPI.")
    args = parser.parse_args()

    data_dir = args.data_dir if args.data_dir.is_absolute() else ROOT / args.data_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    font_name = apply_publication_style(args.dpi)

    payload = {
        "font_used": font_name,
        "fig1": plot_condition_funnel(data_dir, output_dir),
        "fig2": plot_comparability_table(data_dir, output_dir),
        "fig3": plot_phd_overview(output_dir),
        "fig4": plot_data_distribution(data_dir, output_dir),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
