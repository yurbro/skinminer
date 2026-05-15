from __future__ import annotations

import argparse
import json
import math
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

COLOR_INITIAL = "#A9BCD0"
COLOR_OPTIMIZED = "#245A8D"
COLOR_LITERATURE = "#D97B1E"
COLOR_TEXT = "#1F2933"
COLOR_MUTED = "#6B7280"
COLOR_GRID = "#E5E7EB"
COLOR_MATCH = "#4DAA57"
COLOR_PARTIAL = "#D8A31A"
COLOR_MISMATCH = "#C44E52"


def choose_font() -> str:
    for candidate in ["Arial", "Helvetica", "DejaVu Sans"]:
        try:
            path = font_manager.findfont(candidate, fallback_to_default=False)
        except Exception:
            continue
        if path:
            return candidate
    return "DejaVu Sans"


def configure_style(dpi: int) -> str:
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
            "savefig.pad_inches": 0.05,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    return font_name


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_pdf_png(fig: plt.Figure, output_dir: Path, stem: str) -> list[str]:
    ensure_output_dir(output_dir)
    outputs = []
    for suffix in ["pdf", "png"]:
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path)
        outputs.append(str(path))
    plt.close(fig)
    return outputs


def wrap(text: object, width: int) -> str:
    return textwrap.fill(str(text), width=width, break_long_words=False, break_on_hyphens=False)


def load_landscape(data_dir: Path) -> pd.DataFrame:
    df = pd.read_csv(data_dir / "fig_permeation_landscape.csv")
    df["endpoint_time_h"] = pd.to_numeric(df["endpoint_time_h"], errors="coerce")
    df["cumulative_amount_ug_cm2"] = pd.to_numeric(df["cumulative_amount_ug_cm2"], errors="coerce")
    df = df.dropna(subset=["endpoint_time_h", "cumulative_amount_ug_cm2"]).copy()
    df = df[df["cumulative_amount_ug_cm2"] <= 1000.0].copy()
    df["group"] = np.where(
        df["source"].eq("Literature (SkinMiner extracted)"),
        "Literature (SkinMiner extracted)",
        np.where(df["is_optimized"].eq("yes"), "AL-optimized (this study)", "Initial DOE (this study)"),
    )
    color_map = {
        "Initial DOE (this study)": COLOR_INITIAL,
        "AL-optimized (this study)": COLOR_OPTIMIZED,
        "Literature (SkinMiner extracted)": COLOR_LITERATURE,
    }
    df["color"] = df["group"].map(color_map)
    df = df.sort_values("cumulative_amount_ug_cm2", ascending=False).reset_index(drop=True)
    return df


def plot_fig1_landscape(df: pd.DataFrame, output_dir: Path) -> tuple[list[str], int, int]:
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    y = np.arange(len(df))

    for idx, row in df.iterrows():
        ax.hlines(y=idx, xmin=0, xmax=row["cumulative_amount_ug_cm2"], color=row["color"], linewidth=1.6, alpha=0.45)
        ax.scatter(
            row["cumulative_amount_ug_cm2"],
            idx,
            s=42,
            color=row["color"],
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )

    cf17_row = df[df["formulation_label"] == "Cf17"].iloc[0]
    cf17_idx = int(cf17_row.name)
    cf17_x = float(cf17_row["cumulative_amount_ug_cm2"])

    ax.axvline(cf17_x, ymin=0.0, ymax=1.0, color=COLOR_OPTIMIZED, linestyle=(0, (3, 2)), linewidth=1.0, alpha=0.7)
    ax.annotate(
        "Best in this study\nCf17",
        xy=(cf17_x, cf17_idx),
        xytext=(cf17_x + 60, cf17_idx + 2.2),
        fontsize=7,
        color=COLOR_OPTIMIZED,
        arrowprops={"arrowstyle": "->", "color": COLOR_OPTIMIZED, "linewidth": 0.9},
        ha="left",
        va="center",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df["formulation_label"])
    ax.invert_yaxis()
    ax.set_xlabel(r"24 h cumulative permeation ($\mu$g cm$^{-2}$)")
    ax.set_ylabel("Formulation")
    ax.set_title("24 h Permeation Performance Landscape", pad=8)
    ax.xaxis.grid(True, color=COLOR_GRID, linewidth=0.5)
    ax.set_axisbelow(True)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_INITIAL, markeredgecolor="white", markersize=6.5, label="Initial DOE (this study)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_OPTIMIZED, markeredgecolor="white", markersize=6.5, label="AL-optimized (this study)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_LITERATURE, markeredgecolor="white", markersize=6.5, label="Literature (SkinMiner extracted)"),
    ]
    ax.legend(handles=legend_handles, frameon=False, loc="lower right")
    ax.text(-0.08, 1.02, "a", transform=ax.transAxes, fontsize=11, fontweight="bold")

    outputs = save_pdf_png(fig, output_dir, "fig1_permeation_landscape")
    return outputs, cf17_idx + 1, len(df)


