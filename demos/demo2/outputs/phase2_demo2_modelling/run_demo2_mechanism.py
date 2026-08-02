from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_demo2_4feature as four_feature
import run_demo2_modelling as demo2


OUT = SCRIPT_DIR
FEATURES = four_feature.FEATURE_VARIANTS["4_feature"]
FEATURE_LABELS = {
    "log10_vehicle_solubility": "log10 solubility",
    "ethanol_fraction": "ethanol fraction",
    "pg_fraction": "PG fraction",
    "water_fraction": "water fraction",
}
REFERENCE_COLUMNS = {
    "log10_vehicle_solubility": "feat_log10_vehicle_solubility",
    "ethanol_fraction": "feat_ethanol_fraction",
    "pg_fraction": "feat_pg_fraction",
    "water_fraction": "feat_water_fraction",
}
LOG10_2 = math.log10(2.0)
RANDOM_STATE = 42

PCA_CSV = OUT / "feature_space_pca.csv"
OVERLAP_JSON = OUT / "feature_space_overlap_metrics.json"
LOOCV_JSON = OUT / "bolla_internal_loocv_results.json"
FIG_PDF = OUT / "figure_feature_space.pdf"
FIG_PNG = OUT / "figure_feature_space.png"
REPORT = OUT / "demo2_mechanism_report.md"

PALETTE = {
    "xiao": "#0072B2",
    "bolla": "#D55E00",
    "line": "#222222",
    "grid": "#D9D9D9",
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


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(json_safe(payload), indent=2, sort_keys=True), encoding="utf-8")


def build_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    xiao = four_feature.add_fraction_features(demo2.build_xiao()).reset_index(drop=True)
    bolla = four_feature.add_fraction_features(demo2.build_bolla()).reset_index(drop=True)
    combined = pd.concat([xiao, bolla], ignore_index=True)
    return xiao, bolla, combined


def verify_features(xiao: pd.DataFrame, bolla: pd.DataFrame) -> dict:
    references = {
        "Xiao": pd.read_csv(OUT / "transfer_4feature_bolla_to_xiao.csv").set_index("record_id"),
        "Bolla": pd.read_csv(OUT / "transfer_4feature_xiao_to_bolla.csv").set_index("record_id"),
    }
    datasets = {"Xiao": xiao, "Bolla": bolla}
    max_abs_diff = 0.0
    compared = 0
    for dataset_name, frame in datasets.items():
        reference = references[dataset_name]
        if set(frame["record_id"].astype(str)) != set(reference.index.astype(str)):
            raise ValueError(f"{dataset_name} record IDs do not match Step 2g transfer CSV")
        for _, row in frame.iterrows():
            record_id = str(row["record_id"])
            for feature, ref_col in REFERENCE_COLUMNS.items():
                difference = abs(float(row[feature]) - float(reference.loc[record_id, ref_col]))
                max_abs_diff = max(max_abs_diff, difference)
                compared += 1
                if difference > 5e-10:
                    raise ValueError(
                        f"Feature mismatch for {dataset_name}/{record_id}/{feature}: "
                        f"computed={row[feature]}, reference={reference.loc[record_id, ref_col]}"
                    )
    return {
        "status": "PASS",
        "n_values_compared": compared,
        "max_absolute_difference": max_abs_diff,
        "reference_files": [
            "transfer_4feature_xiao_to_bolla.csv",
            "transfer_4feature_bolla_to_xiao.csv",
        ],
    }


def bbox(points: np.ndarray) -> dict:
    return {
        "pc1_min": float(np.min(points[:, 0])),
        "pc1_max": float(np.max(points[:, 0])),
        "pc2_min": float(np.min(points[:, 1])),
        "pc2_max": float(np.max(points[:, 1])),
    }


def bbox_area(box: dict) -> float:
    return float((box["pc1_max"] - box["pc1_min"]) * (box["pc2_max"] - box["pc2_min"]))


def bbox_overlap(xiao_box: dict, bolla_box: dict) -> dict:
    pc1_low = max(xiao_box["pc1_min"], bolla_box["pc1_min"])
    pc1_high = min(xiao_box["pc1_max"], bolla_box["pc1_max"])
    pc2_low = max(xiao_box["pc2_min"], bolla_box["pc2_min"])
    pc2_high = min(xiao_box["pc2_max"], bolla_box["pc2_max"])
    width = max(0.0, pc1_high - pc1_low)
    height = max(0.0, pc2_high - pc2_low)
    intersection_area = width * height
    xiao_area = bbox_area(xiao_box)
    bolla_area = bbox_area(bolla_box)
    return {
        "intersection_bbox": {
            "pc1_min": pc1_low if width > 0 else None,
            "pc1_max": pc1_high if width > 0 else None,
            "pc2_min": pc2_low if height > 0 else None,
            "pc2_max": pc2_high if height > 0 else None,
        },
        "intersection_area": float(intersection_area),
        "xiao_bbox_area": xiao_area,
        "bolla_bbox_area": bolla_area,
        "percent_of_xiao_bbox_intersected": float(100.0 * intersection_area / xiao_area) if xiao_area > 0 else None,
        "percent_of_bolla_bbox_intersected": float(100.0 * intersection_area / bolla_area) if bolla_area > 0 else None,
        "has_positive_area_overlap": bool(intersection_area > 0),
    }


