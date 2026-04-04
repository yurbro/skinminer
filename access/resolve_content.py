from __future__ import annotations

import hashlib
import logging
import re
import time
from pathlib import Path
from typing import Any, Iterable, Mapping

import requests

from schemas.models import ContentAccess
from utils.io import make_paper_id, sanitize_filename, write_jsonl, write_optional_csv
from utils.resume import load_typed_jsonl_if_exists
from utils.status_panel import ProgressCallback

EUROPE_PMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UNPAYWALL_API = "https://api.unpaywall.org/v2"
USER_AGENT = {"User-Agent": "SkinMiner/round1-refactor (OA content resolver)"}
LOGGER = logging.getLogger("skinminer.access")


def _requests_get_with_retries(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: int = 40,
    stream: bool = False,
    allow_redirects: bool = True,
    max_retries: int = 4,
) -> requests.Response:
    """Issue a GET request with lightweight retry/backoff for unstable OA endpoints."""

    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                stream=stream,
                allow_redirects=allow_redirects,
            )
            if response.status_code in {408, 425, 429, 500, 502, 503, 504} and attempt < max_retries:
                response.close()
                raise requests.HTTPError(f"retryable_status:{response.status_code}")
            return response
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= max_retries:
                break
            time.sleep(min(8.0, 0.8 * attempt))
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"Failed GET request: {url}")


def _normalize_style(url: str, style: str) -> str | None:
    raw = f"{style} {url}".lower()
    if "xml" in raw:
        return "pmc_xml"
    if "html" in raw or "fulltext" in raw:
        return "html"
    if "pdf" in raw:
        return "pdf"
    return None


def _lookup_epmc(doi: str, pmid: str) -> dict[str, Any]:
    if not doi and not pmid:
        return {}
    query = f'DOI:"{doi}"' if doi else f'EXT_ID:"{pmid}"'
    response = _requests_get_with_retries(
        EUROPE_PMC_SEARCH,
        params={"query": query, "format": "json", "pageSize": 1, "resultType": "core"},
        headers=USER_AGENT,
        timeout=40,
    )
    response.raise_for_status()
    results = response.json().get("resultList", {}).get("result", [])
    return results[0] if results else {}


def _lookup_unpaywall_pdf(doi: str, email: str | None) -> str | None:
    if not doi or not email:
        return None
    response = _requests_get_with_retries(
        f"{UNPAYWALL_API}/{doi}",
        params={"email": email},
        headers=USER_AGENT,
        timeout=40,
    )
    if response.status_code != 200:
        return None
    payload = response.json()
    location = payload.get("best_oa_location") or {}
    return location.get("url_for_pdf")


def _download_asset(url: str, destination: Path) -> bool:
    response = _requests_get_with_retries(
        url,
        headers=USER_AGENT,
        timeout=60,
        stream=True,
        allow_redirects=True,
        max_retries=4,
    )
    if response.status_code != 200:
        response.close()
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=1024 * 64):
            if chunk:
                handle.write(chunk)
    response.close()
    return destination.exists() and destination.stat().st_size > 0


def _materialize_asset(url: str, destination: Path) -> tuple[bool, str]:
    """Reuse a local artifact when present, otherwise download it."""

    if destination.exists() and destination.stat().st_size > 0:
        return True, "reused_local"
    downloaded = _download_asset(url, destination)
    return (downloaded, "downloaded" if downloaded else "failed")


def _build_local_path(content_root: Path, paper_id: str, fmt: str, doi: str) -> Path:
    suffix = {"pmc_xml": ".xml", "html": ".html", "pdf": ".pdf"}[fmt]
    stem = sanitize_filename(doi or paper_id)
    digest = hashlib.sha1(f"{paper_id}:{fmt}:{doi}".encode("utf-8")).hexdigest()[:10]
    return content_root / fmt / f"{stem}__{digest}{suffix}"


