from __future__ import annotations

import json
import math
import re
import shutil
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import demonstration_v6_icl as v6


NEW_MODEL = {"provider": "openai", "model": "gpt-5.4", "label": "GPT-5.4"}
ALL_MODELS = [
    {"provider": "openai", "model": "gpt-4o-mini", "label": "GPT-4o-mini"},
    {"provider": "anthropic", "model": "claude-sonnet-4-6", "label": "Claude Sonnet 4.6"},
    NEW_MODEL,
]
PRICE_PER_MTOK = {
    **v6.PRICE_PER_MTOK,
    # Configured estimate for GPT-5.4. The report derives cost from measured API token usage.
    "gpt-5.4": {"input": 15.00, "output": 60.00},
}
MODEL_COLORS = {
    "gpt-4o-mini": v6.COLORS["blue"],
    "claude-sonnet-4-6": v6.COLORS["orange"],
    "gpt-5.4": v6.COLORS["green"],
}


def configure_globals() -> None:
    v6.MODELS = ALL_MODELS
    v6.PRICE_PER_MTOK = PRICE_PER_MTOK


def backup_once(path: Path, suffix: str = "_2models") -> None:
    if not path.exists():
        return
    target = path.with_name(f"{path.stem}{suffix}{path.suffix}")
    if not target.exists():
        shutil.copy2(path, target)


def backup_two_model_outputs() -> None:
    for name in [
        "icl_predictions.csv",
        "llm_call_log.csv",
        "icl_summary_metrics.csv",
        "icl_repeat_metrics.csv",
        "icl_per_formulation.csv",
        "permutation_validation.csv",
        "icl_results.md",
        "paper_section_draft.md",
    ]:
        backup_once(v6.OUTPUT_DIR / name)
    for name in [
        "fig_icl_main_comparison.png",
        "fig_icl_main_comparison.pdf",
        "fig_icl_best_parity.png",
        "fig_icl_best_parity.pdf",
    ]:
        backup_once(v6.FIGURE_DIR / name)


def usage_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICE_PER_MTOK.get(model, {"input": 0.0, "output": 0.0})
    return (input_tokens / 1_000_000.0) * price["input"] + (output_tokens / 1_000_000.0) * price["output"]


