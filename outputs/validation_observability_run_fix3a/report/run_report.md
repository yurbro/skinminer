# Run Report: run_2176ef44caaa

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `32`
- Final records evaluated: `32`
- Actually verified: `12`
- Final unresolved: `17`
- Final rejected: `3`

## Route Distribution
- figure: 8
- table: 2

## Extractor Outputs
- figure: 9
- table: 24
- text: 0

## Verification Outcomes
- rejected: 3
- unresolved: 17
- verified: 12

## Scope Buckets
- out_of_scope: 2
- recoverable_unresolved: 17
- strict_in_scope: 12
- useful_but_out_of_scope: 1

## Scope Tags
- non_target_api: 2
- recoverable_api_basis: 13
- recoverable_endpoint: 2
- recoverable_figure_digitization: 2
- recoverable_support_gap: 4
- recoverable_unit_normalization: 1
- recoverable_unresolved: 17
- useful_api_concentration_out_of_scope: 1
- useful_but_out_of_scope: 1
- useful_device_out_of_scope: 1
- useful_study_type_out_of_scope: 1

## Failure Taxonomy
- ambiguous_api_concentration: 15
- figure_digitization_failed: 3
- insufficient_evidence: 5
- missing_area: 1
- missing_endpoint: 3
- not_target_api: 2
- not_target_api_concentration: 1
- not_target_device: 1
- not_target_study_type: 1
- percent_only: 3
- unit_normalization_failed: 1

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 7
- figure_digitization_failed: 3
- insufficient_evidence: 5
- missing_area: 1
- missing_endpoint: 3
- not_target_api: 2
- not_target_api_concentration: 1
- not_target_device: 1
- not_target_study_type: 1
- percent_only: 3
- unit_normalization_failed: 1
### table
- ambiguous_api_concentration: 8

## Figure Stage Counts
- digitization_no_output: 2
- digitized_curves: 9
- digitized_endpoints_failed: 3
- digitized_endpoints_ok: 9
- mapped_curves: 9
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
- endpoint_curve_present:no: 1
- recommended_route:skip: 1
- why_not_digitizable:calibration_curve_not_target: 1

## Figure Digitization Statuses
- digitization_no_output: 2
- fail_missing_axis_range: 1
- ok: 9

## Figure Mapping Statuses
- vision_mapped: 9

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 14
- priority_bucket:high: 14
- review_focus:api_concentration_basis: 13
- review_focus:endpoint_value: 1
- recommended_status:rejected: 3
- recommended_status:unresolved: 11
- disagreement:scope_bucket_disagreement: 3
- disagreement:status_disagreement: 3

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-04-06.v1
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
- applied: 6
- skipped: 19
#### patch_area
- skipped: 4
#### patch_endpoint_time
- applied: 3
#### patch_endpoint_value
- applied: 12
- skipped: 18

## Patch Success Counts
- patch_api_concentration: 6
- patch_endpoint_time: 3
- patch_endpoint_value: 12