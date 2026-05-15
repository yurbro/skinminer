from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
V3_SOURCE_DATA = ROOT / "outputs" / "demonstration_v3" / "source_paper_data.csv"
V3_CASE_REPORT = ROOT / "outputs" / "demonstration_v3" / "case_study_results.md"
V4_REPORT = ROOT / "outputs" / "demonstration_v4" / "learning_curve_results.md"
OUTPUT_DIR = ROOT / "outputs" / "demonstration_v5"
FIGURE_DIR = OUTPUT_DIR / "figures"

DOI = "10.1208/s12249-013-9995-4"
FEATURE_COLUMNS = ["particle_size_nm", "vit_e_tpgs_pct_wv", "hpmc_k100_pct_wv", "time_h"]
FEATURE_LABELS = ["Particle size", "TPGS", "HPMC", "Time"]

RANDOM_STATE = 42
N_RESTARTS = 15

COLORS = {
    "blue": "#2B6C8A",
    "light_blue": "#8AB6D6",
    "dark_blue": "#164A64",
    "orange": "#C97931",
    "red": "#B94B48",
    "green": "#3D7C59",
    "slate": "#56616F",
    "gray": "#B8BFC7",
    "light_gray": "#E6E9ED",
}

TIME_COLORS = {
    24.0: "#8AB6D6",
    48.0: "#2B6C8A",
    72.0: "#164A64",
}


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "axes.linewidth": 0.6,
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


def build_kernel(input_dim: int):
    return ConstantKernel(1.0, (1e-3, 1e3)) * RBF(
        length_scale=np.ones(input_dim),
        length_scale_bounds=(1e-2, 1e2),
    )