def summarize_conditions(df: pd.DataFrame) -> tuple[dict[str, str], dict[str, str]]:
    paper = df[df["source"] == "Paper 1 (this study)"].copy()
    lit = df[(df["source"] == "Literature (SkinMiner extracted)") & (df["formulation_label"].astype(str).str.startswith("F"))].copy()

    paper_summary = {
        "API": "Ibuprofen 5% w/w",
        "Membrane": "Strat-M synthetic membrane",
        "Device": "Franz cell",
        "Receptor": "PBS",
        "Dose": "Finite dose, 300 mg",
        "Excipient system": "P407 / EtOH / PG\nP407 20-30 wt%\nEtOH 10-20 wt%\nPG 10-20 wt%",
    }

    literature_summary = {
        "API": lit["api_concentration"].dropna().replace("", np.nan).dropna().mode().iloc[0].replace("%w/v", "% w/v") if not lit.empty else "",
        "Membrane": f"{lit['membrane_type'].mode().iloc[0]}" if not lit.empty else "",
        "Device": lit["device"].mode().iloc[0] if not lit.empty else "",
        "Receptor": lit["receptor_medium"].mode().iloc[0] if not lit.empty else "",
        "Dose": f"{lit['dose_type'].mode().iloc[0]} dose" if not lit.empty else "",
        "Excipient system": "Vit. E TPGS / HPMC\nTPGS 0.1-2% w/v\nHPMC K100 1-3% w/v\nHPMC K4 base 2% w/v",
    }
    return paper_summary, literature_summary


def plot_fig2_conditions(df: pd.DataFrame, output_dir: Path) -> list[str]:
    paper_summary, literature_summary = summarize_conditions(df)
    rows = [
        ("API", paper_summary["API"], literature_summary["API"], "Partial", COLOR_PARTIAL),
        ("Membrane", paper_summary["Membrane"], literature_summary["Membrane"], "Mismatch", COLOR_MISMATCH),
        ("Device", paper_summary["Device"], literature_summary["Device"], "Match", COLOR_MATCH),
        ("Receptor", paper_summary["Receptor"], literature_summary["Receptor"], "Match", COLOR_MATCH),
        ("Dose", paper_summary["Dose"], literature_summary["Dose"], "Mismatch", COLOR_MISMATCH),
        ("Excipient system", paper_summary["Excipient system"], literature_summary["Excipient system"], "Mismatch", COLOR_MISMATCH),
    ]

    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    col_x = [0.02, 0.19, 0.50, 0.87]
    col_w = [0.15, 0.29, 0.35, 0.11]
    header_y = 0.91
    row_h = 0.125

    headers = ["Dimension", "Paper 1 (this study)", "Literature benchmark", "Match"]
    for x, w, header in zip(col_x, col_w, headers):
        ax.add_patch(Rectangle((x, header_y), w, 0.075, facecolor="#F3F4F6", edgecolor="#D1D5DB", linewidth=0.6))
        ax.text(x + w / 2, header_y + 0.037, header, ha="center", va="center", fontsize=8, fontweight="bold", color=COLOR_TEXT)

    for idx, (dimension, paper_value, lit_value, match_text, match_color) in enumerate(rows):
        y = header_y - (idx + 1) * row_h
        fill = "#FFFFFF" if idx % 2 == 0 else "#FAFAFA"
        for x, w in zip(col_x[:3], col_w[:3]):
            ax.add_patch(Rectangle((x, y), w, row_h, facecolor=fill, edgecolor="#D1D5DB", linewidth=0.5))
        ax.add_patch(Rectangle((col_x[3], y), col_w[3], row_h, facecolor=fill, edgecolor="#D1D5DB", linewidth=0.5))

        ax.text(col_x[0] + 0.01, y + row_h / 2, dimension, ha="left", va="center", fontsize=8, color=COLOR_TEXT, fontweight="bold")
        ax.text(col_x[1] + 0.01, y + row_h / 2, wrap(paper_value, 21), ha="left", va="center", fontsize=6.8, color=COLOR_TEXT)
        ax.text(col_x[2] + 0.01, y + row_h / 2, wrap(lit_value, 23), ha="left", va="center", fontsize=6.8, color=COLOR_TEXT)

        pill_x = col_x[3] + 0.018
        pill_y = y + row_h / 2 - 0.022
        pill_w = col_w[3] - 0.036
        pill_h = 0.044
        ax.add_patch(
            FancyBboxPatch(
                (pill_x, pill_y),
                pill_w,
                pill_h,
                boxstyle="round,pad=0.01,rounding_size=0.01",
                facecolor=match_color,
                edgecolor="none",
                alpha=0.92,
            )
        )
        ax.text(col_x[3] + col_w[3] / 2, y + row_h / 2, match_text, ha="center", va="center", fontsize=7, color="white", fontweight="bold")

    ax.set_title("Experimental Condition Comparison", loc="left", pad=8)
    ax.text(
        0.02,
        0.06,
        "F1-F8 share one benchmark context; the excipient row summarizes the factor ranges extracted by SkinMiner.",
        fontsize=6.6,
        color=COLOR_MUTED,
    )
    ax.text(-0.03, 1.02, "b", transform=ax.transAxes, fontsize=11, fontweight="bold")

    return save_pdf_png(fig, output_dir, "fig2_condition_comparison")


