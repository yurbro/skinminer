"""Unit parsing and normalization helpers shared by assembly and verification."""

from __future__ import annotations

import math
import re
from typing import Iterable


def _clean_text(text: str) -> str:
    cleaned = text or ""
    return (
        cleaned.replace("Âµ", "u")
        .replace("µ", "u")
        .replace("μ", "u")
        .replace("Â²", "2")
        .replace("²", "2")
        .replace("–", "-")
        .replace("—", "-")
    )


def _compact_unit_slashes(text: str) -> str:
    """Normalize unit spellings like `w / v` to `w/v` for matching only."""

    return re.sub(r"\s*/\s*", "/", text or "")


def _contains_explicit_molar_unit(text: str) -> re.Match[str] | None:
    """Return a match only for explicit molar concentration units, not length units like `mm`."""

    return re.search(r"(\d+(?:\.\d+)?)\s*(mM|μM|uM|nM)\b", text)


def _has_formulation_concentration_context(lowered: str, dosage_form: str) -> bool:
    return any(
        token in lowered
        for token in (
            "composition",
            "formulation",
            "preparation",
            "drug loading",
            "drug content",
            "api concentration",
            "active ingredient",
            "active drug",
            "drug substance",
            "drug concentration",
            "loaded formulation",
            "table 1",
            "table i",
        )
    ) or any(
        token and token in lowered
        for token in (dosage_form, "gel", "cream", "ointment", "emulgel", "patch", "vehicle")
    )


def _has_endpoint_or_receiver_context(lowered: str) -> bool:
    return any(
        token in lowered
        for token in (
            "receiver",
            "receptor",
            "acceptor",
            "donor fluid",
            "sample aliquot",
            "aliquot",
            "permeated",
            "permeation",
            "cumulative amount",
            "amount permeated",
            "release after",
            "release at",
            "flux",
            "jss",
            "steady-state flux",
            "papp",
            "permeability coefficient",
            "release medium",
            "receptor medium",
            "receiver medium",
            "receiver compartment",
            "receptor compartment",
        )
    )


def fragment_matches_api_context(
    text: str,
    *,
    api_name: str = "ibuprofen",
    formulation_label: str = "",
    dosage_form: str = "",
) -> bool:
    """Return whether a fragment likely refers to the target API concentration."""

    lowered = _clean_text(text).strip().lower()
    if not lowered:
        return False

    api_name = (api_name or "ibuprofen").strip().lower()
    formulation_label = (formulation_label or "").strip().lower()
    dosage_form = (dosage_form or "").strip().lower()
    excipient_only_cues = (
        "propylene glycol",
        "glycerin",
        "water",
        "ethanol",
        "carbopol",
        "transcutol",
        "cremophor",
        "oleic acid",
        "isopropyl myristate",
        "surfactant",
        "cosurfactant",
    )

    has_formulation_context = _has_formulation_concentration_context(lowered, dosage_form)
    has_endpoint_or_receiver_context = _has_endpoint_or_receiver_context(lowered)
    if has_endpoint_or_receiver_context and not has_formulation_context:
        return False
    if api_name and api_name in lowered:
        return True
    if formulation_label and len(formulation_label) >= 3 and formulation_label in lowered:
        return True
    if has_formulation_context:
        return True
    if any(token in lowered for token in ("calibration curve", "limit of quantitation", "cell viability", "cytotoxicity", "ha cat", "hplc", "detection method")):
        return False
    if "pka" in lowered and "%" not in lowered and "mg/" not in lowered and "drug" not in lowered:
        return False
    if any(token in lowered for token in excipient_only_cues) and api_name not in lowered:
        return False
    if any(token in lowered for token in ("composition", "formulations listed in table", "loaded formulation", "preparation")) and any(
        token in lowered for token in ("%", "w/w", "wt%", "mg/g", "g/100 g", "mg/ml")
    ):
        return True
    if any(token and token in lowered for token in (dosage_form, "formulation", "gel", "cream", "ointment", "emulgel", "patch", "vehicle")) and any(
        token in lowered for token in ("%", "w/w", "wt%", "mg/g", "g/100 g", "mg/ml")
    ):
        return True
    return False


