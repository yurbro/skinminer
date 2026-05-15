# Run Report: run_a1e9ae25e17f

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `28`
- Final records evaluated: `28`
- Actually verified: `10`
- Final unresolved: `16`
- Final rejected: `2`

## Route Distribution
- figure: 8
- mixed: 1
- table: 1

## Extractor Outputs
- figure: 13
- table: 17
- text: 0

## Verification Outcomes
- rejected: 2
- unresolved: 16
- verified: 10

## Scope Buckets
- recoverable_unresolved: 16
- strict_in_scope: 10
- useful_but_out_of_scope: 2

## Scope Tags
- recoverable_api_basis: 7
- recoverable_area: 1
- recoverable_endpoint: 1
- recoverable_figure_digitization: 1
- recoverable_support_gap: 11
- recoverable_unit_normalization: 4
- recoverable_unresolved: 16
- useful_api_concentration_out_of_scope: 1
- useful_but_out_of_scope: 2
- useful_device_out_of_scope: 1
- useful_study_type_out_of_scope: 1

## Failure Taxonomy
- ambiguous_api_concentration: 8
- figure_digitization_failed: 2
- insufficient_evidence: 12
- missing_area: 2
- missing_endpoint: 2
- not_target_api_concentration: 1
- not_target_device: 1
- not_target_study_type: 1
- percent_only: 2
- unit_normalization_failed: 4

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 6
- figure_digitization_failed: 2
- insufficient_evidence: 10
- missing_area: 2
- missing_endpoint: 2
- not_target_api_concentration: 1
- not_target_device: 1
- not_target_study_type: 1
- percent_only: 2
- unit_normalization_failed: 3
### mixed
- insufficient_evidence: 2
- unit_normalization_failed: 1
### table
- ambiguous_api_concentration: 2

## Figure Stage Counts
- digitization_no_output: 3
- digitized_curves: 15
- digitized_endpoints_failed: 3
- digitized_endpoints_ok: 15
- mapped_curves: 15
- triage_artifacts: 9
- triage_digitize_candidates: 7
- triage_has_permeation_plot_true: 7
- unmapped_curves: 0

## Figure Gate Counts
- routed_candidates: 9
- after_gate: 9

## Figure Triage Routes
- digitize: 7
- skip: 2

## Figure Plot Presence
- false: 2
- true: 7

## Figure Triage Signals
- digitizable:no: 2
- endpoint_curve_present:no: 1
- recommended_route:skip: 2
- ticks_readable:uncertain: 2
- why_not_digitizable:calibration_curve_not_target: 1
- why_not_digitizable:the_figures_do_not_show_clear_endpoint_curves_for_ibuprofen_they_focus_on_variou: 1

## Figure Digitization Statuses
- digitization_no_output: 3
- ok: 15

## Figure Mapping Statuses
- vision_mapped: 15

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 11
- priority_bucket:high: 10
- priority_bucket:medium: 1
- review_focus:api_concentration_basis: 7
- review_focus:endpoint_value: 1
- review_focus:unit_normalization: 3
- recommended_status:rejected: 1
- recommended_status:unresolved: 10
- disagreement:scope_bucket_disagreement: 1
- disagreement:status_disagreement: 1

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
- applied: 6
- skipped: 3
#### patch_endpoint_value
- applied: 11
- skipped: 15

## Patch Success Counts
- patch_area: 6
- patch_endpoint_value: 11