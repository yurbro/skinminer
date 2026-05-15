from __future__ import annotations

import copy
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

# Source field decisions:
# - GPT policy provenance comes from these existing rescore JSONL files:
#   outputs/full_run_16_post_all_fixes/v2_rescore/verified_records.jsonl
#   outputs/full_run_16_post_all_fixes/v3_rescore/verified_records.jsonl
#   outputs/full_run_16_post_all_fixes/v4_rescore/verified_records.jsonl
# - Claude cross-reference provenance comes from:
#   outputs/experiment_E3_claude_v2/v2_rescore/verified_records.jsonl
# - Unresolved/rejected fallback records are also read from the latest v4
#   policy files plus patched_area/patched_* and assembled_records JSONL files
#   in both source runs. No extractors, PDFs, APIs, or LLMs are called.
# - Core extracted fields are read from formulation.*, endpoint.*,
#   conditions.*, route, evidence_items, verification_status, and scope_bucket.

GPT_RUN = ROOT / "outputs" / "full_run_16_post_all_fixes"
CLAUDE_RUN = ROOT / "outputs" / "experiment_E3_claude_v2"
OUTPUT_DIR = ROOT / "outputs" / "phase0b_stage1"
REPORT_PATH = ROOT / "reports" / "phase0b_stage1_ibuprofen_audit.md"

ALL_RECORDS_PATH = OUTPUT_DIR / "all_ibuprofen_records.jsonl"
PAPER_SUMMARY_PATH = OUTPUT_DIR / "paper_level_summary.csv"
PAIR_COMPAT_PATH = OUTPUT_DIR / "paper_pair_compatibility.csv"
FACTOR_MATRIX_PATH = OUTPUT_DIR / "factor_coverage_matrix.csv"
GO_NOGO_PATH = OUTPUT_DIR / "go_nogo_decision.md"

API_RE = re.compile(r"\b(ibuprofen sodium|ibuprofen lysine|ibuprofen)\b", re.I)
IBUPROFEN_MENTION_RE = re.compile(r"ibuprofen", re.I)

PROVENANCE_RANK = {
    "verified_v2_gpt": 0,
    "verified_v2_claude": 1,
    "verified_v3_gpt_only": 2,
    "verified_v4_gpt_only": 3,
    "unresolved": 4,
    "rejected": 5,
}

SOURCE_PATH_PRIORITY = {
    "v4_rescore": 100,
    "v3_rescore": 90,
    "v2_rescore": 80,
    "verified_records": 70,
    "patched_endpoint_value": 64,
    "patched_endpoint_time": 63,
    "patched_api_concentration": 62,
    "patched_area": 61,
    "assembled_records": 50,
}

TIME_TO_HOURS = {
    "h": 1.0,
    "hr": 1.0,
    "hrs": 1.0,
    "hour": 1.0,
    "hours": 1.0,
    "d": 24.0,
    "day": 24.0,
    "days": 24.0,
    "min": 1.0 / 60.0,
    "mins": 1.0 / 60.0,
    "minute": 1.0 / 60.0,
    "minutes": 1.0 / 60.0,
}

VALUE_STATUSES = {"present_with_value", "present_with_range"}

BUCKET_SPECS: list[tuple[str, list[str]]] = [
    ("cosolvent_pg", [r"propylene glycol", r"\bPG\b"]),
    ("cosolvent_etoh", [r"\bethanol\b", r"\bEtOH\b", r"(?<!poly)\balcohol\b"]),
    ("cosolvent_water", [r"\bwater\b", r"aqueous"]),
    ("cosolvent_glycerin", [r"glycerin", r"glycerol"]),
    ("cosolvent_dmso", [r"\bDMSO\b", r"dimethyl sulfoxide"]),
    ("cosolvent_other", [r"transcutol", r"\bDMI\b", r"N-methyl pyrrolidone", r"\bNMP\b"]),
    ("polymer_hpmc", [r"\bHPMC\b", r"hydroxypropyl methylcellulose", r"hypromellose"]),
    ("polymer_carbopol", [r"carbopol", r"carbomer"]),
    ("polymer_poloxamer", [r"poloxamer", r"pluronic"]),
    ("polymer_other", [r"\bPVP\b", r"chitosan", r"xanthan", r"alginate", r"cellulose"]),
    ("surfactant_tween", [r"tween", r"polysorbate"]),
    ("surfactant_span", [r"\bspan\s*\d+", r"\bspan\b"]),
    (
        "surfactant_sls",
        [r"\bSLS\b", r"sodium lauryl sulfate", r"sodium dodecyl sulfate", r"\bSDS\b"],
    ),
    ("surfactant_tpgs", [r"\bTPGS\b", r"vit\.?\s?E TPGS"]),
    ("surfactant_other", [r"cremophor", r"labrasol", r"solutol", r"kolliphor"]),
    ("enhancer_terpene", [r"limonene", r"menthol", r"eucalyptol", r"terpene"]),
    ("enhancer_fatty_acid", [r"oleic acid", r"linoleic acid", r"lauric acid"]),
    ("enhancer_azone", [r"\bazone\b", r"laurocapram"]),
    ("enhancer_ipm", [r"isopropyl myristate", r"\bIPM\b"]),
    ("oil_mineral", [r"mineral oil", r"paraffin", r"liquid paraffin"]),
    ("oil_silicone", [r"silicone oil", r"dimethicone"]),
    (
        "nano_carrier",
        [r"liposome", r"niosome", r"nanoemulsion", r"nanoparticle", r"\bSLN\b", r"\bNLC\b", r"microemulsion"],
    ),
    ("microneedle_or_iontophoresis", [r"microneedle", r"ionto", r"electroporation"]),
]