def draw_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    facecolor: str,
    title: str,
    body: str,
    title_color: str = "white",
    title_size: float = 9.0,
    body_size: float = 7.4,
    title_wrap: int = 18,
    body_wrap: int = 18,
) -> None:
    x, y = xy
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=0.9,
            edgecolor="none",
            facecolor=facecolor,
        )
    )
    ax.text(
        x + width / 2,
        y + height * 0.72,
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


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = COLOR_MUTED, lw: float = 1.0, style: str = "-|>") -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=10, linewidth=lw, color=color))


def plot_fig3_phd_overview(output_dir: Path) -> list[str]:
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    boxes = [
        ((0.05, 0.56), "#5078A0", "Paper 1\nEDMA", "Accelerate each\nIVPT cycle"),
        ((0.29, 0.56), "#4A8F63", "Paper 2\nActive learning", "Reduce total\nexperiments"),
        ((0.53, 0.56), "#8B6BB8", "Paper 3\nSymbolic regression", "Gain interpretable\ninsights"),
        ((0.77, 0.56), "#D97B1E", "Paper 4\nSkinMiner", "Auto-acquire\nliterature benchmarks"),
    ]
    box_w = 0.17
    box_h = 0.22
    for (x, y), color, title, body in boxes:
        draw_box(ax, (x, y), box_w, box_h, color, title, body, title_size=8.4, body_size=6.9, title_wrap=16, body_wrap=18)

    for start_x in [0.22, 0.46, 0.70]:
        arrow(ax, (start_x, 0.67), (start_x + 0.07, 0.67), color=COLOR_MUTED, lw=1.1)

    central = FancyBboxPatch(
        (0.25, 0.15),
        0.50,
        0.16,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        linewidth=0.0,
        facecolor="#EEF2F7",
    )
    ax.add_patch(central)
    ax.text(0.50, 0.24, "Data-driven formulation design", ha="center", va="center", fontsize=9.5, fontweight="bold", color=COLOR_TEXT)
    ax.text(0.50, 0.19, "& cross-study benchmarking", ha="center", va="center", fontsize=8.5, color=COLOR_TEXT)

    for center_x in [0.135, 0.375, 0.615, 0.855]:
        arrow(ax, (center_x, 0.56), (center_x, 0.32), color=COLOR_MUTED, lw=1.0)
    arrow(ax, (0.85, 0.56), (0.35, 0.46), color=COLOR_LITERATURE, lw=1.0)
    ax.text(0.60, 0.49, "Literature benchmark informs\nfuture optimization", fontsize=7, color=COLOR_LITERATURE, ha="center", va="center")

    ax.text(0.03, 0.95, "PhD Methodological Chain", fontsize=10, fontweight="bold", color=COLOR_TEXT)
    ax.text(0.03, 0.90, "From efficient formulation optimization to automated literature benchmarking", fontsize=7.2, color=COLOR_MUTED)
    ax.text(-0.01, 1.02, "c", transform=ax.transAxes, fontsize=11, fontweight="bold")

    return save_pdf_png(fig, output_dir, "fig3_phd_overview")


