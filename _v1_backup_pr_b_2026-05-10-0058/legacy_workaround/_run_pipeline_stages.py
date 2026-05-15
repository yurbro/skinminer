from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assembly.assemble_records import assemble_records
from detection.router import route_papers
from extractors.figure.build_records import extract_batch as extract_figure_batch
from extractors.table.extractor import extract_batch as extract_table_batch
from extractors.text.extractor import extract_batch as extract_text_batch
from patchers.patch_api_concentration import patch_api_concentration
from patchers.patch_area import patch_area
from patchers.patch_endpoint import patch_endpoint_value
from patchers.patch_endpoint_time import patch_endpoint_time
from policies import V4AcceptFluxPolicy
from schemas.models import ContentAccess, ExtractorRunContext, Record, RouteDecision
from utils.io import write_jsonl, write_records_jsonl
from verification.verify_records import verify_records


OUTPUT_ROOT = ROOT / "outputs" / "watkinson_dryrun"
MODEL = "gpt-4o-mini"
LLM_PROVIDER = "openai"

PAPERS = [
    {
        "paper_id": "Watkinson_2009_I",
        "doi": "10.1159/000183922",
        "title": "Influence of Ethanol/Water Cosolvent Systems on Ibuprofen Skin Permeation. I.",
        "year": 2009,
        "pdf": ROOT / "papers" / "uploaded_external" / "watkinson_2009_I.pdf",
        "expected": 13,
    },
    {
        "paper_id": "Watkinson_2009_II",
        "doi": "10.1159/000231528",
        "title": "Influence of Propylene Glycol/Water and Ethanol/Propylene Glycol/Water Cosolvent Systems on Ibuprofen Skin Permeation. II.",
        "year": 2009,
        "pdf": ROOT / "papers" / "uploaded_external" / "watkinson_2009_II.pdf",
        "expected": 20,
    },
    {
        "paper_id": "Watkinson_2011_III",
        "doi": "10.1159/000315139",
        "title": "Influence of Oleic Acid/Medium Chain Glycerides Lipophilic Vehicles on Ibuprofen Skin Permeation. III.",
        "year": 2011,
        "pdf": ROOT / "papers" / "uploaded_external" / "watkinson_2011_III.pdf",
        "expected": 14,
    },
]


def progress(stage: str):
    def _callback(done: int, item: str, detail: str = "") -> None:
        print(f"[{stage}] {done} {item} {detail}".strip(), flush=True)

    return _callback


def write_empty(path: Path) -> None:
    write_jsonl([], path)


def dump_alias(source: Path, alias: Path) -> None:
    if source.exists():
        alias.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def select_pairs(
    handle: ContentAccess,
    decision: RouteDecision,
    routes: set[str],
) -> list[tuple[ContentAccess, RouteDecision]]:
    return [(handle, decision)] if decision.route in routes else []


