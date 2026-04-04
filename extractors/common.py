"""Shared helpers for standardized extractor interfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from schemas.models import ContentAccess, ExtractorRunContext, RecordProvenance, RouteDecision


def artifact_path(run_context: ExtractorRunContext, *parts: str) -> Path:
    """Build an artifact path rooted at the extractor output directory."""

    base = Path(run_context.output_dir or ".")
    path = base.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def build_provenance(
    extractor_name: str,
    content_handle: ContentAccess,
    route_decision: RouteDecision,
    source_format: str | None = None,
    source_path: str | None = None,
    source_pages: list[int] | None = None,
    artifact_paths: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> RecordProvenance:
    """Construct standardized provenance metadata for a record."""

    resolved_source_format = source_format or content_handle.preferred_format
    resolved_source_path = source_path or content_handle.local_paths.get(resolved_source_format, "")
    if not resolved_source_path and content_handle.local_paths:
        resolved_source_path = next(iter(content_handle.local_paths.values()))
    if not resolved_source_path:
        resolved_source_path = content_handle.access_urls.get(resolved_source_format, "")
    return RecordProvenance(
        extractor_name=extractor_name,
        source_format=resolved_source_format,
        source_path=resolved_source_path,
        source_pages=list(source_pages or []),
        route_label=route_decision.route,
        route_notes=route_decision.notes,
        artifact_paths=list(artifact_paths or []),
        metadata=dict(metadata or {}),
    )


def require_pdf_path(content_handle: ContentAccess) -> str:
    """Return a local PDF path or raise when the legacy extractor cannot proceed."""

    pdf_path = content_handle.local_paths.get("pdf", "")
    if not pdf_path:
        raise FileNotFoundError(f"No local PDF is available for paper_id={content_handle.paper_id}")
    return pdf_path


def _clean_fragment(text: str) -> str:
    return " ".join((text or "").split()).strip().lower()


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def device_label_strength(label: str) -> int:
    """Return an ordinal strength for normalized device labels."""

    lowered = (label or "").strip().lower()
    if lowered == "franz diffusion cell":
        return 4
    if lowered in {"side-by-side diffusion cell", "flow-through diffusion cell"}:
        return 3
    if lowered == "diffusion cell":
        return 2
    return 0


def infer_device_label(*fragments: str) -> str:
    """Infer a normalized device label from extraction or routing fragments."""

    lowered = " ".join(_clean_fragment(fragment) for fragment in fragments if fragment).strip()
    if not lowered:
        return ""
    permeation_like = _contains_any(
        lowered,
        (
            "permeation",
            "permeated",
            "percutaneous",
            "transdermal",
            "skin flux",
            "cumulative amount",
            "release profile",
            "drug release",
            "diffusion area",
            "membrane",
            "stratum corneum",
            "receptor medium",
            "receiver medium",
        ),
    )
    obvious_non_device_context = _contains_any(
        lowered,
        (
            "risk ratio",
            "venous leg ulcer",
            "randomized",
            "clinical trial",
            "patients",
            "subjects",
            "healthy volunteers",
            "kidney",
            "enzyme activity",
            "kat i",
            "kat ii",
            "core body temperature",
            "exercise",
            "antibacterial",
            "minimum inhibitory concentration",
            "pampa",
            "skin pampa",
            "parallel artificial membrane permeability assay",
        ),
    )
    if "pampa" in lowered or "parallel artificial membrane permeability assay" in lowered:
        return ""
    if any(token in lowered for token in ("side-by-side diffusion", "side by side diffusion", "side-by-side cell", "side by side cell")):
        return "side-by-side diffusion cell"
    if any(token in lowered for token in ("flow-through diffusion", "flow through diffusion", "hanson diffusion", "enhancer cell")):
        return "flow-through diffusion cell"

    franz_signals = 0
    explicit_cell_cue = _contains_any(
        lowered,
        (
            "franz diffusion cell",
            "franz cell",
            "franz cells",
            "vertical diffusion cell",
            "vertical-type diffusion cell",
            "static diffusion cell",
            "diffusion cell",
            "permeation cell",
            "diffusion chamber",
        ),
    )
    if any(
        token in lowered
        for token in (
            "franz",
            "franz cell",
            "franz cells",
            "franz diffusion cell",
            "modified franz",
            "franz-type",
            "vertical diffusion",
            "vertical diffusion cell",
            "vertical-type diffusion",
            "static diffusion cell",
            "static vertical diffusion",
            "jacketed vertical diffusion",
            "static jacketed diffusion",
        )
    ):
        franz_signals += 3
    donor_like = any(token in lowered for token in ("donor compartment", "donor chamber", "donor cell", "donor phase", "donor solution"))
    receptor_like = any(
        token in lowered
        for token in (
            "receptor compartment",
            "receptor chamber",
            "receptor cell",
            "receiver compartment",
            "receiver chamber",
            "acceptor chamber",
            "acceptor compartment",
            "receptor solution",
            "receiver solution",
            "acceptor solution",
            "receptor phase",
            "receiver phase",
            "receptor fluid",
            "receiver fluid",
        )
    )
    if donor_like and receptor_like:
        franz_signals += 2
    if "donor" in lowered and any(token in lowered for token in ("receptor", "receiver", "acceptor")) and explicit_cell_cue:
        franz_signals += 2
    if any(token in lowered for token in ("membrane mounted between donor and receptor", "mounted between donor and receptor", "clamped between donor and receptor", "skin mounted between donor and receptor")):
        franz_signals += 2
    if any(
        token in lowered
        for token in (
            "diffusion area",
            "effective area",
            "sampling port",
            "sampling arm",
            "magnetic stirrer",
            "stirred receptor",
            "orifice",
            "jacketed receptor",
            "jacketed receiver",
            "clamped between donor and receptor",
            "membrane mounted",
            "skin mounted",
            "receiver medium",
            "receptor medium",
        )
    ):
        franz_signals += 1
    if franz_signals >= 3 and (explicit_cell_cue or donor_like or receptor_like):
        return "Franz diffusion cell"
    if explicit_cell_cue and (permeation_like or donor_like or receptor_like) and not obvious_non_device_context:
        return "diffusion cell"
    return ""


def infer_study_type_label(*fragments: str) -> str:
    """Infer a normalized study-type label from route and evidence fragments."""

    lowered = " ".join(_clean_fragment(fragment) for fragment in fragments if fragment).strip()
    if not lowered:
        return ""

    clinical_or_non_target = _contains_any(
        lowered,
        (
            "clinical trial",
            "randomized",
            "patients",
            "healthy volunteers",
            "venous leg ulcer",
            "core body temperature",
            "exercise-induced",
            "kat i",
            "kat ii",
            "enzyme activity",
            "in vivo",
            "analgesic effect",
            "pain relief",
            "risk ratio",
            "pampa",
            "skin pampa",
            "parallel artificial membrane permeability assay",
        ),
    )
    if clinical_or_non_target:
        return "uncertain"

    ivpt_like = _contains_any(
        lowered,
        (
            "ivpt",
            "in vitro permeation",
            "skin permeation",
            "percutaneous absorption",
            "transdermal permeation",
            "franz diffusion cell",
            "receiver compartment",
            "receptor compartment",
            "cumulative amount permeated",
            "flux",
        ),
    )
    ivrt_like = _contains_any(
        lowered,
        (
            "ivrt",
            "in vitro release",
            "drug release",
            "release profile",
            "cumulative release",
            "released drug",
            "dissolution profile",
            "release test",
        ),
    )
    if ivpt_like and ivrt_like:
        return "both"
    if ivpt_like:
        return "IVPT"
    if ivrt_like:
        return "IVRT"
    return ""


def find_device_support_fragment(target_label: str, *fragments: str) -> str:
    """Return the most informative fragment supporting a normalized device label."""

    target = (target_label or "").strip().lower()
    if not target:
        return ""

    scored: list[tuple[int, str]] = []
    for fragment in fragments:
        cleaned = " ".join((fragment or "").split()).strip()
        lowered = cleaned.lower()
        if not cleaned:
            continue
        score = 0
        if target == "franz diffusion cell":
            if _contains_any(lowered, ("franz", "vertical diffusion", "static diffusion", "vertical-type diffusion")):
                score += 4
            if "donor" in lowered and _contains_any(lowered, ("receptor", "receiver", "acceptor")):
                score += 2
            if _contains_any(
                lowered,
                (
                    "diffusion area",
                    "effective area",
                    "sampling port",
                    "jacketed receptor",
                    "jacketed receiver",
                    "receptor medium",
                    "receiver medium",
                    "orifice",
                    "clamped between donor and receptor",
                    "membrane mounted",
                    "skin mounted",
                ),
            ):
                score += 1
        elif target == "diffusion cell":
            if _contains_any(lowered, ("diffusion cell", "permeation cell", "diffusion chamber")):
                score += 3
        elif target == "side-by-side diffusion cell":
            if _contains_any(lowered, ("side-by-side", "side by side")):
                score += 4
        elif target == "flow-through diffusion cell":
            if _contains_any(lowered, ("flow-through", "flow through", "hanson diffusion", "enhancer cell")):
                score += 4
        if score > 0:
            scored.append((score, cleaned))

    if not scored:
        return ""
    scored.sort(key=lambda item: (-item[0], len(item[1])))
    return scored[0][1]


def has_local_pdf(content_handle: ContentAccess) -> bool:
    """Return whether a readable local PDF is available."""

    pdf_path = content_handle.local_paths.get("pdf", "")
    return bool(pdf_path and Path(pdf_path).exists())


def has_structured_source(content_handle: ContentAccess, formats: tuple[str, ...] = ("pmc_xml", "html")) -> bool:
    """Return whether a structured source is available locally or by URL."""

    for fmt in formats:
        local_path = content_handle.local_paths.get(fmt, "")
        if local_path and Path(local_path).exists():
            return True
        if content_handle.access_urls.get(fmt):
            return True
    return False
