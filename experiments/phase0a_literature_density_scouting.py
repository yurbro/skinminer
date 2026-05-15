from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "outputs" / "phase0a"
REPORT_PATH = ROOT / "reports" / "phase0a_literature_density_scouting.md"
NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "skinminer-codex@example.com")
USER_AGENT = f"skinminer-phase0a-scouting/1.0 (mailto:{NCBI_EMAIL})"

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC_SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CROSSREF_WORKS_URL = "https://api.crossref.org/works"


TRACKS = {
    "track_a_caffeine": {
        "summary_track": "A_caffeine",
        "report_label": "Track A - caffeine/nicotinamide/lidocaine vehicles",
        "pubmed_query": """
(
  caffeine[Title/Abstract] OR caffeine[MeSH Terms] OR
  nicotinamide[Title/Abstract] OR nicotinamide[MeSH Terms] OR
  niacinamide[Title/Abstract] OR
  lidocaine[Title/Abstract] OR lidocaine[MeSH Terms] OR
  lignocaine[Title/Abstract]
)
AND (
  "in vitro permeation"[Title/Abstract] OR
  "Franz cell"[Title/Abstract] OR
  "Franz diffusion"[Title/Abstract] OR
  "skin permeation"[Title/Abstract] OR
  "transdermal"[Title/Abstract] OR
  "percutaneous absorption"[Title/Abstract]
)
AND (
  "propylene glycol"[Title/Abstract] OR
  "ethanol"[Title/Abstract] OR
  "PG/water"[Title/Abstract] OR
  "vehicle"[Title/Abstract] OR
  "co-solvent"[Title/Abstract] OR
  "cosolvent"[Title/Abstract] OR
  "isopropyl myristate"[Title/Abstract] OR
  "mineral oil"[Title/Abstract]
)
AND ("1990"[PDAT] : "2026"[PDAT])
""".strip(),
        "epmc_query": """
(
  (
    TITLE_ABS:"caffeine" OR MESH:"caffeine" OR
    TITLE_ABS:"nicotinamide" OR MESH:"nicotinamide" OR
    TITLE_ABS:"niacinamide" OR
    TITLE_ABS:"lidocaine" OR MESH:"lidocaine" OR
    TITLE_ABS:"lignocaine"
  )
  AND (
    TITLE_ABS:"in vitro permeation" OR
    TITLE_ABS:"Franz cell" OR
    TITLE_ABS:"Franz diffusion" OR
    TITLE_ABS:"skin permeation" OR
    TITLE_ABS:"transdermal" OR
    TITLE_ABS:"percutaneous absorption"
  )
  AND (
    TITLE_ABS:"propylene glycol" OR
    TITLE_ABS:"ethanol" OR
    TITLE_ABS:"PG/water" OR
    TITLE_ABS:"vehicle" OR
    TITLE_ABS:"co-solvent" OR
    TITLE_ABS:"cosolvent" OR
    TITLE_ABS:"isopropyl myristate" OR
    TITLE_ABS:"mineral oil"
  )
  AND PUB_YEAR:[1990 TO 2026]
  AND OPEN_ACCESS:y
)
""".strip(),
    },
    "track_b_ibuprofen_gel": {
        "summary_track": "B_ibuprofen_gel",
        "report_label": "Track B - ibuprofen gel matrices",
        "pubmed_query": """
(ibuprofen[Title/Abstract] OR ibuprofen[MeSH Terms])
AND (
  "in vitro permeation"[Title/Abstract] OR
  "Franz cell"[Title/Abstract] OR
  "Franz diffusion"[Title/Abstract] OR
  "skin permeation"[Title/Abstract] OR
  "transdermal"[Title/Abstract] OR
  "percutaneous absorption"[Title/Abstract] OR
  IVRT[Title/Abstract] OR
  IVPT[Title/Abstract]
)
AND (
  "Carbopol"[Title/Abstract] OR
  "HPMC"[Title/Abstract] OR
  "hydroxypropyl methylcellulose"[Title/Abstract] OR
  "Poloxamer"[Title/Abstract] OR
  "Pluronic"[Title/Abstract] OR
  "gel"[Title/Abstract] OR
  "hydrogel"[Title/Abstract]
)
AND ("1990"[PDAT] : "2026"[PDAT])
""".strip(),
        "epmc_query": """
(
  (TITLE_ABS:"ibuprofen" OR MESH:"ibuprofen")
  AND (
    TITLE_ABS:"in vitro permeation" OR
    TITLE_ABS:"Franz cell" OR
    TITLE_ABS:"Franz diffusion" OR
    TITLE_ABS:"skin permeation" OR
    TITLE_ABS:"transdermal" OR
    TITLE_ABS:"percutaneous absorption" OR
    TITLE_ABS:"IVRT" OR
    TITLE_ABS:"IVPT"
  )
  AND (
    TITLE_ABS:"Carbopol" OR
    TITLE_ABS:"HPMC" OR
    TITLE_ABS:"hydroxypropyl methylcellulose" OR
    TITLE_ABS:"Poloxamer" OR
    TITLE_ABS:"Pluronic" OR
    TITLE_ABS:"gel" OR
    TITLE_ABS:"hydrogel"
  )
  AND PUB_YEAR:[1990 TO 2026]
  AND OPEN_ACCESS:y
)
""".strip(),
    },
}


def log(message: str) -> None:
    print(message, flush=True)