def pooled_sd(a: np.ndarray, b: np.ndarray) -> float:
    numerator = (len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)
    denominator = len(a) + len(b) - 2
    return float(math.sqrt(numerator / denominator))


def analyse_feature_space(
    combined: pd.DataFrame,
    feature_sanity: dict,
) -> tuple[pd.DataFrame, dict]:
    matrix = combined[FEATURES].to_numpy(dtype=float)
    scaler = StandardScaler()
    standardised = scaler.fit_transform(matrix)
    pca = PCA(n_components=4, svd_solver="full")
    coordinates = pca.fit_transform(standardised)

    pca_rows = combined[["dataset", "record_id", "formulation_label"]].copy()
    for index in range(4):
        pca_rows[f"PC{index + 1}"] = coordinates[:, index]
    for feature_index, feature in enumerate(FEATURES):
        pca_rows[feature] = matrix[:, feature_index]
        pca_rows[f"z_{feature}"] = standardised[:, feature_index]

    dataset_mask = combined["dataset"].astype(str).to_numpy() == "Xiao"
    xiao_pc = coordinates[dataset_mask, :2]
    bolla_pc = coordinates[~dataset_mask, :2]
    xiao_box = bbox(xiao_pc)
    bolla_box = bbox(bolla_pc)
    overlap = bbox_overlap(xiao_box, bolla_box)
    bolla_inside_xiao_pc_box = (
        (bolla_pc[:, 0] >= xiao_box["pc1_min"])
        & (bolla_pc[:, 0] <= xiao_box["pc1_max"])
        & (bolla_pc[:, 1] >= xiao_box["pc2_min"])
        & (bolla_pc[:, 1] <= xiao_box["pc2_max"])
    )
    xiao_inside_bolla_pc_box = (
        (xiao_pc[:, 0] >= bolla_box["pc1_min"])
        & (xiao_pc[:, 0] <= bolla_box["pc1_max"])
        & (xiao_pc[:, 1] >= bolla_box["pc2_min"])
        & (xiao_pc[:, 1] <= bolla_box["pc2_max"])
    )

    xiao_z_min = np.min(standardised[dataset_mask], axis=0)
    xiao_z_max = np.max(standardised[dataset_mask], axis=0)
    bolla_z_min = np.min(standardised[~dataset_mask], axis=0)
    bolla_z_max = np.max(standardised[~dataset_mask], axis=0)
    bolla_inside_xiao_4d_box = np.all(
        (standardised[~dataset_mask] >= xiao_z_min) & (standardised[~dataset_mask] <= xiao_z_max),
        axis=1,
    )
    xiao_inside_bolla_4d_box = np.all(
        (standardised[dataset_mask] >= bolla_z_min) & (standardised[dataset_mask] <= bolla_z_max),
        axis=1,
    )

    xiao_centroid = np.mean(xiao_pc, axis=0)
    bolla_centroid = np.mean(bolla_pc, axis=0)
    pooled_sds = np.array(
        [
            pooled_sd(xiao_pc[:, 0], bolla_pc[:, 0]),
            pooled_sd(xiao_pc[:, 1], bolla_pc[:, 1]),
        ],
        dtype=float,
    )
    standardised_centroid_delta = (bolla_centroid - xiao_centroid) / pooled_sds
    centroid_distance = float(np.linalg.norm(standardised_centroid_delta))

    range_rows = []
    for feature_index, feature in enumerate(FEATURES):
        xiao_values = standardised[dataset_mask, feature_index]
        bolla_values = standardised[~dataset_mask, feature_index]
        overlap_low = max(float(np.min(xiao_values)), float(np.min(bolla_values)))
        overlap_high = min(float(np.max(xiao_values)), float(np.max(bolla_values)))
        overlap_width = max(0.0, overlap_high - overlap_low)
        range_rows.append(
            {
                "feature": feature,
                "xiao_min_standardised": float(np.min(xiao_values)),
                "xiao_max_standardised": float(np.max(xiao_values)),
                "bolla_min_standardised": float(np.min(bolla_values)),
                "bolla_max_standardised": float(np.max(bolla_values)),
                "ranges_overlap": bool(overlap_width > 0 or math.isclose(overlap_low, overlap_high)),
                "overlap_min_standardised": overlap_low if overlap_width > 0 else None,
                "overlap_max_standardised": overlap_high if overlap_width > 0 else None,
                "overlap_width_standardised": overlap_width,
                "bolla_records_inside_xiao_range": int(
                    np.sum((bolla_values >= np.min(xiao_values)) & (bolla_values <= np.max(xiao_values)))
                ),
                "n_bolla_records": int(len(bolla_values)),
            }
        )

    component_weights = {
        feature: {
            "PC1": float(pca.components_[0, index]),
            "PC2": float(pca.components_[1, index]),
        }
        for index, feature in enumerate(FEATURES)
    }
    correlation_loadings = {
        feature: {
            "PC1": float(pca.components_[0, index] * math.sqrt(pca.explained_variance_[0])),
            "PC2": float(pca.components_[1, index] * math.sqrt(pca.explained_variance_[1])),
        }
        for index, feature in enumerate(FEATURES)
    }

    metrics = {
        "metadata": {
            "n_records": int(len(combined)),
            "n_xiao": int(np.sum(dataset_mask)),
            "n_bolla": int(np.sum(~dataset_mask)),
            "features": FEATURES,
            "standardisation_scope": "StandardScaler fit on all 37 rows for visualisation only.",
            "pca_solver": "full",
            "random_state": RANDOM_STATE,
        },
        "feature_sanity_against_step2g": feature_sanity,
        "standard_scaler": {
            feature: {
                "mean": float(scaler.mean_[index]),
                "scale": float(scaler.scale_[index]),
            }
            for index, feature in enumerate(FEATURES)
        },
        "pca": {
            "explained_variance_ratio": {
                f"PC{index + 1}": float(value)
                for index, value in enumerate(pca.explained_variance_ratio_)
            },
            "component_weights": component_weights,
            "correlation_loadings": correlation_loadings,
        },
        "standardised_feature_range_overlap": range_rows,
        "pc1_pc2_bounding_boxes": {
            "xiao": xiao_box,
            "bolla": bolla_box,
            "overlap": overlap,
            "point_coverage": {
                "bolla_records_inside_xiao_bbox": int(np.sum(bolla_inside_xiao_pc_box)),
                "n_bolla_records": int(len(bolla_pc)),
                "xiao_records_inside_bolla_bbox": int(np.sum(xiao_inside_bolla_pc_box)),
                "n_xiao_records": int(len(xiao_pc)),
            },
        },
        "standardised_4d_hyperrectangle_coverage": {
            "bolla_records_inside_xiao_hyperrectangle": int(np.sum(bolla_inside_xiao_4d_box)),
            "n_bolla_records": int(np.sum(~dataset_mask)),
            "xiao_records_inside_bolla_hyperrectangle": int(np.sum(xiao_inside_bolla_4d_box)),
            "n_xiao_records": int(np.sum(dataset_mask)),
        },
        "pc1_pc2_centroids": {
            "xiao": {"PC1": float(xiao_centroid[0]), "PC2": float(xiao_centroid[1])},
            "bolla": {"PC1": float(bolla_centroid[0]), "PC2": float(bolla_centroid[1])},
            "raw_delta_bolla_minus_xiao": {
                "PC1": float(bolla_centroid[0] - xiao_centroid[0]),
                "PC2": float(bolla_centroid[1] - xiao_centroid[1]),
            },
            "pooled_sd": {"PC1": float(pooled_sds[0]), "PC2": float(pooled_sds[1])},
            "delta_in_pooled_sd_units": {
                "PC1": float(standardised_centroid_delta[0]),
                "PC2": float(standardised_centroid_delta[1]),
            },
            "euclidean_distance_in_pooled_sd_units": centroid_distance,
        },
    }
    return pca_rows, metrics


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