BUCKETS = [bucket for bucket, _ in BUCKET_SPECS]
COMPILED_BUCKETS = [
    (bucket, [re.compile(pattern, re.I) for pattern in patterns]) for bucket, patterns in BUCKET_SPECS
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def normalize_ws(value: Any) -> str:
    return " ".join(str(value or "").split())


def norm_doi(value: Any) -> str:
    return normalize_ws(value).lower()


def to_float(value: Any) -> float | None:
    if value in [None, ""]:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return numeric


def round_float(value: Any, digits: int = 6) -> float | None:
    numeric = to_float(value)
    if numeric is None:
        return None
    return round(numeric, digits)


def format_number(value: Any) -> str:
    numeric = to_float(value)
    if numeric is None:
        return normalize_ws(value)
    if abs(numeric - round(numeric)) < 1e-9:
        return str(int(round(numeric)))
    return f"{numeric:.6g}"


def clean_unit(unit: Any) -> str:
    text = normalize_ws(unit)
    replacements = {
        "渭": "u",
        "碌": "u",
        "µ": "u",
        "μ": "u",
        "虏": "^2",
        "²": "^2",
        "／": "/",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = text.replace("cm2", "cm^2").replace("cm 2", "cm^2")
    return text


def normalized_unit(unit: Any) -> str:
    text = clean_unit(unit).lower()
    text = text.replace(" ", "")
    text = text.replace("per", "/")
    text = text.replace("ug/cm^2/hours", "ug/cm^2/h")
    text = text.replace("ug/cm^2/hour", "ug/cm^2/h")
    return text


def api_name(record: dict[str, Any]) -> str:
    formulation = record.get("formulation") or {}
    return normalize_ws(formulation.get("api_name") or record.get("api_name") or "")


def is_ibuprofen_pool_record(record: dict[str, Any]) -> bool:
    return bool(API_RE.search(api_name(record)))


def is_near_miss_api_name(name: str) -> bool:
    lower = name.lower().strip()
    if "ibuprofen" not in lower:
        return False
    canonical = {
        "ibuprofen",
        "ibuprofen sodium",
        "ibuprofen lysine",
        "ibuprofen sodium (ibu na)",
    }
    if lower in canonical:
        return False
    near_tokens = ["ester", "conjugate", "peg", "s(+)", "s-", "r(-)", "r-"]
    return any(token in lower for token in near_tokens) or lower not in canonical


def source_priority(path: Path) -> int:
    rendered = str(path).replace("\\", "/")
    for token, priority in SOURCE_PATH_PRIORITY.items():
        if token in rendered:
            return priority
    return 0


def row_completeness(record: dict[str, Any]) -> int:
    formulation = record.get("formulation") or {}
    endpoint = record.get("endpoint") or {}
    conditions = record.get("conditions") or {}
    components = formulation.get("components") or []
    score = 0
    for value in [
        formulation.get("api_concentration_value"),
        formulation.get("api_concentration_unit"),
        endpoint.get("value"),
        endpoint.get("unit"),
        endpoint.get("time_value"),
        endpoint.get("time_unit"),
        endpoint.get("normalized_value"),
        endpoint.get("normalized_unit"),
        conditions.get("membrane_type"),
        conditions.get("dose_type"),
    ]:
        if value not in [None, ""]:
            score += 1
    score += min(len(components), 5)
    score += min(len(record.get("evidence_items") or []), 5)
    return score


def normalise_endpoint_kind(kind: Any) -> str:
    text = normalize_ws(kind).lower()
    if not text:
        return ""
    if text in {"amount_total", "amount_per_area", "amount"}:
        return "cumulative_amount"
    if "cumulative" in text or "amount" in text or "q" == text:
        return "cumulative_amount"
    if text in {"jss", "flux", "steady_state_flux"} or "flux" in text:
        return "flux"
    if text in {"kp", "k_p", "permeability_coefficient"} or "permeability" in text:
        return "kp"
    if "lag" in text:
        return "lag_time"
    if "papp" in text:
        return "papp"
    return text


def endpoint_unit(record: dict[str, Any]) -> str:
    endpoint = record.get("endpoint") or {}
    unit = endpoint.get("normalized_unit") or endpoint.get("unit") or ""
    return normalized_unit(unit)


def endpoint_value(record: dict[str, Any]) -> float | None:
    endpoint = record.get("endpoint") or {}
    value = endpoint.get("normalized_value")
    if value in [None, ""]:
        value = endpoint.get("value")
    return round_float(value)


def endpoint_time_value_unit(record: dict[str, Any]) -> tuple[float | None, str]:
    endpoint = record.get("endpoint") or {}
    value = endpoint.get("time_value")
    unit = normalize_ws(endpoint.get("time_unit") or "")
    if value in [None, ""]:
        conditions = record.get("conditions") or {}
        value = conditions.get("duration_h")
        unit = "h" if value not in [None, ""] else unit
    return to_float(value), unit


def time_to_hours(value: Any, unit: Any) -> float | None:
    numeric = to_float(value)
    if numeric is None:
        return None
    factor = TIME_TO_HOURS.get(normalize_ws(unit).lower())
    if factor is None:
        return None
    return round(numeric * factor, 6)


def endpoint_time_h(record: dict[str, Any]) -> float | None:
    value, unit = endpoint_time_value_unit(record)
    return time_to_hours(value, unit)


def format_time_h(value: float | None) -> str:
    if value is None:
        return ""
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value))}h"
    return f"{value:.3g}h"


def membrane_type(record: dict[str, Any]) -> str:
    conditions = record.get("conditions") or {}
    return normalize_ws(conditions.get("membrane_type") or record.get("barrier") or "")


def normalize_membrane(value: Any) -> str:
    text = normalize_ws(value).lower()
    if not text:
        return ""
    text = text.replace("dermatomed", "").replace("excised", "")
    text = re.sub(r"\s+", " ", text).strip(" ;,")
    if "strat-m" in text or "strat m" in text:
        return "strat-m"
    if "human" in text and "skin" in text:
        return "human skin"
    if ("porcine" in text or "pig" in text) and "skin" in text:
        return "porcine skin"
    if "rat" in text and "skin" in text:
        return "rat skin"
    if "mouse" in text and "skin" in text:
        return "mouse skin"
    if "stratum corneum" in text:
        return "stratum corneum"
    return text


def dose_mode(record: dict[str, Any]) -> str:
    conditions = record.get("conditions") or {}
    text = normalize_ws(conditions.get("dose_type") or record.get("dose_mode") or "").lower()
    if text in {"finite", "infinite"}:
        return text
    if "finite" in text:
        return "finite"
    if "infinite" in text:
        return "infinite"
    return "unspecified"


def extraction_sources(record: dict[str, Any]) -> set[str]:
    sources: set[str] = set()
    route = normalize_ws(record.get("route") or "").lower()
    if route in {"table", "text", "figure"}:
        sources.add(route)
    for evidence in record.get("evidence_items") or []:
        modality = normalize_ws(evidence.get("modality") or "").lower()
        if modality in {"table", "text", "figure"}:
            sources.add(modality)
    if not sources and route:
        sources.add(route)
    return sources


def extraction_source_label(record: dict[str, Any]) -> str:
    sources = sorted(extraction_sources(record))
    if not sources:
        return "unspecified"
    if len(sources) == 1:
        return sources[0]
    return "mixed"


def component_display(component: dict[str, Any]) -> str:
    parts = []
    for key in ["name", "concentration_value", "concentration_unit", "basis", "raw", "note", "type"]:
        value = component.get(key)
        if value not in [None, ""]:
            parts.append(normalize_ws(value))
    return " ".join(parts)


def component_name_text(component: dict[str, Any]) -> str:
    return " ".join(
        normalize_ws(component.get(key))
        for key in ["name", "raw", "type"]
        if component.get(key) not in [None, ""]
    )


def top_level_components(record: dict[str, Any]) -> list[dict[str, Any]]:
    formulation = record.get("formulation") or {}
    rendered: list[dict[str, Any]] = []
    for component in formulation.get("components") or []:
        rendered.append(
            {
                "name": component.get("name") or "",
                "type": component.get("type") or component.get("basis") or "",
                "value": component.get("value", component.get("concentration_value")),
                "unit": component.get("unit", component.get("concentration_unit") or ""),
                "raw": component.get("raw") or "",
                "note": component.get("note") or "",
            }
        )
    return rendered


