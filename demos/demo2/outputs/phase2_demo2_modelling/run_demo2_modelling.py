from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "phase2_demo2_modelling"
AUDIT = ROOT / "outputs" / "phase2_demo2_audit"
OUT.mkdir(parents=True, exist_ok=True)

FEATURES = ["log10_vehicle_solubility", "ethanol_fraction", "drug_state_solubilized"]
LOG10_2 = math.log10(2.0)
RANDOM_STATE = 42


XIAO_BBD = [
    (30, 20, 15, 5, 25, 10.08, 0.58),
    (30, 15, 10, 5, 35, 11.38, 0.71),
    (25, 20, 20, 5, 25, 9.50, 1.20),
    (25, 15, 15, 5, 35, 9.18, 1.34),
    (25, 15, 15, 5, 35, 10.89, 0.41),
    (25, 15, 15, 5, 35, 10.39, 0.35),
    (25, 10, 20, 5, 35, 10.62, 1.69),
    (25, 20, 10, 5, 35, 8.60, 0.47),
    (20, 20, 15, 5, 35, 8.86, 0.82),
    (30, 10, 15, 5, 35, 11.44, 0.69),
    (20, 15, 10, 5, 45, 9.93, 0.80),
    (25, 10, 10, 5, 45, 9.28, 0.56),
    (20, 15, 20, 5, 35, 10.48, 0.53),
    (30, 15, 20, 5, 25, 9.11, 0.44),
    (20, 10, 15, 5, 45, 10.67, 1.02),
]
XIAO_LHS = [
    (21.0, 16.6, 17.3, 5, 25, 11.36, 0.29),
    (21.3, 20.0, 10.6, 5, 35, 13.52, 0.77),
    (22.7, 14.4, 16.0, 5, 25, 13.17, 1.06),
    (23.5, 17.9, 18.1, 5, 35, 10.49, 0.80),
    (24.3, 13.1, 11.9, 5, 35, 11.65, 0.20),
    (25.5, 10.1, 14.8, 5, 35, 11.52, 0.42),
    (26.6, 11.6, 16.8, 5, 35, 13.36, 0.10),
    (27.2, 18.7, 13.1, 5, 35, 11.45, 0.56),
    (28.3, 15.5, 12.7, 5, 35, 12.50, 1.16),
    (29.2, 12.9, 19.6, 5, 35, 11.41, 0.80),
]
XIAO_RUN = [
    (21.17, 19.95, 10.59, 5, None, 10.12, 0.54),
    (25.22, 19.41, 19.29, 5, None, 8.02, 0.81),
    (26.06, 11.99, 15.70, 5, None, 10.00, 0.91),
    (20.95, 19.44, 12.14, 5, None, 14.15, 0.77),
]


XIAO_SOLUBILITY = {
    "ethanol": 337.78,
    "pg": 189.41,
    "water": 0.19,
}

BOLLA_STRUCTURAL_EXCLUDED = {
    "white_petrolatum",
    "span20",
    "kolliphor_cs20",
    "glycerol_monostearate",
    "cetyl_alcohol",
    "stearyl_alcohol",
    "cetostearyl_alcohol",
    "sepineo_se68",
    "sepineo_p600",
    "tefose63",
    "hpmc",
    "carbopol974",
    "hpc",
}


def fnum(value: float | int | np.floating | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return float(value)


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, float):
        return None if math.isnan(value) else value
    return value


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(json_safe(payload), indent=2, sort_keys=True), encoding="utf-8")


def log_mixture_solubility(row: pd.Series, solubility: dict[str, float], components: list[str]) -> tuple[float, float, str]:
    weights = []
    labels = []
    for component in components:
        value = float(row.get(component, 0.0) or 0.0)
        if value > 0 and component in solubility:
            weights.append(value)
            labels.append(component)
    total = float(sum(weights))
    if total <= 0:
        return float("nan"), 0.0, ""
    log_s = sum((weight / total) * math.log10(solubility[label]) for weight, label in zip(weights, labels))
    return log_s, total, ";".join(labels)


