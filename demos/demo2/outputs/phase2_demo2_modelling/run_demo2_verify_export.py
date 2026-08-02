from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, rankdata, spearmanr


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_demo2_modelling as demo2


OUT = SCRIPT_DIR
FEATURES = demo2.FEATURES
LOG10_2 = math.log10(2.0)


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


def fmt(value: float | int | None, digits: int = 6, na: str = "NA") -> str:
    if value is None:
        return na
    if isinstance(value, float) and math.isnan(value):
        return na
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.{digits}f}"


def record_map(df: pd.DataFrame) -> dict[str, pd.Series]:
    return {str(row["record_id"]): row for _, row in df.iterrows()}


def export_rows(transfer: dict, train: pd.DataFrame, test: pd.DataFrame) -> list[dict]:
    test_by_id = record_map(test)
    rows = []
    for pred in transfer["predictions"]:
        record_id = str(pred["record_id"])
        source = test_by_id[record_id]
        residual = float(pred["predicted_log10_J"] - pred["actual_log10_J"])
        rows.append(
            {
                "record_id": record_id,
                "J_actual": float(pred["actual_J"]),
                "logJ_actual": float(pred["actual_log10_J"]),
                "logJ_pred": float(pred["predicted_log10_J"]),
                "J_pred": float(pred["predicted_J"]),
                "residual_log": residual,
                "abs_residual_log": abs(residual),
                "within_2x": int(abs(residual) <= LOG10_2),
                "feat_log10_vehicle_solubility": float(source["log10_vehicle_solubility"]),
                "feat_ethanol_fraction": float(source["ethanol_fraction"]),
                "feat_drug_state_solubilized": float(source["drug_state_solubilized"]),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
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
        "feat_drug_state_solubilized",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            formatted = {}
            for key in columns:
                value = row[key]
                if isinstance(value, float):
                    formatted[key] = f"{value:.12f}"
                else:
                    formatted[key] = value
            writer.writerow(formatted)


def feature_table_rows(df: pd.DataFrame) -> list[dict]:
    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "record_id": str(row["record_id"]),
                "J": float(row["J"]),
                "log10_J": float(row["log10_J"]),
                "feat_log10_vehicle_solubility": float(row["log10_vehicle_solubility"]),
                "feat_ethanol_fraction": float(row["ethanol_fraction"]),
                "feat_drug_state_solubilized": float(row["drug_state_solubilized"]),
            }
        )
    return rows


def recompute_metrics(direction_key: str, transfer: dict, train: pd.DataFrame, rows: list[dict]) -> dict:
    y_actual = np.array([row["logJ_actual"] for row in rows], dtype=float)
    y_pred = np.array([row["logJ_pred"] for row in rows], dtype=float)
    residuals = y_pred - y_actual
    mean_test = float(np.mean(y_actual))
    mean_train = float(np.mean(train["log10_J"].to_numpy(dtype=float)))
    ss_res = float(np.sum((y_actual - y_pred) ** 2))
    ss_tot_test = float(np.sum((y_actual - mean_test) ** 2))
    ss_tot_train = float(np.sum((y_actual - mean_train) ** 2))
    r2_conv = float(1.0 - ss_res / ss_tot_test)
    r2_gen = float(1.0 - ss_res / ss_tot_train)
    rmse = float(math.sqrt(ss_res / len(rows)))
    actual_ranks = rankdata(y_actual, method="average")
    pred_ranks = rankdata(y_pred, method="average")
    spearman = float(spearmanr(y_actual, y_pred).statistic)
    pearson = float(pearsonr(y_actual, y_pred).statistic)
    within_count = int(np.sum(np.abs(residuals) <= LOG10_2))
    return {
        "direction": direction_key,
        "n_test": int(len(rows)),
        "mean_logJ_test": mean_test,
        "mean_logJ_train": mean_train,
        "SS_res": ss_res,
        "SS_tot_testmean": ss_tot_test,
        "SS_tot_trainmean": ss_tot_train,
        "R2_conv": r2_conv,
        "R2_gen": r2_gen,
        "RMSE_logJ": rmse,
        "Spearman_rho": spearman,
        "Pearson_r": pearson,
        "within_2x_count": within_count,
        "within_2x_n": int(len(rows)),
        "within_2x_fraction": float(within_count / len(rows)),
        "rank_vectors": {
            "record_id": [row["record_id"] for row in rows],
            "logJ_actual": y_actual.tolist(),
            "logJ_pred": y_pred.tolist(),
            "actual_rank_average": actual_ranks.tolist(),
            "pred_rank_average": pred_ranks.tolist(),
        },
        "reported_primary_metrics": transfer["metrics"],
        "metric_deltas_vs_reported": {
            "R2_conv": r2_conv - float(transfer["metrics"]["R2_conv"]),
            "R2_gen": r2_gen - float(transfer["metrics"]["R2_gen_train_mean_baseline"]),
            "RMSE_logJ": rmse - float(transfer["metrics"]["rmse_logJ"]),
            "Spearman_rho": spearman - float(transfer["metrics"]["spearman_rho"]),
            "Pearson_r": pearson - float(transfer["metrics"]["pearson_r"]),
            "within_2x_count": within_count - int(transfer["metrics"]["within_2x_count"]),
        },
    }


