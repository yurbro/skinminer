#!/usr/bin/env python3
"""Rebuild Demo 1 Table 4, few-shot calibration, and Figure 10.

All model inputs are read from this demo's bundled ``data`` directory. All
generated artifacts are written to this demo's ``outputs`` directory.
"""

from __future__ import annotations

import csv
import json
import math
import platform
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy
import sklearn
from scipy.stats import pearsonr, spearmanr
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------------------------
# Frozen parameters and relative paths
# ---------------------------------------------------------------------------

RANDOM_STATE = 42
RIDGE_ALPHA = 1.0
RIDGE_FIT_INTERCEPT = True
RIDGE_SOLVER = "auto"
RIDGE_TOL = 1e-4
WITHIN_2X_LOG10_THRESHOLD = 0.301
GPR_RESTARTS = 5
GPR_NORMALIZE_Y = True
GPR_ALPHA = 1e-10
GPR_OPTIMIZER = "fmin_l_bfgs_b"
GPR_CONSTANT_VALUE = 1.0
GPR_CONSTANT_BOUNDS = (1e-3, 1e3)
GPR_LENGTH_SCALE = 1.0
GPR_LENGTH_SCALE_BOUNDS = (1e-5, 1e5)
GPR_MATERN_NU = 2.5
GPR_NOISE_LEVEL = 1.0
GPR_NOISE_LEVEL_BOUNDS = (1e-5, 1e5)
FEWSHOT_K_VALUES = (3, 5)
FEWSHOT_REPEATS = 80
FEWSHOT_SD_DDOF = 1
PNG_DPI = 600
FIGURE_SIZE_INCHES = (7.0, 3.5)
HISTOGRAM_BINS = 20

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATASET_PATH = DATA_DIR / "dataset.csv"
SOLUBILITY_PATH = DATA_DIR / "solubility_table.csv"
OUTPUT_DIR = SCRIPT_DIR / "outputs"

FEATURE_SETS = {
    "composition_only": ("ethanol_vv", "PG_vv", "water_vv"),
    "composition_plus_solubility": (
        "ethanol_vv",
        "PG_vv",
        "water_vv",
        "log10_solubility",
    ),
}

# Validation targets are paper display values, not model inputs.
PAPER_TABLE4 = {
    ("ridge", "composition_only"): {
        "rmse_logJ": (0.206, 3),
        "r2": (-0.58, 2),
        "spearman_rho": (0.615, 3),
        "pearson_r": (0.675, 3),
        "within_2x": ("9/12", None),
    },
    ("ridge", "composition_plus_solubility"): {
        "rmse_logJ": (0.199, 3),
        "r2": (-0.47, 2),
        "spearman_rho": (0.706, 3),
        "pearson_r": (0.734, 3),
        "within_2x": ("9/12", None),
    },
    ("gpr", "composition_only"): {
        "rmse_logJ": (0.332, 3),
        "r2": (-3.10, 2),
        "spearman_rho": (0.601, 3),
        "pearson_r": (0.378, 3),
        "within_2x": ("5/12", None),
    },
    ("gpr", "composition_plus_solubility"): {
        "rmse_logJ": (0.329, 3),
        "r2": (-3.03, 2),
        "spearman_rho": (0.218, 3),
        "pearson_r": (0.392, 3),
        "within_2x": ("5/12", None),
    },
}

PAPER_FEWSHOT = {
    (5, "composition_plus_solubility", "mean_rmse"): (0.114, 3),
    (5, "composition_plus_solubility", "sd_spearman"): (0.186, 3),
    (5, "composition_only", "sd_spearman"): (0.311, 3),
}

WONG = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "reddish_purple": "#CC79A7",
    "grey": "#7A7A7A",
    "black": "#222222",
}


