from __future__ import annotations

from dataclasses import dataclass

from policies.v1_strict_ibuprofen_5pct import V1StrictIbuprofen5PctPolicy
from schemas.models import Record


@dataclass(slots=True)
class V3AnyIbuprofenConcentrationPolicy(V1StrictIbuprofen5PctPolicy):
    """V3 policy that keeps V1 scope gates but accepts any ibuprofen concentration."""

    name: str = "v3_any_ibuprofen_concentration"

    def concentration_scope_status(self, record: Record) -> str:
        api_name = (record.formulation.api_name or "").strip().lower()
        if api_name == self.api_name:
            return "ok"
        if not api_name:
            return "missing"
        return "out_of_scope"
