from __future__ import annotations

import csv
import itertools
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_demo2_sample_matched as sample_matched


OUT = SCRIPT_DIR
RESULTS_JSON = OUT / "ratio_sweep_results.json"
SUMMARY_CSV = OUT / "ratio_sweep_summary.csv"
LINES_PDF = OUT / "figure_ratio_sweep_lines.pdf"
LINES_PNG = OUT / "figure_ratio_sweep_lines.png"
HEATMAP_PDF = OUT / "figure_ratio_sweep_heatmap.pdf"
HEATMAP_PNG = OUT / "figure_ratio_sweep_heatmap.png"
REPORT = OUT / "demo2_ratio_sweep_report.md"
STEP2M_PURE_JSON = OUT / "sample_matched_pure_inhouse_results.json"
STEP2M_MIXED_JSON = OUT / "sample_matched_mixed_results.json"

RANDOM_STATE = 42
SUBSET_CAP = 200
LIT_VALUES = [0, 2, 4, 6, 8]
N_VALUES = [8, 12, 16, 20, 24]
FEATURES = sample_matched.FEATURES
CENTER_IDS = sample_matched.CENTER_IDS
BOUNDARY_TOLERANCE = 1e-6

LINE_STYLES = {
    0: {"color": "#0072B2", "linestyle": "-", "marker": "o"},
    2: {"color": "#56B4E9", "linestyle": "-.", "marker": "s"},
    4: {"color": "#E69F00", "linestyle": "--", "marker": "^"},
    6: {"color": "#F4A261", "linestyle": "-.", "marker": "v"},
    8: {"color": "#D55E00", "linestyle": "--", "marker": "D"},
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


def valid_inhouse_count(ih: int, n_non_center: int = 26, center_size: int = 3) -> int:
    return sample_matched.fewshot.comb_count(
        n_non_center, ih
    ) + sample_matched.fewshot.comb_count(n_non_center, ih - center_size)


def draw_valid_inhouse_subset(
    rng: np.random.Generator,
    non_center: tuple[int, ...],
    center: tuple[int, ...],
    ih: int,
) -> tuple[int, ...]:
    without_center = sample_matched.fewshot.comb_count(len(non_center), ih)
    with_center = sample_matched.fewshot.comb_count(
        len(non_center), ih - len(center)
    )
    total = without_center + with_center
    if total == 0:
        raise ValueError(f"No valid in-house subset for ih={ih}")

    use_center = with_center > 0 and bool(rng.random() < with_center / total)
    if use_center:
        extra = ih - len(center)
        picked = (
            tuple(sorted(rng.choice(non_center, size=extra, replace=False).tolist()))
            if extra
            else tuple()
        )
        return tuple(sorted(center + picked))
    return tuple(sorted(rng.choice(non_center, size=ih, replace=False).tolist()))


def enumerate_joint_subsets(
    literature_indices: tuple[int, ...],
    non_center: tuple[int, ...],
    center: tuple[int, ...],
    lit: int,
    ih: int,
) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    literature_subsets = list(itertools.combinations(literature_indices, lit))
    inhouse_subsets = sample_matched.fewshot.enumerate_valid_xiao_subsets(
        non_center, center, ih
    )
    return [
        (tuple(lit_subset), tuple(ih_subset))
        for lit_subset in literature_subsets
        for ih_subset in inhouse_subsets
    ]


def sample_joint_subsets(
    rng: np.random.Generator,
    literature_indices: tuple[int, ...],
    non_center: tuple[int, ...],
    center: tuple[int, ...],
    lit: int,
    ih: int,
    cap: int,
) -> tuple[list[tuple[tuple[int, ...], tuple[int, ...]]], int, bool]:
    literature_subsets = list(itertools.combinations(literature_indices, lit))
    total_valid = len(literature_subsets) * valid_inhouse_count(ih)
    if total_valid <= cap:
        return (
            enumerate_joint_subsets(
                literature_indices, non_center, center, lit, ih
            ),
            total_valid,
            True,
        )

    sampled: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    attempts = 0
    while len(sampled) < cap:
        attempts += 1
        if attempts > cap * 5000:
            raise RuntimeError(
                f"Could not draw {cap} unique joint subsets for lit={lit}, ih={ih}"
            )
        lit_subset = literature_subsets[int(rng.integers(0, len(literature_subsets)))]
        ih_subset = draw_valid_inhouse_subset(rng, non_center, center, ih)
        sampled.add((tuple(lit_subset), tuple(ih_subset)))
    return sorted(sampled), total_valid, False


def boundary_plans(
    xiao: pd.DataFrame,
) -> tuple[
    dict[int, list[tuple[tuple[int, ...], tuple[int, ...]]]],
    dict[int, list[tuple[tuple[int, ...], tuple[int, ...]]]],
]:
    pure_plan, _ = sample_matched.pure_subset_plan(xiao)
    mixed_plan, _ = sample_matched.mixed_subset_plan(xiao)
    all_literature = tuple(range(8))
    lit_zero = {
        n: [(tuple(), tuple(ih_subset)) for ih_subset in pure_plan[n]]
        for n in N_VALUES
    }
    lit_eight = {
        n: [(all_literature, tuple(ih_subset)) for ih_subset in mixed_plan[n]]
        for n in N_VALUES
    }
    return lit_zero, lit_eight


def make_grid_plan(
    xiao: pd.DataFrame,
    bolla: pd.DataFrame,
) -> tuple[dict[tuple[int, int], list[tuple[tuple[int, ...], tuple[int, ...]]]], dict]:
    center, non_center = sample_matched.center_indices(xiao)
    literature_indices = tuple(range(len(bolla)))
    lit_zero, lit_eight = boundary_plans(xiao)
    rng = np.random.default_rng(RANDOM_STATE)

    plan = {}
    audit = {}
    for lit in LIT_VALUES:
        for n in N_VALUES:
            ih = n - lit
            total_valid = math.comb(len(bolla), lit) * valid_inhouse_count(ih)
            if lit == 0:
                subsets = lit_zero[n]
                exhaustive = total_valid <= SUBSET_CAP
            elif lit == 8:
                subsets = lit_eight[n]
                exhaustive = total_valid <= SUBSET_CAP
            else:
                subsets, sampled_total, exhaustive = sample_joint_subsets(
                    rng,
                    literature_indices,
                    non_center,
                    center,
                    lit,
                    ih,
                    SUBSET_CAP,
                )
                if sampled_total != total_valid:
                    raise RuntimeError("Joint subset count mismatch")

            expected_used = total_valid if total_valid <= SUBSET_CAP else SUBSET_CAP
            if len(subsets) != expected_used:
                raise RuntimeError(
                    f"Unexpected subset count for lit={lit}, n={n}: "
                    f"{len(subsets)} vs {expected_used}"
                )
            if len(subsets) != len(set(subsets)):
                raise RuntimeError(f"Duplicate joint subsets for lit={lit}, n={n}")
            plan[(lit, n)] = subsets
            audit[f"({lit}, {n})"] = {
                "lit": lit,
                "ih": ih,
                "n": n,
                "total_valid_subsets_under_center_block_rule": int(total_valid),
                "n_used": int(len(subsets)),
                "n_skipped_by_cap": int(total_valid - len(subsets)),
                "exhaustive": bool(exhaustive),
                "selection": (
                    "all valid joint subsets"
                    if exhaustive
                    else "200 unique deterministic joint subsets"
                ),
            }
    return plan, audit


def run_subset(
    lit: int,
    n: int,
    subset_number: int,
    lit_indices: tuple[int, ...],
    ih_indices: tuple[int, ...],
    xiao: pd.DataFrame,
    bolla: pd.DataFrame,
) -> dict:
    ih = n - lit
    train_literature = bolla.iloc[list(lit_indices)].copy()
    train_inhouse = xiao.iloc[list(ih_indices)].copy()
    test_inhouse = xiao.drop(index=list(ih_indices)).reset_index(drop=True)
    train = pd.concat([train_literature, train_inhouse], ignore_index=True)

    if len(train_literature) != lit or len(train_inhouse) != ih or len(train) != n:
        raise RuntimeError(f"Training count mismatch for lit={lit}, n={n}")
    center_audit = sample_matched.assert_center_policy(
        train_inhouse, test_inhouse
    )
    predicted, _ = sample_matched.fit_predict(train, test_inhouse)
    actual = test_inhouse["log10_J"].to_numpy(dtype=float)
    metrics = sample_matched.metrics_from_arrays(actual, predicted)
    if metrics["R2_conv"] is None:
        raise RuntimeError(f"Undefined R2 for lit={lit}, n={n}")

    return {
        "subset_number": int(subset_number),
        "lit_subset": train_literature["record_id"].astype(str).tolist(),
        "ih_subset": train_inhouse["record_id"].astype(str).tolist(),
        "test_ids": test_inhouse["record_id"].astype(str).tolist(),
        "R2_conv": metrics["R2_conv"],
        "spearman": metrics["spearman_rho"],
        "pearson": metrics["pearson_r"],
        "rmse_logJ": metrics["rmse_logJ"],
        "within_2x": metrics["within_2x_fraction"],
        "within_2x_count": metrics["within_2x_count"],
        **center_audit,
    }


def mean_std(values: list[float | None]) -> tuple[float, float]:
    clean = np.asarray([float(value) for value in values if value is not None], dtype=float)
    if len(clean) != len(values):
        raise RuntimeError("Unexpected undefined metric in ratio sweep")
    return float(np.mean(clean)), float(np.std(clean, ddof=0))


def aggregate_cell(
    lit: int,
    n: int,
    records: list[dict],
    audit: dict,
) -> dict:
    ih = n - lit
    row = {
        "lit": lit,
        "ih": ih,
        "n": n,
        "n_subsets": len(records),
        "n_test": 29 - ih,
        "exhaustive": audit["exhaustive"],
        "total_valid_subsets": audit[
            "total_valid_subsets_under_center_block_rule"
        ],
    }
    for metric, prefix in [
        ("R2_conv", "R2_conv"),
        ("rmse_logJ", "RMSE_logJ"),
        ("spearman", "spearman"),
        ("pearson", "pearson"),
        ("within_2x", "within_2x"),
    ]:
        mean, std = mean_std([record[metric] for record in records])
        row[f"{prefix}_mean"] = mean
        row[f"{prefix}_std"] = std
    return row


def load_step2m_boundaries() -> tuple[dict, dict]:
    pure = json.loads(STEP2M_PURE_JSON.read_text(encoding="utf-8"))
    mixed = json.loads(STEP2M_MIXED_JSON.read_text(encoding="utf-8"))
    return pure, mixed


def validate_boundaries(
    cells: dict[str, dict],
    summary_rows: list[dict],
) -> dict:
    pure, mixed = load_step2m_boundaries()
    summary_lookup = {(row["lit"], row["n"]): row for row in summary_rows}
    checks = []
    differences = []

    for lit, source in [(0, pure), (8, mixed)]:
        source_summary = {int(row["m"]): row for row in source["summary"]}
        source_records_by_m = {
            m: [record for record in source["records"] if int(record["m"]) == m]
            for m in N_VALUES
        }
        for n in N_VALUES:
            new_row = summary_lookup[(lit, n)]
            old_row = source_summary[n]
            metric_map = {
                "R2_conv_mean": "R2_conv_mean",
                "R2_conv_std": "R2_conv_std",
                "RMSE_logJ_mean": "rmse_logJ_mean",
                "RMSE_logJ_std": "rmse_logJ_std",
                "spearman_mean": "spearman_rho_mean",
                "spearman_std": "spearman_rho_std",
                "within_2x_mean": "within_2x_fraction_mean",
                "within_2x_std": "within_2x_fraction_std",
            }
            cell_diffs = {
                new_name: abs(float(new_row[new_name]) - float(old_row[old_name]))
                for new_name, old_name in metric_map.items()
            }
            differences.extend(cell_diffs.values())

            new_records = cells[f"({lit}, {n})"]["subsets"]
            old_records = source_records_by_m[n]
            if lit == 0:
                subset_sequence_match = [
                    record["ih_subset"] for record in new_records
                ] == [record["xiao_train_record_ids"] for record in old_records]
            else:
                subset_sequence_match = (
                    [record["ih_subset"] for record in new_records]
                    == [record["xiao_train_record_ids"] for record in old_records]
                    and all(
                        len(record["lit_subset"]) == 8 for record in new_records
                    )
                )
            checks.append(
                {
                    "lit": lit,
                    "n": n,
                    "status": (
                        "PASS"
                        if max(cell_diffs.values()) <= BOUNDARY_TOLERANCE
                        and subset_sequence_match
                        else "FAIL"
                    ),
                    "subset_sequence_exact_match": subset_sequence_match,
                    "metric_absolute_differences": cell_diffs,
                    "maximum_metric_difference": max(cell_diffs.values()),
                }
            )

    worst = max(differences)
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {
        "status": status,
        "tolerance": BOUNDARY_TOLERANCE,
        "worst_case_metric_difference": worst,
        "checks": checks,
    }


def write_summary_csv(rows: list[dict]) -> None:
    columns = [
        "lit",
        "ih",
        "n",
        "n_subsets",
        "R2_conv_mean",
        "R2_conv_std",
        "RMSE_logJ_mean",
        "RMSE_logJ_std",
        "spearman_mean",
        "spearman_std",
        "within_2x_mean",
        "within_2x_std",
        "n_test",
        "exhaustive",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            output = {}
            for column in columns:
                value = row[column]
                output[column] = f"{value:.12f}" if isinstance(value, float) else value
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
            "legend.fontsize": 7.2,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def make_line_figure(rows: list[dict]) -> None:
    configure_matplotlib()
    lookup = {(row["lit"], row["n"]): row for row in rows}
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.65, 3.75),
        gridspec_kw={"wspace": 0.34},
        constrained_layout=False,
    )

    for lit in LIT_VALUES:
        style = LINE_STYLES[lit]
        r2 = [lookup[(lit, n)]["R2_conv_mean"] for n in N_VALUES]
        r2_std = [lookup[(lit, n)]["R2_conv_std"] for n in N_VALUES]
        rho = [lookup[(lit, n)]["spearman_mean"] for n in N_VALUES]
        rho_std = [lookup[(lit, n)]["spearman_std"] for n in N_VALUES]
        common = {
            "color": style["color"],
            "linestyle": style["linestyle"],
            "marker": style["marker"],
            "markersize": 4.2,
            "linewidth": 1.05,
            "capsize": 2,
            "label": f"lit={lit}",
        }
        axes[0].errorbar(N_VALUES, r2, yerr=r2_std, **common)
        axes[1].errorbar(N_VALUES, rho, yerr=rho_std, **common)

    axes[0].axhline(0, color="#222222", linewidth=0.8, linestyle=(0, (3, 3)))
    axes[1].axhline(0, color="#222222", linewidth=0.8, linestyle=(0, (3, 3)))
    axes[0].set_title(
        "A  R$^2_{conv}$ across literature/in-house mixing ratios",
        loc="left",
        fontweight="bold",
        pad=7,
    )
    axes[1].set_title(
        "B  Spearman $\\rho$ across mixing ratios",
        loc="left",
        fontweight="bold",
        pad=7,
    )
    axes[0].set_ylabel("Mean R$^2_{conv}$")
    axes[1].set_ylabel("Mean Spearman $\\rho$")
    for axis in axes:
        axis.set_xlabel("Total training size, n")
        axis.set_xticks(N_VALUES)
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.45)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.tick_params(direction="out", length=3, width=0.8)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.90),
        ncol=5,
        frameon=False,
        columnspacing=1.4,
        handlelength=2.1,
    )
    fig.suptitle(
        "Configuration-ratio sweep: does any lit/ih mix outperform pure in-house?",
        fontsize=10,
        fontweight="bold",
        y=0.985,
    )
    fig.subplots_adjust(left=0.078, right=0.985, bottom=0.17, top=0.76)
    fig.savefig(
        LINES_PDF,
        metadata={"Creator": "SkinMiner", "CreationDate": None, "ModDate": None},
    )
    fig.savefig(LINES_PNG, dpi=450, metadata={"Software": "SkinMiner"})
    plt.close(fig)


