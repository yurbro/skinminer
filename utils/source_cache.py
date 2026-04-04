"""Disciplined caching for remote structured source text."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


DEFAULT_SOURCE_CACHE_ROOT = Path("papers") / "source_cache"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cache_paths(cache_root: Path, namespace: str, url: str, suffix: str) -> tuple[Path, Path]:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    text_path = cache_root / namespace / f"{digest}{suffix}"
    meta_path = cache_root / namespace / f"{digest}.json"
    return text_path, meta_path


def _existing_cached_text_path(cache_root: Path, namespace: str, url: str) -> Path | None:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    namespace_dir = cache_root / namespace
    if not namespace_dir.exists():
        return None
    candidates = [
        path
        for path in sorted(namespace_dir.glob(f"{digest}.*"))
        if path.is_file() and path.suffix.lower() != ".json" and path.stat().st_size > 0
    ]
    return candidates[0] if candidates else None


def _suffix_for(url: str, content_type: str) -> str:
    lowered = f"{url} {content_type}".lower()
    if "xml" in lowered:
        return ".xml"
    if "html" in lowered or "htm" in lowered:
        return ".html"
    return ".txt"


def fetch_cached_text(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
    max_retries: int = 3,
    cache_root: str | Path = DEFAULT_SOURCE_CACHE_ROOT,
    namespace: str = "structured_text",
    allow_stale_on_error: bool = True,
) -> str:
    """Fetch remote text with stable on-disk caching by URL."""

    cache_root = Path(cache_root)
    fallback_text_path, fallback_meta_path = _cache_paths(cache_root, namespace, url, ".txt")
    cached_text_path = _existing_cached_text_path(cache_root, namespace, url)
    if cached_text_path is not None:
        return cached_text_path.read_text(encoding="utf-8", errors="ignore")

    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers or {}, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.encoding or response.apparent_encoding or "utf-8"
            text = response.text
            suffix = _suffix_for(url, response.headers.get("Content-Type", ""))
            text_path, meta_path = _cache_paths(cache_root, namespace, url, suffix)
            text_path.parent.mkdir(parents=True, exist_ok=True)
            text_path.write_text(text, encoding="utf-8")
            meta_path.write_text(
                json.dumps(
                    {
                        "url": url,
                        "namespace": namespace,
                        "cached_at_utc": _utc_now(),
                        "content_type": response.headers.get("Content-Type", ""),
                        "status_code": response.status_code,
                        "encoding": response.encoding,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            if text_path != fallback_text_path and fallback_text_path.exists():
                fallback_text_path.unlink(missing_ok=True)
            if meta_path != fallback_meta_path and fallback_meta_path.exists():
                fallback_meta_path.unlink(missing_ok=True)
            return text
        except Exception as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            time.sleep(min(5.0, 0.8 * attempt))

    stale_path = _existing_cached_text_path(cache_root, namespace, url)
    if allow_stale_on_error and stale_path is not None:
        fallback_meta_path.parent.mkdir(parents=True, exist_ok=True)
        fallback_meta_path.write_text(
            json.dumps(
                {
                    "url": url,
                    "namespace": namespace,
                    "last_error_type": type(last_exc).__name__ if last_exc else "RuntimeError",
                    "last_error": str(last_exc) if last_exc else "unknown",
                    "failed_at_utc": _utc_now(),
                    "stale_cache_used": True,
                    "stale_cache_path": str(stale_path),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return stale_path.read_text(encoding="utf-8", errors="ignore")

    fallback_meta_path.parent.mkdir(parents=True, exist_ok=True)
    fallback_meta_path.write_text(
        json.dumps(
            {
                "url": url,
                "namespace": namespace,
                "last_error_type": type(last_exc).__name__ if last_exc else "RuntimeError",
                "last_error": str(last_exc) if last_exc else "unknown",
                "failed_at_utc": _utc_now(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"Failed to fetch remote text from {url}")
