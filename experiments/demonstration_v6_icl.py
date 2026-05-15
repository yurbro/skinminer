from __future__ import annotations

import json
import math
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.metrics import mean_absolute_error, r2_score


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DATA = ROOT / "outputs" / "demonstration_v3" / "source_paper_data.csv"
V5_METRICS = ROOT / "outputs" / "demonstration_v5" / "global_metrics.json"
OUTPUT_DIR = ROOT / "outputs" / "demonstration_v6"
FIGURE_DIR = OUTPUT_DIR / "figures"
RAW_DIR = OUTPUT_DIR / "raw_responses"

TEMPERATURE = 0.3
MAX_TOKENS = 200
REPEATS = 3
GPR_BASELINE_R2 = 0.5998318667370934

MODELS = [
    {"provider": "openai", "model": "gpt-4o-mini", "label": "GPT-4o-mini"},
    {"provider": "anthropic", "model": "claude-sonnet-4-6", "label": "Claude Sonnet 4.6"},
]
CONDITIONS = ["no_context", "general_context", "icl", "permuted_icl"]
CONDITION_LABELS = {
    "no_context": "No context",
    "general_context": "General",
    "icl": "ICL",
    "permuted_icl": "Permuted ICL",
}
TIMEPOINTS = [24, 48, 72]

# Pricing fallback, USD per 1M tokens. Updated in report when verified manually.
PRICE_PER_MTOK = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
}

COLORS = {
    "blue": "#2B6C8A",
    "orange": "#C97931",
    "green": "#3D7C59",
    "red": "#B94B48",
    "gray": "#9AA3AD",
    "dark_gray": "#56616F",
    "light_gray": "#E9EDF2",
}
TIME_COLORS = {24: "#7FB3D5", 48: "#2B6C8A", 72: "#164A64"}


@dataclass(frozen=True)
class LLMResult:
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    provider: str
    model: str


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.06,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def load_formulation_records() -> pd.DataFrame:
    data = pd.read_csv(SOURCE_DATA)
    rows: list[dict[str, float | str]] = []
    for formulation, group in data.groupby("formulation_label"):
        first = group.iloc[0]
        row: dict[str, float | str] = {
            "formulation_label": formulation,
            "particle_size_nm": float(first["particle_size_nm"]),
            "vit_e_tpgs_pct_wv": float(first["vit_e_tpgs_pct_wv"]),
            "hpmc_k100_pct_wv": float(first["hpmc_k100_pct_wv"]),
        }
        for time_h in TIMEPOINTS:
            item = group[group["time_h"] == time_h].iloc[0]
            row[f"val_{time_h}h"] = float(item["cum_amount_ug_cm2"])
            row[f"sd_{time_h}h"] = float(item["cum_amount_sd_ug_cm2"])
        rows.append(row)
    return pd.DataFrame(rows).sort_values("formulation_label").reset_index(drop=True)


def formulation_line(row: pd.Series, letter: str | None = None) -> str:
    name = f"Formulation {letter}" if letter else "Formulation"
    return (
        f"{name}: PS={row['particle_size_nm']:.0f} nm, "
        f"TPGS={row['vit_e_tpgs_pct_wv']:.1f}% w/v, HPMC={row['hpmc_k100_pct_wv']:.1f}% w/v\n"
        f"  24h: {row['val_24h']:.0f} ± {row['sd_24h']:.0f}, "
        f"48h: {row['val_48h']:.0f} ± {row['sd_48h']:.0f}, "
        f"72h: {row['val_72h']:.0f} ± {row['sd_72h']:.0f}"
    )


def general_background() -> str:
    return """Background: Ibuprofen nanosuspensions for transdermal delivery typically show cumulative permeation in the range of 100-2000 µg/cm² across 24-72 hours on porcine skin via Franz cell. Key formulation factors include:
- Particle size: smaller particles generally enhance permeation
- Vit E TPGS (surfactant): aids drug dissolution and skin permeation enhancement
- HPMC K100 (polymer): affects viscosity and release kinetics"""