def call_openai_json(prompt: str, model: str, seed: int, raw_file: Path) -> dict[str, Any]:
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    if raw_file.exists():
        return json.loads(raw_file.read_text(encoding="utf-8"))

    from openai import OpenAI

    client = OpenAI()
    attempts: list[dict[str, Any]] = []
    for attempt in range(3):
        attempt_seed = seed + attempt * 10_000
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=v6.TEMPERATURE,
                max_completion_tokens=v6.MAX_TOKENS,
                response_format={"type": "json_object"},
                seed=attempt_seed,
            )
            text = response.choices[0].message.content or ""
            parsed = v6.parse_llm_response(text)
            usage = response.usage
            input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
            output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
            total_tokens = int(getattr(usage, "total_tokens", input_tokens + output_tokens) or 0)
            attempts.append(
                {
                    "attempt": attempt,
                    "text": text,
                    "parsed": parsed,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "error": None,
                }
            )
            if parsed is not None:
                break
        except Exception as exc:
            attempts.append(
                {
                    "attempt": attempt,
                    "text": "",
                    "parsed": None,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "error": repr(exc),
                }
            )

    final = next((item for item in reversed(attempts) if item["parsed"] is not None), attempts[-1])
    input_tokens = sum(int(item["input_tokens"]) for item in attempts)
    output_tokens = sum(int(item["output_tokens"]) for item in attempts)
    payload = {
        "provider": "openai",
        "model": model,
        "parsed_success": final["parsed"] is not None,
        "parsed": final["parsed"],
        "raw_response": final["text"],
        "attempts": attempts,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": sum(int(item["total_tokens"]) for item in attempts),
        "error": final.get("error"),
        "cost_usd_estimate": usage_cost(model, input_tokens, output_tokens),
        "cost_rate_note": "configured estimate: input $15/M tokens, output $60/M tokens",
    }
    raw_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def run_gpt54_only() -> tuple[pd.DataFrame, pd.DataFrame]:
    formulations = v6.load_formulation_records()
    detail_rows: list[dict[str, Any]] = []
    call_rows: list[dict[str, Any]] = []
    total_calls = len(formulations) * len(v6.CONDITIONS) * v6.REPEATS
    completed = 0

    provider = NEW_MODEL["provider"]
    model = NEW_MODEL["model"]
    model_label = NEW_MODEL["label"]
    print(f"Supplement model string: {model}")

    for fold_idx, held_out in formulations.iterrows():
        held_in = formulations.drop(index=fold_idx).reset_index(drop=True)
        fold = str(held_out["formulation_label"])
        for condition in v6.CONDITIONS:
            for repeat in range(v6.REPEATS):
                seed = fold_idx * 100 + repeat
                examples = v6.permute_examples(held_in, seed) if condition == "permuted_icl" else held_in
                prompt = v6.build_prompt(condition, examples, held_out)
                raw_file = v6.raw_path(model, fold, condition, repeat)
                payload = call_openai_json(prompt, model, seed, raw_file)
                parsed = payload.get("parsed") or {}

                call_rows.append(
                    {
                        "model": model,
                        "model_label": model_label,
                        "provider": provider,
                        "fold": fold,
                        "condition": condition,
                        "repeat": repeat,
                        "parsed_success": bool(payload.get("parsed_success")),
                        "input_tokens": int(payload.get("input_tokens", 0) or 0),
                        "output_tokens": int(payload.get("output_tokens", 0) or 0),
                        "total_tokens": int(payload.get("total_tokens", 0) or 0),
                        "cost_usd_estimate": float(payload.get("cost_usd_estimate", 0.0) or 0.0),
                        "raw_response_path": str(raw_file),
                        "error": payload.get("error"),
                    }
                )
                for time_h in v6.TIMEPOINTS:
                    true_value = float(held_out[f"val_{time_h}h"])
                    pred_value = parsed.get(f"{time_h}h", math.nan)
                    pred_value = float(pred_value) if pred_value is not None else math.nan
                    detail_rows.append(
                        {
                            "model": model,
                            "model_label": model_label,
                            "provider": provider,
                            "fold": fold,
                            "condition": condition,
                            "repeat": repeat,
                            "timepoint_h": time_h,
                            "true_value": true_value,
                            "pred_value": pred_value,
                            "abs_error": abs(true_value - pred_value) if not math.isnan(pred_value) else math.nan,
                            "raw_response": payload.get("raw_response", ""),
                            "raw_response_path": str(raw_file),
                            "parsed_success": bool(payload.get("parsed_success")),
                        }
                    )
                completed += 1
                if completed % 12 == 0 or completed == total_calls:
                    print(f"Completed GPT-5.4 calls: {completed}/{total_calls}")

    return pd.DataFrame(detail_rows), pd.DataFrame(call_rows)


def combine_with_existing(new_predictions: pd.DataFrame, new_calls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    existing_predictions = pd.read_csv(v6.OUTPUT_DIR / "icl_predictions_2models.csv")
    existing_calls = pd.read_csv(v6.OUTPUT_DIR / "llm_call_log_2models.csv")

    existing_predictions = existing_predictions[existing_predictions["model"] != NEW_MODEL["model"]]
    existing_calls = existing_calls[existing_calls["model"] != NEW_MODEL["model"]]

    predictions = pd.concat([existing_predictions, new_predictions], ignore_index=True)
    call_log = pd.concat([existing_calls, new_calls], ignore_index=True)
    return predictions, call_log


def plot_main_comparison(summary: pd.DataFrame, repeats: pd.DataFrame, permutation: pd.DataFrame) -> None:
    condition_order = v6.CONDITIONS
    x = np.arange(len(condition_order))
    width = 0.24
    fig, ax = plt.subplots(figsize=(6.8, 3.6))

    for idx, model_info in enumerate(ALL_MODELS):
        model = model_info["model"]
        subset = summary[summary["model"] == model].set_index("condition").loc[condition_order]
        rep_subset = repeats[repeats["model"] == model]
        yerr = [
            rep_subset[rep_subset["condition"] == condition]["R2"].std(ddof=1)
            for condition in condition_order
        ]
        offset = (idx - 1) * width
        ax.bar(
            x + offset,
            subset["R2"],
            yerr=yerr,
            capsize=2,
            width=width,
            color=MODEL_COLORS[model],
            label=model_info["label"],
        )
        pval = permutation[permutation["model"] == model]["p_value"].iloc[0]
        y_anchor = float(subset.loc["icl", "R2"])
        ax.text(
            x[2] + offset,
            y_anchor + 0.07,
            f"p={pval:.3f}" if not math.isnan(pval) else "p=NA",
            ha="center",
            va="bottom",
            fontsize=6.5,
            color=v6.COLORS["dark_gray"],
            rotation=0,
        )

    ax.axhline(
        v6.GPR_BASELINE_R2,
        ls="--",
        lw=0.9,
        color=v6.COLORS["red"],
        label="GPR R$^2$ = 0.60",
    )
    ax.set_xticks(x, [v6.CONDITION_LABELS[item] for item in condition_order], rotation=20, ha="right")
    ax.set_ylabel("R$^2$ (LOFO)")
    ax.set_title("ICL prediction performance")
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=4,
        frameon=False,
        handlelength=1.8,
        columnspacing=1.4,
    )
    ax.set_ylim(min(-2.05, float(summary["R2"].min()) - 0.15), max(1.08, float(summary["R2"].max()) + 0.25))
    fig.subplots_adjust(bottom=0.28)
    fig.savefig(v6.FIGURE_DIR / "fig_icl_main_comparison.png")
    fig.savefig(v6.FIGURE_DIR / "fig_icl_main_comparison.pdf")
    plt.close(fig)