def build_xiao() -> pd.DataFrame:
    rows = []
    for prefix, data in (("BBD", XIAO_BBD), ("LHS", XIAO_LHS), ("RUN", XIAO_RUN)):
        for index, (p407, ethanol, pg, mct, water, j, j_sd) in enumerate(data, start=1):
            if water is None:
                water = 95.0 - p407 - ethanol - pg - mct
            record_id = f"{prefix}{index}"
            rows.append(
                {
                    "dataset": "Xiao",
                    "record_id": record_id,
                    "formulation_label": record_id,
                    "subset": prefix,
                    "api_pct_ww": 5.0,
                    "poloxamer407": float(p407),
                    "ethanol": float(ethanol),
                    "pg": float(pg),
                    "mct_xiao": float(mct),
                    "water_xiao": float(water),
                    "J": float(j),
                    "J_sd": float(j_sd),
                    "protocol_cell": "Franz",
                    "membrane": "Strat-M",
                    "receptor_medium": "PBS pH 7.4",
                    "eda_cm2": 2.01,
                    "duration_h": 30.0,
                }
            )
    df = pd.DataFrame(rows)
    df["log10_vehicle_solubility"], df["solubilising_weight_pct"], df["solubilising_components"] = zip(
        *df.apply(
            lambda row: log_mixture_solubility(
                pd.Series({"ethanol": row["ethanol"], "pg": row["pg"], "water": row["water_xiao"]}),
                XIAO_SOLUBILITY,
                ["ethanol", "pg", "water"],
            ),
            axis=1,
        )
    )
    df["ethanol_fraction"] = df["ethanol"] / 100.0
    df["drug_state_solubilized"] = 0
    df["log10_J"] = np.log10(df["J"])
    return df


def build_bolla() -> pd.DataFrame:
    endpoints = pd.read_csv(AUDIT / "bolla_extracted_records_real.csv")
    composition = pd.read_csv(AUDIT / "bolla_composition_real.csv")
    solubility_table = pd.read_csv(AUDIT / "bolla_solubility_real.csv")
    df = composition.merge(
        endpoints[["formulation_label", "J_value", "J_sd", "Q24_value", "Q24_sd", "lag_h", "device", "receptor_medium", "eda_cm2"]],
        on="formulation_label",
        how="left",
    )
    bolla_sol = {row["excipient"]: float(row["solubility_mg_per_g"]) for _, row in solubility_table.iterrows()}
    bolla_sol.update({"water": 0.19, "ethanol": 337.78})
    sol_components = sorted(bolla_sol)
    df["log10_vehicle_solubility"], df["solubilising_weight_pct"], df["solubilising_components"] = zip(
        *df.apply(lambda row: log_mixture_solubility(row, bolla_sol, sol_components), axis=1)
    )
    df["dataset"] = "Bolla"
    df["record_id"] = df["formulation_label"]
    df["subset"] = "Table7"
    df["J"] = df["J_value"].astype(float)
    df["J_sd"] = df["J_sd"].astype(float)
    df["log10_J"] = np.log10(df["J"])
    df["ethanol_fraction"] = df["ethanol"].astype(float) / 100.0
    df["drug_state_solubilized"] = (df["drug_state"].astype(str).str.lower() == "solubilized").astype(int)
    df["api_pct_ww"] = df["ibuprofen"].astype(float)
    df["protocol_cell"] = "flow-through"
    df["membrane"] = "Strat-M"
    df["duration_h"] = 24.0
    return df


def train_predict(train: pd.DataFrame, test: pd.DataFrame) -> tuple[np.ndarray, Pipeline]:
    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("ridge", Ridge(alpha=1.0)),
        ]
    )
    model.fit(train[FEATURES].to_numpy(), train["log10_J"].to_numpy())
    pred = model.predict(test[FEATURES].to_numpy())
    return pred, model


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, train_mean: float) -> dict:
    residual = y_pred - y_true
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_train = float(np.sum((y_true - train_mean) ** 2))
    spearman = spearmanr(y_true, y_pred).statistic if len(y_true) > 1 else float("nan")
    pearson = pearsonr(y_true, y_pred).statistic if len(y_true) > 1 else float("nan")
    return {
        "spearman_rho": float(spearman),
        "rmse_logJ": float(math.sqrt(mean_squared_error(y_true, y_pred))),
        "within_2x": float(np.mean(np.abs(residual) <= LOG10_2)),
        "within_2x_count": int(np.sum(np.abs(residual) <= LOG10_2)),
        "n": int(len(y_true)),
        "R2_conv": float(r2_score(y_true, y_pred)),
        "R2_gen_train_mean_baseline": float(1.0 - ss_res / ss_train) if ss_train > 0 else float("nan"),
        "pearson_r": float(pearson),
        "mean_residual_log10": float(np.mean(residual)),
        "median_abs_residual_log10": float(np.median(np.abs(residual))),
    }


