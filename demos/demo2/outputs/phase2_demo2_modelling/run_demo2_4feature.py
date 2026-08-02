from __future__ import annotations

import csv
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_demo2_modelling as demo2


OUT = SCRIPT_DIR
RANDOM_STATE = 42
LOG10_2 = math.log10(2.0)
MODELS = ["ridge", "gpr"]
TARGETS = ["log10", "raw"]
FEATURE_VARIANTS = {
    "2_feature": ["log10_vehicle_solubility", "ethanol_fraction"],
    "4_feature": ["log10_vehicle_solubility", "ethanol_fraction", "pg_fraction", "water_fraction"],
}


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return [json_safe(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, float):
        return None if math.isnan(value) else value
    return value


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(json_safe(payload), indent=2, sort_keys=True), encoding="utf-8")


def add_fraction_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if str(out["dataset"].iloc[0]) == "Xiao":
        out["pg_fraction"] = out["pg"].to_numpy(dtype=float) / 100.0
        out["water_fraction"] = out["water_xiao"].to_numpy(dtype=float) / 100.0
    else:
        out["pg_fraction"] = out.get("propylene_glycol", pd.Series(0.0, index=out.index)).fillna(0.0).to_numpy(dtype=float) / 100.0
        out["water_fraction"] = out.get("water", pd.Series(0.0, index=out.index)).fillna(0.0).to_numpy(dtype=float) / 100.0
    return out


def target_values(df: pd.DataFrame, target: str) -> np.ndarray:
    if target == "log10":
        return df["log10_J"].to_numpy(dtype=float)
    if target == "raw":
        return df["J"].to_numpy(dtype=float)
    raise ValueError(target)


def predicted_j(y_pred: np.ndarray, target: str) -> np.ndarray:
    if target == "log10":
        return np.power(10.0, y_pred)
    if target == "raw":
        return y_pred
    raise ValueError(target)


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


def fit_predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    model_name: str,
    target: str,
) -> tuple[np.ndarray, np.ndarray | None, dict]:
    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[features].to_numpy(dtype=float))
    x_test = scaler.transform(test[features].to_numpy(dtype=float))
    y_train = target_values(train, target)
    model_info: dict = {
        "features": features,
        "feature_scaler_mean": {name: float(value) for name, value in zip(features, scaler.mean_)},
        "feature_scaler_scale": {name: float(value) for name, value in zip(features, scaler.scale_)},
    }
    if model_name == "ridge":
        model = Ridge(alpha=1.0)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        model_info.update(
            {
                "model": "Ridge(alpha=1.0)",
                "ridge_intercept": float(model.intercept_),
                "ridge_coefficients_scaled_feature_space": {name: float(value) for name, value in zip(features, model.coef_)},
            }
        )
        return pred, None, model_info
    if model_name == "gpr":
        kernel = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=1.0)
        model = GaussianProcessRegressor(
            kernel=kernel,
            normalize_y=True,
            n_restarts_optimizer=10,
            random_state=RANDOM_STATE,
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            model.fit(x_train, y_train)
        pred, sigma = model.predict(x_test, return_std=True)
        model_info.update(
            {
                "model": "GaussianProcessRegressor(ConstantKernel*RBF + WhiteKernel, normalize_y=True, n_restarts_optimizer=10)",
                "kernel_initial": str(kernel),
                "kernel_optimized": str(model.kernel_),
                "log_marginal_likelihood": float(model.log_marginal_likelihood(model.kernel_.theta)),
                "convergence_warnings": [str(item.message) for item in caught],
            }
        )
        return pred, sigma, model_info
    raise ValueError(model_name)


def within_2x_from_j(true_j: np.ndarray, pred_j: np.ndarray) -> tuple[float, int, int, list[bool]]:
    flags: list[bool] = []
    nonphysical = 0
    for truth, pred in zip(true_j, pred_j):
        if truth <= 0 or pred <= 0:
            flags.append(False)
            nonphysical += 1
        else:
            flags.append(bool(abs(math.log10(pred) - math.log10(truth)) <= LOG10_2))
    count = int(sum(flags))
    return float(count / len(flags)), count, nonphysical, flags


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, true_j: np.ndarray, pred_j: np.ndarray) -> dict:
    within, within_count, nonphysical, _flags = within_2x_from_j(true_j, pred_j)
    return {
        "R2_conv": float(r2_score(y_true, y_pred)),
        "RMSE": float(math.sqrt(mean_squared_error(y_true, y_pred))),
        "spearman_rho": correlation_or_none(y_true, y_pred, "spearman"),
        "pearson_r": correlation_or_none(y_true, y_pred, "pearson"),
        "within_2x": within,
        "within_2x_count": within_count,
        "nonphysical_predictions": nonphysical,
        "n": int(len(y_true)),
        "mean_residual": float(np.mean(y_pred - y_true)),
        "median_abs_residual": float(np.median(np.abs(y_pred - y_true))),
    }


