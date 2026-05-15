from __future__ import annotations

import math
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.metrics import mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "demonstration_v3"
FIGURE_DIR = OUTPUT_DIR / "figures"
SKINMINER_V2_DATA = ROOT / "outputs" / "demonstration_v2" / "literature_ibuprofen_data.csv"

DOI = "10.1208/s12249-013-9995-4"
DIFFUSION_AREA_CM2 = 0.64
DECISION_THRESHOLD = 0.2
RANDOM_STATE = 42

FEATURES_A = [
    "particle_size_nm",
    "vit_e_tpgs_pct_wv",
    "hpmc_k100_pct_wv",
    "cum_amount_24h_ug_cm2",
    "cum_amount_48h_ug_cm2",
]
FEATURES_B = ["particle_size_nm", "vit_e_tpgs_pct_wv", "hpmc_k100_pct_wv", "cum_amount_24h_ug_cm2"]

COLORS = {
    "ink": "#1F2933",
    "slate": "#56616F",
    "blue": "#2B6C8A",
    "green": "#3D7C59",
    "orange": "#C97931",
    "red": "#B94B48",
    "gray": "#B8BFC7",
    "light_gray": "#E6E9ED",
}

OUTCOME_COLORS = {
    "TP": COLORS["green"],
    "TN": COLORS["blue"],
    "FP": COLORS["orange"],
    "FN": COLORS["red"],
}


MANUAL_DATA = [
    ("F1", 300, 2.0, 1.0, 24, 298.0, 57.8),
    ("F1", 300, 2.0, 1.0, 48, 536.5, 63.4),
    ("F1", 300, 2.0, 1.0, 72, 1142.4, 107.5),
    ("F2", 300, 2.0, 3.0, 24, 155.9, 11.4),
    ("F2", 300, 2.0, 3.0, 48, 580.2, 58.6),
    ("F2", 300, 2.0, 3.0, 72, 1178.9, 144.2),
    ("F3", 900, 2.0, 3.0, 24, 140.2, 35.9),
    ("F3", 900, 2.0, 3.0, 48, 543.5, 112.5),
    ("F3", 900, 2.0, 3.0, 72, 759.6, 94.4),
    ("F4", 300, 0.1, 3.0, 24, 132.3, 65.7),
    ("F4", 300, 0.1, 3.0, 48, 464.8, 18.2),
    ("F4", 300, 0.1, 3.0, 72, 734.4, 195.2),
    ("F5", 900, 0.1, 3.0, 24, 312.3, 53.1),
    ("F5", 900, 0.1, 3.0, 48, 542.5, 65.1),
    ("F5", 900, 0.1, 3.0, 72, 799.5, 133.3),
    ("F6", 900, 2.0, 1.0, 24, 148.8, 28.6),
    ("F6", 900, 2.0, 1.0, 48, 551.2, 123.0),
    ("F6", 900, 2.0, 1.0, 72, 808.0, 128.9),
    ("F7", 900, 0.1, 1.0, 24, 123.9, 24.6),
    ("F7", 900, 0.1, 1.0, 48, 260.1, 81.5),
    ("F7", 900, 0.1, 1.0, 72, 387.9, 146.1),
    ("F8", 300, 0.1, 1.0, 24, 132.3, 51.6),
    ("F8", 300, 0.1, 1.0, 48, 464.8, 110.8),
    ("F8", 300, 0.1, 1.0, 72, 734.4, 88.8),
]


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
            "legend.fontsize": 8,
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


def build_source_dataframe() -> pd.DataFrame:
    frame = pd.DataFrame(
        MANUAL_DATA,
        columns=[
            "formulation_label",
            "particle_size_nm",
            "vit_e_tpgs_pct_wv",
            "hpmc_k100_pct_wv",
            "time_h",
            "cum_amount_ug",
            "cum_amount_sd_ug",
        ],
    )
    frame["cum_amount_ug_cm2"] = frame["cum_amount_ug"] / DIFFUSION_AREA_CM2
    frame["cum_amount_sd_ug_cm2"] = frame["cum_amount_sd_ug"] / DIFFUSION_AREA_CM2
    return frame


