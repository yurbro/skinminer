# Run Report: run_48d438c1f45f

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `26`
- Final records evaluated: `26`
- Actually verified: `8`
- Final unresolved: `15`
- Final rejected: `3`

## Route Distribution
- figure: 8
- table: 2

## Extractor Outputs
- figure: 4
- table: 23
- text: 0

## Verification Outcomes
- rejected: 3
- unresolved: 15
- verified: 8

## Scope Buckets
- out_of_scope: 3
- recoverable_unresolved: 13
- strict_in_scope: 8
- useful_but_out_of_scope: 2

## Scope Tags
- non_target_api: 3
- recoverable_api_basis: 10
- recoverable_endpoint: 2
- recoverable_figure_digitization: 2
- recoverable_support_gap: 4
- recoverable_unresolved: 13
- useful_api_concentration_out_of_scope: 2
- useful_but_out_of_scope: 2

## Failure Taxonomy
- ambiguous_api_concentration: 13
- figure_digitization_failed: 3
- insufficient_evidence: 8
- missing_area: 2
- missing_endpoint: 3
- not_target_api: 3
- not_target_api_concentration: 2
- not_target_device: 1
- percent_only: 2

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 5
- figure_digitization_failed: 3
- insufficient_evidence: 8
- missing_area: 2
- missing_endpoint: 3
- not_target_api: 3
- not_target_api_concentration: 2
- not_target_device: 1
- percent_only: 2
### table
- ambiguous_api_concentration: 8

## Figure Stage Counts
- digitization_no_output: 3
- digitized_curves: 9
- digitized_endpoints_failed: 4
- digitized_endpoints_ok: 9
- mapped_curves: 4
- triage_artifacts: 8
- triage_digitize_candidates: 7
- triage_has_permeation_plot_true: 7
- unmapped_curves: 5

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
- endpoint_curve_present:uncertain: 1
- recommended_route:skip: 1
- ticks_readable:uncertain: 1
- why_not_digitizable:calibration_curve_not_target: 1

## Figure Digitization Statuses
- digitization_no_output: 3
- fail_missing_axis_range: 1
- ok: 9

## Figure Mapping Statuses
- underconstrained_labels: 5
- vision_mapped: 4

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 11
- priority_bucket:high: 10
- priority_bucket:medium: 1
- review_focus:api_concentration_basis: 10
- review_focus:endpoint_value: 1
- recommended_status:rejected: 4
- recommended_status:unresolved: 7
- disagreement:scope_bucket_disagreement: 4
- disagreement:status_disagreement: 4

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
- applied: 1
- skipped: 16
#### patch_area
- skipped: 4
#### patch_endpoint_value
- applied: 3
- skipped: 9

## Patch Success Counts
- patch_api_concentration: 1
- patch_endpoint_value: 3