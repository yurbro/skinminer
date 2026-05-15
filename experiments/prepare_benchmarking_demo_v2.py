from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "demonstration"
PAPER1_XLSX = Path(
    r"C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\ReviewerToCodex\codex-3\paper1.xlsx"
)
PATCHED_AREA_JSONL = ROOT / "outputs" / "full_run_16_post_all_fixes" / "patched_area.jsonl"
LITERATURE_24H_FULL_CSV = OUTPUT_DIR / "literature_24h_data_full.csv"

TIME_COLUMNS = ["t1", "t2", "t3", "t4", "t6", "t8", "t22", "t24", "t26", "t28"]
PAPER1_REQUIRED_COLUMNS = {"Time", "Poloxamer 407", "Ethanol", "Propyene glycol", *TIME_COLUMNS}

PAPER1_API = "Ibuprofen 5% w/w"
PAPER1_DEVICE = "Franz cell"
PAPER1_MEMBRANE = "Strat-M synthetic membrane"
PAPER1_EXCIPIENT = "Poloxamer 407 / Ethanol / Propylene glycol gel"
PAPER1_DOSE = "Finite dose, 300 mg"
PAPER1_RECEPTOR = "PBS"
PAPER1_AREA = "Not encoded in spreadsheet"
PAPER1_CONDITION_NOTE = "Strat-M, finite dose 300 mg, Poloxamer 407 gel"

LITERATURE_DOI = "10.1208/s12249-013-9995-4"
LITERATURE_DEVICE = "Franz diffusion cell"
LITERATURE_MEMBRANE = "Porcine skin"
LITERATURE_EXCIPIENT = "Vit. E TPGS / HPMC nanosuspension"
LITERATURE_DOSE = "Infinite dose"
LITERATURE_RECEPTOR = "PBS (pH 7.4)"
LITERATURE_AREA = "0.64 cm2"
LITERATURE_CONDITION_NOTE = "Porcine skin, infinite dose, TPGS/HPMC nanosuspension"

LEVEL_LABELS = {
    1: "Level 1: Exact match",
    2: "Level 2: Same excipient system",
    3: "Level 3: Partial excipient overlap",
    4: "Level 4: Same API + device only",
    0: "No funnel match",
}

LABEL_RE = re.compile(r"^\s*((?:Cf|BO|OPT)\d+)_(\d+)\s*$", re.IGNORECASE)
F_LABEL_RE = re.compile(r"^F(\d+)$", re.IGNORECASE)
POLoxamer_RE = re.compile(r"\b(poloxamer(?:\s*(?:407|188))?|p407|pluronic\s*f127)\b", re.IGNORECASE)
ETHANOL_RE = re.compile(r"\bethanol\b|\betoh\b", re.IGNORECASE)
PG_RE = re.compile(r"\bpropylene\s*glycol\b|\bpropyl?ene glycol\b|\bpg\b", re.IGNORECASE)
DEVICE_RE = re.compile(r"\bfranz\b|\bdiffusion\s+cell\b", re.IGNORECASE)
MEMBRANE_RE = re.compile(r"\bstrat[-\s]?m\b|\bsynthetic\b", re.IGNORECASE)
BARRIER_CONTEXT_RE = re.compile(
    r"\bskin\b|\bmembrane\b|\bstratum\b|\bcorneum\b|\bporcine\b|\bhuman\b|\bmouse\b|\brat\b",
    re.IGNORECASE,
)
EXCLUDE_CONTEXT_RE = re.compile(r"\bi\.p\.\b|\bintraperitoneal\b|\binjection\b|\bmg/kg\b", re.IGNORECASE)


def normalize_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def formulation_sort_key(value: str) -> tuple[int, int]:
    if value.startswith("Cf"):
        return (0, int(value[2:]))
    if value.startswith("BO"):
        return (1, int(value[2:]))
    if value.startswith("OPT"):
        return (2, int(value[3:]))
    if value.startswith("F"):
        return (3, int(value[1:]))
    return (9, 0)


def parse_paper1_label(value: object) -> tuple[str, int]:
    match = LABEL_RE.fullmatch(str(value))
    if not match:
        raise ValueError(f"Unexpected Paper 1 label: {value!r}")
    return match.group(1), int(match.group(2))


def classify_design(label: str) -> tuple[str, str, int]:
    if label.startswith("Cf"):
        num = int(label[2:])
        if 1 <= num <= 15:
            return ("BBD", "Box-Behnken design", 1)
        if 16 <= num <= 25:
            return ("LHS", "Latin hypercube sampling", 2)
    if label.startswith("BO"):
        return ("BO", "Bayesian optimization", 3)
    if label.startswith("OPT"):
        return ("OPT", "Final optimum", 4)
    raise ValueError(f"Unsupported formulation label for design classification: {label}")


