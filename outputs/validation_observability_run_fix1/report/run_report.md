# Run Report: run_f48ca0ccefbf

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `28`
- Final records evaluated: `28`
- Actually verified: `11`
- Final unresolved: `14`
- Final rejected: `3`

## Route Distribution
- figure: 8
- table: 2

## Extractor Outputs
- figure: 11
- table: 19
- text: 0

## Verification Outcomes
- rejected: 3
- unresolved: 14
- verified: 11

## Scope Buckets
- recoverable_unresolved: 10
- strict_in_scope: 11
- useful_but_out_of_scope: 7

## Scope Tags
- recoverable_api_basis: 6
- recoverable_support_gap: 5
- recoverable_unit_normalization: 1
- recoverable_unresolved: 10
- useful_api_concentration_out_of_scope: 6
- useful_but_out_of_scope: 7
- useful_device_out_of_scope: 3
- useful_endpoint_out_of_scope: 1

## Failure Taxonomy
- ambiguous_api_concentration: 7
- insufficient_evidence: 5
- missing_area: 2
- not_target_api_concentration: 6
- not_target_device: 3
- percent_only: 2
- unit_normalization_failed: 1

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 2
- insufficient_evidence: 5
- missing_area: 2
- not_target_api_concentration: 6
- not_target_device: 3
- percent_only: 2
- unit_normalization_failed: 1
### table
- ambiguous_api_concentration: 5

## Figure Stage Counts
- digitization_no_output: 3
- digitized_curves: 11
- digitized_endpoints_failed: 3
- digitized_endpoints_ok: 11
- mapped_curves: 11
- triage_artifacts: 8
- triage_digitize_candidates: 7
- triage_has_permeation_plot_true: 7
- unmapped_curves: 0

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
- endpoint_curve_present:no: 2
- recommended_route:skip: 1
- ticks_readable:no: 1
- ticks_readable:uncertain: 2
- why_not_digitizable:figure_does_not_contain_endpoint_curves_suitable_for_digitization: 1

## Figure Digitization Statuses
- digitization_no_output: 3
- ok: 11

## Figure Mapping Statuses
- vision_mapped: 11

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 6
- priority_bucket:high: 6
- review_focus:api_concentration_basis: 6
- recommended_status:rejected: 2
- recommended_status:unresolved: 4
- disagreement:scope_bucket_disagreement: 2
- disagreement:status_disagreement: 2

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
- skipped: 17
#### patch_area
- skipped: 4
#### patch_endpoint_time
- applied: 1
#### patch_endpoint_value
- applied: 9
- skipped: 9

## Patch Success Counts
- patch_endpoint_time: 1
- patch_endpoint_value: 9