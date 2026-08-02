from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_demo2_fewshot as fewshot


OUT = SCRIPT_DIR
PURE_JSON = OUT / "sample_matched_pure_inhouse_results.json"
MIXED_JSON = OUT / "sample_matched_mixed_results.json"
SUMMARY_CSV = OUT / "sample_matched_summary.csv"
FIG_PDF = OUT / "figure_sample_matched_comparison.pdf"
FIG_PNG = OUT / "figure_sample_matched_comparison.png"
REPORT = OUT / "demo2_sample_matched_report.md"
EXISTING_FEWSHOT_JSON = OUT / "fewshot_bolla_to_xiao_results.json"
EXISTING_FEWSHOT_CSV = OUT / "fewshot_summary_table.csv"
EXISTING_INTERNAL_JSON = OUT / "xiao_internal_4feature_loocv_results.json"

RANDOM_STATE = 42
SUBSET_CAP = 200
M_VALUES = [8, 12, 16, 20, 24, 28]
MIXED_PLAN_K_VALUES = [0, 1, 2, 4, 8, 12, 16, 20]
FEATURES = fewshot.FEATURES
CENTER_IDS = fewshot.XIAO_CENTER_IDS
LOG10_2 = math.log10(2.0)

PALETTE = {
    "pure": "#0072B2",
    "mixed": "#D55E00",
    "line": "#222222",
    "grid": "#D9D9D9",
}


