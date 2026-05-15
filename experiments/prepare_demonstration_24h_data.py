from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs/demonstration"
PAPER1_XLSX = Path(
    r"C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\ReviewerToCodex\codex-3\paper1.xlsx"
)
LITERATURE_FULL = OUTPUT_DIR / "literature_permeation_data_full.csv"

TIME_COLUMNS = ["t1", "t2", "t3", "t4", "t6", "t8", "t22", "t24", "t26", "t28"]
RAW_COLUMNS = [
    "formulation_id",
    "replicate",
    "poloxamer_407_pct",
    "ethanol_pct",
    "propylene_glycol_pct",
    *TIME_COLUMNS,
]


def parse_time_label(value: object) -> tuple[str, int]:
    match = re.fullmatch(r"\s*(Cf\d+)_(\d+)\s*", str(value))
    if not match:
        raise ValueError(f"Unexpected Paper 1 row label: {value!r}")
    return match.group(1), int(match.group(2))


def parse_api_concentration_pct(row: pd.Series) -> float | None:
    value = pd.to_numeric(row.get("api_concentration_value"), errors="coerce")
    if not np.isfinite(value):
        return None
    unit = str(row.get("api_concentration_unit") or "").strip().lower()
    basis = str(row.get("api_basis") or "").strip().lower()
    if "%" in unit or unit in {"percent", "pct"}:
        return float(value)
    if unit.replace(" ", "") in {"mg/ml", "mgmL".lower()} and "w/v" in basis.replace(" ", ""):
        return float(value) / 10.0
    return None


def prepare_paper1() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not PAPER1_XLSX.exists():
        raise FileNotFoundError(f"Paper 1 Excel file not found: {PAPER1_XLSX}")

    df = pd.read_excel(PAPER1_XLSX, sheet_name=0)
    required = {"Time", "Poloxamer 407", "Ethanol", "Propyene glycol", *TIME_COLUMNS}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Paper 1 Excel is missing required columns: {sorted(missing)}")

    parsed = df["Time"].apply(parse_time_label)
    raw = pd.DataFrame(
        {
            "formulation_id": [item[0] for item in parsed],
            "replicate": [item[1] for item in parsed],
            "poloxamer_407_pct": pd.to_numeric(df["Poloxamer 407"], errors="coerce"),
            "ethanol_pct": pd.to_numeric(df["Ethanol"], errors="coerce"),
            "propylene_glycol_pct": pd.to_numeric(df["Propyene glycol"], errors="coerce"),
        }
    )
    for column in TIME_COLUMNS:
        raw[column] = pd.to_numeric(df[column], errors="coerce")

    raw = raw[RAW_COLUMNS].sort_values(["formulation_id", "replicate"]).reset_index(drop=True)
    if raw[RAW_COLUMNS[2:]].isna().any().any():
        raise ValueError("Paper 1 data contain non-numeric values in numeric columns.")

    replicate_counts = raw.groupby("formulation_id")["replicate"].nunique()
    if raw["formulation_id"].nunique() != 20 or not (replicate_counts == 5).all():
        raise ValueError(
            "Paper 1 data are expected to contain 20 formulations with 5 replicates each; "
            f"found {raw['formulation_id'].nunique()} formulations and replicate counts "
            f"{replicate_counts.to_dict()}."
        )

    all_replicates = raw[
        [
            "formulation_id",
            "replicate",
            "poloxamer_407_pct",
            "ethanol_pct",
            "propylene_glycol_pct",
            "t24",
        ]
    ].rename(columns={"t24": "cumulative_amount_24h_ug_cm2"})

    mean_24h = (
        all_replicates.groupby(
            ["formulation_id", "poloxamer_407_pct", "ethanol_pct", "propylene_glycol_pct"],
            as_index=False,
        )
        .agg(cumulative_amount_24h_ug_cm2=("cumulative_amount_24h_ug_cm2", "mean"))
        .sort_values("formulation_id")
        .reset_index(drop=True)
    )
    mean_24h["data_source"] = "self_generated"
    return raw, mean_24h, all_replicates