def formulation_signature(record: dict[str, Any]) -> str:
    formulation = record.get("formulation") or {}
    components = formulation.get("components") or []
    component_payload: list[tuple[Any, ...]] = []
    for component in components:
        component_payload.append(
            (
                normalize_ws(component.get("name")).lower(),
                round_float(component.get("concentration_value")),
                normalized_unit(component.get("concentration_unit") or ""),
                normalize_ws(component.get("basis")).lower(),
                normalize_ws(component.get("raw")).lower(),
                normalize_ws(component.get("note")).lower(),
            )
        )
    payload = {
        "label": normalize_ws(formulation.get("label")).lower(),
        "api_name": api_name(record).lower(),
        "api_conc_value": round_float(formulation.get("api_concentration_value")),
        "api_conc_unit": normalized_unit(formulation.get("api_concentration_unit") or ""),
        "api_basis": normalize_ws(formulation.get("api_basis")).lower(),
        "dosage_form": normalize_ws(formulation.get("dosage_form")).lower(),
        "components": sorted(component_payload),
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=True)


def content_dedupe_key(record: dict[str, Any]) -> tuple[Any, ...]:
    endpoint = record.get("endpoint") or {}
    return (
        norm_doi(record.get("doi")),
        formulation_signature(record),
        normalise_endpoint_kind(endpoint.get("kind")),
        round_float(endpoint_time_h(record)),
        endpoint_value(record),
        endpoint_unit(record),
    )


def record_id_key(record: dict[str, Any]) -> tuple[Any, ...]:
    record_id = normalize_ws(record.get("record_id"))
    if not record_id:
        return content_dedupe_key(record)
    return ("record_id", norm_doi(record.get("doi")), record_id)


def compile_policy_sets() -> dict[str, set[str]]:
    paths = {
        "gpt_v2": GPT_RUN / "v2_rescore" / "verified_records.jsonl",
        "gpt_v3": GPT_RUN / "v3_rescore" / "verified_records.jsonl",
        "gpt_v4": GPT_RUN / "v4_rescore" / "verified_records.jsonl",
        "claude_v2": CLAUDE_RUN / "v2_rescore" / "verified_records.jsonl",
    }
    result: dict[str, set[str]] = {}
    for name, path in paths.items():
        result[name] = {
            normalize_ws(row.get("record_id"))
            for row in load_jsonl(path)
            if row.get("verification_status") == "verified" and normalize_ws(row.get("record_id"))
        }
    return result


def source_specs(policy_sets: dict[str, set[str]]) -> list[dict[str, Any]]:
    def verified_filter(status: str) -> bool:
        return status == "verified"

    def unresolved_filter(status: str) -> bool:
        return status in {"unresolved", "pending"}

    def rejected_filter(status: str) -> bool:
        return status == "rejected"

    return [
        {
            "path": GPT_RUN / "v2_rescore" / "verified_records.jsonl",
            "tag": "verified_v2_gpt",
            "filter": verified_filter,
            "record_filter": lambda row: True,
        },
        {
            "path": GPT_RUN / "v3_rescore" / "verified_records.jsonl",
            "tag": "verified_v3_gpt_only",
            "filter": verified_filter,
            "record_filter": lambda row: normalize_ws(row.get("record_id")) not in policy_sets["gpt_v2"],
        },
        {
            "path": GPT_RUN / "v4_rescore" / "verified_records.jsonl",
            "tag": "verified_v4_gpt_only",
            "filter": verified_filter,
            "record_filter": lambda row: normalize_ws(row.get("record_id")) not in policy_sets["gpt_v3"],
        },
        {
            "path": CLAUDE_RUN / "v2_rescore" / "verified_records.jsonl",
            "tag": "verified_v2_claude",
            "filter": verified_filter,
            "record_filter": lambda row: True,
        },
        {
            "path": GPT_RUN / "v4_rescore" / "verified_records.jsonl",
            "tag": "unresolved",
            "filter": unresolved_filter,
            "record_filter": lambda row: True,
        },
        {
            "path": GPT_RUN / "v4_rescore" / "verified_records.jsonl",
            "tag": "rejected",
            "filter": rejected_filter,
            "record_filter": lambda row: True,
        },
        {
            "path": CLAUDE_RUN / "v2_rescore" / "verified_records.jsonl",
            "tag": "unresolved",
            "filter": unresolved_filter,
            "record_filter": lambda row: True,
        },
        {
            "path": CLAUDE_RUN / "v2_rescore" / "verified_records.jsonl",
            "tag": "rejected",
            "filter": rejected_filter,
            "record_filter": lambda row: True,
        },
    ]


def fallback_source_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    filenames = [
        "assembled_records.jsonl",
        "patched_area.jsonl",
        "patched_api_concentration.jsonl",
        "patched_endpoint_time.jsonl",
        "patched_endpoint_value.jsonl",
    ]
    for run in [GPT_RUN, CLAUDE_RUN]:
        for filename in filenames:
            path = run / filename
            specs.append(
                {
                    "path": path,
                    "tag": "unresolved",
                    "filter": lambda status: status in {"pending", "unresolved"},
                    "record_filter": lambda row: True,
                }
            )
            specs.append(
                {
                    "path": path,
                    "tag": "rejected",
                    "filter": lambda status: status == "rejected",
                    "record_filter": lambda row: True,
                }
            )
    return specs


def annotate_record(record: dict[str, Any], tag: str, path: Path) -> dict[str, Any]:
    payload = copy.deepcopy(record)
    original_provenance = payload.get("provenance")
    if isinstance(original_provenance, dict):
        payload["source_extraction_provenance"] = original_provenance
    payload["provenance"] = tag
    payload["source_provenances"] = [tag]
    payload["source_jsonl_paths"] = [str(path.relative_to(ROOT))]
    payload["source_jsonl_priority"] = source_priority(path)
    payload["api_name"] = api_name(payload)
    formulation = payload.get("formulation") or {}
    endpoint = payload.get("endpoint") or {}
    payload["api_concentration_value"] = formulation.get("api_concentration_value")
    payload["api_concentration_unit"] = clean_unit(formulation.get("api_concentration_unit") or "")
    payload["components"] = top_level_components(payload)
    payload["endpoint_kind"] = normalise_endpoint_kind(endpoint.get("kind"))
    payload["endpoint_value"] = endpoint_value(payload)
    payload["endpoint_unit"] = endpoint_unit(payload)
    time_value, time_unit = endpoint_time_value_unit(payload)
    payload["time_value"] = time_value
    payload["time_unit"] = time_unit
    payload["time_h"] = endpoint_time_h(payload)
    payload["membrane_type"] = membrane_type(payload)
    payload["membrane_type_normalized"] = normalize_membrane(payload["membrane_type"])
    payload["dose_mode"] = dose_mode(payload)
    payload["extraction_source"] = extraction_source_label(payload)
    payload["api_near_miss_review"] = is_near_miss_api_name(payload["api_name"])
    return payload


