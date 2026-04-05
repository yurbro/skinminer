"""Round 2 research-grade pipeline entrypoint for SkinMiner."""

from __future__ import annotations

import argparse
import json
import logging
from collections import Counter, defaultdict
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from access.content_strategy import build_default_content_strategy
from access.resolve_content import resolve_content_batch
from assembly.assemble_records import assemble_records
from configs.run_profiles import DEFAULT_RUN_PROFILE, RUN_PROFILE_REGISTRY_VERSION, STAGE_MODEL_KEYS, get_run_profile, list_run_profiles
from corpus.build_epmc import build_corpus
from corpus.query_profiles import DEFAULT_QUERY_PROFILE, QUERY_PROFILE_REGISTRY_VERSION, get_query_profile, list_query_profiles
from detection.router import ROUTER_PROMPT_ASSET_ID, ROUTER_PROMPT_VERSION, route_papers
from extractors.common import has_local_pdf, has_structured_source
from extractors.figure.build_records import extract_batch as extract_figure_batch
from extractors.figure.map_curves import FIGURE_MAPPING_PROMPT_ASSET_ID, FIGURE_MAPPING_PROMPT_VERSION
from extractors.figure.triage import FIGURE_TRIAGE_PROMPT_ASSET_ID, FIGURE_TRIAGE_PROMPT_VERSION
from extractors.table.extractor import TABLE_EXTRACTION_PROMPT_ASSET_ID, TABLE_EXTRACTION_PROMPT_VERSION, extract_batch as extract_table_batch
from extractors.text.extract_fields import TEXT_EXTRACTION_PROMPT_ASSET_ID, TEXT_EXTRACTION_PROMPT_VERSION
from extractors.text.extractor import extract_batch as extract_text_batch
from patchers.patch_api_concentration import patch_api_concentration
from patchers.patch_endpoint import patch_endpoint_value
from patchers.patch_area import patch_area
from patchers.patch_endpoint_time import patch_endpoint_time
from policies.v1_strict_ibuprofen_5pct import V1StrictIbuprofen5PctPolicy
from reports.build_run_report import build_run_report
from schemas.models import ContentAccess, ExtractorRunContext, RouteDecision
from triage.llm_triage import triage_records_with_llm
from triage.prompts import TRIAGE_PROMPT_ASSET_ID, TRIAGE_PROMPT_VERSION
from triage.rule_filter import apply_rule_filter
from utils.io import load_jsonl, load_records_jsonl, make_paper_id, write_jsonl, write_optional_csv
from utils.long_run import LongRunMonitor, merge_progress_callbacks
from utils.manifest import create_run_manifest, write_manifest
from utils.resume import (
    build_file_fingerprints,
    build_resume_signature,
    clear_stage_marker,
    load_stage_marker,
    load_typed_jsonl_if_exists,
    mark_stage_done,
    stage_is_done,
    stage_marker_matches_signature,
    validate_existing_stage_markers,
)
from utils.status_panel import PipelineStatusPanel
from verification.llm_adjudicate import adjudicate_records, select_adjudication_candidates
from verification.verify_records import verify_records

LOGGER = logging.getLogger("skinminer.pipeline")
PROMPT_PATHS = [
    "triage/prompts.py",
    "extractors/text/extract_fields.py",
    "extractors/table/extractor.py",
    "extractors/figure/triage.py",
    "extractors/figure/map_curves.py",
]
CONFIG_PATHS = [
    "policies/v1_strict_ibuprofen_5pct.py",
    "corpus/query_profiles.py",
    "configs/run_profiles.py",
]
PROMPT_ASSETS = {
    TRIAGE_PROMPT_ASSET_ID: TRIAGE_PROMPT_VERSION,
    ROUTER_PROMPT_ASSET_ID: ROUTER_PROMPT_VERSION,
    TEXT_EXTRACTION_PROMPT_ASSET_ID: TEXT_EXTRACTION_PROMPT_VERSION,
    TABLE_EXTRACTION_PROMPT_ASSET_ID: TABLE_EXTRACTION_PROMPT_VERSION,
    FIGURE_TRIAGE_PROMPT_ASSET_ID: FIGURE_TRIAGE_PROMPT_VERSION,
    FIGURE_MAPPING_PROMPT_ASSET_ID: FIGURE_MAPPING_PROMPT_VERSION,
}


def _load_input_corpus(path: Path) -> list[dict]:
    if path.suffix.lower() == ".jsonl":
        return pd.read_json(path, lines=True).to_dict("records")
    return pd.read_csv(path).to_dict("records")


def _find_existing_pdf(doi: str, pdf_dir: Path) -> str:
    if not doi or not pdf_dir.exists():
        return ""
    stem = doi.lower().replace("/", "_").replace(":", "_").replace(".", "_")
    matches = sorted(pdf_dir.glob(f"{stem}__*.pdf"))
    return str(matches[0]) if matches else ""


def _build_content_handles(triaged_rows: list[dict], access_items: list[ContentAccess]) -> dict[str, ContentAccess]:
    access_by_paper = {item.paper_id: item for item in access_items}
    access_by_doi = {item.doi: item for item in access_items if item.doi}
    handles: dict[str, ContentAccess] = {}

    for row in triaged_rows:
        doi = str(row.get("doi", "") or "").strip().lower()
        title = str(row.get("title", "") or "")
        existing_paper_id = str(row.get("paper_id", "") or "")
        access_item = access_by_paper.get(existing_paper_id) or access_by_doi.get(doi)
        paper_id = existing_paper_id or (access_item.paper_id if access_item else make_paper_id(doi=doi, title=title))
        local_paths = dict(access_item.local_paths) if access_item else {}
        if "pdf" not in local_paths:
            existing_pdf = _find_existing_pdf(doi, Path("papers/pdf"))
            if existing_pdf:
                local_paths["pdf"] = existing_pdf

        handles[paper_id] = ContentAccess(
            paper_id=paper_id,
            doi=doi,
            title=title,
            pmid=access_item.pmid if access_item else "",
            pmcid=access_item.pmcid if access_item else "",
            preferred_format=access_item.preferred_format if access_item else ("pdf" if local_paths else "unresolved"),
            available_formats=access_item.available_formats if access_item else (["pdf"] if local_paths else []),
            access_urls=access_item.access_urls if access_item else {},
            local_paths=local_paths,
            status=access_item.status if access_item else ("downloaded" if local_paths else "unresolved"),
            notes=list(access_item.notes) if access_item else [],
        )
    return handles


def _build_route_inputs(triaged_rows: list[dict], content_handles: dict[str, ContentAccess]) -> list[dict]:
    routed_inputs: list[dict] = []
    for row in triaged_rows:
        doi = str(row.get("doi", "") or "").strip().lower()
        title = str(row.get("title", "") or "")
        paper_id = str(row.get("paper_id", "") or "")
        if not paper_id:
            for handle in content_handles.values():
                if handle.doi == doi:
                    paper_id = handle.paper_id
                    break
        if not paper_id:
            paper_id = make_paper_id(doi=doi, title=title)
        handle = content_handles.get(paper_id)
        routed_inputs.append(
            {
                **row,
                "paper_id": paper_id,
                "preferred_format": handle.preferred_format if handle else "unresolved",
                "available_formats": handle.available_formats if handle else [],
                "access_urls": dict(handle.access_urls) if handle else {},
                "local_paths": dict(handle.local_paths) if handle else {},
                "access_status": handle.status if handle else "unresolved",
                "pdf_path": handle.local_paths.get("pdf", "") if handle else "",
                "title": title,
            }
        )
    return routed_inputs


def _pairs_from_route_decisions(
    route_decisions: list[RouteDecision],
    content_handles: dict[str, ContentAccess],
    *,
    routes: set[str],
    source_check: Callable[[ContentAccess], bool] | None = None,
) -> list[tuple[ContentAccess, RouteDecision]]:
    pairs: list[tuple[ContentAccess, RouteDecision]] = []
    for decision in route_decisions:
        if decision.route not in routes:
            continue
        handle = content_handles.get(decision.paper_id)
        if not handle:
            continue
        if source_check and not source_check(handle):
            continue
        pairs.append((handle, decision))
    return pairs


