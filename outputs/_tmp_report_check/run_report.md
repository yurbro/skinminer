# Run Report: run_c8e16e412ed1

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Assembled records: `124`
- Final records evaluated: `124`
- Actually verified: `7`
- Final unresolved: `69`
- Final rejected: `48`

## Route Distribution

## Extractor Outputs
- figure: 0
- table: 0
- text: 0

## Verification Outcomes
- rejected: 48
- unresolved: 69
- verified: 7

## Scope Buckets
- out_of_scope: 27
- recoverable_unresolved: 61
- strict_in_scope: 7
- useful_but_out_of_scope: 29

## Failure Taxonomy
- ambiguous_api_concentration: 56
- insufficient_evidence: 87
- missing_api_concentration: 10
- missing_area: 31
- missing_endpoint: 6
- missing_endpoint_time: 4
- not_target_api: 27
- not_target_api_concentration: 10
- not_target_device: 19
- not_target_study_type: 18
- percent_only: 5
- unit_normalization_failed: 10

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 26
- insufficient_evidence: 28
- missing_area: 11
- not_target_api: 13
- not_target_api_concentration: 6
- not_target_device: 10
- not_target_study_type: 12
- percent_only: 4
- unit_normalization_failed: 6
### mixed
- ambiguous_api_concentration: 4
- insufficient_evidence: 32
- missing_api_concentration: 1
- missing_area: 5
- missing_endpoint: 6
- missing_endpoint_time: 4
- not_target_api: 6
- not_target_api_concentration: 2
- not_target_device: 8
- not_target_study_type: 4
- percent_only: 1
- unit_normalization_failed: 4
### table
- ambiguous_api_concentration: 16
- insufficient_evidence: 17
- missing_api_concentration: 9
- missing_area: 10
- not_target_api: 8
- not_target_api_concentration: 2
- not_target_device: 1
- not_target_study_type: 2
### text
- ambiguous_api_concentration: 10
- insufficient_evidence: 10
- missing_area: 5

## Figure Stage Counts
- digitized_curves: 26
- digitized_endpoints_failed: 1
- digitized_endpoints_ok: 26
- mapped_curves: 26
- triage_artifacts: 14
- triage_digitize_candidates: 14
- unmapped_curves: 0

## Figure Gate Counts
- routed_candidates: 23
- after_gate: 15
- skipped:missing_explicit_figure_signal: 8

## Figure Triage Routes
- digitize: 14

## Figure Triage Signals
- endpoint_curve_present:no: 1

## Figure Digitization Statuses
- fail_missing_axis_range: 1
- ok: 26

## Figure Mapping Statuses
- vision_mapped: 26

## LLM Reliability
### detection.router
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 233
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.figure.map_curves
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 10
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.figure.triage
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 14
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.table
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 37
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.text
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 20
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### triage.llm_triage
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 749
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0

## LLM Adjudication Audit
- rows: 0
- none
- disagreement:none

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-03-28.v1
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1

## Blockage Summary
### Access Statuses
- downloaded: 229
- error: 1
- resolved: 82
- unresolved: 230
### Access Reasons
- resolve_error_connectionerror: 1
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
- skipped: 93
#### patch_area
- applied: 11
- skipped: 51
#### patch_endpoint_time
- applied: 26
- skipped: 4
#### patch_endpoint_value
- applied: 54
- skipped: 60

## Patch Success Counts
- patch_api_concentration: 2
- patch_area: 11
- patch_endpoint_time: 26
- patch_endpoint_value: 54