def normalize_time_to_hours(value: float | None, unit: str) -> float | None:
    """Normalize a time value to hours when the unit is recognized."""

    if value is None:
        return None
    lowered = _clean_text(unit).strip().lower()
    if lowered in {"h", "hr", "hrs", "hour", "hours"}:
        return float(value)
    if lowered in {"min", "mins", "minute", "minutes"}:
        return float(value) / 60.0
    if lowered in {"s", "sec", "secs", "second", "seconds"}:
        return float(value) / 3600.0
    if lowered in {"d", "day", "days"}:
        return float(value) * 24.0
    return None


def normalize_amount_per_area(value: float | None, unit: str) -> tuple[float | None, str]:
    """Normalize amount-per-area units to `ug/cm^2` when possible."""

    if value is None:
        return None, ""
    lowered = _clean_text(unit).lower().replace(" ", "")
    if "mg/cm2" in lowered or "mg/cm^2" in lowered:
        return float(value) * 1000.0, "ug/cm^2"
    if "ug/cm2" in lowered or "ug/cm^2" in lowered:
        return float(value), "ug/cm^2"
    if "ng/cm2" in lowered or "ng/cm^2" in lowered:
        return float(value) / 1000.0, "ug/cm^2"
    return None, ""


def coerce_endpoint_kind_from_unit(kind: str, unit: str) -> str:
    """Coerce endpoint kind when the unit encodes a stronger semantic signal."""

    lowered = _clean_text(unit).lower().replace(" ", "")
    if any(token in lowered for token in ("mg/cm2", "mg/cm^2", "ug/cm2", "ug/cm^2", "ng/cm2", "ng/cm^2")):
        if kind in {"amount_total", "unknown"}:
            return "amount_per_area"
    return kind


def amount_total_to_ug_per_cm2(value: float | None, unit: str, area_cm2: float | None) -> tuple[float | None, str]:
    """Normalize total amount values to `ug/cm^2` when diffusion area is available."""

    if value is None or area_cm2 is None or area_cm2 <= 0:
        return None, ""
    lowered = _clean_text(unit).lower().replace(" ", "")
    if "ug" in lowered:
        return float(value) / float(area_cm2), "ug/cm^2"
    if "mg" in lowered:
        return float(value) * 1000.0 / float(area_cm2), "ug/cm^2"
    if "ng" in lowered:
        return float(value) / 1000.0 / float(area_cm2), "ug/cm^2"
    return None, ""


def amount_total_or_receiver_concentration_to_ug_per_cm2(
    value: float | None,
    unit: str,
    area_cm2: float | None,
    receptor_volume_ml: float | None = None,
) -> tuple[float | None, str]:
    """Normalize total amount or receptor-concentration endpoints to `ug/cm^2`."""

    lowered = _clean_text(unit).lower().replace(" ", "")
    if any(token in lowered for token in ("ug/ml", "ug/m1", "mg/ml", "ng/ml")):
        if value is None or area_cm2 is None or area_cm2 <= 0 or receptor_volume_ml is None or receptor_volume_ml <= 0:
            return None, ""
        total_ug: float | None = None
        if "ug/ml" in lowered or "ug/m1" in lowered:
            total_ug = float(value) * float(receptor_volume_ml)
        elif "mg/ml" in lowered:
            total_ug = float(value) * 1000.0 * float(receptor_volume_ml)
        elif "ng/ml" in lowered:
            total_ug = float(value) / 1000.0 * float(receptor_volume_ml)
        if total_ug is None:
            return None, ""
        return total_ug / float(area_cm2), "ug/cm^2"

    direct_value, direct_unit = amount_total_to_ug_per_cm2(value, unit, area_cm2)
    if direct_value is not None:
        return direct_value, direct_unit

    if value is None or area_cm2 is None or area_cm2 <= 0 or receptor_volume_ml is None or receptor_volume_ml <= 0:
        return None, ""

    total_ug: float | None = None
    if "ug/ml" in lowered or "ug/m1" in lowered:
        total_ug = float(value) * float(receptor_volume_ml)
    elif "mg/ml" in lowered:
        total_ug = float(value) * 1000.0 * float(receptor_volume_ml)
    elif "ng/ml" in lowered:
        total_ug = float(value) / 1000.0 * float(receptor_volume_ml)
    if total_ug is None:
        return None, ""
    return total_ug / float(area_cm2), "ug/cm^2"