def resolve_content_for_paper(
    row: Mapping[str, Any],
    content_root: str | Path = "papers",
    unpaywall_email: str | None = None,
    download: bool = False,
    require_legacy_pdf: bool = False,
) -> ContentAccess:
    doi = str(row.get("doi", "") or "").strip().lower()
    pmid = str(row.get("pmid", "") or "").strip()
    title = str(row.get("title", "") or "").strip()
    paper_id = str(row.get("paper_id") or make_paper_id(doi=doi, title=title, fallback=pmid or title))
    access_urls: dict[str, str] = {}
    local_paths: dict[str, str] = {}
    notes: list[str] = []

    if str(row.get("url", "") or "").lower().endswith(".pdf"):
        access_urls["pdf"] = str(row.get("url", "")).strip()
        notes.append("seed_pdf_url_from_metadata")

    epmc_result = _lookup_epmc(doi, pmid)
    pmcid = str(epmc_result.get("pmcid", "") or "")
    fulltext_items = epmc_result.get("fullTextUrlList", {}).get("fullTextUrl", []) or []
    for item in fulltext_items:
        url = str(item.get("url", "") or "").strip()
        fmt = _normalize_style(url, str(item.get("documentStyle", "") or ""))
        if fmt and url and fmt not in access_urls:
            access_urls[fmt] = url

    if "pdf" not in access_urls:
        unpaywall_pdf = _lookup_unpaywall_pdf(doi, unpaywall_email)
        if unpaywall_pdf:
            access_urls["pdf"] = unpaywall_pdf
            notes.append("pdf_url_from_unpaywall")

    available_formats = [fmt for fmt in ["pmc_xml", "html", "pdf"] if fmt in access_urls]
    preferred_format = available_formats[0] if available_formats else "unresolved"
    status = "resolved" if preferred_format != "unresolved" else "unresolved"
    content_dir = Path(content_root)

    if download and preferred_format != "unresolved":
        preferred_path = _build_local_path(content_dir, paper_id, preferred_format, doi)
        materialized, action = _materialize_asset(access_urls[preferred_format], preferred_path)
        if materialized:
            local_paths[preferred_format] = str(preferred_path)
            status = "downloaded"
            if action == "reused_local":
                notes.append(f"reused_local:{preferred_format}")
        else:
            notes.append(f"failed_download:{preferred_format}")
            status = "error"

    if require_legacy_pdf and "pdf" in access_urls and "pdf" not in local_paths:
        pdf_path = _build_local_path(content_dir, paper_id, "pdf", doi)
        materialized, action = _materialize_asset(access_urls["pdf"], pdf_path)
        if materialized:
            local_paths["pdf"] = str(pdf_path)
            status = "downloaded"
            if action == "reused_local":
                notes.append("legacy_pdf_reused_local")
            elif download:
                notes.append("legacy_pdf_fallback_downloaded")
            else:
                notes.append("legacy_pdf_auto_downloaded")
        else:
            notes.append("failed_download:pdf")
            if status == "unresolved":
                status = "error"

    return ContentAccess(
        paper_id=paper_id,
        doi=doi,
        pmid=pmid,
        pmcid=pmcid,
        title=title,
        preferred_format=preferred_format,
        available_formats=available_formats,
        access_urls=access_urls,
        local_paths=local_paths,
        status=status,
        notes=notes,
    )


