# Run Report: run_5daf7900815c

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `0`
- Final records evaluated: `0`
- Actually verified: `0`
- Final unresolved: `0`
- Final rejected: `0`

## Route Distribution
- unresolved: 1

## Extractor Outputs
- figure: 0
- table: 0
- text: 0

## Verification Outcomes

## Scope Buckets
- none

## Scope Tags
- none

## Failure Taxonomy

## Failure Taxonomy By Route

## Figure Stage Counts
- digitization_no_output: 0
- digitized_curves: 0
- digitized_endpoints_failed: 0
- digitized_endpoints_ok: 0
- mapped_curves: 0
- triage_artifacts: 0
- triage_digitize_candidates: 0
- triage_has_permeation_plot_true: 0
- unmapped_curves: 0
- vlm_readings_readable: 0
- vlm_readings_total: 0
- vlm_used_as_final: 0

## Figure Gate Counts
- routed_candidates: 0
- after_gate: 0

## Figure Triage Routes

## Figure Plot Presence

## Figure Triage Signals

## Figure Digitization Statuses

## Figure Mapping Statuses

## Figure VLM Grounding Statuses
- none

## Figure VLM Reconciliation Statuses
- none

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 0
- priority_bucket:none
- review_focus:none
- none
- disagreement:none

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-04-06.v1
- extractors.figure.vlm_digitize: 2026-04-08.v2
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1
- verification.llm_adjudication: 2026-04-03.v1

## Blockage Summary
### Access Statuses
- unresolved: 1
### Access Reasons
- none
### Unresolved Route Reasons
- missing_structured_and_pdf_router_source: 1
### Extractor Source / Error Blockages
#### table
- status:none
- error_type:none
- source_backend:none
#### text
- status:none
- error_type:none
- source_backend:none
### Patch Statuses

## Patch Success Counts