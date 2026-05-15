from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.linalg import cho_solve
from scipy.stats import norm, qmc
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C


ROOT = Path(__file__).resolve().parents[1]
V3_DIR = ROOT / "outputs" / "demonstration_v3"
OUTPUT_DIR = ROOT / "outputs" / "demonstration_v4"
FIGURE_DIR = OUTPUT_DIR / "figures"
V3_SOURCE_DATA = V3_DIR / "source_paper_data.csv"
V2_LITERATURE_DATA = ROOT / "outputs" / "demonstration_v2" / "literature_ibuprofen_data.csv"

DOI = "10.1208/s12249-013-9995-4"
N_VALUES = [5, 8, 10, 15, 20, 30, 50, 80, 100, 150, 200]
N_REPEATS = 50
TIMEPOINTS = [24.0, 48.0, 72.0]
DECISION_THRESHOLD = 0.2
ORACLE_RESTARTS = 20
LEARNER_RESTARTS = 10
RANDOM_STATE = 42

FORMULATION_RANGES = {
    "PS": (200.0, 1000.0),
    "TPGS": (0.05, 2.5),
    "HPMC": (0.5, 3.5),
}

COLORS = {
    "blue": "#2B6C8A",
    "orange": "#C97931",
    "green": "#3D7C59",
    "red": "#B94B48",
    "slate": "#56616F",
    "gray": "#B8BFC7",
    "light_gray": "#E6E9ED",
}

DECISION_COLORS = {
    "tp": COLORS["green"],
    "tn": COLORS["blue"],
    "fp": COLORS["orange"],
    "fn": COLORS["red"],
}


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


def make_gpr(input_dim: int, alpha: np.ndarray | float, n_restarts: int) -> GaussianProcessRegressor:
    kernel = C(1.0, (1e-3, 1e3)) * RBF(
        length_scale=[1.0] * input_dim,
        length_scale_bounds=(1e-2, 1e2),
    )
    return GaussianProcessRegressor(
        kernel=kernel,
        alpha=alpha,
        n_restarts_optimizer=n_restarts,
        normalize_y=True,
        random_state=RANDOM_STATE,
    )


def normalized_alpha_from_sd(sd: np.ndarray, y: np.ndarray) -> np.ndarray:
    y_scale = float(np.std(y))
    if y_scale <= 0:
        return np.square(sd)
    return np.square(sd / y_scale)


def fit_with_warnings(model: GaussianProcessRegressor, x: np.ndarray, y: np.ndarray) -> list[str]:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(x, y)
    return [f"{item.category.__name__}: {item.message}" for item in caught]


def length_scale_text(model: GaussianProcessRegressor) -> str:
    return ";".join(f"{value:.4g}" for value in np.asarray(model.kernel_.k2.length_scale, dtype=float))


def fit_oracle(data: pd.DataFrame) -> tuple[GaussianProcessRegressor, dict[str, object]]:
    x_oracle = data[["particle_size_nm", "vit_e_tpgs_pct_wv", "hpmc_k100_pct_wv", "time_h"]].to_numpy(
        dtype=float
    )
    y_oracle = data["cum_amount_ug_cm2"].to_numpy(dtype=float)
    sd_oracle = data["cum_amount_sd_ug_cm2"].to_numpy(dtype=float)
    alpha_oracle = normalized_alpha_from_sd(sd_oracle, y_oracle)
    oracle = make_gpr(4, alpha_oracle, ORACLE_RESTARTS)
    warning_text = fit_with_warnings(oracle, x_oracle, y_oracle)

    raw_alpha_diagnostic = make_gpr(4, np.square(sd_oracle), 5)
    fit_with_warnings(raw_alpha_diagnostic, x_oracle, y_oracle)
    summary = {
        "doi": DOI,
        "n_records": int(len(data)),
        "input_dimensions": 4,
        "n_restarts_optimizer": ORACLE_RESTARTS,
        "alpha_scaling": "alpha = (SD / y_std)^2 because sklearn normalize_y=True standardizes targets",
        "y_std_for_alpha": float(np.std(y_oracle)),
        "in_sample_r2": float(oracle.score(x_oracle, y_oracle)),
        "raw_sd2_alpha_in_sample_r2_diagnostic": float(raw_alpha_diagnostic.score(x_oracle, y_oracle)),
        "learned_kernel": str(oracle.kernel_),
        "learned_length_scale": length_scale_text(oracle),
        "warning_count": len(warning_text),
        "warnings": warning_text,
    }
    return oracle, summary


