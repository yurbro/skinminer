TRIAGE_PROMPT_ASSET_ID = "triage.abstract_relevance"
TRIAGE_PROMPT_VERSION = "2026-03-28.v1"

DEFAULT_TRIAGE_SYSTEM_PROMPT = (
    "You are a strict scientific literature triage assistant for an ibuprofen dermal formulation mining framework. "
    "Use ONLY the provided title and abstract. If the abstract does not support a claim, mark it uncertain. "
    "Prioritize whether the paper should advance to OA full-text processing for diffusion-cell IVPT/IVRT evidence."
)


def build_triage_user_prompt(title: str, abstract: str) -> str:
    return f"TITLE:\n{title}\n\nABSTRACT:\n{abstract}"