def merge_record_lists(records: list[dict[str, Any]], key_fn) -> list[dict[str, Any]]:
    selected: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in records:
        key = key_fn(record)
        previous = selected.get(key)
        if previous is None:
            selected[key] = record
            continue

        merged_sources = sorted(set(previous.get("source_provenances", [])) | set(record.get("source_provenances", [])))
        merged_paths = sorted(set(previous.get("source_jsonl_paths", [])) | set(record.get("source_jsonl_paths", [])))
        prev_rank = PROVENANCE_RANK.get(previous["provenance"], 99)
        curr_rank = PROVENANCE_RANK.get(record["provenance"], 99)
        prev_score = (prev_rank, -row_completeness(previous), -int(previous.get("source_jsonl_priority") or 0))
        curr_score = (curr_rank, -row_completeness(record), -int(record.get("source_jsonl_priority") or 0))
        winner = record if curr_score < prev_score else previous
        winner = copy.deepcopy(winner)
        winner["source_provenances"] = merged_sources
        winner["source_jsonl_paths"] = merged_paths
        winner["provenance"] = min(merged_sources, key=lambda item: PROVENANCE_RANK.get(item, 99))
        selected[key] = winner
    return list(selected.values())


def collect_union_pool() -> tuple[list[dict[str, Any]], Counter, Counter]:
    policy_sets = compile_policy_sets()
    candidates: list[dict[str, Any]] = []
    near_miss_names: Counter = Counter()
    excluded_ibuprofen_mentions: Counter = Counter()

    for spec in [*source_specs(policy_sets), *fallback_source_specs()]:
        path = spec["path"]
        if not path.exists():
            continue
        for row in load_jsonl(path):
            status = str(row.get("verification_status") or "pending")
            if not spec["filter"](status):
                continue
            if not spec["record_filter"](row):
                continue
            name = api_name(row)
            if not is_ibuprofen_pool_record(row):
                if IBUPROFEN_MENTION_RE.search(name):
                    excluded_ibuprofen_mentions[name] += 1
                continue
            if is_near_miss_api_name(name):
                near_miss_names[name] += 1
            candidates.append(annotate_record(row, spec["tag"], path))

    by_record_id = merge_record_lists(candidates, record_id_key)
    by_content = merge_record_lists(by_record_id, content_dedupe_key)
    by_content.sort(key=lambda row: (norm_doi(row.get("doi")), PROVENANCE_RANK.get(row["provenance"], 99), row.get("record_id") or ""))
    return by_content, near_miss_names, excluded_ibuprofen_mentions


def match_bucket(text: str, bucket: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    if bucket == "cosolvent_pg" and "polyethylene glycol" in lower and "propylene glycol" not in lower:
        return False
    if bucket == "polymer_other" and (
        re.search(r"\bHPMC\b", text, re.I)
        or re.search(r"hydroxypropyl methylcellulose", text, re.I)
        or re.search(r"hypromellose", text, re.I)
    ):
        return False
    for candidate, patterns in COMPILED_BUCKETS:
        if candidate != bucket:
            continue
        return any(pattern.search(text) for pattern in patterns)
    return False


def buckets_for_text(text: str) -> list[str]:
    matches: list[str] = []
    for bucket in BUCKETS:
        if match_bucket(text, bucket):
            matches.append(bucket)
    if "polymer_hpmc" in matches and "polymer_other" in matches:
        matches.remove("polymer_other")
    return matches


def numeric_component_value(component: dict[str, Any]) -> tuple[float | None, str]:
    value = component.get("concentration_value", component.get("value"))
    unit = component.get("concentration_unit", component.get("unit") or "")
    numeric = to_float(value)
    if numeric is None:
        return None, clean_unit(unit)
    if abs(numeric) < 1e-12:
        return None, clean_unit(unit)
    return round(numeric, 6), clean_unit(unit)


def ratio_value_for_bucket(text: str, bucket: str) -> float | None:
    ratio = re.search(r"(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)", text)
    if not ratio:
        return None
    first = float(ratio.group(1))
    second = float(ratio.group(2))
    lower = text.lower()
    if bucket == "cosolvent_pg" and ("propylene glycol" in lower or re.search(r"\bpg\b", lower)):
        if re.search(r"(propylene glycol|pg)\s*/\s*water", lower):
            return first
        if re.search(r"water\s*/\s*(propylene glycol|pg)", lower):
            return second
        return first
    if bucket == "cosolvent_water" and "water" in lower:
        if re.search(r"(propylene glycol|pg|ethanol|etoh)\s*/\s*water", lower):
            return second
        if re.search(r"water\s*/\s*(propylene glycol|pg|ethanol|etoh)", lower):
            return first
        return second
    if bucket == "cosolvent_etoh" and ("ethanol" in lower or "etoh" in lower):
        if re.search(r"(ethanol|etoh)\s*/\s*water", lower):
            return first
        if re.search(r"water\s*/\s*(ethanol|etoh)", lower):
            return second
    return None


def percent_values_in_text(text: str) -> list[float]:
    values: list[float] = []
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:%|percent|w/w|w/v|v/v)", text, re.I):
        values.append(round(float(match.group(1)), 6))
    return values


def bucket_value_for_component(component: dict[str, Any], bucket: str) -> tuple[float | None, str]:
    full_text = component_display(component)
    ratio_value = ratio_value_for_bucket(full_text, bucket)
    unit = clean_unit(component.get("concentration_unit") or component.get("unit") or "")
    if ratio_value is not None:
        return round(ratio_value, 6), "%"

    name_text = component_name_text(component)
    if match_bucket(name_text, bucket):
        numeric, component_unit = numeric_component_value(component)
        if numeric is not None:
            return numeric, component_unit

    pct_values = percent_values_in_text(full_text)
    if len(pct_values) == 1:
        return pct_values[0], "%"
    return None, unit


def descriptor_components(record: dict[str, Any]) -> list[dict[str, Any]]:
    formulation = record.get("formulation") or {}
    descriptors = []
    for field in ["label", "api_concentration_raw", "dosage_form", "api_basis"]:
        value = normalize_ws(formulation.get(field))
        if value:
            descriptors.append({"name": value, "raw": value, "basis": f"formulation.{field}"})
    return descriptors


def bucket_observations(record: dict[str, Any]) -> dict[str, list[tuple[float | None, str, str]]]:
    observations: dict[str, list[tuple[float | None, str, str]]] = defaultdict(list)
    formulation = record.get("formulation") or {}
    components = list(formulation.get("components") or []) + descriptor_components(record)
    for component in components:
        text = component_display(component)
        for bucket in buckets_for_text(text):
            value, unit = bucket_value_for_component(component, bucket)
            observations[bucket].append((value, unit, normalize_ws(component.get("name") or text)))
    return observations