def _has_explicit_figure_signal(route_decision: RouteDecision) -> bool:
    if route_decision.endpoint_carrier == "figure":
        return True
    if any(item.modality == "figure" for item in route_decision.anchor_evidence):
        return True
    haystack = " ".join(
        str(value or "")
        for value in (
            route_decision.notes,
            route_decision.raw_labels.get("endpoint_carrier_snippet", ""),
            route_decision.raw_labels.get("where_endpoint", ""),
            route_decision.raw_labels.get("notes", ""),
        )
    ).lower()
    return any(token in haystack for token in ("figure", "fig.", "curve", "plot", "graph", "subplot"))


def _apply_figure_gating(
    pairs: list[tuple[ContentAccess, RouteDecision]],
    *,
    gate_mode: str,
    min_route_confidence: float,
    require_explicit_signal: bool,
) -> tuple[list[tuple[ContentAccess, RouteDecision]], Counter[str]]:
    if gate_mode in {"off", "none"}:
        return pairs, Counter()

    filtered: list[tuple[ContentAccess, RouteDecision]] = []
    skipped: Counter[str] = Counter()
    for content_handle, route_decision in pairs:
        confidence = float(route_decision.route_confidence or 0.0)
        if confidence < min_route_confidence:
            skipped["low_route_confidence"] += 1
            continue
        if require_explicit_signal and not _has_explicit_figure_signal(route_decision):
            skipped["missing_explicit_figure_signal"] += 1
            continue
        filtered.append((content_handle, route_decision))
    return filtered, skipped


def _group_records_by_paper(records: list) -> dict[str, list]:
    grouped: dict[str, list] = defaultdict(list)
    for record in records:
        grouped[record.paper_id].append(record)
    return dict(grouped)


def _resolve_corpus_mode(input_csv: Path, explicit_build_corpus: bool) -> tuple[bool, bool]:
    """Return (effective_build_corpus, fallback_build_corpus)."""

    if explicit_build_corpus:
        return True, False
    if not input_csv.exists():
        return True, True
    return False, False


def _format_stage_model_overrides(default_model: str, stage_models: dict[str, str]) -> str:
    overrides = [f"{key}={value}" for key, value in sorted(stage_models.items()) if value and value != default_model]
    return ", ".join(overrides) if overrides else "none"


def _resolve_stage_models(args: argparse.Namespace, run_profile) -> dict[str, str]:
    stage_models = {key: args.model for key in STAGE_MODEL_KEYS}
    stage_models.update(run_profile.stage_models or {})
    cli_overrides = {
        "llm_triage": args.llm_triage_model,
        "routing": args.routing_model,
        "text_extract": args.text_model,
        "table_extract": args.table_model,
        "figure_triage": args.figure_triage_model,
        "figure_map": args.figure_map_model,
        "llm_adjudicate": args.llm_adjudication_model,
    }
    for key, value in cli_overrides.items():
        if value:
            stage_models[key] = value
    return stage_models


def _suggest_fresh_output_dir(output_dir: Path) -> Path:
    """Suggest a sibling output directory when resume markers are incompatible."""

    if not output_dir.exists():
        return output_dir
    parent = output_dir.parent
    stem = output_dir.name
    candidates = [parent / f"{stem}_fresh", parent / f"{stem}_rerun"]
    for candidate in candidates:
        if not candidate.exists():
            return candidate
    suffix = 2
    while True:
        candidate = parent / f"{stem}_rerun_{suffix:02d}"
        if not candidate.exists():
            return candidate
        suffix += 1


def _count_access_statuses(access_items: list[ContentAccess]) -> Counter:
    return Counter(item.status for item in access_items)


def _count_routes(route_decisions: list[RouteDecision]) -> Counter:
    return Counter(decision.route for decision in route_decisions)


def _count_verification_statuses(records: list) -> Counter:
    return Counter(record.verification_status for record in records)


def _count_patch_applications(records: list, patcher_name: str) -> int:
    return sum(
        1
        for record in records
        for patch in record.patches
        if patch.patcher_name == patcher_name and patch.status == "applied"
    )


def _count_records_with_status(records: list, status: str) -> int:
    return sum(1 for record in records if getattr(record, "verification_status", "") == status)


def _load_corpus_jsonl(path: Path) -> list[dict]:
    return load_jsonl(path)


def _jsonl_row_count(path: Path) -> int | None:
    if not path.exists():
        return None
    return len(load_jsonl(path))


def _load_existing_manifest_row(output_dir: Path) -> dict | None:
    manifest_path = output_dir / "run_manifest.jsonl"
    if not manifest_path.exists():
        return None
    rows = load_jsonl(manifest_path)
    if not rows:
        return None
    return rows[-1]


def _manifest_requested_llm_adjudication(manifest_row: dict) -> bool:
    notes = manifest_row.get("notes", []) or []
    return any("Optional audit-only LLM adjudication enabled" in str(note) for note in notes)