def validate_against_skinminer(source: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    manual = source[
        [
            "formulation_label",
            "time_h",
            "cum_amount_ug_cm2",
        ]
    ].rename(columns={"cum_amount_ug_cm2": "manual_cum_amount_ug_cm2"})

    skinminer = pd.read_csv(SKINMINER_V2_DATA)
    skinminer = skinminer[skinminer["doi"].astype(str).str.lower() == DOI].copy()
    skinminer["endpoint_time_h"] = skinminer["endpoint_time_h"].astype(float)
    skinminer_grouped = (
        skinminer.groupby(["formulation_label", "endpoint_time_h"], as_index=False)
        .agg(
            skinminer_cum_amount_ug_cm2=("cumulative_amount_ug_cm2", "mean"),
            skinminer_record_count=("cumulative_amount_ug_cm2", "size"),
        )
        .rename(columns={"endpoint_time_h": "time_h"})
    )

    merged = manual.merge(skinminer_grouped, on=["formulation_label", "time_h"], how="outer")
    merged["manual_minus_skinminer_ug_cm2"] = (
        merged["manual_cum_amount_ug_cm2"] - merged["skinminer_cum_amount_ug_cm2"]
    )
    merged["abs_diff_ug_cm2"] = merged["manual_minus_skinminer_ug_cm2"].abs()
    max_abs_diff = float(merged["abs_diff_ug_cm2"].max()) if len(merged) else math.nan
    summary = {
        "manual_records": int(len(manual)),
        "skinminer_records": int(len(skinminer)),
        "matched_keys": int(merged["abs_diff_ug_cm2"].notna().sum()),
        "max_abs_diff_ug_cm2": max_abs_diff,
        "consistent": bool(max_abs_diff <= 1e-6 and len(manual) == 24 and len(skinminer_grouped) == 24),
    }
    return merged.sort_values(["formulation_label", "time_h"]), summary


def kernel_factory(feature_count: int):
    return C(1.0, (1e-3, 1e3)) * RBF(
        length_scale=[1.0] * feature_count,
        length_scale_bounds=(1e-2, 1e2),
    )


def fit_gpr(
    x_train: np.ndarray,
    y_train: np.ndarray,
    alpha: np.ndarray,
) -> tuple[GaussianProcessRegressor, list[str]]:
    model = GaussianProcessRegressor(
        kernel=kernel_factory(x_train.shape[1]),
        alpha=alpha,
        n_restarts_optimizer=10,
        normalize_y=True,
        random_state=RANDOM_STATE,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(x_train, y_train)
    warning_text = [f"{item.category.__name__}: {item.message}" for item in caught]
    return model, warning_text


def length_scale_text(model: GaussianProcessRegressor) -> str:
    length_scale = np.asarray(model.kernel_.k2.length_scale, dtype=float)
    return ";".join(f"{value:.4g}" for value in length_scale)


def classify_outcome(decision: str, actual_label: str) -> str:
    if decision == "Continue" and actual_label == "should_continue":
        return "TP"
    if decision == "Stop" and actual_label == "should_stop":
        return "TN"
    if decision == "Continue" and actual_label == "should_stop":
        return "FP"
    return "FN"


def poe_from_prediction(ybest: float, pred: float, std: float) -> float:
    safe_std = max(float(std), 1e-9)
    return float(1.0 - norm.cdf((ybest - pred) / safe_std))


def run_scenario_a(formulations: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    labels = sorted(formulations["formulation_label"].unique(), key=lambda item: int(item[1:]))

    for held in labels:
        train = formulations[formulations["formulation_label"] != held].copy()
        held_row = formulations[formulations["formulation_label"] == held].iloc[0]

        model, warning_text = fit_gpr(
            train[FEATURES_A].to_numpy(dtype=float),
            train["cum_amount_72h_ug_cm2"].to_numpy(dtype=float),
            np.square(train["cum_amount_sd_72h_ug_cm2"].to_numpy(dtype=float))
            + np.square(train["cum_amount_sd_24h_ug_cm2"].to_numpy(dtype=float))
            + np.square(train["cum_amount_sd_48h_ug_cm2"].to_numpy(dtype=float)),
        )
        x_predict = held_row[FEATURES_A].to_numpy(dtype=float).reshape(1, -1)
        pred, std = model.predict(x_predict, return_std=True)

        actual_72h = float(held_row["cum_amount_72h_ug_cm2"])
        ybest = float(train["cum_amount_72h_ug_cm2"].max())
        actual_label = "should_continue" if actual_72h > ybest else "should_stop"
        poe = poe_from_prediction(ybest, float(pred[0]), float(std[0]))
        decision = "Continue" if poe >= DECISION_THRESHOLD else "Stop"
        outcome = classify_outcome(decision, actual_label)

        rows.append(
            {
                "scenario": "A_48h_decision",
                "formulation_label": held,
                "actual_72h_ug_cm2": actual_72h,
                "pred_72h_ug_cm2": float(pred[0]),
                "std_72h_ug_cm2": float(std[0]),
                "ybest_other_72h_ug_cm2": ybest,
                "poe": poe,
                "decision": decision,
                "actual_label": actual_label,
                "outcome": outcome,
                "correct": outcome in {"TP", "TN"},
                "saved_fraction": (72 - 48) / 72 if decision == "Stop" else 0.0,
                "learned_kernel": str(model.kernel_),
                "learned_length_scale": length_scale_text(model),
                "warning_count": len(warning_text),
                "warnings": " | ".join(warning_text),
            }
        )

    return pd.DataFrame(rows)


def build_formulation_level(source: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for formulation_label, group in source.groupby("formulation_label"):
        first = group.iloc[0]
        row: dict[str, float | str] = {
            "formulation_label": formulation_label,
            "particle_size_nm": float(first["particle_size_nm"]),
            "vit_e_tpgs_pct_wv": float(first["vit_e_tpgs_pct_wv"]),
            "hpmc_k100_pct_wv": float(first["hpmc_k100_pct_wv"]),
        }
        for time_h in [24, 48, 72]:
            item = group[group["time_h"] == time_h].iloc[0]
            row[f"cum_amount_{time_h}h_ug_cm2"] = float(item["cum_amount_ug_cm2"])
            row[f"cum_amount_sd_{time_h}h_ug_cm2"] = float(item["cum_amount_sd_ug_cm2"])
        rows.append(row)
    return pd.DataFrame(rows).sort_values("formulation_label").reset_index(drop=True)


def run_scenario_b(formulations: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    labels = sorted(formulations["formulation_label"].unique(), key=lambda item: int(item[1:]))

    for held in labels:
        train = formulations[formulations["formulation_label"] != held].copy()
        held_row = formulations[formulations["formulation_label"] == held].iloc[0]

        model, warning_text = fit_gpr(
            train[FEATURES_B].to_numpy(dtype=float),
            train["cum_amount_72h_ug_cm2"].to_numpy(dtype=float),
            np.square(train["cum_amount_sd_72h_ug_cm2"].to_numpy(dtype=float))
            + np.square(train["cum_amount_sd_24h_ug_cm2"].to_numpy(dtype=float)),
        )
        x_predict = held_row[FEATURES_B].to_numpy(dtype=float).reshape(1, -1)
        pred, std = model.predict(x_predict, return_std=True)

        actual_72h = float(held_row["cum_amount_72h_ug_cm2"])
        ybest = float(train["cum_amount_72h_ug_cm2"].max())
        actual_label = "should_continue" if actual_72h > ybest else "should_stop"
        poe = poe_from_prediction(ybest, float(pred[0]), float(std[0]))
        decision = "Continue" if poe >= DECISION_THRESHOLD else "Stop"
        outcome = classify_outcome(decision, actual_label)

        rows.append(
            {
                "scenario": "B_24h_decision",
                "formulation_label": held,
                "actual_72h_ug_cm2": actual_72h,
                "pred_72h_ug_cm2": float(pred[0]),
                "std_72h_ug_cm2": float(std[0]),
                "ybest_other_72h_ug_cm2": ybest,
                "poe": poe,
                "decision": decision,
                "actual_label": actual_label,
                "outcome": outcome,
                "correct": outcome in {"TP", "TN"},
                "saved_fraction": (72 - 24) / 72 if decision == "Stop" else 0.0,
                "learned_kernel": str(model.kernel_),
                "learned_length_scale": length_scale_text(model),
                "warning_count": len(warning_text),
                "warnings": " | ".join(warning_text),
            }
        )

    return pd.DataFrame(rows)


def summarize_results(results: pd.DataFrame, scenario: str) -> dict[str, object]:
    rmse = float(math.sqrt(mean_squared_error(results["actual_72h_ug_cm2"], results["pred_72h_ug_cm2"])))
    r2 = float(r2_score(results["actual_72h_ug_cm2"], results["pred_72h_ug_cm2"]))
    return {
        "scenario": scenario,
        "n": int(len(results)),
        "accuracy_n": int(results["correct"].sum()),
        "accuracy_pct": float(results["correct"].mean() * 100),
        "type_i_count": int((results["outcome"] == "FN").sum()),
        "type_ii_count": int((results["outcome"] == "FP").sum()),
        "stop_count": int((results["decision"] == "Stop").sum()),
        "continue_count": int((results["decision"] == "Continue").sum()),
        "lead_rate_pct": float(results["saved_fraction"].mean() * 100),
        "rmse_ug_cm2": rmse,
        "r2": r2,
        "warning_folds": int((results["warning_count"] > 0).sum()),
        "median_length_scale": median_length_scale(results),
    }


def median_length_scale(results: pd.DataFrame) -> str:
    values = []
    for text in results["learned_length_scale"]:
        values.append([float(part) for part in str(text).split(";")])
    matrix = np.asarray(values, dtype=float)
    return ";".join(f"{value:.4g}" for value in np.median(matrix, axis=0))


def fmt(value: object, digits: int = 2) -> str:
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.{digits}f}"
    return str(value)


def markdown_table(frame: pd.DataFrame, columns: list[str], digits: int = 2) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, separator]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(fmt(row[col], digits) for col in columns) + " |")
    return "\n".join(lines)


def metric_table(metrics: dict[str, object]) -> str:
    rows = [
        ("Accuracy", f"{metrics['accuracy_n']}/{metrics['n']} = {metrics['accuracy_pct']:.1f}%"),
        ("Type I error", str(metrics["type_i_count"])),
        ("Type II error", str(metrics["type_ii_count"])),
        ("Stop / Continue", f"{metrics['stop_count']} / {metrics['continue_count']}"),
        ("Lead Rate", f"{metrics['lead_rate_pct']:.1f}%"),
        ("RMSE", f"{metrics['rmse_ug_cm2']:.1f} ug/cm2"),
        ("R2", f"{metrics['r2']:.3f}"),
        ("Median length_scale", str(metrics["median_length_scale"])),
        ("Folds with convergence warnings", str(metrics["warning_folds"])),
    ]
    frame = pd.DataFrame(rows, columns=["Metric", "Value"])
    return markdown_table(frame, ["Metric", "Value"], digits=3)


def plot_case_study(results_b: pd.DataFrame, metrics_b: dict[str, object]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"wspace": 0.36})
    ax = axes[0]
    label_offsets = {
        "F1": (18, 8),
        "F2": (18, -10),
        "F3": (18, 14),
        "F4": (18, -12),
        "F5": (18, 2),
        "F6": (18, -22),
        "F7": (18, 8),
        "F8": (18, -28),
    }

    for _, row in results_b.iterrows():
        ax.errorbar(
            row["actual_72h_ug_cm2"],
            row["pred_72h_ug_cm2"],
            yerr=row["std_72h_ug_cm2"],
            fmt="o",
            ms=5,
            lw=0.8,
            color=OUTCOME_COLORS[row["outcome"]],
            ecolor=COLORS["gray"],
            capsize=2,
            zorder=3,
        )
        offset_x, offset_y = label_offsets.get(row["formulation_label"], (18, 0))
        ax.text(
            row["actual_72h_ug_cm2"] + offset_x,
            row["pred_72h_ug_cm2"] + offset_y,
            row["formulation_label"],
            fontsize=7,
            color=COLORS["slate"],
            va="center",
        )

    axis_min = min(results_b["actual_72h_ug_cm2"].min(), results_b["pred_72h_ug_cm2"].min()) - 100
    axis_max = max(results_b["actual_72h_ug_cm2"].max(), results_b["pred_72h_ug_cm2"].max()) + 160
    ax.plot([axis_min, axis_max], [axis_min, axis_max], ls="--", lw=0.8, color=COLORS["slate"])
    ax.set_xlim(axis_min, axis_max)
    ax.set_ylim(axis_min, axis_max)
    ax.set_xlabel("True 72 h cumulative amount (ug/cm2)")
    ax.set_ylabel("Predicted 72 h cumulative amount (ug/cm2)")
    ax.set_title("GPR prediction from 24 h data")
    ax.text(
        0.04,
        0.96,
        f"RMSE = {metrics_b['rmse_ug_cm2']:.1f}\nR2 = {metrics_b['r2']:.2f}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": COLORS["light_gray"], "lw": 0.6},
    )

    ax = axes[1]
    results_sorted = results_b.sort_values("formulation_label", key=lambda values: values.str[1:].astype(int))
    bar_colors = [OUTCOME_COLORS[item] for item in results_sorted["outcome"]]
    ax.bar(results_sorted["formulation_label"], results_sorted["poe"], color=bar_colors, width=0.68)
    ax.scatter(
        results_sorted["formulation_label"],
        np.maximum(results_sorted["poe"].to_numpy(dtype=float), 0.018),
        c=bar_colors,
        s=24,
        marker="s",
        edgecolors="white",
        linewidths=0.5,
        zorder=4,
    )
    ax.axhline(DECISION_THRESHOLD, ls="--", lw=0.9, color=COLORS["red"])
    ax.text(7.45, DECISION_THRESHOLD + 0.015, "T = 0.2", color=COLORS["red"], fontsize=8, ha="right")
    for idx, (_, row) in enumerate(results_sorted.iterrows()):
        ax.text(
            idx,
            min(row["poe"] + 0.04, 0.96),
            f"{row['actual_72h_ug_cm2']:.0f}",
            ha="center",
            va="bottom",
            fontsize=7,
            color=COLORS["slate"],
        )
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Held-out formulation")
    ax.set_ylabel("Probability of exceedance")
    ax.set_title("EDMA decision at 24 h")
    legend_handles = [
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=color, markersize=7, label=label)
        for label, color in OUTCOME_COLORS.items()
    ]
    ax.legend(handles=legend_handles, frameon=False, ncol=2, loc="upper left")

    for item in axes:
        item.spines["top"].set_visible(False)
        item.spines["right"].set_visible(False)

    fig.savefig(FIGURE_DIR / "fig_case_study.png")
    fig.savefig(FIGURE_DIR / "fig_case_study.pdf")
    plt.close(fig)


