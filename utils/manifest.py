from __future__ import annotations

from importlib import metadata
from pathlib import Path
import sys
from typing import Iterable
from uuid import uuid4

from schemas.models import RunManifest
from utils.io import ensure_parent, write_jsonl


def _safe_version(distribution: str) -> str:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return "not-installed"


def create_run_manifest(
    model_name: str,
    policy_name: str,
    input_paths: Iterable[str],
    llm_provider: str = "openai",
    prompt_paths: Iterable[str] | None = None,
    config_paths: Iterable[str] | None = None,
    notes: Iterable[str] | None = None,
) -> RunManifest:
    module_notes = {
        "python": sys.version.split()[0],
        "openai": _safe_version("openai"),
        "anthropic": _safe_version("anthropic"),
        "pandas": _safe_version("pandas"),
        "pydantic": _safe_version("pydantic"),
        "PyMuPDF": _safe_version("PyMuPDF"),
        "opencv-python": _safe_version("opencv-python"),
    }
    module_notes = {key: value for key, value in module_notes.items() if value}
    return RunManifest(
        run_id=f"run_{uuid4().hex[:12]}",
        model_name=model_name,
        llm_provider=llm_provider,
        policy_name=policy_name,
        input_paths=[str(Path(path)) for path in input_paths if path],
        prompt_paths=[str(Path(path)) for path in prompt_paths or [] if path],
        config_paths=[str(Path(path)) for path in config_paths or [] if path],
        module_notes=module_notes,
        notes=list(notes or []),
    )


def write_manifest(manifest: RunManifest, path: str | Path) -> Path:
    out_path = ensure_parent(path)
    write_jsonl([manifest], out_path)
    return out_path
