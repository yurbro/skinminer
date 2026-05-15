"""Metadata extraction for user-supplied PDF entry points."""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal

import fitz
from pydantic import BaseModel, ConfigDict, Field

from utils.io import make_paper_id
from utils.llm_client import LLMProvider, ParsedLLMResponse, default_model_for_provider, parse_structured

LOGGER = logging.getLogger("skinminer.corpus.pdf_metadata")

PDF_METADATA_PROMPT_ASSET_ID = "corpus.pdf_metadata"
PDF_METADATA_PROMPT_VERSION = "2026-05-10.v1"
CORPUS_COLUMNS = [
    "source",
    "id",
    "pmid",
    "pmcid",
    "doi",
    "title",
    "abstract",
    "year",
    "journal",
    "authors",
    "url",
    "query_used",
]

SYSTEM_PROMPT = (
    "You are extracting bibliographic metadata from a scientific paper PDF.\n"
    "Output strict JSON with these keys: doi, title, year, journal, authors, abstract.\n"
    "Rules:\n"
    "- doi: lowercase, no surrounding whitespace. Empty string if not found.\n"
    "- title: as printed on the paper, no truncation.\n"
    "- year: integer; null if not extractable.\n"
    "- journal: full name if available, else publication venue.\n"
    "- authors: list of strings, in order of appearance.\n"
    "- abstract: the paper's abstract verbatim. Critical for downstream pipeline.\n"
    "  If missing, return empty string (do not summarize).\n"
    "- Do not include any text outside the JSON object."
)


class PdfMetadataError(RuntimeError):
    """Raised when a PDF cannot be parsed or LLM metadata extraction cannot run."""


@dataclass(frozen=True)
class PdfInputRow:
    """One row from a user PDF CSV."""

    local_pdf_path: Path
    user_doi_hint: str = ""
    user_title_hint: str = ""


class PdfMetadataLLMResponse(BaseModel):
    """Structured LLM response for PDF bibliographic metadata."""

    model_config = ConfigDict(extra="forbid")

    doi: str = ""
    title: str = ""
    year: int | None = None
    journal: str = ""
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""


class PdfMetadata(BaseModel):
    """Cached metadata for a user-supplied PDF."""

    model_config = ConfigDict(extra="forbid")

    doi: str = ""
    title: str = ""
    year: int | None = None
    journal: str = ""
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    source_pdf_path: str = ""
    source_pdf_sha1: str = ""
    extraction_method: Literal["cache", "llm", "user_hint", "fallback"] = "fallback"
    llm_model_used: str = ""
    warnings: list[str] = Field(default_factory=list)


LLMClient = Callable[..., ParsedLLMResponse[PdfMetadataLLMResponse]]


def metadata_cache_path(pdf_path: Path) -> Path:
    """Return the sibling cache path for a PDF."""

    return Path(f"{pdf_path}.metadata.json")


def read_pdf_input_csv(path: Path) -> list[PdfInputRow]:
    """Read the PR-B user PDF CSV format."""

    csv_path = Path(path)
    rows: list[PdfInputRow] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "local_pdf_path" not in reader.fieldnames:
            raise ValueError("PDF CSV must include a local_pdf_path column")
        for index, row in enumerate(reader, start=2):
            raw_pdf_path = str(row.get("local_pdf_path", "") or "").strip()
            if not raw_pdf_path:
                raise ValueError(f"PDF CSV row {index} is missing local_pdf_path")
            pdf_path = _resolve_pdf_path(raw_pdf_path, csv_path.parent)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF CSV row {index} path does not exist: {pdf_path}")
            rows.append(
                PdfInputRow(
                    local_pdf_path=pdf_path,
                    user_doi_hint=str(row.get("user_doi_hint", "") or "").strip(),
                    user_title_hint=str(row.get("user_title_hint", "") or "").strip(),
                )
            )
    return rows


