"""Round-2 CSV loader and cumulative-policy scorer.

The acceptance level in ``policy_level`` is the *first* level at which a row
became verified. Therefore a requested level is cumulative: v2 includes rows
whose first level is v1 or v2; v3 includes v1, v2 and v3; and so on.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Iterable

from .models import POLICY_LEVELS, PolicyScore, Round2GoldCsvRow


POLICY_RANK = {level: index for index, level in enumerate(POLICY_LEVELS, start=1)}
POLICY_RANK["never"] = 99
VALUE_CORRECT = {"yes", "near", "approximate"}


def cumulative_levels(policy_level: str) -> tuple[str, ...]:
    level = policy_level.lower()
    if level not in POLICY_RANK or level == "never":
        raise ValueError(f"policy level must be one of {POLICY_LEVELS}; got {policy_level!r}")
    return POLICY_LEVELS[: POLICY_RANK[level]]


def load_round2_gold_csv(path: str | Path) -> list[Round2GoldCsvRow]:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [Round2GoldCsvRow.from_mapping(row) for row in csv.DictReader(handle)]
    if not rows:
        raise ValueError(f"Round-2 gold CSV is empty: {source}")
    ids = [row.sample_id for row in rows]
    duplicates = sorted({sample_id for sample_id in ids if ids.count(sample_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate sample_id values: {duplicates}")
    return rows


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def score_round2_gold(
    rows: Iterable[Round2GoldCsvRow],
    *,
    provider: str,
    policy_level: str,
) -> PolicyScore:
    """Score the GPT source population at a cumulative acceptance level.

    Claude membership is not recoverable from the 23 Claude-only rows in the
    main CSV. To prevent a plausible but wrong curve, callers must load the
    provider-specific aggregate through ``provider_policy_audit`` instead.
    """

    provider_name = provider.lower()
    provider_name = {"openai": "gpt", "anthropic": "claude"}.get(provider_name, provider_name)
    if provider_name != "gpt":
        raise ValueError(
            "Claude policy scores cannot be inferred from the main Round-2 CSV; "
            "supply the provider-specific aggregate metrics CSV"
        )
    requested_rank = POLICY_RANK.get(policy_level.lower())
    if requested_rank is None or policy_level.lower() == "never":
        raise ValueError(f"unsupported policy level: {policy_level!r}")
    population = [row for row in rows if row.source_baseline == provider_name]
    verified = [row for row in population if POLICY_RANK[row.policy_level] <= requested_rank]
    rejected = [
        row
        for row in population
        if POLICY_RANK[row.policy_level] > requested_rank and row.pipeline_status_v4 == "rejected"
    ]
    verified_ids = {row.sample_id for row in verified}
    rejected_ids = {row.sample_id for row in rejected}
    unresolved = [
        row for row in population if row.sample_id not in verified_ids and row.sample_id not in rejected_ids
    ]
    scope_tp_rows = [row for row in verified if row.gold_scope_correct == "yes"]
    scope_fp = len(verified) - len(scope_tp_rows)
    scope_value_tp = sum(row.gold_value_correct in VALUE_CORRECT for row in scope_tp_rows)
    precision = len(scope_tp_rows) / len(verified) if verified else None
    end_to_end = scope_value_tp / len(verified) if verified else None
    return PolicyScore(
        provider=provider_name,
        policy_level=policy_level.lower(),
        verified=len(verified),
        unresolved=len(unresolved),
        rejected=len(rejected),
        scope_tp=len(scope_tp_rows),
        scope_fp=scope_fp,
        scope_precision=precision,
        scope_value_tp=scope_value_tp,
        end_to_end_precision=end_to_end,
        unresolved_keep_yes=sum(row.gold_keep_record == "yes" for row in unresolved),
        rejected_keep_no=sum(row.gold_keep_record == "no" for row in rejected),
    )
