from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd
from pydantic import BaseModel

from schemas.models import Record


def ensure_parent(path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return out_path


def normalize_json_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [normalize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalize_json_value(item) for key, item in value.items()}
    return value


def write_jsonl(rows: Iterable[Mapping[str, Any] | BaseModel], path: str | Path) -> Path:
    out_path = ensure_parent(path)
    with out_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            payload = row.model_dump(mode="json") if isinstance(row, BaseModel) else dict(row)
            handle.write(json.dumps(normalize_json_value(payload), ensure_ascii=False) + "\n")
    return out_path


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def load_records_jsonl(path: str | Path) -> list[Record]:
    """Load canonical record JSONL into validated `Record` objects."""

    return [Record.model_validate(row) for row in load_jsonl(path)]


def write_optional_csv(rows: Iterable[Mapping[str, Any]], path: str | Path | None) -> Path | None:
    if path is None:
        return None
    out_path = ensure_parent(path)
    pd.DataFrame(list(rows)).to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


def make_paper_id(doi: str = "", title: str = "", fallback: str = "") -> str:
    base = (doi or "").strip().lower() or (title or "").strip().lower() or fallback.strip().lower()
    if not base:
        base = "paper"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    return f"paper_{digest}"


def make_record_id(paper_id: str, route: str, formulation_label: str = "", suffix: str = "") -> str:
    base = "::".join([paper_id, route, formulation_label.strip().lower(), suffix.strip().lower()])
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    return f"record_{digest}"


def flatten_record(record: Record | Mapping[str, Any]) -> dict[str, Any]:
    """Flatten a canonical record for optional CSV export views."""

    payload = record.model_dump(mode="json") if isinstance(record, Record) else dict(record)
    formulation = payload.get("formulation", {}) or {}
    endpoint = payload.get("endpoint", {}) or {}
    conditions = payload.get("conditions", {}) or {}
    provenance = payload.get("provenance", {}) or {}
    return {
        "record_id": payload.get("record_id"),
        "paper_id": payload.get("paper_id"),
        "doi": payload.get("doi", ""),
        "route": payload.get("route", ""),
        "route_confidence": payload.get("route_confidence"),
        "extractor_confidence": payload.get("extractor_confidence"),
        "mapping_confidence": payload.get("mapping_confidence"),
        "study_type": payload.get("study_type", ""),
        "device": payload.get("device", ""),
        "barrier": payload.get("barrier", ""),
        "formulation_label": formulation.get("label", ""),
        "api_name": formulation.get("api_name", ""),
        "api_concentration_value": formulation.get("api_concentration_value"),
        "api_concentration_unit": formulation.get("api_concentration_unit", ""),
        "api_basis": formulation.get("api_basis", ""),
        "api_concentration_raw": formulation.get("api_concentration_raw", ""),
        "dosage_form": formulation.get("dosage_form", ""),
        "components_json": json.dumps(formulation.get("components", []), ensure_ascii=False),
        "endpoint_field_name": endpoint.get("field_name", ""),
        "endpoint_kind": endpoint.get("kind", ""),
        "endpoint_value": endpoint.get("value"),
        "endpoint_unit": endpoint.get("unit", ""),
        "endpoint_time_value": endpoint.get("time_value"),
        "endpoint_time_unit": endpoint.get("time_unit", ""),
        "endpoint_normalized_value": endpoint.get("normalized_value"),
        "endpoint_normalized_unit": endpoint.get("normalized_unit", ""),
        "diffusion_area_cm2": conditions.get("diffusion_area_cm2"),
        "receptor_volume_ml": conditions.get("receptor_volume_ml"),
        "duration_h": conditions.get("duration_h"),
        "verification_status": payload.get("verification_status", ""),
        "scope_bucket": payload.get("scope_bucket", ""),
        "scope_tags_json": json.dumps(payload.get("scope_tags", []), ensure_ascii=False),
        "verification_support_rate": payload.get("verification_support_rate"),
        "failure_reason": payload.get("failure_reason"),
        "failure_reasons_json": json.dumps(payload.get("failure_reasons", []), ensure_ascii=False),
        "evidence_count": len(payload.get("evidence_items", [])),
        "patch_count": len(payload.get("patches", [])),
        "extractor_name": provenance.get("extractor_name", ""),
        "source_format": provenance.get("source_format", ""),
        "source_path": provenance.get("source_path", ""),
        "artifact_paths_json": json.dumps(provenance.get("artifact_paths", []), ensure_ascii=False),
        "provenance_json": json.dumps(provenance, ensure_ascii=False),
        "evidence_json": json.dumps(payload.get("evidence_items", []), ensure_ascii=False),
        "patches_json": json.dumps(payload.get("patches", []), ensure_ascii=False),
        "source_notes_json": json.dumps(payload.get("source_notes", []), ensure_ascii=False),
    }


def write_records_jsonl(records: Iterable[Record], path: str | Path) -> Path:
    return write_jsonl(records, path)


def write_records_csv(records: Iterable[Record], path: str | Path) -> Path:
    """Write a flat CSV view from canonical record objects."""

    rows = [flatten_record(record) for record in records]
    out_path = ensure_parent(path)
    pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


def sanitize_filename(value: str, max_len: int = 120) -> str:
    clean = re.sub(r"[^a-zA-Z0-9._-]+", "_", (value or "").strip())
    clean = clean.strip("._")
    return clean[:max_len] or "artifact"
