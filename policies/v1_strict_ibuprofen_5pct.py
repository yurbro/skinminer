from __future__ import annotations

from dataclasses import dataclass

from schemas.models import Record


def _is_amount_endpoint(kind: str) -> bool:
    return kind == "cumulative_amount"


def _amount_endpoint(record: Record):
    for endpoint in record.endpoints:
        if endpoint.kind == "cumulative_amount" and endpoint.mean is not None:
            return endpoint
    return None


def _is_out_of_scope_endpoint(kind: str) -> bool:
    return False


def _is_five_weight_percent(record: Record) -> bool:
    formulation = record.formulation
    value = formulation.api_concentration_value
    unit = (formulation.api_concentration_unit or "").lower()
    basis = (formulation.api_basis or "").lower()
    raw = (formulation.api_concentration_raw or "").lower()

    if value is not None and "%" in unit and ("w/w" in unit or "w/w" in basis or "wt" in unit or "wt" in basis):
        return abs(float(value) - 5.0) < 1e-9
    if value is not None and formulation.api_concentration_unit.lower() == "mg/g":
        return abs(float(value) - 50.0) < 1e-9
    return "5% w/w" in raw or "50 mg/g" in raw


def _concentration_scope_status(record: Record) -> str:
    formulation = record.formulation
    value = formulation.api_concentration_value
    unit = (formulation.api_concentration_unit or "").strip().lower()
    basis = (formulation.api_basis or "").strip().lower()
    raw = (formulation.api_concentration_raw or "").strip().lower()
    combined = " ".join(part for part in (unit, basis, raw) if part)

    if value is None and not raw:
        return "missing"
    if _is_five_weight_percent(record):
        return "ok"

    if any(token in combined for token in ("mg/kg", "ug/kg", "dose", "intraperitoneal", "oral", "intravenous", "subcutaneous")):
        return "out_of_scope"
    if basis == "molar" or unit in {"mm", "μm", "um", "nm"}:
        return "ambiguous"

    if any(token in combined for token in ("% w/w", "w/w", "wt%", "wt %", "wt/wt", "mg/g", "g/g")):
        return "out_of_scope"
    if any(token in combined for token in ("% w/v", "w/v", "mg/ml", "mg/l", "ug/ml", "g/l", "%")):
        return "ambiguous"

    return "ambiguous"


@dataclass(slots=True)
class V1StrictIbuprofen5PctPolicy:
    """Strict Round 1/2 scope policy for ibuprofen 5% w/w Franz IVPT/IVRT records."""

    name: str = "v1_strict_ibuprofen_5pct"
    api_name: str = "ibuprofen"
    required_device_term: str = "franz"
    allowed_study_types: tuple[str, ...] = ("IVPT", "IVRT", "both")

    def concentration_scope_status(self, record: Record) -> str:
        return _concentration_scope_status(record)

    def endpoint_scope_status(self, record: Record) -> str:
        amount_endpoint = _amount_endpoint(record)
        if amount_endpoint is not None:
            return "ok"
        endpoint = record.primary_endpoint()
        if endpoint is None or endpoint.mean is None:
            return "missing"
        if _is_out_of_scope_endpoint(endpoint.kind):
            return "out_of_scope"
        if endpoint.kind in {"permeated_fraction", "flux", "permeability_coefficient"}:
            return "ambiguous"
        return "ambiguous"

    def evaluate(self, record: Record) -> tuple[bool, str | None]:
        if (record.formulation.api_name or "").strip().lower() != self.api_name:
            return False, "api_not_ibuprofen"

        if self.required_device_term not in (record.device or "").strip().lower():
            return False, "franz_diffusion_cell_required"

        if (record.study_type or "uncertain") not in self.allowed_study_types:
            return False, "study_type_out_of_scope"

        endpoint_status = self.endpoint_scope_status(record)
        if endpoint_status != "ok":
            return False, "amount_endpoint_required"

        if record.conditions.duration_h is None:
            return False, "endpoint_time_required"

        concentration_status = self.concentration_scope_status(record)
        if concentration_status != "ok":
            return False, "ibuprofen_5pct_w_w_required"

        return True, None

    def annotate(self, record: Record) -> Record:
        passed, failure_reason = self.evaluate(record)
        record.verification_status = "verified" if passed else "rejected"
        record.failure_reason = failure_reason
        return record