def run_one(paper: dict, policy: V4AcceptFluxPolicy) -> dict:
    paper_id = paper["paper_id"]
    out_dir = OUTPUT_ROOT / paper_id
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = Path(paper["pdf"])
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    handle = ContentAccess(
        paper_id=paper_id,
        doi=paper["doi"],
        title=paper["title"],
        preferred_format="pdf",
        available_formats=["pdf"],
        local_paths={"pdf": str(pdf_path)},
        status="downloaded",
        notes=[
            "manual_corpus_workaround=true",
            "source=user_uploaded_external_pdf",
            "entry_point=manual ContentAccess local_paths.pdf from router stage",
        ],
    )
    route_input = {
        "paper_id": paper_id,
        "doi": paper["doi"],
        "title": paper["title"],
        "year": paper["year"],
        "preferred_format": "pdf",
        "available_formats": ["pdf"],
        "access_urls": {},
        "local_paths": {"pdf": str(pdf_path)},
        "access_status": "downloaded",
        "pdf_path": str(pdf_path),
        "manual_corpus_workaround": True,
    }
    write_jsonl([route_input], out_dir / "manual_corpus.jsonl")
    write_jsonl([handle], out_dir / "content_access.jsonl")

    print(f"\n[WATKINSON] {paper_id}: routing", flush=True)
    decisions = route_papers(
        [route_input],
        model=MODEL,
        output_jsonl=out_dir / "route_decisions.jsonl",
        output_csv=None,
        max_retries=3,
        progress_every=1,
        checkpoint_every=1,
        progress_callback=progress(f"{paper_id}:router"),
        resume_jsonl=out_dir / "route_decisions.jsonl",
        llm_provider=LLM_PROVIDER,
    )
    dump_alias(out_dir / "route_decisions.jsonl", out_dir / "router_decision.jsonl")
    decision = decisions[0] if decisions else RouteDecision(paper_id=paper_id, doi=paper["doi"], title=paper["title"])

    run_context = ExtractorRunContext(
        run_id=f"watkinson_dryrun_{paper_id}",
        model_name=MODEL,
        stage_models={
            "routing": MODEL,
            "text_extract": MODEL,
            "table_extract": MODEL,
            "figure_triage": MODEL,
            "figure_vlm": MODEL,
            "figure_map": MODEL,
        },
        output_dir=str(out_dir),
        prompt_paths=[
            "detection/router.py",
            "extractors/text/extract_fields.py",
            "extractors/table/extractor.py",
            "extractors/figure/triage.py",
            "extractors/figure/vlm_digitize.py",
            "extractors/figure/map_curves.py",
        ],
        config_paths=["policies/v4_accept_flux.py"],
        notes=["Watkinson dry-run manual local PDF orchestration; SkinMiner source code unchanged."],
        fail_on_malformed_output=False,
        shared_state={
            "llm_provider": LLM_PROVIDER,
            "figure_failures_by_paper": {},
            "curve_hints_by_paper": {},
        },
    )

    table_pairs = select_pairs(handle, decision, {"table", "mixed", "figure"})
    text_pairs = select_pairs(handle, decision, {"text", "mixed"})
    figure_pairs = select_pairs(handle, decision, {"figure"})

    print(f"[WATKINSON] {paper_id}: table extraction route={decision.route}", flush=True)
    table_records = extract_table_batch(
        table_pairs,
        policy=policy,
        run_context=run_context,
        output_jsonl=out_dir / "table_records.jsonl",
        raw_output_jsonl=out_dir / "table_raw.jsonl",
        output_csv=None,
        progress_callback=progress(f"{paper_id}:table"),
        checkpoint_every=1,
    )
    if not table_pairs:
        write_empty(out_dir / "table_records.jsonl")
        write_empty(out_dir / "table_raw.jsonl")

    print(f"[WATKINSON] {paper_id}: text extraction route={decision.route}", flush=True)
    text_records = extract_text_batch(
        text_pairs,
        policy=policy,
        run_context=run_context,
        output_jsonl=out_dir / "text_records.jsonl",
        raw_output_jsonl=out_dir / "text_raw.jsonl",
        output_csv=None,
        progress_callback=progress(f"{paper_id}:text"),
        checkpoint_every=1,
    )
    if not text_pairs:
        write_empty(out_dir / "text_records.jsonl")
        write_empty(out_dir / "text_raw.jsonl")

    if figure_pairs:
        print(f"[WATKINSON] {paper_id}: figure extraction route={decision.route}", flush=True)
        figure_records = extract_figure_batch(
            figure_pairs,
            policy=policy,
            run_context=run_context,
            output_jsonl=out_dir / "figure_records.jsonl",
            output_csv=None,
            triage_jsonl=out_dir / "figure_triage.jsonl",
            digitized_curves_jsonl=out_dir / "figure_curves.jsonl",
            digitized_endpoints_jsonl=out_dir / "figure_endpoints.jsonl",
            vlm_jsonl=out_dir / "figure_vlm_readings.jsonl",
            mapping_jsonl=out_dir / "figure_curve_map.jsonl",
            progress_callback=progress(f"{paper_id}:figure"),
            checkpoint_every=1,
        )
    else:
        figure_records = []
        write_empty(out_dir / "figure_records.jsonl")
        write_empty(out_dir / "figure_triage.jsonl")
        write_empty(out_dir / "figure_curves.jsonl")
        write_empty(out_dir / "figure_endpoints.jsonl")
        write_empty(out_dir / "figure_vlm_readings.jsonl")
        write_empty(out_dir / "figure_curve_map.jsonl")

    print(f"[WATKINSON] {paper_id}: assembly and verification", flush=True)
    assembled = assemble_records(
        [table_records, text_records, figure_records],
        include_table_partials=False,
        enable_table_promotion=True,
        shared_state=run_context.shared_state,
        output_jsonl=out_dir / "assembled_records.jsonl",
        output_csv=None,
        progress_callback=progress(f"{paper_id}:assembly"),
    )
    initial_verified = verify_records(
        assembled,
        policy=policy,
        output_jsonl=out_dir / "verified_initial.jsonl",
        output_csv=None,
        progress_callback=progress(f"{paper_id}:verify_initial"),
    )
    patched: Iterable[Record] = patch_api_concentration(
        initial_verified,
        output_jsonl=out_dir / "patched_api_concentration.jsonl",
        progress_callback=progress(f"{paper_id}:patch_api"),
    )
    patched = patch_endpoint_value(
        patched,
        output_jsonl=out_dir / "patched_endpoint_value.jsonl",
        progress_callback=progress(f"{paper_id}:patch_endpoint"),
    )
    patched = patch_endpoint_time(
        patched,
        output_jsonl=out_dir / "patched_endpoint_time.jsonl",
        progress_callback=progress(f"{paper_id}:patch_time"),
    )
    patched = patch_area(
        patched,
        output_jsonl=out_dir / "patched_area.jsonl",
        progress_callback=progress(f"{paper_id}:patch_area"),
    )
    verified = verify_records(
        patched,
        policy=policy,
        output_jsonl=out_dir / "verified_records.jsonl",
        output_csv=None,
        progress_callback=progress(f"{paper_id}:verify_final"),
    )

    write_records_jsonl(verified, out_dir / "verified_records.jsonl")
    return {
        "paper_id": paper_id,
        "doi": paper["doi"],
        "route": decision.route,
        "expected": paper["expected"],
        "table_records": len(table_records),
        "text_records": len(text_records),
        "figure_records": len(figure_records),
        "assembled_records": len(assembled),
        "final_records_evaluated": len(verified),
        "verified": sum(1 for record in verified if record.verification_status == "verified"),
        "unresolved": sum(1 for record in verified if record.verification_status == "unresolved"),
        "rejected": sum(1 for record in verified if record.verification_status == "rejected"),
    }


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    policy = V4AcceptFluxPolicy()
    summaries = []
    for paper in PAPERS:
        summaries.append(run_one(paper, policy))
    write_jsonl(summaries, OUTPUT_ROOT / "stage_run_summary.jsonl")
    print("\n[WATKINSON DRY-RUN] Stage execution complete.", flush=True)
    for row in summaries:
        print(
            f"  {row['paper_id']} ({row['doi']}): expected {row['expected']} / "
            f"table {row['table_records']} / assembled {row['assembled_records']} / "
            f"verified {row['verified']} / unresolved {row['unresolved']} / rejected {row['rejected']} / route {row['route']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