def load_paper1_excel() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not PAPER1_XLSX.exists():
        raise FileNotFoundError(f"Paper 1 Excel not found: {PAPER1_XLSX}")

    df = pd.read_excel(PAPER1_XLSX, sheet_name=0)
    missing = PAPER1_REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Paper 1 Excel is missing required columns: {sorted(missing)}")

    parsed = df["Time"].apply(parse_paper1_label)
    raw = pd.DataFrame(
        {
            "formulation_id": [item[0] for item in parsed],
            "replicate": [item[1] for item in parsed],
            "poloxamer_407_pct": pd.to_numeric(df["Poloxamer 407"], errors="coerce"),
            "ethanol_pct": pd.to_numeric(df["Ethanol"], errors="coerce"),
            "propylene_glycol_pct": pd.to_numeric(df["Propyene glycol"], errors="coerce"),
        }
    )
    design_meta = raw["formulation_id"].apply(classify_design)
    raw["design_group"] = [item[0] for item in design_meta]
    raw["design_method"] = [item[1] for item in design_meta]
    raw["design_stage_order"] = [item[2] for item in design_meta]
    raw["source"] = "Paper 1 (this study)"

    for column in TIME_COLUMNS:
        raw[column] = pd.to_numeric(df[column], errors="coerce")

    numeric_columns = ["poloxamer_407_pct", "ethanol_pct", "propylene_glycol_pct", *TIME_COLUMNS]
    if raw[numeric_columns].isna().any().any():
        raise ValueError("Paper 1 Excel contains non-numeric values in required numeric columns.")

    raw = raw.sort_values(
        by=["design_stage_order", "formulation_id", "replicate"],
        key=lambda series: series.map(formulation_sort_key) if series.name == "formulation_id" else series,
    ).reset_index(drop=True)

    replicate_counts = raw.groupby("formulation_id")["replicate"].nunique()
    if len(raw) != 150 or raw["formulation_id"].nunique() != 30 or not (replicate_counts == 5).all():
        raise ValueError(
            "Paper 1 Excel is expected to contain 150 rows, 30 formulations, and 5 replicates each; "
            f"found rows={len(raw)}, formulations={raw['formulation_id'].nunique()}, "
            f"replicate_counts={replicate_counts.to_dict()}."
        )

    all_replicates = raw[
        [
            "source",
            "formulation_id",
            "design_group",
            "design_method",
            "replicate",
            "poloxamer_407_pct",
            "ethanol_pct",
            "propylene_glycol_pct",
            "t24",
        ]
    ].rename(columns={"t24": "cumulative_amount_24h_ug_cm2"})

    mean_24h = (
        all_replicates.groupby(
            [
                "source",
                "formulation_id",
                "design_group",
                "design_method",
                "poloxamer_407_pct",
                "ethanol_pct",
                "propylene_glycol_pct",
            ],
            as_index=False,
        )
        .agg(cumulative_amount_24h_ug_cm2=("cumulative_amount_24h_ug_cm2", "mean"))
        .sort_values(by=["design_group", "formulation_id"], key=lambda series: series.map(formulation_sort_key) if series.name == "formulation_id" else series)
        .reset_index(drop=True)
    )
    return raw, all_replicates, mean_24h


def load_literature_f1f8() -> pd.DataFrame:
    if not LITERATURE_24H_FULL_CSV.exists():
        raise FileNotFoundError(f"Literature 24h full CSV not found: {LITERATURE_24H_FULL_CSV}")

    df = pd.read_csv(LITERATURE_24H_FULL_CSV)
    literature = df[df["doi"] == LITERATURE_DOI].copy()
    literature = literature[literature["formulation_label"].astype(str).str.fullmatch(r"F[1-8]")].copy()
    for column in [
        "api_pct_wv",
        "hpmc_k4_pct_wv_constant",
        "particle_size_nm",
        "vit_e_tpgs_pct_wv",
        "hpmc_k100_pct_wv",
        "cumulative_amount_24h_ug_cm2",
    ]:
        literature[column] = pd.to_numeric(literature[column], errors="coerce")
    literature = literature.sort_values("formulation_label", key=lambda series: series.map(formulation_sort_key)).reset_index(drop=True)
    if len(literature) != 8:
        raise ValueError(f"Expected 8 literature rows F1-F8, found {len(literature)}.")
    return literature