def normalize_space(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def normalize_doi(value: str | None) -> str:
    if not value:
        return ""
    doi = value.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    doi = doi.strip().strip(".")
    return doi.lower()


def parse_year(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    return int(match.group(0)) if match else None


def element_text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return normalize_space("".join(node.itertext()))


class HttpClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def get(self, url: str, params: dict[str, Any] | None = None, timeout: int = 60) -> requests.Response:
        last_exc: Exception | None = None
        for attempt in range(6):
            try:
                response = self.session.get(url, params=params, timeout=timeout)
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise requests.HTTPError(f"transient status {response.status_code}", response=response)
                response.raise_for_status()
                return response
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
                last_exc = exc
                wait = min(60, 1.5 * (2**attempt))
                log(f"  retrying after {wait:.1f}s: {url}")
                time.sleep(wait)
        assert last_exc is not None
        raise last_exc

    def get_json(self, url: str, params: dict[str, Any] | None = None, timeout: int = 60) -> dict[str, Any]:
        return self.get(url, params=params, timeout=timeout).json()

    def get_text(self, url: str, params: dict[str, Any] | None = None, timeout: int = 60) -> str:
        return self.get(url, params=params, timeout=timeout).text


HTTP = HttpClient()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def pubmed_esearch(query: str) -> tuple[int, list[str]]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 100000,
        "tool": "skinminer",
        "email": NCBI_EMAIL,
    }
    data = HTTP.get_json(f"{PUBMED_BASE}/esearch.fcgi", params=params)
    time.sleep(0.34)
    result = data.get("esearchresult", {})
    count = int(result.get("count", 0))
    ids = list(result.get("idlist", []))
    return count, ids


def parse_pubmed_article(article: ET.Element) -> dict[str, Any]:
    medline = article.find("MedlineCitation")
    pubmed_data = article.find("PubmedData")
    article_node = medline.find("Article") if medline is not None else None

    pmid = element_text(medline.find("PMID") if medline is not None else None)
    title = element_text(article_node.find("ArticleTitle") if article_node is not None else None)

    abstract_parts = []
    if article_node is not None:
        for abstract_text in article_node.findall("./Abstract/AbstractText"):
            label = abstract_text.attrib.get("Label")
            text = element_text(abstract_text)
            if text:
                abstract_parts.append(f"{label}: {text}" if label else text)
    abstract = normalize_space(" ".join(abstract_parts))

    journal_title = ""
    journal_iso = ""
    if article_node is not None:
        journal = article_node.find("Journal")
        if journal is not None:
            journal_title = element_text(journal.find("Title"))
            journal_iso = element_text(journal.find("ISOAbbreviation"))

    year = None
    if article_node is not None:
        pub_date = article_node.find("./Journal/JournalIssue/PubDate")
        if pub_date is not None:
            year = parse_year(element_text(pub_date.find("Year"))) or parse_year(element_text(pub_date.find("MedlineDate")))
        if year is None:
            article_date = article_node.find("ArticleDate/Year")
            year = parse_year(element_text(article_date))

    dois = []
    if article_node is not None:
        for location_id in article_node.findall("ELocationID"):
            if location_id.attrib.get("EIdType", "").lower() == "doi":
                doi = normalize_doi(element_text(location_id))
                if doi:
                    dois.append(doi)
    if pubmed_data is not None:
        for article_id in pubmed_data.findall("./ArticleIdList/ArticleId"):
            if article_id.attrib.get("IdType", "").lower() == "doi":
                doi = normalize_doi(element_text(article_id))
                if doi:
                    dois.append(doi)

    mesh_terms = []
    if medline is not None:
        for descriptor in medline.findall("./MeshHeadingList/MeshHeading/DescriptorName"):
            text = element_text(descriptor)
            if text:
                mesh_terms.append(text)

    publication_types = []
    if article_node is not None:
        for publication_type in article_node.findall("./PublicationTypeList/PublicationType"):
            text = element_text(publication_type)
            if text:
                publication_types.append(text)

    languages = []
    if article_node is not None:
        for language in article_node.findall("Language"):
            text = element_text(language)
            if text:
                languages.append(text)

    authors = []
    if article_node is not None:
        for author in article_node.findall("./AuthorList/Author"):
            collective = element_text(author.find("CollectiveName"))
            if collective:
                authors.append({"name": collective, "last": "", "fore": ""})
                continue
            last = element_text(author.find("LastName"))
            fore = element_text(author.find("ForeName"))
            initials = element_text(author.find("Initials"))
            name = normalize_space(" ".join(part for part in [fore or initials, last] if part))
            if name or last:
                authors.append({"name": name or last, "last": last, "fore": fore or initials})

    return {
        "source": "pubmed",
        "pmid": pmid,
        "title": title,
        "abstract": abstract,
        "year": year,
        "journal": journal_title or journal_iso,
        "journal_iso": journal_iso,
        "doi": dois[0] if dois else "",
        "all_dois": sorted(set(dois)),
        "mesh_terms": sorted(set(mesh_terms)),
        "publication_types": publication_types,
        "languages": languages,
        "authors": authors,
        "oa_flag": None,
    }


def fetch_pubmed_records(track_key: str, query: str) -> tuple[int, list[dict[str, Any]]]:
    log(f"Fetching PubMed for {track_key}")
    count, ids = pubmed_esearch(query)
    records: list[dict[str, Any]] = []
    for start in range(0, len(ids), 200):
        batch = ids[start : start + 200]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml",
            "tool": "skinminer",
            "email": NCBI_EMAIL,
        }
        xml_text = HTTP.get_text(f"{PUBMED_BASE}/efetch.fcgi", params=params, timeout=120)
        time.sleep(0.34)
        root = ET.fromstring(xml_text)
        for article in root.findall("./PubmedArticle"):
            records.append(parse_pubmed_article(article))
        log(f"  PubMed {track_key}: {len(records)}/{len(ids)} records")
    return count, records


def normalize_epmc_fulltext_urls(raw: Any) -> list[dict[str, Any]]:
    if not raw:
        return []
    urls = raw.get("fullTextUrl") if isinstance(raw, dict) else raw
    if isinstance(urls, dict):
        urls = [urls]
    if not isinstance(urls, list):
        return []
    normalized = []
    for entry in urls:
        if isinstance(entry, dict):
            normalized.append(entry)
    return normalized


def fetch_epmc_records(track_key: str, query: str) -> tuple[int, list[dict[str, Any]]]:
    log(f"Fetching Europe PMC for {track_key}")
    cursor = "*"
    hit_count = 0
    records: list[dict[str, Any]] = []
    while True:
        params = {
            "query": query,
            "format": "json",
            "pageSize": 1000,
            "cursorMark": cursor,
            "resultType": "core",
        }
        data = HTTP.get_json(EPMC_SEARCH_URL, params=params, timeout=120)
        hit_count = int(data.get("hitCount", hit_count or 0))
        page = data.get("resultList", {}).get("result", [])
        if not page:
            break
        for item in page:
            full_text_urls = normalize_epmc_fulltext_urls(item.get("fullTextUrlList"))
            records.append(
                {
                    "source": "europepmc",
                    "id": item.get("id", ""),
                    "pmid": item.get("pmid", ""),
                    "doi": normalize_doi(item.get("doi", "")),
                    "title": normalize_space(item.get("title", "")),
                    "abstract": normalize_space(item.get("abstractText", "")),
                    "year": parse_year(item.get("pubYear")),
                    "journal": normalize_space(item.get("journalTitle", "")),
                    "isOpenAccess": item.get("isOpenAccess", "") == "Y",
                    "hasPDF": item.get("hasPDF", "") == "Y",
                    "fullTextUrlList": full_text_urls,
                    "authorString": normalize_space(item.get("authorString", "")),
                    "language": item.get("language", ""),
                    "raw": item,
                }
            )
        next_cursor = data.get("nextCursorMark")
        log(f"  Europe PMC {track_key}: {len(records)}/{hit_count} records")
        if not next_cursor or next_cursor == cursor or len(records) >= hit_count:
            break
        cursor = next_cursor
    return hit_count, records


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def crossref_is_open_license(license_items: list[dict[str, Any]]) -> bool:
    for entry in license_items:
        url = str(entry.get("URL", "")).lower()
        if "creativecommons.org" in url or "openaccess" in url or "open-access" in url:
            return True
    return False