def parse_api_concentration(raw_text: str) -> tuple[float | None, str, str]:
    """Parse common API concentration expressions from free text."""

    text = _clean_text(raw_text).strip()
    if not text:
        return None, "", ""

    explicit_pct_pattern = re.compile(
        r"(\d+(?:\.\d+)?)\s*%\s*\(?\s*(w\s*/\s*w|wt\s*/\s*wt|wt\.?\s*%|wt%|w\s*/\s*v|wt\s*/\s*vol|w\s*v)\s*\)?\b",
        flags=re.IGNORECASE,
    )
    explicit_candidates: list[tuple[int, int, float, str, str]] = []
    for match in explicit_pct_pattern.finditer(text):
        token = _compact_unit_slashes(match.group(2).lower())
        basis = "w/v" if "v" in token or "vol" in token else "w/w"
        unit = "% w/v" if basis == "w/v" else "% w/w"
        start, end = match.span()
        before = text[max(0, start - 70) : start].lower()
        after = text[end : min(len(text), end + 35)].lower()
        window = f"{before}{match.group(0).lower()}{after}"
        immediate_context = f"{before}{match.group(0).lower()}"
        compact_window = _compact_unit_slashes(window)
        compact_immediate = _compact_unit_slashes(immediate_context)
        compact_after = _compact_unit_slashes(after)
        has_drug_cue = bool(
            re.search(r"\b(?:ibuprofen|api|active ingredient|active drug|drug substance|model drug)\b", compact_immediate)
            or re.search(r"\bdrug\b.{0,30}\d+(?:\.\d+)?\s*%", compact_immediate)
            or re.search(r"^\s*(?:\([^)]*\)\s*)?\bdrug\b", compact_after)
        )
        has_excipient_cue = any(
            token in compact_window
            for token in (
                "hpmc",
                "vitamin e",
                "tpgs",
                "polymer",
                "surfactant",
                "stabilizer",
                "pluronic",
                "na-cmc",
                "xanthan",
                "carbopol",
            )
        )
        score = 0
        if has_drug_cue:
            score += 20
        if has_excipient_cue and not has_drug_cue:
            score -= 12
        if basis == "w/w":
            score += 2
        else:
            score += 1
        explicit_candidates.append((score, -start, float(match.group(1)), unit, basis))
    if explicit_candidates:
        explicit_candidates.sort(reverse=True)
        _score, _neg_start, value, unit, basis = explicit_candidates[0]
        return value, unit, basis

    match_pct = re.search(r"(\d+(?:\.\d+)?)\s*%\s*\(?\s*(w\s*/\s*w|wt\s*/\s*wt|wt\.?\s*%|wt%)\s*\)?", text, flags=re.IGNORECASE)
    if match_pct:
        return float(match_pct.group(1)), "% w/w", "w/w"

    match_weight_percent = re.search(r"(\d+(?:\.\d+)?)\s*(?:wt\s*%|wt%|w\s*/\s*w|wt\s*/\s*wt)\b", text, flags=re.IGNORECASE)
    if match_weight_percent:
        return float(match_weight_percent.group(1)), "% w/w", "w/w"

    match_weight_volume = re.search(r"(\d+(?:\.\d+)?)\s*%\s*\(?\s*(w\s*/\s*v|wt\s*/\s*vol|w\s*v)\s*\)?\b", text, flags=re.IGNORECASE)
    if match_weight_volume:
        return float(match_weight_volume.group(1)), "% w/v", "w/v"

    match_plain_pct = re.search(r"(\d+(?:\.\d+)?)\s*%\b", text, flags=re.IGNORECASE)
    if match_plain_pct:
        lowered = text.lower()
        compact_lowered = _compact_unit_slashes(lowered)
        if any(token in compact_lowered for token in ("weight/weight", "weight percent", "weight-percent", "w/w", "wt/wt", "wt %", "wt%")):
            return float(match_plain_pct.group(1)), "% w/w", "w/w"
        if any(token in compact_lowered for token in ("weight/volume", "w/v", "wt/vol")):
            return float(match_plain_pct.group(1)), "% w/v", "w/v"
        return float(match_plain_pct.group(1)), "%", ""

    match_mgg = re.search(r"(\d+(?:\.\d+)?)\s*mg\s*/\s*g", text, flags=re.IGNORECASE)
    if match_mgg:
        return float(match_mgg.group(1)), "mg/g", "w/w"

    match_mg_per_g_words = re.search(
        r"(?:contains|contained|loading|loaded with|drug loading|ibuprofen[^.;,\n]{0,40})\s*(\d+(?:\.\d+)?)\s*mg\s*(?:of)?\s*(?:ibuprofen)?\s*per\s*g\b",
        text,
        flags=re.IGNORECASE,
    )
    if match_mg_per_g_words:
        return float(match_mg_per_g_words.group(1)), "mg/g", "w/w"

    match_g_per_g = re.search(r"(\d+(?:\.\d+)?)\s*g\s*/\s*g\b", text, flags=re.IGNORECASE)
    if match_g_per_g:
        value = float(match_g_per_g.group(1))
        if value <= 1.0:
            return value * 100.0, "% w/w", "w/w"
        return value, "g/g", "w/w"

    match_g_per_100g = re.search(r"(\d+(?:\.\d+)?)\s*g\s*/\s*100\s*g", text, flags=re.IGNORECASE)
    if match_g_per_100g:
        return float(match_g_per_100g.group(1)), "% w/w", "w/w"

    match_mg_per_100mg = re.search(r"(\d+(?:\.\d+)?)\s*mg\s*/\s*100\s*mg", text, flags=re.IGNORECASE)
    if match_mg_per_100mg:
        return float(match_mg_per_100mg.group(1)), "% w/w", "w/w"

    match_parts_per_100 = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:parts?|g|mg)\s*(?:of)?\s*(?:ibuprofen)?[^.;,\n]{0,20}per\s*100\s*(?:parts?|g|mg)",
        text,
        flags=re.IGNORECASE,
    )
    if match_parts_per_100:
        return float(match_parts_per_100.group(1)), "% w/w", "w/w"

    match_mgml = re.search(r"(\d+(?:\.\d+)?)\s*mg\s*/\s*m[l1]\b", text, flags=re.IGNORECASE)
    if match_mgml:
        return float(match_mgml.group(1)), "mg/ml", "w/v"

    match_molar = _contains_explicit_molar_unit(text)
    if match_molar:
        return float(match_molar.group(1)), match_molar.group(2), "molar"

    return None, "", ""