def prepare_literature(self_range: tuple[float, float]) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    if not LITERATURE_FULL.exists():
        raise FileNotFoundError(f"Literature full CSV not found: {LITERATURE_FULL}")

    full = pd.read_csv(LITERATURE_FULL)
    full["endpoint_time_h"] = pd.to_numeric(full["endpoint_time"], errors="coerce")
    full["normalized_value_ug_cm2_num"] = pd.to_numeric(full["normalized_value_ug_cm2"], errors="coerce")
    near_24h = full[(full["endpoint_time_h"] >= 23.0) & (full["endpoint_time_h"] <= 25.0)].copy()

    sort_columns = [column for column in ["record_id", "source_baseline", "policy_level"] if column in near_24h.columns]
    canonical = near_24h.sort_values(sort_columns).drop_duplicates("record_id", keep="first").copy()
    canonical["api_concentration_pct"] = canonical.apply(parse_api_concentration_pct, axis=1)

    literature_24h = pd.DataFrame(
        {
            "doi": canonical["doi"],
            "formulation_label": canonical["formulation_label"],
            "membrane_type": canonical["membrane_type"],
            "membrane_source": canonical["membrane_source"],
            "cumulative_amount_24h_ug_cm2": canonical["normalized_value_ug_cm2_num"],
            "api_concentration_pct": canonical["api_concentration_pct"],
            "data_source": "literature",
            "original_endpoint_time_h": canonical["endpoint_time_h"],
            "original_endpoint_unit": canonical["endpoint_unit"],
            "original_endpoint_value": canonical["endpoint_value"],
        }
    ).sort_values(["doi", "formulation_label"]).reset_index(drop=True)

    valid_for_gpr = literature_24h[
        literature_24h["cumulative_amount_24h_ug_cm2"].between(0.0, 1000.0, inclusive="both")
    ].copy()

    summary = write_literature_summary(full, near_24h, literature_24h, valid_for_gpr, self_range)
    return literature_24h, valid_for_gpr, summary


def value_range(values: pd.Series) -> str:
    values = pd.to_numeric(values, errors="coerce").dropna()
    if values.empty:
        return "n/a"
    return f"{values.min():.3f} to {values.max():.3f}"


def write_literature_summary(
    full: pd.DataFrame,
    near_24h: pd.DataFrame,
    literature_24h: pd.DataFrame,
    valid_for_gpr: pd.DataFrame,
    self_range: tuple[float, float],
) -> str:
    doi_counts = literature_24h["doi"].value_counts().to_dict()
    formulation_list = (
        literature_24h.groupby("doi")["formulation_label"]
        .apply(lambda values: ", ".join(str(value) for value in values))
        .to_dict()
    )
    membrane_counts = valid_for_gpr["membrane_type"].fillna("(missing)").value_counts().to_dict()
    lit_range = value_range(literature_24h["cumulative_amount_24h_ug_cm2"])
    valid_range = value_range(valid_for_gpr["cumulative_amount_24h_ug_cm2"])
    self_min, self_max = self_range
    overlap_min = max(self_min, valid_for_gpr["cumulative_amount_24h_ug_cm2"].min())
    overlap_max = min(self_max, valid_for_gpr["cumulative_amount_24h_ug_cm2"].max())
    overlap = overlap_min <= overlap_max

    lines = [
        "# Literature 24h Data Summary",
        "",
        "## Filtering",
        "",
        f"- Source CSV: `{LITERATURE_FULL}`",
        f"- Total records before 24h filtering: `{len(full)}`",
        f"- Raw records within 23-25h: `{len(near_24h)}`",
        f"- Canonical records after record_id dedupe: `{len(literature_24h)}`",
        f"- Records used by the default GPR sanity filter (0-1000 ug/cm2): `{len(valid_for_gpr)}`",
        "",
        "The default GPR run excludes one extreme 24h value above 1000 ug/cm2 because it is not comparable with the Paper 1 response scale. The excluded record remains in `literature_24h_data.csv` for auditability.",
        "",
        "## DOI And Formulation Coverage",
        "",
        "| DOI | Records | Formulations |",
        "|---|---:|---|",
    ]
    for doi, count in doi_counts.items():
        lines.append(f"| `{doi}` | {count} | {formulation_list.get(doi, '')} |")

    lines.extend(
        [
            "",
            "## Response Range",
            "",
            f"- Paper 1 24h mean range: `{self_min:.3f} to {self_max:.3f} ug/cm2`",
            f"- Literature 24h canonical range, including audit outlier: `{lit_range} ug/cm2`",
            f"- Literature 24h default GPR range: `{valid_range} ug/cm2`",
            f"- 24h response ranges overlap after sanity filtering: `{'yes' if overlap else 'no'}`",
            "",
            "## Membrane Types In Default GPR Literature Set",
            "",
            "| Membrane type | Records |",
            "|---|---:|",
        ]
    )
    for membrane, count in membrane_counts.items():
        lines.append(f"| `{membrane}` | {count} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The 24h intersection is materially better than the earlier 28h setup because both Paper 1 and SkinMiner literature records now share an ibuprofen Franz-cell cumulative amount endpoint at the same timepoint.",
            "The main residual mismatch is still formulation domain and membrane domain: Paper 1 uses Poloxamer 407 / ethanol / propylene glycol on Strat-M, while the usable literature block is porcine skin formulations from one paper.",
            "",
        ]
    )
    summary = "\n".join(lines)
    (OUTPUT_DIR / "literature_24h_summary.md").write_text(summary, encoding="utf-8")
    return summary


