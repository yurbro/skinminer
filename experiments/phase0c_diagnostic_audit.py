from __future__ import annotations

"""Phase 0c deterministic diagnostic audit.

No LLM calls and no pipeline reruns are made by this script.

Track B composition-field audit uses the existing structured component-list fields:
- top-level ``components``
- nested ``formulation.components``

Both are read because Phase 0b's union file preserves records from multiple pipeline
artifacts whose flattened and canonical component fields differ slightly.
"""

import csv
import hashlib
import json
import math
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
FULL_RUN_DIR = ROOT / "outputs" / "full_run_16_post_all_fixes"
PHASE0A_TRACK_B = ROOT / "outputs" / "phase0a" / "track_b_ibuprofen_gel" / "deduplicated_papers.jsonl"
PHASE0B_DIR = ROOT / "outputs" / "phase0b_stage1"
OUT_DIR = ROOT / "outputs" / "phase0c"
CACHE_DIR = OUT_DIR / "api_cache"
REPORT_PATH = ROOT / "reports" / "phase0c_diagnostic_audit.md"

NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "skinminer-codex@example.com")
USER_AGENT = f"skinminer-phase0c-diagnostic/1.0 (mailto:{NCBI_EMAIL})"

EPMC_SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CROSSREF_WORKS_URL = "https://api.crossref.org/works"

GPT5_INPUT_PRICE_PER_MTOK = 2.50
CLAUDE_SONNET_INPUT_PRICE_PER_MTOK = 3.00
PRICING_NOTE = (
    "Input-token cost only; assumes OpenAI GPT-5.4 input at $2.50/M tokens "
    "and Claude Sonnet 4.5 input at $3.00/M tokens from official pricing pages "
    "checked on 2026-04-30: https://openai.com/api/pricing/ and "
    "https://platform.claude.com/docs/en/about-claude/pricing."
)


LIKELY_SUBSCRIBED_PUBLISHERS = [
    "Elsevier",
    "Wiley",
    "Wiley-Blackwell",
    "Springer",
    "Springer Nature",
    "Nature",
    "Taylor & Francis",
    "Informa UK",
    "American Chemical Society",
    "ACS",
    "Royal Society of Chemistry",
    "RSC",
    "SAGE",
    "Oxford University Press",
    "Cambridge University Press",
    "AAPS",
]

POSSIBLY_SUBSCRIBED_PUBLISHERS = [
    "Bentham",
    "Hindawi",
    "Karger",
    "Thieme",
    "Dove",
]


TRACK_A_FIELDS = [
    "doi",
    "title",
    "journal",
    "publisher",
    "year",
    "subscription_tier",
    "original_block_reason",
    "current_oa_status",
    "oa_url_if_any",
    "priority_rank",
]

TRACK_B_FIELDS = [
    "doi",
    "n_records_total",
    "pct_records_with_numeric_composition",
    "pct_records_with_components_list",
    "n_distinct_numeric_component_values",
    "provenance_mix",
    "re_extraction_potential",
    "expected_lift_class",
    "est_llm_input_tokens",
]

TRACK_C_FIELDS = [
    "doi",
    "title",
    "journal",
    "year",
    "miss_reason",
    "phase0a_oa",
]


def log(message: str) -> None:
    print(message, flush=True)


def normalize_doi(value: Any) -> str:
    if value is None:
        return ""
    doi = str(value).strip()
    if not doi or doi.lower() == "nan":
        return ""
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.strip().strip(".").lower()