def match_text(recomputed: float | int, reported: float | int, tol: float = 5e-4) -> str:
    return "PASS" if abs(float(recomputed) - float(reported)) <= tol else "FAIL"


def reconciliation_rows(metrics: dict) -> list[dict]:
    specs = [
        ("R2_conv", "R2_conv", "R2_conv", 5e-4),
        ("Spearman rho", "Spearman_rho", "spearman_rho", 5e-4),
        ("RMSE_logJ", "RMSE_logJ", "rmse_logJ", 5e-4),
        ("within-2x", "within_2x_count", "within_2x_count", 0.0),
    ]
    rows = []
    for direction, payload in metrics["directions"].items():
        reported = payload["reported_primary_metrics"]
        for label, recomputed_key, reported_key, tol in specs:
            recomputed = payload[recomputed_key]
            rep = reported[reported_key]
            if label == "within-2x":
                rec_text = f"{payload['within_2x_count']}/{payload['within_2x_n']}"
                rep_text = f"{int(rep)}/{int(reported['n'])}"
                matched = "PASS" if rec_text == rep_text else "FAIL"
            else:
                rec_text = fmt(float(recomputed), 6)
                rep_text = fmt(float(rep), 6)
                matched = match_text(float(recomputed), float(rep), tol=tol)
            rows.append(
                {
                    "metric": label,
                    "direction": direction,
                    "reported": rep_text,
                    "recomputed": rec_text,
                    "match": matched,
                }
            )
    return rows