def paper_records_for_analysis(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_doi[norm_doi(record.get("doi"))].append(record)
    analysis_records: list[dict[str, Any]] = []
    for doi_records in by_doi.values():
        non_rejected = [row for row in doi_records if row["provenance"] != "rejected"]
        analysis_records.extend(non_rejected if non_rejected else doi_records)
    return analysis_records


def bucket_status_for_records(records: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, list[tuple[float, str]]], dict[str, list[str]]]:
    bucket_values: dict[str, set[tuple[float, str]]] = {bucket: set() for bucket in BUCKETS}
    bucket_examples: dict[str, list[str]] = {bucket: [] for bucket in BUCKETS}
    present: set[str] = set()
    for record in records:
        for bucket, observations in bucket_observations(record).items():
            present.add(bucket)
            for value, unit, label in observations:
                if label and len(bucket_examples[bucket]) < 5:
                    bucket_examples[bucket].append(label)
                if value is not None:
                    bucket_values[bucket].add((round(value, 6), unit))

    statuses: dict[str, str] = {}
    rendered_values: dict[str, list[tuple[float, str]]] = {}
    for bucket in BUCKETS:
        values = sorted(bucket_values[bucket])
        rendered_values[bucket] = values
        distinct_numeric = {value for value, _unit in values}
        if bucket not in present:
            statuses[bucket] = "absent"
        elif len(distinct_numeric) >= 2:
            statuses[bucket] = "present_with_range"
        elif values:
            statuses[bucket] = "present_with_value"
        else:
            statuses[bucket] = "present_qualitative"
    return statuses, rendered_values, bucket_examples


def distinct_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def list_cell(values: list[str]) -> str:
    return "[" + ", ".join(values) + "]"


def api_concentration_label(record: dict[str, Any]) -> str:
    formulation = record.get("formulation") or {}
    value = formulation.get("api_concentration_value")
    unit = clean_unit(formulation.get("api_concentration_unit") or "")
    if value in [None, ""]:
        raw = normalize_ws(formulation.get("api_concentration_raw"))
        return raw
    return f"{format_number(value)}{unit}"


def factor_summary(statuses: dict[str, str], values: dict[str, list[tuple[float, str]]]) -> str:
    pieces: list[str] = []
    for bucket in BUCKETS:
        status = statuses[bucket]
        if status == "absent":
            continue
        bucket_values = values.get(bucket) or []
        if bucket_values:
            rendered = ",".join(
                f"{format_number(value)}{unit}" if unit else format_number(value)
                for value, unit in bucket_values[:5]
            )
            if len(bucket_values) > 5:
                rendered += ",..."
            pieces.append(f"{bucket}:{rendered}")
        else:
            pieces.append(f"{bucket}:qualitative")
    return ";".join(pieces) if pieces else "none"


def compute_modelling_score(
    n_records: int,
    internal_factor_variation: bool,
    endpoint_unit_consistency: bool,
    has_24h: bool,
    has_v2_gpt: bool,
    table_records: int,
    bucket_statuses: dict[str, str],
) -> int:
    score = 0
    if n_records >= 8:
        score += 30
    elif n_records >= 5:
        score += 20
    elif n_records >= 3:
        score += 10
    if internal_factor_variation:
        score += 20
    if endpoint_unit_consistency:
        score += 15
    if has_24h:
        score += 10
    if has_v2_gpt:
        score += 10
    if n_records and table_records >= n_records / 2:
        score += 10
    # The task text contains a mojibake minus for these two penalties; use -10.
    if bucket_statuses.get("microneedle_or_iontophoresis") != "absent":
        score -= 10
    if bucket_statuses.get("nano_carrier") != "absent":
        score -= 10
    return max(0, min(100, score))


def build_paper_summary(records: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, Any]]]:
    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        all_by_doi[norm_doi(record.get("doi"))].append(record)
    analysis_records = paper_records_for_analysis(records)
    for record in analysis_records:
        by_doi[norm_doi(record.get("doi"))].append(record)

    summary_rows: list[dict[str, Any]] = []
    factor_rows: list[dict[str, Any]] = []
    paper_info: dict[str, dict[str, Any]] = {}

    for doi in sorted(by_doi):
        doi_records = by_doi[doi]
        n_records = len(doi_records)
        statuses, bucket_values, bucket_examples = bucket_status_for_records(doi_records)
        endpoint_kinds = distinct_sorted([row.get("endpoint_kind") or "" for row in doi_records])
        endpoint_units = distinct_sorted([endpoint_unit(row) for row in doi_records])
        endpoint_unit_consistency = len(endpoint_units) == 1 and bool(endpoint_units[0])
        time_hours = sorted({value for row in doi_records if (value := endpoint_time_h(row)) is not None})
        time_labels = [format_time_h(value) for value in time_hours]
        has_24h = any(abs(value - 24.0) <= 1.0 for value in time_hours)
        has_72h = any(abs(value - 72.0) <= 1.0 for value in time_hours)
        membranes = distinct_sorted([normalize_membrane(membrane_type(row)) for row in doi_records])
        dose_modes = distinct_sorted([dose_mode(row) for row in doi_records])
        formulation_signatures = {formulation_signature(row) for row in doi_records}
        internal_factor_variation = len(formulation_signatures) >= 5 and any(
            status == "present_with_range" for status in statuses.values()
        )
        extraction_counts = Counter()
        for row in doi_records:
            for source in extraction_sources(row):
                if source in {"table", "text", "figure"}:
                    extraction_counts[source] += 1
        source_provenance_counts = Counter(
            source for row in doi_records for source in row.get("source_provenances", [])
        )
        primary_provenance_counts = Counter(row["provenance"] for row in doi_records)
        rejected_only = all(row["provenance"] == "rejected" for row in all_by_doi[doi])
        score = compute_modelling_score(
            n_records=n_records,
            internal_factor_variation=internal_factor_variation,
            endpoint_unit_consistency=endpoint_unit_consistency,
            has_24h=has_24h,
            has_v2_gpt=source_provenance_counts["verified_v2_gpt"] > 0,
            table_records=extraction_counts["table"],
            bucket_statuses=statuses,
        )
        row = {
            "doi": doi,
            "n_records_total": n_records,
            "n_records_v2": source_provenance_counts["verified_v2_gpt"],
            "n_records_v2_claude": source_provenance_counts["verified_v2_claude"],
            "n_records_v3_only": source_provenance_counts["verified_v3_gpt_only"],
            "n_records_v4_only": source_provenance_counts["verified_v4_gpt_only"],
            "n_records_unresolved": primary_provenance_counts["unresolved"],
            "n_records_rejected": primary_provenance_counts["rejected"],
            "rejected_only": rejected_only,
            "n_records_extraction_table": extraction_counts["table"],
            "n_records_extraction_text": extraction_counts["text"],
            "n_records_extraction_figure": extraction_counts["figure"],
            "api_conc_values": list_cell(distinct_sorted([api_concentration_label(row) for row in doi_records])),
            "api_conc_n_distinct": len({api_concentration_label(row) for row in doi_records if api_concentration_label(row)}),
            "endpoint_kinds": ";".join(endpoint_kinds),
            "endpoint_units": ";".join(endpoint_units),
            "endpoint_unit_consistency": endpoint_unit_consistency,
            "time_values": list_cell(time_labels),
            "time_n_distinct": len(time_hours),
            "has_24h": has_24h,
            "has_72h": has_72h,
            "membrane_types": ";".join(membranes),
            "membrane_n_distinct": len(membranes),
            "dose_modes": ";".join(dose_modes),
            "formulation_factor_summary": factor_summary(statuses, bucket_values),
            "n_distinct_formulations": len(formulation_signatures),
            "internal_factor_variation": internal_factor_variation,
            "modelling_candidate_score": score,
            "near_miss_api_records": sum(1 for row in doi_records if row.get("api_near_miss_review")),
        }
        summary_rows.append(row)
        factor_row = {"doi": doi, **{bucket: statuses[bucket] for bucket in BUCKETS}}
        factor_rows.append(factor_row)
        paper_info[doi] = {
            "records": doi_records,
            "summary": row,
            "factor_statuses": statuses,
            "factor_values": bucket_values,
            "factor_examples": bucket_examples,
            "endpoint_kinds": set(endpoint_kinds),
            "endpoint_units": set(endpoint_units),
            "time_hours": time_hours,
            "membranes": set(membranes),
            "score": score,
        }

    summary_df = pd.DataFrame(summary_rows)
    factor_df = pd.DataFrame(factor_rows)
    return summary_df, factor_df, paper_info