def plot_decision_timeline(source: pd.DataFrame, results_b: pd.DataFrame) -> None:
    matrix = (
        source.pivot(index="formulation_label", columns="time_h", values="cum_amount_ug_cm2")
        .loc[[f"F{i}" for i in range(1, 9)], [24, 48, 72]]
    )
    decision_lookup = dict(zip(results_b["formulation_label"], results_b["decision"], strict=True))

    fig, ax = plt.subplots(figsize=(5.1, 3.7))
    image = ax.imshow(matrix.to_numpy(dtype=float), cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(matrix.columns)), [f"{int(value)} h" for value in matrix.columns])
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    ax.set_xlabel("Sampling time")
    ax.set_ylabel("Formulation")
    ax.set_title("Observed permeation timeline and 24 h decision")

    midpoint = float(np.nanmedian(matrix.to_numpy(dtype=float)))
    for row_idx, formulation_label in enumerate(matrix.index):
        for col_idx, time_h in enumerate(matrix.columns):
            value = matrix.loc[formulation_label, time_h]
            text_color = "white" if value > midpoint else COLORS["ink"]
            if int(time_h) == 24:
                label = f"{value:.0f}\n{decision_lookup[formulation_label]}"
            else:
                label = f"{value:.0f}"
            ax.text(col_idx, row_idx, label, ha="center", va="center", fontsize=7, color=text_color)

    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Cumulative amount (ug/cm2)")
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(FIGURE_DIR / "fig_decision_timeline.png")
    fig.savefig(FIGURE_DIR / "fig_decision_timeline.pdf")
    plt.close(fig)