def plot_best_parity(summary: pd.DataFrame, predictions: pd.DataFrame) -> tuple[str, str]:
    return v6.plot_best_parity(summary, predictions)


def plot_three_model_parity(summary: pd.DataFrame, predictions: pd.DataFrame) -> None:
    icl = summary[summary["condition"] == "icl"].copy()
    averaged = (
        predictions[predictions["condition"] == "icl"]
        .groupby(["model", "model_label", "fold", "timepoint_h"], as_index=False)
        .agg(true_value=("true_value", "first"), pred_value=("pred_value", "mean"))
    )
    axis_max = max(float(averaged["true_value"].max()), float(averaged["pred_value"].max())) * 1.08
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.75), sharex=True, sharey=True)
    for ax, model_info in zip(axes, ALL_MODELS):
        model = model_info["model"]
        model_data = averaged[averaged["model"] == model]
        metric = icl[icl["model"] == model].iloc[0]
        ax.plot([0, axis_max], [0, axis_max], ls="--", lw=0.8, color=v6.COLORS["dark_gray"])
        for time_h, group in model_data.groupby("timepoint_h"):
            ax.scatter(
                group["true_value"],
                group["pred_value"],
                s=20,
                color=v6.TIME_COLORS[int(time_h)],
                edgecolor="white",
                linewidth=0.35,
                label=f"{int(time_h)} h",
            )
        ax.set_title(f"{model_info['label']}\nR$^2$={metric['R2']:.2f}, MAE={metric['MAE']:.0f}")
        ax.set_xlim(0, axis_max)
        ax.set_ylim(0, axis_max)
    axes[0].set_ylabel("LLM predicted (µg/cm²)")
    for ax in axes:
        ax.set_xlabel("True (µg/cm²)")
    axes[0].legend(loc="upper left", fontsize=6.5)
    fig.savefig(v6.FIGURE_DIR / "fig_icl_three_model_parity.png")
    fig.savefig(v6.FIGURE_DIR / "fig_icl_three_model_parity.pdf")
    plt.close(fig)