def shared_time_points(a_times: list[float], b_times: list[float], tolerance_h: float = 1.0) -> list[str]:
    matches: list[float] = []
    used_b: set[int] = set()
    for a_time in sorted(a_times):
        for idx, b_time in enumerate(sorted(b_times)):
            if idx in used_b:
                continue
            if abs(a_time - b_time) <= tolerance_h:
                matches.append((a_time + b_time) / 2.0)
                used_b.add(idx)
                break
    deduped: list[float] = []
    for value in matches:
        rounded = round(value, 3)
        if rounded not in deduped:
            deduped.append(rounded)
    return [format_time_h(value) for value in deduped]


def classify_pair(
    shared_buckets: list[str],
    range_in_a: list[str],
    shared_endpoint_kinds: set[str],
    shared_endpoint_units: set[str],
    endpoint_units_identical: bool,
    shared_times: list[str],
    shared_membranes: set[str],
    n_records_a: int,
    n_records_b: int,
) -> tuple[str, str]:
    if not shared_buckets:
        return "INCOMPATIBLE", "No shared formulation-factor bucket with numeric/range values."
    if not shared_endpoint_kinds:
        return "INCOMPATIBLE", "No shared endpoint kind."
    if not shared_membranes:
        return "INCOMPATIBLE", "No shared membrane type."
    # Strong is checked before moderate because the strong rule is a strict subset
    # of moderate in the task wording.
    if (
        len(shared_buckets) >= 2
        and range_in_a
        and n_records_a >= 5
        and n_records_b >= 5
        and len(shared_times) >= 2
        and endpoint_units_identical
    ):
        return "STRONG", "Shared numeric factors, source-side factor range, two aligned times, and identical endpoint-unit sets."
    if len(shared_buckets) >= 2 and shared_times and n_records_a >= 5 and n_records_b >= 3:
        unit_note = " Endpoint units overlap." if shared_endpoint_units else " Endpoint units do not directly overlap."
        return "MODERATE", "At least two shared numeric factors and one aligned time point." + unit_note
    if len(shared_buckets) == 1 and not shared_times:
        return "WEAK", "One shared numeric factor but no aligned time point."
    return "WEAK", "Basic factor/endpoint/membrane overlap exists but does not meet MODERATE thresholds."


def build_pair_compatibility(summary_df: pd.DataFrame, paper_info: dict[str, dict[str, Any]]) -> pd.DataFrame:
    eligible = [
        row["doi"]
        for row in summary_df.to_dict("records")
        if int(row["n_records_total"]) >= 3
    ]
    rows: list[dict[str, Any]] = []
    for doi_a in eligible:
        for doi_b in eligible:
            if doi_a == doi_b:
                continue
            info_a = paper_info[doi_a]
            info_b = paper_info[doi_b]
            status_a = info_a["factor_statuses"]
            status_b = info_b["factor_statuses"]
            shared_buckets = [
                bucket
                for bucket in BUCKETS
                if status_a[bucket] in VALUE_STATUSES and status_b[bucket] in VALUE_STATUSES
            ]
            range_in_a = [bucket for bucket in shared_buckets if status_a[bucket] == "present_with_range"]
            shared_endpoint_kinds = info_a["endpoint_kinds"] & info_b["endpoint_kinds"]
            shared_endpoint_units = info_a["endpoint_units"] & info_b["endpoint_units"]
            endpoint_units_identical = bool(info_a["endpoint_units"]) and info_a["endpoint_units"] == info_b["endpoint_units"]
            shared_times = shared_time_points(info_a["time_hours"], info_b["time_hours"])
            shared_membranes = info_a["membranes"] & info_b["membranes"]
            n_records_a = int(info_a["summary"]["n_records_total"])
            n_records_b = int(info_b["summary"]["n_records_total"])
            compatibility_class, notes = classify_pair(
                shared_buckets=shared_buckets,
                range_in_a=range_in_a,
                shared_endpoint_kinds=shared_endpoint_kinds,
                shared_endpoint_units=shared_endpoint_units,
                endpoint_units_identical=endpoint_units_identical,
                shared_times=shared_times,
                shared_membranes=shared_membranes,
                n_records_a=n_records_a,
                n_records_b=n_records_b,
            )
            rows.append(
                {
                    "paper_A_doi": doi_a,
                    "paper_B_doi": doi_b,
                    "n_records_A": n_records_a,
                    "n_records_B": n_records_b,
                    "shared_buckets_with_value": ",".join(shared_buckets),
                    "n_shared_buckets_with_value": len(shared_buckets),
                    "shared_buckets_with_range_in_A": ",".join(range_in_a),
                    "shared_endpoint_kinds": ";".join(sorted(shared_endpoint_kinds)),
                    "shared_endpoint_units": ";".join(sorted(shared_endpoint_units)),
                    "shared_time_points": ";".join(shared_times),
                    "shared_membrane_types": ";".join(sorted(shared_membranes)),
                    "compatibility_class": compatibility_class,
                    "notes": notes,
                }
            )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int | None = None) -> list[str]:
    if df.empty:
        return ["_None._"]
    view = df[columns].copy()
    if max_rows is not None:
        view = view.head(max_rows)
    return view.to_markdown(index=False).splitlines()


def provenance_mix(records: list[dict[str, Any]]) -> str:
    counts = Counter(row["provenance"] for row in records)
    return ", ".join(f"{key}:{counts[key]}" for key in PROVENANCE_RANK if counts[key])


def class_counts(pair_df: pd.DataFrame) -> Counter:
    if pair_df.empty:
        return Counter()
    return Counter(pair_df["compatibility_class"])


