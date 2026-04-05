"""Run reporting and reproducibility outputs for the SkinMiner pipeline."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from configs.run_profiles import STAGE_MODEL_KEYS
from schemas.models import Record, RouteDecision, RunManifest
from utils.io import ensure_parent, flatten_record, load_jsonl, write_records_csv
from verification.failure_taxonomy import count_failure_codes, count_failure_codes_by_route


def _counter_to_rows(counter: Counter[str], category: str) -> list[dict[str, Any]]:
    return [{category: key, "count": value} for key, value in sorted(counter.items())]


def _mapping_to_rows(mapping: dict[str, int], category: str) -> list[dict[str, Any]]:
    return [{category: key, "count": value} for key, value in sorted(mapping.items())]


def _load_jsonl_if_exists(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    candidate = Path(path)
    if not candidate.exists():
        return []
    return load_jsonl(candidate)


def _load_json_if_exists(path: str | Path | None) -> dict[str, Any]:
    if not path:
        return {}
    candidate = Path(path)
    if not candidate.exists():
        return {}
    return json.loads(candidate.read_text(encoding="utf-8"))


def _normalize_reason_label(value: Any, fallback: str = "unspecified") -> str:
    text = " ".join(str(value or "").split()).lower()
    if not text:
        return fallback
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text[:80] or fallback


def _build_figure_failure_summary(manifest: RunManifest) -> dict[str, Any]:
    triage_rows = _load_jsonl_if_exists(manifest.stage_outputs.get("figure_triage"))
    curve_rows = _load_jsonl_if_exists(manifest.stage_outputs.get("figure_curves"))
    endpoint_rows = _load_jsonl_if_exists(manifest.stage_outputs.get("figure_endpoints"))
    mapping_rows = _load_jsonl_if_exists(manifest.stage_outputs.get("figure_curve_map"))

    triage_signals: Counter[str] = Counter()
    triage_route_counts: Counter[str] = Counter()
    for row in triage_rows:
        recommended_route = str(row.get("recommended_route", "") or "")
        if recommended_route:
            triage_route_counts[recommended_route] += 1
            if recommended_route != "digitize":
                triage_signals[f"recommended_route:{recommended_route}"] += 1
        endpoint_curve_present = str(row.get("endpoint_curve_present", "") or "")
        if endpoint_curve_present and endpoint_curve_present != "yes":
            triage_signals[f"endpoint_curve_present:{endpoint_curve_present}"] += 1
        digitizable = str(row.get("digitizable", "") or "")
        if digitizable and digitizable != "yes":
            triage_signals[f"digitizable:{digitizable}"] += 1
        ticks_readable = str(row.get("ticks_readable", "") or "")
        if ticks_readable and ticks_readable != "yes":
            triage_signals[f"ticks_readable:{ticks_readable}"] += 1
        why_not_digitizable = str(row.get("why_not_digitizable", "") or "")
        if why_not_digitizable.strip():
            triage_signals[f"why_not_digitizable:{_normalize_reason_label(why_not_digitizable)}"] += 1

    endpoint_status_counts: Counter[str] = Counter()
    digitization_failures: Counter[str] = Counter()
    for row in endpoint_rows:
        status = str(row.get("status", "") or "unknown")
        endpoint_status_counts[status] += 1
        if status != "ok":
            digitization_failures[status] += 1

    mapping_status_counts: Counter[str] = Counter()
    mapping_failures: Counter[str] = Counter()
    for row in mapping_rows:
        status = str(row.get("mapping_status", "") or "unknown")
        mapping_status_counts[status] += 1
        mapped_label = str(row.get("mapped_formulation_label", "") or "").strip()
        if status != "vision_mapped" or not mapped_label:
            reason = _normalize_reason_label(row.get("mapping_rationale"), fallback="unmapped")
            mapping_failures[reason] += 1

    stage_counts = {
        "triage_artifacts": len(triage_rows),
        "triage_digitize_candidates": sum(1 for row in triage_rows if row.get("recommended_route") == "digitize"),
        "digitized_curves": len(curve_rows),
        "digitized_endpoints_ok": endpoint_status_counts.get("ok", 0),
        "digitized_endpoints_failed": sum(count for status, count in endpoint_status_counts.items() if status != "ok"),
        "mapped_curves": sum(
            1
            for row in mapping_rows
            if row.get("mapping_status") == "vision_mapped" and str(row.get("mapped_formulation_label", "") or "").strip()
        ),
        "unmapped_curves": sum(
            1
            for row in mapping_rows
            if row.get("mapping_status") != "vision_mapped" or not str(row.get("mapped_formulation_label", "") or "").strip()
        ),
    }

    return {
        "stage_counts": stage_counts,
        "triage_route_counts": dict(triage_route_counts),
        "triage_signals": dict(triage_signals),
        "digitization_status_counts": dict(endpoint_status_counts),
        "digitization_failure_counts": dict(digitization_failures),
        "mapping_status_counts": dict(mapping_status_counts),
        "mapping_failure_counts": dict(mapping_failures),
    }


def _as_reason_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item or "").strip() for item in value if str(item or "").strip()]
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []


def _build_blockage_summary(
    manifest: RunManifest,
    route_decisions: list[RouteDecision],
    verified_records: list[Record],
    output_dir: Path,
) -> dict[str, Any]:
    content_rows = _load_jsonl_if_exists(manifest.stage_outputs.get("content_access"))
    text_raw_rows = _load_jsonl_if_exists(output_dir / "text_raw.jsonl")
    table_raw_rows = _load_jsonl_if_exists(output_dir / "table_raw.jsonl")

    access_status_counts: Counter[str] = Counter()
    access_reason_counts: Counter[str] = Counter()
    for row in content_rows:
        status = str(row.get("status", "") or "unknown")
        access_status_counts[status] += 1
        if status in {"unresolved", "error"}:
            for note in _as_reason_list(row.get("notes")):
                access_reason_counts[_normalize_reason_label(note)] += 1

    unresolved_route_reason_counts: Counter[str] = Counter()
    route_note_counts: Counter[str] = Counter()
    for decision in route_decisions:
        note = str(decision.notes or "").strip()
        if note:
            route_note_counts[_normalize_reason_label(note)] += 1
        if decision.route == "unresolved":
            unresolved_route_reason_counts[_normalize_reason_label(note, fallback="unspecified")] += 1

    extractor_blockages: dict[str, dict[str, int]] = {}
    for name, rows in {"text": text_raw_rows, "table": table_raw_rows}.items():
        status_counts: Counter[str] = Counter()
        error_type_counts: Counter[str] = Counter()
        source_backend_counts: Counter[str] = Counter()
        for row in rows:
            status = str(row.get("status", "") or "unknown")
            status_counts[status] += 1
            if status != "ok":
                error_type = str(row.get("error_type", "") or row.get("status", "") or "unknown")
                error_type_counts[_normalize_reason_label(error_type)] += 1
            source_backend = str(row.get("source_backend", "") or "")
            if source_backend:
                source_backend_counts[_normalize_reason_label(source_backend)] += 1
        extractor_blockages[name] = {
            "status_counts": dict(status_counts),
            "error_type_counts": dict(error_type_counts),
            "source_backend_counts": dict(source_backend_counts),
        }

    patch_status_counts: dict[str, Counter[str]] = {}
    patch_reason_counts: dict[str, Counter[str]] = {}
    for record in verified_records:
        for patch in record.patches:
            patch_status_counts.setdefault(patch.patcher_name, Counter())[patch.status] += 1
            if patch.status != "applied":
                patch_reason_counts.setdefault(patch.patcher_name, Counter())[
                    _normalize_reason_label(patch.notes, fallback="unspecified")
                ] += 1

    return {
        "access_status_counts": dict(access_status_counts),
        "access_reason_counts": dict(access_reason_counts),
        "route_unresolved_reason_counts": dict(unresolved_route_reason_counts),
        "route_note_counts": dict(route_note_counts),
        "extractor_blockages": extractor_blockages,
        "patch_status_counts": {
            patcher: dict(counter)
            for patcher, counter in sorted(patch_status_counts.items())
        },
        "patch_reason_counts": {
            patcher: dict(counter)
            for patcher, counter in sorted(patch_reason_counts.items())
        },
    }


def _build_llm_adjudication_summary(manifest: RunManifest) -> dict[str, Any]:
    rows = _load_jsonl_if_exists(manifest.stage_outputs.get("llm_adjudication"))
    candidate_reason_counts: Counter[str] = Counter()
    priority_bucket_counts: Counter[str] = Counter()
    review_focus_counts: Counter[str] = Counter()
    recommended_status_counts: Counter[str] = Counter()
    should_keep_counts: Counter[str] = Counter()
    disagreement_counts: Counter[str] = Counter()
    original_vs_recommended: Counter[str] = Counter()

    for row in rows:
        candidate_reason_counts[str(row.get("candidate_reason", "") or "unknown")] += 1
        priority_bucket_counts[str(row.get("priority_bucket", "") or "unknown")] += 1
        review_focus_counts[str(row.get("review_focus", "") or "unknown")] += 1
        original_status = str(row.get("original_status", "") or "unknown")
        adjudication = row.get("adjudication", {}) or {}
        recommended_status = str(adjudication.get("recommended_status", "") or "unknown")
        should_keep = str(adjudication.get("should_keep_strict", "") or "unknown")
        recommended_status_counts[recommended_status] += 1
        should_keep_counts[should_keep] += 1
        original_vs_recommended[f"{original_status}->{recommended_status}"] += 1
        if original_status != recommended_status:
            disagreement_counts["status_disagreement"] += 1
        original_scope_bucket = str(row.get("original_scope_bucket", "") or "unknown")
        recommended_scope_bucket = str(adjudication.get("scope_bucket", "") or "unknown")
        if original_scope_bucket != recommended_scope_bucket:
            disagreement_counts["scope_bucket_disagreement"] += 1

    return {
        "row_count": len(rows),
        "candidate_reason_counts": dict(candidate_reason_counts),
        "priority_bucket_counts": dict(priority_bucket_counts),
        "review_focus_counts": dict(review_focus_counts),
        "recommended_status_counts": dict(recommended_status_counts),
        "should_keep_strict_counts": dict(should_keep_counts),
        "disagreement_counts": dict(disagreement_counts),
        "original_vs_recommended_counts": dict(original_vs_recommended),
    }


def build_run_report(
    manifest: RunManifest,
    route_decisions: list[RouteDecision],
    extractor_outputs: dict[str, list[Record]],
    assembled_records: list[Record],
    verified_records: list[Record],
    output_dir: str | Path,
    export_csv_views: bool = True,
) -> dict[str, Any]:
    """Build structured JSON, Markdown, and CSV reporting artifacts for a run."""

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    route_distribution = Counter(decision.route for decision in route_decisions)
    verification_outcomes = Counter(record.verification_status for record in verified_records)
    scope_buckets = Counter(record.scope_bucket or "unknown" for record in verified_records)
    scope_tags = Counter(tag for record in verified_records for tag in (record.scope_tags or []) if tag)
    stage_models = manifest.stage_metrics.get("stage_models", {}) or {key: manifest.model_name for key in STAGE_MODEL_KEYS}
    actual_verified_count = verification_outcomes.get("verified", 0)
    unresolved_count = verification_outcomes.get("unresolved", 0)
    rejected_count = verification_outcomes.get("rejected", 0)
    failure_counts = count_failure_codes(verified_records)
    failure_counts_by_route = count_failure_codes_by_route(verified_records)
    figure_verification_failures = count_failure_codes(verified_records, route="figure")
    figure_failure_summary = _build_figure_failure_summary(manifest)
    long_run_summary = _load_json_if_exists(manifest.stage_outputs.get("long_run_summary"))
    llm_reliability = long_run_summary.get("llm_reliability", {}) if long_run_summary else {}
    llm_adjudication_summary = _build_llm_adjudication_summary(manifest)
    blockage_summary = _build_blockage_summary(manifest, route_decisions, verified_records, out_dir)
    patch_success_counts = Counter(
        patch.patcher_name
        for record in verified_records
        for patch in record.patches
        if patch.status == "applied"
    )
    extractor_counts = {name: len(records) for name, records in extractor_outputs.items()}

    report = {
        "run_id": manifest.run_id,
        "model_name": manifest.model_name,
        "policy_name": manifest.policy_name,
        "timestamp_utc": manifest.timestamp_utc.isoformat(),
        "run_profile": manifest.stage_metrics.get("run_profile", ""),
        "query_profile": manifest.stage_metrics.get("query_profile", ""),
        "query_profile_version": manifest.stage_metrics.get("query_profile_version", ""),
        "query_source": manifest.stage_metrics.get("query_source", ""),
        "stage_models": stage_models,
        "prompt_assets": manifest.stage_metrics.get("prompt_assets", {}),
        "module_counts": extractor_counts,
        "route_distribution": dict(route_distribution),
        "extractor_output_counts": extractor_counts,
        "verification_outcome_counts": dict(verification_outcomes),
        "scope_bucket_counts": dict(scope_buckets),
        "scope_tag_counts": dict(scope_tags),
        "failure_taxonomy_counts": failure_counts,
        "failure_taxonomy_counts_by_route": failure_counts_by_route,
        "figure_verification_failure_taxonomy_counts": figure_verification_failures,
        "figure_stage_counts": figure_failure_summary["stage_counts"],
        "figure_failure_counts": {
            "triage_signals": figure_failure_summary["triage_signals"],
            "digitization_failure_counts": figure_failure_summary["digitization_failure_counts"],
            "mapping_failure_counts": figure_failure_summary["mapping_failure_counts"],
        },
        "figure_gate_counts": manifest.stage_metrics.get("figure_gate_counts", {}),
        "figure_route_counts": figure_failure_summary["triage_route_counts"],
        "figure_digitization_status_counts": figure_failure_summary["digitization_status_counts"],
        "figure_mapping_status_counts": figure_failure_summary["mapping_status_counts"],
        "llm_reliability": llm_reliability,
        "llm_adjudication_summary": llm_adjudication_summary,
        "blockage_summary": blockage_summary,
        "patch_success_counts": dict(patch_success_counts),
        "output_record_counts": {
            "assembled": len(assembled_records),
            "final_records_evaluated": len(verified_records),
            "actually_verified": actual_verified_count,
            "unresolved": unresolved_count,
            "rejected": rejected_count,
        },
    }

    json_path = ensure_parent(out_dir / "run_report.json")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    summary_rows = (
        _counter_to_rows(route_distribution, "route")
        + _mapping_to_rows(extractor_counts, "module")
        + _counter_to_rows(verification_outcomes, "verification_status")
        + _counter_to_rows(scope_buckets, "scope_bucket")
        + _counter_to_rows(scope_tags, "scope_tag")
        + _mapping_to_rows(failure_counts, "failure_code")
        + _counter_to_rows(patch_success_counts, "patcher")
    )
    llm_reliability_rows = [
        {"module": module, "metric": metric, "count": value}
        for module, metrics in sorted(llm_reliability.items())
        for metric, value in sorted(metrics.items())
        if metric != "model_name" and isinstance(value, int)
    ]
    figure_summary_rows = (
        [{"stage": "figure_stage", "bucket": key, "count": value} for key, value in sorted(figure_failure_summary["stage_counts"].items())]
        + [
            {"stage": "figure_gate", "bucket": f"skipped:{key}", "count": value}
            for key, value in sorted((manifest.stage_metrics.get("figure_gate_counts", {}) or {}).get("skipped", {}).items())
        ]
        + [
            {"stage": "figure_gate", "bucket": "routed_candidates", "count": int((manifest.stage_metrics.get("figure_gate_counts", {}) or {}).get("routed_candidates", 0))}
        ]
        + [
            {"stage": "figure_gate", "bucket": "after_gate", "count": int((manifest.stage_metrics.get("figure_gate_counts", {}) or {}).get("after_gate", 0))}
        ]
        + [{"stage": "figure_triage_route", "bucket": key, "count": value} for key, value in sorted(figure_failure_summary["triage_route_counts"].items())]
        + [{"stage": "figure_triage_signal", "bucket": key, "count": value} for key, value in sorted(figure_failure_summary["triage_signals"].items())]
        + [{"stage": "figure_digitization_status", "bucket": key, "count": value} for key, value in sorted(figure_failure_summary["digitization_status_counts"].items())]
        + [{"stage": "figure_digitization_failure", "bucket": key, "count": value} for key, value in sorted(figure_failure_summary["digitization_failure_counts"].items())]
        + [{"stage": "figure_mapping_status", "bucket": key, "count": value} for key, value in sorted(figure_failure_summary["mapping_status_counts"].items())]
        + [{"stage": "figure_mapping_failure", "bucket": key, "count": value} for key, value in sorted(figure_failure_summary["mapping_failure_counts"].items())]
        + [{"stage": f"verification_route:{route}", "bucket": key, "count": value} for route, counts in sorted(failure_counts_by_route.items()) for key, value in sorted(counts.items())]
    )
    blockage_rows = (
        [{"stage": "access_status", "bucket": key, "count": value} for key, value in sorted(blockage_summary["access_status_counts"].items())]
        + [{"stage": "access_reason", "bucket": key, "count": value} for key, value in sorted(blockage_summary["access_reason_counts"].items())]
        + [{"stage": "route_unresolved_reason", "bucket": key, "count": value} for key, value in sorted(blockage_summary["route_unresolved_reason_counts"].items())]
        + [{"stage": "route_note", "bucket": key, "count": value} for key, value in sorted(blockage_summary["route_note_counts"].items())]
        + [
            {"stage": f"{name}_status", "bucket": key, "count": value}
            for name, payload in sorted(blockage_summary["extractor_blockages"].items())
            for key, value in sorted(payload["status_counts"].items())
        ]
        + [
            {"stage": f"{name}_error_type", "bucket": key, "count": value}
            for name, payload in sorted(blockage_summary["extractor_blockages"].items())
            for key, value in sorted(payload["error_type_counts"].items())
        ]
        + [
            {"stage": f"{name}_source_backend", "bucket": key, "count": value}
            for name, payload in sorted(blockage_summary["extractor_blockages"].items())
            for key, value in sorted(payload["source_backend_counts"].items())
        ]
        + [
            {"stage": f"patch_status:{patcher}", "bucket": key, "count": value}
            for patcher, counts in sorted(blockage_summary["patch_status_counts"].items())
            for key, value in sorted(counts.items())
        ]
        + [
            {"stage": f"patch_reason:{patcher}", "bucket": key, "count": value}
            for patcher, counts in sorted(blockage_summary["patch_reason_counts"].items())
            for key, value in sorted(counts.items())
        ]
    )
    adjudication_rows = (
        [{"stage": "llm_adjudication_candidate_reason", "bucket": key, "count": value} for key, value in sorted(llm_adjudication_summary["candidate_reason_counts"].items())]
        + [{"stage": "llm_adjudication_priority_bucket", "bucket": key, "count": value} for key, value in sorted(llm_adjudication_summary["priority_bucket_counts"].items())]
        + [{"stage": "llm_adjudication_review_focus", "bucket": key, "count": value} for key, value in sorted(llm_adjudication_summary["review_focus_counts"].items())]
        + [{"stage": "llm_adjudication_recommended_status", "bucket": key, "count": value} for key, value in sorted(llm_adjudication_summary["recommended_status_counts"].items())]
        + [{"stage": "llm_adjudication_should_keep", "bucket": key, "count": value} for key, value in sorted(llm_adjudication_summary["should_keep_strict_counts"].items())]
        + [{"stage": "llm_adjudication_disagreement", "bucket": key, "count": value} for key, value in sorted(llm_adjudication_summary["disagreement_counts"].items())]
        + [{"stage": "llm_adjudication_transition", "bucket": key, "count": value} for key, value in sorted(llm_adjudication_summary["original_vs_recommended_counts"].items())]
    )
    if export_csv_views:
        pd.DataFrame(summary_rows).to_csv(out_dir / "run_summary.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(figure_summary_rows).to_csv(out_dir / "figure_failure_summary.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(llm_reliability_rows).to_csv(out_dir / "llm_reliability_summary.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(blockage_rows).to_csv(out_dir / "blockage_summary.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(adjudication_rows).to_csv(out_dir / "llm_adjudication_summary.csv", index=False, encoding="utf-8-sig")
        write_records_csv(verified_records, out_dir / "verified_records_flat.csv")
        pd.DataFrame([flatten_record(record) for record in verified_records]).to_csv(
            out_dir / "verified_records_debug.csv",
            index=False,
            encoding="utf-8-sig",
        )

    markdown = [
        f"# Run Report: {manifest.run_id}",
        "",
        f"- Model: `{manifest.model_name}`",
        f"- Policy: `{manifest.policy_name}`",
        f"- Run profile: `{manifest.stage_metrics.get('run_profile', '')}`",
        f"- Query profile: `{manifest.stage_metrics.get('query_profile', '')}`",
        f"- Query profile version: `{manifest.stage_metrics.get('query_profile_version', '')}`",
        f"- Query source: `{manifest.stage_metrics.get('query_source', '')}`",
        f"- Stage models: `{stage_models}`",
        f"- Assembled records: `{len(assembled_records)}`",
        f"- Final records evaluated: `{len(verified_records)}`",
        f"- Actually verified: `{actual_verified_count}`",
        f"- Final unresolved: `{unresolved_count}`",
        f"- Final rejected: `{rejected_count}`",
        "",
        "## Route Distribution",
    ]
    markdown.extend([f"- {key}: {value}" for key, value in sorted(route_distribution.items())])
    markdown.append("")
    markdown.append("## Extractor Outputs")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(extractor_counts.items())])
    markdown.append("")
    markdown.append("## Verification Outcomes")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(verification_outcomes.items())])
    markdown.append("")
    markdown.append("## Scope Buckets")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(scope_buckets.items())] or ["- none"])
    markdown.append("")
    markdown.append("## Scope Tags")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(scope_tags.items())] or ["- none"])
    markdown.append("")
    markdown.append("## Failure Taxonomy")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(failure_counts.items())])
    markdown.append("")
    markdown.append("## Failure Taxonomy By Route")
    for route, counts in sorted(failure_counts_by_route.items()):
        markdown.append(f"### {route}")
        markdown.extend([f"- {key}: {value}" for key, value in sorted(counts.items())])
        if not counts:
            markdown.append("- none")
    markdown.append("")
    markdown.append("## Figure Stage Counts")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(figure_failure_summary["stage_counts"].items())])
    markdown.append("")
    markdown.append("## Figure Gate Counts")
    figure_gate_counts = manifest.stage_metrics.get("figure_gate_counts", {})
    if figure_gate_counts:
        markdown.append(f"- routed_candidates: {figure_gate_counts.get('routed_candidates', 0)}")
        markdown.append(f"- after_gate: {figure_gate_counts.get('after_gate', 0)}")
        skipped = figure_gate_counts.get("skipped", {})
        if skipped:
            markdown.extend([f"- skipped:{key}: {value}" for key, value in sorted(skipped.items())])
    else:
        markdown.append("- none")
    markdown.append("")
    markdown.append("## Figure Triage Routes")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(figure_failure_summary["triage_route_counts"].items())])
    markdown.append("")
    markdown.append("## Figure Triage Signals")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(figure_failure_summary["triage_signals"].items())])
    markdown.append("")
    markdown.append("## Figure Digitization Statuses")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(figure_failure_summary["digitization_status_counts"].items())])
    markdown.append("")
    markdown.append("## Figure Mapping Statuses")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(figure_failure_summary["mapping_status_counts"].items())])
    markdown.append("")
    markdown.append("## LLM Reliability")
    if llm_reliability:
        for module, metrics in sorted(llm_reliability.items()):
            markdown.append(f"### {module}")
            markdown.extend(
                [
                    f"- {metric}: {value}"
                    for metric, value in sorted(metrics.items())
                    if metric != "model_name"
                ]
            )
    else:
        markdown.append("- none")
    markdown.append("")
    markdown.append("## LLM Adjudication Audit")
    markdown.append(f"- rows: {llm_adjudication_summary['row_count']}")
    markdown.extend(
        [f"- priority_bucket:{key}: {value}" for key, value in sorted(llm_adjudication_summary["priority_bucket_counts"].items())]
        or ["- priority_bucket:none"]
    )
    markdown.extend(
        [f"- review_focus:{key}: {value}" for key, value in sorted(llm_adjudication_summary["review_focus_counts"].items())]
        or ["- review_focus:none"]
    )
    markdown.extend(
        [f"- recommended_status:{key}: {value}" for key, value in sorted(llm_adjudication_summary["recommended_status_counts"].items())]
        or ["- none"]
    )
    markdown.extend(
        [f"- disagreement:{key}: {value}" for key, value in sorted(llm_adjudication_summary["disagreement_counts"].items())]
        or ["- disagreement:none"]
    )
    markdown.append("")
    markdown.append("## Prompt Assets")
    prompt_assets = manifest.stage_metrics.get("prompt_assets", {})
    markdown.extend([f"- {key}: {value}" for key, value in sorted(prompt_assets.items())] or ["- none"])
    markdown.append("")
    markdown.append("## Blockage Summary")
    markdown.append("### Access Statuses")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(blockage_summary["access_status_counts"].items())] or ["- none"])
    markdown.append("### Access Reasons")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(blockage_summary["access_reason_counts"].items())] or ["- none"])
    markdown.append("### Unresolved Route Reasons")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(blockage_summary["route_unresolved_reason_counts"].items())] or ["- none"])
    markdown.append("### Extractor Source / Error Blockages")
    for name, payload in sorted(blockage_summary["extractor_blockages"].items()):
        markdown.append(f"#### {name}")
        markdown.extend([f"- status:{key}: {value}" for key, value in sorted(payload["status_counts"].items())] or ["- status:none"])
        markdown.extend([f"- error_type:{key}: {value}" for key, value in sorted(payload["error_type_counts"].items())] or ["- error_type:none"])
        markdown.extend([f"- source_backend:{key}: {value}" for key, value in sorted(payload["source_backend_counts"].items())] or ["- source_backend:none"])
    markdown.append("### Patch Statuses")
    for patcher, counts in sorted(blockage_summary["patch_status_counts"].items()):
        markdown.append(f"#### {patcher}")
        markdown.extend([f"- {key}: {value}" for key, value in sorted(counts.items())] or ["- none"])
    markdown.append("")
    markdown.append("## Patch Success Counts")
    markdown.extend([f"- {key}: {value}" for key, value in sorted(patch_success_counts.items())])
    (out_dir / "run_report.md").write_text("\n".join(markdown), encoding="utf-8")

    return report
