# Run Report: run_b3a44609b651

- Model: `claude-sonnet-4-6`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'claude-sonnet-4-6', 'routing': 'claude-sonnet-4-6', 'text_extract': 'claude-sonnet-4-6', 'table_extract': 'claude-sonnet-4-6', 'figure_triage': 'claude-sonnet-4-6', 'figure_vlm': 'claude-sonnet-4-6', 'figure_map': 'claude-sonnet-4-6', 'llm_adjudicate': 'claude-sonnet-4-6'}`
- Assembled records: `24`
- Final records evaluated: `24`
- Actually verified: `0`
- Final unresolved: `24`
- Final rejected: `0`

## Route Distribution
- table: 1

## Extractor Outputs
- figure: 0
- table: 24
- text: 0

## Verification Outcomes
- unresolved: 24

## Scope Buckets
- recoverable_unresolved: 24

## Scope Tags
- recoverable_api_basis: 24
- recoverable_unresolved: 24

## Failure Taxonomy
- ambiguous_api_concentration: 24

## Failure Taxonomy By Route
### table
- ambiguous_api_concentration: 24

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
- extractors.figure.vlm_digitize: 2026-04-11.v1
- extractors.table.structured_tables: 2026-04-11.v1
- extractors.text.structured_fields: 2026-04-11.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1
- verification.llm_adjudication: 2026-04-03.v1

## Blockage Summary
### Access Statuses
- downloaded: 1
### Access Reasons
- none
### Unresolved Route Reasons
- none
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
#### patch_api_concentration
- skipped: 24

## Patch Success Counts