def component_text(components: object) -> str:
    parts: list[str] = []
    for component in components or []:
        if not isinstance(component, dict):
            continue
        chunk = " ".join(
            normalize_text(component.get(key))
            for key in ["name", "raw", "note", "basis"]
            if normalize_text(component.get(key))
        )
        if chunk:
            parts.append(chunk)
    return " ; ".join(parts)


def evidence_preview(items: list[dict[str, object]], width: int = 240) -> str:
    snippets = [normalize_text((item or {}).get("snippet")) for item in items or []]
    snippets = [snippet for snippet in snippets if snippet]
    if not snippets:
        return ""
    preview = " | ".join(snippets[:3])
    return preview[:width]


def record_guard(rec: dict[str, object], context_blob: str, barrier_blob: str) -> tuple[bool, str]:
    reasons: list[str] = []
    if str(rec.get("study_type") or "").upper() not in {"IVPT", "IVRT"}:
        reasons.append("non_ivpt_or_ivrt")
    if not BARRIER_CONTEXT_RE.search(barrier_blob):
        reasons.append("non_skin_or_membrane_context")
    if EXCLUDE_CONTEXT_RE.search(context_blob):
        reasons.append("excluded_non_topical_context")
    return (len(reasons) == 0, ";".join(reasons))


def search_excipient_matches() -> tuple[pd.DataFrame, dict[str, int], dict[str, object]]:
    if not PATCHED_AREA_JSONL.exists():
        raise FileNotFoundError(f"patched_area.jsonl not found: {PATCHED_AREA_JSONL}")

    rows: list[dict[str, object]] = []
    with PATCHED_AREA_JSONL.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rec = json.loads(line)
            formulation = rec.get("formulation") or {}
            conditions = rec.get("conditions") or {}
            provenance = rec.get("provenance") or {}
            metadata = provenance.get("metadata") or {}
            route_raw_labels = metadata.get("route_raw_labels") or {}
            evidence_items = rec.get("evidence_items") or []

            components_blob = component_text(formulation.get("components"))
            formulation_blob = " | ".join(
                [
                    normalize_text(formulation.get("label")),
                    normalize_text(formulation.get("name")),
                    normalize_text(formulation.get("api_name")),
                    normalize_text(formulation.get("api_concentration_raw")),
                    normalize_text(formulation.get("dosage_form")),
                    components_blob,
                    " ".join(normalize_text(note) for note in (conditions.get("notes") or [])),
                    " ".join(normalize_text(note) for note in (rec.get("source_notes") or [])),
                    " ".join(
                        normalize_text((item or {}).get("snippet"))
                        for item in evidence_items
                        if (item or {}).get("field_name") in {"formulation", "api_concentration", "device", "membrane_type", "membrane_source"}
                    ),
                ]
            )
            device_blob = " | ".join(
                [
                    normalize_text(rec.get("device")),
                    normalize_text(route_raw_labels.get("franz_confirmed")),
                    normalize_text(route_raw_labels.get("where_diffusion_cell")),
                    normalize_text(route_raw_labels.get("where_franz")),
                    normalize_text(provenance.get("route_notes")),
                    " ".join(
                        normalize_text((item or {}).get("snippet"))
                        for item in evidence_items
                        if (item or {}).get("field_name") == "device"
                    ),
                ]
            )
            barrier_blob = " | ".join(
                [
                    normalize_text(rec.get("barrier")),
                    normalize_text(conditions.get("membrane_type")),
                    normalize_text(conditions.get("membrane_source")),
                    " ".join(
                        normalize_text((item or {}).get("snippet"))
                        for item in evidence_items
                        if (item or {}).get("field_name") in {"membrane_type", "membrane_source"}
                    ),
                ]
            )
            api_blob = " | ".join([normalize_text(formulation.get("api_name")), normalize_text(formulation.get("label"))])
            context_blob = " | ".join([api_blob, formulation_blob, barrier_blob])

            guard_pass, guard_reason = record_guard(rec, context_blob, barrier_blob)
            api_match = "ibuprofen" in api_blob.lower()
            device_match = bool(DEVICE_RE.search(device_blob))
            membrane_match = bool(MEMBRANE_RE.search(barrier_blob))
            poloxamer_match = bool(POLoxamer_RE.search(formulation_blob))
            ethanol_match = bool(ETHANOL_RE.search(formulation_blob))
            pg_match = bool(PG_RE.search(formulation_blob))

            level4 = guard_pass and api_match and device_match
            level3 = level4 and any([poloxamer_match, ethanol_match, pg_match])
            level2 = level4 and all([poloxamer_match, ethanol_match, pg_match])
            level1 = level2 and membrane_match
            highest_level = 1 if level1 else 2 if level2 else 3 if level3 else 4 if level4 else 0
            matched_terms = [
                name
                for name, flag in [
                    ("poloxamer", poloxamer_match),
                    ("ethanol", ethanol_match),
                    ("propylene glycol", pg_match),
                ]
                if flag
            ]

            rows.append(
                {
                    "record_id": rec.get("record_id"),
                    "doi": rec.get("doi"),
                    "route": rec.get("route"),
                    "study_type": rec.get("study_type"),
                    "scientific_guard_pass": guard_pass,
                    "guard_reason": guard_reason,
                    "formulation_label": formulation.get("label"),
                    "api_name": formulation.get("api_name"),
                    "dosage_form": formulation.get("dosage_form"),
                    "device": rec.get("device"),
                    "barrier": rec.get("barrier"),
                    "api_concentration_raw": formulation.get("api_concentration_raw"),
                    "components_text": components_blob,
                    "evidence_preview": evidence_preview(evidence_items),
                    "api_match": api_match,
                    "device_match": device_match,
                    "membrane_match": membrane_match,
                    "poloxamer_match": poloxamer_match,
                    "ethanol_match": ethanol_match,
                    "propylene_glycol_match": pg_match,
                    "matched_excipient_terms": ", ".join(matched_terms),
                    "level1_exact_match": level1,
                    "level2_same_excipient_system": level2,
                    "level3_partial_excipient_overlap": level3,
                    "level4_same_api_device": level4,
                    "highest_level": highest_level,
                    "highest_level_label": LEVEL_LABELS[highest_level],
                }
            )

    detail = pd.DataFrame(rows).sort_values(["highest_level", "doi", "formulation_label"], ascending=[True, True, True]).reset_index(drop=True)
    detail.to_csv(OUTPUT_DIR / "excipient_match_detail.csv", index=False, encoding="utf-8-sig")

    eligible = detail[detail["scientific_guard_pass"]].copy()
    funnel_counts = {
        "level1_exact_match": int(eligible["level1_exact_match"].sum()),
        "level2_same_excipient_system": int(eligible["level2_same_excipient_system"].sum()),
        "level3_partial_excipient_overlap": int(eligible["level3_partial_excipient_overlap"].sum()),
        "level4_same_api_device": int(eligible["level4_same_api_device"].sum()),
    }

    level3_rows = eligible[eligible["level3_partial_excipient_overlap"]].copy()
    level3_term_counts = Counter()
    for terms in level3_rows["matched_excipient_terms"]:
        for term in [item.strip() for item in str(terms).split(",") if item.strip()]:
            level3_term_counts[term] += 1
    level3_examples = (
        level3_rows.groupby("doi")["formulation_label"]
        .apply(lambda values: ", ".join(sorted({str(value) for value in values})))
        .to_dict()
    )
    meta = {
        "total_assembled_records": int(len(detail)),
        "scientific_guard_pass_records": int(len(eligible)),
        "level3_unique_doi": int(level3_rows["doi"].nunique()),
        "level3_term_counts": dict(level3_term_counts),
        "level3_examples": level3_examples,
    }
    return detail, funnel_counts, meta


