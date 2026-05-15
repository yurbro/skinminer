"""Evidence-backed verification separated from record assembly."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from extractors.common import device_label_strength, find_device_support_fragment, infer_device_label, infer_study_type_label
from patchers.common import collect_source_fragments
from policies.v1_strict_ibuprofen_5pct import V1StrictIbuprofen5PctPolicy
from schemas.models import EvidenceItem, Record
from utils.io import write_records_csv, write_records_jsonl
from utils.status_panel import ProgressCallback
from utils.units import (
    api_concentration_quality,
    amount_total_or_receiver_concentration_to_ug_per_cm2,
    coerce_endpoint_kind_from_unit,
    infer_api_concentration_from_fragments,
    is_strict_api_concentration_hint,
    normalize_amount_per_area,
    normalize_api_concentration_fields,
    normalize_time_to_hours,
    parse_area_cm2,
    parse_receptor_volume_ml,
)
from verification.failure_taxonomy import FailureCode, classify_outcome
from verification.source_binding_guard import apply_source_context_guard

STRICT_SHARED_API_HINT_MIN_QUALITY = 12
RECOVERABLE_SCOPE_TAGS = {
    FailureCode.AMBIGUOUS_API_CONCENTRATION.value: "recoverable_api_basis",
    FailureCode.MISSING_API_CONCENTRATION.value: "recoverable_api_basis",
    FailureCode.MISSING_AREA.value: "recoverable_area",
    FailureCode.MISSING_ENDPOINT.value: "recoverable_endpoint",
    FailureCode.MISSING_ENDPOINT_TIME.value: "recoverable_endpoint_time",
    FailureCode.UNIT_NORMALIZATION_FAILED.value: "recoverable_unit_normalization",
    FailureCode.INSUFFICIENT_EVIDENCE.value: "recoverable_support_gap",
    FailureCode.AMBIGUOUS_MAPPING.value: "recoverable_mapping",
    FailureCode.FIGURE_DIGITIZATION_FAILED.value: "recoverable_figure_digitization",
    FailureCode.FIGURE_PLOT_CONTEXT_MISSING.value: "recoverable_figure_plot_context",
    FailureCode.SOURCE_CONTEXT_INCONSISTENT.value: "recoverable_source_context",
    FailureCode.UNRESOLVED_ROUTE.value: "recoverable_routing",
}


def _effective_endpoint_kind(record: Record, policy: V1StrictIbuprofen5PctPolicy) -> tuple[str, str | None]:
    resolver = getattr(policy, "effective_endpoint_kind", None)
    if callable(resolver):
        return resolver(record)
    return record.endpoint.kind, None


def _field_supported(record: Record, field_name: str) -> bool:
    return any(item.field_name == field_name for item in record.evidence_items)


def _append_support_evidence(record: Record, field_name: str, snippet: str, confidence: float = 0.55) -> None:
    if not snippet or _field_supported(record, field_name):
        return
    record.evidence_items.append(
        EvidenceItem(
            field_name=field_name,
            modality="metadata" if record.route == "unresolved" else record.route,  # type: ignore[arg-type]
            locator=f"verify:{field_name}",
            snippet=snippet,
            source_ref=record.doi or record.paper_id,
            confidence=confidence,
        )
    )


def _verification_support_rate(record: Record) -> float:
    supported = 0
    checks = 0
    for field_name, has_value in [
        ("device", bool(record.device)),
        ("formulation", bool(record.formulation.api_name)),
        ("api_concentration", record.formulation.api_concentration_value is not None or bool(record.formulation.api_concentration_raw)),
        ("endpoint", record.endpoint.value is not None),
        ("endpoint_time", record.endpoint.time_value is not None),
    ]:
        checks += 1
        if has_value and (_field_supported(record, field_name) or field_name == "formulation"):
            supported += 1
    return supported / checks if checks else 0.0


def _record_fragments(record: Record) -> list[str]:
    return [
        record.device,
        record.provenance.route_notes,
        *(
            str(value)
            for key, value in record.provenance.metadata.get("route_raw_labels", {}).items()
            if key
            in {
                "where_franz",
                "where_diffusion_cell",
                "where_endpoint",
                "endpoint_carrier_snippet",
                "formulation_carrier_snippet",
                "notes",
                "barrier_name_raw",
                "study_type",
            }
            and value
        ),
        *record.source_notes,
        *(
            str(item.get("snippet", "") or "")
            for item in record.provenance.metadata.get("route_anchor_evidence", [])
            if isinstance(item, dict)
        ),
        *(
            str(item.get("locator", "") or "")
            for item in record.provenance.metadata.get("route_anchor_evidence", [])
            if isinstance(item, dict)
        ),
        *(item.snippet for item in record.evidence_items),
        *(item.locator for item in record.evidence_items),
    ]


def _route_raw_labels(record: Record) -> dict[str, str]:
    payload = record.provenance.metadata.get("route_raw_labels", {})
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items() if value is not None}


def _route_raw_label_fragments(record: Record) -> list[str]:
    raw_labels = _route_raw_labels(record)
    fragments: list[str] = []
    for key in (
        "where_franz",
        "where_diffusion_cell",
        "where_endpoint",
        "endpoint_carrier_snippet",
        "formulation_carrier_snippet",
        "notes",
        "barrier_name_raw",
        "study_type",
    ):
        value = " ".join((raw_labels.get(key, "") or "").split()).strip()
        if value and value.lower() not in {"unknown", "uncertain"}:
            fragments.append(value)
    return fragments


def _route_label_device_hint(record: Record) -> tuple[str, str]:
    raw_labels = _route_raw_labels(record)
    franz_confirmed = (raw_labels.get("franz_confirmed", "") or "").strip().lower()
    where_franz = (raw_labels.get("where_franz", "") or "").strip()
    where_diffusion = (raw_labels.get("where_diffusion_cell", "") or "").strip()
    mentions_diffusion = (raw_labels.get("mentions_diffusion_cell", "") or "").strip().lower()

    if franz_confirmed == "yes" or ("franz" in where_franz.lower() and where_franz.lower() not in {"unknown", "uncertain"}):
        return "Franz diffusion cell", where_franz or where_diffusion or record.provenance.route_notes
    if mentions_diffusion == "yes" or (where_diffusion and where_diffusion.lower() not in {"unknown", "uncertain"}):
        return "diffusion cell", where_diffusion or record.provenance.route_notes
    return "", ""


def _route_anchor_items(record: Record) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for payload in record.provenance.metadata.get("route_anchor_evidence", []):
        if not isinstance(payload, dict):
            continue
        try:
            items.append(EvidenceItem.model_validate(payload))
        except Exception:
            continue
    return items


def _append_route_anchor_support(record: Record, field_name: str) -> None:
    if _field_supported(record, field_name):
        return
    for item in _route_anchor_items(record):
        if item.field_name != field_name:
            continue
        record.evidence_items.append(item)
        return


def _has_figure_endpoint_evidence(record: Record) -> bool:
    return any(item.field_name == "endpoint" and item.modality == "figure" for item in record.evidence_items)


def _supported_modalities(record: Record) -> set[str]:
    return {item.modality for item in record.evidence_items if item.modality != "metadata"}


def _has_table_formulation_support(record: Record) -> bool:
    return any(item.field_name in {"formulation", "api_concentration"} and item.modality == "table" for item in record.evidence_items)


def _looks_non_target_study(*fragments: str) -> bool:
    lowered = " ".join(" ".join((fragment or "").split()).lower() for fragment in fragments if fragment).strip()
    if not lowered:
        return False
    if (
        any(token in lowered for token in ("pampa", "skin pampa", "parallel artificial membrane permeability assay"))
        and any(
            token in lowered
            for token in (
                "franz diffusion cell",
                "franz cell",
                "vertical diffusion",
                "receptor compartment",
                "receiver compartment",
                "cumulative amount permeated",
                "skin permeation",
            )
        )
    ):
        return False
    return any(
        token in lowered
        for token in (
            "clinical trial",
            "randomized",
            "patients",
            "healthy volunteers",
            "venous leg ulcer",
            "kat i",
            "kat ii",
            "enzyme activity",
            "analgesic effect",
            "pain relief",
            "risk ratio",
            "pampa",
            "skin pampa",
            "parallel artificial membrane permeability assay",
            "review article",
            "systematic review",
        )
    )


def _first_area_support(record: Record) -> str:
    for item in record.evidence_items:
        if item.field_name == "area" and item.snippet:
            return item.snippet
    for fragment in _record_fragments(record):
        if parse_area_cm2(fragment) is not None:
            return fragment
    return ""


def _first_api_support(record: Record) -> str:
    for item in record.evidence_items:
        if item.field_name == "api_concentration" and item.snippet:
            return item.snippet
    for fragment in [
        record.formulation.api_concentration_raw,
        record.formulation.label,
        record.formulation.dosage_form,
        *record.source_notes,
        *(item.snippet for item in record.evidence_items),
    ]:
        if fragment:
            return fragment
    return ""


def _component_api_fragments(record: Record) -> list[str]:
    fragments: list[str] = []
    for component in record.formulation.components:
        if component.name and component.raw:
            fragments.append(" ".join(part for part in (component.name, component.raw) if part))
        if component.name and component.note:
            fragments.append(" ".join(part for part in (component.name, component.note) if part))
        if component.raw:
            fragments.append(component.raw)
        if component.note:
            fragments.append(component.note)
    return fragments


def _api_search_fragments(record: Record, source_fragments: list[str] | None = None) -> list[str]:
    return [
        record.formulation.api_concentration_raw,
        record.formulation.label,
        record.formulation.dosage_form,
        *_component_api_fragments(record),
        *record.source_notes,
        *(source_fragments or []),
        *(item.snippet for item in record.evidence_items),
    ]


def _normalized_fragment_text(text: str) -> str:
    return " ".join((text or "").lower().replace("µ", "u").replace("μ", "u").split())


def _value_tokens(value: float | None) -> list[str]:
    if value is None:
        return []
    return sorted(
        {
            f"{float(value):g}".lower(),
            f"{float(value):.1f}".rstrip("0").rstrip(".").lower(),
            f"{float(value):.2f}".rstrip("0").rstrip(".").lower(),
            str(int(round(float(value)))).lower(),
        },
        key=len,
        reverse=True,
    )


def _best_support_fragment(
    fragments: list[str],
    *,
    required_terms: list[str] | None = None,
    preferred_terms: list[str] | None = None,
    value: float | None = None,
    unit: str = "",
) -> str:
    best_fragment = ""
    best_score = 0
    value_tokens = _value_tokens(value)
    unit_token = _normalized_fragment_text(unit)
    for fragment in fragments:
        cleaned = " ".join((fragment or "").split()).strip()
        lowered = _normalized_fragment_text(cleaned)
        if not lowered:
            continue
        score = 0
        if required_terms and not all(term in lowered for term in required_terms):
            continue
        if value_tokens and any(token and token in lowered for token in value_tokens):
            score += 4
        if unit_token and unit_token in lowered:
            score += 2
        for term in preferred_terms or []:
            if term and term in lowered:
                score += 2
        if score > best_score:
            best_score = score
            best_fragment = cleaned
    return best_fragment


def _endpoint_support_fragment(record: Record, support_fragments: list[str]) -> str:
    preferred_terms = ["endpoint", "amount", "permeat", "release", "cumulative", "after"]
    if record.endpoint.kind == "flux":
        preferred_terms = ["flux", "steady state", "jss"]
    elif record.endpoint.kind == "percent":
        preferred_terms = ["%", "percent", "release"]
    return _best_support_fragment(
        support_fragments,
        preferred_terms=preferred_terms,
        value=record.endpoint.value,
        unit=record.endpoint.unit,
    )


def _formulation_support_fragment(record: Record, support_fragments: list[str]) -> str:
    label_key = _normalize_label_key(record.formulation.label)
    preferred_terms = [record.formulation.api_name.lower() if record.formulation.api_name else "ibuprofen", "formulation", "table"]
    if label_key:
        preferred_terms.extend(part for part in label_key.split() if part)
    return _best_support_fragment(support_fragments, preferred_terms=preferred_terms)


def _collect_paper_device_hints(records: list[Record]) -> dict[str, tuple[str, str]]:
    hints: dict[str, tuple[str, str]] = {}
    strengths: dict[str, int] = {}
    for record in records:
        fragments = _record_fragments(record)
        inferred = infer_device_label(*fragments)
        if not inferred:
            continue
        strength = device_label_strength(inferred)
        if strength <= strengths.get(record.paper_id, 0):
            continue
        support = find_device_support_fragment(inferred, *fragments) or inferred
        hints[record.paper_id] = (inferred, support)
        strengths[record.paper_id] = strength
    return hints


def _collect_paper_area_hints(records: list[Record]) -> dict[str, tuple[float, str]]:
    grouped: dict[str, list[tuple[float, str]]] = {}
    for record in records:
        area = record.conditions.diffusion_area_cm2
        if area is None:
            continue
        support = _first_area_support(record) or f"{area:g} cm2"
        grouped.setdefault(record.paper_id, []).append((round(float(area), 4), support))

    hints: dict[str, tuple[float, str]] = {}
    for paper_id, entries in grouped.items():
        unique_values = {value for value, _ in entries}
        if len(unique_values) == 1:
            area_value = entries[0][0]
            support = next((support for value, support in entries if value == area_value and support), f"{area_value:g} cm2")
            hints[paper_id] = (area_value, support)
    return hints


def _normalize_label_key(label: str) -> str:
    return " ".join((label or "").strip().lower().split())


def _collect_api_hints(records: list[Record]) -> tuple[dict[tuple[str, str], tuple[float, str, str, str]], dict[str, tuple[float, str, str, str]]]:
    by_label_entries: dict[tuple[str, str], list[tuple[float, str, str, str, int]]] = {}
    by_paper_entries: dict[str, list[tuple[float, str, str, str, int]]] = {}
    for record in records:
        value = record.formulation.api_concentration_value
        unit = record.formulation.api_concentration_unit
        basis = record.formulation.api_basis
        support = _first_api_support(record)
        if value is None:
            inferred_value, inferred_unit, inferred_basis, inferred_fragment = infer_api_concentration_from_fragments(
                _api_search_fragments(record),
                api_name=record.formulation.api_name or "ibuprofen",
                formulation_label=record.formulation.label,
                dosage_form=record.formulation.dosage_form,
                prefer_strict_scope=True,
            )
            if inferred_value is None:
                continue
            value = inferred_value
            unit = inferred_unit
            basis = inferred_basis
            support = inferred_fragment
        payload = (
            float(value),
            unit,
            basis,
            support or f"{value:g} {unit}".strip(),
            api_concentration_quality(value, unit, basis, support or record.formulation.api_concentration_raw, prefer_strict_scope=True),
        )
        label_key = _normalize_label_key(record.formulation.label)
        if label_key:
            by_label_entries.setdefault((record.paper_id, label_key), []).append(payload)
        by_paper_entries.setdefault(record.paper_id, []).append(payload)

    by_label: dict[tuple[str, str], tuple[float, str, str, str]] = {}
    for key, entries in by_label_entries.items():
        best = max(entries, key=lambda item: item[4])
        if best[4] >= STRICT_SHARED_API_HINT_MIN_QUALITY:
            by_label[key] = best[:4]

    by_paper: dict[str, tuple[float, str, str, str]] = {}
    for paper_id, entries in by_paper_entries.items():
        best = max(entries, key=lambda item: item[4])
        if best[4] >= STRICT_SHARED_API_HINT_MIN_QUALITY:
            by_paper[paper_id] = best[:4]
    return by_label, by_paper


def _normalize_record_fields(
    candidate: Record,
    *,
    policy: V1StrictIbuprofen5PctPolicy,
    paper_device_hint: tuple[str, str] | None = None,
    paper_area_hint: tuple[float, str] | None = None,
    label_api_hint: tuple[float, str, str, str] | None = None,
    paper_api_hint: tuple[float, str, str, str] | None = None,
) -> None:
    route_anchor_items = _route_anchor_items(candidate)
    route_label_fragments = _route_raw_label_fragments(candidate)
    candidate.endpoint.kind = coerce_endpoint_kind_from_unit(candidate.endpoint.kind, candidate.endpoint.unit)
    source_fragments = collect_source_fragments(
        candidate,
        keywords=[
            "franz",
            "vertical diffusion",
            "diffusion cell",
            "donor",
            "receptor",
            "receiver",
            "effective area",
            "diffusion area",
            "sampling port",
            "ibuprofen",
            "% w/w",
            "mg/g",
            "drug loading",
        ],
        max_fragments=10,
    )
    support_fragments = [
        candidate.provenance.route_notes,
        *route_label_fragments,
        *candidate.source_notes,
        *source_fragments,
        *(item.snippet for item in route_anchor_items),
        *(item.locator for item in route_anchor_items),
        *(item.snippet for item in candidate.evidence_items),
    ]
    _append_route_anchor_support(candidate, "device")
    _append_route_anchor_support(candidate, "endpoint")
    _append_route_anchor_support(candidate, "formulation")
    study_type_hint = infer_study_type_label(
        candidate.study_type,
        candidate.provenance.route_notes,
        *route_label_fragments,
        *candidate.source_notes,
        *source_fragments,
        *(item.snippet for item in route_anchor_items),
        *(item.snippet for item in candidate.evidence_items),
    )
    current_study_type = candidate.study_type or "uncertain"
    if study_type_hint and study_type_hint != "uncertain":
        candidate.study_type = study_type_hint
    elif current_study_type not in {"IVPT", "IVRT", "both"} and _looks_non_target_study(
        candidate.provenance.route_notes,
        *candidate.source_notes,
        *source_fragments,
        *(item.snippet for item in candidate.evidence_items),
    ):
        candidate.study_type = "uncertain"

    normalized_device = infer_device_label(
        candidate.device,
        candidate.provenance.route_notes,
        *route_label_fragments,
        *candidate.source_notes,
        *source_fragments,
        *(item.snippet for item in route_anchor_items),
        *(item.snippet for item in candidate.evidence_items),
        *(item.locator for item in candidate.evidence_items),
    )
    existing_device = (candidate.device or "").strip()
    route_device_hint, route_device_support = _route_label_device_hint(candidate)
    non_target_device_context = _looks_non_target_study(
        candidate.device,
        candidate.provenance.route_notes,
        *route_label_fragments,
        *candidate.source_notes,
        *source_fragments,
        *(item.snippet for item in route_anchor_items),
        *(item.snippet for item in candidate.evidence_items),
    )
    if normalized_device == "" and existing_device and device_label_strength(existing_device) >= 4:
        normalized_device = existing_device
    if route_device_hint and device_label_strength(route_device_hint) > device_label_strength(normalized_device):
        normalized_device = route_device_hint
    if normalized_device == "" and non_target_device_context and device_label_strength(existing_device) == 0:
        candidate.device = ""
    if not non_target_device_context and paper_device_hint and device_label_strength(paper_device_hint[0]) > device_label_strength(normalized_device):
        normalized_device = paper_device_hint[0]
    if normalized_device:
        candidate.device = normalized_device
        support_fragment = find_device_support_fragment(
            normalized_device,
            candidate.provenance.route_notes,
            *route_label_fragments,
            *candidate.source_notes,
            *source_fragments,
            *(item.snippet for item in route_anchor_items),
            *(item.snippet for item in candidate.evidence_items),
        )
        if not support_fragment and paper_device_hint and paper_device_hint[0] == normalized_device:
            support_fragment = paper_device_hint[1]
        if not support_fragment and route_device_hint == normalized_device:
            support_fragment = route_device_support
        if not support_fragment:
            support_fragment = next(
                (
                    item.snippet
                    for item in route_anchor_items
                    if item.field_name == "device" and item.snippet
                ),
                "",
            )
        if support_fragment:
            _append_support_evidence(candidate, "device", support_fragment)

    if candidate.formulation.label and not _field_supported(candidate, "formulation"):
        formulation_fragment = _formulation_support_fragment(candidate, support_fragments)
        if formulation_fragment:
            _append_support_evidence(candidate, "formulation", formulation_fragment, confidence=0.56)

    normalized_endpoint_time_h = None
    if candidate.endpoint.time_value is not None:
        normalized_endpoint_time_h = normalize_time_to_hours(candidate.endpoint.time_value, candidate.endpoint.time_unit)
    if candidate.conditions.duration_h is None and normalized_endpoint_time_h is not None:
        candidate.conditions.duration_h = normalized_endpoint_time_h
    if candidate.conditions.duration_h is not None and normalized_endpoint_time_h is None:
        candidate.endpoint.time_value = candidate.conditions.duration_h
        candidate.endpoint.time_unit = "hours"

    if candidate.conditions.diffusion_area_cm2 is None:
        for fragment in [
            candidate.provenance.route_notes,
            *route_label_fragments,
            *candidate.source_notes,
            *source_fragments,
            *(item.snippet for item in candidate.evidence_items),
            *(item.locator for item in candidate.evidence_items),
        ]:
            parsed_area = parse_area_cm2(fragment)
            if parsed_area is not None:
                candidate.conditions.diffusion_area_cm2 = parsed_area
                _append_support_evidence(candidate, "area", fragment)
                break
    if candidate.conditions.diffusion_area_cm2 is None and paper_area_hint is not None:
        candidate.conditions.diffusion_area_cm2 = paper_area_hint[0]
        _append_support_evidence(candidate, "area", paper_area_hint[1], confidence=0.58)

    if candidate.conditions.receptor_volume_ml is None:
        for fragment in [
            candidate.provenance.route_notes,
            *route_label_fragments,
            *candidate.source_notes,
            *source_fragments,
            *(item.snippet for item in candidate.evidence_items),
        ]:
            parsed_volume = parse_receptor_volume_ml(fragment)
            if parsed_volume is not None:
                candidate.conditions.receptor_volume_ml = parsed_volume
                _append_support_evidence(candidate, "receptor_volume", fragment)
                break

    concentration_status = policy.concentration_scope_status(candidate)
    if candidate.formulation.api_concentration_value is None or concentration_status in {"ambiguous", "out_of_scope"}:
        value, unit, basis, source_fragment = infer_api_concentration_from_fragments(
            _api_search_fragments(candidate, source_fragments),
            api_name=candidate.formulation.api_name or "ibuprofen",
            formulation_label=candidate.formulation.label,
            dosage_form=candidate.formulation.dosage_form,
            prefer_strict_scope=True,
        )
        if value is not None and is_strict_api_concentration_hint(
            value,
            unit,
            basis,
            source_fragment,
            min_quality=STRICT_SHARED_API_HINT_MIN_QUALITY,
        ):
            candidate.formulation.api_concentration_value = value
            candidate.formulation.api_concentration_unit = unit or candidate.formulation.api_concentration_unit
            candidate.formulation.api_basis = basis or candidate.formulation.api_basis
            _append_support_evidence(candidate, "api_concentration", source_fragment)
    if candidate.formulation.api_concentration_value is None:
        shared_hint = label_api_hint or paper_api_hint
        if shared_hint is not None:
            value, unit, basis, source_fragment = shared_hint
            if is_strict_api_concentration_hint(
                value,
                unit,
                basis,
                source_fragment,
                min_quality=STRICT_SHARED_API_HINT_MIN_QUALITY,
            ):
                candidate.formulation.api_concentration_value = value
                candidate.formulation.api_concentration_unit = unit or candidate.formulation.api_concentration_unit
                candidate.formulation.api_basis = basis or candidate.formulation.api_basis
                _append_support_evidence(candidate, "api_concentration", source_fragment, confidence=0.58)
    (
        candidate.formulation.api_concentration_value,
        candidate.formulation.api_concentration_unit,
        candidate.formulation.api_basis,
    ) = normalize_api_concentration_fields(
        candidate.formulation.api_concentration_value,
        candidate.formulation.api_concentration_unit,
        candidate.formulation.api_basis,
        candidate.formulation.api_concentration_raw,
    )
    shared_hint = label_api_hint or paper_api_hint
    if shared_hint is not None:
        shared_value, shared_unit, shared_basis, shared_fragment = shared_hint
        current_quality = api_concentration_quality(
            candidate.formulation.api_concentration_value,
            candidate.formulation.api_concentration_unit,
            candidate.formulation.api_basis,
            candidate.formulation.api_concentration_raw,
            prefer_strict_scope=True,
        )
        shared_quality = api_concentration_quality(
            shared_value,
            shared_unit,
            shared_basis,
            shared_fragment,
            prefer_strict_scope=True,
        )
        if (
            shared_quality >= STRICT_SHARED_API_HINT_MIN_QUALITY
            and shared_quality > current_quality
            and policy.concentration_scope_status(candidate) != "ok"
        ):
            candidate.formulation.api_concentration_value = shared_value
            candidate.formulation.api_concentration_unit = shared_unit or candidate.formulation.api_concentration_unit
            candidate.formulation.api_basis = shared_basis or candidate.formulation.api_basis
            _append_support_evidence(candidate, "api_concentration", shared_fragment, confidence=0.58)

    if candidate.formulation.api_concentration_value is not None and not _field_supported(candidate, "api_concentration"):
        api_fragment = _best_support_fragment(
            support_fragments,
            preferred_terms=["ibuprofen", "formulation", "table"],
            value=candidate.formulation.api_concentration_value,
            unit=candidate.formulation.api_concentration_unit,
        )
        if api_fragment:
            _append_support_evidence(candidate, "api_concentration", api_fragment, confidence=0.56)

    if candidate.endpoint.time_value is not None and not _field_supported(candidate, "endpoint_time"):
        for fragment in [*route_label_fragments, *candidate.source_notes, *source_fragments, *(item.snippet for item in candidate.evidence_items)]:
            if normalize_time_to_hours(candidate.endpoint.time_value, candidate.endpoint.time_unit) is not None and any(
                token in fragment.lower() for token in ("hour", "hr", "min", "day", "after", " at ")
            ):
                _append_support_evidence(candidate, "endpoint_time", fragment)
                break

    if candidate.endpoint.value is not None and not _field_supported(candidate, "endpoint"):
        endpoint_fragment = _endpoint_support_fragment(candidate, support_fragments)
        if endpoint_fragment:
            _append_support_evidence(candidate, "endpoint", endpoint_fragment, confidence=0.56)

    if candidate.endpoint.kind == "amount_per_area" and candidate.endpoint.normalized_value is None:
        value, unit = normalize_amount_per_area(candidate.endpoint.value, candidate.endpoint.unit)
        candidate.endpoint.normalized_value = value
        candidate.endpoint.normalized_unit = unit
    elif candidate.endpoint.kind == "amount_total" and candidate.endpoint.normalized_value is None:
        value, unit = amount_total_or_receiver_concentration_to_ug_per_cm2(
            candidate.endpoint.value,
            candidate.endpoint.unit,
            candidate.conditions.diffusion_area_cm2,
            candidate.conditions.receptor_volume_ml,
        )
        candidate.endpoint.normalized_value = value
        candidate.endpoint.normalized_unit = unit


def _route_specific_support_threshold(route: str) -> float:
    if route == "table":
        return 0.45
    if route in {"text", "mixed"}:
        return 0.6
    if route == "figure":
        return 0.55
    return 0.5


def _route_specific_failure_codes(record: Record) -> list[str]:
    codes: list[str] = []
    support_rate = _verification_support_rate(record)
    modalities = _supported_modalities(record)
    has_device_support = _field_supported(record, "device")
    has_endpoint_support = _field_supported(record, "endpoint")
    has_api_support = _field_supported(record, "api_concentration")

    if support_rate < _route_specific_support_threshold(record.route):
        codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)

    if record.route == "text":
        if not has_device_support or not has_endpoint_support:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)

    if record.route == "mixed":
        if len(modalities) < 2:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)
        if not has_device_support or not has_endpoint_support:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)

    if record.route == "figure":
        if record.endpoint.value is None and not _has_figure_endpoint_evidence(record):
            codes.append(FailureCode.FIGURE_DIGITIZATION_FAILED.value)
        if not record.formulation.label:
            codes.append(FailureCode.AMBIGUOUS_MAPPING.value)
        elif record.mapping_confidence is not None and record.mapping_confidence < 0.6:
            codes.append(FailureCode.AMBIGUOUS_MAPPING.value)
        if not has_device_support:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)
        if not _has_table_formulation_support(record) and record.mapping_confidence is not None and record.mapping_confidence < 0.75:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)

    deduped: list[str] = []
    for code in codes:
        if code and code not in deduped:
            deduped.append(code)
    return deduped


def _derive_scope_bucket(record: Record, failure_codes: list[str], policy: V1StrictIbuprofen5PctPolicy) -> tuple[str, list[str]]:
    code_set = {code for code in failure_codes if code}
    tags: list[str] = []
    api_name = (record.formulation.api_name or "").strip().lower()

    if not code_set:
        return "strict_in_scope", tags

    if api_name and api_name != policy.api_name:
        return "out_of_scope", ["non_target_api"]

    if code_set & {
        FailureCode.NOT_TARGET_API_CONCENTRATION.value,
        FailureCode.NOT_TARGET_ENDPOINT.value,
        FailureCode.NOT_TARGET_DEVICE.value,
        FailureCode.NOT_TARGET_STUDY_TYPE.value,
    }:
        tags.append("useful_but_out_of_scope")
        if FailureCode.NOT_TARGET_API_CONCENTRATION.value in code_set:
            tags.append("useful_api_concentration_out_of_scope")
        if FailureCode.NOT_TARGET_ENDPOINT.value in code_set or FailureCode.PERCENT_ONLY.value in code_set:
            tags.append("useful_endpoint_out_of_scope")
        if FailureCode.NOT_TARGET_DEVICE.value in code_set:
            tags.append("useful_device_out_of_scope")
        if FailureCode.NOT_TARGET_STUDY_TYPE.value in code_set:
            tags.append("useful_study_type_out_of_scope")
        return "useful_but_out_of_scope", tags

    if classify_outcome(code_set) == "unresolved":
        tags.append("recoverable_unresolved")
        for code, tag in RECOVERABLE_SCOPE_TAGS.items():
            if code in code_set and tag not in tags:
                tags.append(tag)
        if len(tags) == 1:
            tags.append("recoverable_other")
        return "recoverable_unresolved", tags

    return "out_of_scope", tags


def _collect_failure_codes(record: Record, policy: V1StrictIbuprofen5PctPolicy) -> list[str]:
    codes: list[str] = []

    codes.extend(apply_source_context_guard(record))

    if record.route == "unresolved":
        codes.append(FailureCode.UNRESOLVED_ROUTE.value)

    api_name = (record.formulation.api_name or "").strip().lower()
    if api_name and api_name != policy.api_name:
        codes.append(FailureCode.NOT_TARGET_API.value)

    if record.study_type not in policy.allowed_study_types:
        codes.append(FailureCode.NOT_TARGET_STUDY_TYPE.value)

    device = (record.device or "").strip().lower()
    if device:
        if policy.required_device_term not in device:
            codes.append(FailureCode.NOT_TARGET_DEVICE.value)
    else:
        codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)

    has_api_support = _field_supported(record, "api_concentration")
    concentration_status = policy.concentration_scope_status(record)
    if concentration_status == "missing":
        codes.append(FailureCode.MISSING_API_CONCENTRATION.value)
    elif concentration_status == "ambiguous":
        if has_api_support or record.route == "table":
            codes.append(FailureCode.AMBIGUOUS_API_CONCENTRATION.value)
        else:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)
    elif concentration_status == "out_of_scope":
        if has_api_support or record.route == "table":
            codes.append(FailureCode.NOT_TARGET_API_CONCENTRATION.value)
        else:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)

    has_endpoint_support = _field_supported(record, "endpoint")
    endpoint_status = policy.endpoint_scope_status(record)
    effective_kind, _ = _effective_endpoint_kind(record, policy)
    if endpoint_status == "missing":
        codes.append(FailureCode.MISSING_ENDPOINT.value)
    elif endpoint_status == "out_of_scope":
        if has_endpoint_support or record.route == "table":
            codes.append(FailureCode.NOT_TARGET_ENDPOINT.value)
        else:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)
    elif effective_kind == "percent":
        if has_endpoint_support or record.route == "table":
            codes.append(FailureCode.PERCENT_ONLY.value)
        else:
            codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)
    elif endpoint_status == "ambiguous":
        codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)

    if record.endpoint.time_value is None:
        codes.append(FailureCode.MISSING_ENDPOINT_TIME.value)

    if effective_kind == "amount_total" and record.conditions.diffusion_area_cm2 is None:
        codes.append(FailureCode.MISSING_AREA.value)

    if effective_kind in {"amount_per_area", "amount_total"} and record.endpoint.normalized_value is None:
        if effective_kind == "amount_total" and record.conditions.diffusion_area_cm2 is None:
            pass
        else:
            codes.append(FailureCode.UNIT_NORMALIZATION_FAILED.value)

    if record.route == "figure" and (not record.formulation.label or (record.mapping_confidence is not None and record.mapping_confidence < 0.5)):
        codes.append(FailureCode.AMBIGUOUS_MAPPING.value)

    has_figure_endpoint = _has_figure_endpoint_evidence(record) and record.endpoint.value is not None
    if record.endpoint.value is None and not has_figure_endpoint and any(note.startswith("figure_plot_context_missing") for note in record.source_notes):
        codes.append(FailureCode.FIGURE_PLOT_CONTEXT_MISSING.value)
    elif record.endpoint.value is None and not has_figure_endpoint and any(
        note.startswith("figure_digitization_failure:")
        or note.startswith("figure_no_digitized_endpoint")
        or note.startswith("figure_mapping_unresolved")
        for note in record.source_notes
    ):
        codes.append(FailureCode.FIGURE_DIGITIZATION_FAILED.value)

    support_rate = _verification_support_rate(record)
    if support_rate < 0.5:
        codes.append(FailureCode.INSUFFICIENT_EVIDENCE.value)
    codes.extend(_route_specific_failure_codes(record))

    deduped: list[str] = []
    for code in codes:
        if code not in deduped:
            deduped.append(code)
    return deduped


def verify_records(
    records: Iterable[Record],
    policy: V1StrictIbuprofen5PctPolicy | None = None,
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[Record]:
    """Verify canonical records against evidence sufficiency and policy scope."""

    active_policy = policy or V1StrictIbuprofen5PctPolicy()
    verified: list[Record] = []

    record_list = list(records)
    paper_device_hints = _collect_paper_device_hints(record_list)
    paper_area_hints = _collect_paper_area_hints(record_list)
    api_hints_by_label, api_hints_by_paper = _collect_api_hints(record_list)
    for index, record in enumerate(record_list, start=1):
        if progress_callback:
            progress_callback(index - 1, record.paper_id, "verifying evidence")
        candidate = record.model_copy(deep=True)
        _normalize_record_fields(
            candidate,
            policy=active_policy,
            paper_device_hint=paper_device_hints.get(candidate.paper_id),
            paper_area_hint=paper_area_hints.get(candidate.paper_id),
            label_api_hint=api_hints_by_label.get((candidate.paper_id, _normalize_label_key(candidate.formulation.label))),
            paper_api_hint=api_hints_by_paper.get(candidate.paper_id),
        )
        effective_kind, reclassification_reason = _effective_endpoint_kind(candidate, active_policy)
        if reclassification_reason:
            candidate.provenance.metadata["verification_effective_kind"] = effective_kind
            candidate.provenance.metadata["verification_reclassification_reason"] = reclassification_reason
        candidate.verification_support_rate = _verification_support_rate(candidate)
        candidate.failure_reasons = _collect_failure_codes(candidate, active_policy)
        candidate.failure_reason = candidate.failure_reasons[0] if candidate.failure_reasons else None
        candidate.verification_status = classify_outcome(candidate.failure_reasons)  # type: ignore[assignment]
        candidate.scope_bucket, candidate.scope_tags = _derive_scope_bucket(candidate, candidate.failure_reasons, active_policy)
        if candidate.failure_reason:
            candidate.source_notes.append(f"failure_taxonomy:{candidate.failure_reason}")
        if candidate.scope_bucket == "useful_but_out_of_scope" and "scope_bucket:useful_but_out_of_scope" not in candidate.source_notes:
            candidate.source_notes.append("scope_bucket:useful_but_out_of_scope")
        verified.append(candidate)
        if progress_callback:
            progress_callback(index, record.paper_id, f"status={candidate.verification_status}")

    if output_jsonl:
        write_records_jsonl(verified, output_jsonl)
    if output_csv:
        write_records_csv(verified, output_csv)
    return verified