def normalize_api_concentration_fields(
    value: float | None,
    unit: str,
    basis: str,
    raw_text: str = "",
) -> tuple[float | None, str, str]:
    """Normalize API concentration unit and basis strings into a stable schema."""

    resolved_value = value
    resolved_unit = _clean_text(unit).strip()
    resolved_basis = _clean_text(basis).strip()
    lowered_raw = _clean_text(raw_text).lower()
    lowered_unit = resolved_unit.lower()
    lowered_basis = resolved_basis.lower()
    lowered_raw_compact = _compact_unit_slashes(lowered_raw)
    lowered_unit_compact = _compact_unit_slashes(lowered_unit)

    if any(token in lowered_unit_compact or token in lowered_raw_compact for token in ("% (w/w)", "% w/w", "wt%", "wt %", "wt/wt", "g/100 g", "mg/100 mg")):
        resolved_unit = "% w/w"
        resolved_basis = "w/w"
    elif any(token in lowered_unit_compact or token in lowered_raw_compact for token in ("% (w/v)", "% w/v", "w/v", "wt/vol", "mg/ml")):
        if "mg/ml" in lowered_unit_compact:
            resolved_unit = "mg/ml"
        else:
            resolved_unit = "% w/v"
        resolved_basis = "w/v"
    elif "mg/g" in lowered_unit or "mg per g" in lowered_unit or "mg/g" in lowered_raw:
        resolved_unit = "mg/g"
        resolved_basis = "w/w"
    elif "g/g" in lowered_unit:
        resolved_unit = "g/g"
        resolved_basis = "w/w"
    elif resolved_unit in {"mM", "μM", "uM", "nM"} or _contains_explicit_molar_unit(_clean_text(raw_text).strip()):
        resolved_unit = resolved_unit if resolved_unit in {"mM", "μM", "uM", "nM"} else "mM"
        resolved_basis = "molar"

    if resolved_unit == "%" and lowered_basis in {"w/w", "wt", "wt/wt"}:
        resolved_unit = "% w/w"
        resolved_basis = "w/w"
    elif resolved_unit == "%" and lowered_basis in {"w/v", "wt/vol"}:
        resolved_unit = "% w/v"
        resolved_basis = "w/v"

    if resolved_basis not in {"w/w", "w/v", "molar"}:
        if "% w/w" in resolved_unit or resolved_unit in {"mg/g", "g/g"}:
            resolved_basis = "w/w"
        elif "% w/v" in resolved_unit or resolved_unit == "mg/ml":
            resolved_basis = "w/v"
        elif resolved_unit == "mM":
            resolved_basis = "molar"

    return resolved_value, resolved_unit, resolved_basis