def best_pair(pair_df: pd.DataFrame, summary_df: pd.DataFrame) -> dict[str, Any] | None:
    if pair_df.empty:
        return None
    score_by_doi = {
        row["doi"]: int(row["modelling_candidate_score"])
        for row in summary_df.to_dict("records")
    }
    ranked = pair_df.copy()
    class_rank = {"STRONG": 0, "MODERATE": 1, "WEAK": 2, "INCOMPATIBLE": 3}
    ranked["_class_rank"] = ranked["compatibility_class"].map(class_rank).fillna(9)
    ranked["_score_product"] = ranked.apply(
        lambda row: (score_by_doi.get(row["paper_A_doi"], 0) + score_by_doi.get(row["paper_B_doi"], 0))
        * int(row["n_shared_buckets_with_value"]),
        axis=1,
    )
    ranked["_combined_score"] = ranked.apply(
        lambda row: score_by_doi.get(row["paper_A_doi"], 0) + score_by_doi.get(row["paper_B_doi"], 0),
        axis=1,
    )
    strong = ranked[ranked["compatibility_class"] == "STRONG"]
    if not strong.empty:
        return strong.sort_values(["_score_product", "_combined_score"], ascending=[False, False]).iloc[0].to_dict()
    moderate = ranked[ranked["compatibility_class"] == "MODERATE"]
    if not moderate.empty:
        return moderate.sort_values(["_score_product", "_combined_score"], ascending=[False, False]).iloc[0].to_dict()
    weak = ranked[ranked["compatibility_class"] == "WEAK"]
    if not weak.empty:
        return weak.sort_values(["_score_product", "_combined_score"], ascending=[False, False]).iloc[0].to_dict()
    return ranked.sort_values(["_class_rank", "_score_product"], ascending=[True, False]).iloc[0].to_dict()


def stage2_gaps_for_paper(doi: str, paper_info: dict[str, Any]) -> list[str]:
    info = paper_info[doi]
    records = info["records"]
    statuses = info["factor_statuses"]
    examples = info["factor_examples"]
    gaps: list[str] = []
    qualitative = [
        bucket
        for bucket, status in statuses.items()
        if status == "present_qualitative" and bucket not in {"microneedle_or_iontophoresis"}
    ]
    for bucket in qualitative[:3]:
        label = ", ".join(examples.get(bucket) or []) or bucket
        gaps.append(f"{doi}: {bucket} is present qualitatively ({label}) but no numeric value was captured.")
    missing_endpoint_values = sum(1 for row in records if endpoint_value(row) is None)
    if missing_endpoint_values:
        gaps.append(f"{doi}: {missing_endpoint_values} ibuprofen records have no numeric endpoint value in structured fields.")
    missing_times = sum(1 for row in records if endpoint_time_h(row) is None)
    if missing_times:
        gaps.append(f"{doi}: {missing_times} ibuprofen records have no parseable endpoint time.")
    if len(info["endpoint_units"]) > 1:
        gaps.append(f"{doi}: endpoint units vary across records ({'; '.join(sorted(info['endpoint_units']))}).")
    mixed_non_table = sum(1 for row in records if "table" not in extraction_sources(row))
    if mixed_non_table:
        gaps.append(f"{doi}: {mixed_non_table} records were not table-sourced; Stage 2 should re-check table/text alignment.")
    if not gaps:
        gaps.append(f"{doi}: no obvious structured-field gap; Stage 2 would mainly verify extraction fidelity from tables/methods.")
    return gaps


def recommendation(pair_df: pd.DataFrame) -> tuple[str, str]:
    counts = class_counts(pair_df)
    if counts["STRONG"] > 0:
        return "GO-STRONG", "At least one STRONG ordered source-target pair exists."
    moderate = pair_df[pair_df["compatibility_class"] == "MODERATE"] if not pair_df.empty else pd.DataFrame()
    if not moderate.empty:
        best = moderate.sort_values(["n_records_A", "n_records_B"], ascending=False).iloc[0]
        if int(best["n_records_A"]) + int(best["n_records_B"]) >= 12:
            return "GO-MODERATE", "No STRONG pair exists, but at least one MODERATE pair has combined n >= 12."
    return "NO-GO", "No STRONG pair exists and the MODERATE evidence does not satisfy the Stage 2 threshold."