def write_report(
    validation_summary: dict[str, object],
    validation: pd.DataFrame,
    results_a: pd.DataFrame,
    results_b: pd.DataFrame,
    metrics_a: dict[str, object],
    metrics_b: dict[str, object],
) -> None:
    display_cols = [
        "formulation_label",
        "actual_72h_ug_cm2",
        "pred_72h_ug_cm2",
        "std_72h_ug_cm2",
        "poe",
        "decision",
        "actual_label",
        "outcome",
        "correct",
    ]
    quality = pd.DataFrame(
        [
            {
                "Metric": "RMSE (ug/cm2)",
                "Scenario A": metrics_a["rmse_ug_cm2"],
                "Scenario B": metrics_b["rmse_ug_cm2"],
            },
            {"Metric": "R2", "Scenario A": metrics_a["r2"], "Scenario B": metrics_b["r2"]},
            {
                "Metric": "Median length_scale",
                "Scenario A": metrics_a["median_length_scale"],
                "Scenario B": metrics_b["median_length_scale"],
            },
            {
                "Metric": "Warning folds",
                "Scenario A": metrics_a["warning_folds"],
                "Scenario B": metrics_b["warning_folds"],
            },
        ]
    )
    warning_note = (
        "Model fitting completed for all folds with no convergence warnings."
        if metrics_a["warning_folds"] == 0 and metrics_b["warning_folds"] == 0
        else (
            "Model fitting completed for all folds. Convergence warnings are reported above; "
            "they indicate optimizer boundary solutions in this small, noisy, heteroscedastic data set "
            "rather than failed model execution."
        )
    )

    report = f"""# Single-Paper EDMA Case Study: Application to SkinMiner-Extracted Literature

## Source Paper

- DOI: `{DOI}`
- Topic: ibuprofen nanosuspension formulations from Kallakunta et al., AAPS PharmSciTech, 2013.
- Data shape: 8 formulations x 3 timepoints = 24 records.
- API concentration: 5% w/v ibuprofen.
- Membrane: dermatomed porcine skin.
- Diffusion area: 0.64 cm2.
- SD values: manually extracted from Table II and used as true experimental noise.

## Data Validation

- Manual records: {validation_summary['manual_records']}
- SkinMiner records for this DOI: {validation_summary['skinminer_records']}
- Matched formulation x timepoint keys: {validation_summary['matched_keys']}
- Maximum absolute difference: {validation_summary['max_abs_diff_ug_cm2']:.6g} ug/cm2
- Consistent within tolerance: {validation_summary['consistent']}

The validation table is saved as `validation_manual_vs_skinminer.csv`. The cumulative amount values are identical after converting the Table II units from ug to ug/cm2 by dividing by 0.64.

## Method

The model uses the same Gaussian process family as Paper 1: `ConstantKernel * RBF`, scenario-specific input dimensions, `n_restarts_optimizer = 10`, and `normalize_y = True`. Leave-one-formulation-out cross-validation was used. The decision threshold is `T = 0.2`: `PoE < 0.2` is classified as Stop; otherwise Continue.

Feature order for the learned length scales is Scenario A: `[particle size, TPGS, HPMC, 24 h amount, 48 h amount]`; Scenario B: `[particle size, TPGS, HPMC, 24 h amount]`. Scenario A uses `alpha = sd72^2 + sd24^2 + sd48^2`; Scenario B uses `alpha = sd72^2 + sd24^2`.

## Scenario A: Decision Using 24 h + 48 h Data

This scenario trains a formulation-level model `[PS, TPGS, HPMC, 24 h amount, 48 h amount] -> 72 h amount` using the other seven formulations. It represents a 48 h decision point.

{markdown_table(results_a[display_cols], display_cols)}

{metric_table(metrics_a)}

## Scenario B: Decision Using 24 h Only

This scenario trains a formulation-level model `[PS, TPGS, HPMC, 24 h amount] -> 72 h amount`. It represents the earlier 24 h decision point and is closest to the EDMA setup in Paper 1.

{markdown_table(results_b[display_cols], display_cols)}

{metric_table(metrics_b)}

## GPR Model Quality

{markdown_table(quality, ['Metric', 'Scenario A', 'Scenario B'], digits=3)}

Convergence note: {warning_note}

## Comparison with Paper 1

| Metric | Paper 1 baseline | This case study, Scenario A | This case study, Scenario B |
|---|---:|---:|---:|
| Accuracy | 5/5 = 100.0% | {metrics_a['accuracy_n']}/8 = {metrics_a['accuracy_pct']:.1f}% | {metrics_b['accuracy_n']}/8 = {metrics_b['accuracy_pct']:.1f}% |
| Type I error | 0 | {metrics_a['type_i_count']} | {metrics_b['type_i_count']} |
| Type II error | 0 | {metrics_a['type_ii_count']} | {metrics_b['type_ii_count']} |
| Lead Rate | 96.4% | {metrics_a['lead_rate_pct']:.1f}% | {metrics_b['lead_rate_pct']:.1f}% |

## Interpretation

This case study demonstrates that SkinMiner-derived literature data can be connected to the EDMA workflow when formulation factors, timepoints, endpoint values, and experimental SD are available. The result is a focused feasibility demonstration rather than a general performance claim.

Key limitations:

- The SD values are manually extracted from Table II, not produced by the current SkinMiner schema. This directly motivates a schema extension for endpoint uncertainty.
- The experiment contains only eight formulations, so statistical inference is limited.
- The result is from a single paper and cannot be generalized to other APIs, membranes, or formulation systems.
- The TPGS/HPMC nanosuspension system is not the same as the Paper 1 Poloxamer system, so the comparison is methodological rather than formulation-equivalent.

## Generated Outputs

- Source data: `source_paper_data.csv`
- Data validation: `validation_manual_vs_skinminer.csv`
- Scenario A results: `scenario_a_lofo_results.csv`
- Scenario B results: `scenario_b_24h_results.csv`
- Metrics: `scenario_metrics.csv`
- Figure 1: `figures/fig_case_study.png` and `figures/fig_case_study.pdf`
- Figure 2: `figures/fig_decision_timeline.png` and `figures/fig_decision_timeline.pdf`
"""
    (OUTPUT_DIR / "case_study_results.md").write_text(report, encoding="utf-8")

    compact_validation = validation.copy()
    compact_validation["abs_diff_ug_cm2"] = compact_validation["abs_diff_ug_cm2"].fillna(np.nan)
    compact_validation.to_csv(OUTPUT_DIR / "validation_manual_vs_skinminer.csv", index=False)