@dataclass(frozen=True)
class Record:
    record_id: str
    paper_doi: str
    source_table: str
    vehicle_signature: str
    ethanol_vv: float
    pg_vv: float
    water_vv: float
    log10_solubility: float
    j_mean: float
    j_sd: float
    log10_j_mean: float
    split: str


def read_records(path: Path) -> list[Record]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        Record(
            record_id=row["record_id"],
            paper_doi=row["paper_doi"],
            source_table=row["source_table"],
            vehicle_signature=row["vehicle_signature"],
            ethanol_vv=float(row["ethanol_vv"]),
            pg_vv=float(row["PG_vv"]),
            water_vv=float(row["water_vv"]),
            log10_solubility=float(row["log10_solubility"]),
            j_mean=float(row["J_mean"]),
            j_sd=float(row["J_sd"]),
            log10_j_mean=float(row["log10_J_mean"]),
            split=row["split"],
        )
        for row in rows
    ]


def validate_inputs(records: list[Record], solubility_path: Path) -> dict[str, object]:
    train = [record for record in records if record.split == "train"]
    test = [record for record in records if record.split == "test"]
    if len(records) != 17 or len(train) != 5 or len(test) != 12:
        raise ValueError(
            f"Expected 17 records split 5/12; observed {len(records)} "
            f"split {len(train)}/{len(test)}"
        )
    if len({record.record_id for record in records}) != 17:
        raise ValueError("record_id is not unique")
    if any(
        not math.isfinite(value)
        for record in records
        for value in (
            record.ethanol_vv,
            record.pg_vv,
            record.water_vv,
            record.log10_solubility,
            record.j_mean,
            record.log10_j_mean,
        )
    ):
        raise ValueError("Non-finite required input value")
    if any(
        not math.isclose(
            record.ethanol_vv + record.pg_vv + record.water_vv,
            100.0,
            abs_tol=1e-9,
        )
        for record in records
    ):
        raise ValueError("Composition fractions do not sum to 100 v/v%")

    with solubility_path.open("r", encoding="utf-8-sig", newline="") as handle:
        solubility_rows = list(csv.DictReader(handle))
    solubility_index = {
        (row["paper_doi"], row["vehicle_signature"]): row
        for row in solubility_rows
    }
    matched_sources: list[str] = []
    max_abs_log_difference = 0.0
    for record in records:
        key = (record.paper_doi, record.vehicle_signature)
        if key not in solubility_index:
            raise ValueError(f"Missing solubility row for {key}")
        source_row = solubility_index[key]
        matched_sources.append(source_row["source"])
        max_abs_log_difference = max(
            max_abs_log_difference,
            abs(record.log10_solubility - float(source_row["log10_solubility"])),
        )
    source_counts = {
        source: matched_sources.count(source) for source in sorted(set(matched_sources))
    }
    expected_source_counts = {
        "PartII_PG_water_Manrique": 10,
        "PartII_Table1": 2,
        "PartI_Table1": 5,
    }
    if source_counts != expected_source_counts:
        raise ValueError(
            f"Unexpected solubility source distribution: {source_counts}"
        )
    if max_abs_log_difference > 1e-12:
        raise ValueError(
            "Dataset and solubility table disagree: "
            f"max abs log10 difference={max_abs_log_difference}"
        )

    return {
        "records": len(records),
        "train_records": len(train),
        "test_records": len(test),
        "measured_solubility_records": len(records)
        - source_counts.get("PartII_PG_water_Manrique", 0),
        "estimated_solubility_records": source_counts.get(
            "PartII_PG_water_Manrique", 0
        ),
        "solubility_source_counts": source_counts,
        "max_abs_log10_solubility_join_difference": max_abs_log_difference,
    }


def matrix(records: Iterable[Record], feature_set: str) -> np.ndarray:
    rows = []
    for record in records:
        values = {
            "ethanol_vv": record.ethanol_vv,
            "PG_vv": record.pg_vv,
            "water_vv": record.water_vv,
            "log10_solubility": record.log10_solubility,
        }
        rows.append([values[column] for column in FEATURE_SETS[feature_set]])
    return np.asarray(rows, dtype=float)