def transfer_result(name: str, train: pd.DataFrame, test: pd.DataFrame) -> dict:
    pred, model = train_predict(train, test)
    y = test["log10_J"].to_numpy()
    metrics = compute_metrics(y, pred, float(train["log10_J"].mean()))
    predictions = []
    for (_, row), y_pred in zip(test.iterrows(), pred):
        predictions.append(
            {
                "dataset": row["dataset"],
                "record_id": row["record_id"],
                "formulation_label": row["formulation_label"],
                "actual_log10_J": float(row["log10_J"]),
                "predicted_log10_J": float(y_pred),
                "residual_log10_pred_minus_actual": float(y_pred - row["log10_J"]),
                "actual_J": float(row["J"]),
                "predicted_J": float(10**y_pred),
                "within_2x": bool(abs(y_pred - row["log10_J"]) <= LOG10_2),
            }
        )
    ridge = model.named_steps["ridge"]
    scaler = model.named_steps["scaler"]
    return {
        "direction": name,
        "model": "StandardScaler(train only) + Ridge(alpha=1.0)",
        "feature_set": FEATURES,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "train_dataset": sorted(train["dataset"].unique().tolist()),
        "test_dataset": sorted(test["dataset"].unique().tolist()),
        "metrics": metrics,
        "model_parameters": {
            "ridge_alpha": 1.0,
            "ridge_intercept": float(ridge.intercept_),
            "ridge_coefficients_scaled_feature_space": {name: float(value) for name, value in zip(FEATURES, ridge.coef_)},
            "scaler_mean": {name: float(value) for name, value in zip(FEATURES, scaler.mean_)},
            "scaler_scale": {name: float(value) for name, value in zip(FEATURES, scaler.scale_)},
        },
        "predictions": predictions,
    }


def xiao_internal_grouped_loocv(xiao: pd.DataFrame) -> dict:
    key_cols = ["poloxamer407", "ethanol", "pg", "mct_xiao", "water_xiao", "api_pct_ww"]
    groups = []
    for _, group in xiao.groupby(key_cols, dropna=False, sort=False):
        groups.append(group.index.to_list())
    preds = np.full(len(xiao), np.nan)
    fold_details = []
    for fold_id, test_idx in enumerate(groups, start=1):
        train_idx = [idx for idx in xiao.index if idx not in test_idx]
        train = xiao.loc[train_idx]
        test = xiao.loc[test_idx]
        pred, _ = train_predict(train, test)
        preds[[xiao.index.get_loc(idx) for idx in test_idx]] = pred
        fold_details.append(
            {
                "fold_id": fold_id,
                "test_record_ids": test["record_id"].tolist(),
                "test_size": int(len(test)),
                "duplicate_guarded": bool(len(test) > 1),
            }
        )
    y = xiao["log10_J"].to_numpy()
    duplicate_groups = []
    for test_idx in groups:
        if len(test_idx) > 1:
            group = xiao.loc[test_idx]
            duplicate_groups.append(
                {
                    "record_ids": group["record_id"].tolist(),
                    "J_values": group["J"].astype(float).tolist(),
                    "composition": {col: float(group.iloc[0][col]) for col in key_cols},
                }
            )
    metrics = compute_metrics(y, preds, float(xiao["log10_J"].mean()))
    metrics["RMSE_cv"] = metrics["rmse_logJ"]
    metrics["R2_cv"] = metrics["R2_conv"]
    predictions = []
    for (_, row), y_pred in zip(xiao.iterrows(), preds):
        predictions.append(
            {
                "record_id": row["record_id"],
                "actual_log10_J": float(row["log10_J"]),
                "predicted_log10_J": float(y_pred),
                "residual_log10_pred_minus_actual": float(y_pred - row["log10_J"]),
                "actual_J": float(row["J"]),
                "predicted_J": float(10**y_pred),
                "within_2x": bool(abs(y_pred - row["log10_J"]) <= LOG10_2),
            }
        )
    return {
        "name": "Xiao internal leakage-guarded LOOCV",
        "model": "StandardScaler(train only) + Ridge(alpha=1.0)",
        "feature_set": FEATURES,
        "n_records": int(len(xiao)),
        "n_folds": int(len(groups)),
        "duplicate_policy": "Identical Xiao composition rows are held out as one fold, preventing identical composition with different J in train and test.",
        "duplicate_groups": duplicate_groups,
        "metrics": metrics,
        "fold_details": fold_details,
        "predictions": predictions,
    }