def query_oracle(oracle: GaussianProcessRegressor, formulation: np.ndarray) -> np.ndarray:
    queries = np.array([[formulation[0], formulation[1], formulation[2], time_h] for time_h in TIMEPOINTS])
    values = oracle.predict(queries)
    return np.maximum(values, 1e-6)


def build_synthetic_dataset(
    oracle: GaussianProcessRegressor,
    n_formulations: int,
    repeat: int,
    typical_sd_pct: float,
) -> pd.DataFrame:
    sampler = qmc.LatinHypercube(d=3, seed=repeat * 1000 + n_formulations)
    unit_samples = sampler.random(n_formulations)
    synth_formulations = qmc.scale(
        unit_samples,
        [FORMULATION_RANGES["PS"][0], FORMULATION_RANGES["TPGS"][0], FORMULATION_RANGES["HPMC"][0]],
        [FORMULATION_RANGES["PS"][1], FORMULATION_RANGES["TPGS"][1], FORMULATION_RANGES["HPMC"][1]],
    )

    rows: list[dict[str, float | int]] = []
    for f_idx, formulation in enumerate(synth_formulations):
        y_true = query_oracle(oracle, formulation)
        noise_std = np.maximum(np.abs(y_true) * typical_sd_pct, 1e-6)
        rng = np.random.RandomState(repeat * 10000 + f_idx)
        y_obs = np.maximum(y_true + rng.normal(0.0, noise_std), 1e-6)
        rows.append(
            {
                "f_idx": f_idx,
                "PS": formulation[0],
                "TPGS": formulation[1],
                "HPMC": formulation[2],
                "amount_24h": y_obs[0],
                "amount_48h": y_obs[1],
                "amount_72h": y_obs[2],
                "oracle_24h": y_true[0],
                "oracle_48h": y_true[1],
                "oracle_72h": y_true[2],
                "sd_24h": noise_std[0],
                "sd_48h": noise_std[1],
                "sd_72h": noise_std[2],
            }
        )
    return pd.DataFrame(rows)


def loo_predictions(model: GaussianProcessRegressor) -> tuple[np.ndarray, np.ndarray]:
    # Exact leave-one-out predictions for a fitted GPR with fixed hyperparameters.
    k_inv = cho_solve((model.L_, True), np.eye(model.X_train_.shape[0]), check_finite=False)
    diag = np.maximum(np.diag(k_inv), 1e-12)
    loo_mean_norm = model.y_train_ - model.alpha_ / diag
    loo_std_norm = np.sqrt(1.0 / diag)
    y_mean = np.asarray(model._y_train_mean)
    y_std = np.asarray(model._y_train_std)
    return loo_mean_norm * y_std + y_mean, loo_std_norm * y_std