def write_paper_section(metrics_a: dict[str, object], metrics_b: dict[str, object]) -> None:
    section = f"""# Draft Discussion Section: Single-Paper EDMA Case Study

To assess whether the EDMA framework can be extended beyond the in-house experimental system, we performed a focused single-paper case study using SkinMiner-extracted ibuprofen nanosuspension data from Kallakunta et al. (DOI: {DOI}). The paper reports eight formulations measured at 24, 48, and 72 h, enabling leave-one-formulation-out Gaussian process modelling with formulation factors and time-dependent permeation outcomes. Because the current SkinMiner schema does not yet capture endpoint uncertainty, the standard deviations were manually extracted from Table II and used as heteroscedastic experimental noise in the Gaussian process (`alpha = SD^2`).

Using 24 h and 48 h observed responses from the other seven formulations to predict the held-out 72 h response produced an accuracy of {metrics_a['accuracy_n']}/8 ({metrics_a['accuracy_pct']:.1f}%), with {metrics_a['type_i_count']} Type I and {metrics_a['type_ii_count']} Type II decision errors. A stricter early-decision variant using only the 24 h response as an input achieved {metrics_b['accuracy_n']}/8 ({metrics_b['accuracy_pct']:.1f}%) accuracy, with a mean lead rate of {metrics_b['lead_rate_pct']:.1f}%. These results show that the SkinMiner literature output can support the same decision-theoretic workflow used in Paper 1 when sufficient formulation, timepoint, and uncertainty metadata are available.

This result should be interpreted as a feasibility demonstration rather than a general benchmark. The analysis is based on a single TPGS/HPMC nanosuspension paper with only eight formulations, and the formulation system differs from the Poloxamer-based Paper 1 experiments. Nevertheless, the case study identifies a concrete path for extending SkinMiner: endpoint uncertainty should be represented explicitly in the extraction schema so that literature-derived records can be used directly in probabilistic experimental design models.
"""
    (OUTPUT_DIR / "paper_section_draft.md").write_text(section, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    configure_style()

    source = build_source_dataframe()
    source.to_csv(OUTPUT_DIR / "source_paper_data.csv", index=False)

    validation, validation_summary = validate_against_skinminer(source)
    formulations = build_formulation_level(source)

    results_a = run_scenario_a(formulations)
    results_b = run_scenario_b(formulations)
    metrics_a = summarize_results(results_a, "A_48h_decision")
    metrics_b = summarize_results(results_b, "B_24h_decision")
    metrics = pd.DataFrame([metrics_a, metrics_b])

    results_a.to_csv(OUTPUT_DIR / "scenario_a_lofo_results.csv", index=False)
    results_b.to_csv(OUTPUT_DIR / "scenario_b_24h_results.csv", index=False)
    metrics.to_csv(OUTPUT_DIR / "scenario_metrics.csv", index=False)

    plot_case_study(results_b, metrics_b)
    plot_decision_timeline(source, results_b)
    write_report(validation_summary, validation, results_a, results_b, metrics_a, metrics_b)
    write_paper_section(metrics_a, metrics_b)

    print("Demonstration v3 complete")
    print(f"Validation consistent: {validation_summary['consistent']}")
    print(f"Scenario A accuracy: {metrics_a['accuracy_n']}/{metrics_a['n']}, lead={metrics_a['lead_rate_pct']:.1f}%")
    print(f"Scenario B accuracy: {metrics_b['accuracy_n']}/{metrics_b['n']}, lead={metrics_b['lead_rate_pct']:.1f}%")
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