def normalize_space(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.lower() == "nan":
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_year(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    return int(match.group(0)) if match else None


def make_paper_id(doi: str = "", title: str = "", fallback: str = "") -> str:
    base = (doi or "").strip().lower() or (title or "").strip().lower() or fallback.strip().lower()
    if not base:
        base = "paper"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    return f"paper_{digest}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def cache_path(prefix: str, key: str) -> Path:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{prefix}_{digest}.json"


class HttpClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def get_json(self, url: str, params: dict[str, Any] | None = None, timeout: int = 60) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(6):
            try:
                response = self.session.get(url, params=params, timeout=timeout)
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise requests.HTTPError(f"transient {response.status_code}", response=response)
                response.raise_for_status()
                return response.json()
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
                last_exc = exc
                wait = min(60, 1.5 * (2**attempt))
                log(f"  retrying after {wait:.1f}s: {url}")
                time.sleep(wait)
        assert last_exc is not None
        raise last_exc


HTTP = HttpClient()


def cached_json(prefix: str, key: str, fetcher) -> dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = cache_path(prefix, key)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    data = fetcher()
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return data


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def crossref_year(item: dict[str, Any]) -> int | None:
    for key in ["published-print", "published-online", "published", "issued"]:
        parts = (item.get(key) or {}).get("date-parts")
        if parts and parts[0]:
            return parse_year(parts[0][0])
    return None


def crossref_is_open_license(item: dict[str, Any]) -> bool:
    for entry in item.get("license", []) or []:
        url = str(entry.get("URL", "")).lower()
        if "creativecommons.org" in url or "openaccess" in url or "open-access" in url:
            return True
    return False


def crossref_oa_url(item: dict[str, Any]) -> str:
    for link in item.get("link", []) or []:
        url = str(link.get("URL", ""))
        if url and ("pdf" in str(link.get("content-type", "")).lower() or url.lower().endswith(".pdf")):
            return url
    for entry in item.get("license", []) or []:
        url = str(entry.get("URL", ""))
        if url:
            return url
    return ""


def fetch_crossref_for_dois(dois: list[str]) -> dict[str, dict[str, Any]]:
    log(f"Track A: querying Crossref for {len(dois)} DOI(s)")
    results: dict[str, dict[str, Any]] = {}
    for batch_index, batch in enumerate(chunks(sorted(set(dois)), 20), start=1):
        key = ",".join(batch)

        def fetch() -> dict[str, Any]:
            return HTTP.get_json(
                CROSSREF_WORKS_URL,
                params={"filter": ",".join(f"doi:{doi}" for doi in batch), "rows": len(batch), "mailto": NCBI_EMAIL},
                timeout=120,
            )

        data = cached_json("crossref_batch", key, fetch)
        items = data.get("message", {}).get("items", []) or []
        by_doi = {normalize_doi(item.get("DOI")): item for item in items if normalize_doi(item.get("DOI"))}
        for doi in batch:
            item = by_doi.get(doi, {})
            results[doi] = {
                "found": bool(item),
                "publisher": normalize_space(item.get("publisher", "")),
                "title": normalize_space((item.get("title") or [""])[0]) if item else "",
                "journal": normalize_space((item.get("container-title") or [""])[0]) if item else "",
                "year": crossref_year(item) if item else None,
                "is_oa": crossref_is_open_license(item) if item else False,
                "oa_url": crossref_oa_url(item) if item else "",
                "raw": item,
            }
        log(f"  Crossref batch {batch_index}/{len(chunks(sorted(set(dois)), 20))}")
        time.sleep(0.15)
    return results


def normalize_epmc_fulltext_urls(item: dict[str, Any]) -> list[str]:
    raw = item.get("fullTextUrlList")
    if not raw:
        return []
    values = raw.get("fullTextUrl") if isinstance(raw, dict) else raw
    if isinstance(values, dict):
        values = [values]
    if not isinstance(values, list):
        return []
    urls = []
    for entry in values:
        if isinstance(entry, dict) and entry.get("url"):
            urls.append(str(entry["url"]))
    return urls


def fetch_epmc_for_dois(dois: list[str]) -> dict[str, dict[str, Any]]:
    log(f"Track A: querying Europe PMC for {len(dois)} DOI(s)")
    results: dict[str, dict[str, Any]] = {}
    for idx, doi in enumerate(sorted(set(dois)), start=1):
        query = f'DOI:"{doi}"'

        def fetch() -> dict[str, Any]:
            return HTTP.get_json(
                EPMC_SEARCH_URL,
                params={"query": query, "format": "json", "pageSize": 1, "resultType": "core"},
                timeout=60,
            )

        data = cached_json("epmc_doi", doi, fetch)
        items = data.get("resultList", {}).get("result", []) or []
        item = items[0] if items else {}
        urls = normalize_epmc_fulltext_urls(item)
        results[doi] = {
            "found": bool(item),
            "is_oa": item.get("isOpenAccess") == "Y" if item else False,
            "has_pdf": item.get("hasPDF") == "Y" if item else False,
            "oa_url": urls[0] if urls else "",
            "title": normalize_space(item.get("title", "")) if item else "",
            "journal": normalize_space(item.get("journalTitle", "")) if item else "",
            "year": parse_year(item.get("pubYear")) if item else None,
            "raw": item,
        }
        if idx % 25 == 0:
            log(f"  Europe PMC {idx}/{len(dois)}")
        time.sleep(0.05)
    return results


def publisher_subscription_tier(publisher: str, is_now_oa: bool) -> str:
    if is_now_oa:
        return "now_oa"
    for token in LIKELY_SUBSCRIBED_PUBLISHERS:
        if token in publisher:
            return "likely_subscribed"
    for token in POSSIBLY_SUBSCRIBED_PUBLISHERS:
        if token in publisher:
            return "possibly_subscribed"
    return "unlikely_subscribed"


def original_block_reason(row: dict[str, str]) -> str:
    status = normalize_space(row.get("status", ""))
    notes = normalize_space(row.get("notes", ""))
    if notes and notes != "[]":
        return f"{status}: {notes}"
    if status == "unresolved":
        return "unresolved_no_resolved_oa_content"
    if status == "error":
        return "access_error"
    return status


def load_corpus_maps() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    corpus = read_jsonl(FULL_RUN_DIR / "corpus.jsonl")
    by_doi = {}
    by_title = {}
    by_paper_id = {}
    for row in corpus:
        doi = normalize_doi(row.get("doi"))
        title = normalize_space(row.get("title", ""))
        paper_id = make_paper_id(doi=doi, title=title, fallback=normalize_space(row.get("pmid", "")))
        if doi:
            by_doi[doi] = row
        if title:
            by_title[title.lower()] = row
        by_paper_id[paper_id] = row
    return corpus, by_doi, by_title, by_paper_id


def title_abstract_mentions_ibuprofen(row: dict[str, Any]) -> bool:
    return re.search(r"\bibuprofen\b", f"{row.get('title', '')} {row.get('abstract', '')}", re.I) is not None


def track_a_access_rescue() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    corpus, by_doi, by_title, by_paper_id = load_corpus_maps()
    access_rows = read_csv(FULL_RUN_DIR / "content_access.csv")
    blocked: list[tuple[dict[str, str], dict[str, Any]]] = []
    for access in access_rows:
        if normalize_space(access.get("status")) == "downloaded":
            continue
        doi = normalize_doi(access.get("doi"))
        title = normalize_space(access.get("title", ""))
        paper_id = normalize_space(access.get("paper_id", ""))
        corpus_row = by_doi.get(doi) or by_paper_id.get(paper_id) or by_title.get(title.lower()) or {}
        merged = {
            **corpus_row,
            "doi": doi or normalize_doi(corpus_row.get("doi")),
            "title": title or normalize_space(corpus_row.get("title")),
            "abstract": normalize_space(corpus_row.get("abstract", "")),
        }
        if title_abstract_mentions_ibuprofen(merged):
            blocked.append((access, merged))

    blocked_dois = [normalize_doi(paper.get("doi")) for _, paper in blocked if normalize_doi(paper.get("doi"))]
    if not blocked:
        raise RuntimeError("Track A found 0 blocked ibuprofen papers; check content_access extraction.")

    crossref = fetch_crossref_for_dois(blocked_dois)
    epmc = fetch_epmc_for_dois(blocked_dois)

    rows: list[dict[str, Any]] = []
    for access, paper in blocked:
        doi = normalize_doi(paper.get("doi"))
        cr = crossref.get(doi, {})
        ep = epmc.get(doi, {})
        is_now_oa = bool(cr.get("is_oa") or ep.get("is_oa"))
        oa_url = ep.get("oa_url") or cr.get("oa_url") or ""
        publisher = normalize_space(cr.get("publisher", ""))
        tier = publisher_subscription_tier(publisher, is_now_oa)
        status_parts = []
        if cr.get("is_oa"):
            status_parts.append("crossref_oa")
        if ep.get("is_oa"):
            status_parts.append("epmc_oa")
        if not status_parts:
            status_parts.append("not_live_oa")
        rows.append(
            {
                "doi": doi,
                "title": normalize_space(paper.get("title")) or cr.get("title") or ep.get("title") or "",
                "journal": normalize_space(paper.get("journal")) or cr.get("journal") or ep.get("journal") or "",
                "publisher": publisher,
                "year": parse_year(paper.get("year")) or cr.get("year") or ep.get("year") or "",
                "subscription_tier": tier,
                "original_block_reason": original_block_reason(access),
                "current_oa_status": "+".join(status_parts),
                "oa_url_if_any": oa_url,
            }
        )

    tier_order = {"now_oa": 0, "likely_subscribed": 1, "possibly_subscribed": 2, "unlikely_subscribed": 3}
    rows.sort(key=lambda r: (tier_order.get(r["subscription_tier"], 9), -(int(r["year"]) if str(r["year"]).isdigit() else 0), r["title"]))
    for idx, row in enumerate(rows, start=1):
        row["priority_rank"] = idx
    capped = rows[:30]
    stats = {
        "n_blocked_ibuprofen_papers": len(rows),
        "tier_distribution": Counter(row["subscription_tier"] for row in rows),
        "high_tier_count": sum(1 for row in rows if row["subscription_tier"] in {"now_oa", "likely_subscribed"}),
        "realistic_fetch_count": min(20, sum(1 for row in rows if row["subscription_tier"] in {"now_oa", "likely_subscribed"})),
        "all_rows": rows,
    }
    write_csv(OUT_DIR / "track_a_access_rescue_list.csv", capped, TRACK_A_FIELDS)
    return capped, stats


def components_for_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    components = []
    for item in record.get("components") or []:
        if isinstance(item, dict):
            components.append(item)
    formulation = record.get("formulation") or {}
    for item in formulation.get("components") or []:
        if isinstance(item, dict):
            components.append(item)
    return components


def numeric_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, str) and not value.strip():
            return None
        result = float(value)
        if math.isnan(result):
            return None
        return round(result, 8)
    except (TypeError, ValueError):
        return None


def component_numeric_value(component: dict[str, Any]) -> float | None:
    for key in ["value", "concentration_value", "api_concentration_value"]:
        result = numeric_value(component.get(key))
        if result is not None:
            return result
    return None


def endpoint_numeric_value(record: dict[str, Any]) -> float | None:
    endpoint = record.get("endpoint") or {}
    for value in [record.get("endpoint_value"), endpoint.get("normalized_value"), endpoint.get("value")]:
        result = numeric_value(value)
        if result is not None:
            return result
    return None


def extraction_source(record: dict[str, Any]) -> str:
    source = record.get("extraction_source") or record.get("route")
    if source:
        return normalize_space(source).lower()
    for key in ["source_extraction_provenance", "provenance"]:
        payload = record.get(key) or {}
        if isinstance(payload, dict) and payload.get("extractor_name"):
            return normalize_space(payload.get("extractor_name")).lower()
    return "unknown"


def record_table_pages(record: dict[str, Any]) -> set[Any]:
    pages: set[Any] = set()
    for evidence in record.get("evidence_items") or []:
        if isinstance(evidence, dict) and evidence.get("page") is not None:
            pages.add(evidence.get("page"))
    for key in ["source_extraction_provenance", "provenance"]:
        payload = record.get(key) or {}
        if not isinstance(payload, dict):
            continue
        for page in payload.get("source_pages") or []:
            pages.add(page)
        metadata = payload.get("metadata") or {}
        for page in metadata.get("row_source_pages") or []:
            pages.add(page)
        for locator in metadata.get("row_source_locators") or []:
            match = re.search(r"page\s+(\d+)", str(locator), re.I)
            if match:
                pages.add(int(match.group(1)))
    return pages


def record_table_ids(record: dict[str, Any]) -> set[str]:
    table_ids = set()
    for key in ["source_extraction_provenance", "provenance"]:
        payload = record.get(key) or {}
        if isinstance(payload, dict):
            metadata = payload.get("metadata") or {}
            if metadata.get("table_id"):
                table_ids.add(str(metadata["table_id"]))
    for evidence in record.get("evidence_items") or []:
        if isinstance(evidence, dict) and evidence.get("locator"):
            locator = str(evidence["locator"])
            if re.search(r"\btable\b", locator, re.I):
                table_ids.add(locator)
    return table_ids


def expected_lift_class(score: int) -> str:
    if score >= 60:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def provenance_has_microneedle_flag(records: list[dict[str, Any]], paper_summary: dict[str, str] | None) -> bool:
    if paper_summary and "microneedle_or_iontophoresis" in json.dumps(paper_summary).lower():
        return True
    for record in records:
        blob = json.dumps(record, ensure_ascii=False).lower()
        if "microneedle_or_iontophoresis" in blob:
            return True
    return False


def track_b_reextraction_targets() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records = read_jsonl(PHASE0B_DIR / "all_ibuprofen_records.jsonl")
    summaries = {normalize_doi(row.get("doi")): row for row in read_csv(PHASE0B_DIR / "paper_level_summary.csv")}
    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        doi = normalize_doi(record.get("doi"))
        if doi:
            by_doi[doi].append(record)

    rows: list[dict[str, Any]] = []
    for doi, paper_records in by_doi.items():
        n_records = len(paper_records)
        n_with_components = 0
        n_with_numeric_composition = 0
        distinct_component_values = set()
        distinct_endpoint_values = set()
        provenance_counter: Counter[str] = Counter()
        table_pages = set()
        table_ids = set()
        has_verified_v2 = False
        for record in paper_records:
            components = components_for_record(record)
            if components:
                n_with_components += 1
            numeric_components = []
            for component in components:
                value = component_numeric_value(component)
                if value is None:
                    continue
                numeric_components.append(value)
                name = normalize_space(component.get("name") or component.get("name_raw") or "")
                unit = normalize_space(component.get("unit") or component.get("concentration_unit") or "")
                distinct_component_values.add((name.lower(), value, unit.lower()))
            if numeric_components:
                n_with_numeric_composition += 1
            endpoint_value = endpoint_numeric_value(record)
            if endpoint_value is not None:
                distinct_endpoint_values.add(endpoint_value)
            provenance_counter[extraction_source(record)] += 1
            table_pages.update(record_table_pages(record))
            table_ids.update(record_table_ids(record))
            has_verified_v2 = has_verified_v2 or ("verified_v2" in json.dumps(record, ensure_ascii=False).lower())

        pct_numeric = n_with_numeric_composition / n_records if n_records else 0.0
        pct_components = n_with_components / n_records if n_records else 0.0
        text_fraction = provenance_counter.get("text", 0) / n_records if n_records else 0.0
        score = 0
        if n_records >= 10:
            score += 30
        if pct_numeric < 0.3:
            score += 25
        if has_verified_v2:
            score += 15
        if len(distinct_endpoint_values) >= 5:
            score += 10
        if text_fraction >= 0.5:
            score += 10
        if len(table_pages) > 1:
            score += 10
        if n_records <= 3:
            score -= 15
        if provenance_has_microneedle_flag(paper_records, summaries.get(doi)):
            score -= 10
        score = max(0, min(100, score))
        n_tables = max(len(table_ids), len(table_pages))
        est_tokens = n_tables * 3000 + 5000 if n_tables else 12000
        rows.append(
            {
                "doi": doi,
                "n_records_total": n_records,
                "pct_records_with_numeric_composition": round(pct_numeric * 100, 1),
                "pct_records_with_components_list": round(pct_components * 100, 1),
                "n_distinct_numeric_component_values": len(distinct_component_values),
                "provenance_mix": "; ".join(f"{key}={value}" for key, value in provenance_counter.most_common()),
                "re_extraction_potential": score,
                "expected_lift_class": expected_lift_class(score),
                "est_llm_input_tokens": est_tokens,
            }
        )
    rows.sort(key=lambda row: (-int(row["re_extraction_potential"]), -int(row["n_records_total"]), row["doi"]))
    capped = rows[:15]
    stats = {
        "n_papers": len(rows),
        "n_papers_with_high_potential": sum(1 for row in rows if int(row["re_extraction_potential"]) >= 60),
        "all_rows": rows,
    }
    write_csv(OUT_DIR / "track_b_re_extraction_targets.csv", capped, TRACK_B_FIELDS)
    return capped, stats


def load_manifest_query() -> tuple[str, dict[str, Any]]:
    manifest_rows = read_jsonl(FULL_RUN_DIR / "run_manifest.jsonl")
    manifest = manifest_rows[-1] if manifest_rows else {}
    metrics = manifest.get("stage_metrics") or {}
    query = normalize_space(metrics.get("corpus_query", ""))
    lines = [
        f"run_id: {manifest.get('run_id', '')}",
        f"query_profile: {metrics.get('query_profile', '')}",
        f"query_profile_version: {metrics.get('query_profile_version', '')}",
        f"query_source: {metrics.get('query_source', '')}",
        "",
        "SkinMiner retrieval query verbatim:",
        query,
    ]
    (OUT_DIR / "skinminer_retrieval_query.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return query, manifest


def classify_retrieval_miss(paper: dict[str, Any], query: str) -> str:
    title = normalize_space(paper.get("title", ""))
    abstract = normalize_space(paper.get("abstract", ""))
    text = f"{title} {abstract}"
    year = parse_year(paper.get("year"))
    if year and (year < 1900 or year > 2026):
        return "excluded_by_year_filter"
    if not re.search(r"\bibuprofen\b", title, re.I) and re.search(
        r"\b(dexibuprofen|ibuprofenate|ibuprofen\s+(sodium|lysine|salt|complex|derivative)|flurbiprofen)\b",
        title,
        re.I,
    ):
        return "wrong_api_keyword"
    method_terms = re.search(r"\b(permeat\w*|permeation|diffusion|in vitro|release)\b", text, re.I)
    target_terms = re.search(r"\b(skin|membrane|topical|transdermal|diffusion cell)\b", text, re.I)
    if not method_terms or not target_terms:
        return "wrong_method_keyword"
    if not re.search(r"\bibuprofen\b", title, re.I):
        return "wrong_api_keyword"
    return "unknown"


def track_c_retrieval_gap() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    query, manifest = load_manifest_query()
    corpus = read_jsonl(FULL_RUN_DIR / "corpus.jsonl")
    corpus_dois = {normalize_doi(row.get("doi")) for row in corpus if normalize_doi(row.get("doi"))}
    phase0a = read_jsonl(PHASE0A_TRACK_B)
    phase0a_by_doi = {normalize_doi(row.get("doi")): row for row in phase0a if normalize_doi(row.get("doi"))}
    missed_dois = sorted(set(phase0a_by_doi) - corpus_dois)
    rows = []
    for doi in missed_dois:
        paper = phase0a_by_doi[doi]
        rows.append(
            {
                "doi": doi,
                "title": normalize_space(paper.get("title", "")),
                "journal": normalize_space(paper.get("journal", "")),
                "year": paper.get("year") or "",
                "miss_reason": classify_retrieval_miss(paper, query),
                "phase0a_oa": bool(paper.get("is_oa")),
            }
        )
    write_csv(OUT_DIR / "track_c_retrieval_gap.csv", rows, TRACK_C_FIELDS)
    return rows, {
        "query": query,
        "manifest": manifest,
        "phase0a_unique": len(phase0a_by_doi),
        "corpus_dois": len(corpus_dois),
        "missed_count": len(rows),
    }


def count_unique_dois_in_jsonl(path: Path, ibuprofen_only: bool = True, verified_only: bool = False) -> int:
    rows = read_jsonl(path)
    dois = set()
    for row in rows:
        if verified_only and normalize_space(row.get("verification_status", "")).lower() != "verified":
            continue
        if ibuprofen_only:
            blob = json.dumps(
                {
                    "api_name": row.get("api_name"),
                    "formulation": row.get("formulation"),
                    "doi": row.get("doi"),
                    "title": row.get("title"),
                },
                ensure_ascii=False,
            ).lower()
            if "ibuprofen" not in blob:
                continue
        doi = normalize_doi(row.get("doi")) or normalize_space(row.get("paper_id", ""))
        if doi:
            dois.add(doi)
    return len(dois)


def build_funnel_counts() -> list[tuple[str, int]]:
    corpus = read_jsonl(FULL_RUN_DIR / "corpus.jsonl")
    access = read_csv(FULL_RUN_DIR / "content_access.csv")
    stage1_summary = read_csv(PHASE0B_DIR / "paper_level_summary.csv")
    survived_access = [row for row in access if normalize_space(row.get("status")) == "downloaded"]
    verified_v2 = sum(
        1
        for row in stage1_summary
        if int(row.get("n_records_v2") or 0) > 0 or int(row.get("n_records_v2_claude") or 0) > 0
    )
    verified_v3 = sum(
        1
        for row in stage1_summary
        if int(row.get("n_records_v2") or 0) > 0
        or int(row.get("n_records_v2_claude") or 0) > 0
        or int(row.get("n_records_v3_only") or 0) > 0
    )
    verified_v4 = sum(
        1
        for row in stage1_summary
        if int(row.get("n_records_v2") or 0) > 0
        or int(row.get("n_records_v2_claude") or 0) > 0
        or int(row.get("n_records_v3_only") or 0) > 0
        or int(row.get("n_records_v4_only") or 0) > 0
    )
    return [
        ("PubMed/EPMC theoretical universe (from Phase 0a Track B query)", len(read_jsonl(PHASE0A_TRACK_B))),
        ("SkinMiner retrieval corpus (ibuprofen subset)", len(corpus)),
        ("Survived triage", len(access)),
        ("Survived access", len(survived_access)),
        ("Produced >= 1 assembled record", count_unique_dois_in_jsonl(FULL_RUN_DIR / "assembled_records.jsonl")),
        ("Verified at v2", verified_v2),
        ("Verified at v3", verified_v3),
        ("Verified at v4", verified_v4),
        ("Stage 1 audit pool (>= 1 record any provenance)", len(stage1_summary)),
    ]


def markdown_table(rows: list[dict[str, Any]], fields: list[str], max_rows: int) -> list[str]:
    display = rows[:max_rows]
    if not display:
        return ["No rows."]
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
    for row in display:
        values = []
        for field in fields:
            text = normalize_space(row.get(field, ""))
            if len(text) > 90:
                text = text[:87] + "..."
            values.append(text.replace("|", "/"))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def make_recommendation(track_a_stats: dict[str, Any], track_b_stats: dict[str, Any]) -> tuple[str, str]:
    access_ok = int(track_a_stats["high_tier_count"]) >= 5
    reextract_ok = int(track_b_stats["n_papers_with_high_potential"]) >= 5
    if access_ok and reextract_ok:
        return (
            "GO-BOTH",
            "Track A has at least 5 now-OA/likely-subscribed rescue candidates and Track B has at least 5 high-potential re-extraction targets.",
        )
    if access_ok:
        return (
            "GO-ACCESS",
            f"Track A has {track_a_stats['high_tier_count']} now-OA/likely-subscribed rescue candidates, while Track B has only {track_b_stats['n_papers_with_high_potential']} high-potential re-extraction targets.",
        )
    if reextract_ok:
        return (
            "GO-RE-EXTRACT",
            f"Track B has {track_b_stats['n_papers_with_high_potential']} high-potential targets, while Track A has fewer than 5 top-tier rescue candidates.",
        )
    return (
        "NO-GO-CONFIRMED",
        "Both Track A and Track B fall below the 1-2 week action thresholds.",
    )


def build_report(
    track_a_rows: list[dict[str, Any]],
    track_a_stats: dict[str, Any],
    track_b_rows: list[dict[str, Any]],
    track_b_stats: dict[str, Any],
    track_c_rows: list[dict[str, Any]],
    track_c_stats: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.append("# Phase 0c Diagnostic Audit")
    lines.append("")
    lines.append("Deterministic audit only: existing SkinMiner outputs, PubMed/EPMC/Crossref metadata, DOI matching, and structured-field counts. No full-text PDFs were downloaded, no pipeline stage was rerun, and no LLM calls were made.")
    lines.append("")
    lines.append("## 1. Pool Flow")
    lines.append("")
    lines.append("| Stage | Paper count |")
    lines.append("|---|---:|")
    for stage, count in build_funnel_counts():
        label = f"**{stage}**" if stage.startswith("Stage 1") else stage
        lines.append(f"| {label} | {count} |")
    lines.append("")

    lines.append("## 2. Track A Findings")
    lines.append("")
    lines.append(f"Total `n_blocked_ibuprofen_papers`: `{track_a_stats['n_blocked_ibuprofen_papers']}`.")
    tier_distribution = ", ".join(f"{key}={value}" for key, value in track_a_stats["tier_distribution"].most_common())
    lines.append(f"Subscription-tier distribution: {tier_distribution}.")
    lines.append(f"Top-tier candidates realistically fetchable in 1-2 weeks: `{track_a_stats['realistic_fetch_count']}` (capped at 20 manual PDFs).")
    lines.append("")
    lines.append("Top 10 access-rescue candidates:")
    lines.extend(markdown_table(track_a_rows, TRACK_A_FIELDS, 10))
    lines.append("")

    lines.append("## 3. Track B Findings")
    lines.append("")
    lines.append(f"Total `n_papers_with_high_potential`: `{track_b_stats['n_papers_with_high_potential']}`.")
    lines.append("Top 10 re-extraction targets:")
    lines.extend(markdown_table(track_b_rows, TRACK_B_FIELDS, 10))
    top10_tokens = sum(int(row["est_llm_input_tokens"]) for row in track_b_rows[:10])
    gpt_cost = top10_tokens / 1_000_000 * GPT5_INPUT_PRICE_PER_MTOK
    claude_cost = top10_tokens / 1_000_000 * CLAUDE_SONNET_INPUT_PRICE_PER_MTOK
    lines.append("")
    lines.append(
        f"Estimated top-10 input tokens: `{top10_tokens}`. Estimated input-only cost: GPT-5-class `${gpt_cost:.4f}`; Claude Sonnet `${claude_cost:.4f}`. {PRICING_NOTE}"
    )
    lines.append("")

    lines.append("## 4. Track C Findings")
    lines.append("")
    lines.append("SkinMiner retrieval query verbatim:")
    lines.append("")
    lines.append("```text")
    lines.append(track_c_stats["query"])
    lines.append("```")
    lines.append("")
    lines.append(f"Phase 0a Track B unique DOI count: `{track_c_stats['phase0a_unique']}`.")
    lines.append(f"SkinMiner corpus DOI count: `{track_c_stats['corpus_dois']}`.")
    lines.append(f"Missed papers (Phase 0a Track B - SkinMiner corpus): `{track_c_stats['missed_count']}`.")
    lines.append("")
    lines.append("Top 5 missed papers:")
    lines.extend(markdown_table(track_c_rows, TRACK_C_FIELDS, 5))
    lines.append("")
    lines.append("This is logged for paper Discussion section. NOT actioned in this window.")
    lines.append("")

    lines.append("## 5. Decision Recommendation")
    lines.append("")
    recommendation, justification = make_recommendation(track_a_stats, track_b_stats)
    if recommendation == "GO-ACCESS":
        lines.append("Recommend manually downloading the top 5-15 PDFs from Track A and re-injecting them. This is bounded to a 3-7 day action and may add 15-25 papers to the accessible pool; if internal-factor variation still fails, the negative result becomes a stronger limitations discussion.")
    elif recommendation == "GO-RE-EXTRACT":
        lines.append("Recommend Stage 2 LLM re-extraction on the top 5 Track B papers, targeting formulation composition fields only.")
    elif recommendation == "GO-BOTH":
        lines.append("Recommend running access rescue and targeted re-extraction in parallel: manual PDF fetch starts while Stage 2 targets the top re-extraction papers.")
    else:
        lines.append("Recommend accepting the NO-GO and moving to an alternative demonstration framing.")
    lines.append("")
    lines.append(f"RECOMMENDATION: {recommendation} | {justification}")
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    track_a_rows, track_a_stats = track_a_access_rescue()
    track_b_rows, track_b_stats = track_b_reextraction_targets()
    track_c_rows, track_c_stats = track_c_retrieval_gap()

    report = build_report(track_a_rows, track_a_stats, track_b_rows, track_b_stats, track_c_rows, track_c_stats)
    REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")

    log(f"Wrote {OUT_DIR / 'track_a_access_rescue_list.csv'}")
    log(f"Wrote {OUT_DIR / 'track_b_re_extraction_targets.csv'}")
    log(f"Wrote {OUT_DIR / 'track_c_retrieval_gap.csv'}")
    log(f"Wrote {OUT_DIR / 'skinminer_retrieval_query.txt'}")
    log(f"Wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