def query_block(query: pd.Series) -> str:
    return f"""Predict cumulative ibuprofen permeation (in µg/cm²) at 24h, 48h, and 72h through porcine skin (Franz cell, finite dose) for a formulation with:
- Particle size: {query['particle_size_nm']:.0f} nm
- Vit E TPGS: {query['vit_e_tpgs_pct_wv']:.1f}% w/v
- HPMC K100: {query['hpmc_k100_pct_wv']:.1f}% w/v

Respond ONLY with valid JSON. The first character of your response must be "{{".
Do not explain, do not show calculations, and do not include markdown.
JSON schema: {{"24h": <float>, "48h": <float>, "72h": <float>}}"""


def build_prompt(condition: str, examples: pd.DataFrame, query: pd.Series) -> str:
    if condition == "no_context":
        return "You are an expert in pharmaceutical formulation science.\n\n" + query_block(query)

    if condition == "general_context":
        return "You are an expert in pharmaceutical formulation science.\n\n" + general_background() + "\n\n" + query_block(query)

    if condition in {"icl", "permuted_icl"}:
        letters = "ABCDEFG"
        example_lines = [
            formulation_line(row, letters[idx])
            for idx, (_, row) in enumerate(examples.reset_index(drop=True).iterrows())
        ]
        return (
            "You are an expert in pharmaceutical formulation science.\n\n"
            + general_background()
            + "\n\nReference data from related ibuprofen nanosuspension formulations "
            + "(cumulative permeation in µg/cm², mean ± SD across replicates):\n\n"
            + "\n\n".join(example_lines)
            + "\n\nPredict cumulative ibuprofen permeation for a new formulation with:\n"
            + f"- Particle size: {query['particle_size_nm']:.0f} nm\n"
            + f"- Vit E TPGS: {query['vit_e_tpgs_pct_wv']:.1f}% w/v\n"
            + f"- HPMC K100: {query['hpmc_k100_pct_wv']:.1f}% w/v\n\n"
            + 'Respond ONLY with valid JSON. The first character of your response must be "{".\n'
            + "Do not explain, do not show calculations, and do not include markdown.\n"
            + 'JSON schema: {"24h": <float>, "48h": <float>, "72h": <float>}'
        )
    raise ValueError(f"Unknown condition: {condition}")


def permute_examples(held_in: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    perm_idx = rng.permutation(len(held_in))
    shuffled = held_in.copy().reset_index(drop=True)
    y_cols = [f"val_{time_h}h" for time_h in TIMEPOINTS]
    shuffled[y_cols] = held_in.reset_index(drop=True)[y_cols].to_numpy()[perm_idx]
    return shuffled


def parse_llm_response(text: str) -> dict[str, float] | None:
    cleaned = text.strip()
    for candidate in [cleaned, *re.findall(r"\{[^{}]+\}", cleaned, flags=re.DOTALL)]:
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        values: dict[str, float] = {}
        for time_h in TIMEPOINTS:
            found = None
            for key in [f"{time_h}h", str(time_h), f"{time_h}.0h", f"{time_h} h"]:
                if key in parsed:
                    found = parsed[key]
                    break
            if found is None:
                return None
            try:
                values[f"{time_h}h"] = float(found)
            except Exception:
                return None
        return values
    return None


def raw_path(model: str, fold: str, condition: str, repeat: int) -> Path:
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model)
    return RAW_DIR / f"{safe_model}_{fold}_{condition}_{repeat}.json"


def usage_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICE_PER_MTOK.get(model, {"input": 0.0, "output": 0.0})
    return (input_tokens / 1_000_000.0) * price["input"] + (output_tokens / 1_000_000.0) * price["output"]


def call_openai(prompt: str, model: str, seed: int | None) -> LLMResult:
    from openai import OpenAI

    client = OpenAI()
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    if seed is not None:
        kwargs["seed"] = seed
    response = client.chat.completions.create(**kwargs)
    text = response.choices[0].message.content or ""
    usage = response.usage
    input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", input_tokens + output_tokens) or (input_tokens + output_tokens))
    return LLMResult(text, input_tokens, output_tokens, total_tokens, "openai", model)


