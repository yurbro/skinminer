# Run Report: run_b025942c352d

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Assembled records: `42`
- Final records evaluated: `42`
- Actually verified: `0`
- Final unresolved: `20`
- Final rejected: `22`

## Route Distribution
- figure: 8
- mixed: 4
- table: 4
- text: 2
- unresolved: 511

## Extractor Outputs
- figure: 7
- table: 23
- text: 13

## Verification Outcomes
- rejected: 22
- unresolved: 20

## Failure Taxonomy
- insufficient_evidence: 42
- missing_api_concentration: 16
- missing_area: 15
- missing_endpoint: 15
- missing_endpoint_time: 12
- not_target_api: 2
- not_target_device: 21
- not_target_study_type: 2
- percent_only: 2
- unit_normalization_failed: 1

## Failure Taxonomy By Route
### figure
- insufficient_evidence: 21
- missing_api_concentration: 3
- missing_area: 11
- missing_endpoint: 10
- missing_endpoint_time: 7
- not_target_api: 1
- not_target_device: 12
- not_target_study_type: 1
- unit_normalization_failed: 1
### mixed
- insufficient_evidence: 12
- missing_api_concentration: 10
- missing_area: 1
- missing_endpoint: 4
- missing_endpoint_time: 5
- not_target_device: 4
- not_target_study_type: 1
- percent_only: 1
### table
- insufficient_evidence: 5
- missing_api_concentration: 1
- missing_area: 3
- not_target_api: 1
- not_target_device: 5
### text
- insufficient_evidence: 4
- missing_api_concentration: 2
- missing_endpoint: 1
- percent_only: 1

## Figure Stage Counts
- digitized_curves: 7
- digitized_endpoints_failed: 6
- digitized_endpoints_ok: 7
- mapped_curves: 7
- triage_artifacts: 9
- triage_digitize_candidates: 9
- unmapped_curves: 0

## Figure Triage Routes
- digitize: 9

## Figure Triage Signals

## Figure Digitization Statuses
- fail_few_edges: 4
- fail_missing_plot_context: 2
- ok: 7

## Figure Mapping Statuses
- vision_mapped: 7

## Patch Success Counts