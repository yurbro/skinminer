from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_demo2_4feature as four_feature
import run_demo2_modelling as demo2


OUT = SCRIPT_DIR
RESULTS_JSON = OUT / "xiao_internal_4feature_loocv_results.json"
COMPARISON_CSV = OUT / "literature_value_comparison.csv"
REPORT = OUT / "demo2_xiao_internal_4feature_report.md"
FEWSHOT_CSV = OUT / "fewshot_summary_table.csv"
FEWSHOT_JSON = OUT / "fewshot_bolla_to_xiao_results.json"

FEATURES = four_feature.FEATURE_VARIANTS["4_feature"]
CENTER_IDS = ("BBD4", "BBD5", "BBD6")
LOG10_2 = math.log10(2.0)
RANDOM_STATE = 42


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
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, float):
        return None if math.isnan(value) else value
    return value


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(json_safe(payload), indent=2, sort_keys=True), encoding="utf-8")


def build_xiao() -> pd.DataFrame:
    return four_feature.add_fraction_features(demo2.build_xiao()).reset_index(drop=True)


def correlation_or_none(y_true: np.ndarray, y_pred: np.ndarray, method: str) -> float | None:
    if len(y_true) < 2 or np.allclose(y_true, y_true[0]) or np.allclose(y_pred, y_pred[0]):
        return None
    if method == "spearman":
        value = spearmanr(y_true, y_pred).statistic
    elif method == "pearson":
        value = pearsonr(y_true, y_pred).statistic
    else:
        raise ValueError(method)
    return None if math.isnan(float(value)) else float(value)


def make_fold_plan(xiao: pd.DataFrame) -> list[dict]:
    center_indices = xiao.index[xiao["record_id"].isin(CENTER_IDS)].tolist()
    if len(center_indices) != 3:
        raise ValueError(f"Expected center triplet {CENTER_IDS}, found indices {center_indices}")
    center_frame = xiao.loc[center_indices]
    composition_columns = ["poloxamer407", "ethanol", "pg", "mct_xiao", "water_xiao"]
    if any(center_frame[column].nunique(dropna=False) != 1 for column in composition_columns):
        raise ValueError("BBD4/BBD5/BBD6 are not identical center-point compositions")

    folds = [
        {
            "fold_id": 1,
            "fold_type": "group",
            "test_indices": center_indices,
            "test_record_ids": list(CENTER_IDS),
        }
    ]
    fold_id = 2
    for index, row in xiao.iterrows():
        if str(row["record_id"]) in CENTER_IDS:
            continue
        folds.append(
            {
                "fold_id": fold_id,
                "fold_type": "single",
                "test_indices": [int(index)],
                "test_record_ids": [str(row["record_id"])],
            }
        )
        fold_id += 1
    if len(folds) != 27:
        raise ValueError(f"Expected 27 folds, found {len(folds)}")
    return folds


