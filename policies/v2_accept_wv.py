from __future__ import annotations

from dataclasses import dataclass
import re

from policies.v1_strict_ibuprofen_5pct import V1StrictIbuprofen5PctPolicy
from schemas.models import Record


def _compact(text: str) -> str:
    return re.sub(r"\s*/\s*", "/", (text or "").strip().lower())


def _is_five_weight_volume_percent(record: Record) -> bool:
    formulation = record.formulation
    value = formulation.api_concentration_value
    unit = _compact(formulation.api_concentration_unit)
    basis = _compact(formulation.api_basis)
    raw = _compact(formulation.api_concentration_raw)

    if value is not None and "%" in unit and ("w/v" in unit or "w/v" in basis or "wt/vol" in unit or "wt/vol" in basis):
        return abs(float(value) - 5.0) < 1e-9
    if value is not None and unit == "mg/ml":
        return abs(float(value) - 50.0) < 1e-9
    return any(token in raw for token in ("5% w/v", "5 % w/v", "5% (w/v)", "5 % (w/v)", "50 mg/ml"))


@dataclass(slots=True)
class V2AcceptWvPolicy(V1StrictIbuprofen5PctPolicy):
    """V2 policy that accepts 5% w/v or 50 mg/mL ibuprofen formulations."""

    name: str = "v2_accept_wv"

    def concentration_scope_status(self, record: Record) -> str:
        if _is_five_weight_volume_percent(record):
            return "ok"
        return V1StrictIbuprofen5PctPolicy.concentration_scope_status(self, record)