def call_anthropic(prompt: str, model: str, seed: int | None) -> LLMResult:
    from anthropic import Anthropic

    _ = seed  # Anthropic Messages API does not expose a compatible seed parameter.
    client = Anthropic()
    tool_name = "emit_prediction"
    response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        tools=[
            {
                "name": tool_name,
                "description": "Emit only the requested permeation prediction values.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "24h": {"type": "number"},
                        "48h": {"type": "number"},
                        "72h": {"type": "number"},
                    },
                    "required": ["24h", "48h", "72h"],
                    "additionalProperties": False,
                },
            }
        ],
        tool_choice={"type": "tool", "name": tool_name},
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    parsed_tool: dict[str, Any] | None = None
    text_parts: list[str] = []
    for block in response.content:
        if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == tool_name:
            parsed_tool = getattr(block, "input", None)
        elif getattr(block, "type", "") == "text":
            text_parts.append(getattr(block, "text", ""))
    text = json.dumps(parsed_tool, ensure_ascii=False) if parsed_tool is not None else "\n".join(text_parts)
    usage = response.usage
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    return LLMResult(text, input_tokens, output_tokens, input_tokens + output_tokens, "anthropic", model)


def call_llm(provider: str, model: str, prompt: str, seed: int, raw_file: Path) -> dict[str, Any]:
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    if raw_file.exists():
        return json.loads(raw_file.read_text(encoding="utf-8"))

    attempts = []
    for attempt in range(3):
        attempt_seed = seed + attempt * 10_000
        try:
            if provider == "openai":
                result = call_openai(prompt, model, attempt_seed)
            elif provider == "anthropic":
                result = call_anthropic(prompt, model, attempt_seed)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            parsed = parse_llm_response(result.text)
            attempts.append(
                {
                    "attempt": attempt,
                    "text": result.text,
                    "parsed": parsed,
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                    "total_tokens": result.total_tokens,
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
            time.sleep(1.5 * (attempt + 1))

    final = next((item for item in reversed(attempts) if item["parsed"] is not None), attempts[-1])
    payload = {
        "provider": provider,
        "model": model,
        "parsed_success": final["parsed"] is not None,
        "parsed": final["parsed"],
        "raw_response": final["text"],
        "attempts": attempts,
        "input_tokens": sum(int(item["input_tokens"]) for item in attempts),
        "output_tokens": sum(int(item["output_tokens"]) for item in attempts),
        "total_tokens": sum(int(item["total_tokens"]) for item in attempts),
        "error": final.get("error"),
    }
    payload["cost_usd_estimate"] = usage_cost(model, payload["input_tokens"], payload["output_tokens"])
    raw_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def run_experiment() -> tuple[pd.DataFrame, pd.DataFrame]:
    formulations = load_formulation_records()
    detail_rows: list[dict[str, Any]] = []
    call_rows: list[dict[str, Any]] = []
    total_calls = len(MODELS) * len(formulations) * len(CONDITIONS) * REPEATS
    completed = 0

    for model_info in MODELS:
        provider = model_info["provider"]
        model = model_info["model"]
        model_label = model_info["label"]
        for fold_idx, held_out in formulations.iterrows():
            held_in = formulations.drop(index=fold_idx).reset_index(drop=True)
            fold = str(held_out["formulation_label"])
            for condition in CONDITIONS:
                for repeat in range(REPEATS):
                    seed = fold_idx * 100 + repeat
                    examples = permute_examples(held_in, seed) if condition == "permuted_icl" else held_in
                    prompt = build_prompt(condition, examples, held_out)
                    path = raw_path(model, fold, condition, repeat)
                    payload = call_llm(provider, model, prompt, seed, path)
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
                            "raw_response_path": str(path),
                            "error": payload.get("error"),
                        }
                    )
                    for time_h in TIMEPOINTS:
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
                                "raw_response_path": str(path),
                                "parsed_success": bool(payload.get("parsed_success")),
                            }
                        )
                    completed += 1
                    if completed % 12 == 0 or completed == total_calls:
                        print(f"Completed calls: {completed}/{total_calls}")
    return pd.DataFrame(detail_rows), pd.DataFrame(call_rows)