def extract_pdf_metadata(
    pdf_path: Path,
    user_doi_hint: str | None = None,
    user_title_hint: str | None = None,
    use_cache: bool = True,
    llm_client: LLMClient | None = None,
    llm_provider: str | LLMProvider | None = None,
    model: str | None = None,
    max_retries: int = 2,
) -> PdfMetadata:
    """
    Extract bibliographic metadata from a user-supplied PDF.

    Returns metadata with fields needed to construct a standard SkinMiner corpus
    row. The cache path is `<pdf_path>.metadata.json`.
    """

    pdf_path = Path(pdf_path)
    doi_hint = _normalize_doi(user_doi_hint)
    title_hint = str(user_title_hint or "").strip()
    cache_path = metadata_cache_path(pdf_path)
    source_sha1 = _file_sha1(pdf_path)

    if use_cache and cache_path.exists():
        cached = PdfMetadata.model_validate(json.loads(cache_path.read_text(encoding="utf-8")))
        cached = cached.model_copy(update={"extraction_method": "cache"})
        cached = _apply_user_hints(cached, doi_hint=doi_hint, title_hint=title_hint)
        if cached.extraction_method == "user_hint":
            _write_metadata_cache(cached, cache_path)
        return cached

    first_pages_text = extract_first_pages_text(pdf_path, max_pages=2)
    if not first_pages_text.strip():
        metadata = _fallback_metadata(
            pdf_path=pdf_path,
            source_sha1=source_sha1,
            doi_hint=doi_hint,
            title_hint=title_hint,
            warning="no_text_extracted_from_first_pages",
        )
        _write_metadata_cache(metadata, cache_path)
        return metadata

    provider = LLMProvider.parse(llm_provider)
    model_name = model or default_model_for_provider(provider)
    client = llm_client or parse_structured
    user_prompt = _build_user_prompt(pdf_path, first_pages_text)

    attempt = 0
    last_exc: Exception | None = None
    while attempt <= max_retries:
        try:
            response = client(
                provider=provider,
                model=model_name,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                text_format=PdfMetadataLLMResponse,
                timeout=60,
            )
            metadata = _metadata_from_llm_response(
                response.output_parsed,
                pdf_path=pdf_path,
                source_sha1=source_sha1,
                model_name=model_name,
            )
            metadata = _apply_user_hints(metadata, doi_hint=doi_hint, title_hint=title_hint)
            if not metadata.abstract.strip():
                metadata.warnings.append("empty_abstract")
                LOGGER.warning("PDF metadata abstract is empty for %s", pdf_path)
            _write_metadata_cache(metadata, cache_path)
            return metadata
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if _is_timeout_exception(exc) and attempt >= max_retries:
                raise PdfMetadataError(f"LLM metadata extraction timed out for {pdf_path}") from exc
            if not _is_timeout_exception(exc) and attempt >= max_retries:
                LOGGER.warning("Falling back after invalid LLM metadata for %s: %s", pdf_path, exc)
                metadata = _fallback_metadata(
                    pdf_path=pdf_path,
                    source_sha1=source_sha1,
                    doi_hint=doi_hint,
                    title_hint=title_hint,
                    warning=f"invalid_llm_metadata:{type(exc).__name__}",
                )
                _write_metadata_cache(metadata, cache_path)
                return metadata
            attempt += 1
            _backoff_sleep(attempt)

    raise PdfMetadataError(f"LLM metadata extraction failed for {pdf_path}: {last_exc}")


def extract_first_pages_text(pdf_path: Path, max_pages: int = 2) -> str:
    """Extract plain text from the first pages of a normal text PDF."""

    try:
        document = fitz.open(pdf_path)
    except Exception as exc:  # noqa: BLE001
        raise PdfMetadataError(f"Could not open PDF: {pdf_path}") from exc
    try:
        if getattr(document, "is_encrypted", False):
            raise PdfMetadataError(f"PDF is encrypted: {pdf_path}")
        page_texts: list[str] = []
        for page_index in range(min(max_pages, document.page_count)):
            page_texts.append(document.load_page(page_index).get_text("text") or "")
        return "\n\n".join(page_texts)
    except PdfMetadataError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise PdfMetadataError(f"Could not extract text from PDF: {pdf_path}") from exc
    finally:
        document.close()


