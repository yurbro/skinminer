from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
V5_DIR = ROOT / "outputs" / "demonstration_v5"
FIGURE_DIR = V5_DIR / "figures"
PREDICTIONS_CSV = V5_DIR / "logo_cv_predictions.csv"
PER_FORMULATION_CSV = V5_DIR / "per_formulation_metrics.csv"
SOURCE_DATA_CSV = ROOT / "outputs" / "demonstration_v3" / "source_paper_data.csv"
GLOBAL_METRICS_JSON = V5_DIR / "global_metrics.json"

MICRO_UNIT = "µg/cm²"

TIME_COLORS = {
    24.0: "#7FB3D5",
    48.0: "#2B6C8A",
    72.0: "#164A64",
}
COLORS = {
    "blue": "#164A64",
    "light_blue": "#7FB3D5",
    "red": "#B94B48",
    "purple": "#6F5AAE",
    "gray": "#9AA3AD",
    "dark_gray": "#56616F",
    "light_gray": "#E9EDF2",
}
FONT_SCALE = 1.0


def scaled_font(size: float) -> float:
    return size * FONT_SCALE


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
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
        }
    )


def ensure_dirs() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def backup_simple_figures() -> None:
    for stem in ["fig_logo_cv_main", "fig_permeation_profiles"]:
        for suffix in [".png", ".pdf"]:
            src = FIGURE_DIR / f"{stem}{suffix}"
            dst = FIGURE_DIR / f"{stem}_v1{suffix}"
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float]]:
    predictions = pd.read_csv(PREDICTIONS_CSV)
    per_formulation = pd.read_csv(PER_FORMULATION_CSV)
    source = pd.read_csv(SOURCE_DATA_CSV)
    metrics = json.loads(GLOBAL_METRICS_JSON.read_text(encoding="utf-8"))
    predictions["residual"] = predictions["true_value_ug_cm2"] - predictions["predicted_value_ug_cm2"]
    predictions["tick_label"] = predictions["formulation"] + "-" + predictions["time_h"].astype(int).astype(str)
    return predictions, per_formulation, source, metrics


def panel_title(ax: plt.Axes, letter: str, text: str) -> None:
    ax.set_title(rf"$\bf{{{letter}}}$ {text}", loc="left", pad=5)


def r2_color(value: float) -> str:
    if value > 0.5:
        return COLORS["blue"]
    if value > 0.0:
        return COLORS["light_blue"]
    return COLORS["red"]


def formulation_order(values: pd.Series | list[str]) -> list[str]:
    return sorted(set(values), key=lambda item: int(str(item).replace("F", "")))


def draw_panel_a(ax: plt.Axes, predictions: pd.DataFrame) -> None:
    palette = plt.get_cmap("tab10")
    for idx, formulation in enumerate(formulation_order(predictions["formulation"])):
        group = predictions[predictions["formulation"] == formulation].sort_values("time_h")
        color = palette(idx % 10)
        time = group["time_h"].to_numpy(dtype=float)
        true_values = group["true_value_ug_cm2"].to_numpy(dtype=float)
        pred_values = group["predicted_value_ug_cm2"].to_numpy(dtype=float)
        pred_std = group["predicted_std_ug_cm2"].to_numpy(dtype=float)
        ax.plot(time, true_values, color=color, lw=1.0, marker="o", ms=3.2, label=formulation)
        ax.plot(time, pred_values, color=color, lw=0.9, ls="--", marker="s", ms=2.8)
        ax.fill_between(time, pred_values - pred_std, pred_values + pred_std, color=color, alpha=0.10, linewidth=0)

    ax.set_xticks([24, 48, 72])
    ax.set_xlabel("Time (h)")
    ax.set_ylabel(f"Cumulative permeation ({MICRO_UNIT})")
    panel_title(ax, "a", "True vs predicted permeation profiles")
    ax.legend(loc="upper left", ncol=2, title="Solid true / dashed predicted", title_fontsize=scaled_font(7))


def parity_label_offsets() -> dict[tuple[str, int], tuple[float, float]]:
    return {
        ("F1", 24): (42, -45),
        ("F2", 24): (42, 12),
        ("F3", 24): (-82, 44),
        ("F4", 24): (-84, 90),
        ("F5", 24): (34, 34),
        ("F6", 24): (-92, -32),
        ("F7", 24): (36, 48),
        ("F8", 24): (-96, 18),
        ("F1", 48): (32, -52),
        ("F2", 48): (34, -14),
        ("F3", 48): (26, 34),
        ("F4", 48): (-78, 42),
        ("F5", 48): (34, -40),
        ("F6", 48): (34, -12),
        ("F7", 48): (34, 28),
        ("F8", 48): (-76, -32),
        ("F1", 72): (34, -36),
        ("F2", 72): (34, 8),
        ("F3", 72): (30, 36),
        ("F4", 72): (30, 26),
        ("F5", 72): (30, -46),
        ("F6", 72): (30, -16),
        ("F7", 72): (30, 28),
        ("F8", 72): (30, -26),
    }