def api_concentration_quality(
    value: float | None,
    unit: str,
    basis: str,
    raw_text: str = "",
    *,
    prefer_strict_scope: bool = False,
) -> int:
    """Score how useful a concentration expression is for strict-scope recovery."""

    score = 0
    if value is not None:
        score += 1

    resolved_value, resolved_unit, resolved_basis = normalize_api_concentration_fields(value, unit, basis, raw_text)
    lowered_raw = _clean_text(raw_text).lower()
    lowered_unit = resolved_unit.lower()
    lowered_basis = resolved_basis.lower()
    combined = " ".join(part for part in (lowered_unit, lowered_basis, lowered_raw) if part)

    if any(token in combined for token in ("5% w/w", "5 % w/w", "50 mg/g")):
        score += 10
    if lowered_basis == "w/w":
        score += 6
    elif lowered_basis == "w/v":
        score += 2
    elif lowered_basis == "molar":
        score += 1

    if lowered_unit in {"% w/w", "mg/g", "g/g"}:
        score += 4
    elif lowered_unit in {"% w/v", "mg/ml"}:
        score += 1
    elif lowered_unit == "mm":
        score -= 1

    if any(token in combined for token in ("mg/kg", "ug/kg", "dose", "intraperitoneal", "oral", "intravenous")):
        score -= 8

    if prefer_strict_scope:
        if lowered_basis == "w/w":
            score += 4
        elif lowered_basis == "w/v":
            score -= 2
        elif lowered_basis == "molar":
            score -= 3
        if resolved_value is not None and lowered_basis == "w/w" and abs(float(resolved_value) - 5.0) < 1e-9:
            score += 6
        if resolved_value is not None and lowered_unit == "mg/g" and abs(float(resolved_value) - 50.0) < 1e-9:
            score += 6
    return score


def infer_api_concentration_from_fragments(
    fragments: Iterable[str],
    *,
    api_name: str = "ibuprofen",
    formulation_label: str = "",
    dosage_form: str = "",
    prefer_strict_scope: bool = False,
) -> tuple[float | None, str, str, str]:
    """Infer API concentration from an ordered fragment list using shared context rules."""
    candidates: list[tuple[int, int, float, str, str, str]] = []
    for fragment in fragments:
        if not fragment_matches_api_context(
            fragment,
            api_name=api_name,
            formulation_label=formulation_label,
            dosage_form=dosage_form,
        ):
            continue
        value, unit, basis = parse_api_concentration(fragment)
        if value is not None:
            lowered = _clean_text(fragment).strip().lower()
            has_formulation_context = _has_formulation_concentration_context(lowered, dosage_form)
            has_endpoint_or_receiver_context = _has_endpoint_or_receiver_context(lowered)
            score = 0
            if api_name and api_name.lower() in lowered:
                score += 6
            if formulation_label and formulation_label.lower() in lowered:
                score += 2
            if dosage_form and dosage_form.lower() in lowered:
                score += 1
            if has_formulation_context:
                score += 5
            if has_endpoint_or_receiver_context and not has_formulation_context:
                score -= 10
            if basis == "w/w":
                score += 5
            elif basis == "w/v":
                score += 2
            elif basis == "molar":
                score += 1
            if any(token in lowered for token in ("5% w/w", "50 mg/g", "5 % w/w", "wt% ibuprofen", "wt % ibuprofen")):
                score += 6
            if any(token in lowered for token in ("mg/kg", "ug/kg", "intraperitoneal", "oral", "dose", "dosed", "administered")):
                score -= 8
            if prefer_strict_scope:
                if basis == "w/w":
                    score += 6
                elif basis == "w/v":
                    score -= 2
                elif basis == "molar":
                    score -= 4
                if unit == "%" and not basis:
                    score -= 2
            candidates.append((score, -len(lowered), value, unit, basis, fragment))
    if candidates:
        candidates.sort(reverse=True)
        _score, _neg_len, value, unit, basis, fragment = candidates[0]
        return value, unit, basis, fragment
    return None, "", "", ""