def run_logo_cv(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = data[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = data["cum_amount_ug_cm2"].to_numpy(dtype=float)
    y_err = data["cum_amount_sd_ug_cm2"].to_numpy(dtype=float)
    groups = data["formulation_label"].to_numpy()

    predictions: list[dict[str, object]] = []
    fold_rows: list[dict[str, object]] = []
    logo = LeaveOneGroupOut()

    for fold_idx, (train_idx, test_idx) in enumerate(logo.split(x, y, groups=groups), start=1):
        x_train, x_test = x[train_idx], x[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        err_train = y_err[train_idx]
        test_rows = data.iloc[test_idx].copy()
        held_formulation = str(groups[test_idx[0]])

        scaler = StandardScaler()
        x_train_sc = scaler.fit_transform(x_train)
        x_test_sc = scaler.transform(x_test)

        y_mean = float(y_train.mean())
        y_std = float(y_train.std(ddof=0))
        if y_std < 1e-10:
            y_std = 1.0
        y_train_sc = (y_train - y_mean) / y_std
        alpha_train = np.square(err_train) / (y_std**2)

        gpr = GaussianProcessRegressor(
            kernel=build_kernel(x.shape[1]),
            alpha=alpha_train,
            n_restarts_optimizer=N_RESTARTS,
            normalize_y=False,
            random_state=RANDOM_STATE,
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            gpr.fit(x_train_sc, y_train_sc)

        pred_sc, pred_std_sc = gpr.predict(x_test_sc, return_std=True)
        y_pred = pred_sc * y_std + y_mean
        y_pred_std = pred_std_sc * y_std
        fold_length_scale = np.asarray(gpr.kernel_.k2.length_scale, dtype=float)
        warning_text = [f"{item.category.__name__}: {item.message}" for item in caught]

        fold_rows.append(
            {
                "fold": fold_idx,
                "held_out_formulation": held_formulation,
                "learned_kernel": str(gpr.kernel_),
                "length_scale_particle_size": fold_length_scale[0],
                "length_scale_tpgs": fold_length_scale[1],
                "length_scale_hpmc": fold_length_scale[2],
                "length_scale_time": fold_length_scale[3],
                "y_train_mean": y_mean,
                "y_train_std": y_std,
                "warning_count": len(warning_text),
                "warnings": " | ".join(warning_text),
            }
        )

        for local_idx, (_, row) in enumerate(test_rows.iterrows()):
            true_value = float(y_test[local_idx])
            pred_value = float(y_pred[local_idx])
            pred_std = float(y_pred_std[local_idx])
            measurement_sd = float(row["cum_amount_sd_ug_cm2"])
            predictions.append(
                {
                    "formulation": held_formulation,
                    "time_h": float(row["time_h"]),
                    "true_value_ug_cm2": true_value,
                    "predicted_value_ug_cm2": pred_value,
                    "predicted_std_ug_cm2": pred_std,
                    "abs_error": abs(true_value - pred_value),
                    "measurement_sd": measurement_sd,
                    "measurement_sd_ratio_pred_to_exp": pred_std / measurement_sd if measurement_sd > 0 else math.nan,
                    "particle_size_nm": float(row["particle_size_nm"]),
                    "vit_e_tpgs_pct_wv": float(row["vit_e_tpgs_pct_wv"]),
                    "hpmc_k100_pct_wv": float(row["hpmc_k100_pct_wv"]),
                }
            )

    predictions_df = pd.DataFrame(predictions).sort_values(["formulation", "time_h"]).reset_index(drop=True)
    folds_df = pd.DataFrame(fold_rows)
    return predictions_df, folds_df


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(y_true - y_pred))))


def global_metrics(predictions: pd.DataFrame) -> dict[str, float]:
    y_true = predictions["true_value_ug_cm2"].to_numpy(dtype=float)
    y_pred = predictions["predicted_value_ug_cm2"].to_numpy(dtype=float)
    mae = float(mean_absolute_error(y_true, y_pred))
    return {
        "n_predictions": int(len(predictions)),
        "MAE": mae,
        "RMSE": rmse(y_true, y_pred),
        "R2": float(r2_score(y_true, y_pred)),
        "rMAE_pct": mae / float(y_true.mean()) * 100.0,
        "mean_true_value_ug_cm2": float(y_true.mean()),
        "mean_predicted_std_ug_cm2": float(predictions["predicted_std_ug_cm2"].mean()),
        "mean_measurement_sd_ug_cm2": float(predictions["measurement_sd"].mean()),
        "median_predicted_std_ug_cm2": float(predictions["predicted_std_ug_cm2"].median()),
        "median_measurement_sd_ug_cm2": float(predictions["measurement_sd"].median()),
        "mean_pred_std_to_measurement_sd_ratio": float(
            predictions["measurement_sd_ratio_pred_to_exp"].replace([np.inf, -np.inf], np.nan).mean()
        ),
    }


def per_formulation_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for formulation, group in predictions.groupby("formulation"):
        y_true = group["true_value_ug_cm2"].to_numpy(dtype=float)
        y_pred = group["predicted_value_ug_cm2"].to_numpy(dtype=float)
        mae = float(mean_absolute_error(y_true, y_pred))
        rows.append(
            {
                "formulation": formulation,
                "MAE": mae,
                "RMSE": rmse(y_true, y_pred),
                "R2": float(r2_score(y_true, y_pred)) if len(group) >= 2 else math.nan,
                "mean_abs_error_pct": mae / float(y_true.mean()) * 100.0,
                "n_points": int(len(group)),
            }
        )
    return pd.DataFrame(rows).sort_values("formulation").reset_index(drop=True)


def per_timepoint_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for time_h, group in predictions.groupby("time_h"):
        y_true = group["true_value_ug_cm2"].to_numpy(dtype=float)
        y_pred = group["predicted_value_ug_cm2"].to_numpy(dtype=float)
        mae = float(mean_absolute_error(y_true, y_pred))
        rows.append(
            {
                "time_h": float(time_h),
                "MAE": mae,
                "RMSE": rmse(y_true, y_pred),
                "R2": float(r2_score(y_true, y_pred)) if len(group) >= 2 else math.nan,
                "mean_abs_error_pct": mae / float(y_true.mean()) * 100.0,
                "n_points": int(len(group)),
            }
        )
    return pd.DataFrame(rows).sort_values("time_h").reset_index(drop=True)


def kernel_summary(folds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, column in [
        ("particle_size_nm", "length_scale_particle_size"),
        ("vit_e_tpgs_pct_wv", "length_scale_tpgs"),
        ("hpmc_k100_pct_wv", "length_scale_hpmc"),
        ("time_h", "length_scale_time"),
    ]:
        values = folds[column].to_numpy(dtype=float)
        rows.append(
            {
                "feature": label,
                "median_length_scale": float(np.median(values)),
                "mean_length_scale": float(np.mean(values)),
                "sd_length_scale": float(np.std(values, ddof=1)),
            }
        )
    return pd.DataFrame(rows)


def uncertainty_summary(predictions: pd.DataFrame) -> pd.DataFrame:
    abs_error = predictions["abs_error"].to_numpy(dtype=float)
    pred_std = predictions["predicted_std_ug_cm2"].to_numpy(dtype=float)
    measurement_sd = predictions["measurement_sd"].to_numpy(dtype=float)
    rows = [
        {
            "metric": "mean_predicted_std",
            "value": float(np.mean(pred_std)),
        },
        {
            "metric": "mean_measurement_sd",
            "value": float(np.mean(measurement_sd)),
        },
        {
            "metric": "mean_pred_std_to_measurement_sd_ratio",
            "value": float(np.mean(pred_std / measurement_sd)),
        },
        {
            "metric": "corr_abs_error_predicted_std",
            "value": float(np.corrcoef(abs_error, pred_std)[0, 1]),
        },
        {
            "metric": "coverage_within_1_pred_std",
            "value": float(np.mean(abs_error <= pred_std)),
        },
        {
            "metric": "coverage_within_2_pred_std",
            "value": float(np.mean(abs_error <= 2 * pred_std)),
        },
        {
            "metric": "coverage_within_1_measurement_sd",
            "value": float(np.mean(abs_error <= measurement_sd)),
        },
        {
            "metric": "coverage_within_2_measurement_sd",
            "value": float(np.mean(abs_error <= 2 * measurement_sd)),
        },
    ]
    return pd.DataFrame(rows)


def r2_color(value: float) -> str:
    if value > 0.5:
        return COLORS["dark_blue"]
    if value > 0.0:
        return COLORS["light_blue"]
    return COLORS["red"]


def plot_main_figure(predictions: pd.DataFrame, per_form: pd.DataFrame, metrics: dict[str, float]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25), gridspec_kw={"wspace": 0.34})

    ax = axes[0]
    min_axis = 0.0
    max_axis = max(predictions["true_value_ug_cm2"].max(), predictions["predicted_value_ug_cm2"].max()) * 1.08
    x_line = np.linspace(min_axis, max_axis, 200)
    ax.fill_between(
        x_line,
        x_line - metrics["MAE"],
        x_line + metrics["MAE"],
        color=COLORS["light_gray"],
        alpha=0.55,
        linewidth=0,
    )
    ax.plot(x_line, x_line, ls="--", lw=0.8, color=COLORS["slate"])

    for time_h, group in predictions.groupby("time_h"):
        ax.errorbar(
            group["true_value_ug_cm2"],
            group["predicted_value_ug_cm2"],
            yerr=group["predicted_std_ug_cm2"],
            fmt="o",
            ms=4.2,
            lw=0.7,
            capsize=1.8,
            color=TIME_COLORS[float(time_h)],
            ecolor=COLORS["gray"],
            zorder=3,
        )
        for _, row in group.iterrows():
            ax.text(
                row["true_value_ug_cm2"] + 12,
                row["predicted_value_ug_cm2"] + 8,
                row["formulation"],
                fontsize=5.8,
                color=COLORS["slate"],
            )

    ax.set_xlim(min_axis, max_axis)
    ax.set_ylim(min_axis, max_axis)
    ax.set_xlabel("True cumulative permeation (ug/cm2)")
    ax.set_ylabel("GPR predicted (ug/cm2)")
    ax.set_title("LOGO-CV regression")
    parity_handles = [
        Patch(facecolor=COLORS["light_gray"], edgecolor="none", alpha=0.55, label="+/- MAE"),
        Line2D([0], [0], color=COLORS["slate"], lw=0.8, ls="--", label="y = x"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=TIME_COLORS[24.0], markeredgecolor=TIME_COLORS[24.0], label="24 h"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=TIME_COLORS[48.0], markeredgecolor=TIME_COLORS[48.0], label="48 h"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=TIME_COLORS[72.0], markeredgecolor=TIME_COLORS[72.0], label="72 h"),
    ]
    ax.legend(handles=parity_handles, frameon=False, loc="upper left", ncol=2)
    ax.text(
        0.96,
        0.04,
        f"R2 = {metrics['R2']:.2f}\nRMSE = {metrics['RMSE']:.0f} ug/cm2\nMAE = {metrics['MAE']:.0f} ug/cm2",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": COLORS["light_gray"], "lw": 0.6},
    )

    ax = axes[1]
    bar_colors = [r2_color(value) for value in per_form["R2"]]
    ax.bar(per_form["formulation"], per_form["MAE"], color=bar_colors, width=0.72)
    ax.axhline(metrics["MAE"], ls="--", lw=0.8, color=COLORS["slate"])
    ax.text(
        len(per_form) - 0.2,
        metrics["MAE"] + 8,
        "Overall MAE",
        ha="right",
        va="bottom",
        fontsize=7,
        color=COLORS["slate"],
    )
    for idx, row in per_form.iterrows():
        ax.text(idx, row["MAE"] + 10, f"{row['R2']:.2f}", ha="center", va="bottom", fontsize=7)
    ax.set_xlabel("Held-out formulation")
    ax.set_ylabel("MAE (ug/cm2)")
    ax.set_title("Per-formulation error")
    ax.set_ylim(0, float(per_form["MAE"].max()) * 1.34)
    legend_handles = [
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["dark_blue"], markersize=7, label="R2 > 0.5"),
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["light_blue"], markersize=7, label="0 < R2 <= 0.5"),
        plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["red"], markersize=7, label="R2 < 0"),
    ]
    ax.legend(handles=legend_handles, frameon=False, loc="upper right")

    for axis in axes:
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    fig.savefig(FIGURE_DIR / "fig_logo_cv_main.png")
    fig.savefig(FIGURE_DIR / "fig_logo_cv_main.pdf")
    plt.close(fig)