def prediction_rows(
    direction: str,
    feature_variant: str,
    model_name: str,
    target: str,
    test: pd.DataFrame,
    y_pred: np.ndarray,
    sigma: np.ndarray | None,
) -> list[dict]:
    pred_flux = predicted_j(y_pred, target)
    _within, _count, _nonphysical, flags = within_2x_from_j(test["J"].to_numpy(dtype=float), pred_flux)
    rows = []
    for (_, record), pred_y, pred_j, flag, idx in zip(test.iterrows(), y_pred, pred_flux, flags, range(len(test))):
        rows.append(
            {
                "direction": direction,
                "feature_variant": feature_variant,
                "model": model_name,
                "target": target,
                "dataset": record["dataset"],
                "record_id": record["record_id"],
                "formulation_label": record["formulation_label"],
                "actual_target": float(record["log10_J"] if target == "log10" else record["J"]),
                "predicted_target": float(pred_y),
                "sigma_target_space": None if sigma is None else float(sigma[idx]),
                "actual_J": float(record["J"]),
                "predicted_J": float(pred_j),
                "nonphysical_prediction": bool(pred_j <= 0),
                "within_2x": bool(flag),
                "feat_log10_vehicle_solubility": float(record["log10_vehicle_solubility"]),
                "feat_ethanol_fraction": float(record["ethanol_fraction"]),
                "feat_pg_fraction": float(record["pg_fraction"]),
                "feat_water_fraction": float(record["water_fraction"]),
            }
        )
    return rows


def run_transfer_cell(
    direction: str,
    feature_variant: str,
    train: pd.DataFrame,
    test: pd.DataFrame,
    model_name: str,
    target: str,
) -> dict:
    features = FEATURE_VARIANTS[feature_variant]
    y_pred, sigma, model_info = fit_predict(train, test, features, model_name, target)
    y_true = target_values(test, target)
    pred_flux = predicted_j(y_pred, target)
    metrics = compute_metrics(y_true, y_pred, test["J"].to_numpy(dtype=float), pred_flux)
    if sigma is not None:
        metrics["mean_sigma"] = float(np.mean(sigma))
        metrics["median_sigma"] = float(np.median(sigma))
        metrics["max_sigma"] = float(np.max(sigma))
    return {
        "direction": direction,
        "feature_variant": feature_variant,
        "features": features,
        "model": model_name,
        "target": target,
        "target_space": "log10(J)" if target == "log10" else "raw J",
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "train_dataset": str(train["dataset"].iloc[0]),
        "test_dataset": str(test["dataset"].iloc[0]),
        "metrics": metrics,
        "model_info": model_info,
        "predictions": prediction_rows(direction, feature_variant, model_name, target, test, y_pred, sigma),
    }


def feature_stats(df: pd.DataFrame, dataset_name: str) -> dict:
    payload: dict = {"dataset": dataset_name, "features": {}, "per_record": []}
    for feature in ["pg_fraction", "water_fraction"]:
        values = df[feature].to_numpy(dtype=float)
        payload["features"][feature] = {
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "mean": float(np.mean(values)),
            "std_population": float(np.std(values, ddof=0)),
            "nonzero_variance": bool(np.std(values, ddof=0) > 1e-12),
            "flag_constant_or_near_constant": bool(np.std(values, ddof=0) <= 1e-12),
        }
    for _, row in df.iterrows():
        payload["per_record"].append(
            {
                "record_id": str(row["record_id"]),
                "pg_fraction": float(row["pg_fraction"]),
                "water_fraction": float(row["water_fraction"]),
            }
        )
    return payload