def summary_metrics(predictions: pd.DataFrame, call_log: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model in [item["model"] for item in MODELS]:
        for condition in CONDITIONS:
            subset = predictions[(predictions["model"] == model) & (predictions["condition"] == condition)]
            agg = (
                subset.groupby(["fold", "timepoint_h"], as_index=False)
                .agg(true_value=("true_value", "first"), pred_value=("pred_value", "mean"))
                .sort_values(["fold", "timepoint_h"])
            )
            valid = agg["pred_value"].notna()
            true_values = agg.loc[valid, "true_value"].to_numpy(dtype=float)
            pred_values = agg.loc[valid, "pred_value"].to_numpy(dtype=float)
            calls = call_log[(call_log["model"] == model) & (call_log["condition"] == condition)]
            rows.append(
                {
                    "model": model,
                    "model_label": calls["model_label"].iloc[0] if len(calls) else model,
                    "condition": condition,
                    "condition_label": CONDITION_LABELS[condition],
                    "R2": float(r2_score(true_values, pred_values)) if len(true_values) >= 2 else math.nan,
                    "RMSE": float(np.sqrt(np.mean(np.square(true_values - pred_values)))) if len(true_values) else math.nan,
                    "MAE": float(mean_absolute_error(true_values, pred_values)) if len(true_values) else math.nan,
                    "n_valid": int(valid.sum()),
                    "n_failed_parse": int((~valid).sum()),
                    "parse_fail_calls": int((~calls["parsed_success"]).sum()) if len(calls) else 0,
                    "input_tokens": int(calls["input_tokens"].sum()) if len(calls) else 0,
                    "output_tokens": int(calls["output_tokens"].sum()) if len(calls) else 0,
                    "total_tokens": int(calls["total_tokens"].sum()) if len(calls) else 0,
                    "cost_usd_estimate": float(calls["cost_usd_estimate"].sum()) if len(calls) else 0.0,
                }
            )
    return pd.DataFrame(rows)


def repeat_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, condition, repeat), subset in predictions.groupby(["model", "condition", "repeat"]):
        valid = subset["pred_value"].notna()
        true_values = subset.loc[valid, "true_value"].to_numpy(dtype=float)
        pred_values = subset.loc[valid, "pred_value"].to_numpy(dtype=float)
        rows.append(
            {
                "model": model,
                "condition": condition,
                "repeat": repeat,
                "R2": float(r2_score(true_values, pred_values)) if len(true_values) >= 2 else math.nan,
                "RMSE": float(np.sqrt(np.mean(np.square(true_values - pred_values)))) if len(true_values) else math.nan,
                "MAE": float(mean_absolute_error(true_values, pred_values)) if len(true_values) else math.nan,
                "n_valid": int(valid.sum()),
            }
        )
    return pd.DataFrame(rows)


def per_formulation_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    averaged = (
        predictions.groupby(["model", "model_label", "condition", "fold", "timepoint_h"], as_index=False)
        .agg(true_value=("true_value", "first"), pred_value=("pred_value", "mean"))
        .sort_values(["model", "condition", "fold", "timepoint_h"])
    )
    for (model, model_label, condition, fold), subset in averaged.groupby(["model", "model_label", "condition", "fold"]):
        valid = subset["pred_value"].notna()
        true_values = subset.loc[valid, "true_value"].to_numpy(dtype=float)
        pred_values = subset.loc[valid, "pred_value"].to_numpy(dtype=float)
        rows.append(
            {
                "model": model,
                "model_label": model_label,
                "condition": condition,
                "fold": fold,
                "R2": float(r2_score(true_values, pred_values)) if len(true_values) >= 2 else math.nan,
                "RMSE": float(np.sqrt(np.mean(np.square(true_values - pred_values)))) if len(true_values) else math.nan,
                "MAE": float(mean_absolute_error(true_values, pred_values)) if len(true_values) else math.nan,
                "n_valid": int(valid.sum()),
            }
        )
    return pd.DataFrame(rows)