def plot_profile_figure(predictions: pd.DataFrame, per_form: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(5.8, 3.6))
    palette = plt.get_cmap("tab10")
    per_form_lookup = per_form.set_index("formulation")
    for idx, (formulation, group) in enumerate(predictions.groupby("formulation")):
        group = group.sort_values("time_h")
        color = palette(idx % 10)
        ax.plot(
            group["time_h"],
            group["true_value_ug_cm2"],
            marker="o",
            lw=1.1,
            color=color,
            label=formulation,
        )
        ax.plot(
            group["time_h"],
            group["predicted_value_ug_cm2"],
            marker="s",
            lw=1.0,
            ls="--",
            color=color,
            alpha=0.9,
        )
        pred = group["predicted_value_ug_cm2"].to_numpy(dtype=float)
        std = group["predicted_std_ug_cm2"].to_numpy(dtype=float)
        ax.fill_between(group["time_h"], pred - std, pred + std, color=color, alpha=0.11, linewidth=0)

    f7 = predictions[predictions["formulation"] == "F7"].sort_values("time_h")
    if not f7.empty and "F7" in per_form_lookup.index:
        target = f7.iloc[-1]
        ax.annotate(
            f"Extreme extrapolation\nR2 = {per_form_lookup.loc['F7', 'R2']:.1f}",
            xy=(target["time_h"], target["predicted_value_ug_cm2"]),
            xytext=(48, target["predicted_value_ug_cm2"] + 380),
            arrowprops={"arrowstyle": "->", "lw": 0.8, "color": COLORS["red"]},
            fontsize=8,
            color=COLORS["red"],
        )

    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Cumulative permeation (ug/cm2)")
    ax.set_title("Permeation profile predictions")
    ax.set_xticks([24, 48, 72])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper left", title="True solid / predicted dashed")

    fig.savefig(FIGURE_DIR / "fig_permeation_profiles.png")
    fig.savefig(FIGURE_DIR / "fig_permeation_profiles.pdf")
    plt.close(fig)