def crossref_pdf_links(item: dict[str, Any]) -> list[str]:
    urls = []
    for link in item.get("link", []) or []:
        url = str(link.get("URL", ""))
        content_type = str(link.get("content-type", "")).lower()
        intended = str(link.get("intended-application", "")).lower()
        if "pdf" in content_type or url.lower().endswith(".pdf") or intended == "text-mining":
            if url:
                urls.append(url)
    return urls


def fetch_crossref_records(track_key: str, dois: list[str]) -> list[dict[str, Any]]:
    log(f"Fetching Crossref for {track_key}: {len(dois)} DOI(s)")
    records: list[dict[str, Any]] = []
    for batch_index, batch in enumerate(chunks(sorted(set(dois)), 20), start=1):
        filter_value = ",".join(f"doi:{doi}" for doi in batch)
        params = {
            "filter": filter_value,
            "rows": len(batch),
            "mailto": NCBI_EMAIL,
        }
        data = HTTP.get_json(CROSSREF_WORKS_URL, params=params, timeout=120)
        items = data.get("message", {}).get("items", [])
        by_doi = {normalize_doi(item.get("DOI", "")): item for item in items if item.get("DOI")}
        for doi in batch:
            item = by_doi.get(normalize_doi(doi))
            if not item:
                records.append({"source": "crossref", "doi": doi, "found": False, "raw": None})
                continue
            license_items = item.get("license", []) or []
            links = item.get("link", []) or []
            records.append(
                {
                    "source": "crossref",
                    "doi": normalize_doi(item.get("DOI", doi)),
                    "found": True,
                    "title": normalize_space((item.get("title") or [""])[0]),
                    "year": crossref_year(item),
                    "journal": normalize_space((item.get("container-title") or [""])[0]),
                    "license": license_items,
                    "license_urls": [entry.get("URL", "") for entry in license_items if entry.get("URL")],
                    "has_open_license": crossref_is_open_license(license_items),
                    "links": links,
                    "pdf_or_tdm_urls": crossref_pdf_links(item),
                    "raw": item,
                }
            )
        log(f"  Crossref {track_key}: batch {batch_index}/{len(chunks(dois, 20))}")
        time.sleep(0.15)
    return records


def crossref_year(item: dict[str, Any]) -> int | None:
    for key in ["published-print", "published-online", "published", "issued"]:
        date_parts = item.get(key, {}).get("date-parts")
        if date_parts and date_parts[0]:
            return parse_year(date_parts[0][0])
    return None


def build_alias_map(records: list[dict[str, Any]]) -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for record in records:
        doi = normalize_doi(record.get("doi"))
        pmid = str(record.get("pmid") or "").strip()
        if doi and pmid:
            alias_map[f"pmid:{pmid}"] = f"doi:{doi}"
    return alias_map


def paper_key(record: dict[str, Any], alias_map: dict[str, str] | None = None) -> str:
    doi = normalize_doi(record.get("doi"))
    if doi:
        return f"doi:{doi}"
    pmid = str(record.get("pmid") or "").strip()
    if pmid:
        pmid_key = f"pmid:{pmid}"
        return (alias_map or {}).get(pmid_key, pmid_key)
    source_id = str(record.get("id") or "").strip()
    return f"{record.get('source', 'unknown')}:{source_id or id(record)}"


def empty_paper() -> dict[str, Any]:
    return {
        "doi": "",
        "pmid": "",
        "epmc_ids": [],
        "title": "",
        "abstract": "",
        "year": None,
        "journal": "",
        "sources": [],
        "mesh_terms": [],
        "publication_types": [],
        "languages": [],
        "authors": [],
        "is_oa_epmc": False,
        "is_oa_crossref": False,
        "has_pdf_url_epmc": False,
        "has_pdf_url_crossref": False,
        "full_text_urls": [],
        "license_urls": [],
        "crossref_found": False,
    }


def merge_text(existing: str, incoming: str) -> str:
    if not existing:
        return incoming or ""
    if incoming and len(incoming) > len(existing):
        return incoming
    return existing


def merge_pubmed_or_epmc(
    papers: dict[str, dict[str, Any]],
    record: dict[str, Any],
    alias_map: dict[str, str],
) -> None:
    key = paper_key(record, alias_map)
    paper = papers.setdefault(key, empty_paper())
    source = record.get("source", "")
    if source and source not in paper["sources"]:
        paper["sources"].append(source)

    doi = normalize_doi(record.get("doi"))
    if doi and not paper["doi"]:
        paper["doi"] = doi
    pmid = str(record.get("pmid") or "").strip()
    if pmid and not paper["pmid"]:
        paper["pmid"] = pmid
    epmc_id = str(record.get("id") or "").strip()
    if source == "europepmc" and epmc_id and epmc_id not in paper["epmc_ids"]:
        paper["epmc_ids"].append(epmc_id)

    paper["title"] = merge_text(paper["title"], normalize_space(record.get("title", "")))
    paper["abstract"] = merge_text(paper["abstract"], normalize_space(record.get("abstract", "")))
    if not paper["year"]:
        paper["year"] = record.get("year")
    if not paper["journal"]:
        paper["journal"] = normalize_space(record.get("journal", ""))

    for term in record.get("mesh_terms", []) or []:
        if term not in paper["mesh_terms"]:
            paper["mesh_terms"].append(term)
    for pub_type in record.get("publication_types", []) or []:
        if pub_type not in paper["publication_types"]:
            paper["publication_types"].append(pub_type)
    languages = record.get("languages") or ([record.get("language")] if record.get("language") else [])
    for language in languages:
        if language and language not in paper["languages"]:
            paper["languages"].append(language)

    authors = record.get("authors") or []
    if not authors and record.get("authorString"):
        authors = parse_author_string(record.get("authorString", ""))
    if authors and not paper["authors"]:
        paper["authors"] = authors

    if source == "europepmc":
        paper["is_oa_epmc"] = paper["is_oa_epmc"] or bool(record.get("isOpenAccess"))
        paper["has_pdf_url_epmc"] = paper["has_pdf_url_epmc"] or bool(record.get("hasPDF"))
        for entry in record.get("fullTextUrlList", []) or []:
            url = entry.get("url") or entry.get("availability") or entry.get("site")
            if entry.get("url") and entry not in paper["full_text_urls"]:
                paper["full_text_urls"].append(entry)
            style = str(entry.get("documentStyle", "")).lower()
            if style == "pdf" or str(entry.get("url", "")).lower().endswith(".pdf"):
                paper["has_pdf_url_epmc"] = True