def write_excipient_match_report(detail: pd.DataFrame, funnel_counts: dict[str, int], meta: dict[str, object]) -> None:
    level3_rows = detail[detail["scientific_guard_pass"] & detail["level3_partial_excipient_overlap"]].copy()
    lines = [
        "# Excipient-Matched Literature Search",
        "",
        "## Search Scope",
        "",
        f"- Source file: `{PATCHED_AREA_JSONL}`",
        f"- Total assembled records scanned: `{meta['total_assembled_records']}`",
        f"- Records passing the topical/transdermal plausibility guard: `{meta['scientific_guard_pass_records']}`",
        "- Search fields inspected: formulation label/name, API concentration raw text, structured component list, condition notes, and evidence snippets.",
        "",
        "## Funnel Counts",
        "",
        "| Level | Criteria | Matching records |",
        "|---|---|---:|",
        "| Level 1 | Ibuprofen + Franz/diffusion cell + Strat-M/synthetic membrane + poloxamer + ethanol + PG | "
        f"{funnel_counts['level1_exact_match']} |",
        "| Level 2 | Ibuprofen + Franz/diffusion cell + poloxamer + ethanol + PG | "
        f"{funnel_counts['level2_same_excipient_system']} |",
        "| Level 3 | Ibuprofen + Franz/diffusion cell + at least one of poloxamer / ethanol / PG | "
        f"{funnel_counts['level3_partial_excipient_overlap']} |",
        "| Level 4 | Ibuprofen + Franz/diffusion cell | "
        f"{funnel_counts['level4_same_api_device']} |",
        "",
        "## Interpretation",
        "",
        f"- Level 1 exact matches found: `{funnel_counts['level1_exact_match']}`.",
        f"- Level 2 same-excipient-system matches found: `{funnel_counts['level2_same_excipient_system']}`.",
        f"- Level 3 partial-overlap matches found: `{funnel_counts['level3_partial_excipient_overlap']}` across `{meta['level3_unique_doi']}` papers.",
        "- The absence of Level 1 and Level 2 hits means the current SkinMiner corpus does not contain a directly comparable ibuprofen Franz-cell record with the full Poloxamer 407 / ethanol / propylene glycol system.",
        "- That is the core novelty argument for Paper 1: SkinMiner can search the corpus automatically and still show that your exact experimental system is not already represented in the extracted literature set.",
        "",
        "## Level 3 Partial Overlap Breakdown",
        "",
        "| Excipient token | Records |",
        "|---|---:|",
    ]
    for term, count in sorted((meta["level3_term_counts"] or {}).items()):
        lines.append(f"| `{term}` | {count} |")

    lines.extend(
        [
            "",
            "| DOI | Example matched formulation labels |",
            "|---|---|",
        ]
    )
    for doi, labels in sorted((meta["level3_examples"] or {}).items()):
        lines.append(f"| `{doi}` | {labels} |")

    if not level3_rows.empty:
        lines.extend(
            [
                "",
                "## Notes",
                "",
                "- Level 3 hits are partial textual overlaps only. They are useful as reconnaissance signals, not as evidence of direct comparability.",
                "- The funnel intentionally uses assembled records rather than verified-only records because the task here is literature reconnaissance, not benchmark-grade endpoint confirmation.",
                "",
            ]
        )

    (OUTPUT_DIR / "excipient_match_results.md").write_text("\n".join(lines), encoding="utf-8")