def run_grid(xiao: pd.DataFrame, bolla: pd.DataFrame) -> dict:
    result: dict = {
        "metadata": {
            "task": "Demo 2 Step 2g 4-feature bridge control",
            "random_state": RANDOM_STATE,
            "feature_variants": FEATURE_VARIANTS,
            "ridge_alpha": 1.0,
            "gpr_kernel_spec": "ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=1.0)",
            "gpr_normalize_y": True,
            "gpr_n_restarts_optimizer": 10,
            "scaler": "StandardScaler fit on train only",
            "pg_water_source": "Xiao: hardcoded pg/water_xiao from run_demo2_modelling.py; Bolla: propylene_glycol/water columns merged from bolla_composition_real.csv by build_bolla().",
        },
        "feature_sanity": {
            "xiao": feature_stats(xiao, "Xiao"),
            "bolla": feature_stats(bolla, "Bolla"),
        },
        "variants": {},
    }
    directions = {
        "xiao_to_bolla": (xiao, bolla),
        "bolla_to_xiao": (bolla, xiao),
    }
    for variant in FEATURE_VARIANTS:
        result["variants"][variant] = {"features": FEATURE_VARIANTS[variant], "directions": {}}
        for direction, (train, test) in directions.items():
            result["variants"][variant]["directions"][direction] = {}
            for model_name in MODELS:
                result["variants"][variant]["directions"][direction][model_name] = {}
                for target in TARGETS:
                    result["variants"][variant]["directions"][direction][model_name][target] = run_transfer_cell(
                        direction,
                        variant,
                        train,
                        test,
                        model_name,
                        target,
                    )
    return result


def write_primary_csv(path: Path, result: dict) -> None:
    columns = [
        "record_id",
        "J_actual",
        "logJ_actual",
        "logJ_pred",
        "J_pred",
        "residual_log",
        "abs_residual_log",
        "within_2x",
        "feat_log10_vehicle_solubility",
        "feat_ethanol_fraction",
        "feat_pg_fraction",
        "feat_water_fraction",
    ]
    rows = []
    for pred in result["predictions"]:
        residual = float(pred["predicted_target"] - pred["actual_target"])
        rows.append(
            {
                "record_id": pred["record_id"],
                "J_actual": pred["actual_J"],
                "logJ_actual": pred["actual_target"],
                "logJ_pred": pred["predicted_target"],
                "J_pred": pred["predicted_J"],
                "residual_log": residual,
                "abs_residual_log": abs(residual),
                "within_2x": int(pred["within_2x"]),
                "feat_log10_vehicle_solubility": pred["feat_log10_vehicle_solubility"],
                "feat_ethanol_fraction": pred["feat_ethanol_fraction"],
                "feat_pg_fraction": pred["feat_pg_fraction"],
                "feat_water_fraction": pred["feat_water_fraction"],
            }
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: f"{value:.12f}" if isinstance(value, float) else value for key, value in row.items()})


def fmt(value: float | None, digits: int = 3, na: str = "NA") -> str:
    if value is None:
        return na
    if isinstance(value, float) and math.isnan(value):
        return na
    return f"{float(value):.{digits}f}"


def count_text(result: dict) -> str:
    m = result["metrics"]
    return f"{m['within_2x_count']}/{m['n']}"


def comparison_row(direction_label: str, feature_label: str, result: dict) -> str:
    m = result["metrics"]
    return (
        f"| {direction_label} | {feature_label} | {fmt(m['R2_conv'])} | {fmt(m['RMSE'])} | "
        f"{fmt(m['spearman_rho'])} | {count_text(result)} |"
    )