def build_report(
    records: list[dict[str, Any]],
    near_miss_names: Counter,
    excluded_mentions: Counter,
    summary_df: pd.DataFrame,
    pair_df: pd.DataFrame,
    paper_info: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    rec, rec_reason = recommendation(pair_df)
    counts = class_counts(pair_df)
    best = best_pair(pair_df, summary_df)
    score_by_doi = {
        row["doi"]: int(row["modelling_candidate_score"])
        for row in summary_df.to_dict("records")
    }
    records_by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        records_by_doi[norm_doi(record.get("doi"))].append(record)

    summary_by_doi = {row["doi"]: row for row in summary_df.to_dict("records")}
    doi_provenance = {
        doi: set(source for row in rows for source in row.get("source_provenances", []))
        for doi, rows in records_by_doi.items()
    }
    v2_dois = sum(1 for sources in doi_provenance.values() if "verified_v2_gpt" in sources)
    claude_v2_dois = sum(1 for sources in doi_provenance.values() if "verified_v2_claude" in sources)
    v3_only_dois = sum(1 for sources in doi_provenance.values() if "verified_v3_gpt_only" in sources)
    v4_only_dois = sum(1 for sources in doi_provenance.values() if "verified_v4_gpt_only" in sources)
    verified_source_tags = {"verified_v2_gpt", "verified_v2_claude", "verified_v3_gpt_only", "verified_v4_gpt_only"}
    unresolved_only_dois = sum(
        1 for sources in doi_provenance.values() if "unresolved" in sources and not (sources & verified_source_tags)
    )
    rejected_only_dois = sum(
        1
        for sources in doi_provenance.values()
        if "rejected" in sources and not (sources & (verified_source_tags | {"unresolved"}))
    )

    hist_counter = Counter()
    for row in summary_df.to_dict("records"):
        n = int(row["n_records_total"])
        if n == 1:
            hist_counter["1"] += 1
        elif 2 <= n <= 4:
            hist_counter["2-4"] += 1
        elif 5 <= n <= 9:
            hist_counter["5-9"] += 1
        else:
            hist_counter["10+"] += 1

    top_by_records = summary_df.sort_values("n_records_total", ascending=False).head(10).copy()
    top_by_records["provenance_mix"] = top_by_records["doi"].map(lambda doi: provenance_mix(records_by_doi[doi]))

    top_by_score = summary_df.sort_values(
        ["modelling_candidate_score", "n_records_total"],
        ascending=[False, False],
    ).head(10)

    strong_moderate = pair_df[pair_df["compatibility_class"].isin(["STRONG", "MODERATE"])] if not pair_df.empty else pd.DataFrame()

    candidate_text = "_No compatible ordered pair was available._"
    gap_lines: list[str] = []
    cost_line = "Stage 2 not recommended; estimated LLM cost is 0 for this ibuprofen-only path."
    if best is not None:
        doi_a = best["paper_A_doi"]
        doi_b = best["paper_B_doi"]
        n_a = int(best["n_records_A"])
        n_b = int(best["n_records_B"])
        candidate_text = (
            f"`{doi_a}` -> `{doi_b}` ({best['compatibility_class']}), "
            f"n_records {n_a} + {n_b}, "
            f"scores {score_by_doi.get(doi_a, 0)} + {score_by_doi.get(doi_b, 0)}, "
            f"shared numeric buckets: {best['n_shared_buckets_with_value']}."
        )
        gap_lines = stage2_gaps_for_paper(doi_a, paper_info)[:3] + stage2_gaps_for_paper(doi_b, paper_info)[:3]
        passes = 2
        papers = 2
        tokens_per_pass = 8000
        cost_line = (
            f"Rough Stage 2 order: {papers} papers x {passes} passes "
            f"(tables + methods/results text) x ~{tokens_per_pass:,} input tokens = ~{papers * passes * tokens_per_pass:,} input tokens, "
            "~4,000-8,000 output tokens."
        )

    if not gap_lines:
        gap_lines = ["No top pair gaps to list because no candidate pair was found."]

    near_miss_union = Counter(row["api_name"] for row in records if row.get("api_near_miss_review"))
    near_miss_text = (
        ", ".join(f"`{name}` ({count})" for name, count in near_miss_union.most_common())
        if near_miss_union
        else "none"
    )
    excluded_text = (
        ", ".join(f"`{name}` ({count})" for name, count in excluded_mentions.most_common())
        if excluded_mentions
        else "none"
    )

    report_lines = [
        "# Phase 0b Stage 1 Ibuprofen Audit",
        "",
        "Zero-cost audit generated from existing JSONL outputs only. No extractor, PDF, API, or LLM call was made.",
        "",
        "## 1. Pool Composition",
        "",
        f"- Total unique DOIs in ibuprofen union pool: `{len(records_by_doi)}`",
        f"- DOI provenance breakdown: GPT v2 `{v2_dois}`, Claude v2 `{claude_v2_dois}`, GPT v3-only `{v3_only_dois}`, GPT v4-only `{v4_only_dois}`, unresolved-only `{unresolved_only_dois}`, rejected-only `{rejected_only_dois}`.",
        f"- Histogram of n_records_total per paper: 1=`{hist_counter['1']}`, 2-4=`{hist_counter['2-4']}`, 5-9=`{hist_counter['5-9']}`, 10+=`{hist_counter['10+']}`.",
        f"- Near-miss API names flagged for manual review: {near_miss_text}.",
        f"- Ibuprofen-like API names excluded by the pool regex: {excluded_text}.",
        "",
        "Top 10 papers by n_records_total:",
        "",
        *markdown_table(
            top_by_records,
            ["doi", "n_records_total", "n_records_v2", "n_records_v3_only", "n_records_v4_only", "n_records_unresolved", "provenance_mix"],
        ),
        "",
        "## 2. Internal Modelling Viability",
        "",
        f"- Papers with internal_factor_variation=True: `{int(summary_df['internal_factor_variation'].sum())}`",
        f"- Papers with modelling_candidate_score >= 50: `{int((summary_df['modelling_candidate_score'] >= 50).sum())}`",
        "",
        "Top 10 papers by modelling score:",
        "",
        *markdown_table(
            top_by_score,
            ["doi", "n_records_total", "internal_factor_variation", "modelling_candidate_score", "formulation_factor_summary"],
        ),
        "",
        "## 3. Cross-Paper Compatibility",
        "",
        f"- Ordered pair counts: STRONG `{counts['STRONG']}`, MODERATE `{counts['MODERATE']}`, WEAK `{counts['WEAK']}`, INCOMPATIBLE `{counts['INCOMPATIBLE']}`.",
        "",
        "STRONG and MODERATE pairs:",
        "",
        *markdown_table(
            strong_moderate.sort_values(["compatibility_class", "n_shared_buckets_with_value"], ascending=[True, False]) if not strong_moderate.empty else strong_moderate,
            [
                "paper_A_doi",
                "paper_B_doi",
                "n_records_A",
                "n_records_B",
                "shared_buckets_with_value",
                "n_shared_buckets_with_value",
                "shared_buckets_with_range_in_A",
                "shared_endpoint_kinds",
                "shared_endpoint_units",
                "shared_time_points",
                "shared_membrane_types",
                "compatibility_class",
                "notes",
            ],
        ),
        "",
        f"Best candidate pair: {candidate_text}",
        "",
        "## 4. Honest Reality Check",
        "",
        "Stage 2-only gaps for the top candidate pair:",
        "",
        *[f"- {gap}" for gap in gap_lines[:6]],
        "",
        cost_line,
        "",
        "## 5. GO/NO-GO Recommendation",
        "",
        f"{rec}: {rec_reason}",
        "",
        f"RECOMMENDATION: {rec} | {rec_reason}",
        "",
    ]

    decision_lines = [
        "# Phase 0b Stage 1 GO/NO-GO Decision",
        "",
        f"RECOMMENDATION: {rec} | {rec_reason}",
        "",
        f"Top candidate pair: {candidate_text}",
        "",
        "Top 3 Stage 2 gaps:",
        "",
        *[f"- {gap}" for gap in gap_lines[:3]],
        "",
        f"Estimated Stage 2 LLM cost: {cost_line}",
        "",
    ]

    return "\n".join(report_lines), "\n".join(decision_lines)


def write_outputs(
    records: list[dict[str, Any]],
    summary_df: pd.DataFrame,
    factor_df: pd.DataFrame,
    pair_df: pd.DataFrame,
    report_text: str,
    decision_text: str,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ALL_RECORDS_PATH.open("w", encoding="utf-8") as handle:
        for record in records:
            output_record = copy.deepcopy(record)
            output_record.pop("source_jsonl_priority", None)
            handle.write(json.dumps(output_record, ensure_ascii=False, sort_keys=True) + "\n")
    summary_df.to_csv(PAPER_SUMMARY_PATH, index=False, encoding="utf-8-sig")
    factor_df.to_csv(FACTOR_MATRIX_PATH, index=False, encoding="utf-8-sig")
    pair_df.to_csv(PAIR_COMPAT_PATH, index=False, encoding="utf-8-sig")
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    GO_NOGO_PATH.write_text(decision_text, encoding="utf-8")


def main() -> None:
    records, near_miss_names, excluded_mentions = collect_union_pool()
    summary_df, factor_df, paper_info = build_paper_summary(records)
    pair_df = build_pair_compatibility(summary_df, paper_info)
    report_text, decision_text = build_report(
        records=records,
        near_miss_names=near_miss_names,
        excluded_mentions=excluded_mentions,
        summary_df=summary_df,
        pair_df=pair_df,
        paper_info=paper_info,
    )
    write_outputs(records, summary_df, factor_df, pair_df, report_text, decision_text)
    rec, rec_reason = recommendation(pair_df)
    payload = {
        "all_ibuprofen_records": len(records),
        "paper_summary_rows": len(summary_df),
        "pair_compatibility_rows": len(pair_df),
        "factor_matrix_rows": len(factor_df),
        "recommendation": rec,
        "recommendation_reason": rec_reason,
        "outputs": {
            "all_records": str(ALL_RECORDS_PATH.relative_to(ROOT)),
            "paper_summary": str(PAPER_SUMMARY_PATH.relative_to(ROOT)),
            "pair_compatibility": str(PAIR_COMPAT_PATH.relative_to(ROOT)),
            "factor_matrix": str(FACTOR_MATRIX_PATH.relative_to(ROOT)),
            "go_nogo": str(GO_NOGO_PATH.relative_to(ROOT)),
            "report": str(REPORT_PATH.relative_to(ROOT)),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
