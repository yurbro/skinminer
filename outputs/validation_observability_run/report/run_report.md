# Run Report: run_ef93060f18dc

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `33`
- Final records evaluated: `33`
- Actually verified: `10`
- Final unresolved: `21`
- Final rejected: `2`

## Route Distribution
- figure: 7
- mixed: 1
- table: 1
- text: 1

## Extractor Outputs
- figure: 11
- table: 25
- text: 0

## Verification Outcomes
- rejected: 2
- unresolved: 21
- verified: 10

## Scope Buckets
- out_of_scope: 1
- recoverable_unresolved: 17
- strict_in_scope: 10
- useful_but_out_of_scope: 5

## Scope Tags
- non_target_api: 1
- recoverable_api_basis: 14
- recoverable_endpoint: 1
- recoverable_figure_digitization: 1
- recoverable_support_gap: 4
- recoverable_unresolved: 17
- useful_api_concentration_out_of_scope: 5
- useful_but_out_of_scope: 5
- useful_device_out_of_scope: 1

## Failure Taxonomy
- ambiguous_api_concentration: 15
- figure_digitization_failed: 1
- insufficient_evidence: 4
- missing_area: 1
- missing_endpoint: 1
- not_target_api: 1
- not_target_api_concentration: 5
- not_target_device: 1
- percent_only: 2

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 15
- figure_digitization_failed: 1
- insufficient_evidence: 4
- missing_endpoint: 1
- not_target_api: 1
- not_target_api_concentration: 4
- percent_only: 2
### mixed
- missing_area: 1
- not_target_api_concentration: 1
- not_target_device: 1

## Figure Stage Counts
- digitization_no_output: 2
- digitized_curves: 12
- digitized_endpoints_failed: 2
- digitized_endpoints_ok: 12
- mapped_curves: 11
- triage_artifacts: 8
- triage_digitize_candidates: 7
- triage_has_permeation_plot_true: 7
- unmapped_curves: 1

## Figure Gate Counts
- routed_candidates: 8
- after_gate: 8

## Figure Triage Routes
- digitize: 7
- skip: 1

## Figure Plot Presence
- false: 1
- true: 7

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 1
- recommended_route:skip: 1
- ticks_readable:uncertain: 1
- why_not_digitizable:no_clear_endpoint_curves_present: 1

## Figure Digitization Statuses
- digitization_no_output: 2
- ok: 12

## Figure Mapping Statuses
- unmapped: 1
- vision_mapped: 11

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 14
- priority_bucket:high: 14
- review_focus:api_concentration_basis: 14
- recommended_status:unresolved: 14
- disagreement:none

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-03-28.v1
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1
- verification.llm_adjudication: 2026-04-03.v1

## Blockage Summary
### Access Statuses
- downloaded: 10
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
- applied: 2
- skipped: 21
#### patch_area
- skipped: 3
#### patch_endpoint_time
- applied: 12
#### patch_endpoint_value
- applied: 20
- skipped: 22

## Patch Success Counts
- patch_api_concentration: 2
- patch_endpoint_time: 12
- patch_endpoint_value: 20