def grid_row(direction: str, model_name: str, target: str, result: dict) -> str:
    m = result["metrics"]
    return (
        f"| {direction} | {model_name} | {target} | {fmt(m['R2_conv'])} | {fmt(m['RMSE'])} | "
        f"{fmt(m['spearman_rho'])} | {fmt(m['pearson_r'])} | {count_text(result)} | "
        f"{m['nonphysical_predictions']} | {fmt(m.get('mean_sigma'), na='')} |"
    )


def affected_record_rows(results: dict) -> list[dict]:
    two = {
        row["record_id"]: row
        for row in results["variants"]["2_feature"]["directions"]["xiao_to_bolla"]["ridge"]["log10"]["predictions"]
    }
    four = {
        row["record_id"]: row
        for row in results["variants"]["4_feature"]["directions"]["xiao_to_bolla"]["ridge"]["log10"]["predictions"]
    }
    rows = []
    for record_id in ["F2A", "F2B", "F6"]:
        old = two[record_id]
        new = four[record_id]
        rows.append(
            {
                "record_id": record_id,
                "logJ_actual": old["actual_target"],
                "logJ_pred_2feature": old["predicted_target"],
                "logJ_pred_4feature": new["predicted_target"],
                "delta_4_minus_2": new["predicted_target"] - old["predicted_target"],
            }
        )
    return rows


def all_fourfeature_negative(results: dict) -> bool:
    for direction in ["xiao_to_bolla", "bolla_to_xiao"]:
        for model_name in MODELS:
            for target in TARGETS:
                if results["variants"]["4_feature"]["directions"][direction][model_name][target]["metrics"]["R2_conv"] >= 0:
                    return False
    return True


def nonnegative_fourfeature_cells(results: dict) -> list[dict]:
    cells = []
    for direction in ["xiao_to_bolla", "bolla_to_xiao"]:
        for model_name in MODELS:
            for target in TARGETS:
                metrics = results["variants"]["4_feature"]["directions"][direction][model_name][target]["metrics"]
                if metrics["R2_conv"] >= 0:
                    cells.append(
                        {
                            "direction": direction,
                            "model": model_name,
                            "target": target,
                            "R2_conv": metrics["R2_conv"],
                            "spearman_rho": metrics["spearman_rho"],
                            "within_2x_count": metrics["within_2x_count"],
                            "n": metrics["n"],
                        }
                    )
    return cells


def sanity_ok(results: dict) -> bool:
    x2b = results["variants"]["2_feature"]["directions"]["xiao_to_bolla"]["ridge"]["log10"]["metrics"]
    b2x = results["variants"]["2_feature"]["directions"]["bolla_to_xiao"]["ridge"]["log10"]["metrics"]
    return (
        round(x2b["R2_conv"], 3) == -0.413
        and round(x2b["spearman_rho"], 3) == -0.548
        and x2b["within_2x_count"] == 3
        and round(b2x["R2_conv"], 3) == -2.363
        and round(b2x["spearman_rho"], 3) == -0.235
        and b2x["within_2x_count"] == 29
    )