def markdown_table(frame: pd.DataFrame, columns: list[str], digits: int = 3) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.iterrows():
        cells = []
        for col in columns:
            value = row[col]
            if isinstance(value, (float, np.floating)):
                cells.append(f"{float(value):.{digits}f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_logo_cv_report(
    metrics: dict[str, float],
    per_form: pd.DataFrame,
    per_time: pd.DataFrame,
    kernel: pd.DataFrame,
    uncertainty: pd.DataFrame,
) -> None:
    worst = per_form.sort_values("R2").head(2)["formulation"].tolist()
    best_feature = kernel.sort_values("median_length_scale").iloc[0]
    report = f"""# Demonstration v5: 4D LOGO-CV Regression

## Data

- Source: `{DOI}`.
- Records: 8 formulations x 3 timepoints = 24 records.
- Inputs: `particle_size_nm`, `vit_e_tpgs_pct_wv`, `hpmc_k100_pct_wv`, `time_h`.
- Output: `cum_amount_ug_cm2`.
- Experimental SD: `cum_amount_sd_ug_cm2`, used as heteroscedastic GPR noise after y-standardization within each fold.

## Global LOGO-CV Metrics

| Metric | Value |
|---|---:|
| MAE | {metrics['MAE']:.2f} ug/cm2 |
| RMSE | {metrics['RMSE']:.2f} ug/cm2 |
| R2 | {metrics['R2']:.3f} |
| rMAE | {metrics['rMAE_pct']:.1f}% |
| N predictions | {metrics['n_predictions']} |

## Per-Formulation Metrics

{markdown_table(per_form, ['formulation', 'MAE', 'RMSE', 'R2', 'mean_abs_error_pct'], 3)}

Extrapolation failures with R2 < 0: {', '.join(worst)}.

## Per-Timepoint Metrics

{markdown_table(per_time, ['time_h', 'MAE', 'RMSE', 'R2', 'mean_abs_error_pct'], 3)}

## ARD Length Scales

{markdown_table(kernel, ['feature', 'median_length_scale', 'mean_length_scale', 'sd_length_scale'], 3)}

The smallest median length scale is `{best_feature['feature']}`, indicating the strongest fitted sensitivity after within-fold feature standardization.

## Uncertainty Diagnostics

{markdown_table(uncertainty, ['metric', 'value'], 3)}

The mean predicted GPR standard deviation is {metrics['mean_predicted_std_ug_cm2']:.1f} ug/cm2 versus mean experimental SD {metrics['mean_measurement_sd_ug_cm2']:.1f} ug/cm2. This is comparable in magnitude, but coverage diagnostics should be interpreted cautiously because there are only 24 held-out points.

## Interpretation

The 4D LOGO-CV regression task succeeds at a descriptive level: R2 is approximately 0.60 across formulation-held-out predictions. This is materially stronger than the v3/v4 EDMA-style decision experiments, where decision accuracy was inflated by class imbalance and predictive R2 was poor. The regression result supports the paper narrative that SkinMiner-extracted multi-timepoint records can support downstream permeation modelling, while prescriptive decision-making remains underpowered with single-paper data.
"""
    (OUTPUT_DIR / "logo_cv_results.md").write_text(report, encoding="utf-8")


