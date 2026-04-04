from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, TypeVar

from pydantic import BaseModel

from utils.io import ensure_parent, load_jsonl, load_records_jsonl, normalize_json_value

TModel = TypeVar("TModel", bound=BaseModel)


def jsonl_exists(path: str | Path | None) -> bool:
    """Return True when a JSONL path exists on disk."""

    return bool(path) and Path(path).exists()


def load_jsonl_if_exists(path: str | Path | None) -> list[dict[str, Any]]:
    """Load a JSONL file when present, otherwise return an empty list."""

    if not jsonl_exists(path):
        return []
    return load_jsonl(Path(path))


def load_typed_jsonl_if_exists(path: str | Path | None, model_cls: type[TModel]) -> list[TModel]:
    """Load and validate JSONL rows into the provided Pydantic model type."""

    return [model_cls.model_validate(row) for row in load_jsonl_if_exists(path)]


def load_record_jsonl_if_exists(path: str | Path | None) -> list:
    """Load canonical Record JSONL when present, otherwise return an empty list."""

    if not jsonl_exists(path):
        return []
    return load_records_jsonl(Path(path))


def has_expected_row_count(path: str | Path | None, expected_count: int) -> bool:
    """Return True when an existing JSONL file has exactly the expected row count."""

    if not jsonl_exists(path):
        return False
    return len(load_jsonl(Path(path))) == expected_count


def stage_marker_path(output_dir: str | Path, stage_key: str) -> Path:
    """Return the stage-completion marker path used by resume mode."""

    return Path(output_dir) / ".resume" / f"{stage_key}.done.json"


def load_stage_marker(output_dir: str | Path, stage_key: str) -> dict[str, Any]:
    """Load a stage-completion marker payload when present."""

    marker_path = stage_marker_path(output_dir, stage_key)
    if not marker_path.exists():
        return {}
    return json.loads(marker_path.read_text(encoding="utf-8"))


def stage_is_done(output_dir: str | Path, stage_key: str) -> bool:
    """Return True when a stage completion marker exists."""

    return stage_marker_path(output_dir, stage_key).exists()


def clear_stage_marker(output_dir: str | Path, stage_key: str) -> None:
    """Remove an existing stage marker before rerunning a stage."""

    marker_path = stage_marker_path(output_dir, stage_key)
    if marker_path.exists():
        marker_path.unlink()


def _file_fingerprint(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    payload: dict[str, Any] = {"path": str(candidate)}
    if not candidate.exists():
        payload["exists"] = False
        return payload
    stat = candidate.stat()
    payload.update(
        {
            "exists": True,
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        }
    )
    return payload


def build_resume_signature(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a stable digest for resume compatibility checks."""

    normalized_payload = normalize_json_value(dict(payload))
    encoded = json.dumps(normalized_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return {
        "digest": hashlib.sha1(encoded).hexdigest(),
        "payload": normalized_payload,
    }


def build_file_fingerprints(paths: list[str | Path]) -> list[dict[str, Any]]:
    """Return lightweight fingerprints for input, prompt, or config files."""

    return [_file_fingerprint(path) for path in paths]


def stage_marker_matches_signature(output_dir: str | Path, stage_key: str, resume_signature: Mapping[str, Any]) -> bool:
    """Return whether a stage marker matches the expected resume signature."""

    marker = load_stage_marker(output_dir, stage_key)
    if not marker:
        return False
    return marker.get("resume_signature_digest") == resume_signature.get("digest")


def validate_existing_stage_markers(output_dir: str | Path, resume_signature: Mapping[str, Any]) -> list[str]:
    """Return stage keys whose existing markers are incompatible with the current resume signature."""

    resume_dir = Path(output_dir) / ".resume"
    if not resume_dir.exists():
        return []
    incompatible: list[str] = []
    for marker_path in sorted(resume_dir.glob("*.done.json")):
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        if marker.get("resume_signature_digest") != resume_signature.get("digest"):
            incompatible.append(marker_path.stem.removesuffix(".done"))
    return incompatible


def mark_stage_done(output_dir: str | Path, stage_key: str, payload: dict[str, Any] | None = None) -> Path:
    """Write a stage completion marker for checkpoint resume."""

    marker_path = ensure_parent(stage_marker_path(output_dir, stage_key))
    marker_path.write_text(
        json.dumps(normalize_json_value(payload or {}), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return marker_path
