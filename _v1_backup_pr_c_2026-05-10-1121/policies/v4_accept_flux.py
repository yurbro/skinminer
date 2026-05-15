from __future__ import annotations

from dataclasses import dataclass
import re

from policies.v3_any_ibuprofen_concentration import V3AnyIbuprofenConcentrationPolicy
from schemas.models import Record

FLUX_UNITS = frozenset(
    {
        "ug/cm2/h",
        "\u00b5g/cm2/h",
        "\u03bcg/cm2/h",
        "\u00c2\u00b5g/cm2/h",
        "ug/cm^2/h",
        "\u00b5g/cm^2/h",
        "\u03bcg/cm^2/h",
        "ug/cm\u00b2/h",
        "\u00b5g/cm\u00b2/h",
        "\u03bcg/cm\u00b2/h",
        "ug/cm2/hr",
        "ug/cm^2/hr",
        "ug cm-2 h-1",
        "\u00b5g cm-2 h-1",
        "\u03bcg cm-2 h-1",
        "ug.cm-2.h-1",
        "ug/(cm2 h)",
        "\u00b5g/(cm2 h)",
        "\u03bcg/(cm2 h)",
        "ug/(cm^2 h)",
        "\u00b5g/(cm^2 h)",
        "\u03bcg/(cm^2 h)",
        "mg/cm2/h",
        "mg/cm^2/h",
        "mg/cm2/hr",
        "mg cm-2 h-1",
        "mg/(cm2 h)",
        "mg/(cm^2 h)",
        "nmol/cm2/h",
        "nmol cm-2 h-1",
        "nmol/(cm2 h)",
        "pmol/cm2/h",
    }
)


def _clean_endpoint_text(text: str) -> str:
    replacements = {
        "\u00c3\u0192\u00e2\u20ac\u0161\u00c3\u201a\u00c2\u00b5": "u",
        "\u00c3\u201a\u00c2\u00b5": "u",
        "\u00c3\u017d\u00c2\u00bc": "u",
        "\u00c2\u00b5": "u",
        "\u00b5": "u",
        "\u03bc": "u",
        "\u00c3\u0192\u00e2\u20ac\u0161\u00c3\u201a\u00c2\u00b2": "2",
        "\u00c3\u201a\u00c2\u00b2": "2",
        "\u00c2\u00b2": "2",
        "\u00b2": "2",
        "\u00c3\u00a2\u00c2\u0081\u00c2\u00bb": "-",
        "\u00e2\u0081\u00bb": "-",
        "\u207b": "-",
        "\u00c3\u00a2\u02c6\u00e2\u20ac\u2122": "-",
        "\u00e2\u02c6\u2019": "-",
        "\u2212": "-",
    }
    cleaned = text or ""
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    return cleaned.lower()


def _compact_endpoint_text(text: str) -> str:
    return re.sub(r"\s+", "", _clean_endpoint_text(text))


def _normalize_unit(unit: str | None) -> str:
    if unit is None:
        return ""
    return _clean_endpoint_text(unit).replace(" ", "").replace(".", "")


FLUX_UNITS_NORMALIZED = frozenset(_normalize_unit(unit) for unit in FLUX_UNITS)


def is_flux_unit(unit: str | None) -> bool:
    return _normalize_unit(unit) in FLUX_UNITS_NORMALIZED


def _looks_like_permeability_unit(unit: str) -> bool:
    compact = _compact_endpoint_text(unit)
    return any(term in compact for term in ("cm/h", "cm/hr", "cm/s", "cmsec-1", "cmh-1", "cms-1"))


def _permeability_context(record: Record) -> str:
    snippets = " ".join(item.snippet for item in record.evidence_items if item.field_name in {"endpoint", "endpoint_value", "endpoint_unit"})
    return _clean_endpoint_text(" ".join([record.endpoint.field_name, record.endpoint.unit, snippets]))


def _looks_like_permeability_endpoint(record: Record) -> bool:
    if not _looks_like_permeability_unit(record.endpoint.unit):
        return False
    context = _permeability_context(record)
    return any(token in context for token in ("kp", "k p", "papp", "p app", "permeability coefficient", "permeability"))


@dataclass(slots=True)
class V4AcceptFluxPolicy(V3AnyIbuprofenConcentrationPolicy):
    """V4 policy that accepts V3 scope plus flux/Jss and permeability endpoints."""

    name: str = "v4_accept_flux"

    def effective_endpoint_kind(self, record: Record) -> tuple[str, str | None]:
        if record.endpoint.kind == "amount_per_area" and is_flux_unit(record.endpoint.unit):
            return "flux", "unit_implies_flux"
        return record.endpoint.kind, None

    def endpoint_scope_status(self, record: Record) -> str:
        if record.endpoint.value is None:
            return "missing"
        effective_kind, _ = self.effective_endpoint_kind(record)
        if effective_kind in {"flux", "jss"}:
            return "ok"
        if is_flux_unit(record.endpoint.unit):
            return "ok"
        if _looks_like_permeability_endpoint(record):
            return "ok"
        return V3AnyIbuprofenConcentrationPolicy.endpoint_scope_status(self, record)