def make_report(results: dict) -> str:
    x2b2 = results["variants"]["2_feature"]["directions"]["xiao_to_bolla"]["ridge"]["log10"]
    x2b4 = results["variants"]["4_feature"]["directions"]["xiao_to_bolla"]["ridge"]["log10"]
    b2x2 = results["variants"]["2_feature"]["directions"]["bolla_to_xiao"]["ridge"]["log10"]
    b2x4 = results["variants"]["4_feature"]["directions"]["bolla_to_xiao"]["ridge"]["log10"]
    affected = affected_record_rows(results)
    all_negative = all_fourfeature_negative(results)
    f2a_f2b_delta = abs(affected[0]["logJ_pred_4feature"] - affected[1]["logJ_pred_4feature"])
    max_abs_delta = max(abs(row["delta_4_minus_2"]) for row in affected)
    any_feature_flags = [
        f"{dataset}:{feature}"
        for dataset in ["xiao", "bolla"]
        for feature, stats in results["feature_sanity"][dataset]["features"].items()
        if stats["flag_constant_or_near_constant"]
    ]
    nonnegative_cells = nonnegative_fourfeature_cells(results)

    lines = [
        "# Demo 2 Step 2g: 4-Feature Bridge Control",
        "",
        "## Setup",
        "",
        "This control keeps the existing Yalkowsky `log10_vehicle_solubility` feature and adds independent PG and water fractions to remove ethanol's privileged status. The 4-feature bridge is `log10_vehicle_solubility`, `ethanol_fraction`, `pg_fraction`, and `water_fraction`. All model settings match the 2-feature run.",
        "",
        "## Feature Sanity",
        "",
        "| Dataset | Feature | min | max | mean | non-zero variance? |",
        "|---|---|---:|---:|---:|---|",
    ]
    for dataset in ["xiao", "bolla"]:
        for feature, stats in results["feature_sanity"][dataset]["features"].items():
            lines.append(
                f"| {dataset.capitalize()} | {feature} | {fmt(stats['min'])} | {fmt(stats['max'])} | "
                f"{fmt(stats['mean'])} | {'yes' if stats['nonzero_variance'] else 'NO'} |"
            )
    if any_feature_flags:
        lines += ["", f"Feature variance warning: {', '.join(any_feature_flags)} were constant or near-constant."]
    else:
        lines += ["", "Both added features have non-zero variance in both datasets."]

    lines += [
        "",
        "### Bolla PG/Water Per Record",
        "",
        "| record_id | pg_fraction | water_fraction |",
        "|---|---:|---:|",
    ]
    for row in results["feature_sanity"]["bolla"]["per_record"]:
        lines.append(f"| {row['record_id']} | {fmt(row['pg_fraction'], 6)} | {fmt(row['water_fraction'], 6)} |")

    lines += [
        "",
        "## Sanity Check: 2-Feature Ridge/log10 Reproduction",
        "",
        f"- Xiao->Bolla 2-feature Ridge/log10: R2_conv={x2b2['metrics']['R2_conv']:.3f}, Spearman={x2b2['metrics']['spearman_rho']:.3f}, within-2x={count_text(x2b2)}.",
        f"- Bolla->Xiao 2-feature Ridge/log10: R2_conv={b2x2['metrics']['R2_conv']:.3f}, Spearman={b2x2['metrics']['spearman_rho']:.3f}, within-2x={count_text(b2x2)}.",
        f"Sanity status: {'PASS' if sanity_ok(results) else 'FAIL'}.",
        "",
        "## Table A: Primary Ridge/log10 Head-to-Head",
        "",
        "| Direction | Feature set | R2_conv | RMSE_logJ | Spearman rho | within-2x |",
        "|---|---|---:|---:|---:|---:|",
        comparison_row("Xiao->Bolla", "2-feature (main line)", x2b2),
        comparison_row("Xiao->Bolla", "4-feature (this run)", x2b4),
        comparison_row("Bolla->Xiao", "2-feature (main line)", b2x2),
        comparison_row("Bolla->Xiao", "4-feature (this run)", b2x4),
        "",
        "## Table B: Solubilised Bolla Records Under Xiao->Bolla Ridge/log10",
        "",
        "| Bolla record | logJ_actual | 2-feature pred | 4-feature pred | delta 4-2 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in affected:
        lines.append(
            f"| {row['record_id']} | {fmt(row['logJ_actual'])} | {fmt(row['logJ_pred_2feature'])} | "
            f"{fmt(row['logJ_pred_4feature'])} | {fmt(row['delta_4_minus_2'], digits=6)} |"
        )

    lines += [
        "",
        "## Table C: Full 4-Feature Model x Target Grid",
        "",
        "| Direction | Model | Target | R2_conv | RMSE (own space) | Spearman rho | Pearson r | within-2x | non-physical | mean sigma (GPR) |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for direction in ["xiao_to_bolla", "bolla_to_xiao"]:
        for model_name in MODELS:
            for target in TARGETS:
                result = results["variants"]["4_feature"]["directions"][direction][model_name][target]
                lines.append(grid_row(direction, model_name, target, result))

    lines += [
        "",
        "## Interpretation",
        "",
        "1. Does adding PG and water fractions change the negative-transfer conclusion?",
        "",
    ]
    if all_negative:
        lines.append("No. All 4-feature transfer cells remain negative in R2_conv across both directions, both models, and both target spaces.")
    else:
        cell_text = "; ".join(
            f"{cell['direction']} {cell['model']}/{cell['target']} R2_conv={cell['R2_conv']:.3f}, "
            f"rho={fmt(cell['spearman_rho'])}, within={cell['within_2x_count']}/{cell['n']}"
            for cell in nonnegative_cells
        )
        lines.append(
            "Partially. The primary Ridge/log10 cells remain negative in both directions, but the stronger all-model/all-target negative-sign claim is not invariant: "
            f"{cell_text}."
        )
    lines += [
        "",
        "2. Do F2A/F2B/F6 predictions separate under 4-feature?",
        "",
        f"F2A and F2B separate by {f2a_f2b_delta:.6f} log10 units under 4-feature Ridge/log10. The maximum absolute movement among F2A/F2B/F6 relative to 2-feature is {max_abs_delta:.6f} log10 units.",
        "",
        "3. Does the 2-feature bridge over-collapse the chemistry?",
        "",
        "Yes, at least for per-record interpretation: PG and water expose formulation differences hidden by the 2-feature bridge. However, the aggregate transfer metrics remain poor, so the additional chemistry does not overcome the protocol-distance mismatch.",
        "",
        "4. Recommendation",
        "",
        "Use the 4-feature bridge as an important interpretability/sensitivity control because it treats ethanol, PG, and water symmetrically as shared composition axes and exposes hidden per-record chemistry. Keep the primary conclusion anchored to the log10-target transfer results: those remain negative under both 2-feature and 4-feature bridges. Do not claim that every secondary target/model cell remains negative, because 4-feature Xiao->Bolla Ridge/raw is positive.",
        "",
        "## Output Files",
        "",
        "- `transfer_4feature_xiao_to_bolla.csv`",
        "- `transfer_4feature_bolla_to_xiao.csv`",
        "- `transfer_4feature_results.json`",
        "- `demo2_4feature_report.md`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    np.random.seed(RANDOM_STATE)
    xiao = add_fraction_features(demo2.build_xiao())
    bolla = add_fraction_features(demo2.build_bolla())
    results = run_grid(xiao, bolla)

    x2b_primary = results["variants"]["4_feature"]["directions"]["xiao_to_bolla"]["ridge"]["log10"]
    b2x_primary = results["variants"]["4_feature"]["directions"]["bolla_to_xiao"]["ridge"]["log10"]
    write_primary_csv(OUT / "transfer_4feature_xiao_to_bolla.csv", x2b_primary)
    write_primary_csv(OUT / "transfer_4feature_bolla_to_xiao.csv", b2x_primary)
    write_json(OUT / "transfer_4feature_results.json", results)
    (OUT / "demo2_4feature_report.md").write_text(make_report(results), encoding="utf-8")

    print("[DEMO2 4-FEATURE] Done")
    print(f"sanity_2feature={'PASS' if sanity_ok(results) else 'FAIL'}")
    for dataset in ["xiao", "bolla"]:
        for feature, stats in results["feature_sanity"][dataset]["features"].items():
            print(
                f"{dataset}/{feature}: min={stats['min']:.6f} max={stats['max']:.6f} "
                f"mean={stats['mean']:.6f} nonzero_var={stats['nonzero_variance']}"
            )
    for variant in ["2_feature", "4_feature"]:
        for direction in ["xiao_to_bolla", "bolla_to_xiao"]:
            for model_name in MODELS:
                for target in TARGETS:
                    m = results["variants"][variant]["directions"][direction][model_name][target]["metrics"]
                    print(
                        f"{variant}/{direction}/{model_name}/{target}: "
                        f"R2={m['R2_conv']:.3f} RMSE={m['RMSE']:.3f} rho={fmt(m['spearman_rho'])} "
                        f"within={m['within_2x_count']}/{m['n']} nonphys={m['nonphysical_predictions']} "
                        f"sigma={m.get('mean_sigma')}"
                    )


if __name__ == "__main__":
    main()
