# Run Report: run_8b9c5fd4986d

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `15`
- Final records evaluated: `15`
- Actually verified: `2`
- Final unresolved: `11`
- Final rejected: `2`

## Route Distribution
- figure: 8
- table: 2

## Extractor Outputs
- figure: 0
- table: 15
- text: 0

## Verification Outcomes
- rejected: 2
- unresolved: 11
- verified: 2

## Scope Buckets
- out_of_scope: 1
- recoverable_unresolved: 9
- strict_in_scope: 2
- useful_but_out_of_scope: 3

## Scope Tags
- non_target_api: 1
- recoverable_api_basis: 6
- recoverable_area: 1
- recoverable_endpoint: 2
- recoverable_figure_digitization: 2
- recoverable_support_gap: 4
- recoverable_unresolved: 9
- useful_api_concentration_out_of_scope: 3
- useful_but_out_of_scope: 3
- useful_device_out_of_scope: 1

## Failure Taxonomy
- ambiguous_api_concentration: 7
- figure_digitization_failed: 2
- insufficient_evidence: 4
- missing_area: 3
- missing_endpoint: 2
- not_target_api: 1
- not_target_api_concentration: 3
- not_target_device: 1
- percent_only: 2

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 2
- figure_digitization_failed: 2
- insufficient_evidence: 4
- missing_area: 1
- missing_endpoint: 2
- not_target_api_concentration: 3
- not_target_device: 1
- percent_only: 2
### table
- ambiguous_api_concentration: 5
- missing_area: 2
- not_target_api: 1

## Figure Stage Counts
- digitization_no_output: 2
- digitized_curves: 10
- digitized_endpoints_failed: 3
- digitized_endpoints_ok: 10
- mapped_curves: 1
- triage_artifacts: 8
- triage_digitize_candidates: 7
- triage_has_permeation_plot_true: 7
- unmapped_curves: 9
- vlm_readings_readable: 10
- vlm_readings_total: 11
- vlm_used_as_final: 0

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
- ticks_readable:uncertain: 2
- why_not_digitizable:calibration_curve_not_target: 1

## Figure Digitization Statuses
- digitization_no_output: 2
- fail_missing_axis_range: 1
- ok: 10

## Figure Mapping Statuses
- underconstrained_labels: 9
- vision_mapped: 1

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 7
- priority_bucket:high: 6
- priority_bucket:medium: 1
- review_focus:api_concentration_basis: 6
- review_focus:endpoint_value: 1
- recommended_status:rejected: 1
- recommended_status:unresolved: 6
- disagreement:scope_bucket_disagreement: 1
- disagreement:status_disagreement: 1

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-04-06.v1
- extractors.figure.vlm_digitize: 2026-04-08.v1
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
- skipped: 10
#### patch_area
- skipped: 5
#### patch_endpoint_time
- applied: 1
#### patch_endpoint_value
- applied: 4
- skipped: 8

## Patch Success Counts
- patch_api_concentration: 2
- patch_endpoint_time: 1
- patch_endpoint_value: 4