def permutation_tests(per_form: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model in [item["model"] for item in MODELS]:
        icl = (
            per_form[(per_form["model"] == model) & (per_form["condition"] == "icl")]
            .set_index("fold")
            .sort_index()["MAE"]
        )
        perm = (
            per_form[(per_form["model"] == model) & (per_form["condition"] == "permuted_icl")]
            .set_index("fold")
            .sort_index()["MAE"]
        )
        common = sorted(set(icl.index).intersection(perm.index))
        try:
            stat, pval = wilcoxon(icl.loc[common], perm.loc[common], zero_method="wilcox", alternative="less")
        except Exception:
            stat, pval = math.nan, math.nan
        rows.append(
            {
                "model": model,
                "model_label": per_form[per_form["model"] == model]["model_label"].iloc[0],
                "test": "ICL MAE < permuted ICL MAE",
                "wilcoxon_statistic": float(stat) if not math.isnan(stat) else math.nan,
                "p_value": float(pval) if not math.isnan(pval) else math.nan,
                "icl_mean_fold_mae": float(icl.loc[common].mean()),
                "permuted_icl_mean_fold_mae": float(perm.loc[common].mean()),
                "n_folds": len(common),
            }
        )
    return pd.DataFrame(rows)


def plot_main_comparison(summary: pd.DataFrame, repeats: pd.DataFrame, permutation: pd.DataFrame) -> None:
    condition_order = CONDITIONS
    x = np.arange(len(condition_order))
    width = 0.35
    fig, ax = plt.subplots(figsize=(6.1, 3.4))
    for idx, model_info in enumerate(MODELS):
        model = model_info["model"]
        subset = summary[summary["model"] == model].set_index("condition").loc[condition_order]
        rep_subset = repeats[repeats["model"] == model]
        yerr = [
            rep_subset[rep_subset["condition"] == condition]["R2"].std(ddof=1)
            for condition in condition_order
        ]
        offset = (idx - 0.5) * width
        ax.bar(
            x + offset,
            subset["R2"],
            yerr=yerr,
            capsize=2,
            width=width,
            color=COLORS["blue"] if idx == 0 else COLORS["orange"],
            label=model_info["label"],
        )
        pval = permutation[permutation["model"] == model]["p_value"].iloc[0]
        ax.text(
            x[2] + offset,
            max(subset.loc["icl", "R2"], subset.loc["permuted_icl", "R2"]) + 0.08,
            f"p={pval:.3f}" if not math.isnan(pval) else "p=NA",
            ha="center",
            va="bottom",
            fontsize=7,
            color=COLORS["dark_gray"],
        )
    ax.axhline(GPR_BASELINE_R2, ls="--", lw=0.9, color=COLORS["red"])
    ax.text(len(condition_order) - 0.35, GPR_BASELINE_R2 + 0.025, "V5 GPR R² = 0.60", ha="right", fontsize=8, color=COLORS["red"])
    ax.set_xticks(x, [CONDITION_LABELS[item] for item in condition_order], rotation=20, ha="right")
    ax.set_ylabel("R² (LOFO)")
    ax.set_title("ICL prediction performance")
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURE_DIR / "fig_icl_main_comparison.png")
    fig.savefig(FIGURE_DIR / "fig_icl_main_comparison.pdf")
    plt.close(fig)


