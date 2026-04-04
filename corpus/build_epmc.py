from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import requests

from corpus.query_profiles import DEFAULT_QUERY, DEFAULT_QUERY_PROFILE, build_epmc_query, get_query_profile, list_query_profiles
from utils.io import write_jsonl, write_optional_csv

BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
DEFAULT_PAGE_SIZE = 1000
DEFAULT_SLEEP_SECONDS = 0.2


def epmc_search_all(
    query: str,
    max_records: int = 50_000,
    page_size: int = DEFAULT_PAGE_SIZE,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
) -> pd.DataFrame:
    cursor = "*"
    rows: list[dict[str, object]] = []
    fetched = 0

    while True:
        response = requests.get(
            BASE_URL,
            params={
                "query": query,
                "format": "json",
                "pageSize": page_size,
                "cursorMark": cursor,
                "resultType": "core",
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        hits = payload.get("resultList", {}).get("result", [])
        if not hits:
            break

        for item in hits:
            rows.append(
                {
                    "source": item.get("source"),
                    "id": item.get("id"),
                    "pmid": item.get("pmid"),
                    "pmcid": item.get("pmcid"),
                    "doi": item.get("doi"),
                    "title": item.get("title"),
                    "abstract": item.get("abstractText"),
                    "year": item.get("pubYear"),
                    "journal": item.get("journalTitle"),
                    "authors": item.get("authorString"),
                    "url": item.get("doiUrl")
                    or item.get("pmidUrl")
                    or (item.get("fullTextUrlList", {}).get("fullTextUrl", [{}]) or [{}])[0].get("url"),
                    "query_used": query,
                }
            )
            fetched += 1
            if fetched >= max_records:
                break

        if fetched >= max_records:
            break

        next_cursor = payload.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(sleep_seconds)

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    frame["title"] = frame["title"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
    frame["abstract"] = frame["abstract"].fillna("").str.replace(r"\s+", " ", regex=True).str.strip()
    frame["doi"] = frame["doi"].fillna("").str.lower().str.strip()
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    frame = frame.sort_values(["doi", "year"], na_position="last")
    frame = frame.drop_duplicates(subset=["doi"], keep="first")
    frame = frame.drop_duplicates(subset=["title", "year"], keep="first")
    return frame.reset_index(drop=True)


def build_corpus(
    query: str = DEFAULT_QUERY,
    max_results: int = 50_000,
    output_jsonl: str | Path | None = None,
    output_csv: str | Path | None = None,
) -> list[dict[str, object]]:
    frame = epmc_search_all(query=query, max_records=max_results)
    rows = frame.to_dict("records")
    if output_jsonl:
        write_jsonl(rows, output_jsonl)
    if output_csv:
        write_optional_csv(rows, output_csv)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an OA-focused Europe PMC corpus.")
    parser.add_argument("--query", type=str, default=None)
    parser.add_argument("--query-profile", type=str, default=DEFAULT_QUERY_PROFILE)
    parser.add_argument("--list-query-profiles", action="store_true")
    parser.add_argument("--max-results", type=int, default=50_000)
    parser.add_argument("--output-jsonl", type=Path, default=Path("outputs/corpus_ibuprofen.jsonl"))
    parser.add_argument("--output-csv", type=Path, default=Path("data/corpus_ibuprofen.csv"))
    args = parser.parse_args()

    if args.list_query_profiles:
        for profile in list_query_profiles():
            print(f"{profile.name}\t{profile.version}\t{profile.description}")
        return

    query_profile = get_query_profile(args.query_profile)
    query = args.query or query_profile.query

    rows = build_corpus(
        query=query,
        max_results=args.max_results,
        output_jsonl=args.output_jsonl,
        output_csv=args.output_csv,
    )
    print(f"Corpus rows: {len(rows)}")
    print(f"Query profile: {query_profile.name} ({query_profile.version})")
    print(f"Saved JSONL: {args.output_jsonl}")
    print(f"Saved CSV: {args.output_csv}")


if __name__ == "__main__":
    main()
