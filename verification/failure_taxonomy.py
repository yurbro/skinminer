"""Formal failure taxonomy for evidence-backed verification."""

from __future__ import annotations

from collections import Counter
from enum import StrEnum
from typing import Iterable

from schemas.models import Record


class FailureCode(StrEnum):
    """Reusable verification and patching failure codes."""

    MISSING_ENDPOINT = "missing_endpoint"
    MISSING_ENDPOINT_TIME = "missing_endpoint_time"
    MISSING_AREA = "missing_area"
    MISSING_API_CONCENTRATION = "missing_api_concentration"
    AMBIGUOUS_API_CONCENTRATION = "ambiguous_api_concentration"
    NOT_TARGET_API = "not_target_api"
    NOT_TARGET_API_CONCENTRATION = "not_target_api_concentration"
    NOT_TARGET_DEVICE = "not_target_device"
    NOT_TARGET_ENDPOINT = "not_target_endpoint"
    NOT_TARGET_STUDY_TYPE = "not_target_study_type"
    PERCENT_ONLY = "percent_only"
    UNRESOLVED_ROUTE = "unresolved_route"
    AMBIGUOUS_MAPPING = "ambiguous_mapping"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNIT_NORMALIZATION_FAILED = "unit_normalization_failed"
    FIGURE_DIGITIZATION_FAILED = "figure_digitization_failed"
    FIGURE_PLOT_CONTEXT_MISSING = "figure_plot_context_missing"


REJECTED_CODES = {
    FailureCode.NOT_TARGET_API.value,
    FailureCode.NOT_TARGET_DEVICE.value,
    FailureCode.NOT_TARGET_STUDY_TYPE.value,
}


UNRESOLVED_CODES = {
    FailureCode.MISSING_ENDPOINT.value,
    FailureCode.MISSING_ENDPOINT_TIME.value,
    FailureCode.MISSING_AREA.value,
    FailureCode.MISSING_API_CONCENTRATION.value,
    FailureCode.AMBIGUOUS_API_CONCENTRATION.value,
    FailureCode.NOT_TARGET_API_CONCENTRATION.value,
    FailureCode.NOT_TARGET_ENDPOINT.value,
    FailureCode.PERCENT_ONLY.value,
    FailureCode.UNRESOLVED_ROUTE.value,
    FailureCode.AMBIGUOUS_MAPPING.value,
    FailureCode.INSUFFICIENT_EVIDENCE.value,
    FailureCode.UNIT_NORMALIZATION_FAILED.value,
    FailureCode.FIGURE_DIGITIZATION_FAILED.value,
    FailureCode.FIGURE_PLOT_CONTEXT_MISSING.value,
}


def classify_outcome(failure_codes: Iterable[str]) -> str:
    """Classify verification status from a set of taxonomy codes."""

    codes = {code for code in failure_codes if code}
    if not codes:
        return "verified"
    if codes & REJECTED_CODES:
        return "rejected"
    return "unresolved"


def count_failure_codes(records: Iterable[Record], route: str | None = None) -> dict[str, int]:
    """Count failure codes across verified or unresolved records."""

    counter: Counter[str] = Counter()
    for record in records:
        if route is not None and record.route != route:
            continue
        for code in record.failure_reasons:
            if code:
                counter[code] += 1
    return dict(counter)


def count_failure_codes_by_route(records: Iterable[Record]) -> dict[str, dict[str, int]]:
    """Count failure taxonomy codes grouped by record route."""

    grouped: dict[str, Counter[str]] = {}
    for record in records:
        route_counter = grouped.setdefault(record.route, Counter())
        for code in record.failure_reasons:
            if code:
                route_counter[code] += 1
    return {route: dict(counter) for route, counter in sorted(grouped.items())}