def plot_best_parity(summary: pd.DataFrame, predictions: pd.DataFrame) -> tuple[str, str]:
    best = summary.sort_values("R2", ascending=False).iloc[0]
    model = best["model"]
    condition = best["condition"]
    averaged = (
        predictions[(predictions["model"] == model) & (predictions["condition"] == condition)]
        .groupby(["fold", "timepoint_h"], as_index=False)
        .agg(true_value=("true_value", "first"), pred_value=("pred_value", "mean"))
        .sort_values(["fold", "timepoint_h"])
    )
    fig, ax = plt.subplots(figsize=(3.8, 3.5))
    axis_max = max(float(averaged["true_value"].max()), float(averaged["pred_value"].max())) * 1.08
    ax.plot([0, axis_max], [0, axis_max], ls="--", lw=0.8, color=COLORS["dark_gray"])
    for time_h, group in averaged.groupby("timepoint_h"):
        ax.scatter(
            group["true_value"],
            group["pred_value"],
            s=24,
            color=TIME_COLORS[int(time_h)],
            edgecolor="white",
            linewidth=0.4,
            label=f"{int(time_h)} h",
        )
    ax.text(
        0.96,
        0.04,
        f"{best['model_label']}\n{best['condition_label']}\nR²={best['R2']:.2f}\nRMSE={best['RMSE']:.0f} µg/cm²\nMAE={best['MAE']:.0f} µg/cm²",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": COLORS["light_gray"], "lw": 0.6},
    )
    ax.set_xlim(0, axis_max)
    ax.set_ylim(0, axis_max)
    ax.set_xlabel("True cumulative permeation (µg/cm²)")
    ax.set_ylabel("LLM predicted (µg/cm²)")
    ax.set_title("Best ICL parity plot")
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(FIGURE_DIR / "fig_icl_best_parity.png")
    fig.savefig(FIGURE_DIR / "fig_icl_best_parity.pdf")
    plt.close(fig)
    return str(model), str(condition)


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
    planned_calls = len(call_log)
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
    ]
    report = f"""# Demonstration v6: In-Context Learning for Permeation Prediction

## Experiment Summary

This experiment evaluates whether SkinMiner-extracted structured records can serve as in-context examples for numerical LLM prediction. This is in-context learning (ICL), not retrieval-augmented generation (RAG). A true RAG system over the full SkinMiner corpus remains future work.

- Data: 8 formulations x 3 timepoints from `10.1208/s12249-013-9995-4`.
- Cross-validation: leave-one-formulation-out.
- Models: GPT-4o-mini and Claude Sonnet 4.6.
- Conditions: no context, general context, ICL, and permuted ICL.
- Repeats: {REPEATS} per model x condition x fold.
- Planned calls completed/logged: {planned_calls}/192.
- Parse failure calls: {parse_fail_calls}; failure rate: {parse_fail_calls / planned_calls * 100:.1f}%.
- Estimated total cost: ${total_cost:.4f} using configured per-token prices.

## Summary Metrics

{markdown_table(summary_display, list(summary_display.columns), 3)}

## Permutation Validation

{markdown_table(permutation_display, list(permutation_display.columns), 3)}

The permutation control tests whether LLMs use the structured examples rather than relying only on generic priors. If ICL is not better than permuted ICL, the evidence for true example use is weak.

## Best Condition

Best condition by R2: `{best['model_label']}` with `{best['condition_label']}`.

- R2: {best['R2']:.3f}
- RMSE: {best['RMSE']:.1f} µg/cm²
- MAE: {best['MAE']:.1f} µg/cm²
- V5 GPR baseline R2: {GPR_BASELINE_R2:.3f}

## Per-Formulation Breakdown

{markdown_table(per_form[['model_label', 'condition', 'fold', 'R2', 'RMSE', 'MAE', 'n_valid']], ['model_label', 'condition', 'fold', 'R2', 'RMSE', 'MAE', 'n_valid'], 3)}

## Failure Analysis

Parse failures are counted at the LLM-call level and at the 24-point evaluation level. Raw responses are saved under `raw_responses/` for audit. Numerical predictions outside plausible monotonic permeation trends were not post-corrected; this is intentional to evaluate raw ICL behaviour.

## Honest Judgment

This is a small, single-paper ICL experiment. It does not prove that LLMs have learned formulation science, and it should not be described as RAG. The key diagnostic is ICL versus permuted ICL. If the best ICL condition does not clearly exceed permuted ICL for the same model, the structured examples did not provide strong usable signal. If it does, the result supports a narrower claim: SkinMiner records can be used as structured demonstrations that improve LLM numerical predictions in a constrained, single-paper setting.
"""
    (OUTPUT_DIR / "icl_results.md").write_text(report, encoding="utf-8")