def protocol_distance() -> dict:
    eda_score = abs(math.log10(2.01 / 0.785))
    duration_score = abs(math.log10(30.0 / 24.0))
    dimensions = [
        {
            "dimension": "membrane",
            "xiao": "Strat-M",
            "bolla": "Strat-M",
            "score": 0.0,
            "rule": "0 because membrane is identical.",
        },
        {
            "dimension": "diffusion_cell",
            "xiao": "Franz static cell",
            "bolla": "PermeGear flow-through cell",
            "score": 1.0,
            "rule": "1 because diffusion-cell class differs.",
        },
        {
            "dimension": "receptor_medium",
            "xiao": "PBS pH 7.4",
            "bolla": "10% v/v ethanol",
            "score": 0.85,
            "rule": "High score for different sink chemistry and ethanol cosolvent.",
        },
        {
            "dimension": "dose_mode",
            "xiao": "approximately 300 mg finite",
            "bolla": "approximately 10 mg finite",
            "score": 0.50,
            "rule": "Both are finite dose, but donor mass differs by about 30x; assigned moderate distance.",
        },
        {
            "dimension": "EDA",
            "xiao": "2.01 cm2",
            "bolla": "0.785 cm2",
            "score": eda_score,
            "rule": "abs(log10(area ratio)); 10x difference would score 1.",
        },
        {
            "dimension": "duration",
            "xiao": "30 h",
            "bolla": "24 h",
            "score": duration_score,
            "rule": "abs(log10(duration ratio)); 10x difference would score 1.",
        },
        {
            "dimension": "composition_paradigm",
            "xiao": "continuous P407/EtOH/PG/MCT hydrogel design",
            "bolla": "categorical semisolid creams/gels with mostly non-overlapping excipients",
            "score": 1.0,
            "rule": "1 because raw composition spaces have essentially no direct overlap.",
        },
        {
            "dimension": "API",
            "xiao": "ibuprofen free acid 5% w/w",
            "bolla": "ibuprofen free acid 3-5% w/w",
            "score": 0.10,
            "rule": "Low score because API and basis match; concentration range differs modestly.",
        },
    ]
    scalar = float(np.mean([row["score"] for row in dimensions]))
    return {
        "description": "Interpretable 0-1 protocol-distance descriptor, not a calibrated physical metric.",
        "dimensions": dimensions,
        "scalar_mean": scalar,
    }


def make_feature_table(xiao: pd.DataFrame, bolla: pd.DataFrame) -> pd.DataFrame:
    component_cols = [
        "poloxamer407",
        "ethanol",
        "pg",
        "mct_xiao",
        "water_xiao",
        "ibuprofen",
        "propylene_glycol",
        "oleyl_alcohol",
        "isopropyl_myristate",
        "transcutol",
        "mineral_oil",
        "white_petrolatum",
        "peg400",
        "mct",
        "glycerol",
        "span20",
        "polysorbate80",
        "kolliphor_cs20",
        "glycerol_monostearate",
        "cetyl_alcohol",
        "stearyl_alcohol",
        "cetostearyl_alcohol",
        "sepineo_se68",
        "sepineo_p600",
        "tefose63",
        "hpmc",
        "carbopol974",
        "hpc",
        "water",
    ]
    for col in component_cols:
        if col not in xiao.columns:
            xiao[col] = 0.0
        if col not in bolla.columns:
            bolla[col] = 0.0
    base_cols = [
        "dataset",
        "record_id",
        "formulation_label",
        "subset",
        "api_pct_ww",
        "J",
        "J_sd",
        "log10_J",
        "protocol_cell",
        "membrane",
        "receptor_medium",
        "eda_cm2",
        "duration_h",
        "solubilising_components",
        "solubilising_weight_pct",
        *FEATURES,
        *component_cols,
    ]
    return pd.concat([xiao[base_cols], bolla[base_cols]], ignore_index=True)


def fmt(value: float, digits: int = 3) -> str:
    if value is None or math.isnan(float(value)):
        return "nan"
    return f"{float(value):.{digits}f}"