def resolve_content_batch(
    rows: Iterable[Mapping[str, Any]],
    content_root: str | Path = "papers",
    unpaywall_email: str | None = None,
    download: bool = False,
    require_legacy_pdf: bool = False,
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
    progress_every: int = 25,
    checkpoint_every: int = 25,
    progress_callback: ProgressCallback | None = None,
    resume_jsonl: str | Path | None = None,
) -> list[ContentAccess]:
    row_list = list(rows)
    total = len(row_list)
    started_at = time.perf_counter()
    progress_every = max(1, progress_every)
    checkpoint_every = max(1, checkpoint_every)
    existing_items = load_typed_jsonl_if_exists(resume_jsonl, ContentAccess)
    existing_map = {item.paper_id: item for item in existing_items}
    ordered_paper_ids = [
        str(row.get("paper_id") or make_paper_id(
            doi=str(row.get("doi", "") or "").strip().lower(),
            title=str(row.get("title", "") or "").strip(),
            fallback=str(row.get("pmid", "") or "").strip() or str(row.get("title", "") or "").strip(),
        ))
        for row in row_list
    ]
    resolved_map: dict[str, ContentAccess] = {paper_id: existing_map[paper_id] for paper_id in ordered_paper_ids if paper_id in existing_map}
    completed_before = len(resolved_map)

    LOGGER.info(
        "Starting OA content resolution for %s papers (download=%s, require_legacy_pdf=%s)",
        total,
        download,
        require_legacy_pdf,
    )
    if progress_callback and completed_before:
        progress_callback(completed_before, "resume", f"loaded={completed_before}")

    remaining_rows = [row for row, paper_id in zip(row_list, ordered_paper_ids, strict=False) if paper_id not in resolved_map]
    for remaining_index, row in enumerate(remaining_rows, start=1):
        doi = str(row.get("doi", "") or "").strip().lower()
        pmid = str(row.get("pmid", "") or "").strip()
        title = str(row.get("title", "") or "").strip()
        paper_id = str(row.get("paper_id") or make_paper_id(doi=doi, title=title, fallback=pmid or title))
        completed_so_far = completed_before + remaining_index - 1
        current_item = paper_id or doi or title[:60] or f"row_{completed_so_far + 1}"

        if progress_callback:
            progress_callback(completed_so_far, current_item, "resolving OA access")

        try:
            item = resolve_content_for_paper(
                row,
                content_root=content_root,
                unpaywall_email=unpaywall_email,
                download=download,
                require_legacy_pdf=require_legacy_pdf,
            )
        except Exception as exc:
            LOGGER.exception("Content resolution failed for paper_id=%s doi=%s", paper_id, doi)
            item = ContentAccess(
                paper_id=paper_id,
                doi=doi,
                pmid=pmid,
                title=title,
                status="error",
                notes=[f"resolve_error:{type(exc).__name__}"],
            )

        resolved_map[paper_id] = item
        completed_total = completed_so_far + 1
        if progress_callback:
            progress_callback(completed_total, current_item, f"status={item.status} formats={','.join(item.available_formats) or '-'}")

        if output_jsonl and (completed_total % checkpoint_every == 0 or completed_total == total):
            ordered_resolved = [resolved_map[paper_id] for paper_id in ordered_paper_ids if paper_id in resolved_map]
            write_jsonl(ordered_resolved, output_jsonl)

        if completed_total % progress_every == 0 or completed_total == total:
            elapsed = time.perf_counter() - started_at
            resolved = list(resolved_map.values())
            resolved_count = sum(entry.status == "resolved" for entry in resolved)
            downloaded_count = sum(entry.status == "downloaded" for entry in resolved)
            unresolved_count = sum(entry.status == "unresolved" for entry in resolved)
            error_count = sum(entry.status == "error" for entry in resolved)
            LOGGER.info(
                "Content resolution progress %s/%s (resolved=%s downloaded=%s unresolved=%s error=%s elapsed=%.1fs)",
                completed_total,
                total,
                resolved_count,
                downloaded_count,
                unresolved_count,
                error_count,
                elapsed,
            )

    ordered_resolved = [resolved_map[paper_id] for paper_id in ordered_paper_ids if paper_id in resolved_map]
    if output_jsonl:
        write_jsonl(ordered_resolved, output_jsonl)
    if output_csv:
        write_optional_csv([item.model_dump(mode="json") for item in ordered_resolved], output_csv)
    return ordered_resolved