def plot_fig4_pipeline_overview(output_dir: Path) -> list[str]:
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(x: float, y: float, w: float, h: float, color: str, title: str, body: str, text_color: str = "white") -> None:
        draw_box(ax, (x, y), w, h, color, title, body, title_color=text_color, title_size=8.2, body_size=6.5, title_wrap=16, body_wrap=18)

    box(0.33, 0.85, 0.34, 0.11, "#6B7280", "Open-access corpus", "1,828 papers")
    arrow(ax, (0.50, 0.85), (0.50, 0.76))
    box(0.31, 0.67, 0.38, 0.12, "#9AA5B1", "Routing review", "536 papers with signals")
    ax.text(0.74, 0.72, "480 unresolved /\nblocked at routing", fontsize=6.8, color=COLOR_MUTED, ha="left", va="center")
    arrow(ax, (0.50, 0.67), (0.50, 0.57))

    box(0.08, 0.45, 0.18, 0.11, "#4F86C6", "Text agent", "14 papers")
    box(0.29, 0.45, 0.18, 0.11, "#4F86C6", "Table agent", "18 papers")
    box(0.50, 0.45, 0.18, 0.11, "#4F86C6", "Figure agent", "15 papers")
    box(0.71, 0.45, 0.18, 0.11, "#4F86C6", "Mixed route", "9 papers")
    for center_x in [0.17, 0.38, 0.59, 0.80]:
        arrow(ax, (0.50, 0.57), (center_x, 0.56), lw=0.9)

    arrow(ax, (0.50, 0.45), (0.50, 0.34))
    box(0.32, 0.24, 0.36, 0.11, "#2E6F40", "Assembly", "239 records")
    arrow(ax, (0.50, 0.24), (0.50, 0.12))
    draw_box(
        ax,
        (0.29, 0.02),
        0.42,
        0.13,
        "#D97B1E",
        "Verified set",
        "47 v3 verified ibuprofen cumulative rows\n28 matched 24 h points",
        title_color="white",
        title_size=7.6,
        body_size=5.8,
        title_wrap=18,
        body_wrap=22,
    )

    ax.text(0.03, 0.96, "SkinMiner pipeline overview", fontsize=10, fontweight="bold", color=COLOR_TEXT)
    ax.text(0.03, 0.92, "Frozen benchmark baseline.\nCounts for the v3 ibuprofen benchmark subset.", fontsize=7.0, color=COLOR_MUTED, va="top")
    ax.text(-0.01, 1.02, "d", transform=ax.transAxes, fontsize=11, fontweight="bold")

    return save_pdf_png(fig, output_dir, "fig4_pipeline_overview")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate benchmarking demonstration figures.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing benchmarking CSV files.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for figure outputs.")
    parser.add_argument("--dpi", type=int, default=300, help="PNG/render DPI. Use 600 for high-resolution export.")
    args = parser.parse_args()

    data_dir = args.data_dir if args.data_dir.is_absolute() else ROOT / args.data_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    font_name = configure_style(args.dpi)

    landscape = load_landscape(data_dir)
    conditions = pd.read_csv(data_dir / "fig_experimental_conditions.csv")

    fig1_paths, cf17_rank, total_ranked = plot_fig1_landscape(landscape, output_dir)
    fig2_paths = plot_fig2_conditions(conditions, output_dir)
    fig3_paths = plot_fig3_phd_overview(output_dir)
    fig4_paths = plot_fig4_pipeline_overview(output_dir)

    payload = {
        "font_used": font_name,
        "figure1": fig1_paths,
        "figure2": fig2_paths,
        "figure3": fig3_paths,
        "figure4": fig4_paths,
        "cf17_rank": cf17_rank,
        "landscape_total": total_ranked,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