def is_strict_api_concentration_hint(
    value: float | None,
    unit: str,
    basis: str,
    raw_text: str = "",
    *,
    min_quality: int = 12,
) -> bool:
    """Return whether a concentration hint is strong enough for strict-scope promotion."""

    return (
        api_concentration_quality(
            value,
            unit,
            basis,
            raw_text,
            prefer_strict_scope=True,
        )
        >= min_quality
    )


def parse_area_cm2(text: str) -> float | None:
    """Parse diffusion area values reported in square centimeters."""

    cleaned = _clean_text(text)

    keyword_match = re.search(
        r"(?:diffusion|effective|exposed|surface|permeation|orifice|available|membrane|release|donor)\s+area(?:\s+of|\s*=|\s*:|\s+was|\s+is)?\s*(\d+(?:\.\d+)?)\s*(cm\s*2|cm\^2|cm²|mm\s*2|mm\^2|mm²)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if keyword_match:
        value = float(keyword_match.group(1))
        unit = keyword_match.group(2).lower()
        return value / 100.0 if unit.startswith("mm") else value

    generic_match = re.search(r"(\d+(?:\.\d+)?)\s*(cm\s*2|cm\^2|cm²|mm\s*2|mm\^2|mm²)\b", cleaned, flags=re.IGNORECASE)
    if generic_match:
        value = float(generic_match.group(1))
        unit = generic_match.group(2).lower()
        return value / 100.0 if unit.startswith("mm") else value

    rectangular_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(cm|mm)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(cm|mm)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if rectangular_match:
        width = float(rectangular_match.group(1))
        width_unit = rectangular_match.group(2).lower()
        height = float(rectangular_match.group(3))
        height_unit = rectangular_match.group(4).lower()
        if width_unit == "mm":
            width = width / 10.0
        if height_unit == "mm":
            height = height / 10.0
        if width > 0 and height > 0:
            return round(width * height, 4)

    diameter_match = re.search(
        r"(?:diameter|orifice)\s*(?:of|=|:)?\s*(\d+(?:\.\d+)?)\s*(mm|cm)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if diameter_match:
        diameter = float(diameter_match.group(1))
        if diameter_match.group(2).lower() == "mm":
            diameter = diameter / 10.0
        radius_cm = diameter / 2.0
        return round(math.pi * radius_cm * radius_cm, 4)

    radius_match = re.search(
        r"(?:radius)\s*(?:of|=|:)?\s*(\d+(?:\.\d+)?)\s*(mm|cm)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if radius_match:
        radius_cm = float(radius_match.group(1))
        if radius_match.group(2).lower() == "mm":
            radius_cm = radius_cm / 10.0
        return round(math.pi * radius_cm * radius_cm, 4)

    av_match = re.search(
        r"\bA[vV]?\s*(?:=|:)\s*(\d+(?:\.\d+)?)\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if av_match and any(token in cleaned.lower() for token in ("diffusion", "permeat", "release", "membrane", "cell")):
        return float(av_match.group(1))

    return None


def parse_receptor_volume_ml(text: str) -> float | None:
    """Parse receptor or receiver chamber volume in mL."""

    cleaned = _clean_text(text)
    contextual_patterns = [
        r"(?:receptor|receiver)\s+(?:volume|compartment|chamber|cell)[^.]{0,220}?(?:approximately\s*)?(\d+(?:\.\d+)?)\s*m[l1]\b",
        r"(?:orifice|filled\s+up\s+to)[^.]{0,140}?(?:approximately\s*)?(\d+(?:\.\d+)?)\s*m[l1]\b[^.]{0,100}?(?:receptor|receiver)",
        r"(\d+(?:\.\d+)?)\s*m[l1]\b[^.]{0,100}?(?:receptor|receiver)\s+(?:volume|compartment|chamber|cell)",
    ]
    for pattern in contextual_patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))

    match = re.search(
        r"(?:receptor|receiver)\s+(?:volume|compartment|chamber)(?:\s+was|\s+of|\s*=|\s*:)?\s*(?:approximately\s*)?(\d+(?:\.\d+)?)\s*m[l1]\b",
        cleaned,
        flags=re.IGNORECASE,
    )
    if match:
        return float(match.group(1))

    generic_match = re.search(r"(\d+(?:\.\d+)?)\s*m[l1]\b", cleaned, flags=re.IGNORECASE)
    if generic_match:
        start, end = generic_match.span()
        local_context = cleaned[max(0, start - 80) : min(len(cleaned), end + 80)].lower()
        if any(token in local_context for token in ("receptor", "receiver")) and not any(
            token in local_context for token in ("donor compartment", "dose tube", "syringe", "gel administered")
        ):
            return float(generic_match.group(1))
    return None


TIME_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours|min|mins|minute|minutes|d|day|days)\b",
    flags=re.IGNORECASE,
)