def make_heatmap(rows: list[dict]) -> None:
    configure_matplotlib()
    lookup = {(row["lit"], row["n"]): row for row in rows}
    means = np.array(
        [
            [lookup[(lit, n)]["R2_conv_mean"] for n in N_VALUES]
            for lit in LIT_VALUES
        ],
        dtype=float,
    )
    stds = np.array(
        [
            [lookup[(lit, n)]["R2_conv_std"] for n in N_VALUES]
            for lit in LIT_VALUES
        ],
        dtype=float,
    )

    fig, ax = plt.subplots(figsize=(6.45, 4.25), constrained_layout=False)
    norm = Normalize(vmin=float(np.min(means)), vmax=0.0)
    image = ax.imshow(
        means,
        origin="lower",
        aspect="auto",
        cmap="viridis",
        norm=norm,
    )
    for row_index, lit in enumerate(LIT_VALUES):
        for column_index, n in enumerate(N_VALUES):
            mean = means[row_index, column_index]
            std = stds[row_index, column_index]
            rgba = image.cmap(image.norm(mean))
            luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
            color = "black" if luminance > 0.58 else "white"
            ax.text(
                column_index,
                row_index + 0.08,
                f"{mean:.2f}",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                color=color,
            )
            ax.text(
                column_index,
                row_index - 0.18,
                f"+/- {std:.2f}",
                ha="center",
                va="center",
                fontsize=6.3,
                color=color,
            )

    ax.set_xticks(np.arange(len(N_VALUES)))
    ax.set_xticklabels(N_VALUES)
    ax.set_yticks(np.arange(len(LIT_VALUES)))
    ax.set_yticklabels(LIT_VALUES)
    ax.set_xlabel("Total training size, n")
    ax.set_ylabel("Literature records in training, lit")
    ax.set_title(
        "Configuration-ratio R$^2_{conv}$ landscape",
        fontweight="bold",
        pad=9,
    )
    ax.set_xticks(np.arange(-0.5, len(N_VALUES), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(LIT_VALUES), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Mean R$^2_{conv}$")
    colorbar.ax.axhline(0, color="#222222", linewidth=1.0)
    fig.subplots_adjust(left=0.14, right=0.90, bottom=0.14, top=0.88)
    fig.savefig(
        HEATMAP_PDF,
        metadata={"Creator": "SkinMiner", "CreationDate": None, "ModDate": None},
    )
    fig.savefig(HEATMAP_PNG, dpi=450, metadata={"Software": "SkinMiner"})
    plt.close(fig)


def format_pm(mean: float, std: float) -> str:
    return f"{mean:.3f} +/- {std:.3f}"


def analyse_grid(rows: list[dict]) -> dict:
    lookup = {(row["lit"], row["n"]): row for row in rows}
    cross_sections = []
    all_monotonic_nonincreasing = True
    any_lit_mean_win = False
    any_lit_one_sd_win = False
    best_nonzero_improvement = None

    for n in N_VALUES:
        ordered = [lookup[(lit, n)] for lit in LIT_VALUES]
        means = [row["R2_conv_mean"] for row in ordered]
        best_index = int(np.argmax(means))
        best = ordered[best_index]
        pure = ordered[0]
        adjacent = []
        for previous, current in zip(ordered[:-1], ordered[1:]):
            change = current["R2_conv_mean"] - previous["R2_conv_mean"]
            adjacent.append(
                {
                    "from_lit": previous["lit"],
                    "to_lit": current["lit"],
                    "R2_change": change,
                    "change_per_added_literature_record": change / 2.0,
                    "sign": "positive" if change > 0 else "negative" if change < 0 else "zero",
                }
            )
        monotonic = all(change["R2_change"] <= 0 for change in adjacent)
        all_monotonic_nonincreasing = all_monotonic_nonincreasing and monotonic

        nonzero_comparisons = []
        for candidate in ordered[1:]:
            improvement = candidate["R2_conv_mean"] - pure["R2_conv_mean"]
            combined_sd = math.sqrt(
                candidate["R2_conv_std"] ** 2 + pure["R2_conv_std"] ** 2
            )
            mean_win = improvement > 0
            one_sd_win = mean_win and improvement >= combined_sd
            any_lit_mean_win = any_lit_mean_win or mean_win
            any_lit_one_sd_win = any_lit_one_sd_win or one_sd_win
            comparison = {
                "lit": candidate["lit"],
                "improvement_over_lit0": improvement,
                "combined_one_sd": combined_sd,
                "mean_higher_than_lit0": mean_win,
                "higher_by_at_least_combined_1SD": one_sd_win,
            }
            nonzero_comparisons.append(comparison)
            if mean_win and (
                best_nonzero_improvement is None
                or improvement > best_nonzero_improvement["improvement_over_lit0"]
            ):
                best_nonzero_improvement = {"n": n, **comparison}

        cross_sections.append(
            {
                "n": n,
                "best_lit": best["lit"],
                "best_ih": best["ih"],
                "best_R2_conv_mean": best["R2_conv_mean"],
                "lit0_R2_conv_mean": pure["R2_conv_mean"],
                "lit0_is_highest": best["lit"] == 0,
                "monotonic_nonincreasing_with_lit": monotonic,
                "ranking_best_to_worst": [
                    row["lit"]
                    for row in sorted(
                        ordered, key=lambda item: item["R2_conv_mean"], reverse=True
                    )
                ],
                "adjacent_marginal_changes": adjacent,
                "nonzero_lit_vs_lit0": nonzero_comparisons,
            }
        )

    lit0_highest_every_n = all(section["lit0_is_highest"] for section in cross_sections)
    if lit0_highest_every_n and all_monotonic_nonincreasing:
        scenario = 1
        scenario_text = (
            "Scenario 1: lit=0 is highest at every n and mean R2_conv decreases "
            "monotonically as literature replaces in-house records."
        )
    elif any_lit_mean_win:
        scenario = 2
        scenario_text = (
            "Scenario 2: at least one lit>0 cell has higher mean R2_conv than "
            "its lit=0 counterpart, indicating a possible literature sweet spot."
        )
    else:
        scenario = 3
        scenario_text = (
            "Scenario 3 (weak non-monotonicity): lit=0 remains highest, but at least "
            "one adjacent intermediate-literature step reverses direction."
        )

    return {
        "cross_sections": cross_sections,
        "lit0_highest_every_n": lit0_highest_every_n,
        "all_n_monotonic_nonincreasing_with_lit": all_monotonic_nonincreasing,
        "any_lit_gt0_mean_outperforms_lit0": any_lit_mean_win,
        "any_lit_gt0_outperforms_lit0_by_combined_1SD": any_lit_one_sd_win,
        "best_nonzero_lit_improvement": best_nonzero_improvement,
        "scenario": scenario,
        "scenario_text": scenario_text,
    }


def make_report(
    rows: list[dict],
    boundary: dict,
    analysis: dict,
    audit: dict,
) -> None:
    lookup = {(row["lit"], row["n"]): row for row in rows}
    lines = [
        "# Demo 2 Step 2n: Configuration-Ratio Sweep",
        "",
        "## 1. Setup and Sanity Checks",
        "",
        "The 5 x 5 grid spans literature counts `lit={0,2,4,6,8}` and matched total training sizes `n={8,12,16,20,24}`, with `ih=n-lit`. Every model uses the unchanged 4-feature bridge, log10(J), StandardScaler fitted on training rows only, and Ridge(alpha=1.0). Evaluation is always on held-out in-house records.",
        "",
        "BBD4/BBD5/BBD6 were treated as one indivisible center-point block in every in-house subset. Effective valid-subset counts therefore use `C(26, ih) + C(26, ih-3)` rather than treating all 29 in-house rows as independent choices. Leakage guard: PASS.",
        "",
        f"Boundary tolerance: {boundary['tolerance']:.1e}. All ten Step 2m boundary cells passed; worst-case aggregate metric difference={boundary['worst_case_metric_difference']:.3e}. The lit=0 cells exactly reproduce Configuration A subset sequences and the lit=8 cells exactly reproduce Configuration B subset sequences.",
        "",
        f"Total retained subset fits: {sum(row['n_subsets'] for row in rows)} across 25 cells. Only `(lit=8, n=8)` is exhaustive with one possible subset; every other cell uses 200 deterministic unique subsets.",
        "",
        "## 2. Full 25-Cell Summary",
        "",
        "| lit | ih | n | R2_conv mean +/- std | Spearman rho mean +/- std | n_test | n_subsets |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['lit']} | {row['ih']} | {row['n']} | "
            f"{format_pm(row['R2_conv_mean'], row['R2_conv_std'])} | "
            f"{format_pm(row['spearman_mean'], row['spearman_std'])} | "
            f"{row['n_test']} | {row['n_subsets']} |"
        )

    lines += [
        "",
        "## 3. Per-n Cross-Sections",
        "",
    ]
    for section in analysis["cross_sections"]:
        n = section["n"]
        best = lookup[(section["best_lit"], n)]
        rankings = " > ".join(f"lit={lit}" for lit in section["ranking_best_to_worst"])
        strong = [
            comparison["lit"]
            for comparison in section["nonzero_lit_vs_lit0"]
            if comparison["higher_by_at_least_combined_1SD"]
        ]
        mean_wins = [
            comparison["lit"]
            for comparison in section["nonzero_lit_vs_lit0"]
            if comparison["mean_higher_than_lit0"]
        ]
        lines += [
            f"### n={n}",
            "",
            f"Best mean R2_conv: lit={best['lit']}, ih={best['ih']}, {best['R2_conv_mean']:.3f}. Ranking: {rankings}.",
            "",
            f"Monotonic non-increasing as lit rises: {'yes' if section['monotonic_nonincreasing_with_lit'] else 'no'}. Literature-positive mean cells versus lit=0: {', '.join('lit=' + str(value) for value in mean_wins) if mean_wins else 'none'}. Cells exceeding lit=0 by at least one combined SD: {', '.join('lit=' + str(value) for value in strong) if strong else 'none'}.",
            "",
        ]

    lines += [
        "## 4. Marginal Value of Literature",
        "",
        "Each value below is the change in mean R2_conv per added literature record over an adjacent two-record step. Positive values improve R2_conv; negative values worsen it.",
        "",
        "| n | lit 0->2 | lit 2->4 | lit 4->6 | lit 6->8 | classification |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for section in analysis["cross_sections"]:
        changes = [
            item["change_per_added_literature_record"]
            for item in section["adjacent_marginal_changes"]
        ]
        if all(value < 0 for value in changes):
            classification = "negative throughout"
        elif any(value > 0 for value in changes):
            classification = "mixed / non-monotonic"
        else:
            classification = "zero or negative"
        lines.append(
            f"| {section['n']} | "
            + " | ".join(f"{value:+.3f}" for value in changes)
            + f" | {classification} |"
        )

    lines += [
        "",
        "## 5. Direct Answer: Can Literature Reduce In-House Experiments?",
        "",
    ]
    if analysis["any_lit_gt0_mean_outperforms_lit0"]:
        best = analysis["best_nonzero_lit_improvement"]
        lines += [
            f"Yes at the mean level: the strongest nonzero-literature improvement occurs at n={best['n']}, lit={best['lit']}, with delta R2_conv={best['improvement_over_lit0']:+.3f} relative to lit=0.",
            "",
            f"Improvement separated by at least one combined SD: {'yes' if analysis['any_lit_gt0_outperforms_lit0_by_combined_1SD'] else 'no'}. This changes the simple uniformly-negative framing and suggests a ratio-dependent effect.",
        ]
    else:
        lines += [
            "No. Across all 25 cells, no lit>0 configuration exceeds the corresponding lit=0 mean R2_conv. Pure in-house training is highest at every n, so literature data does not reduce the required in-house experiments for this pair under this protocol.",
        ]

    lines += [
        "",
        "## 6. Outcome Scenario",
        "",
        f"**{analysis['scenario_text']}**",
        "",
    ]
    if analysis["scenario"] == 1:
        conclusion = (
            "The grid strengthens the bounded negative-value conclusion: replacing "
            "in-house records with literature records progressively worsens prediction."
        )
    elif analysis["scenario"] == 2:
        conclusion = (
            "The grid identifies a ratio-dependent sweet spot and the Demo 2 message "
            "must be revised away from uniformly negative literature value."
        )
    else:
        positive_adjacent = [
            (section["n"], change)
            for section in analysis["cross_sections"]
            for change in section["adjacent_marginal_changes"]
            if change["R2_change"] > 0
        ]
        strongest = max(
            positive_adjacent,
            key=lambda item: item[1]["R2_change"],
        )
        reversal_n, reversal = strongest
        reversal_from = lookup[(reversal["from_lit"], reversal_n)]
        reversal_to = lookup[(reversal["to_lit"], reversal_n)]
        pure_at_reversal = lookup[(0, reversal_n)]
        conclusion = (
            "The grid is technically non-monotonic without a literature cell beating pure "
            f"in-house. The largest positive adjacent reversal is n={reversal_n}, "
            f"lit={reversal['from_lit']}->{reversal['to_lit']} "
            f"(delta R2_conv={reversal['R2_change']:+.3f}); this is far smaller than the "
            f"cell standard deviations ({reversal_from['R2_conv_std']:.3f} and "
            f"{reversal_to['R2_conv_std']:.3f}) and the destination remains "
            f"{abs(reversal_to['R2_conv_mean'] - pure_at_reversal['R2_conv_mean']):.3f} "
            "R2 units below lit=0. It is not evidence of a positive literature sweet spot, but it prevents "
            "a literal claim that every adjacent literature increment monotonically worsens "
            "the mean."
        )
    lines += [
        conclusion,
        "",
        "This judgement is bounded to the Xiao-Bolla pair, the four-feature bridge, log10(J), and Ridge(alpha=1.0). It does not generalize to literature data as a whole.",
        "",
        "## Outputs",
        "",
        "- `ratio_sweep_results.json`",
        "- `ratio_sweep_summary.csv`",
        "- `figure_ratio_sweep_lines.pdf` and `.png`",
        "- `figure_ratio_sweep_heatmap.pdf` and `.png`",
        "- `run_demo2_ratio_sweep.py`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    xiao, bolla = sample_matched.fewshot.build_inputs()
    if len(xiao) != 29 or len(bolla) != 8:
        raise ValueError(f"Expected Xiao=29 and Bolla=8, got {len(xiao)} and {len(bolla)}")

    plan, audit = make_grid_plan(xiao, bolla)
    cells: dict[str, dict] = {}
    summary_rows = []
    for lit in LIT_VALUES:
        for n in N_VALUES:
            key = f"({lit}, {n})"
            subsets = [
                run_subset(
                    lit,
                    n,
                    subset_number,
                    lit_indices,
                    ih_indices,
                    xiao,
                    bolla,
                )
                for subset_number, (lit_indices, ih_indices) in enumerate(
                    plan[(lit, n)], start=1
                )
            ]
            cell_summary = aggregate_cell(lit, n, subsets, audit[key])
            summary_rows.append(cell_summary)
            cells[key] = {
                "lit": lit,
                "ih": n - lit,
                "n": n,
                "n_subsets": len(subsets),
                "exhaustive": audit[key]["exhaustive"],
                "n_test": 29 - (n - lit),
                "total_valid_subsets": audit[key][
                    "total_valid_subsets_under_center_block_rule"
                ],
                "summary": cell_summary,
                "subsets": subsets,
            }

    boundary = validate_boundaries(cells, summary_rows)
    if boundary["status"] != "PASS":
        raise RuntimeError(
            f"Step 2m boundary reproduction failed: {json.dumps(boundary, indent=2)}"
        )
    analysis = analyse_grid(summary_rows)
    payload = {
        "metadata": {
            "analysis": "5x5 literature/in-house configuration-ratio sweep",
            "features": FEATURES,
            "model": "StandardScaler fit on training rows only + Ridge(alpha=1.0)",
            "target": "log10(J)",
            "random_state": RANDOM_STATE,
            "subset_cap": SUBSET_CAP,
            "lit_values": LIT_VALUES,
            "n_values": N_VALUES,
            "center_group_record_ids": list(CENTER_IDS),
            "center_group_policy": "BBD4/BBD5/BBD6 are an indivisible block.",
            "test_scope": "held-out in-house records only",
        },
        "boundary_sanity_checks": boundary,
        "subset_sampling_audit": audit,
        "analysis": analysis,
        "leakage_guard": {
            "status": "PASS",
            "n_violations": 0,
            "subsets_checked": int(sum(row["n_subsets"] for row in summary_rows)),
        },
        **cells,
    }

    write_json(RESULTS_JSON, payload)
    write_summary_csv(summary_rows)
    make_line_figure(summary_rows)
    make_heatmap(summary_rows)
    make_report(summary_rows, boundary, analysis, audit)

    print("[DEMO2 RATIO SWEEP] Done")
    print(f"Cells: {len(summary_rows)}")
    print(f"Subset fits: {sum(row['n_subsets'] for row in summary_rows)}")
    print(
        f"Boundary sanity: {boundary['status']} "
        f"worst_diff={boundary['worst_case_metric_difference']:.3e}"
    )
    print(f"Outcome: Scenario {analysis['scenario']}")
    print(analysis["scenario_text"])
    print(f"Results: {RESULTS_JSON}")
    print(f"Summary: {SUMMARY_CSV}")
    print(f"Line figure: {LINES_PDF}")
    print(f"Line figure: {LINES_PNG}")
    print(f"Heatmap: {HEATMAP_PDF}")
    print(f"Heatmap: {HEATMAP_PNG}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