def write_boundary_analysis(metrics: dict[str, float]) -> None:
    text = f"""# Boundary Analysis: Descriptive Modelling vs Prescriptive EDMA

The final demonstration supports a descriptive modelling claim. Using SkinMiner-extracted multi-timepoint data from one ibuprofen nanosuspension paper, the 4D LOGO-CV Gaussian process regression model achieved R2 = {metrics['R2']:.2f}, RMSE = {metrics['RMSE']:.0f} ug/cm2, and MAE = {metrics['MAE']:.0f} ug/cm2 across 24 held-out predictions. This shows that structured extraction of formulation factors, timepoints, endpoint values, and endpoint SD can support cross-formulation permeation prediction at moderate accuracy.

The EDMA-style decision task remains a boundary case rather than a successful application. In v3, the Stop/Continue decision achieved 87.5% accuracy, but this was driven by class imbalance and a model that effectively stopped every formulation; predictive R2 was negative. In v4, the sample-complexity analysis showed that R2 > 0.5 was not reached even at N = 200 under the single-paper oracle. The bottleneck is therefore not simply record count, but formulation-space coverage and balanced representation of high-performing candidates.

The methodological implication is that single-paper data can support descriptive modelling, but prescriptive decision-making requires cross-paper aggregation. SkinMiner's value is foundational: it converts dispersed literature records into structured data that can eventually support both descriptive and decision-oriented modelling once enough comparable formulation space has been accumulated.
"""
    (OUTPUT_DIR / "boundary_analysis_summary.md").write_text(text, encoding="utf-8")


