"""Named cost-control run profiles for common pipeline modes."""

from __future__ import annotations

from dataclasses import dataclass


RUN_PROFILE_REGISTRY_VERSION = "2026-04-05.v1"
DEFAULT_RUN_PROFILE = "balanced_full"

STAGE_MODEL_KEYS = (
    "llm_triage",
    "routing",
    "text_extract",
    "table_extract",
    "figure_triage",
    "figure_map",
    "llm_adjudicate",
)


@dataclass(frozen=True)
class RunProfile:
    """Resolved defaults for a reproducible pipeline mode."""

    name: str
    description: str
    model: str
    stage_models: dict[str, str]
    with_llm_triage: bool
    enable_figure: bool
    download_content: bool
    auto_pdf_download: bool
    figure_gate_mode: str
    figure_min_route_confidence: float
    figure_require_explicit_signal: bool


RUN_PROFILES: dict[str, RunProfile] = {
    "balanced_full": RunProfile(
        name="balanced_full",
        description="Default full pipeline mode with LLM triage and figure branch enabled.",
        model="gpt-4o-mini",
        stage_models={},
        with_llm_triage=True,
        enable_figure=True,
        download_content=False,
        auto_pdf_download=True,
        figure_gate_mode="conservative",
        figure_min_route_confidence=0.55,
        figure_require_explicit_signal=True,
    ),
    "text_table_baseline": RunProfile(
        name="text_table_baseline",
        description="Lower-cost baseline focused on structured text/table extraction without figure processing.",
        model="gpt-4o-mini",
        stage_models={},
        with_llm_triage=True,
        enable_figure=False,
        download_content=False,
        auto_pdf_download=True,
        figure_gate_mode="off",
        figure_min_route_confidence=0.0,
        figure_require_explicit_signal=False,
    ),
    "budget_lean": RunProfile(
        name="budget_lean",
        description="Leanest mode that relies on structured OA text first and avoids figure work and automatic PDF downloads.",
        model="gpt-4o-mini",
        stage_models={},
        with_llm_triage=True,
        enable_figure=False,
        download_content=False,
        auto_pdf_download=False,
        figure_gate_mode="off",
        figure_min_route_confidence=0.0,
        figure_require_explicit_signal=False,
    ),
    "figure_deep": RunProfile(
        name="figure_deep",
        description="Heavier figure-oriented mode that keeps figure enabled and eagerly downloads primary OA content.",
        model="gpt-4o-mini",
        stage_models={},
        with_llm_triage=True,
        enable_figure=True,
        download_content=True,
        auto_pdf_download=True,
        figure_gate_mode="aggressive",
        figure_min_route_confidence=0.25,
        figure_require_explicit_signal=False,
    ),
}


def get_run_profile(name: str) -> RunProfile:
    """Return a named run profile."""

    try:
        return RUN_PROFILES[name]
    except KeyError as exc:
        available = ", ".join(sorted(RUN_PROFILES))
        raise ValueError(f"Unknown run profile: {name}. Available: {available}") from exc


def list_run_profiles() -> list[RunProfile]:
    """List run profiles in stable order."""

    return [RUN_PROFILES[name] for name in sorted(RUN_PROFILES)]