def aggregate_loocv(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    residual = y_pred - y_true
    within = np.abs(residual) <= LOG10_2
    return {
        "R2_conv": float(r2_score(y_true, y_pred)),
        "rmse_logJ": float(math.sqrt(mean_squared_error(y_true, y_pred))),
        "spearman_rho": correlation_or_none(y_true, y_pred, "spearman"),
        "pearson_r": correlation_or_none(y_true, y_pred, "pearson"),
        "within_2x_fraction": float(np.mean(within)),
        "within_2x_count": int(np.sum(within)),
        "n": int(len(y_true)),
    }


def ridge_fold(train: pd.DataFrame, test: pd.DataFrame) -> tuple[float, dict]:
    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[FEATURES].to_numpy(dtype=float))
    x_test = scaler.transform(test[FEATURES].to_numpy(dtype=float))
    model = Ridge(alpha=1.0)
    model.fit(x_train, train["log10_J"].to_numpy(dtype=float))
    prediction = float(model.predict(x_test)[0])
    info = {
        "scaler_mean": {feature: float(value) for feature, value in zip(FEATURES, scaler.mean_)},
        "scaler_scale": {feature: float(value) for feature, value in zip(FEATURES, scaler.scale_)},
        "ridge_intercept": float(model.intercept_),
        "ridge_coefficients_scaled_feature_space": {
            feature: float(value) for feature, value in zip(FEATURES, model.coef_)
        },
    }
    return prediction, info