def build_corpus_from_metadata(
    metadata_records: list[PdfMetadata],
    *,
    query_used: str = "user_upload_pdf",
) -> list[dict[str, Any]]:
    """Build standard SkinMiner corpus rows from PDF metadata."""

    rows: list[dict[str, Any]] = []
    for metadata in metadata_records:
        paper_id = make_paper_id(
            doi=metadata.doi,
            title=metadata.title,
            fallback=metadata.source_pdf_path,
        )
        row = {
            "source": "USER_PDF",
            "id": paper_id,
            "pmid": "",
            "pmcid": "",
            "doi": metadata.doi,
            "title": metadata.title,
            "abstract": metadata.abstract,
            "year": metadata.year if metadata.year is not None else "",
            "journal": metadata.journal,
            "authors": ", ".join(metadata.authors),
            "url": metadata.source_pdf_path,
            "query_used": query_used,
        }
        rows.append({column: row.get(column, "") for column in CORPUS_COLUMNS})
    return rows


def _resolve_pdf_path(raw_pdf_path: str, csv_parent: Path) -> Path:
    candidate = Path(raw_pdf_path).expanduser()
    if candidate.is_absolute() or candidate.exists():
        return candidate
    csv_relative = csv_parent / candidate
    if csv_relative.exists():
        return csv_relative
    return candidate


def _build_user_prompt(pdf_path: Path, first_pages_text: str) -> str:
    return (
        f"PDF_PATH: {pdf_path}\n"
        "Extract only bibliographic metadata from the following text from the first two PDF pages.\n\n"
        f"PDF_TEXT:\n{first_pages_text[:24000]}"
    )


def _metadata_from_llm_response(
    payload: PdfMetadataLLMResponse,
    *,
    pdf_path: Path,
    source_sha1: str,
    model_name: str,
) -> PdfMetadata:
    return PdfMetadata(
        doi=_normalize_doi(payload.doi),
        title=" ".join((payload.title or "").split()),
        year=payload.year,
        journal=" ".join((payload.journal or "").split()),
        authors=[" ".join(str(author).split()) for author in payload.authors if str(author).strip()],
        abstract=(payload.abstract or "").strip(),
        source_pdf_path=str(pdf_path),
        source_pdf_sha1=source_sha1,
        extraction_method="llm",
        llm_model_used=model_name,
    )


def _apply_user_hints(metadata: PdfMetadata, *, doi_hint: str, title_hint: str) -> PdfMetadata:
    updates: dict[str, Any] = {}
    if doi_hint:
        updates["doi"] = doi_hint
    if title_hint:
        updates["title"] = title_hint
    if not updates:
        return metadata
    warnings = list(metadata.warnings)
    warnings.append("user_hint_applied")
    updates["warnings"] = warnings
    updates["extraction_method"] = "user_hint"
    return metadata.model_copy(update=updates)


def _fallback_metadata(
    *,
    pdf_path: Path,
    source_sha1: str,
    doi_hint: str,
    title_hint: str,
    warning: str,
) -> PdfMetadata:
    fallback_doi = doi_hint or f"{source_sha1[:12]}fallback"
    return PdfMetadata(
        doi=_normalize_doi(fallback_doi),
        title=title_hint or pdf_path.stem.replace("_", " "),
        year=None,
        journal="",
        authors=[],
        abstract="",
        source_pdf_path=str(pdf_path),
        source_pdf_sha1=source_sha1,
        extraction_method="fallback" if not (doi_hint or title_hint) else "user_hint",
        llm_model_used="",
        warnings=[warning],
    )


def _write_metadata_cache(metadata: PdfMetadata, cache_path: Path) -> None:
    cache_path.write_text(
        json.dumps(metadata.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _normalize_doi(value: str | None) -> str:
    return str(value or "").strip().lower()


def _file_sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_timeout_exception(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    detail = str(exc).lower()
    return "timeout" in name or "timed out" in detail


def _backoff_sleep(attempt: int) -> None:
    time.sleep(min(10.0, (2**attempt) * 0.5) + random.random() * 0.25)