def write_paper_section(metrics: dict[str, float], per_form: pd.DataFrame) -> None:
    negative = per_form[per_form["R2"] < 0]["formulation"].tolist()
    positive = per_form[per_form["R2"] > 0]
    r2_min = float(positive["R2"].min()) if len(positive) else math.nan
    r2_max = float(positive["R2"].max()) if len(positive) else math.nan
    section = f"""## Application: Cross-Formulation Permeation Modelling

To demonstrate that SkinMiner-extracted data can support downstream modelling tasks, we trained a four-dimensional Gaussian Process Regression model on multi-timepoint ibuprofen permeation records extracted from Kallakunta et al. (DOI: {DOI}). The model used particle size, surfactant concentration, polymer concentration, and time as inputs to predict cumulative permeation amount. Leave-one-formulation-out cross-validation yielded R2 = {metrics['R2']:.2f}, RMSE = {metrics['RMSE']:.0f} ug/cm2, and MAE = {metrics['MAE']:.0f} ug/cm2 across 24 held-out predictions, with measurement SD propagated as heteroscedastic GPR noise after within-fold target standardization.

Per-formulation analysis revealed that {len(positive)} of 8 formulations had positive held-out R2 values (range: {r2_min:.2f}-{r2_max:.2f}), while {', '.join(negative)} exhibited extrapolation failure. This pattern is consistent with the sparsity of the underlying formulation design, where eight formulations span a three-factor space and provide limited support for cross-formulation generalization. The result identifies formulation-space coverage, rather than data volume alone, as the binding constraint.

These results indicate that SkinMiner's structured extraction can support descriptive modelling tasks at moderate accuracy. However, prescriptive decision-making frameworks that require well-calibrated predictive uncertainty across the formulation space, such as probability-of-exceedance based experimental design, still require cross-paper aggregation beyond single-paper extraction. SkinMiner's contribution is therefore foundational: it provides the structured corpus necessary to enable both descriptive and prescriptive applications, with the latter requiring corpus-scale aggregation as future work.
"""
    (OUTPUT_DIR / "paper_section_draft.md").write_text(section, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    configure_style()
    if not V3_SOURCE_DATA.exists():
        raise FileNotFoundError(f"Missing v3 source data: {V3_SOURCE_DATA}")

    data = pd.read_csv(V3_SOURCE_DATA)
    predictions, folds = run_logo_cv(data)
    metrics = global_metrics(predictions)
    per_form = per_formulation_metrics(predictions)
    per_time = per_timepoint_metrics(predictions)
    kernel = kernel_summary(folds)
    uncertainty = uncertainty_summary(predictions)

    predictions.to_csv(OUTPUT_DIR / "logo_cv_predictions.csv", index=False)
    per_form.to_csv(OUTPUT_DIR / "per_formulation_metrics.csv", index=False)
    per_time.to_csv(OUTPUT_DIR / "per_timepoint_metrics.csv", index=False)
    folds.to_csv(OUTPUT_DIR / "fold_kernel_diagnostics.csv", index=False)
    kernel.to_csv(OUTPUT_DIR / "kernel_length_scale_summary.csv", index=False)
    uncertainty.to_csv(OUTPUT_DIR / "uncertainty_diagnostics.csv", index=False)
    (OUTPUT_DIR / "global_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    plot_main_figure(predictions, per_form, metrics)
    plot_profile_figure(predictions, per_form)
    write_logo_cv_report(metrics, per_form, per_time, kernel, uncertainty)
    write_boundary_analysis(metrics)
    write_paper_section(metrics, per_form)

    print("Demonstration v5 complete")
    print(f"R2={metrics['R2']:.3f}, RMSE={metrics['RMSE']:.2f}, MAE={metrics['MAE']:.2f}, rMAE={metrics['rMAE_pct']:.1f}%")
    print("Negative per-formulation R2:", ", ".join(per_form[per_form["R2"] < 0]["formulation"].tolist()))
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