def build_fig_permeation_landscape(mean_24h: pd.DataFrame, literature: pd.DataFrame) -> pd.DataFrame:
    paper1 = mean_24h[
        [
            "source",
            "formulation_id",
            "design_group",
            "design_method",
            "cumulative_amount_24h_ug_cm2",
        ]
    ].rename(columns={"formulation_id": "formulation_label"})
    paper1["doi"] = "this_study"
    paper1["endpoint_time_h"] = 24.0
    paper1["excipient_system"] = PAPER1_EXCIPIENT
    paper1["membrane_type"] = PAPER1_MEMBRANE
    paper1["condition_note"] = PAPER1_CONDITION_NOTE

    literature_rows = pd.DataFrame(
        {
            "source": "Literature (SkinMiner extracted)",
            "formulation_label": literature["formulation_label"],
            "design_group": "Literature",
            "design_method": "SkinMiner literature extraction",
            "cumulative_amount_24h_ug_cm2": literature["cumulative_amount_24h_ug_cm2"],
            "doi": literature["doi"],
            "endpoint_time_h": 24.0,
            "excipient_system": LITERATURE_EXCIPIENT,
            "membrane_type": literature["membrane_type"],
            "condition_note": LITERATURE_CONDITION_NOTE,
        }
    )

    combined = pd.concat([paper1, literature_rows], ignore_index=True)
    combined.to_csv(OUTPUT_DIR / "fig_permeation_landscape.csv", index=False, encoding="utf-8-sig")
    return combined


