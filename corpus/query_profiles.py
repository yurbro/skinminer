"""Versioned Europe PMC query profiles for reproducible corpus construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


QUERY_PROFILE_REGISTRY_VERSION = "2026-03-28.v1"


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        trimmed = str(value or "").strip()
        if not trimmed or trimmed in seen:
            continue
        seen.add(trimmed)
        ordered.append(trimmed)
    return ordered


def _or_clause(tokens: Iterable[str]) -> str:
    items = _dedupe(tokens)
    return f"({' OR '.join(items)})" if items else ""


def build_epmc_query(
    drug_terms: Iterable[str],
    mechanism_terms: Iterable[str],
    target_terms: Iterable[str],
) -> str:
    """Build a Europe PMC boolean query from grouped token lists."""

    title_abstract_tokens: list[str] = []
    for term in _dedupe(drug_terms):
        quoted = term if term.startswith('"') and term.endswith('"') else f'"{term}"'
        title_abstract_tokens.extend([f"TITLE:{quoted}", f"ABSTRACT:{quoted}"])

    clauses = [
        _or_clause(title_abstract_tokens),
        _or_clause(mechanism_terms),
        _or_clause(target_terms),
    ]
    return " AND ".join(clause for clause in clauses if clause)


@dataclass(frozen=True)
class QueryProfile:
    """Named, versioned query asset used for corpus construction."""

    name: str
    version: str
    description: str
    query: str


QUERY_PROFILES: dict[str, QueryProfile] = {
    "ibuprofen_dermal_oa_v1": QueryProfile(
        name="ibuprofen_dermal_oa_v1",
        version="2026-03-28.v1",
        description="Broad OA-first ibuprofen dermal/transdermal/permeation query for baseline corpus building.",
        query=build_epmc_query(
            drug_terms=["ibuprofen"],
            mechanism_terms=["permeation", "permeat*", "diffusion", '"in vitro"', "release"],
            target_terms=["skin", "membrane", "topical", "transdermal", '"diffusion cell"'],
        ),
    ),
    "ibuprofen_dermal_franz_focus_v1": QueryProfile(
        name="ibuprofen_dermal_franz_focus_v1",
        version="2026-03-28.v1",
        description="Narrower Franz / IVPT / IVRT focused query for follow-up recall/precision studies.",
        query=build_epmc_query(
            drug_terms=["ibuprofen"],
            mechanism_terms=["permeation", "release", '"franz diffusion cell"', "IVPT", "IVRT"],
            target_terms=["skin", '"diffusion cell"', '"vertical diffusion"', "topical", "transdermal"],
        ),
    ),
}

DEFAULT_QUERY_PROFILE = "ibuprofen_dermal_oa_v1"
DEFAULT_QUERY = QUERY_PROFILES[DEFAULT_QUERY_PROFILE].query


def get_query_profile(name: str) -> QueryProfile:
    """Return a registered query profile by name."""

    try:
        return QUERY_PROFILES[name]
    except KeyError as exc:
        available = ", ".join(sorted(QUERY_PROFILES))
        raise ValueError(f"Unknown query profile: {name}. Available: {available}") from exc


def list_query_profiles() -> list[QueryProfile]:
    """List available query profiles in stable order."""

    return [QUERY_PROFILES[name] for name in sorted(QUERY_PROFILES)]