def scenario_arrays(synth_df: pd.DataFrame, scenario: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if scenario == "A":
        feature_cols = ["PS", "TPGS", "HPMC", "amount_24h", "amount_48h"]
    elif scenario == "B":
        feature_cols = ["PS", "TPGS", "HPMC", "amount_24h"]
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    x = synth_df[feature_cols].to_numpy(dtype=float)
    y = synth_df["amount_72h"].to_numpy(dtype=float)
    alpha = normalized_alpha_from_sd(synth_df["sd_72h"].to_numpy(dtype=float), y)
    return x, y, alpha


def evaluate_scenario(synth_df: pd.DataFrame, n_formulations: int, repeat: int, scenario: str) -> dict[str, object]:
    x, actuals, alpha = scenario_arrays(synth_df, scenario)
    model = make_gpr(x.shape[1], alpha, LEARNER_RESTARTS)
    warning_text = fit_with_warnings(model, x, actuals)
    pred_mean, pred_std = loo_predictions(model)

    decisions: list[str] = []
    actual_labels: list[str] = []
    for held_idx, actual in enumerate(actuals):
        train_values = np.delete(actuals, held_idx)
        ybest = float(train_values.max())
        poe = float(1.0 - norm.cdf((ybest - pred_mean[held_idx]) / max(pred_std[held_idx], 1e-6)))
        decisions.append("Stop" if poe < DECISION_THRESHOLD else "Continue")
        actual_labels.append("should_continue" if actual > ybest else "should_stop")

    decisions_array = np.asarray(decisions)
    labels_array = np.asarray(actual_labels)
    correct = (
        ((decisions_array == "Stop") & (labels_array == "should_stop"))
        | ((decisions_array == "Continue") & (labels_array == "should_continue"))
    )
    type1 = (decisions_array == "Stop") & (labels_array == "should_continue")
    type2 = (decisions_array == "Continue") & (labels_array == "should_stop")
    tp = (decisions_array == "Continue") & (labels_array == "should_continue")
    tn = (decisions_array == "Stop") & (labels_array == "should_stop")

    ss_res = float(np.sum(np.square(actuals - pred_mean)))
    ss_tot = float(np.sum(np.square(actuals - actuals.mean())))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else math.nan
    rmse = float(np.sqrt(np.mean(np.square(actuals - pred_mean))))
    stops = int((decisions_array == "Stop").sum())
    time_saved_per_stop = (72 - 48) / 72 if scenario == "A" else (72 - 24) / 72

    return {
        "N": n_formulations,
        "repeat": repeat,
        "scenario": scenario,
        "accuracy": float(correct.mean()),
        "rmse": rmse,
        "r2": r2,
        "type1": int(type1.sum()),
        "type2": int(type2.sum()),
        "tp": int(tp.sum()),
        "tn": int(tn.sum()),
        "fp": int(type2.sum()),
        "fn": int(type1.sum()),
        "tp_rate": float(tp.mean()),
        "tn_rate": float(tn.mean()),
        "fp_rate": float(type2.mean()),
        "fn_rate": float(type1.mean()),
        "lead_rate": float((stops / len(decisions)) * time_saved_per_stop),
        "stop_rate": float(stops / len(decisions)),
        "continue_rate": float((decisions_array == "Continue").mean()),
        "n_should_continue": int((labels_array == "should_continue").sum()),
        "n_successful_predictions": int(len(pred_mean)),
        "learned_kernel": str(model.kernel_),
        "learned_length_scale": length_scale_text(model),
        "warning_count": len(warning_text),
    }


def run_learning_curve(oracle: GaussianProcessRegressor, typical_sd_pct: float) -> pd.DataFrame:
    results: list[dict[str, object]] = []
    total = len(N_VALUES) * N_REPEATS
    completed = 0
    for n_formulations in N_VALUES:
        for repeat in range(N_REPEATS):
            synth_df = build_synthetic_dataset(oracle, n_formulations, repeat, typical_sd_pct)
            for scenario in ["A", "B"]:
                try:
                    results.append(evaluate_scenario(synth_df, n_formulations, repeat, scenario))
                except Exception as exc:  # Keep long simulations robust and auditable.
                    results.append(
                        {
                            "N": n_formulations,
                            "repeat": repeat,
                            "scenario": scenario,
                            "error": repr(exc),
                        }
                    )
            completed += 1
            if completed % 50 == 0 or completed == total:
                print(f"Completed synthetic datasets: {completed}/{total}")
    return pd.DataFrame(results)


def aggregate_results(results: pd.DataFrame) -> pd.DataFrame:
    valid = results[results["accuracy"].notna()].copy()
    agg_map = {
        "accuracy": ["mean", "std"],
        "rmse": ["mean", "std"],
        "r2": ["mean", "std"],
        "type1": ["mean", "std"],
        "type2": ["mean", "std"],
        "lead_rate": ["mean", "std"],
        "tp_rate": ["mean", "std"],
        "tn_rate": ["mean", "std"],
        "fp_rate": ["mean", "std"],
        "fn_rate": ["mean", "std"],
        "stop_rate": ["mean", "std"],
        "continue_rate": ["mean", "std"],
        "n_should_continue": ["mean", "std"],
        "warning_count": ["mean", "sum"],
    }
    summary = valid.groupby(["scenario", "N"], as_index=False).agg(agg_map)
    summary.columns = [
        "_".join([part for part in col if part]).rstrip("_") if isinstance(col, tuple) else col
        for col in summary.columns
    ]
    return summary


def identify_thresholds(summary: pd.DataFrame) -> pd.DataFrame:
    targets = [
        ("R2 > 0", "r2_mean", 0.0, ">"),
        ("R2 > 0.5", "r2_mean", 0.5, ">"),
        ("Accuracy >= 0.9", "accuracy_mean", 0.9, ">="),
    ]
    rows = []
    for scenario in ["A", "B"]:
        scenario_summary = summary[summary["scenario"] == scenario].sort_values("N")
        for target_name, col, threshold, op in targets:
            min_n: int | None = None
            for _, row in scenario_summary.iterrows():
                value = float(row[col])
                reached = value > threshold if op == ">" else value >= threshold
                if reached:
                    min_n = int(row["N"])
                    break
            rows.append({"scenario": scenario, "target": target_name, "min_N": min_n})
    return pd.DataFrame(rows)


def format_threshold(thresholds: pd.DataFrame, scenario: str, target: str) -> str:
    value = thresholds[(thresholds["scenario"] == scenario) & (thresholds["target"] == target)]["min_N"].iloc[0]
    if pd.isna(value):
        return "Not reached"
    return str(int(value))


def fmt_mean_sd(mean: float, sd: float, digits: int = 3) -> str:
    return f"{mean:.{digits}f} +/- {sd:.{digits}f}"


def scenario_summary_table(summary: pd.DataFrame, scenario: str) -> str:
    subset = summary[summary["scenario"] == scenario].sort_values("N").copy()
    lines = [
        "| N | Mean R2 +/- SD | Mean RMSE | Mean Accuracy | Mean Type I | Mean Type II | Mean Lead Rate |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in subset.iterrows():
        lines.append(
            "| "
            + " | ".join(
                [
                    str(int(row["N"])),
                    fmt_mean_sd(row["r2_mean"], row["r2_std"], 3),
                    f"{row['rmse_mean']:.1f}",
                    f"{row['accuracy_mean']:.3f}",
                    f"{row['type1_mean']:.2f}",
                    f"{row['type2_mean']:.2f}",
                    f"{row['lead_rate_mean'] * 100:.1f}%",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def get_min_n(thresholds: pd.DataFrame, scenario: str, target: str) -> float | None:
    value = thresholds[(thresholds["scenario"] == scenario) & (thresholds["target"] == target)]["min_N"].iloc[0]
    return None if pd.isna(value) else float(value)


def plot_learning_curve(summary: pd.DataFrame, thresholds: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"wspace": 0.34})
    scenario_styles = {
        "A": {"label": "Scenario A: 48 h decision", "color": COLORS["blue"], "linestyle": "-"},
        "B": {"label": "Scenario B: 24 h decision", "color": COLORS["orange"], "linestyle": "--"},
    }

    ax = axes[0]
    for scenario, style in scenario_styles.items():
        subset = summary[summary["scenario"] == scenario].sort_values("N")
        x = subset["N"].to_numpy(dtype=float)
        y = subset["r2_mean"].to_numpy(dtype=float)
        sd = subset["r2_std"].fillna(0).to_numpy(dtype=float)
        ax.plot(x, y, label=style["label"], color=style["color"], linestyle=style["linestyle"], marker="o", ms=3)
        ax.fill_between(x, y - sd, y + sd, color=style["color"], alpha=0.16, linewidth=0)
        min_n = get_min_n(thresholds, scenario, "R2 > 0.5")
        if min_n is not None:
            y_at_min = float(subset[subset["N"] == min_n]["r2_mean"].iloc[0])
            ax.annotate(
                f"N={int(min_n)}",
                xy=(min_n, y_at_min),
                xytext=(min_n * 1.12, 0.56 if scenario == "A" else 0.42),
                arrowprops={"arrowstyle": "->", "lw": 0.7, "color": style["color"]},
                color=style["color"],
                fontsize=8,
            )
    for line_y, label in [(0.0, "R2=0"), (0.5, "R2=0.5"), (0.9, "R2=0.9")]:
        ax.axhline(line_y, color=COLORS["gray"], lw=0.7, ls=":")
        ax.text(N_VALUES[-1] * 1.02, line_y, label, va="center", fontsize=7, color=COLORS["slate"])
    ax.set_xscale("log")
    ax.set_xticks(N_VALUES, [str(value) for value in N_VALUES], rotation=35)
    ax.set_xlabel("N formulations")
    ax.set_ylabel("LOO predictive R2")
    ax.set_title("Predictive learning curve")
    ax.set_ylim(-0.06, 1.03)
    ax.legend(frameon=False, loc="upper left")

    ax = axes[1]
    for scenario, style in scenario_styles.items():
        subset = summary[summary["scenario"] == scenario].sort_values("N")
        x = subset["N"].to_numpy(dtype=float)
        y = subset["accuracy_mean"].to_numpy(dtype=float)
        sd = subset["accuracy_std"].fillna(0).to_numpy(dtype=float)
        ax.plot(x, y, label=style["label"], color=style["color"], linestyle=style["linestyle"], marker="o", ms=3)
        ax.fill_between(x, y - sd, y + sd, color=style["color"], alpha=0.16, linewidth=0)
        min_n = get_min_n(thresholds, scenario, "Accuracy >= 0.9")
        if min_n is not None:
            y_at_min = float(subset[subset["N"] == min_n]["accuracy_mean"].iloc[0])
            ax.annotate(
                f"N={int(min_n)}",
                xy=(min_n, y_at_min),
                xytext=(min_n * 1.12, 0.91 if scenario == "A" else 0.83),
                arrowprops={"arrowstyle": "->", "lw": 0.7, "color": style["color"]},
                color=style["color"],
                fontsize=8,
            )
    ax.axhline(0.9, color=COLORS["red"], lw=0.8, ls="--")
    ax.text(55, 0.918, "Accuracy = 0.9", va="center", fontsize=7, color=COLORS["red"])
    ax.set_xscale("log")
    ax.set_xticks(N_VALUES, [str(value) for value in N_VALUES], rotation=35)
    ax.set_ylim(0.0, 1.03)
    ax.set_xlabel("N formulations")
    ax.set_ylabel("Decision accuracy")
    ax.set_title("Decision learning curve")

    for axis in axes:
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    fig.savefig(FIGURE_DIR / "fig_learning_curve.png")
    fig.savefig(FIGURE_DIR / "fig_learning_curve.pdf")
    plt.close(fig)


def plot_error_composition(summary: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharey=True, gridspec_kw={"wspace": 0.16})
    for ax, scenario, title in [
        (axes[0], "A", "Scenario A: 48 h decision"),
        (axes[1], "B", "Scenario B: 24 h decision"),
    ]:
        subset = summary[summary["scenario"] == scenario].sort_values("N").copy()
        x = np.arange(len(subset))
        bottoms = np.zeros(len(subset))
        for key, label in [("tp", "TP"), ("tn", "TN"), ("fp", "FP"), ("fn", "FN")]:
            values = subset[f"{key}_rate_mean"].to_numpy(dtype=float)
            ax.bar(x, values, bottom=bottoms, color=DECISION_COLORS[key], width=0.72, label=label)
            bottoms += values
        ax.set_xticks(x, [str(int(value)) for value in subset["N"]], rotation=35)
        ax.set_xlabel("N formulations")
        ax.set_title(title)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].set_ylabel("Mean decision proportion")
    axes[1].legend(frameon=False, loc="center left", bbox_to_anchor=(1.0, 0.5))

    fig.savefig(FIGURE_DIR / "fig_error_composition.png")
    fig.savefig(FIGURE_DIR / "fig_error_composition.pdf")
    plt.close(fig)


def threshold_pivot_markdown(thresholds: pd.DataFrame) -> str:
    rows = []
    for target in ["R2 > 0", "R2 > 0.5", "Accuracy >= 0.9"]:
        rows.append(
            {
                "Target": target,
                "Scenario A min N": format_threshold(thresholds, "A", target),
                "Scenario B min N": format_threshold(thresholds, "B", target),
            }
        )
    frame = pd.DataFrame(rows)
    return frame.to_markdown(index=False)


def skinminer_formulation_counts() -> pd.DataFrame:
    if not V2_LITERATURE_DATA.exists():
        return pd.DataFrame()
    data = pd.read_csv(V2_LITERATURE_DATA)
    if "doi" not in data.columns or "formulation_label" not in data.columns:
        return pd.DataFrame()
    counts = (
        data.groupby("doi", as_index=False)
        .agg(records=("formulation_label", "size"), formulations=("formulation_label", "nunique"))
        .sort_values("formulations", ascending=False)
    )
    return counts


def write_report(
    oracle_summary: dict[str, object],
    typical_sd_pct: float,
    summary: pd.DataFrame,
    thresholds: pd.DataFrame,
    formulation_counts: pd.DataFrame,
) -> None:
    r2_a = format_threshold(thresholds, "A", "R2 > 0.5")
    r2_b = format_threshold(thresholds, "B", "R2 > 0.5")
    acc_a = format_threshold(thresholds, "A", "Accuracy >= 0.9")
    acc_b = format_threshold(thresholds, "B", "Accuracy >= 0.9")

    if formulation_counts.empty:
        formulation_count_text = "- Current single-paper formulation count: 8 formulations in the v3 case-study paper."
    else:
        counts_table = formulation_counts.to_markdown(index=False)
        formulation_count_text = (
            "- Formulation counts in the current v2 ibuprofen demonstration extraction:\n\n"
            f"{counts_table}\n\n"
            f"- The v3 case-study paper contains 8 formulations."
        )

    report = f"""# Sample Complexity Analysis for EDMA-GPR on Literature Data

## Reference GPR (Oracle)

- Trained on: {oracle_summary['n_records']} records from `{DOI}`
- Input dimensions: 4 (`PS`, `TPGS`, `HPMC`, `time`)
- Learned length_scale: `{oracle_summary['learned_length_scale']}`
- In-sample R2: {oracle_summary['in_sample_r2']:.3f}
- Alpha scaling: `{oracle_summary['alpha_scaling']}`
- Raw `SD^2` diagnostic R2 without scaling: {oracle_summary['raw_sd2_alpha_in_sample_r2_diagnostic']:.3f}
- Optimizer restarts: {oracle_summary['n_restarts_optimizer']}
- Convergence warning count: {oracle_summary['warning_count']}
- Role: synthetic proxy for the formulation-time-permeation relationship

## Method

- Sampled N formulations from `[PS, TPGS, HPMC]` space using Latin Hypercube sampling.
- Queried the oracle at 24 h, 48 h, and 72 h.
- Added synthetic observation noise using the median relative SD from the source paper: {typical_sd_pct * 100:.1f}%.
- Because `sklearn` standardizes the target when `normalize_y=True`, experimental SD was converted to normalized alpha as `(SD / y_std)^2`; using raw `SD^2` makes the oracle collapse to a mean model.
- Trained formulation-level GPR models for two scenarios:
- Scenario A: `[PS, TPGS, HPMC, 24 h amount, 48 h amount] -> 72 h amount`, decision at 48 h, 33.3% lead time per Stop.
- Scenario B: `[PS, TPGS, HPMC, 24 h amount] -> 72 h amount`, decision at 24 h, 66.7% lead time per Stop.
- Repeats: {N_REPEATS} per N value per scenario.
- Implementation note: for tractability, each synthetic dataset/scenario was fitted once and leave-one-out predictions were computed with the exact GPR LOO formula under the fitted hyperparameters. This avoids the prohibitively expensive naive loop of refitting tens of thousands of GPRs.

## Learning Curve Results

### Scenario A (5-dim, 48 h decision)

{scenario_summary_table(summary, "A")}

### Scenario B (4-dim, 24 h decision)

{scenario_summary_table(summary, "B")}

## Sample Size Thresholds

{threshold_pivot_markdown(thresholds)}

## Comparison with Real Data Availability

{formulation_count_text}

- Required N for Scenario A R2 > 0.5: {r2_a}
- Required N for Scenario B R2 > 0.5: {r2_b}
- Required N for Scenario A accuracy >= 0.9: {acc_a}
- Required N for Scenario B accuracy >= 0.9: {acc_b}
- Implication: single-paper data is insufficient for a stable EDMA-GPR model under this synthetic proxy; multi-paper aggregation is necessary.

## Scenario Comparison

Scenario A uses more information because it observes both 24 h and 48 h permeation before predicting 72 h. It therefore has a later decision point and a lower per-Stop lead rate, but should be statistically easier than Scenario B. Scenario B makes an earlier 24 h decision and preserves a larger lead rate, but it has less observed response information and therefore requires at least as much data to reach comparable predictive power.

Observed thresholds:

- R2 > 0.5: Scenario A = {r2_a}; Scenario B = {r2_b}
- Accuracy >= 0.9: Scenario A = {acc_a}; Scenario B = {acc_b}

Important interpretation: the accuracy threshold is not sufficient evidence of useful EDMA behaviour here. Each LOFO synthetic dataset has only one "should_continue" formulation, so a model that mostly stops candidates can achieve high accuracy as N grows. The R2 curves remain near zero and R2 > 0.5 is not reached by N = 200 in either scenario. Therefore the defensible sample-complexity conclusion should be based on predictive R2, not accuracy alone.

## Limitations

- This is a conditional analysis based on one paper; it cannot be generalized to all ibuprofen formulations.
- The reference GPR is a learned proxy, not a physical ground truth.
- The conclusion should be read as: if this paper's relationship complexity is representative, the model needs approximately the reported N.
- Synthetic noise is based on the source paper's typical relative SD; real cross-paper noise may be larger and structured.
- Cross-paper heterogeneity in membranes, dose, vehicles, and assay settings is not modelled.
- The analytic LOO implementation fits hyperparameters on the full synthetic dataset before computing LOO predictions, so the predictive estimates may be slightly optimistic compared with full nested LOFO hyperparameter refitting.

## Conclusion

The v3 result showed that eight formulations are insufficient for a meaningful EDMA-GPR model: predictive R2 was negative and the decision model stopped every held-out formulation. The sample complexity analysis supports the same interpretation at larger scale. Under the learned single-paper oracle, R2 > 0.5 is not reached even at N = 200, so this experiment does not support a precise minimum-N claim for predictive modelling. It supports a more conservative conclusion: single-paper data are underpowered, and EDMA-style decision models need literature-scale aggregation plus better-balanced evaluation targets rather than isolated single-paper extraction.
"""
    (OUTPUT_DIR / "learning_curve_results.md").write_text(report, encoding="utf-8")


def write_paper_section(thresholds: pd.DataFrame) -> None:
    r2_a = format_threshold(thresholds, "A", "R2 > 0.5")
    r2_b = format_threshold(thresholds, "B", "R2 > 0.5")
    acc_a = format_threshold(thresholds, "A", "Accuracy >= 0.9")
    acc_b = format_threshold(thresholds, "B", "Accuracy >= 0.9")
    section = f"""## Sample Complexity for Literature-Driven EDMA

The single-paper EDMA case study showed that eight formulations were insufficient to train a useful Gaussian process decision model: predictive R2 remained below zero and the model classified every held-out formulation as Stop. To estimate the formulation count required for literature-driven EDMA, we performed a conditional sample-complexity analysis. A reference Gaussian process was first trained on the 24 timepoint-level records from Kallakunta et al. and then used as a synthetic oracle over the formulation space. Synthetic formulation sets were sampled with Latin Hypercube sampling, queried at 24, 48, and 72 h, and evaluated with leave-one-out Gaussian process decision models.

Under this single-paper oracle, neither the 48 h decision model using `[PS, TPGS, HPMC, 24 h amount, 48 h amount]` nor the earlier 24 h decision model using `[PS, TPGS, HPMC, 24 h amount]` reached R2 > 0.5 by N = 200. Both scenarios reached decision accuracy >= 0.9 at N >= {acc_a}, but this threshold is not sufficient evidence of useful EDMA behaviour because each leave-one-out synthetic dataset contains only one true "should_continue" candidate and high accuracy can be achieved by predominantly stopping candidates. The more defensible conclusion is therefore based on predictive R2: individual ibuprofen papers provide far fewer formulation-level examples than would be required for stable literature-driven EDMA, supporting multi-paper aggregation as a prerequisite for robust modelling.

This analysis is not a physical simulation and should not be interpreted as a general ibuprofen benchmark. The oracle is a learned proxy from one paper, synthetic noise is estimated from that paper's reported SD values, and cross-paper heterogeneity is not represented. The conclusion is conditional: if the relationship complexity in this paper is representative, single-paper data are underpowered and literature-scale aggregation is necessary.
"""
    (OUTPUT_DIR / "paper_section_draft.md").write_text(section, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    configure_style()

    if not V3_SOURCE_DATA.exists():
        raise FileNotFoundError(f"Missing v3 source data: {V3_SOURCE_DATA}")

    source = pd.read_csv(V3_SOURCE_DATA)
    typical_sd_pct = float((source["cum_amount_sd_ug_cm2"] / source["cum_amount_ug_cm2"]).median())

    print("Fitting reference oracle...")
    oracle, oracle_summary = fit_oracle(source)
    (OUTPUT_DIR / "oracle_summary.json").write_text(json.dumps(oracle_summary, indent=2), encoding="utf-8")

    print("Running sample complexity loop...")
    results = run_learning_curve(oracle, typical_sd_pct)
    results.to_csv(OUTPUT_DIR / "learning_curve_raw.csv", index=False)

    summary = aggregate_results(results)
    thresholds = identify_thresholds(summary)
    formulation_counts = skinminer_formulation_counts()

    summary.to_csv(OUTPUT_DIR / "learning_curve_summary.csv", index=False)
    thresholds.to_csv(OUTPUT_DIR / "thresholds.csv", index=False)
    if not formulation_counts.empty:
        formulation_counts.to_csv(OUTPUT_DIR / "skinminer_ibuprofen_formulation_counts.csv", index=False)

    plot_learning_curve(summary, thresholds)
    plot_error_composition(summary)
    write_report(oracle_summary, typical_sd_pct, summary, thresholds, formulation_counts)
    write_paper_section(thresholds)

    print("Demonstration v4 complete")
    print(f"Oracle R2: {oracle_summary['in_sample_r2']:.3f}")
    print(f"Oracle length_scale: {oracle_summary['learned_length_scale']}")
    print(thresholds.to_string(index=False))
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