def build_fig_experimental_conditions(mean_24h: pd.DataFrame, literature: pd.DataFrame) -> pd.DataFrame:
    paper_rows = pd.DataFrame(
        {
            "source": "Paper 1 (this study)",
            "formulation_label": mean_24h["formulation_id"],
            "design_group": mean_24h["design_group"],
            "design_method": mean_24h["design_method"],
            "doi": "this_study",
            "api_name": "Ibuprofen",
            "api_concentration": PAPER1_API,
            "membrane_type": "Strat-M",
            "membrane_source": "synthetic",
            "receptor_medium": PAPER1_RECEPTOR,
            "dose_type": "finite",
            "dose_amount": "300 mg",
            "diffusion_area_cm2": "",
            "device": PAPER1_DEVICE,
            "excipient_1_name": "Poloxamer 407",
            "excipient_1_value": mean_24h["poloxamer_407_pct"].map(lambda value: f"{value:g}% w/w"),
            "excipient_2_name": "Ethanol",
            "excipient_2_value": mean_24h["ethanol_pct"].map(lambda value: f"{value:g}% w/w"),
            "excipient_3_name": "Propylene glycol",
            "excipient_3_value": mean_24h["propylene_glycol_pct"].map(lambda value: f"{value:g}% w/w"),
            "condition_note": PAPER1_CONDITION_NOTE,
        }
    )
    literature_rows = pd.DataFrame(
        {
            "source": "Literature (SkinMiner extracted)",
            "formulation_label": literature["formulation_label"],
            "design_group": "Literature",
            "design_method": "SkinMiner literature extraction",
            "doi": literature["doi"],
            "api_name": "Ibuprofen",
            "api_concentration": literature["api_pct_wv"].map(lambda value: f"{value:g}% w/v"),
            "membrane_type": literature["membrane_type"],
            "membrane_source": literature["membrane_source"],
            "receptor_medium": LITERATURE_RECEPTOR,
            "dose_type": "infinite",
            "dose_amount": "infinite dose",
            "diffusion_area_cm2": 0.64,
            "device": LITERATURE_DEVICE,
            "excipient_1_name": "Vit. E TPGS",
            "excipient_1_value": literature["vit_e_tpgs_pct_wv"].map(lambda value: f"{value:g}% w/v"),
            "excipient_2_name": "HPMC K100",
            "excipient_2_value": literature["hpmc_k100_pct_wv"].map(lambda value: f"{value:g}% w/v"),
            "excipient_3_name": "HPMC K4 (base)",
            "excipient_3_value": literature["hpmc_k4_pct_wv_constant"].map(lambda value: f"{value:g}% w/v"),
            "condition_note": LITERATURE_CONDITION_NOTE,
        }
    )
    combined = pd.concat([paper_rows, literature_rows], ignore_index=True)
    combined.to_csv(OUTPUT_DIR / "fig_experimental_conditions.csv", index=False, encoding="utf-8-sig")
    return combined


def build_plot_support_csvs(funnel_counts: dict[str, int]) -> None:
    funnel = pd.DataFrame(
        [
            {"level": "Level 1", "criteria": "Exact match", "count": funnel_counts["level1_exact_match"]},
            {"level": "Level 2", "criteria": "Same excipient system", "count": funnel_counts["level2_same_excipient_system"]},
            {"level": "Level 3", "criteria": "Partial excipient overlap", "count": funnel_counts["level3_partial_excipient_overlap"]},
            {"level": "Level 4", "criteria": "Same API + device", "count": funnel_counts["level4_same_api_device"]},
        ]
    )
    funnel.to_csv(OUTPUT_DIR / "fig_condition_funnel.csv", index=False, encoding="utf-8-sig")

    comparability = pd.DataFrame(
        [
            {"dimension": "API", "paper1": PAPER1_API, "literature": "Ibuprofen 5% w/v", "match_symbol": "≈", "match_label": "Partial", "extracted": "Yes"},
            {"dimension": "Device", "paper1": PAPER1_DEVICE, "literature": LITERATURE_DEVICE, "match_symbol": "✓", "match_label": "Match", "extracted": "Yes"},
            {"dimension": "Membrane", "paper1": PAPER1_MEMBRANE, "literature": LITERATURE_MEMBRANE, "match_symbol": "×", "match_label": "Mismatch", "extracted": "Yes"},
            {"dimension": "Excipient", "paper1": PAPER1_EXCIPIENT, "literature": LITERATURE_EXCIPIENT, "match_symbol": "×", "match_label": "Mismatch", "extracted": "Yes"},
            {"dimension": "Dose", "paper1": PAPER1_DOSE, "literature": LITERATURE_DOSE, "match_symbol": "×", "match_label": "Mismatch", "extracted": "Yes"},
            {"dimension": "Receptor", "paper1": PAPER1_RECEPTOR, "literature": LITERATURE_RECEPTOR, "match_symbol": "✓", "match_label": "Match", "extracted": "Yes"},
            {"dimension": "Area", "paper1": PAPER1_AREA, "literature": LITERATURE_AREA, "match_symbol": "≈", "match_label": "Partial", "extracted": "Yes"},
        ]
    )
    comparability.to_csv(OUTPUT_DIR / "fig_comparability_table.csv", index=False, encoding="utf-8-sig")