def target(records: Iterable[Record]) -> np.ndarray:
    return np.asarray([record.log10_j_mean for record in records], dtype=float)


def make_ridge() -> Pipeline:
    return Pipeline(
        [
            ("standard_scaler", StandardScaler()),
            (
                "ridge",
                Ridge(
                    alpha=RIDGE_ALPHA,
                    fit_intercept=RIDGE_FIT_INTERCEPT,
                    solver=RIDGE_SOLVER,
                    tol=RIDGE_TOL,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def make_gpr() -> Pipeline:
    kernel = ConstantKernel(
        constant_value=GPR_CONSTANT_VALUE,
        constant_value_bounds=GPR_CONSTANT_BOUNDS,
    ) * Matern(
        length_scale=GPR_LENGTH_SCALE,
        length_scale_bounds=GPR_LENGTH_SCALE_BOUNDS,
        nu=GPR_MATERN_NU,
    ) + WhiteKernel(
        noise_level=GPR_NOISE_LEVEL,
        noise_level_bounds=GPR_NOISE_LEVEL_BOUNDS,
    )
    return Pipeline(
        [
            ("standard_scaler", StandardScaler()),
            (
                "gpr",
                GaussianProcessRegressor(
                    kernel=kernel,
                    alpha=GPR_ALPHA,
                    optimizer=GPR_OPTIMIZER,
                    n_restarts_optimizer=GPR_RESTARTS,
                    normalize_y=GPR_NORMALIZE_Y,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def top3_hit(actual: np.ndarray, predicted: np.ndarray) -> float:
    actual_top3 = set(np.argsort(actual)[-3:])
    predicted_top3 = set(np.argsort(predicted)[-3:])
    return len(actual_top3 & predicted_top3) / 3.0


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, object]:
    residual = predicted - actual
    within_count = int(np.sum(np.abs(residual) <= WITHIN_2X_LOG10_THRESHOLD))
    return {
        "rmse_logJ": float(np.sqrt(np.mean(residual**2))),
        "mae_logJ": float(np.mean(np.abs(residual))),
        "bias_logJ": float(np.mean(residual)),
        "r2": float(r2_score(actual, predicted)),
        "spearman_rho": float(spearmanr(actual, predicted).statistic),
        "pearson_r": float(pearsonr(actual, predicted).statistic),
        "within_2x_count": within_count,
        "within_2x": f"{within_count}/{len(actual)}",
        "within_2x_ratio": float(within_count / len(actual)),
        "top3_hit": float(top3_hit(actual, predicted)),
        "n": int(len(actual)),
    }


def classify_numeric(observed: float, paper: float, decimals: int) -> str:
    if abs(observed - paper) <= 1e-12:
        return "EXACT"
    if f"{observed:.{decimals}f}" == f"{paper:.{decimals}f}":
        return "ROUNDING_MATCH"
    return "MISMATCH"


def rebuild_zero_shot(
    train: list[Record], test: list[Record]
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[tuple[str, str], np.ndarray]]:
    results: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    prediction_map: dict[tuple[str, str], np.ndarray] = {}
    y_train = target(train)
    y_test = target(test)

    for feature_set in FEATURE_SETS:
        x_train = matrix(train, feature_set)
        x_test = matrix(test, feature_set)
        for model_name, model in (("ridge", make_ridge()), ("gpr", make_gpr())):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                model.fit(x_train, y_train)
            predicted = model.predict(x_test)
            metrics = calculate_metrics(y_test, predicted)
            kernel_optimized = ""
            if model_name == "gpr":
                kernel_optimized = str(model.named_steps["gpr"].kernel_)
            result = {
                "model": model_name,
                "feature_set": feature_set,
                **metrics,
                "warning_count": len(caught),
                "optimized_kernel": kernel_optimized,
            }
            results.append(result)
            prediction_map[(model_name, feature_set)] = predicted
            for record, actual, prediction in zip(test, y_test, predicted):
                predictions.append(
                    {
                        "model": model_name,
                        "feature_set": feature_set,
                        "record_id": record.record_id,
                        "paper_doi": record.paper_doi,
                        "source_table": record.source_table,
                        "vehicle_signature": record.vehicle_signature,
                        "actual_log10J": float(actual),
                        "predicted_log10J": float(prediction),
                        "residual": float(prediction - actual),
                        "within_2x": bool(
                            abs(prediction - actual) <= WITHIN_2X_LOG10_THRESHOLD
                        ),
                    }
                )
    return results, predictions, prediction_map


def compare_table4(results: list[dict[str, object]]) -> list[dict[str, object]]:
    indexed = {
        (str(row["model"]), str(row["feature_set"])): row for row in results
    }
    comparison: list[dict[str, object]] = []
    for key, targets in PAPER_TABLE4.items():
        model, feature_set = key
        observed_row = indexed[key]
        for metric, (paper_value, decimals) in targets.items():
            if metric == "within_2x":
                observed_value = str(observed_row["within_2x"])
                status = "EXACT" if observed_value == paper_value else "MISMATCH"
                difference: object = "0" if status == "EXACT" else "N/A"
            else:
                observed_value = float(observed_row[metric])
                status = classify_numeric(observed_value, float(paper_value), int(decimals))
                difference = observed_value - float(paper_value)
            comparison.append(
                {
                    "model": model,
                    "feature_set": feature_set,
                    "metric": metric,
                    "paper_value": paper_value,
                    "rebuilt_value": observed_value,
                    "difference_rebuilt_minus_paper": difference,
                    "display_decimals": "" if decimals is None else decimals,
                    "status": status,
                }
            )
    return comparison


def rebuild_fewshot(
    train: list[Record], target_domain: list[Record]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    group_order = [
        (k, feature_set)
        for k in FEWSHOT_K_VALUES
        for feature_set in FEATURE_SETS
    ]
    # The archived raw-run file repeats the same 80 child seeds for every
    # (k, feature_set) group. Spawn once, then reuse by repeat index.
    child_sequences = np.random.SeedSequence(RANDOM_STATE).spawn(FEWSHOT_REPEATS)
    raw_rows: list[dict[str, object]] = []

    for k, feature_set in group_order:
        for repeat_idx in range(FEWSHOT_REPEATS):
            child = child_sequences[repeat_idx]
            child_seed = int(child.generate_state(1)[0])
            rng = np.random.default_rng(child)
            calibration_indices = np.sort(
                rng.choice(len(target_domain), size=k, replace=False)
            )
            calibration_set = set(int(index) for index in calibration_indices)
            evaluation_indices = np.asarray(
                [
                    index
                    for index in range(len(target_domain))
                    if index not in calibration_set
                ],
                dtype=int,
            )
            calibration = [target_domain[index] for index in calibration_indices]
            evaluation = [target_domain[index] for index in evaluation_indices]
            expanded_train = train + calibration

            model = make_ridge()
            model.fit(matrix(expanded_train, feature_set), target(expanded_train))
            actual = target(evaluation)
            predicted = model.predict(matrix(evaluation, feature_set))
            metrics = calculate_metrics(actual, predicted)
            raw_rows.append(
                {
                    "k": k,
                    "feature_set": feature_set,
                    "repeat_idx": repeat_idx,
                    "child_seed": child_seed,
                    "calibration_record_ids": ";".join(
                        target_domain[index].record_id for index in calibration_indices
                    ),
                    "evaluation_record_ids": ";".join(
                        target_domain[index].record_id for index in evaluation_indices
                    ),
                    "rmse_logJ": metrics["rmse_logJ"],
                    "mae_logJ": metrics["mae_logJ"],
                    "bias_logJ": metrics["bias_logJ"],
                    "spearman_rho": metrics["spearman_rho"],
                    "pearson_r": metrics["pearson_r"],
                    "within_2x_ratio": metrics["within_2x_ratio"],
                    "top3_hit": metrics["top3_hit"],
                    "test_n": metrics["n"],
                }
            )

    summary_rows: list[dict[str, object]] = []
    for k, feature_set in group_order:
        group = [
            row
            for row in raw_rows
            if row["k"] == k and row["feature_set"] == feature_set
        ]
        summary: dict[str, object] = {
            "k": k,
            "feature_set": feature_set,
            "n_repeats": len(group),
        }
        for source_name, output_name in (
            ("rmse_logJ", "rmse"),
            ("mae_logJ", "mae"),
            ("bias_logJ", "bias"),
            ("spearman_rho", "spearman"),
            ("pearson_r", "pearson"),
            ("within_2x_ratio", "within_2x"),
            ("top3_hit", "top3_hit"),
        ):
            values = np.asarray([float(row[source_name]) for row in group])
            summary[f"mean_{output_name}"] = float(np.mean(values))
            # Archived aggregate SD values use sample SD (pandas default).
            summary[f"sd_{output_name}"] = float(
                np.std(values, ddof=FEWSHOT_SD_DDOF)
            )
            if source_name == "spearman_rho":
                summary["median_spearman"] = float(np.median(values))
        summary_rows.append(summary)
    return raw_rows, summary_rows


def compare_fewshot(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    indexed = {
        (int(row["k"]), str(row["feature_set"])): row for row in summary_rows
    }
    comparison: list[dict[str, object]] = []
    for (k, feature_set, metric), (paper_value, decimals) in PAPER_FEWSHOT.items():
        observed = float(indexed[(k, feature_set)][metric])
        comparison.append(
            {
                "k": k,
                "feature_set": feature_set,
                "metric": metric,
                "paper_value": paper_value,
                "rebuilt_value": observed,
                "difference_rebuilt_minus_paper": observed - paper_value,
                "display_decimals": decimals,
                "status": classify_numeric(observed, paper_value, decimals),
            }
        )
    return comparison


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def configure_plot_style() -> None:
    matplotlib.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "axes.linewidth": 0.6,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def make_figure10(
    test: list[Record],
    prediction_map: dict[tuple[str, str], np.ndarray],
    fewshot_raw: list[dict[str, object]],
    fewshot_summary: list[dict[str, object]],
) -> None:
    configure_plot_style()
    actual = target(test)
    figure, axes = plt.subplots(1, 2, figsize=FIGURE_SIZE_INCHES)
    figure.subplots_adjust(
        left=0.085,
        right=0.985,
        bottom=0.17,
        top=0.88,
        wspace=0.30,
    )
    ax_a, ax_b = axes

    lower = min(float(np.min(actual)), *(float(np.min(v)) for v in prediction_map.values()))
    upper = max(float(np.max(actual)), *(float(np.max(v)) for v in prediction_map.values()))
    plot_min = math.floor((lower - 0.08) * 20) / 20
    plot_max = math.ceil((upper + 0.08) * 20) / 20
    line_x = np.linspace(plot_min, plot_max, 300)
    ax_a.fill_between(
        line_x,
        line_x - WITHIN_2X_LOG10_THRESHOLD,
        line_x + WITHIN_2X_LOG10_THRESHOLD,
        color="#D9D9D9",
        alpha=0.50,
        linewidth=0,
        zorder=0,
    )
    ax_a.plot(line_x, line_x, color=WONG["black"], linewidth=1.0, zorder=1)

    scatter_specs = (
        ("ridge", "composition_only", "o", WONG["blue"], True, "Ridge comp"),
        (
            "ridge",
            "composition_plus_solubility",
            "^",
            WONG["blue"],
            True,
            "Ridge comp+S",
        ),
        ("gpr", "composition_only", "o", WONG["orange"], False, "GPR comp"),
        (
            "gpr",
            "composition_plus_solubility",
            "^",
            WONG["orange"],
            False,
            "GPR comp+S",
        ),
    )
    for model, feature_set, marker, color, filled, label in scatter_specs:
        ax_a.scatter(
            actual,
            prediction_map[(model, feature_set)],
            s=34,
            marker=marker,
            facecolors=color if filled else "none",
            edgecolors="white" if filled else color,
            linewidths=0.8 if filled else 1.1,
            alpha=0.78 if filled else 0.90,
            label=label,
            zorder=3,
        )
    ax_a.set_xlim(plot_min, plot_max)
    ax_a.set_ylim(plot_min, plot_max)
    ax_a.set_aspect("equal", adjustable="box")
    ax_a.set_title("A. Zero-shot Part I to Part II")
    ax_a.set_xlabel("Actual log10 flux (µg/cm²/h)")
    ax_a.set_ylabel("Predicted log10 flux (µg/cm²/h)")
    ax_a.text(
        0.04,
        0.96,
        "Best: ridge composition_plus_solubility\n"
        "rho=0.71, n=12, thr=0.587",
        transform=ax_a.transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )
    ax_a.legend(loc="lower right", frameon=False, handletextpad=0.5)
    ax_a.grid(False)

    summary_index = {
        (int(row["k"]), str(row["feature_set"])): row for row in fewshot_summary
    }
    hist_specs = (
        (3, "composition_only", WONG["green"], "-", "k=3 comp"),
        (3, "composition_plus_solubility", WONG["green"], "--", "k=3 comp+S"),
        (5, "composition_only", WONG["reddish_purple"], "-", "k=5 comp"),
        (
            5,
            "composition_plus_solubility",
            WONG["reddish_purple"],
            "--",
            "k=5 comp+S",
        ),
    )
    bins = np.linspace(-1.0, 1.0, HISTOGRAM_BINS + 1)
    for k, feature_set, color, linestyle, label in hist_specs:
        values = np.asarray(
            [
                float(row["spearman_rho"])
                for row in fewshot_raw
                if int(row["k"]) == k and row["feature_set"] == feature_set
            ]
        )
        ax_b.hist(
            values,
            bins=bins,
            density=True,
            histtype="step",
            linewidth=1.2,
            color=color,
            linestyle=linestyle,
            label=label,
        )
        summary = summary_index[(k, feature_set)]
        ax_b.axvline(
            float(summary["mean_spearman"]),
            color=color,
            linestyle=linestyle,
            linewidth=0.9,
            alpha=0.80,
        )
        ax_b.axvline(
            float(summary["median_spearman"]),
            color=color,
            linestyle=":",
            linewidth=0.8,
            alpha=0.75,
        )
    ax_b.axvline(0.0, color=WONG["black"], linewidth=0.7, alpha=0.8)
    ax_b.set_xlim(-1.0, 1.0)
    ax_b.set_ylim(0.0, 3.55)
    ax_b.set_title("B. Few-shot Spearman distributions")
    ax_b.set_xlabel("Spearman rho")
    ax_b.set_ylabel("Density")
    ax_b.legend(loc="upper left", frameon=False)
    ax_b.grid(False)

    for axis in axes:
        axis.spines["top"].set_linewidth(0.6)
        axis.spines["right"].set_linewidth(0.6)
        axis.spines["bottom"].set_linewidth(0.6)
        axis.spines["left"].set_linewidth(0.6)

    figure.savefig(OUTPUT_DIR / "fig10_demo1_rebuilt.pdf")
    figure.savefig(OUTPUT_DIR / "fig10_demo1_rebuilt.png", dpi=PNG_DPI)
    plt.close(figure)


def main() -> None:
    if not DATASET_PATH.is_file() or not SOLUBILITY_PATH.is_file():
        raise FileNotFoundError(
            "Expected SkinMiner source inputs at relative path ../../../SkinMiner"
        )
    records = read_records(DATASET_PATH)
    input_validation = validate_inputs(records, SOLUBILITY_PATH)
    train = [record for record in records if record.split == "train"]
    test = [record for record in records if record.split == "test"]

    zero_shot, predictions, prediction_map = rebuild_zero_shot(train, test)
    table4_comparison = compare_table4(zero_shot)
    write_csv(OUTPUT_DIR / "table4_rebuilt.csv", zero_shot)
    write_csv(OUTPUT_DIR / "table4_comparison.csv", table4_comparison)
    write_csv(OUTPUT_DIR / "predictions_zero_shot_rebuilt.csv", predictions)

    ridge_mismatches = [
        row
        for row in table4_comparison
        if row["model"] == "ridge" and row["status"] == "MISMATCH"
    ]
    if ridge_mismatches:
        failure = {
            "status": "STOPPED_RIDGE_MISMATCH",
            "ridge_mismatches": ridge_mismatches,
            "input_validation": input_validation,
        }
        (OUTPUT_DIR / "run_summary.json").write_text(
            json.dumps(failure, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        raise SystemExit("Ridge Table 4 mismatch; stopped without parameter changes")

    fewshot_raw, fewshot_summary = rebuild_fewshot(train, test)
    fewshot_comparison = compare_fewshot(fewshot_summary)
    write_csv(OUTPUT_DIR / "fewshot_raw_runs_rebuilt.csv", fewshot_raw)
    write_csv(OUTPUT_DIR / "fewshot_results_rebuilt.csv", fewshot_summary)
    write_csv(OUTPUT_DIR / "fewshot_comparison.csv", fewshot_comparison)
    make_figure10(test, prediction_map, fewshot_raw, fewshot_summary)

    summary = {
        "status": "COMPLETED",
        "source_inputs": [
            str(DATASET_PATH.relative_to(SCRIPT_DIR)).replace("\\", "/"),
            str(SOLUBILITY_PATH.relative_to(SCRIPT_DIR)).replace("\\", "/"),
        ],
        "parameters": {
            "random_state": RANDOM_STATE,
            "ridge_alpha": RIDGE_ALPHA,
            "ridge_solver": RIDGE_SOLVER,
            "ridge_tol": RIDGE_TOL,
            "within_2x_log10_threshold": WITHIN_2X_LOG10_THRESHOLD,
            "gpr_restarts": GPR_RESTARTS,
            "gpr_normalize_y": GPR_NORMALIZE_Y,
            "gpr_alpha": GPR_ALPHA,
            "gpr_optimizer": GPR_OPTIMIZER,
            "fewshot_k_values": list(FEWSHOT_K_VALUES),
            "fewshot_repeats_per_group": FEWSHOT_REPEATS,
            "fewshot_sd_ddof": FEWSHOT_SD_DDOF,
        },
        "input_validation": input_validation,
        "table4_status_counts": {
            status: sum(row["status"] == status for row in table4_comparison)
            for status in ("EXACT", "ROUNDING_MATCH", "MISMATCH")
        },
        "fewshot_status_counts": {
            status: sum(row["status"] == status for row in fewshot_comparison)
            for status in ("EXACT", "ROUNDING_MATCH", "MISMATCH")
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "outputs": [
            "table4_rebuilt.csv",
            "table4_comparison.csv",
            "predictions_zero_shot_rebuilt.csv",
            "fewshot_raw_runs_rebuilt.csv",
            "fewshot_results_rebuilt.csv",
            "fewshot_comparison.csv",
            "fig10_demo1_rebuilt.pdf",
            "fig10_demo1_rebuilt.png",
        ],
    }
    (OUTPUT_DIR / "run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