def parse_author_string(value: str) -> list[dict[str, str]]:
    authors = []
    for item in value.split(","):
        name = normalize_space(item)
        if not name:
            continue
        parts = name.split()
        authors.append({"name": name, "last": parts[0] if parts else name, "fore": " ".join(parts[1:])})
    return authors


def merge_crossref(papers: dict[str, dict[str, Any]], record: dict[str, Any]) -> None:
    doi = normalize_doi(record.get("doi"))
    if not doi:
        return
    key = f"doi:{doi}"
    paper = papers.setdefault(key, empty_paper())
    if "crossref" not in paper["sources"]:
        paper["sources"].append("crossref")
    paper["doi"] = paper["doi"] or doi
    paper["crossref_found"] = bool(record.get("found"))
    if record.get("found"):
        paper["title"] = merge_text(paper["title"], normalize_space(record.get("title", "")))
        if not paper["year"]:
            paper["year"] = record.get("year")
        if not paper["journal"]:
            paper["journal"] = normalize_space(record.get("journal", ""))
        paper["is_oa_crossref"] = paper["is_oa_crossref"] or bool(record.get("has_open_license"))
        paper["has_pdf_url_crossref"] = paper["has_pdf_url_crossref"] or bool(record.get("pdf_or_tdm_urls"))
        for url in record.get("license_urls", []) or []:
            if url and url not in paper["license_urls"]:
                paper["license_urls"].append(url)
        for url in record.get("pdf_or_tdm_urls", []) or []:
            entry = {"url": url, "source": "crossref"}
            if entry not in paper["full_text_urls"]:
                paper["full_text_urls"].append(entry)


