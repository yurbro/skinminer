# Round 1 Migration Notes

This round reorganizes the existing step-based research scripts into package modules while intentionally preserving legacy scientific logic wherever possible.

## Script Mapping

| Legacy script | New module | Round 1 note |
| --- | --- | --- |
| `scripts/step1_build_corpus_epmc.py` | `corpus/build_epmc.py` | Retrieval and deduplication preserved, query and outputs made configurable. |
| `scripts/step2_rule_screen.py` | `triage/rule_filter.py` | Heuristic screening preserved, now returns relevance labels and hints. |
| `scripts/step3_stage2_openai.py` | `triage/llm_triage.py` | Structured abstract triage preserved with centralized prompt wiring. |
| `scripts/step4_2_make_fulltext_inventory.py` | `access/resolve_content.py` | Inventory concept replaced by normalized OA content access objects. |
| `scripts/step4_3_download_fulltext_oa.py` | `access/resolve_content.py` | OA URL discovery and optional download consolidated under content resolution. |
| `scripts/step5_evidence_index_openai_v1_3.py` | `detection/router.py` | Evidence indexing now feeds route decisions plus anchor evidence. |
| `scripts/step6_extract_records_openai_v1_2.py` | `extractors/text/extractor.py` | Legacy PDF text extraction adapted into unified `Record` output. |
| `scripts/step6_5_verify_openai.py` | `verification/verify_records.py` | Round 1 keeps a lighter policy-first verifier and adds a TODO for legacy page-grounded verification reintegration. |
| `scripts/step7_formulation_table_extract_openai.py` | `extractors/table/extractor.py` | Formulation tables now emit partial formulation-backed records for later assembly. |
| `scripts/step7_figure_triage_openai.py` | `extractors/figure/triage.py` | Figure triage preserved as a dedicated figure branch module. |
| `scripts/step7_figure_digitize_cv.py` | `extractors/figure/digitize.py` | CV digitization preserved with configurable inputs and outputs. |
| `scripts/step7_map_curves_to_formulations_openai_vision.py` | `extractors/figure/map_curves.py` | Vision-based curve-to-formulation alignment preserved behind a module interface. |
| `scripts/step7_build_figure_records.py` | `extractors/figure/build_records.py` | Figure endpoints are now converted into unified `Record` objects. |
| `scripts/step7_merge_text_figure_v1.py` | `assembly/assemble_records.py` | Merge stage simplified into modular assembly and deduplication. |
| `scripts/step7_qc_api_5pct_from_components.py` | `policies/v1_strict_ibuprofen_5pct.py` | Strict 5% ibuprofen scope is centralized as policy instead of being scattered across scripts. |
| `scripts/step7_refine_api_conc_openai.py` | `verification/verify_records.py` and `policies/v1_strict_ibuprofen_5pct.py` | Remaining concentration refinement is a follow-up TODO after policy centralization. |

## New Shared Layers

- `schemas/models.py`
  Defines `Record`, `EvidenceItem`, `ContentAccess`, `RouteDecision`, and manifest-related shared models.
- `policies/v1_strict_ibuprofen_5pct.py`
  Centralizes strict scope rules for API, Franz diffusion cell, IVPT/IVRT, amount endpoint, endpoint time, and 5% w/w.
- `utils/io.py`
  Adds JSONL-first output helpers and optional CSV export.
- `utils/manifest.py`
  Adds minimal run manifest support.

## Known Round 1 TODOs

- Reintroduce deeper page-grounded verification from the legacy verifier behind the new verification interface.
- Improve table/text record alignment so text-route records can consume table-derived formulation labels more directly.
- Expand the content resolver to make better use of PMC XML and HTML once downstream extractors are no longer PDF-first.
- Decide whether step-level compatibility shims should be added for the old `scripts/` entrypoints after the new package pipeline stabilizes.