def json_safe(value):
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return [json_safe(item) for item in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
        return None if math.isnan(value) else value
    if isinstance(value, float):
        return None if math.isnan(value) else value
    return value


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(json_safe(payload), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def mean_std(values: list[float | None]) -> tuple[float | None, float | None, int]:
    clean = [float(value) for value in values if value is not None and not math.isnan(float(value))]
    if not clean:
        return None, None, 0
    array = np.asarray(clean, dtype=float)
    return float(np.mean(array)), float(np.std(array, ddof=0)), int(len(array))


def correlation_or_none(
    actual: np.ndarray,
    predicted: np.ndarray,
    method: str,
) -> float | None:
    if len(actual) < 2 or np.allclose(actual, actual[0]) or np.allclose(predicted, predicted[0]):
        return None
    if method == "spearman":
        value = spearmanr(actual, predicted).statistic
    elif method == "pearson":
        value = pearsonr(actual, predicted).statistic
    else:
        raise ValueError(method)
    return None if math.isnan(float(value)) else float(value)


def metrics_from_arrays(actual: np.ndarray, predicted: np.ndarray) -> dict:
    residual = predicted - actual
    within = np.abs(residual) <= LOG10_2
    r2 = None
    if len(actual) >= 2 and not np.allclose(actual, actual[0]):
        r2 = float(r2_score(actual, predicted))
    return {
        "R2_conv": r2,
        "rmse_logJ": float(math.sqrt(mean_squared_error(actual, predicted))),
        "spearman_rho": correlation_or_none(actual, predicted, "spearman"),
        "pearson_r": correlation_or_none(actual, predicted, "pearson"),
        "within_2x_fraction": float(np.mean(within)),
        "within_2x_count": int(np.sum(within)),
        "n_test": int(len(actual)),
    }


def fit_predict(train: pd.DataFrame, test: pd.DataFrame) -> tuple[np.ndarray, dict]:
    scaler = StandardScaler()
    train_features = scaler.fit_transform(train[FEATURES].to_numpy(dtype=float))
    test_features = scaler.transform(test[FEATURES].to_numpy(dtype=float))
    model = Ridge(alpha=1.0)
    model.fit(train_features, train["log10_J"].to_numpy(dtype=float))
    predicted = model.predict(test_features)
    audit = {
        "scaler_mean": {
            feature: float(value) for feature, value in zip(FEATURES, scaler.mean_)
        },
        "scaler_scale": {
            feature: float(value) for feature, value in zip(FEATURES, scaler.scale_)
        },
        "ridge_intercept": float(model.intercept_),
        "ridge_coefficients_scaled_feature_space": {
            feature: float(value) for feature, value in zip(FEATURES, model.coef_)
        },
    }
    return predicted, audit


def center_indices(xiao: pd.DataFrame) -> tuple[tuple[int, ...], tuple[int, ...]]:
    center = tuple(
        int(index) for index in xiao.index[xiao["record_id"].isin(CENTER_IDS)].tolist()
    )
    non_center = tuple(
        int(index) for index in xiao.index[~xiao["record_id"].isin(CENTER_IDS)].tolist()
    )
    if len(center) != 3 or len(non_center) != 26:
        raise ValueError(f"Unexpected center/non-center counts: {center}, n_non_center={len(non_center)}")
    center_rows = xiao.iloc[list(center)]
    for feature in FEATURES:
        if center_rows[feature].nunique(dropna=False) != 1:
            raise ValueError(f"Center triplet differs on feature {feature}")
    return center, non_center


def pure_subset_plan(xiao: pd.DataFrame) -> tuple[dict[int, list[tuple[int, ...]]], dict[int, dict]]:
    center, non_center = center_indices(xiao)
    rng = np.random.default_rng(RANDOM_STATE)
    plan: dict[int, list[tuple[int, ...]]] = {}
    audit: dict[int, dict] = {}
    for m in M_VALUES:
        subsets, total_valid, skipped = fewshot.sample_valid_xiao_subsets(
            non_center,
            center,
            m,
            SUBSET_CAP,
            rng,
        )
        plan[m] = subsets
        audit[m] = {
            "m": m,
            "total_valid_subsets": int(total_valid),
            "n_used": int(len(subsets)),
            "n_skipped_by_cap": int(skipped),
            "cap": SUBSET_CAP,
            "selection": "all valid subsets" if total_valid <= SUBSET_CAP else "200 unique deterministic subsets",
        }
    return plan, audit


def mixed_subset_plan(xiao: pd.DataFrame) -> tuple[dict[int, list[tuple[int, ...]]], dict[int, dict]]:
    center, non_center = center_indices(xiao)
    rng = np.random.default_rng(RANDOM_STATE)
    plan_by_k: dict[int, list[tuple[int, ...]]] = {}
    audit_by_k: dict[int, dict] = {}
    for k in MIXED_PLAN_K_VALUES:
        if k == 0:
            subsets = [tuple()]
            total_valid = 1
            skipped = 0
        else:
            subsets, total_valid, skipped = fewshot.sample_valid_xiao_subsets(
                non_center,
                center,
                k,
                SUBSET_CAP,
                rng,
            )
        plan_by_k[k] = subsets
        audit_by_k[k] = {
            "k_xiao": k,
            "m": k + 8,
            "total_valid_subsets": int(total_valid),
            "n_used": int(len(subsets)),
            "n_skipped_by_cap": int(skipped),
            "cap": SUBSET_CAP,
            "selection": "all valid subsets" if total_valid <= SUBSET_CAP else "200 unique deterministic subsets",
        }
    return (
        {m: plan_by_k[m - 8] for m in M_VALUES},
        {m: audit_by_k[m - 8] for m in M_VALUES},
    )


def assert_center_policy(train_xiao: pd.DataFrame, test_xiao: pd.DataFrame) -> dict:
    train_center = sorted(set(train_xiao["record_id"].astype(str)).intersection(CENTER_IDS))
    test_center = sorted(set(test_xiao["record_id"].astype(str)).intersection(CENTER_IDS))
    valid = (
        (len(train_center) == 3 and len(test_center) == 0)
        or (len(train_center) == 0 and len(test_center) == 3)
    )
    if not valid:
        raise RuntimeError(
            f"Center triplet split: train={train_center}, test={test_center}"
        )
    return {
        "center_group_in_train": train_center,
        "center_group_in_test": test_center,
        "center_group_indivisible": True,
    }


def run_one_subset(
    configuration: str,
    m: int,
    subset_number: int,
    subset: tuple[int, ...],
    xiao: pd.DataFrame,
    bolla: pd.DataFrame,
) -> dict:
    train_xiao = xiao.iloc[list(subset)].copy()
    test_xiao = xiao.drop(index=list(subset)).reset_index(drop=True)
    if configuration == "pure_inhouse":
        train = train_xiao.reset_index(drop=True)
        n_literature = 0
    elif configuration == "mixed":
        train = pd.concat([bolla, train_xiao], ignore_index=True)
        n_literature = len(bolla)
    else:
        raise ValueError(configuration)

    if len(train) != m:
        raise RuntimeError(
            f"{configuration} m={m} produced n_train={len(train)} for subset {subset_number}"
        )
    center_audit = assert_center_policy(train_xiao, test_xiao)
    predicted, model_audit = fit_predict(train, test_xiao)
    actual = test_xiao["log10_J"].to_numpy(dtype=float)
    metrics = metrics_from_arrays(actual, predicted)

    predictions = []
    for (_, row), prediction in zip(test_xiao.iterrows(), predicted):
        residual = float(prediction) - float(row["log10_J"])
        predictions.append(
            {
                "record_id": str(row["record_id"]),
                "logJ_actual": float(row["log10_J"]),
                "logJ_pred": float(prediction),
                "residual_pred_minus_actual": residual,
                "within_2x": bool(abs(residual) <= LOG10_2),
            }
        )

    return {
        "configuration": configuration,
        "m": int(m),
        "subset_number": int(subset_number),
        "subset_indices": [int(index) for index in subset],
        "xiao_train_record_ids": train_xiao["record_id"].astype(str).tolist(),
        "test_record_ids": test_xiao["record_id"].astype(str).tolist(),
        "n_train_total": int(len(train)),
        "n_train_inhouse": int(len(train_xiao)),
        "n_train_literature": int(n_literature),
        **center_audit,
        "metrics": metrics,
        "predictions": predictions,
        "model_audit": model_audit,
    }


def aggregate_records(records: list[dict], plan_audit: dict[int, dict]) -> list[dict]:
    summary: list[dict] = []
    configuration = str(records[0]["configuration"])
    for m in M_VALUES:
        cells = [record for record in records if record["m"] == m]
        if not cells:
            raise RuntimeError(f"No records for {configuration} m={m}")
        row = {
            "configuration": configuration,
            "m": int(m),
            "n_train_total": int(m),
            "n_train_inhouse": int(cells[0]["n_train_inhouse"]),
            "n_train_literature": int(cells[0]["n_train_literature"]),
            "n_test_xiao": int(cells[0]["metrics"]["n_test"]),
            "n_subsets": int(len(cells)),
            "total_valid_subsets": int(plan_audit[m]["total_valid_subsets"]),
            "n_skipped_by_cap": int(plan_audit[m]["n_skipped_by_cap"]),
        }
        for metric, output_name in [
            ("R2_conv", "R2_conv"),
            ("rmse_logJ", "rmse_logJ"),
            ("spearman_rho", "spearman_rho"),
            ("pearson_r", "pearson_r"),
            ("within_2x_fraction", "within_2x_fraction"),
        ]:
            mean, std, n_defined = mean_std(
                [cell["metrics"][metric] for cell in cells]
            )
            row[f"{output_name}_mean"] = mean
            row[f"{output_name}_std"] = std
            row[f"{output_name}_n_defined"] = n_defined
        summary.append(row)
    return summary


def pooled_m28_diagnostic(records: list[dict]) -> dict:
    cells = [record for record in records if record["m"] == 28]
    actual: list[float] = []
    predicted: list[float] = []
    record_ids: list[str] = []
    for cell in cells:
        for prediction in cell["predictions"]:
            actual.append(float(prediction["logJ_actual"]))
            predicted.append(float(prediction["logJ_pred"]))
            record_ids.append(str(prediction["record_id"]))
    if len(cells) != 26 or len(record_ids) != 26 or len(set(record_ids)) != 26:
        raise RuntimeError("Expected 26 unique non-center held-out predictions for pure m=28")
    if set(record_ids).intersection(CENTER_IDS):
        raise RuntimeError("Center records must not appear in a valid pure m=28 test set")
    metrics = metrics_from_arrays(
        np.asarray(actual, dtype=float),
        np.asarray(predicted, dtype=float),
    )
    return {
        "status": "diagnostic_only_not_subset_mean",
        "reason": (
            "Each m=28 pure-in-house subset has one test record, so per-subset R2_conv, "
            "Spearman rho, and Pearson r are undefined. The 26 valid unique held-out "
            "predictions are pooled only for the requested LOOCV sanity check."
        ),
        "n_valid_unique_subsets": 26,
        "n_pooled_predictions": 26,
        "excluded_from_possible_test_set_due_to_center_block": list(CENTER_IDS),
        "pooled_test_record_ids": record_ids,
        "metrics": metrics,
    }


def build_payload(
    configuration: str,
    records: list[dict],
    summary: list[dict],
    plan_audit: dict[int, dict],
    pooled_m28: dict | None = None,
) -> dict:
    payload = {
        "metadata": {
            "analysis": "Sample-size-matched literature-data-value comparison predicting Xiao in-house records",
            "configuration": configuration,
            "features": FEATURES,
            "model": "StandardScaler fit on training rows only + Ridge(alpha=1.0)",
            "target": "log10(J)",
            "random_state": RANDOM_STATE,
            "subset_cap": SUBSET_CAP,
            "m_values": M_VALUES,
            "center_group_record_ids": list(CENTER_IDS),
            "center_group_policy": "BBD4/BBD5/BBD6 are an indivisible block.",
            "R2_conv_definition": "sklearn r2_score within each test set using that test set's actual mean as baseline",
            "within_2x_definition": "abs(predicted log10 J - actual log10 J) <= log10(2)",
        },
        "subset_sampling_audit": {str(m): plan_audit[m] for m in M_VALUES},
        "summary": summary,
        "records": records,
        "leakage_guard": {
            "status": "PASS",
            "n_violations": 0,
            "records_checked": len(records),
        },
    }
    if pooled_m28 is not None:
        payload["m28_pooled_sanity_diagnostic"] = pooled_m28
    return payload


def validate_against_existing(
    mixed_records: list[dict],
    mixed_summary: list[dict],
    pure_m28: dict,
) -> dict:
    existing_records = json.loads(EXISTING_FEWSHOT_JSON.read_text(encoding="utf-8"))
    existing_k12 = [row for row in existing_records if int(row["k"]) == 12]
    new_m20 = [row for row in mixed_records if int(row["m"]) == 20]
    existing_subsets = [tuple(row["subset_record_ids"]) for row in existing_k12]
    new_subsets = [tuple(row["xiao_train_record_ids"]) for row in new_m20]
    subset_match = existing_subsets == new_subsets

    existing_summary = pd.read_csv(EXISTING_FEWSHOT_CSV)
    old_row = existing_summary[
        (existing_summary["direction"] == "bolla_to_xiao")
        & (existing_summary["k"] == 12)
    ].iloc[0]
    new_row = next(row for row in mixed_summary if row["m"] == 20)
    metric_differences = {
        "R2_conv_mean": abs(float(new_row["R2_conv_mean"]) - float(old_row["R2_conv_mean"])),
        "R2_conv_std": abs(float(new_row["R2_conv_std"]) - float(old_row["R2_conv_std"])),
        "rmse_logJ_mean": abs(float(new_row["rmse_logJ_mean"]) - float(old_row["rmse_logJ_mean"])),
        "rmse_logJ_std": abs(float(new_row["rmse_logJ_std"]) - float(old_row["rmse_logJ_std"])),
        "spearman_rho_mean": abs(float(new_row["spearman_rho_mean"]) - float(old_row["spearman_mean"])),
        "spearman_rho_std": abs(float(new_row["spearman_rho_std"]) - float(old_row["spearman_std"])),
    }
    fewshot_match = subset_match and max(metric_differences.values()) < 1e-12

    internal = json.loads(EXISTING_INTERNAL_JSON.read_text(encoding="utf-8"))
    existing_internal_r2 = float(internal["aggregate_metrics"]["R2_conv"])
    pooled_r2 = float(pure_m28["metrics"]["R2_conv"])
    m28_in_expected_range = -0.40 <= pooled_r2 <= -0.10

    return {
        "mixed_m20_vs_step2h_k12": {
            "status": "PASS" if fewshot_match else "FAIL",
            "n_subsets_existing": len(existing_k12),
            "n_subsets_new": len(new_m20),
            "subset_sequence_exact_match": subset_match,
            "maximum_metric_difference": max(metric_differences.values()),
            "metric_differences": metric_differences,
            "existing_R2_conv_mean": float(old_row["R2_conv_mean"]),
            "new_R2_conv_mean": float(new_row["R2_conv_mean"]),
        },
        "pure_m28_pooled_vs_grouped_loocv": {
            "status": "PASS" if m28_in_expected_range else "FLAG",
            "pooled_m28_R2_conv": pooled_r2,
            "existing_grouped_loocv_R2_conv": existing_internal_r2,
            "absolute_difference": abs(pooled_r2 - existing_internal_r2),
            "expected_prompt_range": [-0.40, -0.10],
            "within_expected_prompt_range": m28_in_expected_range,
            "comparability_note": (
                "The pooled m=28 diagnostic covers 26 non-center records. The grouped "
                "LOOCV reference covers all 29 records and holds BBD4/BBD5/BBD6 out together."
            ),
        },
    }


def add_pooled_fields(summary: list[dict], pure_m28: dict) -> None:
    for row in summary:
        row["pooled_diagnostic_R2_conv"] = None
        row["pooled_diagnostic_spearman_rho"] = None
        row["pooled_diagnostic_n"] = None
        if row["configuration"] == "pure_inhouse" and row["m"] == 28:
            row["pooled_diagnostic_R2_conv"] = pure_m28["metrics"]["R2_conv"]
            row["pooled_diagnostic_spearman_rho"] = pure_m28["metrics"]["spearman_rho"]
            row["pooled_diagnostic_n"] = pure_m28["metrics"]["n_test"]


def write_summary_csv(rows: list[dict]) -> None:
    columns = [
        "configuration",
        "m",
        "n_train_total",
        "n_train_inhouse",
        "n_train_literature",
        "n_test_xiao",
        "n_subsets",
        "total_valid_subsets",
        "n_skipped_by_cap",
        "R2_conv_mean",
        "R2_conv_std",
        "R2_conv_n_defined",
        "rmse_logJ_mean",
        "rmse_logJ_std",
        "spearman_rho_mean",
        "spearman_rho_std",
        "spearman_rho_n_defined",
        "pearson_r_mean",
        "pearson_r_std",
        "within_2x_fraction_mean",
        "within_2x_fraction_std",
        "pooled_diagnostic_R2_conv",
        "pooled_diagnostic_spearman_rho",
        "pooled_diagnostic_n",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            output = {}
            for column in columns:
                value = row.get(column)
                if isinstance(value, float):
                    output[column] = f"{value:.12f}"
                elif value is None:
                    output[column] = ""
                else:
                    output[column] = value
            writer.writerow(output)


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.5,
            "axes.titlesize": 9,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.5,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def summary_lookup(rows: list[dict]) -> dict[tuple[str, int], dict]:
    return {(str(row["configuration"]), int(row["m"])): row for row in rows}


def make_figure(rows: list[dict], pure_m28: dict) -> None:
    configure_matplotlib()
    lookup = summary_lookup(rows)
    pure_defined_m = [
        m for m in M_VALUES if lookup[("pure_inhouse", m)]["R2_conv_mean"] is not None
    ]
    pure_r2 = [lookup[("pure_inhouse", m)]["R2_conv_mean"] for m in pure_defined_m]
    pure_r2_std = [lookup[("pure_inhouse", m)]["R2_conv_std"] for m in pure_defined_m]
    mixed_r2 = [lookup[("mixed", m)]["R2_conv_mean"] for m in M_VALUES]
    mixed_r2_std = [lookup[("mixed", m)]["R2_conv_std"] for m in M_VALUES]

    pure_rho_m = [
        m for m in M_VALUES if lookup[("pure_inhouse", m)]["spearman_rho_mean"] is not None
    ]
    pure_rho = [lookup[("pure_inhouse", m)]["spearman_rho_mean"] for m in pure_rho_m]
    pure_rho_std = [lookup[("pure_inhouse", m)]["spearman_rho_std"] for m in pure_rho_m]
    mixed_rho = [lookup[("mixed", m)]["spearman_rho_mean"] for m in M_VALUES]
    mixed_rho_std = [lookup[("mixed", m)]["spearman_rho_std"] for m in M_VALUES]

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.65, 3.65),
        gridspec_kw={"wspace": 0.34},
        constrained_layout=False,
    )

    common_pure = {
        "color": PALETTE["pure"],
        "marker": "o",
        "markersize": 4.5,
        "linewidth": 1.2,
        "capsize": 2.5,
        "label": "Pure in-house (configuration A)",
    }
    common_mixed = {
        "color": PALETTE["mixed"],
        "marker": "^",
        "markersize": 5,
        "linewidth": 1.2,
        "linestyle": (0, (4, 3)),
        "capsize": 2.5,
        "label": "Mixed: 8 literature + (n-8) in-house",
    }

    axes[0].errorbar(pure_defined_m, pure_r2, yerr=pure_r2_std, **common_pure)
    axes[0].errorbar(M_VALUES, mixed_r2, yerr=mixed_r2_std, **common_mixed)
    axes[0].scatter(
        [28],
        [pure_m28["metrics"]["R2_conv"]],
        s=34,
        marker="o",
        facecolor="white",
        edgecolor=PALETTE["pure"],
        linewidth=1.2,
        zorder=5,
        label="Pure m=28 pooled diagnostic",
    )
    axes[0].axhline(0, color=PALETTE["line"], linewidth=0.8, linestyle=(0, (3, 3)))
    axes[0].set_title("A  Conventional R$^2$", loc="left", fontweight="bold", pad=7)
    axes[0].set_ylabel("Mean R$^2_{conv}$")
    axes[0].set_xlabel("Matched total training size, n")
    axes[0].set_xticks(M_VALUES)
    axes[0].grid(axis="y", color=PALETTE["grid"], linewidth=0.45)
    axes[0].legend(loc="lower right", frameon=False, handlelength=2.2)

    axes[1].errorbar(pure_rho_m, pure_rho, yerr=pure_rho_std, **common_pure)
    axes[1].errorbar(M_VALUES, mixed_rho, yerr=mixed_rho_std, **common_mixed)
    axes[1].scatter(
        [28],
        [pure_m28["metrics"]["spearman_rho"]],
        s=34,
        marker="o",
        facecolor="white",
        edgecolor=PALETTE["pure"],
        linewidth=1.2,
        zorder=5,
        label="Pure m=28 pooled diagnostic",
    )
    axes[1].axhline(0, color=PALETTE["line"], linewidth=0.8, linestyle=(0, (3, 3)))
    axes[1].set_title("B  Spearman rank correlation", loc="left", fontweight="bold", pad=7)
    axes[1].set_ylabel("Mean Spearman $\\rho$")
    axes[1].set_xlabel("Matched total training size, n")
    axes[1].set_xticks(M_VALUES)
    axes[1].grid(axis="y", color=PALETTE["grid"], linewidth=0.45)

    for axis in axes:
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.tick_params(direction="out", length=3, width=0.8)

    fig.suptitle(
        "Sample-size-matched literature-data-value comparison",
        fontsize=10,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.925,
        "Pure in-house and mixed training at matched total sizes; higher curves indicate better prediction of in-house records.",
        ha="center",
        va="top",
        fontsize=7.7,
        color="#333333",
    )
    fig.subplots_adjust(left=0.078, right=0.985, bottom=0.18, top=0.82)
    fig.savefig(
        FIG_PDF,
        metadata={"Creator": "SkinMiner", "CreationDate": None, "ModDate": None},
    )
    fig.savefig(FIG_PNG, dpi=450, metadata={"Software": "SkinMiner"})
    plt.close(fig)


def format_pm(mean: float | None, std: float | None, digits: int = 3) -> str:
    if mean is None:
        return "undefined"
    if std is None:
        return f"{mean:.{digits}f}"
    return f"{mean:.{digits}f} +/- {std:.{digits}f}"


def summary_table_lines(rows: list[dict], configuration: str) -> list[str]:
    selected = [row for row in rows if row["configuration"] == configuration]
    lines = [
        "| m | n_subsets | R2_conv mean +/- std | RMSE_logJ mean +/- std | Spearman rho mean +/- std | within-2x mean +/- std |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in selected:
        r2_text = format_pm(row["R2_conv_mean"], row["R2_conv_std"])
        rho_text = format_pm(row["spearman_rho_mean"], row["spearman_rho_std"])
        if configuration == "pure_inhouse" and row["m"] == 28:
            r2_text = (
                f"undefined per subset; pooled diagnostic "
                f"{row['pooled_diagnostic_R2_conv']:.3f}"
            )
            rho_text = (
                f"undefined per subset; pooled diagnostic "
                f"{row['pooled_diagnostic_spearman_rho']:.3f}"
            )
        lines.append(
            f"| {row['m']} | {row['n_subsets']} | {r2_text} | "
            f"{format_pm(row['rmse_logJ_mean'], row['rmse_logJ_std'])} | "
            f"{rho_text} | "
            f"{format_pm(row['within_2x_fraction_mean'], row['within_2x_fraction_std'])} |"
        )
    return lines


def direct_comparison(rows: list[dict]) -> tuple[list[str], list[dict]]:
    lookup = summary_lookup(rows)
    lines = [
        "| m | Pure A R2_conv | Mixed B R2_conv | Pure A rho | Mixed B rho | R2 head-to-head |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    outcomes: list[dict] = []
    for m in M_VALUES:
        pure = lookup[("pure_inhouse", m)]
        mixed = lookup[("mixed", m)]
        if pure["R2_conv_mean"] is None:
            pure_r2 = pure["pooled_diagnostic_R2_conv"]
            pure_rho = pure["pooled_diagnostic_spearman_rho"]
            result = "A pooled diagnostic > B mean" if pure_r2 > mixed["R2_conv_mean"] else "B mean >= A pooled diagnostic"
            separation = None
        else:
            pure_r2 = pure["R2_conv_mean"]
            pure_rho = pure["spearman_rho_mean"]
            pure_low = pure_r2 - pure["R2_conv_std"]
            mixed_high = mixed["R2_conv_mean"] + mixed["R2_conv_std"]
            separation = bool(pure_low > mixed_high)
            if pure_r2 > mixed["R2_conv_mean"]:
                result = "A higher; 1-SD bars separated" if separation else "A higher; 1-SD bars overlap"
            else:
                result = "B >= A"
        outcomes.append(
            {
                "m": m,
                "pure_R2": pure_r2,
                "mixed_R2": mixed["R2_conv_mean"],
                "pure_rho": pure_rho,
                "mixed_rho": mixed["spearman_rho_mean"],
                "pure_R2_higher": bool(pure_r2 > mixed["R2_conv_mean"]),
                "one_sd_separation": separation,
                "result": result,
            }
        )
        lines.append(
            f"| {m} | "
            f"{f'{pure_r2:.3f} (pooled)' if pure['R2_conv_mean'] is None else format_pm(pure['R2_conv_mean'], pure['R2_conv_std'])} | "
            f"{format_pm(mixed['R2_conv_mean'], mixed['R2_conv_std'])} | "
            f"{f'{pure_rho:.3f} (pooled)' if pure['spearman_rho_mean'] is None else format_pm(pure['spearman_rho_mean'], pure['spearman_rho_std'])} | "
            f"{format_pm(mixed['spearman_rho_mean'], mixed['spearman_rho_std'])} | "
            f"{result} |"
        )
    return lines, outcomes


def make_report(
    rows: list[dict],
    validations: dict,
    pure_audit: dict[int, dict],
    mixed_audit: dict[int, dict],
) -> None:
    direct_lines, outcomes = direct_comparison(rows)
    formal = [outcome for outcome in outcomes if outcome["one_sd_separation"] is not None]
    pure_wins = [outcome["m"] for outcome in formal if outcome["pure_R2_higher"]]
    separated = [outcome["m"] for outcome in formal if outcome["one_sd_separation"]]
    mixed_wins = [outcome["m"] for outcome in formal if not outcome["pure_R2_higher"]]
    m28_outcome = next(outcome for outcome in outcomes if outcome["m"] == 28)
    m20 = next(row for row in rows if row["configuration"] == "mixed" and row["m"] == 20)
    pure_m28 = next(row for row in rows if row["configuration"] == "pure_inhouse" and row["m"] == 28)

    lines = [
        "# Demo 2 Step 2m: Sample-Size-Matched Literature-Value Comparison",
        "",
        "## 1. Setup and Sanity Checks",
        "",
        "The comparison uses the unchanged 4-feature bridge (`log10_vehicle_solubility`, `ethanol_fraction`, `pg_fraction`, `water_fraction`), log10(J), StandardScaler fitted on training rows only, and Ridge(alpha=1.0). At each m, configuration A trains on m in-house records and configuration B trains on all 8 literature records plus m-8 in-house records. Both evaluate only on held-out in-house records.",
        "",
        "The prompt's phrase `BBD F4/F5/F6` maps to the actual record IDs BBD4/BBD5/BBD6. These three identical center-point compositions were always included together or excluded together. Leakage guard: PASS.",
        "",
        f"Subset records retained for audit: {sum(row['n_subsets'] for row in rows if row['configuration'] == 'pure_inhouse')} for configuration A and {sum(row['n_subsets'] for row in rows if row['configuration'] == 'mixed')} for configuration B.",
        "",
        f"**Pure A, m=28 sanity diagnostic.** There are only {pure_audit[28]['total_valid_subsets']} valid unique 28-of-29 training sets under the indivisible-center rule. Every valid split leaves one non-center record for testing, so per-subset R2_conv and rank correlations are mathematically undefined. Pooling the 26 unique held-out predictions gives R2_conv={pure_m28['pooled_diagnostic_R2_conv']:.3f} and Spearman rho={pure_m28['pooled_diagnostic_spearman_rho']:.3f}. This is within the requested -0.40 to -0.10 range and differs from the all-29 grouped-LOOCV R2_conv by {validations['pure_m28_pooled_vs_grouped_loocv']['absolute_difference']:.3f}. It is a diagnostic, not a subset mean.",
        "",
        f"**Mixed B, m=20 sanity check.** The 8-literature + 12-in-house cell exactly reuses the Step 2h k=12 subset sequence: {validations['mixed_m20_vs_step2h_k12']['subset_sequence_exact_match']}. Its R2_conv is {m20['R2_conv_mean']:.3f} +/- {m20['R2_conv_std']:.3f}; maximum difference from the prior summary is {validations['mixed_m20_vs_step2h_k12']['maximum_metric_difference']:.3e}. Status: {validations['mixed_m20_vs_step2h_k12']['status']}.",
        "",
        "Configuration A and B have matched total training sizes but different held-out in-house test sizes. R2_conv is normalized within each test set, but the differing test composition remains a caveat. No best-case subsets are reported.",
        "",
        "## 2. Configuration A: Pure In-House",
        "",
        *summary_table_lines(rows, "pure_inhouse"),
        "",
        "Subset-count audit:",
        "",
        "| m | total valid | used | skipped by 200 cap |",
        "|---:|---:|---:|---:|",
    ]
    for m in M_VALUES:
        audit = pure_audit[m]
        lines.append(
            f"| {m} | {audit['total_valid_subsets']} | {audit['n_used']} | {audit['n_skipped_by_cap']} |"
        )

    lines += [
        "",
        "## 3. Configuration B: Mixed Literature and In-House",
        "",
        *summary_table_lines(rows, "mixed"),
        "",
        "Subset-count audit:",
        "",
        "| m | in-house anchors | total valid | used | skipped by 200 cap |",
        "|---:|---:|---:|---:|---:|",
    ]
    for m in M_VALUES:
        audit = mixed_audit[m]
        lines.append(
            f"| {m} | {m - 8} | {audit['total_valid_subsets']} | {audit['n_used']} | {audit['n_skipped_by_cap']} |"
        )

    lines += [
        "",
        "## 4. Direct Head-to-Head Comparison",
        "",
        *direct_lines,
        "",
        "The `m=28` pure point is shown as a pooled diagnostic rather than a mean +/- std and is excluded from formal error-bar separation claims.",
        "",
        "## 5. Interpretation",
        "",
        f"Across the formally comparable m values with defined per-subset R2_conv (m={', '.join(map(str, [8, 12, 16, 20, 24]))}), pure in-house has the higher mean at m={', '.join(map(str, pure_wins)) if pure_wins else 'none'}. Mixed training has an equal or higher mean at {('m=' + ', '.join(map(str, mixed_wins))) if mixed_wins else 'no formally comparable m value'}.",
        "",
        f"Using non-overlap of mean +/- 1 SD intervals as the requested descriptive separation criterion, pure in-house is separated from mixed at m={', '.join(map(str, separated)) if separated else 'none'}. This is descriptive rather than a formal paired significance test because the two configurations use different test sets.",
        "",
        f"At m=28, the pure pooled diagnostic R2_conv is {m28_outcome['pure_R2']:.3f}, compared with mixed mean {m28_outcome['mixed_R2']:.3f}; this supports the same direction but is not included in the mean +/- std comparison.",
        "",
        "R2_conv is the primary result. Spearman rho is retained as a secondary ordering diagnostic; near-zero or crossing rank correlations do not override a consistently worse mixed-training R2_conv.",
        "",
    ]

    if mixed_wins:
        bottom_line = (
            "The matched-size analysis does not support a uniformly negative literature-value "
            "claim because mixed training reaches or exceeds pure in-house at one or more formal m values."
        )
    elif len(pure_wins) == 5:
        bottom_line = (
            "For this Xiao-Bolla pair under the fixed 4-feature Ridge protocol, the sample-size-matched "
            "comparison supports negative literature augmentation value for predicting in-house flux: "
            "pure in-house training has higher mean R2_conv at every formally comparable matched size."
        )
    else:
        bottom_line = (
            "The matched-size evidence is mixed and does not justify a simple negative-value conclusion."
        )

    lines += [
        f"**Bottom line.** {bottom_line}",
        "",
        "This conclusion is bounded to this specific Xiao-Bolla dataset pair, target, feature bridge, and Ridge model. It does not imply that literature data is generally useless or harmful.",
        "",
        "## Outputs",
        "",
        "- `sample_matched_pure_inhouse_results.json`",
        "- `sample_matched_mixed_results.json`",
        "- `sample_matched_summary.csv`",
        "- `figure_sample_matched_comparison.pdf`",
        "- `figure_sample_matched_comparison.png`",
        "- `run_demo2_sample_matched.py`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    xiao, bolla = fewshot.build_inputs()
    if len(xiao) != 29 or len(bolla) != 8:
        raise ValueError(f"Expected Xiao=29 and Bolla=8, got {len(xiao)} and {len(bolla)}")

    pure_plan, pure_audit = pure_subset_plan(xiao)
    mixed_plan, mixed_audit = mixed_subset_plan(xiao)

    pure_records = [
        run_one_subset("pure_inhouse", m, number, subset, xiao, bolla)
        for m in M_VALUES
        for number, subset in enumerate(pure_plan[m], start=1)
    ]
    mixed_records = [
        run_one_subset("mixed", m, number, subset, xiao, bolla)
        for m in M_VALUES
        for number, subset in enumerate(mixed_plan[m], start=1)
    ]

    pure_summary = aggregate_records(pure_records, pure_audit)
    mixed_summary = aggregate_records(mixed_records, mixed_audit)
    pure_m28 = pooled_m28_diagnostic(pure_records)
    combined_summary = pure_summary + mixed_summary
    add_pooled_fields(combined_summary, pure_m28)
    validations = validate_against_existing(mixed_records, mixed_summary, pure_m28)
    if validations["mixed_m20_vs_step2h_k12"]["status"] != "PASS":
        raise RuntimeError("Mixed m=20 did not reproduce Step 2h k=12")
    if validations["pure_m28_pooled_vs_grouped_loocv"]["status"] != "PASS":
        raise RuntimeError("Pure m=28 pooled sanity diagnostic is outside the requested range")

    pure_payload = build_payload(
        "pure_inhouse",
        pure_records,
        pure_summary,
        pure_audit,
        pooled_m28=pure_m28,
    )
    pure_payload["sanity_checks"] = {
        "pure_m28_pooled_vs_grouped_loocv": validations[
            "pure_m28_pooled_vs_grouped_loocv"
        ]
    }
    mixed_payload = build_payload(
        "mixed",
        mixed_records,
        mixed_summary,
        mixed_audit,
    )
    mixed_payload["sanity_checks"] = {
        "mixed_m20_vs_step2h_k12": validations["mixed_m20_vs_step2h_k12"]
    }

    write_json(PURE_JSON, pure_payload)
    write_json(MIXED_JSON, mixed_payload)
    write_summary_csv(combined_summary)
    make_figure(combined_summary, pure_m28)
    make_report(combined_summary, validations, pure_audit, mixed_audit)

    print("[DEMO2 SAMPLE-MATCHED] Done")
    print(f"Pure subset records: {len(pure_records)}")
    print(f"Mixed subset records: {len(mixed_records)}")
    print(
        "Pure m=28 pooled sanity: "
        f"R2={pure_m28['metrics']['R2_conv']:.3f} "
        f"rho={pure_m28['metrics']['spearman_rho']:.3f}"
    )
    m20 = next(row for row in mixed_summary if row["m"] == 20)
    print(
        "Mixed m=20 reproduction: "
        f"R2={m20['R2_conv_mean']:.3f}+/-{m20['R2_conv_std']:.3f} "
        f"status={validations['mixed_m20_vs_step2h_k12']['status']}"
    )
    print(f"Pure JSON: {PURE_JSON}")
    print(f"Mixed JSON: {MIXED_JSON}")
    print(f"Summary: {SUMMARY_CSV}")
    print(f"Figure: {FIG_PDF}")
    print(f"Figure: {FIG_PNG}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
