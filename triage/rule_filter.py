from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

from utils.io import write_jsonl, write_optional_csv

DEFAULT_PASS_PATTERNS = [
    r"\bin vitro\b",
    r"\bpermeat",
    r"\bdiffus",
    r"\brelease\b",
    r"\btransdermal\b",
    r"\btopical\b",
    r"\bskin\b",
    r"\bmembrane\b",
    r"\bfranz\b",
    r"\bdiffusion cell\b",
]

DEFAULT_EXCLUDE_PATTERNS = [
    r"\boral\b",
    r"\btablet\b",
    r"\bcapsule\b",
    r"\bplasma\b",
    r"\bpharmacokinet",
    r"\bin vivo\b",
]


def _has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _matched_patterns(text: str, patterns: Iterable[str]) -> list[str]:
    matched: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            matched.append(pattern)
    return matched


def apply_rule_filter(
    records: Iterable[Mapping[str, Any]],
    output_pass_jsonl: str | None = None,
    output_fail_jsonl: str | None = None,
    output_pass_csv: str | None = None,
    output_fail_csv: str | None = None,
    pass_patterns: Iterable[str] = DEFAULT_PASS_PATTERNS,
    exclude_patterns: Iterable[str] = DEFAULT_EXCLUDE_PATTERNS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    passed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for row in records:
        record = dict(row)
        text = f"{record.get('title', '')} {record.get('abstract', '')}".strip()
        matched_pass = _matched_patterns(text, pass_patterns)
        matched_exclude = _matched_patterns(text, exclude_patterns)
        has_ibuprofen = bool(re.search(r"\bibuprofen\b", text, flags=re.IGNORECASE))
        is_relevant = has_ibuprofen and bool(matched_pass) and not bool(matched_exclude)

        record["rule_relevance_label"] = "relevant" if is_relevant else "not_relevant"
        record["rule_confidence"] = 0.8 if is_relevant else 0.2
        record["rule_hints"] = matched_pass[:5]
        record["rule_exclusions"] = matched_exclude[:5]

        if is_relevant:
            passed.append(record)
        else:
            failed.append(record)

    if output_pass_jsonl:
        write_jsonl(passed, output_pass_jsonl)
    if output_fail_jsonl:
        write_jsonl(failed, output_fail_jsonl)
    write_optional_csv(passed, output_pass_csv)
    write_optional_csv(failed, output_fail_csv)
    return passed, failed