def extract_time_mentions(text: str) -> list[tuple[float, str]]:
    """Extract time-value mentions from text in order of appearance."""

    cleaned = _clean_text(text)
    return [(float(match.group(1)), match.group(2)) for match in TIME_PATTERN.finditer(cleaned)]


AMOUNT_PATTERN = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(mg|ug|ng)\s*(/\s*cm(?:2|\^2))?\b", flags=re.IGNORECASE)


def parse_endpoint_amount(text: str) -> tuple[float | None, str, str]:
    """Parse a single unambiguous amount-like endpoint expression from text."""

    cleaned = _clean_text(text)
    if re.search(r"\d+(?:\.\d+)?\s*[-/]\s*\d+(?:\.\d+)?\s*(mg|ug|ng)", cleaned, flags=re.IGNORECASE):
        return None, "", "unknown"

    matches = [
        (
            float(match.group(1)),
            _clean_text(match.group(2) + (match.group(3) or "")),
            "amount_per_area" if match.group(3) else "amount_total",
        )
        for match in AMOUNT_PATTERN.finditer(cleaned)
    ]
    unique = {(value, unit, kind) for value, unit, kind in matches}
    if len(unique) != 1:
        return None, "", "unknown"
    value, unit, kind = unique.pop()
    return value, unit, kind


def parse_endpoint_unit_hint(text: str) -> tuple[str, str]:
    """Parse endpoint unit hints even when no unique numeric value is available."""

    cleaned = _clean_text(text)
    lowered = cleaned.lower().replace(" ", "")

    if "ug/cm2" in lowered or "ug/cm^2" in lowered:
        return "ug/cm^2", "amount_per_area"
    if "mg/cm2" in lowered or "mg/cm^2" in lowered:
        return "mg/cm^2", "amount_per_area"
    if "ng/cm2" in lowered or "ng/cm^2" in lowered:
        return "ng/cm^2", "amount_per_area"
    if "ug/ml" in lowered or "ug/m1" in lowered:
        return "ug/mL", "amount_total"
    if "mg/ml" in lowered:
        return "mg/mL", "amount_total"
    if "ng/ml" in lowered:
        return "ng/mL", "amount_total"
    if lowered.endswith("ug") or "amountof" in lowered and "ug" in lowered:
        return "ug", "amount_total"
    if lowered.endswith("mg") or "amountof" in lowered and "mg" in lowered:
        return "mg", "amount_total"
    if lowered.endswith("ng") or "amountof" in lowered and "ng" in lowered:
        return "ng", "amount_total"
    return "", "unknown"


def endpoint_unit_quality(unit: str) -> int:
    """Return a coarse quality score for endpoint-unit reuse and normalization."""

    lowered = _clean_text(unit).lower().replace(" ", "")
    if lowered in {"", "mau"}:
        return 0
    if "ug/cm2" in lowered or "ug/cm^2" in lowered:
        return 6
    if "mg/cm2" in lowered or "mg/cm^2" in lowered or "ng/cm2" in lowered or "ng/cm^2" in lowered:
        return 5
    if "ug/ml" in lowered or "mg/ml" in lowered or "ng/ml" in lowered:
        return 4
    if lowered in {"ug", "mg", "ng"}:
        return 3
    return 0