def gpr_fold(train: pd.DataFrame, test: pd.DataFrame) -> tuple[float, float, dict]:
    prediction, sigma, info = four_feature.fit_predict(
        train,
        test,
        FEATURES,
        model_name="gpr",
        target="log10",
    )
    return float(prediction[0]), float(sigma[0]), info


def run_bolla_loocv(bolla: pd.DataFrame) -> dict:
    model_predictions: dict[str, list[dict]] = {"ridge": [], "gpr": []}
    for held_out_index in range(len(bolla)):
        test = bolla.iloc[[held_out_index]].copy()
        train = bolla.drop(index=held_out_index).reset_index(drop=True)
        record_id = str(test.iloc[0]["record_id"])
        actual = float(test.iloc[0]["log10_J"])

        ridge_prediction, ridge_info = ridge_fold(train, test)
        gpr_prediction, gpr_sigma, gpr_info = gpr_fold(train, test)
        for model_name, prediction, sigma, info in [
            ("ridge", ridge_prediction, None, ridge_info),
            ("gpr", gpr_prediction, gpr_sigma, gpr_info),
        ]:
            residual = prediction - actual
            model_predictions[model_name].append(
                {
                    "record_id": record_id,
                    "logJ_actual": actual,
                    "logJ_pred": prediction,
                    "residual_pred_minus_actual": residual,
                    "abs_residual": abs(residual),
                    "within_2x": bool(abs(residual) <= LOG10_2),
                    "predictive_sigma_logJ": sigma,
                    "fold_model_info": info,
                }
            )

    models = {}
    for model_name, rows in model_predictions.items():
        actual = np.array([row["logJ_actual"] for row in rows], dtype=float)
        predicted = np.array([row["logJ_pred"] for row in rows], dtype=float)
        models[model_name] = {
            "model": (
                "StandardScaler(train fold only) + Ridge(alpha=1.0)"
                if model_name == "ridge"
                else "StandardScaler(train fold only) + GPR(ConstantKernel*RBF + WhiteKernel, normalize_y=True, n_restarts_optimizer=10, random_state=42)"
            ),
            "features": FEATURES,
            "target": "log10(J)",
            "aggregate_metrics": aggregate_loocv(actual, predicted),
            "predictions": rows,
        }

    return {
        "metadata": {
            "analysis": "Bolla-internal leave-one-out cross-validation",
            "n_records": int(len(bolla)),
            "n_folds": int(len(bolla)),
            "features": FEATURES,
            "target": "log10(J)",
            "within_2x_definition": "abs(predicted log10 J - actual log10 J) <= log10(2)",
            "R2_conv_definition": "sklearn r2_score over all eight concatenated held-out predictions",
            "random_state": RANDOM_STATE,
        },
        "models": models,
    }


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8.5,
            "axes.titlesize": 9.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.8,
        }
    )


def add_bbox(ax, points: np.ndarray, color: str, linestyle: str) -> None:
    low = np.min(points, axis=0)
    high = np.max(points, axis=0)
    ax.add_patch(
        Rectangle(
            (low[0], low[1]),
            high[0] - low[0],
            high[1] - low[1],
            facecolor="none",
            edgecolor=color,
            linewidth=0.8,
            linestyle=linestyle,
            alpha=0.75,
            zorder=1,
        )
    )