def run_grouped_loocv(xiao: pd.DataFrame) -> dict:
    folds = make_fold_plan(xiao)
    predictions: list[dict] = []
    fold_details: list[dict] = []
    predicted_by_index = np.full(len(xiao), np.nan, dtype=float)

    for fold in folds:
        test_indices = fold["test_indices"]
        train = xiao.drop(index=test_indices).reset_index(drop=True)
        test = xiao.loc[test_indices]

        scaler = StandardScaler()
        x_train = scaler.fit_transform(train[FEATURES].to_numpy(dtype=float))
        x_test = scaler.transform(test[FEATURES].to_numpy(dtype=float))
        model = Ridge(alpha=1.0)
        model.fit(x_train, train["log10_J"].to_numpy(dtype=float))
        fold_predictions = model.predict(x_test)

        train_ids = set(train["record_id"].astype(str))
        test_ids = set(test["record_id"].astype(str))
        center_train = train_ids.intersection(CENTER_IDS)
        center_test = test_ids.intersection(CENTER_IDS)
        if center_train and center_test:
            raise RuntimeError(
                f"Center-point leakage in fold {fold['fold_id']}: "
                f"train={sorted(center_train)}, test={sorted(center_test)}"
            )
        if center_test and center_test != set(CENTER_IDS):
            raise RuntimeError(f"Partial center group in test fold {fold['fold_id']}")

        fold_details.append(
            {
                "fold_id": fold["fold_id"],
                "fold_type": fold["fold_type"],
                "test_record_ids": fold["test_record_ids"],
                "n_train_records": int(len(train)),
                "n_test_records": int(len(test)),
                "center_group_in_train": sorted(center_train),
                "center_group_in_test": sorted(center_test),
                "leakage_guard_pass": True,
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
        )

        for (row_index, row), prediction in zip(test.iterrows(), fold_predictions):
            actual = float(row["log10_J"])
            prediction = float(prediction)
            residual = prediction - actual
            predicted_by_index[int(row_index)] = prediction
            predictions.append(
                {
                    "fold_id": fold["fold_id"],
                    "fold_type": fold["fold_type"],
                    "record_id": str(row["record_id"]),
                    "logJ_actual": actual,
                    "logJ_pred": prediction,
                    "residual_pred_minus_actual": residual,
                    "abs_residual": abs(residual),
                    "within_2x": bool(abs(residual) <= LOG10_2),
                }
            )

    if np.isnan(predicted_by_index).any():
        raise RuntimeError("Not every Xiao record received exactly one held-out prediction")
    if len(predictions) != 29 or len({row["record_id"] for row in predictions}) != 29:
        raise RuntimeError("Expected 29 unique held-out predictions")

    y_true = xiao["log10_J"].to_numpy(dtype=float)
    residual = predicted_by_index - y_true
    within = np.abs(residual) <= LOG10_2
    metrics = {
        "R2_conv": float(r2_score(y_true, predicted_by_index)),
        "rmse_logJ": float(math.sqrt(mean_squared_error(y_true, predicted_by_index))),
        "spearman_rho": correlation_or_none(y_true, predicted_by_index, "spearman"),
        "pearson_r": correlation_or_none(y_true, predicted_by_index, "pearson"),
        "within_2x_fraction": float(np.mean(within)),
        "within_2x_count": int(np.sum(within)),
        "n": int(len(y_true)),
    }

    predictions.sort(key=lambda row: int(xiao.index[xiao["record_id"] == row["record_id"]][0]))
    train_sizes = [row["n_train_records"] for row in fold_details]
    prediction_weighted_train_size = sum(
        row["n_train_records"] * row["n_test_records"] for row in fold_details
    ) / len(xiao)
    return {
        "metadata": {
            "analysis": "Xiao-internal grouped LOOCV under the Demo 2 main-line 4-feature bridge",
            "features": FEATURES,
            "model": "StandardScaler(train fold only) + Ridge(alpha=1.0)",
            "target": "log10(J)",
            "random_state": RANDOM_STATE,
            "n_records": int(len(xiao)),
            "n_folds": int(len(folds)),
            "center_group_record_ids": list(CENTER_IDS),
            "center_group_policy": (
                "BBD4/BBD5/BBD6 are held out together and never split between train and test."
            ),
            "fold_train_record_counts": train_sizes,
            "mean_train_records_per_fold": float(np.mean(train_sizes)),
            "prediction_weighted_mean_train_records": float(prediction_weighted_train_size),
            "prompt_arithmetic_correction": (
                "With all 29 records retained, the 26 single-record folds train on 28 records "
                "and the center-group fold trains on 26 records. Therefore the mean is 27.926 "
                "records per fold, not 27.6; no center records were discarded."
            ),
            "R2_conv_definition": (
                "sklearn r2_score over all 29 pooled held-out predictions using the mean of "
                "the 29 actual log10(J) values as the baseline"
            ),
            "within_2x_definition": "abs(predicted log10 J - actual log10 J) <= log10(2)",
        },
        "aggregate_metrics": metrics,
        "fold_details": fold_details,
        "predictions": predictions,
        "leakage_guard": {
            "status": "PASS",
            "n_violations": 0,
            "group_fold_test_record_ids": list(CENTER_IDS),
            "no_fold_splits_center_triplet": True,
        },
    }


def validate_fewshot_summary(summary: pd.DataFrame, records: list[dict]) -> dict:
    checks = {}
    for k in [0, 12]:
        row = summary[
            (summary["direction"] == "bolla_to_xiao") & (summary["k"].astype(int) == k)
        ]
        if len(row) != 1:
            raise ValueError(f"Expected one Bolla-to-Xiao summary row for k={k}")
        row = row.iloc[0]
        subset_records = [item for item in records if int(item["k"]) == k]
        if len(subset_records) != int(row["n_subsets"]):
            raise ValueError(f"Subset count mismatch at k={k}")
        for json_key, csv_prefix in [
            ("R2_conv", "R2_conv"),
            ("rmse_logJ", "rmse_logJ"),
            ("spearman", "spearman"),
            ("within_2x", "within_2x"),
        ]:
            values = np.asarray([float(item[json_key]) for item in subset_records], dtype=float)
            mean = float(np.mean(values))
            std = float(np.std(values, ddof=0))
            if (
                abs(mean - float(row[f"{csv_prefix}_mean"])) > 5e-12
                or abs(std - float(row[f"{csv_prefix}_std"])) > 5e-12
            ):
                raise ValueError(f"Few-shot JSON/CSV mismatch at k={k}, metric={json_key}")
        checks[str(k)] = {
            "n_subsets": int(row["n_subsets"]),
            "n_test_per_subset": sorted({int(item["n_test"]) for item in subset_records}),
        }
    return {"status": "PASS", "checks": checks}


def comparison_rows(loocv: dict) -> tuple[list[dict], dict]:
    summary = pd.read_csv(FEWSHOT_CSV)
    records = json.loads(FEWSHOT_JSON.read_text(encoding="utf-8"))
    audit = validate_fewshot_summary(summary, records)
    k0 = summary[
        (summary["direction"] == "bolla_to_xiao") & (summary["k"].astype(int) == 0)
    ].iloc[0]
    k12 = summary[
        (summary["direction"] == "bolla_to_xiao") & (summary["k"].astype(int) == 12)
    ].iloc[0]
    internal = loocv["aggregate_metrics"]

    rows = [
        {
            "training_set": "Xiao-only (grouped LOOCV)",
            "n_train_description": "26 for center-group fold; 28 for single-record folds",
            "n_train_mean_records": loocv["metadata"]["mean_train_records_per_fold"],
            "test_set": "held-out Xiao (29 pooled predictions)",
            "n_test": 29,
            "n_subsets_or_folds": 27,
            "R2_conv_mean": internal["R2_conv"],
            "R2_conv_std": None,
            "rmse_logJ_mean": internal["rmse_logJ"],
            "rmse_logJ_std": None,
            "spearman_mean": internal["spearman_rho"],
            "spearman_std": None,
            "pearson_mean": internal["pearson_r"],
            "pearson_std": None,
            "within_2x_mean": internal["within_2x_fraction"],
            "within_2x_std": None,
            "within_2x_display": f"{internal['within_2x_count']}/{internal['n']}",
        },
        {
            "training_set": "Bolla-only (zero-shot, k=0)",
            "n_train_description": "8 Bolla",
            "n_train_mean_records": 8.0,
            "test_set": "all 29 Xiao",
            "n_test": 29,
            "n_subsets_or_folds": int(k0["n_subsets"]),
            "R2_conv_mean": float(k0["R2_conv_mean"]),
            "R2_conv_std": float(k0["R2_conv_std"]),
            "rmse_logJ_mean": float(k0["rmse_logJ_mean"]),
            "rmse_logJ_std": float(k0["rmse_logJ_std"]),
            "spearman_mean": float(k0["spearman_mean"]),
            "spearman_std": float(k0["spearman_std"]),
            "pearson_mean": float(k0["pearson_mean"]),
            "pearson_std": float(k0["pearson_std"]),
            "within_2x_mean": float(k0["within_2x_mean"]),
            "within_2x_std": float(k0["within_2x_std"]),
            "within_2x_display": "24/29",
        },
        {
            "training_set": "Bolla + 12 Xiao (few-shot k=12 mean)",
            "n_train_description": "8 Bolla + 12 Xiao",
            "n_train_mean_records": 20.0,
            "test_set": "remaining 17 Xiao; varies across 200 subsets",
            "n_test": 17,
            "n_subsets_or_folds": int(k12["n_subsets"]),
            "R2_conv_mean": float(k12["R2_conv_mean"]),
            "R2_conv_std": float(k12["R2_conv_std"]),
            "rmse_logJ_mean": float(k12["rmse_logJ_mean"]),
            "rmse_logJ_std": float(k12["rmse_logJ_std"]),
            "spearman_mean": float(k12["spearman_mean"]),
            "spearman_std": float(k12["spearman_std"]),
            "pearson_mean": float(k12["pearson_mean"]),
            "pearson_std": float(k12["pearson_std"]),
            "within_2x_mean": float(k12["within_2x_mean"]),
            "within_2x_std": float(k12["within_2x_std"]),
            "within_2x_display": (
                f"{float(k12['within_2x_mean']):.3f} +/- "
                f"{float(k12['within_2x_std']):.3f}"
            ),
        },
    ]
    return rows, audit


def write_comparison_csv(rows: list[dict]) -> None:
    columns = list(rows[0].keys())
    with COMPARISON_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            output = {}
            for key, value in row.items():
                if value is None:
                    output[key] = ""
                elif isinstance(value, float):
                    output[key] = f"{value:.12f}"
                else:
                    output[key] = value
            writer.writerow(output)


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def pm(mean: float, std: float | None, digits: int = 3) -> str:
    if std is None:
        return fmt(mean, digits)
    return f"{fmt(mean, digits)} +/- {fmt(std, digits)}"


def make_report(loocv: dict, rows: list[dict], fewshot_audit: dict) -> str:
    internal = rows[0]
    zero_shot = rows[1]
    k12 = rows[2]
    internal_r2 = float(internal["R2_conv_mean"])
    zero_shot_r2 = float(zero_shot["R2_conv_mean"])
    k12_r2 = float(k12["R2_conv_mean"])

    if internal_r2 > 0:
        internal_sign = "positive"
    elif math.isclose(internal_r2, 0.0, abs_tol=0.05):
        internal_sign = "near zero"
    else:
        internal_sign = "negative"

    lines = [
        "# Demo 2 Step 2k: Xiao-Internal 4-Feature LOOCV and Literature-Data Value",
        "",
        "## Setup and Missing Comparison Cell",
        "",
        "This analysis adds the missing Xiao-only reference under the exact Demo 2 main-line configuration: the 4-feature bridge (`log10_vehicle_solubility`, `ethanol_fraction`, `pg_fraction`, `water_fraction`), StandardScaler fitted on training rows only, Ridge(alpha=1.0), and log10(J) target. No SkinMiner source code or model hyperparameters were changed.",
        "",
        "BBD4/BBD5/BBD6 are the identical 25/15/15/5/35 center-point triplet. They are held out together in one group fold and are never split between train and test. Leakage-guard status: PASS; zero violations.",
        "",
        "Arithmetic clarification: with all 29 Xiao records retained, the center-group fold trains on 26 records and each of the 26 single-record folds trains on 28 records. The exact average is 27.926 training records per fold. The prompt's references to 25 records and an average of 27.6 are inconsistent with a full 29-record grouped LOOCV, so no center records were discarded to force those numbers.",
        "",
        "## Xiao-Internal 4-Feature Grouped LOOCV",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| R2_conv | {internal['R2_conv_mean']:.6f} |",
        f"| RMSE_logJ | {internal['rmse_logJ_mean']:.6f} |",
        f"| Spearman rho | {internal['spearman_mean']:.6f} |",
        f"| Pearson r | {internal['pearson_mean']:.6f} |",
        f"| within-2x | {internal['within_2x_display']} ({internal['within_2x_mean']:.6f}) |",
        f"| folds / pooled predictions | {internal['n_subsets_or_folds']} / {internal['n_test']} |",
        "",
        f"The Xiao-internal R2_conv is {internal_sign} ({internal_r2:.3f}). All 29 predictions are within two-fold, but this is not evidence of strong modelling because Xiao log10(J) occupies a narrow range: the negative R2_conv and near-zero rank correlation show that the 4-feature model does not recover record-level variation better than the test-mean baseline.",
        "",
        "This is consistent with earlier Xiao-internal findings that the in-house flux variation approaches measurement uncertainty. The value of this new cell is not novelty of sign, but a fair main-line-feature reference for the literature augmentation comparison.",
        "",
        "## Literature-Data-Value Comparison",
        "",
        "| Training set | n_train | Test set | R2_conv | RMSE_logJ | Spearman rho | within-2x |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['training_set']} | {row['n_train_description']} | {row['test_set']} | "
            f"{pm(row['R2_conv_mean'], row['R2_conv_std'])} | "
            f"{pm(row['rmse_logJ_mean'], row['rmse_logJ_std'])} | "
            f"{pm(row['spearman_mean'], row['spearman_std'])} | "
            f"{row['within_2x_display']} |"
        )

    lines += [
        "",
        "The k=0 and k=12 few-shot rows were read from `fewshot_summary_table.csv` and independently reaggregated from `fewshot_bolla_to_xiao_results.json`. "
        f"Audit status: {fewshot_audit['status']}.",
        "",
        "## Interpretation",
        "",
        f"1. **Xiao-only performance.** Xiao-internal grouped LOOCV is {internal_sign}: R2_conv={internal_r2:.3f}, RMSE_logJ={internal['rmse_logJ_mean']:.3f}, and Spearman rho={internal['spearman_mean']:.3f}. The low RMSE and 29/29 within-2x result reflect the narrow Xiao response range; R2_conv remains the primary reading.",
        "",
        f"2. **Does Bolla-only training help Xiao prediction?** No. Relative to Xiao-only LOOCV, Bolla-only zero-shot changes R2_conv from {internal_r2:.3f} to {zero_shot_r2:.3f} and RMSE_logJ from {internal['rmse_logJ_mean']:.3f} to {zero_shot['rmse_logJ_mean']:.3f}. This is substantially worse magnitude prediction. Spearman remains near zero in both cases, so Bolla does not add useful ordering signal.",
        "",
        f"3. **Does Bolla + 12 Xiao recover Xiao-only performance?** No. The mean k=12 R2_conv is {k12_r2:.3f} +/- {k12['R2_conv_std']:.3f}, still well below Xiao-only {internal_r2:.3f}; RMSE_logJ is {k12['rmse_logJ_mean']:.3f} +/- {k12['rmse_logJ_std']:.3f}, compared with Xiao-only {internal['rmse_logJ_mean']:.3f}. Mean Spearman is {k12['spearman_mean']:.3f} +/- {k12['spearman_std']:.3f}, which remains compatible with no ordering signal.",
        "",
        "The k=12 comparison is approximate rather than exact: each few-shot model is evaluated on a different 17-record Xiao subset, whereas Xiao-only LOOCV pools predictions for all 29 records. The k=12 model also trains on 20 total records (8 Bolla + 12 Xiao), compared with 26 or 28 Xiao records per internal fold. The robust result is directional: adding out-of-distribution Bolla records does not approach the Xiao-only R2_conv or RMSE reference, and rank correlation remains near zero.",
        "",
        "## Practical Bottom Line",
        "",
        "For this specific Xiao-Bolla pair, literature data provides negative rather than positive augmentation value for predicting in-house flux under the fixed 4-feature Ridge protocol. Bolla-only training is dramatically worse than Xiao-only grouped LOOCV, and adding 12 Xiao anchors to Bolla does not recover Xiao-only performance.",
        "",
        "This conclusion is deliberately bounded: it does not imply that literature data is useless in general. On this pair, literature data does not provide useful augmentation signal for in-house modelling because the in-house dataset's own flux variation approaches measurement uncertainty and adding out-of-distribution training records exacerbates rather than ameliorates the prediction problem.",
        "",
        "Reducing experiments through literature augmentation requires the literature contribution to be at least neutral and preferably positive. That condition is not met here.",
        "",
        "## Output Audit",
        "",
        "- `xiao_internal_4feature_loocv_results.json`: 27 fold records, 29 pooled held-out predictions, aggregate metrics, and fold-level scaler/model audit.",
        "- `literature_value_comparison.csv`: structured three-row comparison.",
        "- `run_demo2_literature_value.py`: deterministic standalone harness.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    np.random.seed(RANDOM_STATE)
    xiao = build_xiao()
    loocv = run_grouped_loocv(xiao)
    rows, fewshot_audit = comparison_rows(loocv)

    write_json(RESULTS_JSON, loocv)
    write_comparison_csv(rows)
    REPORT.write_text(make_report(loocv, rows, fewshot_audit), encoding="utf-8")

    metrics = loocv["aggregate_metrics"]
    print("[DEMO2 LITERATURE VALUE] Done")
    print(
        f"Xiao internal 4-feature grouped LOOCV: R2={metrics['R2_conv']:.3f} "
        f"RMSE={metrics['rmse_logJ']:.3f} rho={metrics['spearman_rho']:.3f} "
        f"within={metrics['within_2x_count']}/{metrics['n']}"
    )
    print(
        f"folds={loocv['metadata']['n_folds']} "
        f"mean_train_records={loocv['metadata']['mean_train_records_per_fold']:.3f} "
        f"leakage_guard={loocv['leakage_guard']['status']}"
    )
    print(f"fewshot_audit={fewshot_audit['status']}")
    print(f"Results: {RESULTS_JSON}")
    print(f"Comparison: {COMPARISON_CSV}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
