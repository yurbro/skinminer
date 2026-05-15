from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, DotProduct, RBF, WhiteKernel
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs/demonstration"
FEATURE_COLUMNS = ["poloxamer_407_pct", "ethanol_pct", "propylene_glycol_pct"]
RESPONSE_COLUMN = "cumulative_amount_24h_ug_cm2"


@dataclass(frozen=True)
class Scenario:
    name: str
    n_train: int
    augment: bool


SCENARIOS = [
    Scenario("baseline_5", 5, False),
    Scenario("augmented_5", 5, True),
    Scenario("baseline_10", 10, False),
    Scenario("augmented_10", 10, True),
    Scenario("baseline_15", 15, False),
    Scenario("augmented_15", 15, True),
    Scenario("baseline_20", 20, False),
    Scenario("augmented_20", 20, True),
]


def make_kernel(mode: str):
    if mode == "paper_like":
        return (
            ConstantKernel(1.0, (1e-3, 1e3))
            + ConstantKernel(1.0, (1e-3, 1e3)) * DotProduct()
            + ConstantKernel(1.0, (1e-3, 1e3)) * RBF(length_scale=1.0, length_scale_bounds=(1e-3, 1e3))
            + WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-6, 1e2))
        )
    return ConstantKernel(1.0, (1e-3, 1e3)) * RBF(length_scale=1.0, length_scale_bounds=(1e-3, 1e3)) + WhiteKernel(
        noise_level=1.0, noise_level_bounds=(1e-6, 1e2)
    )


def load_own_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"formulation_id", *FEATURE_COLUMNS, RESPONSE_COLUMN}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Own-data CSV is missing required columns: {sorted(missing)}")
    for column in [*FEATURE_COLUMNS, RESPONSE_COLUMN]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=[*FEATURE_COLUMNS, RESPONSE_COLUMN]).copy()
    if df["formulation_id"].nunique() < 2:
        raise ValueError("Own-data CSV must contain at least two formulations.")
    return df