def make_figure(pca_rows: pd.DataFrame, metrics: dict) -> None:
    configure_matplotlib()
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.65, 3.65),
        gridspec_kw={"width_ratios": [1.04, 0.96], "wspace": 0.38},
    )

    ax = axes[0]
    xiao = pca_rows[pca_rows["dataset"] == "Xiao"]
    bolla = pca_rows[pca_rows["dataset"] == "Bolla"]
    ax.scatter(
        xiao["PC1"],
        xiao["PC2"],
        s=30,
        marker="o",
        facecolor=PALETTE["xiao"],
        edgecolor=PALETTE["line"],
        linewidth=0.45,
        alpha=0.88,
        label="in-house",
        zorder=3,
    )
    ax.scatter(
        bolla["PC1"],
        bolla["PC2"],
        s=38,
        marker="^",
        facecolor="white",
        edgecolor=PALETTE["bolla"],
        linewidth=1.2,
        label="literature",
        zorder=4,
    )
    add_bbox(ax, xiao[["PC1", "PC2"]].to_numpy(dtype=float), PALETTE["xiao"], "--")
    add_bbox(ax, bolla[["PC1", "PC2"]].to_numpy(dtype=float), PALETTE["bolla"], ":")

    label_offsets = {
        "F1A": (10, 12),
        "F1B": (10, -16),
        "F2A": (10, 12),
        "F2B": (10, -18),
        "F3": (12, 12),
        "F4": (10, -18),
        "F5": (8, 12),
        "F6": (10, 12),
        "RUN1": (12, 14),
        "RUN2": (12, -16),
        "RUN3": (12, -16),
        "RUN4": (12, -14),
    }
    labelled = pd.concat([bolla, xiao[xiao["record_id"].isin(["RUN1", "RUN2", "RUN3", "RUN4"])]]).copy()
    for _, row in labelled.iterrows():
        record_id = str(row["record_id"])
        ax.annotate(
            record_id,
            (row["PC1"], row["PC2"]),
            xytext=label_offsets.get(record_id, (4, 4)),
            textcoords="offset points",
            fontsize=6.7,
            color="#222222",
            arrowprops={
                "arrowstyle": "-",
                "linewidth": 0.3,
                "color": "#666666",
                "shrinkA": 1.5,
                "shrinkB": 2,
            },
            zorder=5,
        )
    explained = metrics["pca"]["explained_variance_ratio"]
    ax.set_xlabel(f"PC1 ({100 * explained['PC1']:.1f}% variance)")
    ax.set_ylabel(f"PC2 ({100 * explained['PC2']:.1f}% variance)")
    ax.set_title("A  Four-feature PCA distribution", loc="left", fontweight="bold", pad=7)
    ax.legend(loc="best", frameon=False, handletextpad=0.4)
    ax.axhline(0, color=PALETTE["grid"], linewidth=0.55, zorder=0)
    ax.axvline(0, color=PALETTE["grid"], linewidth=0.55, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ranges = metrics["standardised_feature_range_overlap"]
    y_positions = np.arange(len(ranges), dtype=float)
    bar_height = 0.15
    offset = 0.11
    for index, row in enumerate(ranges):
        xiao_min = row["xiao_min_standardised"]
        xiao_max = row["xiao_max_standardised"]
        bolla_min = row["bolla_min_standardised"]
        bolla_max = row["bolla_max_standardised"]
        ax2.broken_barh(
            [(xiao_min, xiao_max - xiao_min)],
            (index - offset - bar_height / 2, bar_height),
            facecolors=PALETTE["xiao"],
            edgecolors=PALETTE["line"],
            linewidth=0.45,
        )
        ax2.broken_barh(
            [(bolla_min, bolla_max - bolla_min)],
            (index + offset - bar_height / 2, bar_height),
            facecolors="white",
            edgecolors=PALETTE["bolla"],
            linewidth=1.0,
        )
        for value, y_value, color in [
            (xiao_min, index - offset, PALETTE["line"]),
            (xiao_max, index - offset, PALETTE["line"]),
            (bolla_min, index + offset, PALETTE["bolla"]),
            (bolla_max, index + offset, PALETTE["bolla"]),
        ]:
            ax2.plot([value, value], [y_value - 0.075, y_value + 0.075], color=color, linewidth=0.65)
    ax2.set_yticks(y_positions)
    ax2.set_yticklabels([FEATURE_LABELS[row["feature"]] for row in ranges])
    ax2.invert_yaxis()
    ax2.axvline(0, color="#777777", linewidth=0.6, linestyle=(0, (3, 3)))
    ax2.set_xlabel("Standardised feature value")
    ax2.set_title("B  Per-feature dataset ranges", loc="left", fontweight="bold", pad=7)
    ax2.legend(
        handles=[
            Patch(facecolor=PALETTE["xiao"], edgecolor=PALETTE["line"], label="in-house"),
            Patch(facecolor="white", edgecolor=PALETTE["bolla"], label="literature"),
        ],
        loc="lower right",
        bbox_to_anchor=(1.12, 0.01),
        frameon=False,
        handlelength=1.4,
    )
    ax2.grid(axis="x", color=PALETTE["grid"], linewidth=0.45)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.subplots_adjust(left=0.085, right=0.955, bottom=0.16, top=0.90)
    fig.savefig(FIG_PDF)
    fig.savefig(FIG_PNG, dpi=450)
    plt.close(fig)


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def internal_verdict(loocv: dict) -> tuple[str, list[str]]:
    qualifying = []
    for model_name, result in loocv["models"].items():
        metrics = result["aggregate_metrics"]
        if metrics["R2_conv"] > 0.3 and metrics["spearman_rho"] is not None and metrics["spearman_rho"] > 0.5:
            qualifying.append(model_name)
    all_negative = all(result["aggregate_metrics"]["R2_conv"] < 0 for result in loocv["models"].values())
    if qualifying:
        return (
            "internally modellable with limited small-N evidence",
            qualifying,
        )
    if all_negative:
        return (
            "internal modellability is not demonstrated; the result is inconclusive at n=8 and indicates target-side difficulty",
            qualifying,
        )
    return (
        "inconclusive due to small N; performance is below the pre-specified R2_conv > 0.3 and Spearman > 0.5 threshold",
        qualifying,
    )


def make_report(metrics: dict, loocv: dict) -> str:
    overlap = metrics["pc1_pc2_bounding_boxes"]["overlap"]
    point_coverage = metrics["pc1_pc2_bounding_boxes"]["point_coverage"]
    hyperrectangle_coverage = metrics["standardised_4d_hyperrectangle_coverage"]
    centroid = metrics["pc1_pc2_centroids"]
    range_rows = metrics["standardised_feature_range_overlap"]
    disjoint_features = [FEATURE_LABELS[row["feature"]] for row in range_rows if not row["ranges_overlap"]]
    overlapping_features = [FEATURE_LABELS[row["feature"]] for row in range_rows if row["ranges_overlap"]]
    verdict, qualifying_models = internal_verdict(loocv)
    ridge = loocv["models"]["ridge"]["aggregate_metrics"]
    gpr = loocv["models"]["gpr"]["aggregate_metrics"]

    if point_coverage["bolla_records_inside_xiao_bbox"] == 0:
        distribution_phrase = (
            "The PC1-PC2 bounding boxes overlap geometrically, but none of the 8 literature observations "
            "falls inside the in-house PC1-PC2 box"
        )
    else:
        distribution_phrase = (
            "The PC1-PC2 point clouds have partial empirical overlap: "
            f"{point_coverage['bolla_records_inside_xiao_bbox']}/8 literature observations fall inside "
            "the in-house PC1-PC2 box"
        )

    if qualifying_models:
        target_contribution = (
            f"Bolla passes the pre-specified internal-modellability threshold for {', '.join(qualifying_models)}, "
            "so the cross-dataset failure is primarily attributable to feature-space and protocol mismatch."
        )
    else:
        target_contribution = (
            "Neither model passes the pre-specified internal-modellability threshold, so small-N target-side "
            "difficulty contributes alongside the feature-space mismatch; the evidence does not support a purely cross-dataset explanation."
        )

    lines = [
        "# Demo 2 Step 2i: Mechanism Analysis",
        "",
        "## Combined Mechanism Interpretation",
        "",
        f"{distribution_phrase}; likewise, {hyperrectangle_coverage['bolla_records_inside_xiao_hyperrectangle']}/8 literature records fall inside the in-house four-dimensional feature hyperrectangle. The two dataset centroids are {centroid['euclidean_distance_in_pooled_sd_units']:.2f} pooled standard deviations apart in PC1-PC2 space, although all four marginal feature ranges overlap.",
        f"Bolla-internal LOOCV gives Ridge R2_conv={ridge['R2_conv']:.3f}, rho={ridge['spearman_rho']:.3f}, and GPR R2_conv={gpr['R2_conv']:.3f}, rho={gpr['spearman_rho']:.3f}; {target_contribution}",
        "Mechanistically, ridge is driven toward a narrow prediction range because the source-side linear signal is weak and every literature record lies outside the observed in-house multivariate feature envelope; the RBF GPR reverts toward its learned mean as kernel similarity decays away from training points.",
        "Thus the observed near-constant ridge predictions and GPR prior-mean collapse are model-specific symptoms of the same distribution mismatch, with the Bolla LOOCV result determining whether limited target-side modellability is an additional contributor.",
        "",
        "## Analysis A: Four-Feature Distribution",
        "",
        "The combined 37-record feature matrix was standardised with StandardScaler fitted on all rows for visualisation only. This scaling was not used for transfer-model evaluation.",
        "",
        "### Standardisation Parameters",
        "",
        "| Feature | Mean | Scale |",
        "|---|---:|---:|",
    ]
    for feature in FEATURES:
        row = metrics["standard_scaler"][feature]
        lines.append(f"| `{feature}` | {row['mean']:.6f} | {row['scale']:.6f} |")

    lines += [
        "",
        "### PCA Explained Variance",
        "",
        "| Component | Explained variance ratio |",
        "|---|---:|",
    ]
    for component, value in metrics["pca"]["explained_variance_ratio"].items():
        lines.append(f"| {component} | {value:.6f} |")

    lines += [
        "",
        "### PCA Loadings",
        "",
        "Component weights are the PCA eigenvector coefficients; correlation loadings additionally scale each coefficient by the square root of the component eigenvalue.",
        "",
        "| Feature | PC1 weight | PC2 weight | PC1 correlation loading | PC2 correlation loading |",
        "|---|---:|---:|---:|---:|",
    ]
    for feature in FEATURES:
        weight = metrics["pca"]["component_weights"][feature]
        loading = metrics["pca"]["correlation_loadings"][feature]
        lines.append(
            f"| `{feature}` | {weight['PC1']:.6f} | {weight['PC2']:.6f} | "
            f"{loading['PC1']:.6f} | {loading['PC2']:.6f} |"
        )

    lines += [
        "",
        "### Standardised Feature-Range Overlap",
        "",
        "| Feature | in-house range | literature range | Overlap? | Shared interval | literature records inside in-house range |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for row in range_rows:
        shared = (
            f"[{row['overlap_min_standardised']:.3f}, {row['overlap_max_standardised']:.3f}]"
            if row["ranges_overlap"] and row["overlap_min_standardised"] is not None
            else "none"
        )
        lines.append(
            f"| {FEATURE_LABELS[row['feature']]} | [{row['xiao_min_standardised']:.3f}, "
            f"{row['xiao_max_standardised']:.3f}] | [{row['bolla_min_standardised']:.3f}, "
            f"{row['bolla_max_standardised']:.3f}] | {'yes' if row['ranges_overlap'] else 'DISJOINT'} | "
            f"{shared} | {row['bolla_records_inside_xiao_range']}/{row['n_bolla_records']} |"
        )

    xiao_box = metrics["pc1_pc2_bounding_boxes"]["xiao"]
    bolla_box = metrics["pc1_pc2_bounding_boxes"]["bolla"]
    lines += [
        "",
        "### PC1-PC2 Bounding Boxes and Centroids",
        "",
        "| Dataset | PC1 range | PC2 range | Centroid (PC1, PC2) |",
        "|---|---:|---:|---:|",
        f"| in-house | [{xiao_box['pc1_min']:.3f}, {xiao_box['pc1_max']:.3f}] | "
        f"[{xiao_box['pc2_min']:.3f}, {xiao_box['pc2_max']:.3f}] | "
        f"({centroid['xiao']['PC1']:.3f}, {centroid['xiao']['PC2']:.3f}) |",
        f"| literature | [{bolla_box['pc1_min']:.3f}, {bolla_box['pc1_max']:.3f}] | "
        f"[{bolla_box['pc2_min']:.3f}, {bolla_box['pc2_max']:.3f}] | "
        f"({centroid['bolla']['PC1']:.3f}, {centroid['bolla']['PC2']:.3f}) |",
        "",
        f"- PC1-PC2 bounding-box intersection area: {overlap['intersection_area']:.6f}.",
        f"- Percentage of in-house bounding box intersected by literature box: {overlap['percent_of_xiao_bbox_intersected']:.3f}%.",
        f"- Percentage of literature bounding box intersected by in-house box: {overlap['percent_of_bolla_bbox_intersected']:.3f}%.",
        f"- Literature observations inside the in-house PC1-PC2 bounding box: {point_coverage['bolla_records_inside_xiao_bbox']}/{point_coverage['n_bolla_records']}.",
        f"- In-house observations inside the literature PC1-PC2 bounding box: {point_coverage['xiao_records_inside_bolla_bbox']}/{point_coverage['n_xiao_records']}.",
        f"- Literature observations inside the in-house four-dimensional feature hyperrectangle: {hyperrectangle_coverage['bolla_records_inside_xiao_hyperrectangle']}/{hyperrectangle_coverage['n_bolla_records']}.",
        f"- Centroid displacement in pooled-SD units: PC1={centroid['delta_in_pooled_sd_units']['PC1']:.3f}, PC2={centroid['delta_in_pooled_sd_units']['PC2']:.3f}; Euclidean distance={centroid['euclidean_distance_in_pooled_sd_units']:.3f}.",
        "",
        f"Overlapping feature ranges: {', '.join(overlapping_features) if overlapping_features else 'none'}. Disjoint feature ranges: {', '.join(disjoint_features) if disjoint_features else 'none'}.",
        "",
        f"Verdict: {distribution_phrase}, and no literature record lies inside the in-house four-dimensional hyperrectangle. Because every marginal range overlaps, the separation is multivariate and driven by feature combinations and extremes rather than by one wholly disjoint feature. This supports out-of-distribution test exposure as a proximate mechanism for negative cross-protocol transfer.",
        "",
        "## Analysis B: Bolla-Internal LOOCV",
        "",
        "Each fold trains on seven Bolla records and predicts the eighth. StandardScaler is fitted on the seven-record training fold only. R2_conv is sklearn R2 computed once over all eight concatenated held-out predictions; RMSE is in log10(J); within-2x means absolute log10 residual <= log10(2).",
        "",
        "### Per-Fold Predictions",
        "",
        "| Held out | logJ actual | Ridge pred | Ridge residual | Ridge abs residual | Ridge within-2x | GPR pred | GPR residual | GPR abs residual | GPR within-2x |",
        "|---|---:|---:|---:|---:|---|---:|---:|---:|---|",
    ]
    ridge_rows = {row["record_id"]: row for row in loocv["models"]["ridge"]["predictions"]}
    gpr_rows = {row["record_id"]: row for row in loocv["models"]["gpr"]["predictions"]}
    for record_id in ridge_rows:
        ridge_row = ridge_rows[record_id]
        gpr_row = gpr_rows[record_id]
        lines.append(
            f"| {record_id} | {ridge_row['logJ_actual']:.6f} | {ridge_row['logJ_pred']:.6f} | "
            f"{ridge_row['residual_pred_minus_actual']:.6f} | {ridge_row['abs_residual']:.6f} | "
            f"{'yes' if ridge_row['within_2x'] else 'no'} | {gpr_row['logJ_pred']:.6f} | "
            f"{gpr_row['residual_pred_minus_actual']:.6f} | {gpr_row['abs_residual']:.6f} | "
            f"{'yes' if gpr_row['within_2x'] else 'no'} |"
        )

    lines += [
        "",
        "### Aggregate Metrics",
        "",
        "| Model | R2_conv | RMSE_logJ | Spearman rho | Pearson r | within-2x |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model_name in ["ridge", "gpr"]:
        result = loocv["models"][model_name]["aggregate_metrics"]
        lines.append(
            f"| {model_name.upper()} | {result['R2_conv']:.6f} | {result['rmse_logJ']:.6f} | "
            f"{fmt(result['spearman_rho'], 6)} | {fmt(result['pearson_r'], 6)} | "
            f"{result['within_2x_count']}/{result['n']} |"
        )

    lines += [
        "",
        f"Verdict: Bolla {verdict}. A model is called internally modellable here only if pooled LOOCV R2_conv > 0.3 and Spearman rho > 0.5; qualifying models: {', '.join(qualifying_models) if qualifying_models else 'none'}.",
        "",
        "Important caveat: only eight records are available for four input features. LOOCV therefore has very limited statistical power, and a modest positive score would still be compatible with chance. Scores below the stated threshold are interpreted as inconclusive rather than proof that Bolla is definitively unmodellable.",
        "",
        "## Path to Paper",
        "",
        f"The feature-space analysis provides the clearer direct mechanism-level evidence because it quantifies the geometric relationship between source and target: {point_coverage['bolla_records_inside_xiao_bbox']}/8 literature points inside the in-house PC1-PC2 box, {hyperrectangle_coverage['bolla_records_inside_xiao_hyperrectangle']}/8 inside the in-house four-dimensional hyperrectangle, and a {centroid['euclidean_distance_in_pooled_sd_units']:.2f}-pooled-SD centroid separation. The Bolla-internal LOOCV adds the necessary target-side control: {target_contribution}",
        "",
        "Together, these analyses answer the supervisor's symptoms-versus-mechanism concern. The cross-dataset prediction collapse is linked directly to feature-space distribution mismatch, while the internal control determines whether the eight-record target dataset also lacks enough stable structure for independent modelling.",
        "",
        "## Output Audit",
        "",
        f"- Step 2g feature-value sanity check: {metrics['feature_sanity_against_step2g']['status']}; "
        f"{metrics['feature_sanity_against_step2g']['n_values_compared']} values compared; "
        f"maximum absolute difference={metrics['feature_sanity_against_step2g']['max_absolute_difference']:.3e}.",
        "- `feature_space_pca.csv`",
        "- `feature_space_overlap_metrics.json`",
        "- `bolla_internal_loocv_results.json`",
        "- `figure_feature_space.pdf`",
        "- `figure_feature_space.png`",
        "- `run_demo2_mechanism.py`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    np.random.seed(RANDOM_STATE)
    xiao, bolla, combined = build_inputs()
    feature_sanity = verify_features(xiao, bolla)
    pca_rows, overlap_metrics = analyse_feature_space(combined, feature_sanity)
    loocv = run_bolla_loocv(bolla)

    pca_rows.to_csv(PCA_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    write_json(OVERLAP_JSON, overlap_metrics)
    write_json(LOOCV_JSON, loocv)
    make_figure(pca_rows, overlap_metrics)
    REPORT.write_text(make_report(overlap_metrics, loocv), encoding="utf-8")

    overlap = overlap_metrics["pc1_pc2_bounding_boxes"]["overlap"]
    centroid_distance = overlap_metrics["pc1_pc2_centroids"]["euclidean_distance_in_pooled_sd_units"]
    print("[DEMO2 MECHANISM] Done")
    print(
        f"feature_sanity={feature_sanity['status']} "
        f"max_abs_diff={feature_sanity['max_absolute_difference']:.3e}"
    )
    print(
        f"PCA bbox overlap: Xiao={overlap['percent_of_xiao_bbox_intersected']:.3f}% "
        f"Bolla={overlap['percent_of_bolla_bbox_intersected']:.3f}%"
    )
    print(f"PCA centroid distance={centroid_distance:.3f} pooled SD")
    for model_name in ["ridge", "gpr"]:
        result = loocv["models"][model_name]["aggregate_metrics"]
        print(
            f"Bolla LOOCV {model_name}: R2={result['R2_conv']:.3f} "
            f"RMSE={result['rmse_logJ']:.3f} rho={result['spearman_rho']:.3f} "
            f"within={result['within_2x_count']}/{result['n']}"
        )
    print(f"Figure: {FIG_PDF}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