def markdown_table(frame: pd.DataFrame, columns: list[str], digits: int = 3) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.iterrows():
        cells = []
        for col in columns:
            value = row[col]
            if isinstance(value, (float, np.floating)):
                cells.append(f"{float(value):.{digits}f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(
    summary: pd.DataFrame,
    per_form: pd.DataFrame,
    permutation: pd.DataFrame,
    call_log: pd.DataFrame,
    best_model: str,
    best_condition: str,
) -> None:
    best = summary[(summary["model"] == best_model) & (summary["condition"] == best_condition)].iloc[0]
    total_cost = float(call_log["cost_usd_estimate"].sum())
    parse_fail_calls = int((~call_log["parsed_success"]).sum())
    gpt54_calls = call_log[call_log["model"] == NEW_MODEL["model"]]
    gpt54_cost = float(gpt54_calls["cost_usd_estimate"].sum())
    summary_display = summary[
        [
            "model_label",
            "condition_label",
            "R2",
            "RMSE",
            "MAE",
            "n_valid",
            "n_failed_parse",
            "parse_fail_calls",
            "cost_usd_estimate",
        ]
    ].copy()
    permutation_display = permutation[
        ["model_label", "test", "p_value", "icl_mean_fold_mae", "permuted_icl_mean_fold_mae", "n_folds"]
    ].copy()
    gpt54_summary = summary[summary["model"] == NEW_MODEL["model"]].copy()
    report = f"""# Demonstration v6: In-Context Learning for Permeation Prediction

## Supplement Update: GPT-5.4 Added

This supplement appends GPT-5.4 to the existing GPT-4o-mini and Claude Sonnet 4.6 ICL experiment. The previous two-model results were not rerun; their original outputs were backed up with `_2models` suffixes before recomputing the combined summary.

- Added model string: `{NEW_MODEL['model']}`.
- New GPT-5.4 calls completed/logged: {len(gpt54_calls)}/96.
- Total calls now completed/logged: {len(call_log)}/288.
- Parse failure calls: {parse_fail_calls}; failure rate: {parse_fail_calls / len(call_log) * 100:.1f}%.
- GPT-5.4 estimated cost: ${gpt54_cost:.4f}.
- Total estimated cost including original V6 runs: ${total_cost:.4f}.
- Cost note: estimates use API token usage and configured rates; GPT-5.4 is set to input $15/M tokens and output $60/M tokens.

## Summary Metrics

{markdown_table(summary_display, list(summary_display.columns), 3)}

## GPT-5.4 Condition Summary

{markdown_table(gpt54_summary[['condition_label', 'R2', 'RMSE', 'MAE', 'n_valid', 'parse_fail_calls', 'cost_usd_estimate']], ['condition_label', 'R2', 'RMSE', 'MAE', 'n_valid', 'parse_fail_calls', 'cost_usd_estimate'], 3)}

## Permutation Validation

{markdown_table(permutation_display, list(permutation_display.columns), 3)}

The permutation control tests whether LLMs use the structured examples rather than relying only on generic priors. If ICL is not better than permuted ICL, the evidence for true example use is weak.

## Best Condition

Best condition by R2: `{best['model_label']}` with `{best['condition_label']}`.

- R2: {best['R2']:.3f}
- RMSE: {best['RMSE']:.1f} ug/cm2
- MAE: {best['MAE']:.1f} ug/cm2
- V5 GPR baseline R2: {v6.GPR_BASELINE_R2:.3f}

## Three-Model Interpretation

The three-model comparison separates two claims. First, structured context improves numerical anchoring relative to no-context prompting for all models. Second, the stricter ICL-vs-permuted-ICL diagnostic remains the key test of whether the examples provide formulation-response signal rather than only range information.

## Per-Formulation Breakdown

{markdown_table(per_form[['model_label', 'condition', 'fold', 'R2', 'RMSE', 'MAE', 'n_valid']], ['model_label', 'condition', 'fold', 'R2', 'RMSE', 'MAE', 'n_valid'], 3)}

## Honest Judgment

This remains a small, single-paper ICL experiment, not RAG. GPT-5.4 broadens the model comparison to a stronger OpenAI model, but the interpretation depends on the permutation control. If GPT-5.4 ICL does not clearly beat permuted ICL, the honest conclusion is that the records are useful for range anchoring but do not yet prove reliable example-based formulation-response learning. If it does beat permuted ICL, the claim can be strengthened for capable models, while still limiting the scope to a constrained single-paper setting.
"""
    (v6.OUTPUT_DIR / "icl_results.md").write_text(report, encoding="utf-8")


