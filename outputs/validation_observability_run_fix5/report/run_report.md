# Run Report: run_ee8d926d42cd

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `23`
- Final records evaluated: `23`
- Actually verified: `6`
- Final unresolved: `14`
- Final rejected: `3`

## Route Distribution
- figure: 7
- table: 2
- text: 1

## Extractor Outputs
- figure: 2
- table: 17
- text: 5

## Verification Outcomes
- rejected: 3
- unresolved: 14
- verified: 6

## Scope Buckets
- out_of_scope: 2
- recoverable_unresolved: 13
- strict_in_scope: 6
- useful_but_out_of_scope: 2

## Scope Tags
- non_target_api: 2
- recoverable_api_basis: 7
- recoverable_support_gap: 13
- recoverable_unresolved: 13
- useful_api_concentration_out_of_scope: 1
- useful_but_out_of_scope: 2
- useful_study_type_out_of_scope: 1

## Failure Taxonomy
- ambiguous_api_concentration: 8
- figure_digitization_failed: 1
- insufficient_evidence: 14
- missing_api_concentration: 1
- missing_area: 1
- missing_endpoint: 1
- not_target_api: 2
- not_target_api_concentration: 2
- not_target_device: 1
- not_target_study_type: 1
- percent_only: 2

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 2
- figure_digitization_failed: 1
- insufficient_evidence: 3
- missing_api_concentration: 1
- missing_area: 1
- missing_endpoint: 1
- not_target_api: 2
- not_target_api_concentration: 2
- not_target_device: 1
- not_target_study_type: 1
- percent_only: 2
### table
- ambiguous_api_concentration: 6
- insufficient_evidence: 6
### text
- insufficient_evidence: 5

## Figure Stage Counts
- digitization_no_output: 2
- digitized_curves: 9
- digitized_endpoints_failed: 3
- digitized_endpoints_ok: 9
- mapped_curves: 4
- triage_artifacts: 7
- triage_digitize_candidates: 6
- triage_has_permeation_plot_true: 6
- unmapped_curves: 5
- vlm_readings_readable: 12
- vlm_readings_total: 13
- vlm_used_as_final: 2

## Figure Gate Counts
- routed_candidates: 7
- after_gate: 7

## Figure Triage Routes
- digitize: 6
- skip: 1

## Figure Plot Presence
- false: 1
- true: 6

## Figure Triage Signals
- digitizable:uncertain: 1
- endpoint_curve_present:no: 1
- endpoint_curve_present:uncertain: 1
- recommended_route:skip: 1
- ticks_readable:uncertain: 1
- why_not_digitizable:the_figure_displays_images_with_unclear_data_representation_for_endpoint_curves: 1

## Figure Digitization Statuses
- digitization_no_output: 2
- fail_missing_axis_range: 1
- ok: 9

## Figure Mapping Statuses
- underconstrained_labels: 5
- vision_mapped: 4

## Figure VLM Grounding Statuses
- figure_label_space: 3
- figure_label_space_only: 1
- none: 1
- ungrounded: 8

## Figure VLM Reconciliation Statuses
- cv_only: 8
- cv_vlm_disagreement: 2
- unreadable: 1
- vlm_only: 2

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
- extractors.figure.triage: 2026-04-06.v1
- extractors.figure.vlm_digitize: 2026-04-08.v2
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
- skipped: 12
#### patch_area
- skipped: 3
#### patch_endpoint_value
- applied: 2
- skipped: 4

## Patch Success Counts
- patch_endpoint_value: 2