def write_distribution_data(mean_24h: pd.DataFrame, valid_literature_24h: pd.DataFrame) -> None:
    self_fig = mean_24h[["formulation_id", "cumulative_amount_24h_ug_cm2"]].rename(
        columns={"formulation_id": "formulation_label"}
    )
    self_fig.insert(0, "source", "self_generated")
    lit_fig = valid_literature_24h[["formulation_label", "cumulative_amount_24h_ug_cm2"]].copy()
    lit_fig.insert(0, "source", "literature")
    fig_data = pd.concat([self_fig, lit_fig], ignore_index=True)
    fig_data.to_csv(OUTPUT_DIR / "fig_data_distribution.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw, mean_24h, all_replicates = prepare_paper1()
    self_range = (
        float(mean_24h["cumulative_amount_24h_ug_cm2"].min()),
        float(mean_24h["cumulative_amount_24h_ug_cm2"].max()),
    )
    literature_24h, valid_literature_24h, _ = prepare_literature(self_range)
    write_distribution_data(mean_24h, valid_literature_24h)

    raw.to_csv(OUTPUT_DIR / "paper1_raw_data.csv", index=False, encoding="utf-8-sig")
    mean_24h.to_csv(OUTPUT_DIR / "paper1_24h_mean.csv", index=False, encoding="utf-8-sig")
    all_replicates.to_csv(OUTPUT_DIR / "paper1_24h_all_replicates.csv", index=False, encoding="utf-8-sig")
    literature_24h.to_csv(OUTPUT_DIR / "literature_24h_data.csv", index=False, encoding="utf-8-sig")

    payload = {
        "paper1_raw_csv": str(OUTPUT_DIR / "paper1_raw_data.csv"),
        "paper1_mean_csv": str(OUTPUT_DIR / "paper1_24h_mean.csv"),
        "paper1_replicates_csv": str(OUTPUT_DIR / "paper1_24h_all_replicates.csv"),
        "literature_24h_csv": str(OUTPUT_DIR / "literature_24h_data.csv"),
        "literature_24h_summary": str(OUTPUT_DIR / "literature_24h_summary.md"),
        "fig_data_distribution": str(OUTPUT_DIR / "fig_data_distribution.csv"),
        "paper1_formulations": int(mean_24h["formulation_id"].nunique()),
        "paper1_replicate_rows": int(len(all_replicates)),
        "paper1_24h_range": self_range,
        "literature_24h_records": int(len(literature_24h)),
        "literature_24h_records_default_gpr": int(len(valid_literature_24h)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