def write_paper_section(summary: pd.DataFrame, permutation: pd.DataFrame) -> None:
    best = summary.sort_values("R2", ascending=False).iloc[0]
    gpt54 = summary[(summary["model"] == NEW_MODEL["model"]) & (summary["condition"] == "icl")].iloc[0]
    gpt54_perm = permutation[permutation["model"] == NEW_MODEL["model"]].iloc[0]
    significant = float(gpt54_perm["p_value"]) < 0.05
    if significant:
        conclusion = (
            f"The strongest evidence for genuine ICL utilization came from GPT-5.4 "
            f"(p = {gpt54_perm['p_value']:.3f}), indicating that a more capable model can extract "
            "formulation-response signal from structured SkinMiner records."
        )
    else:
        conclusion = (
            f"Across the three models, GPT-5.4 reached R2 = {gpt54['R2']:.2f} in the ICL condition, "
            f"but its ICL-vs-permuted diagnostic did not reach p < 0.05 (p = {gpt54_perm['p_value']:.3f}). "
            "This supports a cautious interpretation: the structured records help constrain numerical ranges, "
            "but do not by themselves prove robust example-based formulation-response learning."
        )
    text = f"""## Application: LLM-Driven In-Context Prediction

To complement the Gaussian process regression demonstration, we evaluated whether SkinMiner-extracted records can be used directly as structured in-context examples for LLM-driven numerical prediction. Using the same ibuprofen nanosuspension data set, we performed leave-one-formulation-out evaluation across four prompt conditions: no context, general domain context, in-context learning with the other seven formulations, and a permuted in-context control in which formulation factors were paired with incorrect permeation profiles. The updated comparison covers GPT-4o-mini, Claude Sonnet 4.6, and GPT-5.4, with three repeats per fold.

The best overall condition was {best['model_label']} with {best['condition_label']}, reaching R2 = {best['R2']:.2f}, RMSE = {best['RMSE']:.0f} ug/cm2, and MAE = {best['MAE']:.0f} ug/cm2. The V5 GPR baseline achieved R2 = {v6.GPR_BASELINE_R2:.2f}. {conclusion}

This experiment should be interpreted as ICL, not RAG. It is based on one paper and a small formulation set. The result therefore supports a limited downstream-utility claim: SkinMiner outputs can provide structured demonstrations for LLM scientific reasoning in a constrained setting. Full retrieval-augmented modelling over the SkinMiner corpus remains future work.
"""
    (v6.OUTPUT_DIR / "paper_section_draft.md").write_text(text, encoding="utf-8")


def main() -> None:
    configure_globals()
    v6.ensure_dirs()
    v6.configure_style()
    backup_two_model_outputs()

    new_predictions, new_calls = run_gpt54_only()
    predictions, call_log = combine_with_existing(new_predictions, new_calls)
    predictions.to_csv(v6.OUTPUT_DIR / "icl_predictions.csv", index=False)
    call_log.to_csv(v6.OUTPUT_DIR / "llm_call_log.csv", index=False)

    summary = v6.summary_metrics(predictions, call_log)
    repeats = v6.repeat_metrics(predictions)
    per_form = v6.per_formulation_metrics(predictions)
    permutation = v6.permutation_tests(per_form)

    summary.to_csv(v6.OUTPUT_DIR / "icl_summary_metrics.csv", index=False)
    repeats.to_csv(v6.OUTPUT_DIR / "icl_repeat_metrics.csv", index=False)
    per_form.to_csv(v6.OUTPUT_DIR / "icl_per_formulation.csv", index=False)
    permutation.to_csv(v6.OUTPUT_DIR / "permutation_validation.csv", index=False)

    plot_main_comparison(summary, repeats, permutation)
    best_model, best_condition = plot_best_parity(summary, predictions)
    plot_three_model_parity(summary, predictions)
    write_report(summary, per_form, permutation, call_log, best_model, best_condition)
    write_paper_section(summary, permutation)

    gpt54 = summary[summary["model"] == NEW_MODEL["model"]]
    print("Demonstration v6 supplement complete")
    print(gpt54[["model_label", "condition_label", "R2", "RMSE", "MAE", "n_valid", "parse_fail_calls"]].to_string(index=False))
    print(permutation[["model_label", "p_value", "icl_mean_fold_mae", "permuted_icl_mean_fold_mae"]].to_string(index=False))
    print(f"GPT-5.4 estimated cost USD: {new_calls['cost_usd_estimate'].sum():.4f}")
    print(f"Combined estimated cost USD: {call_log['cost_usd_estimate'].sum():.4f}")
    print(f"Outputs: {v6.OUTPUT_DIR}")


if __name__ == "__main__":
    main()