def draw_panel_b(ax: plt.Axes, predictions: pd.DataFrame, metrics: dict[str, float]) -> None:
    axis_max = max(predictions["true_value_ug_cm2"].max(), predictions["predicted_value_ug_cm2"].max()) * 1.07
    x_line = np.linspace(0, axis_max, 200)
    mae = float(metrics["MAE"])
    ax.fill_between(x_line, x_line - mae, x_line + mae, color=COLORS["light_gray"], alpha=0.65, linewidth=0)
    ax.plot(x_line, x_line, color=COLORS["dark_gray"], lw=0.8, ls="--")

    for time_h, group in predictions.groupby("time_h"):
        ax.scatter(
            group["true_value_ug_cm2"],
            group["predicted_value_ug_cm2"],
            s=18,
            color=TIME_COLORS[float(time_h)],
            edgecolor="white",
            linewidth=0.35,
            label=f"{int(time_h)} h",
            zorder=3,
        )

    offsets = parity_label_offsets()
    for _, row in predictions.iterrows():
        key = (row["formulation"], int(row["time_h"]))
        dx, dy = offsets.get(key, (28, 18))
        ax.annotate(
            row["formulation"],
            xy=(row["true_value_ug_cm2"], row["predicted_value_ug_cm2"]),
            xytext=(row["true_value_ug_cm2"] + dx, row["predicted_value_ug_cm2"] + dy),
            fontsize=scaled_font(5.5),
            color=COLORS["dark_gray"],
            arrowprops={"arrowstyle": "-", "lw": 0.35, "color": COLORS["gray"], "shrinkA": 0, "shrinkB": 3},
        )

    ax.set_xlim(0, axis_max)
    ax.set_ylim(0, axis_max)
    ax.set_xlabel(f"Actual ({MICRO_UNIT})")
    ax.set_ylabel(f"Predicted ({MICRO_UNIT})")
    panel_title(ax, "b", "Parity plot by timepoint")
    ax.legend(loc="upper left", ncol=3)
    ax.text(
        0.97,
        0.04,
        f"MAE = {metrics['MAE']:.0f} {MICRO_UNIT}\nRMSE = {metrics['RMSE']:.0f} {MICRO_UNIT}\nR² = {metrics['R2']:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=scaled_font(7),
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": COLORS["light_gray"], "lw": 0.5},
    )


def draw_panel_c(ax: plt.Axes, predictions: pd.DataFrame, metrics: dict[str, float]) -> None:
    order = formulation_order(predictions["formulation"])
    x = np.arange(len(order))
    width = 0.24
    for offset, time_h in zip([-width, 0, width], [24.0, 48.0, 72.0], strict=True):
        values = [
            float(
                predictions[(predictions["formulation"] == formulation) & (predictions["time_h"] == time_h)][
                    "abs_error"
                ].iloc[0]
            )
            for formulation in order
        ]
        ax.bar(x + offset, values, width=width, color=TIME_COLORS[time_h], label=f"{int(time_h)} h")
    ax.axhline(metrics["MAE"], color=COLORS["dark_gray"], lw=0.8, ls="--")
    ax.text(len(order) - 0.15, metrics["MAE"] + 9, "Overall MAE", ha="right", va="bottom", fontsize=scaled_font(7), color=COLORS["dark_gray"])
    ax.set_xticks(x, order)
    ax.set_ylabel(f"Absolute error ({MICRO_UNIT})")
    panel_title(ax, "c", "Absolute error by timepoint")
    ax.legend(loc="upper left", ncol=3)