def build_deduplicated_papers(
    pubmed_records: list[dict[str, Any]],
    epmc_records: list[dict[str, Any]],
    crossref_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    papers: dict[str, dict[str, Any]] = {}
    alias_map = build_alias_map(pubmed_records + epmc_records)
    for record in pubmed_records + epmc_records:
        merge_pubmed_or_epmc(papers, record, alias_map)
    for record in crossref_records:
        merge_crossref(papers, record)

    rows = []
    for key, paper in papers.items():
        paper["dedup_key"] = key
        paper["is_oa"] = bool(paper["is_oa_epmc"] or paper["is_oa_crossref"])
        paper["oa_with_pdf_url"] = bool(paper["has_pdf_url_epmc"] or paper["has_pdf_url_crossref"])
        paper["mesh_terms"] = sorted(set(paper["mesh_terms"]))
        paper["publication_types"] = sorted(set(paper["publication_types"]))
        paper["languages"] = sorted(set(paper["languages"]))
        rows.append(paper)
    rows.sort(key=lambda row: (row.get("year") or 9999, row.get("title") or ""))
    return rows


def rx(pattern: str, text: str, flags: int = re.I) -> bool:
    return re.search(pattern, text, flags) is not None


def count_rx(pattern: str, text: str, flags: int = re.I) -> int:
    return len(re.findall(pattern, text, flags))


def term_near_percent(term_pattern: str, text: str) -> bool:
    percent = r"\d+(?:\.\d+)?\s*(?:%|percent|w/w|w/v|v/v)"
    return bool(
        re.search(rf"(?:{term_pattern})[^.;:()\n]{{0,90}}{percent}", text, re.I)
        or re.search(rf"{percent}[^.;:()\n]{{0,90}}(?:{term_pattern})", text, re.I)
    )


def any_in_vitro_term(text: str) -> bool:
    return rx(r"\bin vitro\b|\bivpt\b|\bivrt\b|\bfranz\b|\bdiffusion cell\b|\bpermeation\b", text)


def audit_paper(track_key: str, paper: dict[str, Any]) -> dict[str, Any]:
    title = paper.get("title", "") or ""
    abstract = paper.get("abstract", "") or ""
    text = normalize_space(f"{title} {abstract}")
    text_l = text.lower()
    title_l = title.lower()

    endpoint_flags = {
        "has_flux_term": rx(r"\b(flux|jss|j_ss|steady[- ]state)\b", text_l),
        "has_cumulative_term": rx(r"\bcumulative\s+(amount|permeated|amount\s+permeated)\b", text_l),
        "has_kp_term": rx(r"\b(permeability\s+coefficient|kp|k_p)\b", text_l),
        "has_lag_term": rx(r"\blag[- ]?time\b", text_l),
    }
    method_flags = {
        "has_franz": rx(r"\bfranz\b", text_l),
        "has_ivpt_acronym": rx(r"\bivpt\b|\bivrt\b", text_l),
        "has_skin_type": rx(r"\b(human|porcine|pig|hairless mouse|strat-?m|silicone)\b.*?\b(skin|membrane)\b", text_l)
        or rx(r"\b(epidermis|dermatomed)\b", text_l),
        "has_ivivc": rx(r"\bivivc\b|in vitro.*in vivo", text_l),
    }

    negative_flags = {
        "is_review": rx(r"\breview\b|\bsystematic\b|\bmeta[- ]analysis\b", text_l)
        or any("review" in pub_type.lower() for pub_type in paper.get("publication_types", [])),
        "is_in_vivo_only": rx(r"\bvolunteer|\bhuman subject|\bclinical trial", text_l) and not any_in_vitro_term(text_l),
        "is_animal_pk_only": rx(r"\bplasma|\bpharmacokinetic", text_l) and not any_in_vitro_term(text_l),
        "is_iontophoresis_or_microneedle": rx(r"\bionto|\bmicroneedle|\belectroporation\b", text_l),
    }

    formulation_flags: dict[str, bool] = {}
    api_flags: dict[str, bool] = {}
    if track_key == "track_a_caffeine":
        api_flags = {
            "is_caffeine": rx(r"\bcaffeine\b", text_l),
            "is_nicotinamide": rx(r"\bnicotinamide\b|\bniacinamide\b", text_l),
            "is_lidocaine": rx(r"\blidocaine\b|\blignocaine\b", text_l),
            "is_ibuprofen": False,
        }
        formulation_flags = {
            "has_pg_pct": term_near_percent(r"\bpg\b|\bpropylene glycol\b", text_l),
            "has_etoh_pct": term_near_percent(r"\betoh\b|\bethanol\b|\bethanolic\b|\bethyl alcohol\b", text_l),
            "has_water_pct": term_near_percent(r"\bwater\b|\baqueous\b", text_l),
            "has_mineral_oil_pct": term_near_percent(r"\bmineral oil\b", text_l),
            "has_ipm_pct": term_near_percent(r"\bipm\b|\bisopropyl myristate\b", text_l),
        }
    else:
        api_flags = {
            "is_caffeine": False,
            "is_nicotinamide": False,
            "is_lidocaine": False,
            "is_ibuprofen": rx(r"\bibuprofen\b", text_l),
        }
        formulation_flags = {
            "has_carbopol_pct": term_near_percent(r"\bcarbopol\b", text_l),
            "has_hpmc_pct": term_near_percent(r"\bhpmc\b|\bhydroxypropyl methylcellulose\b", text_l),
            "has_poloxamer_pct": term_near_percent(r"\bpoloxamer\b|\bpluronic\b", text_l),
            "has_gel_word_in_title": rx(r"\bgel\b", title_l),
        }

    percent_value_count = count_rx(r"\d+(?:\.\d+)?\s*(?:%|percent|w/w|w/v|v/v)", text_l)
    has_percent_range = rx(r"\d+(?:\.\d+)?\s*(?:-|to|\u2013|\u2014)\s*\d+(?:\.\d+)?\s*(?:%|percent|w/w|w/v|v/v)", text_l)
    multi_terms_count = count_rx(
        r"\b(design of experiments|doe|factorial|response surface|mixture design|formulations?|vehicles?|ratios?|different|various|several|series|prepared|optimized|optimization|concentrations?|levels?|binary|ternary)\b",
        text_l,
    )
    endpoint_count = sum(1 for value in endpoint_flags.values() if value)
    method_positive_count = sum(
        1
        for key in ["has_franz", "has_ivpt_acronym", "has_skin_type"]
        if method_flags.get(key)
    )
    if track_key == "track_a_caffeine":
        api_positive = any(
            api_flags[key]
            for key in ["is_caffeine", "is_nicotinamide", "is_lidocaine"]
        )
    else:
        api_positive = bool(api_flags.get("is_ibuprofen"))
    quantitative_pct_flag = any(
        value
        for key, value in formulation_flags.items()
        if key != "has_gel_word_in_title"
    )
    modelling_ready_oa = bool(
        paper.get("is_oa")
        and api_positive
        and endpoint_count >= 1
        and method_positive_count >= 1
        and not negative_flags["is_review"]
        and not negative_flags["is_in_vivo_only"]
        and not negative_flags["is_animal_pk_only"]
    )
    candidate_score = (
        (multi_terms_count * 4)
        + (5 if has_percent_range else 0)
        + min(percent_value_count, 8)
        + (4 if method_flags["has_franz"] else 0)
        + (3 * endpoint_count)
        + (3 if quantitative_pct_flag else 0)
        + ((paper.get("year") or 0) - 1990) / 20
    )
    audit = {
        **api_flags,
        **endpoint_flags,
        **method_flags,
        **formulation_flags,
        **negative_flags,
        "has_percent_range": has_percent_range,
        "percent_value_count": percent_value_count,
        "multi_formulation_terms": multi_terms_count,
        "endpoint_signal_count": endpoint_count,
        "method_signal_count": method_positive_count,
        "with_quantitative_pct_in_abstract": quantitative_pct_flag,
        "modelling_ready_oa": modelling_ready_oa,
        "candidate_score": round(candidate_score, 3),
    }
    return audit


def audit_rows(track_key: str, papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for paper in papers:
        audit = audit_paper(track_key, paper)
        paper["audit"] = audit
        row = {
            "dedup_key": paper.get("dedup_key", ""),
            "doi": paper.get("doi", ""),
            "pmid": paper.get("pmid", ""),
            "year": paper.get("year", ""),
            "journal": paper.get("journal", ""),
            "title": paper.get("title", ""),
            "is_oa": paper.get("is_oa", False),
            "oa_with_pdf_url": paper.get("oa_with_pdf_url", False),
            **audit,
        }
        rows.append(row)
    return rows


AUDIT_FIELDNAMES = [
    "dedup_key",
    "doi",
    "pmid",
    "year",
    "journal",
    "title",
    "is_oa",
    "oa_with_pdf_url",
    "is_caffeine",
    "is_nicotinamide",
    "is_lidocaine",
    "is_ibuprofen",
    "has_flux_term",
    "has_cumulative_term",
    "has_kp_term",
    "has_lag_term",
    "has_franz",
    "has_ivpt_acronym",
    "has_skin_type",
    "has_ivivc",
    "has_pg_pct",
    "has_etoh_pct",
    "has_water_pct",
    "has_mineral_oil_pct",
    "has_ipm_pct",
    "has_carbopol_pct",
    "has_hpmc_pct",
    "has_poloxamer_pct",
    "has_gel_word_in_title",
    "is_review",
    "is_in_vivo_only",
    "is_animal_pk_only",
    "is_iontophoresis_or_microneedle",
    "has_percent_range",
    "percent_value_count",
    "multi_formulation_terms",
    "endpoint_signal_count",
    "method_signal_count",
    "with_quantitative_pct_in_abstract",
    "modelling_ready_oa",
    "candidate_score",
]


def api_breakdown(papers: list[dict[str, Any]]) -> str:
    counts = {
        "caffeine": sum(1 for p in papers if p["audit"].get("is_caffeine")),
        "nicotinamide": sum(1 for p in papers if p["audit"].get("is_nicotinamide")),
        "lidocaine": sum(1 for p in papers if p["audit"].get("is_lidocaine")),
    }
    multi = sum(
        1
        for p in papers
        if sum(
            [
                bool(p["audit"].get("is_caffeine")),
                bool(p["audit"].get("is_nicotinamide")),
                bool(p["audit"].get("is_lidocaine")),
            ]
        )
        > 1
    )
    return (
        f"caffeine={counts['caffeine']}, nicotinamide={counts['nicotinamide']}, "
        f"lidocaine={counts['lidocaine']}, multi-API={multi}"
    )


def build_summary_row(
    track_key: str,
    pubmed_count: int,
    epmc_count: int,
    papers: list[dict[str, Any]],
) -> dict[str, Any]:
    modelling_ready = [p for p in papers if p["audit"].get("modelling_ready_oa")]
    pct_count = sum(1 for p in papers if p["audit"].get("with_quantitative_pct_in_abstract"))
    years = [p.get("year") for p in papers if p.get("year")]
    pre_2010 = sum(1 for year in years if year < 2010)
    post_2015 = sum(1 for year in years if year > 2015)
    return {
        "track": TRACKS[track_key]["summary_track"],
        "pubmed_hits": pubmed_count,
        "epmc_hits": epmc_count,
        "unique_papers": len(papers),
        "oa_papers": sum(1 for p in papers if p.get("is_oa")),
        "oa_with_pdf_url": sum(1 for p in papers if p.get("is_oa") and p.get("oa_with_pdf_url")),
        "modelling_ready_oa": len(modelling_ready),
        "with_franz_in_abstract": sum(1 for p in modelling_ready if p["audit"].get("has_franz")),
        "with_quantitative_pct_in_abstract": pct_count,
        "pre_2010_pct": round((pre_2010 / len(years) * 100), 1) if years else 0.0,
        "post_2015_pct": round((post_2015 / len(years) * 100), 1) if years else 0.0,
        "api_breakdown": api_breakdown(papers) if track_key == "track_a_caffeine" else "",
    }


SUMMARY_FIELDNAMES = [
    "track",
    "pubmed_hits",
    "epmc_hits",
    "unique_papers",
    "oa_papers",
    "oa_with_pdf_url",
    "modelling_ready_oa",
    "with_franz_in_abstract",
    "with_quantitative_pct_in_abstract",
    "pre_2010_pct",
    "post_2015_pct",
    "api_breakdown",
]


def modelling_ready_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [paper for paper in papers if paper["audit"].get("modelling_ready_oa")]


def formulation_coverage(track_key: str, papers: list[dict[str, Any]]) -> dict[str, int]:
    ready = modelling_ready_papers(papers)
    if track_key == "track_a_caffeine":
        keys = ["has_pg_pct", "has_etoh_pct", "has_water_pct", "has_mineral_oil_pct", "has_ipm_pct"]
    else:
        keys = ["has_carbopol_pct", "has_hpmc_pct", "has_poloxamer_pct", "has_gel_word_in_title"]
    coverage = {key: sum(1 for p in ready if p["audit"].get(key)) for key in keys}
    coverage["any_pct_excipient"] = sum(1 for p in ready if p["audit"].get("with_quantitative_pct_in_abstract"))
    coverage["has_percent_range"] = sum(1 for p in ready if p["audit"].get("has_percent_range"))
    coverage["multi_pct_values"] = sum(1 for p in ready if p["audit"].get("percent_value_count", 0) >= 2)
    return coverage


def formulation_diversity(track_key: str, papers: list[dict[str, Any]]) -> int:
    coverage = formulation_coverage(track_key, papers)
    if track_key == "track_a_caffeine":
        keys = ["has_pg_pct", "has_etoh_pct", "has_water_pct", "has_mineral_oil_pct", "has_ipm_pct"]
    else:
        keys = ["has_carbopol_pct", "has_hpmc_pct", "has_poloxamer_pct"]
    return sum(1 for key in keys if coverage.get(key, 0) > 0)


def candidate_papers(
    papers: list[dict[str, Any]],
    limit: int,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    pool = modelling_ready_papers(papers)
    if api_key:
        pool = [paper for paper in pool if paper["audit"].get(api_key)]
    ranked = sorted(
        pool,
        key=lambda p: (
            p["audit"].get("multi_formulation_terms", 0),
            bool(p["audit"].get("has_percent_range")),
            bool(p["audit"].get("has_franz")),
            p["audit"].get("endpoint_signal_count", 0),
            p["audit"].get("percent_value_count", 0),
            p.get("year") or 0,
            p["audit"].get("candidate_score", 0),
        ),
        reverse=True,
    )
    return ranked[:limit]


def paper_identifier(paper: dict[str, Any]) -> str:
    if paper.get("doi"):
        return f"doi:{paper['doi']}"
    if paper.get("pmid"):
        return f"pmid:{paper['pmid']}"
    return paper.get("dedup_key", "")


def api_tags(paper: dict[str, Any]) -> str:
    tags = []
    if paper["audit"].get("is_caffeine"):
        tags.append("caffeine")
    if paper["audit"].get("is_nicotinamide"):
        tags.append("nicotinamide")
    if paper["audit"].get("is_lidocaine"):
        tags.append("lidocaine")
    return ", ".join(tags) if tags else "-"


def candidate_signal_text(paper: dict[str, Any]) -> str:
    audit = paper["audit"]
    signals = []
    if audit.get("multi_formulation_terms"):
        signals.append(f"multi_terms={audit['multi_formulation_terms']}")
    if audit.get("has_percent_range"):
        signals.append("range_pct")
    if audit.get("percent_value_count"):
        signals.append(f"pct_values={audit['percent_value_count']}")
    if audit.get("has_franz"):
        signals.append("Franz")
    endpoint_names = [
        key.replace("has_", "").replace("_term", "")
        for key in ["has_flux_term", "has_cumulative_term", "has_kp_term", "has_lag_term"]
        if audit.get(key)
    ]
    if endpoint_names:
        signals.append("endpoints=" + "/".join(endpoint_names))
    if audit.get("is_iontophoresis_or_microneedle"):
        signals.append("ionto/microneedle")
    return "; ".join(signals) if signals else "-"


def markdown_candidates(candidates: list[dict[str, Any]], include_api: bool) -> list[str]:
    if not candidates:
        return ["No OA modelling-ready candidates under the regex screen."]
    header = "| Rank | Year | API | Identifier | Journal | Title | Signals |" if include_api else "| Rank | Year | Identifier | Journal | Title | Signals |"
    sep = "|---:|---:|---|---|---|---|---|" if include_api else "|---:|---:|---|---|---|---|"
    lines = [header, sep]
    for idx, paper in enumerate(candidates, start=1):
        title = (paper.get("title") or "").replace("|", "/")
        if len(title) > 130:
            title = title[:127] + "..."
        journal = (paper.get("journal") or "").replace("|", "/")
        if len(journal) > 40:
            journal = journal[:37] + "..."
        if include_api:
            lines.append(
                f"| {idx} | {paper.get('year') or ''} | {api_tags(paper)} | {paper_identifier(paper)} | "
                f"{journal} | {title} | {candidate_signal_text(paper)} |"
            )
        else:
            lines.append(
                f"| {idx} | {paper.get('year') or ''} | {paper_identifier(paper)} | "
                f"{journal} | {title} | {candidate_signal_text(paper)} |"
            )
    return lines


def year_histogram_lines(papers: list[dict[str, Any]]) -> list[str]:
    years = Counter(p.get("year") for p in modelling_ready_papers(papers) if p.get("year"))
    if not years:
        return ["No publication years available for OA modelling-ready papers."]
    lines = ["| Year | Count | Histogram |", "|---:|---:|---|"]
    for year in sorted(years):
        count = years[year]
        bar = "#" * min(count, 40)
        lines.append(f"| {year} | {count} | `{bar}` |")
    return lines


def concentration_summary(papers: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    ready = modelling_ready_papers(papers)
    journal_counts = Counter(p.get("journal") or "Unknown" for p in ready)
    author_counts: Counter[str] = Counter()
    for paper in ready:
        authors = paper.get("authors", []) or []
        for author in authors[:1] + authors[-1:]:
            last = normalize_space(author.get("last") or author.get("name") or "")
            if last:
                author_counts[last] += 1
    top_journals = [
        f"{journal}={count} ({count / len(ready) * 100:.1f}%)"
        for journal, count in journal_counts.most_common(5)
    ] if ready else []
    top_authors = [
        f"{author}={count} ({count / len(ready) * 100:.1f}%)"
        for author, count in author_counts.most_common(5)
    ] if ready else []
    return top_journals, top_authors


def language_summary(papers: list[dict[str, Any]]) -> str:
    languages = Counter()
    for paper in papers:
        vals = paper.get("languages") or ["unknown"]
        for value in vals:
            languages[value or "unknown"] += 1
    if not languages:
        return "No language metadata."
    return ", ".join(f"{key}={value}" for key, value in languages.most_common())


def decision_class(modelling_ready_count: int, multi_form_candidates: int) -> str:
    if modelling_ready_count >= 30 and multi_form_candidates >= 5:
        return "Strong"
    if 15 <= modelling_ready_count < 30:
        return "Marginal"
    return "Weak"


def choose_recommendation(track_data: dict[str, dict[str, Any]]) -> tuple[str, str]:
    ranked = []
    class_rank = {"Weak": 0, "Marginal": 1, "Strong": 2}
    for track_key, data in track_data.items():
        ready_count = len(modelling_ready_papers(data["papers"]))
        candidate_count = len(candidate_papers(data["papers"], 10))
        cls = decision_class(ready_count, candidate_count)
        diversity = formulation_diversity(track_key, data["papers"])
        ranked.append((class_rank[cls], ready_count, diversity, track_key, cls, candidate_count))
    ranked.sort(reverse=True)
    best = ranked[0]
    if best[0] == 0:
        return "NEITHER", "Both tracks are weak under the regex-only OA modelling-ready screen."
    if best[3] == "track_a_caffeine":
        return "A", f"Track A has {best[1]} OA modelling-ready papers, {best[5]} ranked multi-formulation candidates, and formulation diversity across {best[2]} excipient classes."
    return "B", f"Track B has {best[1]} OA modelling-ready papers, {best[5]} ranked multi-formulation candidates, and formulation diversity across {best[2]} matrix classes."


def build_report(track_data: dict[str, dict[str, Any]], summary_rows: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Phase 0a Literature Density Scouting")
    lines.append("")
    lines.append("Metadata-only scout using PubMed E-utilities, Europe PMC OA search, Crossref metadata, and deterministic regex audit. No full-text PDFs were downloaded and no LLM scoring was used.")
    lines.append("")

    lines.append("## 1. OA modelling-ready counts")
    lines.append("")
    lines.append("| Track | PubMed hits | Europe PMC OA hits | Unique papers | OA papers | OA + PDF URL | OA modelling-ready | Franz | Non-Franz | With % composition | Without % composition |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in summary_rows:
        track_key = "track_a_caffeine" if row["track"] == "A_caffeine" else "track_b_ibuprofen_gel"
        ready = modelling_ready_papers(track_data[track_key]["papers"])
        franz = sum(1 for p in ready if p["audit"].get("has_franz"))
        pct_ready = sum(1 for p in ready if p["audit"].get("with_quantitative_pct_in_abstract"))
        lines.append(
            f"| {row['track']} | {row['pubmed_hits']} | {row['epmc_hits']} | {row['unique_papers']} | "
            f"{row['oa_papers']} | {row['oa_with_pdf_url']} | {row['modelling_ready_oa']} | "
            f"{franz} | {len(ready) - franz} | {pct_ready} | {len(ready) - pct_ready} |"
        )
    lines.append("")
    for track_key, data in track_data.items():
        lines.append(f"### {TRACKS[track_key]['report_label']}: publication-year histogram")
        lines.extend(year_histogram_lines(data["papers"]))
        lines.append("")

    lines.append("## 2. Formulation-factor coverage")
    lines.append("")
    for track_key, data in track_data.items():
        ready = modelling_ready_papers(data["papers"])
        coverage = formulation_coverage(track_key, data["papers"])
        lines.append(f"### {TRACKS[track_key]['report_label']}")
        lines.append(f"Coverage below is counted within {len(ready)} OA modelling-ready papers.")
        if track_key == "track_a_caffeine":
            lines.append(
                f"PG with numeric %: {coverage['has_pg_pct']}; EtOH with numeric %: {coverage['has_etoh_pct']}; "
                f"water with numeric %: {coverage['has_water_pct']}; mineral oil with numeric %: {coverage['has_mineral_oil_pct']}; "
                f"IPM with numeric %: {coverage['has_ipm_pct']}."
            )
        else:
            lines.append(
                f"Carbopol with numeric %: {coverage['has_carbopol_pct']}; HPMC with numeric %: {coverage['has_hpmc_pct']}; "
                f"Poloxamer/Pluronic with numeric %: {coverage['has_poloxamer_pct']}; gel word in title: {coverage['has_gel_word_in_title']}."
            )
        lines.append(
            f"Multi-ratio proxy: {coverage['has_percent_range']} papers have explicit % ranges and "
            f"{coverage['multi_pct_values']} papers have at least two percentage values in title/abstract."
        )
        lines.append("")

    lines.append("## 3. Source/target paper candidates")
    lines.append("")
    for track_key, data in track_data.items():
        lines.append(f"### {TRACKS[track_key]['report_label']}: top candidates")
        lines.extend(markdown_candidates(candidate_papers(data["papers"], 10), include_api=(track_key == "track_a_caffeine")))
        lines.append("")
        if track_key == "track_a_caffeine":
            per_api = [
                ("caffeine", "is_caffeine"),
                ("nicotinamide/niacinamide", "is_nicotinamide"),
                ("lidocaine/lignocaine", "is_lidocaine"),
            ]
            for label, key in per_api:
                lines.append(f"#### Track A per-API top candidates: {label}")
                lines.extend(markdown_candidates(candidate_papers(data["papers"], 5, api_key=key), include_api=True))
                lines.append("")

    lines.append("## 4. Recommendation")
    lines.append("")
    lines.append("| Track | Signal class | OA modelling-ready | Ranked multi-formulation candidates | Formulation diversity count |")
    lines.append("|---|---|---:|---:|---:|")
    for track_key, data in track_data.items():
        ready_count = len(modelling_ready_papers(data["papers"]))
        candidate_count = len(candidate_papers(data["papers"], 10))
        cls = decision_class(ready_count, candidate_count)
        diversity = formulation_diversity(track_key, data["papers"])
        lines.append(f"| {TRACKS[track_key]['summary_track']} | {cls} | {ready_count} | {candidate_count} | {diversity} |")
    recommendation, reason = choose_recommendation(track_data)
    lines.append("")
    lines.append(f"Decision: {recommendation}. {reason}")
    lines.append("")

    lines.append("## 5. Risks / caveats")
    lines.append("")
    for track_key, data in track_data.items():
        papers = data["papers"]
        ready = modelling_ready_papers(papers)
        ionto = sum(1 for p in ready if p["audit"].get("is_iontophoresis_or_microneedle"))
        top_journals, top_authors = concentration_summary(papers)
        pubmed_hits = data["pubmed_count"]
        if track_key == "track_a_caffeine" and pubmed_hits < 500:
            prior_note = "PubMed hits are well below the rough prior of 500-1500, so the prior was optimistic for the exact vehicle-constrained query."
        elif track_key == "track_b_ibuprofen_gel" and pubmed_hits < 150:
            prior_note = "PubMed hits are below the rough prior of 150-500, so the prior was optimistic for the exact gel query."
        else:
            prior_note = "PubMed hits are within the rough prior range."
        lines.append(f"### {TRACKS[track_key]['report_label']}")
        lines.append(f"Ionto/microneedle/electroporation dilution risk: {ionto}/{len(ready)} OA modelling-ready papers flagged.")
        lines.append(f"Journal concentration among OA modelling-ready papers: {', '.join(top_journals) if top_journals else 'none'}." )
        lines.append(f"First/senior author concentration proxy: {', '.join(top_authors) if top_authors else 'none'}." )
        lines.append(f"Language metadata across unique papers: {language_summary(papers)}.")
        lines.append(prior_note)
        lines.append("")

    lines.append(f"RECOMMENDED TRACK: {recommendation} | {reason}")
    lines.append("")
    return "\n".join(lines)


def collect_track(track_key: str, config: dict[str, Any]) -> dict[str, Any]:
    track_dir = OUTPUT_ROOT / track_key
    track_dir.mkdir(parents=True, exist_ok=True)

    pubmed_count, pubmed_records = fetch_pubmed_records(track_key, config["pubmed_query"])
    write_jsonl(track_dir / "pubmed_hits.jsonl", pubmed_records)

    epmc_count, epmc_records = fetch_epmc_records(track_key, config["epmc_query"])
    write_jsonl(track_dir / "europepmc_hits.jsonl", epmc_records)

    dois = sorted(
        {
            normalize_doi(record.get("doi"))
            for record in pubmed_records + epmc_records
            if normalize_doi(record.get("doi"))
        }
    )
    crossref_records = fetch_crossref_records(track_key, dois)
    write_jsonl(track_dir / "crossref_hits.jsonl", crossref_records)

    papers = build_deduplicated_papers(pubmed_records, epmc_records, crossref_records)
    if len(papers) < 30:
        log(f"WARNING: {track_key} produced fewer than 30 unique papers ({len(papers)}).")
    audit = audit_rows(track_key, papers)
    write_jsonl(track_dir / "deduplicated_papers.jsonl", papers)
    write_csv(track_dir / "abstract_signal_audit.csv", audit, AUDIT_FIELDNAMES)

    return {
        "pubmed_count": pubmed_count,
        "epmc_count": epmc_count,
        "pubmed_records": pubmed_records,
        "epmc_records": epmc_records,
        "crossref_records": crossref_records,
        "papers": papers,
        "audit": audit,
    }


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    track_data: dict[str, dict[str, Any]] = {}
    for track_key, config in TRACKS.items():
        track_data[track_key] = collect_track(track_key, config)

    summary_rows = [
        build_summary_row(
            track_key,
            data["pubmed_count"],
            data["epmc_count"],
            data["papers"],
        )
        for track_key, data in track_data.items()
    ]
    write_csv(OUTPUT_ROOT / "comparison_summary.csv", summary_rows, SUMMARY_FIELDNAMES)
    report = build_report(track_data, summary_rows)
    REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")

    log(f"Wrote {OUTPUT_ROOT / 'comparison_summary.csv'}")
    log(f"Wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