def markdown_feature_table(rows: list[dict], max_rows: int | None = None) -> list[str]:
    selected = rows if max_rows is None else rows[:max_rows]
    lines = [
        "| record_id | J | log10_J | feat_log10_vehicle_solubility | feat_ethanol_fraction | feat_drug_state_solubilized |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in selected:
        lines.append(
            f"| {row['record_id']} | {fmt(row['J'], 6)} | {fmt(row['log10_J'], 6)} | "
            f"{fmt(row['feat_log10_vehicle_solubility'], 6)} | {fmt(row['feat_ethanol_fraction'], 6)} | "
            f"{fmt(row['feat_drug_state_solubilized'], 6)} |"
        )
    return lines


def make_report(
    metrics: dict,
    xiao_to_bolla_rows: list[dict],
    bolla_to_xiao_rows: list[dict],
    train_feature_sections: dict,
) -> str:
    rec_rows = reconciliation_rows(metrics)
    lines = [
        "# Demo 2 Verification Export",
        "",
        "## Purpose",
        "",
        "This export reuses the existing primary Demo 2 ridge/log10 transfer predictions from `transfer_xiao_to_bolla.json` and `transfer_bolla_to_xiao.json`. No modelling was rerun. The CSV files contain per-record actual values, predictions, residuals, within-2x flags, and the exact three solubility-bridge feature values fed to the model.",
        "",
        "Primary configuration: StandardScaler(train only) + Ridge(alpha=1.0), target=log10(J), features=`log10_vehicle_solubility`, `ethanol_fraction`, `drug_state_solubilized`.",
        "",
        "## Sanity Reconciliation",
        "",
        "| metric | direction | reported | recomputed here | match? |",
        "|---|---|---:|---:|---|",
    ]
    for row in rec_rows:
        lines.append(f"| {row['metric']} | {row['direction']} | {row['reported']} | {row['recomputed']} | {row['match']} |")

    lines += [
        "",
        "## R2 Hand-Check Terms",
        "",
        "| direction | n_test | mean_logJ_test | mean_logJ_train | SS_res | SS_tot_testmean | SS_tot_trainmean | R2_conv | R2_gen | RMSE_logJ | Spearman rho | Pearson r | within-2x |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for direction, payload in metrics["directions"].items():
        lines.append(
            f"| {direction} | {payload['n_test']} | {fmt(payload['mean_logJ_test'], 9)} | "
            f"{fmt(payload['mean_logJ_train'], 9)} | {fmt(payload['SS_res'], 9)} | "
            f"{fmt(payload['SS_tot_testmean'], 9)} | {fmt(payload['SS_tot_trainmean'], 9)} | "
            f"{fmt(payload['R2_conv'], 9)} | {fmt(payload['R2_gen'], 9)} | {fmt(payload['RMSE_logJ'], 9)} | "
            f"{fmt(payload['Spearman_rho'], 9)} | {fmt(payload['Pearson_r'], 9)} | "
            f"{payload['within_2x_count']}/{payload['within_2x_n']} |"
        )

    lines += [
        "",
        "## Rank Vectors Used For Spearman",
        "",
    ]
    for direction, payload in metrics["directions"].items():
        rv = payload["rank_vectors"]
        lines += [
            f"### {direction}",
            "",
            "| record_id | logJ_actual | actual_rank | logJ_pred | pred_rank |",
            "|---|---:|---:|---:|---:|",
        ]
        for rid, actual, actual_rank, pred, pred_rank in zip(
            rv["record_id"],
            rv["logJ_actual"],
            rv["actual_rank_average"],
            rv["logJ_pred"],
            rv["pred_rank_average"],
        ):
            lines.append(f"| {rid} | {fmt(actual, 9)} | {fmt(actual_rank, 6)} | {fmt(pred, 9)} | {fmt(pred_rank, 6)} |")
        lines.append("")

    lines += [
        "## Training Feature Values",
        "",
        "### Xiao->Bolla training records (Xiao, n=29)",
        "",
    ]
    lines += markdown_feature_table(train_feature_sections["xiao_to_bolla_train"])
    lines += [
        "",
        "### Bolla->Xiao training records (Bolla, n=8)",
        "",
    ]
    lines += markdown_feature_table(train_feature_sections["bolla_to_xiao_train"])

    lines += [
        "",
        "## Exported CSV Files",
        "",
        f"- `verify_xiao_to_bolla.csv` rows: {len(xiao_to_bolla_rows)}",
        f"- `verify_bolla_to_xiao.csv` rows: {len(bolla_to_xiao_rows)}",
        "- `verify_metrics_recompute.json` includes the same hand-check terms and rank vectors.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    xiao = demo2.build_xiao()
    bolla = demo2.build_bolla()
    xiao_to_bolla = json.loads((OUT / "transfer_xiao_to_bolla.json").read_text(encoding="utf-8"))
    bolla_to_xiao = json.loads((OUT / "transfer_bolla_to_xiao.json").read_text(encoding="utf-8"))

    x2b_rows = export_rows(xiao_to_bolla, xiao, bolla)
    b2x_rows = export_rows(bolla_to_xiao, bolla, xiao)
    write_csv(OUT / "verify_xiao_to_bolla.csv", x2b_rows)
    write_csv(OUT / "verify_bolla_to_xiao.csv", b2x_rows)

    metrics = {
        "metadata": {
            "source_predictions": {
                "xiao_to_bolla": "transfer_xiao_to_bolla.json",
                "bolla_to_xiao": "transfer_bolla_to_xiao.json",
            },
            "model": "StandardScaler(train only) + Ridge(alpha=1.0)",
            "target": "log10(J)",
            "features": FEATURES,
            "within_2x_threshold_log10": LOG10_2,
            "modelling_rerun": False,
        },
        "directions": {
            "Xiao->Bolla": recompute_metrics("Xiao->Bolla", xiao_to_bolla, xiao, x2b_rows),
            "Bolla->Xiao": recompute_metrics("Bolla->Xiao", bolla_to_xiao, bolla, b2x_rows),
        },
    }
    write_json(OUT / "verify_metrics_recompute.json", metrics)

    train_features = {
        "xiao_to_bolla_train": feature_table_rows(xiao),
        "bolla_to_xiao_train": feature_table_rows(bolla),
    }
    (OUT / "demo2_verify_report.md").write_text(
        make_report(metrics, x2b_rows, b2x_rows, train_features),
        encoding="utf-8",
    )

    print("[DEMO2 VERIFY EXPORT] Done")
    for direction, payload in metrics["directions"].items():
        print(
            f"{direction}: R2_conv={payload['R2_conv']:.6f}, R2_gen={payload['R2_gen']:.6f}, "
            f"RMSE_logJ={payload['RMSE_logJ']:.6f}, Spearman={payload['Spearman_rho']:.6f}, "
            f"within={payload['within_2x_count']}/{payload['within_2x_n']}"
        )
    for row in reconciliation_rows(metrics):
        if row["match"] != "PASS":
            print(f"WARNING mismatch: {row}")


if __name__ == "__main__":
    main()
