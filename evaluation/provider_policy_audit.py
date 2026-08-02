"""Read sanitized provider-policy aggregates without private audit text."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import PolicyScore


LEVEL_LABELS = {
    "v1": "strict",
    "v2": "extended",
    "v3": "any-concentration",
    "v4": "flux-augmented",
}
PROVIDER_LABELS = {"gpt": "openai", "claude": "anthropic"}


def _integer(row: dict[str, str], name: str) -> int:
    value = str(row.get(name, "")).strip()
    if not value:
        raise ValueError(f"provider aggregate is missing {name!r}")
    return int(value)


def _ratio(row: dict[str, str], name: str) -> float | None:
    value = str(row.get(name, "")).strip()
    return None if not value else float(value) / 100.0


def load_provider_policy_score(path: str | Path, *, provider: str, policy_level: str) -> PolicyScore:
    provider_key = provider.lower()
    provider_key = {"openai": "gpt", "anthropic": "claude"}.get(provider_key, provider_key)
    if provider_key not in PROVIDER_LABELS:
        raise ValueError("provider must be gpt or claude")
    if policy_level not in LEVEL_LABELS:
        raise ValueError("policy_level must be v1, v2, v3 or v4")
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        matches = [
            row
            for row in csv.DictReader(handle)
            if row.get("provider", "").strip().lower() == PROVIDER_LABELS[provider_key]
            and row.get("level", "").strip().lower() == LEVEL_LABELS[policy_level]
        ]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one aggregate row for {provider_key}/{policy_level}; found {len(matches)}"
        )
    row = matches[0]
    verified = _integer(row, "verified")
    return PolicyScore(
        provider=provider_key,
        policy_level=policy_level,
        verified=verified,
        unresolved=int(row["unresolved"]) if str(row.get("unresolved", "")).strip() else -1,
        rejected=int(row["rejected"]) if str(row.get("rejected", "")).strip() else -1,
        scope_tp=_integer(row, "scope_TP"),
        scope_fp=_integer(row, "scope_FP"),
        scope_precision=_ratio(row, "scope_precision"),
        scope_value_tp=_integer(row, "scope_value_TP"),
        end_to_end_precision=_ratio(row, "end_to_end_precision"),
        unresolved_keep_yes=None,
        rejected_keep_no=None,
    )