def write_benchmarking_analysis(
    raw: pd.DataFrame,
    mean_24h: pd.DataFrame,
    funnel_counts: dict[str, int],
    meta: dict[str, object],
) -> str:
    paper1_range = (
        float(mean_24h["cumulative_amount_24h_ug_cm2"].min()),
        float(mean_24h["cumulative_amount_24h_ug_cm2"].max()),
    )
    design_counts = mean_24h["design_group"].value_counts().to_dict()
    level3_term_counts = meta["level3_term_counts"] or {}

    lines = [
        "# Benchmarking Demonstration Analysis",
        "",
        "## 1. Why The Earlier Ranking Was Removed",
        "",
        "The previous benchmarking version ranked Paper 1 and literature permeation values together even when membrane type, excipient system, and dose mode were materially different. That ranking was not scientifically defensible.",
        "",
        "This revised version changes the closure narrative: SkinMiner is used first as an automated literature reconnaissance engine, then as a structured comparability-assessment tool. The literature distribution is still shown, but only as context, not as a direct cross-condition leaderboard.",
        "",
        "## 2. Updated Paper 1 Dataset",
        "",
        f"- Updated Excel rows: `{len(raw)}`",
        f"- Unique formulations: `{mean_24h['formulation_id'].nunique()}`",
        f"- Replicates per formulation: `5`",
        f"- Design groups: `BBD={design_counts.get('BBD', 0)}`, `LHS={design_counts.get('LHS', 0)}`, `BO={design_counts.get('BO', 0)}`, `OPT={design_counts.get('OPT', 0)}`",
        f"- Paper 1 24 h mean range: `{paper1_range[0]:.1f}-{paper1_range[1]:.1f} ug/cm2`",
        "",
        "## 3. Excipient-Matched Literature Search",
        "",
        f"SkinMiner searched all `{meta['total_assembled_records']}` assembled records from the frozen GPT baseline (`full_run_16_post_all_fixes/patched_area.jsonl`). To suppress obvious non-topical contamination, the funnel only counts records that pass a topical/transdermal plausibility guard (`study_type` IVPT/IVRT plus skin/membrane context, excluding injection-like contexts).",
        "",
        "| Funnel level | Matching records |",
        "|---|---:|",
        f"| Level 1 exact match | {funnel_counts['level1_exact_match']} |",
        f"| Level 2 same excipient system | {funnel_counts['level2_same_excipient_system']} |",
        f"| Level 3 partial excipient overlap | {funnel_counts['level3_partial_excipient_overlap']} |",
        f"| Level 4 same API + device only | {funnel_counts['level4_same_api_device']} |",
        "",
        f"Level 2 is the critical result and it is `0`: no extracted record in the current corpus matches ibuprofen + Franz/diffusion cell + the full Poloxamer / ethanol / propylene glycol system. Level 1 is also `0`, so there is no exact match once Strat-M/synthetic membrane is required.",
        "",
        f"Level 3 returns `{funnel_counts['level3_partial_excipient_overlap']}` records across `{meta['level3_unique_doi']}` papers. The partial overlaps are only reconnaissance signals: `poloxamer={level3_term_counts.get('poloxamer', 0)}`, `ethanol={level3_term_counts.get('ethanol', 0)}`, `propylene glycol={level3_term_counts.get('propylene glycol', 0)}`.",
        "",
        "## 4. Automated Comparability Assessment",
        "",
        "SkinMiner can still structure a literature condition block automatically. The F1-F8 ibuprofen nanosuspension records provide a good demonstration case because the extraction captures API concentration, membrane, receptor, dose mode, diffusion area, and excipient composition.",
        "",
        "However, the structured comparison shows why those values must not be ranked directly against Paper 1:",
        "",
        "- API is only partially aligned (`5% w/w` vs `5% w/v`).",
        "- Device is aligned (Franz diffusion cell).",
        "- Membrane is not aligned (`Strat-M` vs `porcine skin`).",
        "- Excipient system is not aligned (`Poloxamer 407 / EtOH / PG` vs `Vit. E TPGS / HPMC`).",
        "- Dose mode is not aligned (`finite 300 mg` vs `infinite dose`).",
        "- Receptor is aligned closely enough for qualitative comparison (`PBS` vs `PBS pH 7.4`).",
        "",
        "That is why Figure 4 is now a split distribution figure with an explicit 'not directly comparable' separator instead of a combined ranking plot.",
        "",
        "## 5. What SkinMiner Contributes To The PhD Story",
        "",
        "Paper 1-3 solve how to optimize formulations efficiently inside a chosen experimental system. Paper 4 adds the missing literature-intelligence layer: it can automatically search whether that system already exists in the literature, expose when it does not, and make comparability judgments explicit when only partially related systems are available.",
        "",
        "## 6. Updated Closure Statement",
        "",
        "SkinMiner closes the loop not by naively merging heterogeneous literature responses into model training, but by turning the literature into a structured reconnaissance layer for formulation science. It answers three practical questions after optimization: Is there prior literature in the same excipient system? If not, how novel is the current setup? And if related papers exist, which condition mismatches prevent direct comparison?",
        "",
    ]
    text = "\n".join(lines)
    (OUTPUT_DIR / "benchmarking_analysis.md").write_text(text, encoding="utf-8")
    return text