def write_paper_section(summary: pd.DataFrame, permutation: pd.DataFrame) -> None:
    best = summary.sort_values("R2", ascending=False).iloc[0]
    model_perm = permutation[permutation["model"] == best["model"]].iloc[0]
    text = f"""## Application: LLM-Driven In-Context Prediction

To complement the Gaussian process regression demonstration, we evaluated whether SkinMiner-extracted records can be used directly as structured in-context examples for LLM-driven numerical prediction. Using the same ibuprofen nanosuspension data set, we performed leave-one-formulation-out evaluation across four prompt conditions: no context, general domain context, in-context learning with the other seven formulations, and a permuted in-context control in which formulation factors were paired with incorrect permeation profiles. GPT-4o-mini and Claude Sonnet 4.6 were each evaluated with three repeats per fold.

The best condition was {best['model_label']} with {best['condition_label']}, reaching R2 = {best['R2']:.2f}, RMSE = {best['RMSE']:.0f} µg/cm², and MAE = {best['MAE']:.0f} µg/cm². The corresponding V5 GPR baseline achieved R2 = {GPR_BASELINE_R2:.2f}. The permutation diagnostic for this model gave p = {model_perm['p_value']:.3f} for ICL MAE being lower than permuted ICL MAE. This comparison is essential: improvement over no-context prompting alone is not sufficient to show that the LLM used the examples, whereas improvement over permuted examples indicates that the structured SkinMiner records supplied usable formulation-response signal.

This experiment should be interpreted as ICL, not RAG. It is based on one paper, a small formulation set, and two mainstream models. The result therefore supports a limited downstream-utility claim: SkinMiner outputs can provide structured demonstrations for LLM scientific reasoning in a constrained setting. Full retrieval-augmented modelling over the SkinMiner corpus remains future work.
"""
    (OUTPUT_DIR / "paper_section_draft.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    configure_style()
    predictions, call_log = run_experiment()
    predictions.to_csv(OUTPUT_DIR / "icl_predictions.csv", index=False)
    call_log.to_csv(OUTPUT_DIR / "llm_call_log.csv", index=False)

    summary = summary_metrics(predictions, call_log)
    repeats = repeat_metrics(predictions)
    per_form = per_formulation_metrics(predictions)
    permutation = permutation_tests(per_form)

    summary.to_csv(OUTPUT_DIR / "icl_summary_metrics.csv", index=False)
    repeats.to_csv(OUTPUT_DIR / "icl_repeat_metrics.csv", index=False)
    per_form.to_csv(OUTPUT_DIR / "icl_per_formulation.csv", index=False)
    permutation.to_csv(OUTPUT_DIR / "permutation_validation.csv", index=False)

    plot_main_comparison(summary, repeats, permutation)
    best_model, best_condition = plot_best_parity(summary, predictions)
    write_report(summary, per_form, permutation, call_log, best_model, best_condition)
    write_paper_section(summary, permutation)

    print("Demonstration v6 complete")
    print(summary[["model_label", "condition_label", "R2", "RMSE", "MAE", "n_valid", "parse_fail_calls"]].to_string(index=False))
    print(permutation[["model_label", "p_value", "icl_mean_fold_mae", "permuted_icl_mean_fold_mae"]].to_string(index=False))
    print(f"Estimated cost USD: {call_log['cost_usd_estimate'].sum():.4f}")
    print(f"Outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