def _manifest_soft_resume_compatible(
    manifest_row: dict,
    *,
    model_name: str,
    stage_models: dict[str, str],
    policy_name: str,
    run_profile_name: str,
    query_profile_name: str,
    query_profile_version: str,
    query_source: str,
    corpus_query: str,
    with_llm_adjudication: bool,
) -> bool:
    stage_metrics = manifest_row.get("stage_metrics", {}) or {}
    manifest_stage_models = dict(stage_metrics.get("stage_models", {}) or {})
    if not manifest_stage_models:
        manifest_stage_models = {key: manifest_row.get("model_name", "") for key in STAGE_MODEL_KEYS}
    checks = [
        manifest_row.get("model_name", "") == model_name,
        manifest_stage_models == stage_models,
        manifest_row.get("policy_name", "") == policy_name,
        stage_metrics.get("run_profile", "") == run_profile_name,
        stage_metrics.get("query_profile", "") == query_profile_name,
        stage_metrics.get("query_profile_version", "") == query_profile_version,
        stage_metrics.get("query_source", "") == query_source,
        stage_metrics.get("corpus_query", "") == corpus_query,
        _manifest_requested_llm_adjudication(manifest_row) == with_llm_adjudication,
    ]
    return all(checks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Round 2 research-grade SkinMiner pipeline.")
    parser.add_argument("--input-csv", type=Path, default=Path("data/corpus_ibuprofen.csv"))
    parser.add_argument("--build-corpus", action="store_true")
    parser.add_argument("--query", type=str, default=None)
    parser.add_argument("--query-profile", type=str, default=DEFAULT_QUERY_PROFILE)
    parser.add_argument("--list-query-profiles", action="store_true")
    parser.add_argument("--run-profile", type=str, default=DEFAULT_RUN_PROFILE)
    parser.add_argument("--list-run-profiles", action="store_true")
    parser.add_argument("--max-results", type=int, default=50000)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/round2_run"))
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--llm-triage-model", type=str, default=None)
    parser.add_argument("--routing-model", type=str, default=None)
    parser.add_argument("--text-model", type=str, default=None)
    parser.add_argument("--table-model", type=str, default=None)
    parser.add_argument("--figure-triage-model", type=str, default=None)
    parser.add_argument("--figure-map-model", type=str, default=None)
    parser.add_argument("--with-llm-triage", dest="with_llm_triage", action="store_true")
    parser.add_argument("--no-llm-triage", dest="with_llm_triage", action="store_false")
    parser.add_argument("--download-content", dest="download_content", action="store_true")
    parser.add_argument("--no-download-content", dest="download_content", action="store_false")
    parser.add_argument("--auto-pdf-download", dest="auto_pdf_download", action="store_true")
    parser.add_argument("--no-auto-pdf-download", dest="auto_pdf_download", action="store_false")
    parser.add_argument("--enable-figure", dest="enable_figure", action="store_true")
    parser.add_argument("--disable-figure", dest="enable_figure", action="store_false")
    parser.add_argument("--export-csv", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--access-checkpoint-every", type=int, default=25)
    parser.add_argument("--long-run-mode", action="store_true")
    parser.add_argument("--long-run-log-every", type=int, default=25)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--with-llm-adjudication", action="store_true")
    parser.add_argument("--llm-adjudication-model", type=str, default=None)
    parser.add_argument("--llm-adjudication-limit", type=int, default=None)
    parser.add_argument("--status-panel", dest="status_panel", action="store_true")
    parser.add_argument("--no-status-panel", dest="status_panel", action="store_false")
    parser.set_defaults(
        status_panel=True,
        auto_pdf_download=None,
        with_llm_triage=None,
        enable_figure=None,
        download_content=None,
    )
    args = parser.parse_args()

    if args.list_query_profiles:
        for profile in list_query_profiles():
            print(f"{profile.name}\t{profile.version}\t{profile.description}")
        return
    if args.list_run_profiles:
        for profile in list_run_profiles():
            profile_stage_models = {key: profile.stage_models.get(key, profile.model) for key in STAGE_MODEL_KEYS}
            print(
                f"{profile.name}\t{profile.model}\tllm_triage={profile.with_llm_triage}\t"
                f"figure={profile.enable_figure}\tdownload={profile.download_content}\t"
                f"auto_pdf={profile.auto_pdf_download}\tfigure_gate={profile.figure_gate_mode}\t"
                f"figure_min_conf={profile.figure_min_route_confidence:.2f}\t"
                f"stage_overrides={_format_stage_model_overrides(profile.model, profile_stage_models)}\t"
                f"{profile.description}"
            )
        return

    logging.basicConfig(
        level=logging.WARNING if args.status_panel else logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )
    run_profile = get_run_profile(args.run_profile)
    if args.model is None:
        args.model = run_profile.model
    if args.with_llm_triage is None:
        args.with_llm_triage = run_profile.with_llm_triage
    if args.enable_figure is None:
        args.enable_figure = run_profile.enable_figure
    if args.download_content is None:
        args.download_content = run_profile.download_content
    if args.auto_pdf_download is None:
        args.auto_pdf_download = run_profile.auto_pdf_download
    stage_models = _resolve_stage_models(args, run_profile)
    args.llm_adjudication_model = stage_models["llm_adjudicate"]
    query_profile = get_query_profile(args.query_profile)
    effective_query = args.query or query_profile.query
    query_source_label = f"custom_override:{query_profile.name}" if args.query else f"profile:{query_profile.name}"
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    policy = V1StrictIbuprofen5PctPolicy()
    content_strategy = build_default_content_strategy(
        eager_download_primary=args.download_content,
        auto_download_pdf_for_legacy=args.auto_pdf_download,
    )
    effective_build_corpus, fallback_build_corpus = _resolve_corpus_mode(args.input_csv, args.build_corpus)
    corpus_csv_output: Path | None = None
    if fallback_build_corpus:
        corpus_csv_output = args.input_csv
    elif args.export_csv:
        corpus_csv_output = output_dir / "corpus.csv"
    if effective_build_corpus and fallback_build_corpus:
        corpus_source_label = f"fallback_build:EuropePMC -> {args.input_csv}"
    elif effective_build_corpus:
        corpus_source_label = "explicit_build:EuropePMC"
    else:
        corpus_source_label = f"input_csv:{args.input_csv}"
    manifest_notes = [
        "Round 2 extractor standardization, verification, patching, and reporting pipeline.",
        "OA-only; legacy extraction logic preserved inside modular wrappers.",
        *content_strategy.notes,
    ]
    if args.resume:
        manifest_notes.append("Resume mode enabled: completed stages may be skipped and iterative stages may continue from JSONL checkpoints.")
        manifest_notes.append("Resume now enforces run-signature consistency for the same output directory.")
    manifest_input_paths = [str(args.input_csv)] if not effective_build_corpus else []
    if fallback_build_corpus:
        manifest_notes.append(f"Input corpus missing at {args.input_csv}; fell back to Europe PMC corpus build.")
        LOGGER.warning("Input corpus missing at %s; falling back to Europe PMC corpus build.", args.input_csv)
    long_run_dir = output_dir / "long_run"
    if args.long_run_mode:
        manifest_notes.append("Long-run mode enabled: stage events, state snapshots, error capture, cumulative LLM usage logging, and LLM retry/malformed-output statistics.")
    manifest_notes.append(
        f"Corpus query profile: {query_profile.name} ({query_profile.version}); query source={query_source_label}."
    )
    manifest_notes.append(f"Run profile: {run_profile.name}. {run_profile.description}")
    if args.with_llm_adjudication:
        manifest_notes.append(
            "Optional audit-only LLM adjudication enabled after final rule verification; "
            "this now prioritizes recoverable unresolved records for rescue-oriented second opinions "
            "and does not override verified_records."
        )
    manifest_notes.append(
        "Figure gating: "
        f"mode={run_profile.figure_gate_mode}, min_route_confidence={run_profile.figure_min_route_confidence:.2f}, "
        f"require_explicit_signal={'yes' if run_profile.figure_require_explicit_signal else 'no'}."
    )
    manifest_notes.append(
        "Stage-level model configuration: "
        f"default={args.model}; overrides={_format_stage_model_overrides(args.model, stage_models)}."
    )
    resume_signature = build_resume_signature(
        {
            "pipeline_version": "round2_resume_v4",
            "effective_build_corpus": effective_build_corpus,
            "fallback_build_corpus": fallback_build_corpus,
            "input_csv": build_file_fingerprints([args.input_csv]),
            "run_profile": run_profile.name,
            "run_profile_registry_version": RUN_PROFILE_REGISTRY_VERSION,
            "figure_gate_mode": run_profile.figure_gate_mode,
            "figure_min_route_confidence": run_profile.figure_min_route_confidence,
            "figure_require_explicit_signal": run_profile.figure_require_explicit_signal,
            "query_profile": query_profile.name,
            "query_profile_version": query_profile.version,
            "query_source": query_source_label,
            "query": effective_query,
            "max_results": args.max_results,
            "limit": args.limit,
            "model": args.model,
            "stage_models": stage_models,
            "policy_name": policy.name,
            "with_llm_triage": args.with_llm_triage,
            "download_content": args.download_content,
            "with_llm_adjudication": args.with_llm_adjudication,
            "llm_adjudication_limit": args.llm_adjudication_limit,
            "auto_pdf_download": args.auto_pdf_download,
            "enable_figure": args.enable_figure,
            "prompt_files": build_file_fingerprints(PROMPT_PATHS),
            "config_files": build_file_fingerprints(CONFIG_PATHS),
        }
    )
    if args.resume:
        existing_manifest_row = _load_existing_manifest_row(output_dir)
        manifest_resume_digest = ""
        if existing_manifest_row:
            manifest_stage_metrics = existing_manifest_row.get("stage_metrics", {}) or {}
            manifest_resume_digest = str(manifest_stage_metrics.get("resume_signature_digest", "") or "")
        incompatible_stages = validate_existing_stage_markers(output_dir, resume_signature)
        if (
            incompatible_stages
            and existing_manifest_row
            and manifest_resume_digest
            and _manifest_soft_resume_compatible(
                existing_manifest_row,
                model_name=args.model,
                stage_models=stage_models,
                policy_name=policy.name,
                run_profile_name=run_profile.name,
                query_profile_name=query_profile.name,
                query_profile_version=query_profile.version,
                query_source=query_source_label,
                corpus_query=effective_query,
                with_llm_adjudication=args.with_llm_adjudication,
            )
        ):
            LOGGER.warning(
                "Resume markers use an older digest for the same run configuration; "
                "reusing existing resume signature %s for compatibility.",
                manifest_resume_digest,
            )
            resume_signature["digest"] = manifest_resume_digest
            incompatible_stages = validate_existing_stage_markers(output_dir, resume_signature)
        if incompatible_stages:
            incompatible_list = ", ".join(incompatible_stages)
            suggested_output_dir = _suggest_fresh_output_dir(output_dir)
            raise RuntimeError(
                "Resume markers are incompatible with the current run configuration. "
                f"Stages: {incompatible_list}. Reuse the same configuration, delete {output_dir / '.resume'}, "
                f"or start from a new output directory such as '{suggested_output_dir}'."
            )
    manifest = create_run_manifest(
        model_name=args.model,
        policy_name=policy.name,
        input_paths=manifest_input_paths,
        prompt_paths=PROMPT_PATHS,
        config_paths=CONFIG_PATHS,
        notes=manifest_notes,
    )
    if args.long_run_mode:
        manifest.stage_outputs.update(
            {
                "long_run_events": str(long_run_dir / "events.jsonl"),
                "long_run_state": str(long_run_dir / "state.json"),
                "long_run_summary": str(long_run_dir / "summary.json"),
            }
        )
        manifest.stage_metrics.update(
            {
                "long_run_enabled": True,
                "long_run_progress_log_every": args.long_run_log_every,
            }
        )
    if args.resume:
        manifest.stage_metrics["resume_enabled"] = True
    manifest.stage_metrics.update(
        {
            "resume_signature_digest": resume_signature["digest"],
            "query_profile": query_profile.name,
            "query_profile_version": query_profile.version,
            "query_profile_registry_version": QUERY_PROFILE_REGISTRY_VERSION,
            "run_profile": run_profile.name,
            "run_profile_registry_version": RUN_PROFILE_REGISTRY_VERSION,
            "figure_gate_mode": run_profile.figure_gate_mode,
            "figure_min_route_confidence": run_profile.figure_min_route_confidence,
            "figure_require_explicit_signal": run_profile.figure_require_explicit_signal,
            "query_source": query_source_label,
            "query_override": bool(args.query),
            "corpus_query": effective_query,
            "prompt_assets": PROMPT_ASSETS,
            "stage_models": stage_models,
        }
    )
    manifest.module_notes.update({f"prompt_asset:{asset_id}": version for asset_id, version in sorted(PROMPT_ASSETS.items())})
    stage_labels = {
        "corpus": "Corpus",
        "rule_filter": "Rule Triage",
        "llm_triage": "LLM Triage",
        "access": "Content Access",
        "routing": "Evidence Routing",
        "table_extract": "Table Extract",
        "text_extract": "Text Extract",
        "figure_extract": "Figure Extract",
        "assembly": "Assembly",
        "verify_initial": "Verify Initial",
        "patch_api": "Patch API Conc",
        "patch_endpoint": "Patch Endpoint",
        "patch_time": "Patch End Time",
        "patch_area": "Patch Area",
        "verify_final": "Verify Final",
        "llm_adjudicate": "LLM Adjudicate",
        "report": "Run Report",
    }
    write_manifest(manifest, output_dir / "run_manifest.jsonl")

    with LongRunMonitor(
        enabled=args.long_run_mode,
        run_id=manifest.run_id,
        output_dir=output_dir,
        progress_log_every=args.long_run_log_every,
    ) as long_run_monitor, PipelineStatusPanel(
        enabled=args.status_panel,
        header_lines=[
            f"Run ID: {manifest.run_id}",
            f"Corpus Source: {corpus_source_label}",
            f"Corpus Query: {query_source_label} @ {query_profile.version}",
            f"Run Profile: {run_profile.name}",
            f"Content Strategy: {content_strategy.summary}",
            f"Long Run: {long_run_monitor.summary_label if args.long_run_mode else 'off'}",
            f"Resume: {'on' if args.resume else 'off'}",
            f"Model: {args.model} | Stage Overrides: {_format_stage_model_overrides(args.model, stage_models)} | Policy: {policy.name} | Output: {output_dir}",
        ],
    ) as status_panel:
        for key, label in stage_labels.items():
            status_panel.register_stage(key, label)
            long_run_monitor.register_stage(key, label)

        def start_stage(key: str, *, total: int | None = None, detail: str = "") -> None:
            clear_stage_marker(output_dir, key)
            status_panel.start_stage(key, total=total, detail=detail)
            long_run_monitor.stage_started(key, stage_labels[key], total=total, detail=detail)

        def finish_stage(
            key: str,
            *,
            completed: int | None = None,
            total: int | None = None,
            detail: str = "",
            input_count: int | None = None,
            output_count: int | None = None,
            output_paths: list[Path] | None = None,
        ) -> None:
            status_panel.finish_stage(key, completed=completed, total=total, detail=detail)
            long_run_monitor.stage_finished(key, completed=completed, total=total, detail=detail)
            mark_stage_done(
                output_dir,
                key,
                {
                    "stage": key,
                    "completed": completed,
                    "total": total,
                    "detail": detail,
                    "input_count": input_count,
                    "output_count": output_count,
                    "output_paths": [str(path) for path in output_paths or []],
                    "resume_signature_digest": resume_signature["digest"],
                },
            )

        def skip_stage(key: str, detail: str = "") -> None:
            status_panel.skip_stage(key, detail)
            long_run_monitor.stage_skipped(key, detail=detail)

        def fail_stage(key: str, exc: Exception) -> None:
            detail = f"{type(exc).__name__}: {exc}"
            status_panel.fail_stage(key, detail)
            long_run_monitor.stage_failed(key, detail=detail, error_type=type(exc).__name__)

        def stage_callback(key: str):
            return merge_progress_callbacks(
                status_panel.make_callback(key),
                long_run_monitor.make_progress_callback(key),
            )

        def can_resume_stage(
            key: str,
            *,
            required_paths: list[Path] | None = None,
            expected_input_count: int | None = None,
            expected_output_count: int | None = None,
            output_count_path: Path | None = None,
        ) -> bool:
            if not args.resume:
                return False
            if not stage_is_done(output_dir, key):
                return False
            if not stage_marker_matches_signature(output_dir, key, resume_signature):
                return False
            marker = load_stage_marker(output_dir, key)
            if expected_input_count is not None and marker.get("input_count") != expected_input_count:
                return False
            if required_paths and any(not path.exists() for path in required_paths):
                return False
            if expected_output_count is not None:
                marker_output_count = marker.get("output_count")
                if marker_output_count != expected_output_count:
                    return False
                if output_count_path is not None and _jsonl_row_count(output_count_path) != expected_output_count:
                    return False
            elif output_count_path is not None and marker.get("output_count") is not None:
                if _jsonl_row_count(output_count_path) != marker.get("output_count"):
                    return False
            return True

        corpus_stage_detail = "loading input corpus"
        if effective_build_corpus and fallback_build_corpus:
            corpus_stage_detail = f"input missing -> fallback build ({args.input_csv})"
        elif effective_build_corpus:
            corpus_stage_detail = "building corpus from Europe PMC"
        if can_resume_stage(
            "corpus",
            required_paths=[output_dir / "corpus.jsonl"],
            output_count_path=output_dir / "corpus.jsonl",
        ):
            corpus_rows = _load_corpus_jsonl(output_dir / "corpus.jsonl")
            skip_stage("corpus", f"resume:loaded rows={len(corpus_rows)}")
        else:
            start_stage("corpus", detail=corpus_stage_detail)
            try:
                if effective_build_corpus:
                    corpus_rows = build_corpus(
                        query=effective_query,
                        max_results=args.max_results,
                        output_jsonl=output_dir / "corpus.jsonl",
                        output_csv=corpus_csv_output,
                    )
                else:
                    corpus_rows = _load_input_corpus(args.input_csv)
                    if args.limit:
                        corpus_rows = corpus_rows[: args.limit]
                    write_jsonl(corpus_rows, output_dir / "corpus.jsonl")
                if args.limit and effective_build_corpus:
                    corpus_rows = corpus_rows[: args.limit]
                    write_jsonl(corpus_rows, output_dir / "corpus.jsonl")
                    if corpus_csv_output:
                        write_optional_csv(corpus_rows, corpus_csv_output)
                finish_stage(
                    "corpus",
                    completed=len(corpus_rows),
                    total=len(corpus_rows),
                    detail=f"rows={len(corpus_rows)}",
                    output_count=len(corpus_rows),
                    output_paths=[output_dir / "corpus.jsonl"],
                )
            except Exception as exc:
                fail_stage("corpus", exc)
                raise
        manifest.stage_outputs["corpus"] = str(output_dir / "corpus.jsonl")
        if corpus_csv_output:
            manifest.stage_outputs["corpus_csv"] = str(corpus_csv_output)

        if (
            can_resume_stage(
                "rule_filter",
                required_paths=[output_dir / "rule_pass.jsonl", output_dir / "rule_fail.jsonl"],
                expected_input_count=len(corpus_rows),
            )
            and (_jsonl_row_count(output_dir / "rule_pass.jsonl") or 0) + (_jsonl_row_count(output_dir / "rule_fail.jsonl") or 0) == len(corpus_rows)
        ):
            passed = load_jsonl(output_dir / "rule_pass.jsonl")
            failed = load_jsonl(output_dir / "rule_fail.jsonl")
            skip_stage("rule_filter", f"resume:pass={len(passed)} fail={len(failed)}")
        else:
            start_stage("rule_filter", total=len(corpus_rows), detail="applying heuristic screen")
            try:
                passed, failed = apply_rule_filter(
                    corpus_rows,
                    output_pass_jsonl=output_dir / "rule_pass.jsonl",
                    output_fail_jsonl=output_dir / "rule_fail.jsonl",
                    output_pass_csv=(output_dir / "rule_pass.csv") if args.export_csv else None,
                    output_fail_csv=(output_dir / "rule_fail.csv") if args.export_csv else None,
                )
                finish_stage(
                    "rule_filter",
                    completed=len(corpus_rows),
                    total=len(corpus_rows),
                    detail=f"pass={len(passed)} fail={len(failed)}",
                    input_count=len(corpus_rows),
                    output_count=len(passed) + len(failed),
                    output_paths=[output_dir / "rule_pass.jsonl", output_dir / "rule_fail.jsonl"],
                )
            except Exception as exc:
                fail_stage("rule_filter", exc)
                raise
        manifest.stage_outputs["rule_filter_pass"] = str(output_dir / "rule_pass.jsonl")
        manifest.stage_outputs["rule_filter_fail"] = str(output_dir / "rule_fail.jsonl")

        triaged_rows = passed
        if args.with_llm_triage:
            if can_resume_stage(
                "llm_triage",
                required_paths=[output_dir / "llm_triage.jsonl"],
                expected_input_count=len(passed),
                expected_output_count=len(passed),
                output_count_path=output_dir / "llm_triage.jsonl",
            ):
                triage_rows = load_jsonl(output_dir / "llm_triage.jsonl")
                triaged_rows = [row for row in triage_rows if row.get("queue") in {"now", "later"}]
                skip_stage("llm_triage", f"resume:kept={len(triaged_rows)}")
            else:
                start_stage("llm_triage", total=len(passed), detail="requesting OpenAI triage")
                try:
                    triage_rows = triage_records_with_llm(
                        passed,
                        model=stage_models["llm_triage"],
                        output_jsonl=output_dir / "llm_triage.jsonl",
                        output_csv=(output_dir / "llm_triage.csv") if args.export_csv else None,
                        progress_every=args.progress_every,
                        checkpoint_every=args.progress_every,
                        progress_callback=stage_callback("llm_triage"),
                        long_run_monitor=long_run_monitor,
                        resume_jsonl=(output_dir / "llm_triage.jsonl") if args.resume else None,
                    )
                    triaged_rows = [row for row in triage_rows if row.get("queue") in {"now", "later"}]
                    finish_stage(
                        "llm_triage",
                        completed=len(passed),
                        total=len(passed),
                        detail=f"kept={len(triaged_rows)}",
                        input_count=len(passed),
                        output_count=len(triage_rows),
                        output_paths=[output_dir / "llm_triage.jsonl"],
                    )
                except Exception as exc:
                    fail_stage("llm_triage", exc)
                    raise
            manifest.stage_outputs["llm_triage"] = str(output_dir / "llm_triage.jsonl")
        else:
            skip_stage("llm_triage", "disabled")

        access_stage_detail = "resolving OA access"
        if content_strategy.auto_download_pdf_for_legacy and not content_strategy.eager_download_primary:
            access_stage_detail = "resolving OA access + auto PDF for legacy extraction"
        elif content_strategy.eager_download_primary:
            access_stage_detail = "resolving OA access + downloading primary content"
        if can_resume_stage(
            "access",
            required_paths=[output_dir / "content_access.jsonl"],
            expected_input_count=len(triaged_rows),
            expected_output_count=len(triaged_rows),
            output_count_path=output_dir / "content_access.jsonl",
        ):
            access_items = load_typed_jsonl_if_exists(output_dir / "content_access.jsonl", ContentAccess)
            access_counts = _count_access_statuses(access_items)
            skip_stage(
                "access",
                (
                    f"resume:resolved={access_counts.get('resolved', 0)} "
                    f"downloaded={access_counts.get('downloaded', 0)} "
                    f"unresolved={access_counts.get('unresolved', 0)} "
                    f"error={access_counts.get('error', 0)}"
                ),
            )
        else:
            start_stage("access", total=len(triaged_rows), detail=access_stage_detail)
            try:
                access_items = resolve_content_batch(
                    triaged_rows,
                    content_root="papers",
                    download=content_strategy.eager_download_primary,
                    require_legacy_pdf=content_strategy.auto_download_pdf_for_legacy,
                    output_jsonl=output_dir / "content_access.jsonl",
                    output_csv=(output_dir / "content_access.csv") if args.export_csv else None,
                    progress_every=args.progress_every,
                    checkpoint_every=args.access_checkpoint_every,
                    progress_callback=stage_callback("access"),
                    resume_jsonl=(output_dir / "content_access.jsonl") if args.resume else None,
                )
                access_counts = _count_access_statuses(access_items)
                finish_stage(
                    "access",
                    completed=len(triaged_rows),
                    total=len(triaged_rows),
                    detail=(
                        f"resolved={access_counts.get('resolved', 0)} "
                        f"downloaded={access_counts.get('downloaded', 0)} "
                        f"unresolved={access_counts.get('unresolved', 0)} "
                        f"error={access_counts.get('error', 0)}"
                    ),
                    input_count=len(triaged_rows),
                    output_count=len(access_items),
                    output_paths=[output_dir / "content_access.jsonl"],
                )
            except Exception as exc:
                fail_stage("access", exc)
                raise
        manifest.stage_outputs["content_access"] = str(output_dir / "content_access.jsonl")

        content_handles = _build_content_handles(triaged_rows, access_items)
        routed_inputs = _build_route_inputs(triaged_rows, content_handles)

        if can_resume_stage(
            "routing",
            required_paths=[output_dir / "route_decisions.jsonl"],
            expected_input_count=len(routed_inputs),
            expected_output_count=len(routed_inputs),
            output_count_path=output_dir / "route_decisions.jsonl",
        ):
            route_decisions = load_typed_jsonl_if_exists(output_dir / "route_decisions.jsonl", RouteDecision)
            route_counts = _count_routes(route_decisions)
            skip_stage("routing", f"resume:{' '.join(f'{route}={count}' for route, count in sorted(route_counts.items()))}")
        else:
            start_stage("routing", total=len(routed_inputs), detail="selecting extraction route")
            try:
                route_decisions = route_papers(
                    routed_inputs,
                    model=stage_models["routing"],
                    output_jsonl=output_dir / "route_decisions.jsonl",
                    output_csv=(output_dir / "route_decisions.csv") if args.export_csv else None,
                    progress_every=args.progress_every,
                    checkpoint_every=args.progress_every,
                    progress_callback=stage_callback("routing"),
                    long_run_monitor=long_run_monitor,
                    resume_jsonl=(output_dir / "route_decisions.jsonl") if args.resume else None,
                )
                route_counts = _count_routes(route_decisions)
                finish_stage(
                    "routing",
                    completed=len(routed_inputs),
                    total=len(routed_inputs),
                    detail=" ".join(f"{route}={count}" for route, count in sorted(route_counts.items())),
                    input_count=len(routed_inputs),
                    output_count=len(route_decisions),
                    output_paths=[output_dir / "route_decisions.jsonl"],
                )
            except Exception as exc:
                fail_stage("routing", exc)
                raise
        manifest.stage_outputs["route_decisions"] = str(output_dir / "route_decisions.jsonl")

        table_route_pairs = _pairs_from_route_decisions(
            route_decisions,
            content_handles,
            routes={"table", "mixed", "figure"},
            source_check=lambda handle: has_structured_source(handle) or has_local_pdf(handle),
        )
        text_route_pairs = _pairs_from_route_decisions(
            route_decisions,
            content_handles,
            routes={"text", "mixed"},
            source_check=lambda handle: has_structured_source(handle) or has_local_pdf(handle),
        )
        figure_route_pairs = _pairs_from_route_decisions(
            route_decisions,
            content_handles,
            routes={"figure", "mixed"},
            source_check=has_local_pdf,
        )
        figure_route_pairs, figure_gate_skips = _apply_figure_gating(
            figure_route_pairs,
            gate_mode=run_profile.figure_gate_mode,
            min_route_confidence=run_profile.figure_min_route_confidence,
            require_explicit_signal=run_profile.figure_require_explicit_signal,
        )
        run_context_figure_gate_counts = {
            "routed_candidates": len(
                _pairs_from_route_decisions(
                    route_decisions,
                    content_handles,
                    routes={"figure", "mixed"},
                    source_check=has_local_pdf,
                )
            ),
            "after_gate": len(figure_route_pairs),
            "skipped": dict(figure_gate_skips),
        }
        run_context = ExtractorRunContext(
            run_id=manifest.run_id,
            model_name=args.model,
            stage_models=stage_models,
            output_dir=str(output_dir),
            prompt_paths=PROMPT_PATHS,
            config_paths=CONFIG_PATHS,
            notes=["Round 2 standardized extractor context."],
            fail_on_malformed_output=True,
            shared_state={
                "long_run_monitor": long_run_monitor,
                "figure_gate_counts": run_context_figure_gate_counts,
            },
        )

        table_stage_total = len(table_route_pairs)
        if can_resume_stage(
            "table_extract",
            required_paths=[output_dir / "table_records.jsonl", output_dir / "table_raw.jsonl"],
            expected_input_count=table_stage_total,
            output_count_path=output_dir / "table_records.jsonl",
        ):
            table_records = load_records_jsonl(output_dir / "table_records.jsonl")
            skip_stage("table_extract", f"resume:records={len(table_records)}")
        else:
            start_stage("table_extract", total=table_stage_total, detail="extracting structured-first table modality")
            try:
                table_records = extract_table_batch(
                    table_route_pairs,
                    policy=policy,
                    run_context=run_context,
                    output_jsonl=output_dir / "table_records.jsonl",
                    raw_output_jsonl=output_dir / "table_raw.jsonl",
                    output_csv=(output_dir / "table_records.csv") if args.export_csv else None,
                    progress_callback=stage_callback("table_extract"),
                    checkpoint_every=args.progress_every,
                )
                finish_stage(
                    "table_extract",
                    completed=table_stage_total,
                    total=table_stage_total,
                    detail=f"records={len(table_records)}",
                    input_count=table_stage_total,
                    output_count=len(table_records),
                    output_paths=[output_dir / "table_records.jsonl", output_dir / "table_raw.jsonl"],
                )
            except Exception as exc:
                fail_stage("table_extract", exc)
                raise
        run_context.shared_state["table_records_by_paper"] = _group_records_by_paper(table_records)

        text_stage_total = len(text_route_pairs)
        if can_resume_stage(
            "text_extract",
            required_paths=[output_dir / "text_records.jsonl", output_dir / "text_raw.jsonl"],
            expected_input_count=text_stage_total,
            output_count_path=output_dir / "text_records.jsonl",
        ):
            text_records = load_records_jsonl(output_dir / "text_records.jsonl")
            skip_stage("text_extract", f"resume:records={len(text_records)}")
        else:
            start_stage("text_extract", total=text_stage_total, detail="extracting structured-first text modality")
            try:
                text_records = extract_text_batch(
                    text_route_pairs,
                    policy=policy,
                    run_context=run_context,
                    output_jsonl=output_dir / "text_records.jsonl",
                    raw_output_jsonl=output_dir / "text_raw.jsonl",
                    output_csv=(output_dir / "text_records.csv") if args.export_csv else None,
                    progress_callback=stage_callback("text_extract"),
                    checkpoint_every=args.progress_every,
                )
                finish_stage(
                    "text_extract",
                    completed=text_stage_total,
                    total=text_stage_total,
                    detail=f"records={len(text_records)}",
                    input_count=text_stage_total,
                    output_count=len(text_records),
                    output_paths=[output_dir / "text_records.jsonl", output_dir / "text_raw.jsonl"],
                )
            except Exception as exc:
                fail_stage("text_extract", exc)
                raise

        figure_records: list = []
        figure_stage_total = len(figure_route_pairs)
        if args.enable_figure:
            if can_resume_stage(
                "figure_extract",
                required_paths=[
                    output_dir / "figure_records.jsonl",
                    output_dir / "figure_triage.jsonl",
                    output_dir / "figure_curves.jsonl",
                    output_dir / "figure_endpoints.jsonl",
                    output_dir / "figure_curve_map.jsonl",
                ],
                expected_input_count=figure_stage_total,
                output_count_path=output_dir / "figure_records.jsonl",
            ):
                figure_records = load_records_jsonl(output_dir / "figure_records.jsonl")
                skip_stage("figure_extract", f"resume:records={len(figure_records)}")
            else:
                gate_detail = ""
                if run_context_figure_gate_counts["skipped"]:
                    gate_detail = " | gate:" + ",".join(
                        f"{reason}={count}" for reason, count in sorted(figure_gate_skips.items())
                    )
                start_stage(
                    "figure_extract",
                    total=figure_stage_total,
                    detail=f"extracting traceable figure modality{gate_detail}",
                )
                try:
                    figure_records = extract_figure_batch(
                        figure_route_pairs,
                        policy=policy,
                        run_context=run_context,
                        output_jsonl=output_dir / "figure_records.jsonl",
                        output_csv=(output_dir / "figure_records.csv") if args.export_csv else None,
                        triage_jsonl=output_dir / "figure_triage.jsonl",
                        digitized_curves_jsonl=output_dir / "figure_curves.jsonl",
                        digitized_endpoints_jsonl=output_dir / "figure_endpoints.jsonl",
                        mapping_jsonl=output_dir / "figure_curve_map.jsonl",
                        progress_callback=stage_callback("figure_extract"),
                        checkpoint_every=args.progress_every,
                    )
                    finish_stage(
                        "figure_extract",
                        completed=figure_stage_total,
                        total=figure_stage_total,
                        detail=f"records={len(figure_records)}",
                        input_count=figure_stage_total,
                        output_count=len(figure_records),
                        output_paths=[
                            output_dir / "figure_records.jsonl",
                            output_dir / "figure_triage.jsonl",
                            output_dir / "figure_curves.jsonl",
                            output_dir / "figure_endpoints.jsonl",
                            output_dir / "figure_curve_map.jsonl",
                        ],
                    )
                except Exception as exc:
                    fail_stage("figure_extract", exc)
                    raise
        else:
            skip_stage("figure_extract", "disabled")

        assembly_input_count = len(table_records) + len(text_records) + len(figure_records)
        if can_resume_stage(
            "assembly",
            required_paths=[output_dir / "assembled_records.jsonl"],
            expected_input_count=assembly_input_count,
            output_count_path=output_dir / "assembled_records.jsonl",
        ):
            assembled = load_records_jsonl(output_dir / "assembled_records.jsonl")
            skip_stage("assembly", f"resume:assembled={len(assembled)}")
        else:
            start_stage("assembly", total=assembly_input_count, detail="merging candidate records")
            try:
                assembled = assemble_records(
                    [table_records, text_records, figure_records],
                    include_table_partials=False,
                    shared_state=run_context.shared_state,
                    output_jsonl=output_dir / "assembled_records.jsonl",
                    output_csv=(output_dir / "assembled_records.csv") if args.export_csv else None,
                    progress_callback=stage_callback("assembly"),
                )
                finish_stage(
                    "assembly",
                    completed=assembly_input_count,
                    total=assembly_input_count,
                    detail=f"assembled={len(assembled)}",
                    input_count=assembly_input_count,
                    output_count=len(assembled),
                    output_paths=[output_dir / "assembled_records.jsonl"],
                )
            except Exception as exc:
                fail_stage("assembly", exc)
                raise

        if can_resume_stage(
            "verify_initial",
            required_paths=[output_dir / "verified_initial.jsonl"],
            expected_input_count=len(assembled),
            expected_output_count=len(assembled),
            output_count_path=output_dir / "verified_initial.jsonl",
        ):
            initial_verified = load_records_jsonl(output_dir / "verified_initial.jsonl")
            initial_status_counts = _count_verification_statuses(initial_verified)
            skip_stage("verify_initial", f"resume:{' '.join(f'{status}={count}' for status, count in sorted(initial_status_counts.items()))}")
        else:
            start_stage("verify_initial", total=len(assembled), detail="policy + evidence verification")
            try:
                initial_verified = verify_records(
                    assembled,
                    policy=policy,
                    output_jsonl=output_dir / "verified_initial.jsonl",
                    output_csv=(output_dir / "verified_initial.csv") if args.export_csv else None,
                    progress_callback=stage_callback("verify_initial"),
                )
                initial_status_counts = _count_verification_statuses(initial_verified)
                finish_stage(
                    "verify_initial",
                    completed=len(assembled),
                    total=len(assembled),
                    detail=" ".join(f"{status}={count}" for status, count in sorted(initial_status_counts.items())),
                    input_count=len(assembled),
                    output_count=len(initial_verified),
                    output_paths=[output_dir / "verified_initial.jsonl"],
                )
            except Exception as exc:
                fail_stage("verify_initial", exc)
                raise

        if can_resume_stage(
            "patch_api",
            required_paths=[output_dir / "patched_api_concentration.jsonl"],
            expected_input_count=len(initial_verified),
            expected_output_count=len(initial_verified),
            output_count_path=output_dir / "patched_api_concentration.jsonl",
        ):
            patched_records = load_records_jsonl(output_dir / "patched_api_concentration.jsonl")
            skip_stage("patch_api", f"resume:applied={_count_patch_applications(patched_records, 'patch_api_concentration')}")
        else:
            start_stage("patch_api", total=len(initial_verified), detail="recovering api concentration evidence")
            try:
                patched_records = patch_api_concentration(
                    initial_verified,
                    output_jsonl=output_dir / "patched_api_concentration.jsonl",
                    progress_callback=stage_callback("patch_api"),
                )
                finish_stage(
                    "patch_api",
                    completed=len(initial_verified),
                    total=len(initial_verified),
                    detail=f"applied={_count_patch_applications(patched_records, 'patch_api_concentration')}",
                    input_count=len(initial_verified),
                    output_count=len(patched_records),
                    output_paths=[output_dir / "patched_api_concentration.jsonl"],
                )
            except Exception as exc:
                fail_stage("patch_api", exc)
                raise

        if can_resume_stage(
            "patch_endpoint",
            required_paths=[output_dir / "patched_endpoint_value.jsonl"],
            expected_input_count=len(patched_records),
            expected_output_count=len(patched_records),
            output_count_path=output_dir / "patched_endpoint_value.jsonl",
        ):
            patched_records = load_records_jsonl(output_dir / "patched_endpoint_value.jsonl")
            skip_stage("patch_endpoint", f"resume:applied={_count_patch_applications(patched_records, 'patch_endpoint_value')}")
        else:
            start_stage("patch_endpoint", total=len(patched_records), detail="recovering endpoint value evidence")
            try:
                patched_records = patch_endpoint_value(
                    patched_records,
                    output_jsonl=output_dir / "patched_endpoint_value.jsonl",
                    progress_callback=stage_callback("patch_endpoint"),
                )
                finish_stage(
                    "patch_endpoint",
                    completed=len(patched_records),
                    total=len(patched_records),
                    detail=f"applied={_count_patch_applications(patched_records, 'patch_endpoint_value')}",
                    input_count=len(patched_records),
                    output_count=len(patched_records),
                    output_paths=[output_dir / "patched_endpoint_value.jsonl"],
                )
            except Exception as exc:
                fail_stage("patch_endpoint", exc)
                raise

        if can_resume_stage(
            "patch_time",
            required_paths=[output_dir / "patched_endpoint_time.jsonl"],
            expected_input_count=len(patched_records),
            expected_output_count=len(patched_records),
            output_count_path=output_dir / "patched_endpoint_time.jsonl",
        ):
            patched_records = load_records_jsonl(output_dir / "patched_endpoint_time.jsonl")
            skip_stage("patch_time", f"resume:applied={_count_patch_applications(patched_records, 'patch_endpoint_time')}")
        else:
            start_stage("patch_time", total=len(patched_records), detail="recovering endpoint time evidence")
            try:
                patched_records = patch_endpoint_time(
                    patched_records,
                    output_jsonl=output_dir / "patched_endpoint_time.jsonl",
                    progress_callback=stage_callback("patch_time"),
                )
                finish_stage(
                    "patch_time",
                    completed=len(patched_records),
                    total=len(patched_records),
                    detail=f"applied={_count_patch_applications(patched_records, 'patch_endpoint_time')}",
                    input_count=len(patched_records),
                    output_count=len(patched_records),
                    output_paths=[output_dir / "patched_endpoint_time.jsonl"],
                )
            except Exception as exc:
                fail_stage("patch_time", exc)
                raise

        if can_resume_stage(
            "patch_area",
            required_paths=[output_dir / "patched_area.jsonl"],
            expected_input_count=len(patched_records),
            expected_output_count=len(patched_records),
            output_count_path=output_dir / "patched_area.jsonl",
        ):
            patched_records = load_records_jsonl(output_dir / "patched_area.jsonl")
            skip_stage("patch_area", f"resume:applied={_count_patch_applications(patched_records, 'patch_area')}")
        else:
            start_stage("patch_area", total=len(patched_records), detail="recovering diffusion area evidence")
            try:
                patched_records = patch_area(
                    patched_records,
                    output_jsonl=output_dir / "patched_area.jsonl",
                    progress_callback=stage_callback("patch_area"),
                )
                finish_stage(
                    "patch_area",
                    completed=len(patched_records),
                    total=len(patched_records),
                    detail=f"applied={_count_patch_applications(patched_records, 'patch_area')}",
                    input_count=len(patched_records),
                    output_count=len(patched_records),
                    output_paths=[output_dir / "patched_area.jsonl"],
                )
            except Exception as exc:
                fail_stage("patch_area", exc)
                raise

        if can_resume_stage(
            "verify_final",
            required_paths=[output_dir / "verified_records.jsonl"],
            expected_input_count=len(patched_records),
            expected_output_count=len(patched_records),
            output_count_path=output_dir / "verified_records.jsonl",
        ):
            verified = load_records_jsonl(output_dir / "verified_records.jsonl")
            final_status_counts = _count_verification_statuses(verified)
            skip_stage("verify_final", f"resume:{' '.join(f'{status}={count}' for status, count in sorted(final_status_counts.items()))}")
        else:
            start_stage("verify_final", total=len(patched_records), detail="final verification after patching")
            try:
                verified = verify_records(
                    patched_records,
                    policy=policy,
                    output_jsonl=output_dir / "verified_records.jsonl",
                    output_csv=(output_dir / "verified_records.csv") if args.export_csv else None,
                    progress_callback=stage_callback("verify_final"),
                )
                final_status_counts = _count_verification_statuses(verified)
                finish_stage(
                    "verify_final",
                    completed=len(patched_records),
                    total=len(patched_records),
                    detail=" ".join(f"{status}={count}" for status, count in sorted(final_status_counts.items())),
                    input_count=len(patched_records),
                    output_count=len(verified),
                    output_paths=[output_dir / "verified_records.jsonl"],
                )
            except Exception as exc:
                fail_stage("verify_final", exc)
                raise

        adjudication_rows: list[dict] = []
        if args.with_llm_adjudication:
            adjudication_output_path = output_dir / "llm_adjudication.jsonl"
            adjudication_csv_path = output_dir / "llm_adjudication.csv"
            adjudication_candidates = select_adjudication_candidates(verified, limit=args.llm_adjudication_limit)
            if can_resume_stage(
                "llm_adjudicate",
                required_paths=[adjudication_output_path],
                expected_input_count=len(adjudication_candidates),
            ):
                adjudication_rows = load_jsonl(adjudication_output_path)
                skip_stage("llm_adjudicate", f"resume:rows={len(adjudication_rows)}")
            else:
                start_stage(
                    "llm_adjudicate",
                    total=len(adjudication_candidates),
                    detail="audit-only recoverable-unresolved ranking",
                )
                try:
                    adjudication_rows = adjudicate_records(
                        verified,
                        model=stage_models["llm_adjudicate"],
                        output_jsonl=adjudication_output_path,
                        output_csv=adjudication_csv_path if args.export_csv else None,
                        progress_callback=stage_callback("llm_adjudicate"),
                        long_run_monitor=long_run_monitor,
                        limit=args.llm_adjudication_limit,
                    )
                    finish_stage(
                        "llm_adjudicate",
                        completed=len(adjudication_candidates),
                        total=len(adjudication_candidates),
                        detail=f"rows={len(adjudication_rows)}",
                        input_count=len(adjudication_candidates),
                        output_count=len(adjudication_rows),
                        output_paths=[adjudication_output_path],
                    )
                except Exception as exc:
                    fail_stage("llm_adjudicate", exc)
                    raise
        else:
            skip_stage("llm_adjudicate", "disabled")

        manifest.stage_outputs.update(
            {
                "table_records": str(output_dir / "table_records.jsonl"),
                "text_records": str(output_dir / "text_records.jsonl"),
                "assembled_records": str(output_dir / "assembled_records.jsonl"),
                "verified_initial": str(output_dir / "verified_initial.jsonl"),
                "verified_records": str(output_dir / "verified_records.jsonl"),
                "patched_api_concentration": str(output_dir / "patched_api_concentration.jsonl"),
                "patched_endpoint_value": str(output_dir / "patched_endpoint_value.jsonl"),
                "patched_endpoint_time": str(output_dir / "patched_endpoint_time.jsonl"),
                "patched_area": str(output_dir / "patched_area.jsonl"),
            }
        )
        if args.with_llm_adjudication:
            manifest.stage_outputs["llm_adjudication"] = str(output_dir / "llm_adjudication.jsonl")
        if args.enable_figure:
            manifest.stage_outputs.update(
                {
                    "figure_triage": str(output_dir / "figure_triage.jsonl"),
                    "figure_curves": str(output_dir / "figure_curves.jsonl"),
                    "figure_endpoints": str(output_dir / "figure_endpoints.jsonl"),
                    "figure_curve_map": str(output_dir / "figure_curve_map.jsonl"),
                    "figure_records": str(output_dir / "figure_records.jsonl"),
                }
            )

        manifest.stage_metrics.update(
            {
                "corpus_rows": len(corpus_rows),
                "rule_pass_rows": len(passed),
                "triaged_rows": len(triaged_rows),
                "route_decisions": len(route_decisions),
                "table_records": len(table_records),
                "text_records": len(text_records),
                "figure_records": len(figure_records),
                "assembled_records": len(assembled),
                "final_records_evaluated": len(verified),
                "actually_verified_records": _count_records_with_status(verified, "verified"),
                "final_unresolved_records": _count_records_with_status(verified, "unresolved"),
                "final_rejected_records": _count_records_with_status(verified, "rejected"),
                "patch_count": sum(len(record.patches) for record in verified),
                "figure_gate_counts": run_context.shared_state.get("figure_gate_counts", {}),
                "llm_adjudication_rows": len(adjudication_rows),
            }
        )
        write_manifest(manifest, output_dir / "run_manifest.jsonl")

        report_output_paths = [output_dir / "report" / "run_report.md", output_dir / "report" / "run_report.json"]
        if can_resume_stage(
            "report",
            required_paths=report_output_paths,
            expected_input_count=len(verified),
        ):
            report = json.loads((output_dir / "report" / "run_report.json").read_text(encoding="utf-8"))
            manifest.stage_metrics.update(
                {
                    "figure_stage_counts": report.get("figure_stage_counts", {}),
                    "figure_failure_counts": report.get("figure_failure_counts", {}),
                    "figure_verification_failure_taxonomy_counts": report.get("figure_verification_failure_taxonomy_counts", {}),
                    "llm_reliability": report.get("llm_reliability", {}),
                    "llm_adjudication_summary": report.get("llm_adjudication_summary", {}),
                }
            )
            write_manifest(manifest, output_dir / "run_manifest.jsonl")
            skip_stage("report", f"resume:path={output_dir / 'report' / 'run_report.md'}")
        else:
            start_stage("report", detail="building run report")
            try:
                report = build_run_report(
                    manifest=manifest,
                    route_decisions=route_decisions,
                    extractor_outputs={
                        "table": table_records,
                        "text": text_records,
                        "figure": figure_records,
                    },
                    assembled_records=assembled,
                    verified_records=verified,
                    output_dir=output_dir / "report",
                    export_csv_views=args.export_csv,
                )
                manifest.stage_metrics.update(
                    {
                        "figure_stage_counts": report.get("figure_stage_counts", {}),
                        "figure_failure_counts": report.get("figure_failure_counts", {}),
                        "figure_verification_failure_taxonomy_counts": report.get("figure_verification_failure_taxonomy_counts", {}),
                        "llm_reliability": report.get("llm_reliability", {}),
                        "llm_adjudication_summary": report.get("llm_adjudication_summary", {}),
                    }
                )
                write_manifest(manifest, output_dir / "run_manifest.jsonl")
                finish_stage(
                    "report",
                    detail=f"path={output_dir / 'report' / 'run_report.md'}",
                    input_count=len(verified),
                    output_paths=report_output_paths,
                )
            except Exception as exc:
                fail_stage("report", exc)
                raise

    print(f"Corpus rows: {len(corpus_rows)}")
    print(f"Route decisions: {len(route_decisions)}")
    print(f"Table records: {len(table_records)}")
    print(f"Text records: {len(text_records)}")
    print(f"Figure records: {len(figure_records)}")
    print(f"Final records evaluated: {len(verified)}")
    print(f"Actually verified: {_count_records_with_status(verified, 'verified')}")
    print(f"Final unresolved: {_count_records_with_status(verified, 'unresolved')}")
    print(f"Final rejected: {_count_records_with_status(verified, 'rejected')}")
    print(f"Run report: {output_dir / 'report' / 'run_report.md'}")
    print(f"Failure taxonomy counts: {report['failure_taxonomy_counts']}")
    print(f"Figure failure counts: {report['figure_failure_counts']}")
    if args.with_llm_adjudication:
        print(f"LLM adjudication rows: {report.get('llm_adjudication_summary', {}).get('row_count', 0)}")
        print(f"LLM adjudication summary: {output_dir / 'report' / 'llm_adjudication_summary.csv'}")
    if args.long_run_mode:
        print(f"Long-run summary: {long_run_dir / 'summary.json'}")
        print(f"Long-run events: {long_run_dir / 'events.jsonl'}")


if __name__ == "__main__":
    main()