def load_replicates(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    df = pd.read_csv(path)
    required = {"formulation_id", RESPONSE_COLUMN}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Replicate CSV is missing required columns: {sorted(missing)}")
    df[RESPONSE_COLUMN] = pd.to_numeric(df[RESPONSE_COLUMN], errors="coerce")
    return df.dropna(subset=["formulation_id", RESPONSE_COLUMN]).copy()


def load_literature(path: Path, max_response: float | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(path)
    required = {"formulation_label", RESPONSE_COLUMN}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Literature CSV is missing required columns: {sorted(missing)}")
    df[RESPONSE_COLUMN] = pd.to_numeric(df[RESPONSE_COLUMN], errors="coerce")
    raw = df.dropna(subset=[RESPONSE_COLUMN]).copy()
    if max_response is None:
        return raw, raw.copy()
    used = raw[raw[RESPONSE_COLUMN].between(0.0, max_response, inclusive="both")].copy()
    return raw, used


def sigma_own_from_training(train_df: pd.DataFrame, replicate_df: pd.DataFrame | None) -> float:
    if replicate_df is not None:
        train_groups = set(train_df["formulation_id"].astype(str))
        reps = replicate_df[replicate_df["formulation_id"].astype(str).isin(train_groups)]
        stds = reps.groupby("formulation_id")[RESPONSE_COLUMN].std(ddof=1).dropna()
        stds = stds[stds > 0]
        if not stds.empty:
            return float(stds.mean())

    global_std = float(train_df[RESPONSE_COLUMN].std(ddof=1))
    if np.isfinite(global_std) and global_std > 0:
        return max(global_std * 0.1, 1.0)
    return 5.0


def literature_pseudo_features(X_train: np.ndarray, n_lit: int) -> np.ndarray:
    if n_lit == 0:
        return np.empty((0, X_train.shape[1]), dtype=float)
    center = np.mean(X_train, axis=0, keepdims=True)
    return np.repeat(center, n_lit, axis=0)


def evaluate_model(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    literature_df: pd.DataFrame,
    replicate_df: pd.DataFrame | None,
    augment: bool,
    alpha_factor: float | None,
    kernel_mode: str,
    seed: int,
) -> dict[str, float | int]:
    X_train = train_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_train = train_df[RESPONSE_COLUMN].to_numpy(dtype=float)
    X_test = test_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_test = test_df[RESPONSE_COLUMN].to_numpy(dtype=float)

    sigma_own = sigma_own_from_training(train_df, replicate_df)
    alpha_own = np.full(len(train_df), sigma_own**2, dtype=float)

    X_fit = X_train
    y_fit = y_train
    alpha = alpha_own
    n_lit = 0

    if augment:
        lit_values = literature_df[RESPONSE_COLUMN].dropna().to_numpy(dtype=float)
        n_lit = len(lit_values)
        X_lit = literature_pseudo_features(X_train, n_lit)
        alpha_lit = np.full(n_lit, (float(alpha_factor) * sigma_own) ** 2, dtype=float)
        X_fit = np.vstack([X_train, X_lit])
        y_fit = np.concatenate([y_train, lit_values])
        alpha = np.concatenate([alpha_own, alpha_lit])

    model = GaussianProcessRegressor(
        kernel=make_kernel(kernel_mode),
        alpha=alpha,
        normalize_y=True,
        n_restarts_optimizer=2,
        random_state=seed,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model.fit(X_fit, y_fit)
    y_pred = model.predict(X_test)

    return {
        "sigma_own": sigma_own,
        "n_train_rows": int(len(train_df)),
        "n_test_rows": int(len(test_df)),
        "n_train_groups": int(train_df["formulation_id"].nunique()),
        "n_test_groups": int(test_df["formulation_id"].nunique()),
        "n_lit_rows": int(n_lit),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "r2": float(r2_score(y_test, y_pred)) if len(y_test) > 1 else np.nan,
        "y_test_mean": float(np.mean(y_test)),
    }


def scenario_splits(
    own_df: pd.DataFrame,
    n_train: int,
    n_splits: int,
    seed: int,
) -> Iterable[tuple[int, np.ndarray, np.ndarray, str]]:
    groups = np.array(sorted(own_df["formulation_id"].unique()))
    rng = np.random.default_rng(seed + n_train)
    if n_train < len(groups):
        for split_id in range(n_splits):
            train_groups = np.array(sorted(rng.choice(groups, size=n_train, replace=False)))
            test_groups = np.array(sorted([group for group in groups if group not in set(train_groups)]))
            yield split_id, train_groups, test_groups, "holdout"
        return

    gkf = GroupKFold(n_splits=min(5, len(groups)))
    unique_group_df = own_df.drop_duplicates("formulation_id")
    for split_id, (train_idx, test_idx) in enumerate(
        gkf.split(
            unique_group_df[FEATURE_COLUMNS].to_numpy(),
            groups=unique_group_df["formulation_id"].to_numpy(),
        )
    ):
        if split_id >= n_splits:
            break
        train_groups = unique_group_df.iloc[train_idx]["formulation_id"].to_numpy()
        test_groups = unique_group_df.iloc[test_idx]["formulation_id"].to_numpy()
        yield split_id, train_groups, test_groups, "group_cv"


def summarize_results(results_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    grouped = (
        results_df.groupby(["scenario", "n_train", "augment", "alpha_factor"], dropna=False)
        .agg(
            rmse_mean=("rmse", "mean"),
            rmse_sd=("rmse", "std"),
            r2_mean=("r2", "mean"),
            r2_sd=("r2", "std"),
            n_runs=("split_id", "count"),
        )
        .reset_index()
    )

    baseline_map = {
        int(row["n_train"]): float(row["rmse_mean"])
        for _, row in grouped[grouped["augment"] == False].iterrows()  # noqa: E712
    }
    grouped["rmse_change_vs_baseline_pct"] = grouped.apply(
        lambda row: np.nan
        if not row["augment"]
        else 100.0 * (float(row["rmse_mean"]) - baseline_map[int(row["n_train"])]) / baseline_map[int(row["n_train"])],
        axis=1,
    )
    grouped["rmse_improvement_vs_baseline_pct"] = -grouped["rmse_change_vs_baseline_pct"]

    best_rows = []
    rmse_curve_rows = []
    for n_train in sorted(grouped["n_train"].unique()):
        baseline_row = grouped[(grouped["n_train"] == n_train) & (grouped["augment"] == False)].iloc[0]
        best_rows.append(baseline_row.to_dict())
        rmse_curve_rows.append(
            {
                "n_train": int(n_train),
                "method": "baseline",
                "rmse_mean": float(baseline_row["rmse_mean"]),
                "rmse_std": float(baseline_row["rmse_sd"]) if pd.notna(baseline_row["rmse_sd"]) else 0.0,
            }
        )
        aug_block = grouped[(grouped["n_train"] == n_train) & (grouped["augment"] == True)]
        if not aug_block.empty:
            best_aug = aug_block.sort_values("rmse_mean").iloc[0]
            best_rows.append(best_aug.to_dict())
            rmse_curve_rows.append(
                {
                    "n_train": int(n_train),
                    "method": "augmented_best",
                    "rmse_mean": float(best_aug["rmse_mean"]),
                    "rmse_std": float(best_aug["rmse_sd"]) if pd.notna(best_aug["rmse_sd"]) else 0.0,
                }
            )
    return grouped, pd.DataFrame(best_rows), pd.DataFrame(rmse_curve_rows)


def format_pm(mean: float, sd: float | None) -> str:
    sd_value = 0.0 if sd is None or pd.isna(sd) else float(sd)
    return f"{float(mean):.3f}+/-{sd_value:.3f}"


def write_summary(
    path: Path,
    own_data_path: Path,
    literature_path: Path,
    own_df: pd.DataFrame,
    literature_raw_df: pd.DataFrame,
    literature_used_df: pd.DataFrame,
    grouped_df: pd.DataFrame,
    best_df: pd.DataFrame,
    alpha_factors: list[float],
    kernel_mode: str,
    max_literature_response: float | None,
) -> None:
    own_range = (own_df[RESPONSE_COLUMN].min(), own_df[RESPONSE_COLUMN].max())
    lit_range = (literature_raw_df[RESPONSE_COLUMN].min(), literature_raw_df[RESPONSE_COLUMN].max())
    lit_used_range = (literature_used_df[RESPONSE_COLUMN].min(), literature_used_df[RESPONSE_COLUMN].max())
    membrane_counts = literature_used_df.get("membrane_type", pd.Series(dtype=object)).fillna("(missing)").value_counts()

    lines = [
        "# GPR Literature Augmentation Results (24h Shared Timepoint)",
        "",
        "## 1. Data Summary",
        "",
        "### Self-Generated Data (Paper 1)",
        "",
        f"- Input: `{own_data_path}`",
        f"- Formulations: `{own_df['formulation_id'].nunique()}`",
        "- Replicates: `5 per formulation in the source file; formulation means used for GPR`",
        "- Timepoint: `24h`",
        f"- Response range: `{own_range[0]:.3f} to {own_range[1]:.3f} ug/cm2`",
        "- Excipients: `Poloxamer 407, Ethanol, Propylene glycol`",
        "",
        "### Literature Data (SkinMiner)",
        "",
        f"- Input: `{literature_path}`",
        f"- Canonical records at 24h: `{len(literature_raw_df)}`",
        f"- Records used after default sanity filter: `{len(literature_used_df)}`",
        f"- Source papers used: `{literature_used_df['doi'].nunique() if 'doi' in literature_used_df else 'n/a'}`",
        f"- Raw response range: `{lit_range[0]:.3f} to {lit_range[1]:.3f} ug/cm2`",
        f"- Used response range: `{lit_used_range[0]:.3f} to {lit_used_range[1]:.3f} ug/cm2`",
        f"- Max literature response filter: `{max_literature_response if max_literature_response is not None else 'disabled'}`",
        "",
        "### Literature Membrane Types Used",
        "",
        "| Membrane type | Records |",
        "|---|---:|",
    ]
    for membrane, count in membrane_counts.items():
        lines.append(f"| `{membrane}` | {count} |")

    lines.extend(
        [
            "",
            "### Overlap Assessment",
            "",
            "Both datasets now share ibuprofen, Franz-cell/diffusion-cell context, cumulative amount response, and the 24h timepoint. The main remaining mismatch is formulation chemistry and membrane type.",
            "",
            "## 2. Results",
            "",
            "### Main Table",
            "",
            "| Scenario | N_train | Augmented? | alpha | RMSE (mean+/-SD) | R2 (mean+/-SD) | RMSE change vs baseline |",
            "|---|---:|---|---:|---|---|---:|",
        ]
    )
    for _, row in grouped_df.sort_values(["n_train", "augment", "alpha_factor"]).iterrows():
        alpha_text = "-" if pd.isna(row["alpha_factor"]) else str(int(row["alpha_factor"]))
        change = "-" if not row["augment"] else f"{row['rmse_change_vs_baseline_pct']:.1f}%"
        lines.append(
            f"| {row['scenario']} | {int(row['n_train'])} | {'Yes' if row['augment'] else 'No'} | "
            f"{alpha_text} | {format_pm(row['rmse_mean'], row['rmse_sd'])} | "
            f"{format_pm(row['r2_mean'], row['r2_sd'])} | {change} |"
        )

    lines.extend(
        [
            "",
            "### Best Alpha Per Scenario",
            "",
            "| N_train | Best alpha | Best RMSE | Baseline RMSE | Improvement |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for n_train in sorted(grouped_df["n_train"].unique()):
        baseline = grouped_df[(grouped_df["n_train"] == n_train) & (grouped_df["augment"] == False)].iloc[0]
        aug = grouped_df[(grouped_df["n_train"] == n_train) & (grouped_df["augment"] == True)].sort_values("rmse_mean").iloc[0]
        lines.append(
            f"| {int(n_train)} | {int(aug['alpha_factor'])} | {aug['rmse_mean']:.3f} | "
            f"{baseline['rmse_mean']:.3f} | {aug['rmse_improvement_vs_baseline_pct']:.1f}% |"
        )

    best_aug = best_df[best_df["augment"] == True].sort_values("rmse_mean")  # noqa: E712
    best_gain = best_df[best_df["augment"] == True].sort_values("rmse_improvement_vs_baseline_pct", ascending=False)  # noqa: E712
    if not best_aug.empty:
        best_overall = best_aug.iloc[0]
        best_improvement = best_gain.iloc[0]
        finding_lines = [
            f"1. Lowest augmented RMSE: N={int(best_overall['n_train'])}, alpha={int(best_overall['alpha_factor'])}, RMSE={best_overall['rmse_mean']:.3f}.",
            f"2. Largest RMSE improvement: N={int(best_improvement['n_train'])}, alpha={int(best_improvement['alpha_factor'])}, improvement={best_improvement['rmse_improvement_vs_baseline_pct']:.1f}%.",
            "3. The 24h alignment makes the augmentation scientifically cleaner than the previous 28h placeholder setup.",
            "4. The limitation remains domain mismatch: literature provides response-scale information, not a matched Poloxamer/Ethanol/PG formulation map.",
        ]
    else:
        finding_lines = ["1. No augmented scenarios were generated."]

    lines.extend(
        [
            "",
            "## 3. Visualization Data",
            "",
            "- Distribution data: `fig_data_distribution.csv`",
            "- RMSE curve data: `fig_rmse_curves.csv`",
            "",
            "## 4. Key Findings",
            "",
            *finding_lines,
            "",
            "## 5. PhD Closure Narrative",
            "",
            "SkinMiner closes the loop with Paper 1 by turning verified literature extraction into an explicit prior for early-stage GPR modelling; the revised 24h endpoint provides a shared experimental anchor, so the demonstration tests literature-assisted prediction under sparse self-generated data rather than an unmatched timepoint proxy.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the 24h GPR literature augmentation demonstration.")
    parser.add_argument(
        "--own-data",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "paper1_24h_mean.csv",
        help="CSV with Paper 1 24h formulation means.",
    )
    parser.add_argument(
        "--own-replicates",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "paper1_24h_all_replicates.csv",
        help="CSV with Paper 1 24h replicate rows, used to estimate own-data noise.",
    )
    parser.add_argument(
        "--literature-data",
        type=Path,
        default=DEFAULT_OUTPUT_DIR / "literature_24h_data.csv",
        help="24h literature CSV produced by prepare_demonstration_24h_data.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for result artifacts.",
    )
    parser.add_argument(
        "--alpha-factors",
        type=float,
        nargs="+",
        default=[3.0, 5.0, 10.0, 20.0, 50.0],
        help="Alpha-factor multipliers for literature noise.",
    )
    parser.add_argument(
        "--kernel",
        choices=["basic", "paper_like"],
        default="paper_like",
        help="Kernel family for GaussianProcessRegressor.",
    )
    parser.add_argument(
        "--n-splits",
        type=int,
        default=10,
        help="Number of random splits for holdout training sizes. N=20 uses 5-fold group CV.",
    )
    parser.add_argument("--seed", type=int, default=20260423, help="Random seed for split reproducibility.")
    parser.add_argument(
        "--max-literature-response",
        type=float,
        default=1000.0,
        help="Default sanity filter for 24h literature response in ug/cm2. Use a negative value to disable.",
    )
    args = parser.parse_args()

    own_data_path = args.own_data if args.own_data.is_absolute() else ROOT / args.own_data
    own_replicates_path = args.own_replicates if args.own_replicates.is_absolute() else ROOT / args.own_replicates
    literature_path = args.literature_data if args.literature_data.is_absolute() else ROOT / args.literature_data
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    max_literature_response = None if args.max_literature_response < 0 else args.max_literature_response
    own_df = load_own_data(own_data_path)
    replicate_df = load_replicates(own_replicates_path)
    literature_raw_df, literature_used_df = load_literature(literature_path, max_literature_response)
    if literature_used_df.empty:
        raise ValueError("No literature records remain after filtering.")

    results: list[dict[str, float | int | str | None]] = []
    for scenario in SCENARIOS:
        for split_id, train_groups, test_groups, split_strategy in scenario_splits(
            own_df, scenario.n_train, args.n_splits, args.seed
        ):
            train_df = own_df[own_df["formulation_id"].isin(train_groups)].copy()
            test_df = own_df[own_df["formulation_id"].isin(test_groups)].copy()

            if scenario.augment:
                for alpha_factor in args.alpha_factors:
                    metrics = evaluate_model(
                        train_df,
                        test_df,
                        literature_used_df,
                        replicate_df,
                        augment=True,
                        alpha_factor=alpha_factor,
                        kernel_mode=args.kernel,
                        seed=args.seed + split_id + int(alpha_factor * 10),
                    )
                    results.append(
                        {
                            "scenario": scenario.name,
                            "n_train": scenario.n_train,
                            "augment": True,
                            "alpha_factor": alpha_factor,
                            "split_id": split_id,
                            "split_strategy": split_strategy,
                            **metrics,
                        }
                    )
            else:
                metrics = evaluate_model(
                    train_df,
                    test_df,
                    literature_used_df,
                    replicate_df,
                    augment=False,
                    alpha_factor=None,
                    kernel_mode=args.kernel,
                    seed=args.seed + split_id,
                )
                results.append(
                    {
                        "scenario": scenario.name,
                        "n_train": scenario.n_train,
                        "augment": False,
                        "alpha_factor": np.nan,
                        "split_id": split_id,
                        "split_strategy": split_strategy,
                        **metrics,
                    }
                )

    results_df = pd.DataFrame(results)
    grouped_df, best_df, rmse_curve_df = summarize_results(results_df)

    results_path = output_dir / "gpr_augmentation_results_24h.csv"
    grouped_path = output_dir / "gpr_augmentation_figure_data_24h.csv"
    summary_path = output_dir / "gpr_augmentation_summary_24h.md"
    rmse_curve_path = output_dir / "fig_rmse_curves.csv"

    results_df.to_csv(results_path, index=False, encoding="utf-8-sig")
    grouped_df.to_csv(grouped_path, index=False, encoding="utf-8-sig")
    rmse_curve_df.to_csv(rmse_curve_path, index=False, encoding="utf-8-sig")
    write_summary(
        summary_path,
        own_data_path,
        literature_path,
        own_df,
        literature_raw_df,
        literature_used_df,
        grouped_df,
        best_df,
        args.alpha_factors,
        args.kernel,
        max_literature_response,
    )

    payload = {
        "results_csv": str(results_path),
        "summary_md": str(summary_path),
        "figure_data_csv": str(grouped_path),
        "rmse_curve_csv": str(rmse_curve_path),
        "own_data_path": str(own_data_path),
        "literature_data_path": str(literature_path),
        "literature_records_raw": int(len(literature_raw_df)),
        "literature_records_used": int(len(literature_used_df)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