def make_figure(xiao_to_bolla: dict, bolla_to_xiao: dict, xiao_cv: dict, distance: dict) -> None:
    predictions = xiao_to_bolla["predictions"]
    actual = np.array([row["actual_log10_J"] for row in predictions])
    pred = np.array([row["predicted_log10_J"] for row in predictions])
    labels = [row["formulation_label"] for row in predictions]
    metrics = xiao_to_bolla["metrics"]
    scalar = distance["scalar_mean"]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    lo = min(actual.min(), pred.min()) - 0.08
    hi = max(actual.max(), pred.max()) + 0.08
    grid = np.linspace(lo, hi, 100)
    ax.fill_between(grid, grid - LOG10_2, grid + LOG10_2, color="#d6e4f0", alpha=0.75, label="2-fold band")
    ax.plot(grid, grid, color="#222222", linewidth=1.2, label="1:1")
    ax.scatter(actual, pred, s=46, color="#2f6f9f", edgecolor="white", linewidth=0.7, zorder=3)
    for x, y, label in zip(actual, pred, labels):
        ax.annotate(label, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Actual log10 J")
    ax.set_ylabel("Predicted log10 J")
    ax.set_title("Xiao -> Bolla zero-shot")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.grid(True, linewidth=0.4, color="#d9d9d9")
    text = (
        f"distance={scalar:.2f}\n"
        f"rho={metrics['spearman_rho']:.2f}\n"
        f"R2_conv={metrics['R2_conv']:.2f}\n"
        f"within-2x={metrics['within_2x_count']}/{metrics['n']}"
    )
    ax.text(0.03, 0.97, text, transform=ax.transAxes, va="top", ha="left", fontsize=8.5, bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": "#bbbbbb"})

    ax2 = axes[1]
    points = [
        (0.0, xiao_cv["metrics"]["R2_conv"], "Xiao internal"),
        (scalar, xiao_to_bolla["metrics"]["R2_conv"], "Xiao->Bolla"),
        (scalar, bolla_to_xiao["metrics"]["R2_conv"], "Bolla->Xiao"),
    ]
    colors = ["#4c956c", "#2f6f9f", "#b75d69"]
    for (x, y, label), color in zip(points, colors):
        ax2.scatter([x], [y], s=58, color=color, edgecolor="white", linewidth=0.7, zorder=3)
        ax2.annotate(label, (x, y), xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax2.axhline(0, color="#666666", linewidth=0.8)
    ax2.set_xlabel("Protocol distance scalar")
    ax2.set_ylabel("R2_conv")
    ax2.set_title("Distance vs transfer quality")
    ax2.set_xlim(-0.04, min(1.0, scalar + 0.18))
    ys = [p[1] for p in points if not math.isnan(p[1])]
    ax2.set_ylim(min(ys) - 0.3, max(ys) + 0.3)
    ax2.grid(True, linewidth=0.4, color="#d9d9d9")
    fig.tight_layout()
    fig.savefig(OUT / "figure_demo2_main.png", dpi=300)
    fig.savefig(OUT / "figure_demo2_main.pdf")
    plt.close(fig)


def report_text(feature_table: pd.DataFrame, distance: dict, x2b: dict, b2x: dict, xcv: dict) -> str:
    xiao = feature_table[feature_table["dataset"] == "Xiao"]
    bolla = feature_table[feature_table["dataset"] == "Bolla"]
    xiao_log_span = float(xiao["log10_J"].max() - xiao["log10_J"].min())
    bolla_log_span = float(bolla["log10_J"].max() - bolla["log10_J"].min())
    xiao_mean_rmse = float(math.sqrt(mean_squared_error(xiao["log10_J"], np.repeat(xiao["log10_J"].mean(), len(xiao)))))

    assignments = {
        "Xiao solubilising": "ethanol, PG, water",
        "Xiao excluded": "poloxamer407 and MCT treated as approximately non-solubilising for the feature bridge",
        "Bolla solubilising": "transcutol, propylene_glycol, isopropyl_myristate, oleyl_alcohol, mct, mineral_oil, peg400, glycerol, polysorbate80, water, ethanol",
        "Bolla excluded": ", ".join(sorted(BOLLA_STRUCTURAL_EXCLUDED)),
        "Unit assumption": "Bolla mg/g solubility values are used as approximate mg/mL under density approximately 1 g/mL.",
    }

    def metric_line(result: dict) -> str:
        m = result["metrics"]
        return (
            f"Spearman rho={fmt(m['spearman_rho'])}, RMSE_logJ={fmt(m['rmse_logJ'])}, "
            f"within-2x={m['within_2x_count']}/{m['n']} ({fmt(m['within_2x'])}), "
            f"R2_conv={fmt(m['R2_conv'])}, R2_gen_train_mean={fmt(m['R2_gen_train_mean_baseline'])}, "
            f"Pearson r={fmt(m['pearson_r'])}"
        )

    lines = [
        "# Demo 2 Step 2 Modelling Report",
        "",
        "## 1. Data Provenance",
        "",
        "Bolla endpoint records come from real SkinMiner extraction in `outputs/phase2_demo2_audit/bolla_extracted_records_real.csv`: Table 7 was routed to the table extractor and recovered 8/8 flux records. Bolla composition and solubility come from `bolla_composition_real.csv` and `bolla_solubility_real.csv`; composition was generated by deterministic parsing of the real PDF table text after the endpoint-oriented generic table prompt proved unsuitable for the wide composition matrix.",
        "",
        "Xiao 2025 is hardcoded in this standalone modelling script as in-house ground truth: 15 BBD, 10 LHS, and 4 RUN records, all with supplied steady-state flux J and J_sd.",
        "",
        "## 2. Transparent Override",
        "",
        "The Bolla endpoint records were extraction-verified against Table 7 but rejected by the v4 Franz-only verifier as `not_target_device` because Bolla uses flow-through cells. They are used here by explicit researcher decision for cross-protocol transfer modelling. The device mismatch is treated as a protocol-distance dimension, not hidden.",
        "",
        "## 3. Feature Construction",
        "",
        "Features are restricted to the 3-feature solubility-anchored bridge: `log10_vehicle_solubility`, `ethanol_fraction`, and `drug_state_solubilized`.",
        "",
        "Yalkowsky-style log-linear mixture solubility was computed as `log10(S_mix) = sum(w_i_normalised * log10(S_i))` over solubilising components only. Weights are renormalised over solubilising components after excluding structural, wax, and polymer components.",
        "",
        "Solubilising assignments:",
    ]
    for key, value in assignments.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "Xiao drug state is encoded conservatively as `drug_state_solubilized=0` for all records, reflecting a coarse assumption from the prompt. Bolla drug state uses the extracted composition table column: F2A, F2B, and F6 are solubilized; all other Bolla formulations are suspended.",
            "",
            "For Xiao RUN rows, water is computed as the excipient balance to 95% after P407, ethanol, PG, and MCT, because ibuprofen is fixed at 5% w/w. BBD/LHS water values are used as supplied.",
            "",
            f"Feature table rows: Xiao={len(xiao)}, Bolla={len(bolla)}, total={len(feature_table)}.",
            "",
            "## 4. Protocol Distance",
            "",
            f"Scalar mean protocol distance = {distance['scalar_mean']:.3f}. This is an interpretable descriptor, not a calibrated physical metric.",
            "",
            "| Dimension | Xiao | Bolla | Score | Rule |",
            "|---|---|---|---:|---|",
        ]
    )
    for row in distance["dimensions"]:
        lines.append(f"| {row['dimension']} | {row['xiao']} | {row['bolla']} | {row['score']:.3f} | {row['rule']} |")
    lines.extend(
        [
            "",
            "## 5. Zero-Shot Transfer",
            "",
            "R2_conv is the primary R2 everywhere. R2_gen_train_mean is reported only as a secondary train-mean-baseline variant.",
            "",
            f"Xiao -> Bolla: {metric_line(x2b)}.",
            "",
            f"Bolla -> Xiao: {metric_line(b2x)}.",
            "",
            f"The directions are asymmetric. Xiao J spans {xiao['J'].min():.2f}-{xiao['J'].max():.2f} (log10 span={xiao_log_span:.3f}); predicting the Xiao mean alone gives RMSE_logJ={xiao_mean_rmse:.3f}. Bolla J spans {bolla['J'].min():.2f}-{bolla['J'].max():.2f} (log10 span={bolla_log_span:.3f}). Therefore Bolla -> Xiao RMSE/within-2x can look modest even when R2_conv and rank correlation show poor transfer. Xiao -> Bolla is more informative because Bolla spans a much wider flux range.",
            "",
            "## 6. Xiao-Internal LOOCV Reference",
            "",
            f"Leakage-guarded Xiao internal CV: RMSE_cv={fmt(xcv['metrics']['RMSE_cv'])}, R2_cv={fmt(xcv['metrics']['R2_cv'])}, Spearman rho={fmt(xcv['metrics']['spearman_rho'])}, within-2x={xcv['metrics']['within_2x_count']}/{xcv['metrics']['n']}.",
            "",
            "Xiao's published full-composition RSM/BO LOOCV R2 values were 0.42/0.84; this 3-feature solubility-anchored CV is expected to differ and is reported as computed.",
            "",
            "Duplicate center-point compositions were detected and grouped into a single held-out fold, so identical compositions with different J values do not appear in both train and test in any fold.",
            "",
            "## 7. Few-Shot",
            "",
            "Few-shot modelling was not run. This keeps the report focused on the required zero-shot transfer diagnosis and avoids presenting narrow-range Xiao RMSE reductions as optimisation-ready transfer.",
            "",
            "## 8. Distance-Quality Interpretation",
            "",
            "The high Xiao-Bolla protocol distance corresponds to weak or negative zero-shot transfer under the agreed 3-feature bridge. The low-distance Xiao-internal reference is also limited by the deliberately compressed feature set, but it is still the relevant within-protocol anchor. The result is a transfer-readiness warning rather than a transfer-success demonstration.",
            "",
            "## 9. Demo-1 Comparison",
            "",
            "| Experiment | Feature paradigm | Direction | Spearman rho | RMSE_logJ | within-2x | R2_conv | R2_gen |",
            "|---|---|---|---:|---:|---:|---:|---:|",
            "| Demo 1 section 3.5.1 | composition_plus_solubility | reported transfer | 0.706 | 0.199 | 9/12 | not reported | 0.70 |",
            f"| Demo 2 | 3-feature solubility bridge | Xiao -> Bolla | {x2b['metrics']['spearman_rho']:.3f} | {x2b['metrics']['rmse_logJ']:.3f} | {x2b['metrics']['within_2x_count']}/{x2b['metrics']['n']} | {x2b['metrics']['R2_conv']:.3f} | {x2b['metrics']['R2_gen_train_mean_baseline']:.3f} |",
            f"| Demo 2 | 3-feature solubility bridge | Bolla -> Xiao | {b2x['metrics']['spearman_rho']:.3f} | {b2x['metrics']['rmse_logJ']:.3f} | {b2x['metrics']['within_2x_count']}/{b2x['metrics']['n']} | {b2x['metrics']['R2_conv']:.3f} | {b2x['metrics']['R2_gen_train_mean_baseline']:.3f} |",
            "",
            "Demo 2 is not directly comparable in level because it uses a different feature paradigm: a 3-feature solubility-anchored bridge rather than demo-1's richer composition_plus_solubility representation. The comparison is methodological: both demos report transfer with explicit feature constraints and labelled R2 baselines.",
            "",
            "## Output Files",
            "",
            "- `feature_table.csv`",
            "- `protocol_distance.json`",
            "- `transfer_xiao_to_bolla.json`",
            "- `transfer_bolla_to_xiao.json`",
            "- `xiao_internal_loocv.json`",
            "- `figure_demo2_main.pdf` and `figure_demo2_main.png`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    np.random.seed(RANDOM_STATE)
    xiao = build_xiao()
    bolla = build_bolla()
    feature_table = make_feature_table(xiao.copy(), bolla.copy())
    feature_table.to_csv(OUT / "feature_table.csv", index=False)

    distance = protocol_distance()
    write_json(OUT / "protocol_distance.json", distance)

    x2b = transfer_result("Xiao_to_Bolla_zero_shot", xiao, bolla)
    b2x = transfer_result("Bolla_to_Xiao_zero_shot", bolla, xiao)
    xcv = xiao_internal_grouped_loocv(xiao)
    write_json(OUT / "transfer_xiao_to_bolla.json", x2b)
    write_json(OUT / "transfer_bolla_to_xiao.json", b2x)
    write_json(OUT / "xiao_internal_loocv.json", xcv)

    make_figure(x2b, b2x, xcv, distance)
    (OUT / "demo2_modelling_report.md").write_text(report_text(feature_table, distance, x2b, b2x, xcv), encoding="utf-8")

    print("[DEMO2 MODELLING] Done")
    print(f"Xiao -> Bolla: {x2b['metrics']}")
    print(f"Bolla -> Xiao: {b2x['metrics']}")
    print(f"Xiao internal CV: {xcv['metrics']}")
    print(f"Protocol distance scalar: {distance['scalar_mean']:.3f}")


if __name__ == "__main__":
    main()