def draw_panel_d(ax: plt.Axes, per_formulation: pd.DataFrame, metrics: dict[str, float]) -> None:
    per_formulation = per_formulation.sort_values("formulation", key=lambda s: s.str.replace("F", "").astype(int))
    x = np.arange(len(per_formulation))
    colors = [r2_color(value) for value in per_formulation["R2"]]
    ax.bar(x, per_formulation["MAE"], color=colors, width=0.72)
    ax.axhline(metrics["MAE"], color=COLORS["dark_gray"], lw=0.8, ls="--")
    ax.text(len(per_formulation) - 0.15, metrics["MAE"] + 9, "Overall MAE", ha="right", va="bottom", fontsize=scaled_font(7), color=COLORS["dark_gray"])
    for idx, row in per_formulation.iterrows():
        ax.text(idx, row["MAE"] + 10, f"{row['R2']:.2f}", ha="center", va="bottom", fontsize=scaled_font(7))
    ax.set_xticks(x, per_formulation["formulation"])
    ax.set_ylabel(f"MAE ({MICRO_UNIT})")
    panel_title(ax, "d", "Per-formulation MAE")
    ax.set_ylim(0, float(per_formulation["MAE"].max()) * 1.32)
    handles = [
        Patch(facecolor=COLORS["blue"], edgecolor="none", label="R² > 0.5"),
        Patch(facecolor=COLORS["light_blue"], edgecolor="none", label="0 < R² ≤ 0.5"),
        Patch(facecolor=COLORS["red"], edgecolor="none", label="R² < 0"),
    ]
    ax.legend(handles=handles, loc="upper left")


def draw_panel_e(ax: plt.Axes, predictions: pd.DataFrame) -> None:
    ordered = predictions.sort_values(["formulation", "time_h"], key=lambda s: s.str.replace("F", "").astype(int) if s.name == "formulation" else s)
    x = np.arange(len(ordered))
    width = 0.38
    ax.bar(x - width / 2, ordered["predicted_std_ug_cm2"], width=width, color=COLORS["purple"], label="GPR σ")
    ax.bar(x + width / 2, ordered["measurement_sd"], width=width, color=COLORS["gray"], label="Measurement SD")
    ax.set_xticks(x, ordered["tick_label"], rotation=55, ha="right")
    ax.set_ylabel(f"Uncertainty ({MICRO_UNIT})")
    panel_title(ax, "e", "GPR predictive uncertainty vs measurement SD")
    ax.legend(loc="upper left")


def draw_panel_f(ax: plt.Axes, predictions: pd.DataFrame) -> None:
    residual = predictions["residual"].to_numpy(dtype=float)
    mu = float(np.mean(residual))
    sigma = float(np.std(residual, ddof=1))
    ax.hist(residual, bins=8, density=True, color=COLORS["light_blue"], edgecolor="white", alpha=0.9)
    x = np.linspace(residual.min() - 80, residual.max() + 80, 300)
    if sigma > 0:
        pdf = (1.0 / (sigma * math.sqrt(2.0 * math.pi))) * np.exp(-0.5 * np.square((x - mu) / sigma))
        ax.plot(x, pdf, color=COLORS["blue"], lw=1.2)
    ax.axvline(0, color=COLORS["dark_gray"], lw=0.8, ls="--")
    ax.set_xlabel(f"Residual, true - predicted ({MICRO_UNIT})")
    ax.set_ylabel("Density")
    panel_title(ax, "f", "Residual distribution")
    ax.text(
        0.96,
        0.95,
        f"N(μ={mu:.0f}, σ={sigma:.0f})",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=scaled_font(7),
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": COLORS["light_gray"], "lw": 0.5},
    )


def build_composite() -> None:
    configure_style()
    ensure_dirs()
    backup_simple_figures()
    predictions, per_formulation, _source, metrics = load_inputs()

    fig = plt.figure(figsize=(14, 8.5), facecolor="white")
    gs = gridspec.GridSpec(
        2,
        3,
        figure=fig,
        hspace=0.40,
        wspace=0.32,
        left=0.06,
        right=0.98,
        top=0.96,
        bottom=0.08,
    )
    axes = [fig.add_subplot(gs[row, col]) for row in range(2) for col in range(3)]

    draw_panel_a(axes[0], predictions)
    draw_panel_b(axes[1], predictions, metrics)
    draw_panel_c(axes[2], predictions, metrics)
    draw_panel_d(axes[3], per_formulation, metrics)
    draw_panel_e(axes[4], predictions)
    draw_panel_f(axes[5], predictions)

    for ax in axes:
        ax.set_facecolor("white")
        ax.grid(False)

    fig.savefig(FIGURE_DIR / "fig_logo_cv_composite.png")
    fig.savefig(FIGURE_DIR / "fig_logo_cv_composite.pdf")
    plt.close(fig)


def main() -> None:
    build_composite()
    png = FIGURE_DIR / "fig_logo_cv_composite.png"
    pdf = FIGURE_DIR / "fig_logo_cv_composite.pdf"
    print("Composite figure generated")
    print(f"PNG: {png} ({png.stat().st_size} bytes)")
    print(f"PDF: {pdf} ({pdf.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