def write_final_summary(mean_24h: pd.DataFrame, funnel_counts: dict[str, int]) -> str:
    lines = [
        "# SkinMiner PhD Closure Demonstration - Final Summary",
        "",
        "## Approach",
        "",
        "This revised demonstration uses SkinMiner as a literature-intelligence layer rather than a cross-condition ranking engine. The workflow is: update the Paper 1 formulation dataset, search the extracted literature for excipient-matched records, and then show the remaining literature only with an explicit comparability judgment.",
        "",
        "## Main Findings",
        "",
        f"- Updated Paper 1 dataset: `{mean_24h['formulation_id'].nunique()}` formulations at 24 h.",
        f"- Exact condition-matched literature records: `{funnel_counts['level1_exact_match']}`.",
        f"- Same-excipient-system literature records: `{funnel_counts['level2_same_excipient_system']}`.",
        f"- Partial-overlap reconnaissance records: `{funnel_counts['level3_partial_excipient_overlap']}`.",
        "",
        "## PhD Narrative",
        "",
        "Paper 1-3 optimize formulations efficiently and interpretably. Paper 4 does something different but complementary: it automates the literature search needed to decide whether an optimized formulation sits in a known experimental space, a partially related space, or a genuinely new one. That makes SkinMiner a practical deployment tool for EDMA-style formulation programs, because it adds data availability screening, condition comparability checking, and external landscape awareness after optimization.",
        "",
    ]
    text = "\n".join(lines)
    (OUTPUT_DIR / "demonstration_final_summary.md").write_text(text, encoding="utf-8")
    return text


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw, all_replicates, mean_24h = load_paper1_excel()
    literature = load_literature_f1f8()
    detail, funnel_counts, meta = search_excipient_matches()

    raw.to_csv(OUTPUT_DIR / "paper1_raw_data.csv", index=False, encoding="utf-8-sig")
    all_replicates.to_csv(OUTPUT_DIR / "paper1_24h_all_replicates.csv", index=False, encoding="utf-8-sig")
    mean_24h.to_csv(OUTPUT_DIR / "paper1_24h_mean.csv", index=False, encoding="utf-8-sig")
    literature.to_csv(OUTPUT_DIR / "literature_24h_data.csv", index=False, encoding="utf-8-sig")

    build_fig_permeation_landscape(mean_24h, literature)
    build_fig_experimental_conditions(mean_24h, literature)
    build_plot_support_csvs(funnel_counts)
    write_excipient_match_report(detail, funnel_counts, meta)
    benchmarking_text = write_benchmarking_analysis(raw, mean_24h, funnel_counts, meta)
    final_summary_text = write_final_summary(mean_24h, funnel_counts)

    payload = {
        "paper1_raw_csv": str(OUTPUT_DIR / "paper1_raw_data.csv"),
        "paper1_replicates_csv": str(OUTPUT_DIR / "paper1_24h_all_replicates.csv"),
        "paper1_mean_csv": str(OUTPUT_DIR / "paper1_24h_mean.csv"),
        "literature_24h_csv": str(OUTPUT_DIR / "literature_24h_data.csv"),
        "excipient_match_results_md": str(OUTPUT_DIR / "excipient_match_results.md"),
        "excipient_match_detail_csv": str(OUTPUT_DIR / "excipient_match_detail.csv"),
        "benchmarking_analysis_md": str(OUTPUT_DIR / "benchmarking_analysis.md"),
        "demonstration_final_summary_md": str(OUTPUT_DIR / "demonstration_final_summary.md"),
        "paper1_formulations": int(mean_24h["formulation_id"].nunique()),
        "paper1_rows": int(len(raw)),
        "funnel_counts": funnel_counts,
        "level3_term_counts": meta["level3_term_counts"],
        "benchmarking_summary_chars": len(benchmarking_text),
        "final_summary_chars": len(final_summary_text),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
