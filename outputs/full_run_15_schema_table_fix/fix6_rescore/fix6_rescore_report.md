# Fix 6 targeted rescore report

- Input: `outputs\full_run_15_schema_table_fix\patched_area.jsonl`
- Baseline: `outputs\full_run_15_schema_table_fix\verified_records.jsonl`
- Output: `outputs\full_run_15_schema_table_fix\fix6_rescore\verified_records_fix6.jsonl`
- Policy: `v1_strict_ibuprofen_5pct`
- Scope: targeted re-verification only; no full pipeline rerun.

## Overall status

| status | before | after | delta |
|---|---:|---:|---:|
| verified | 10 | 1 | -9 |
| unresolved | 161 | 170 | +9 |
| rejected | 62 | 62 | +0 |

## Route status deltas

| route | status | before | after | delta |
|---|---|---:|---:|---:|
| figure | verified | 9 | 0 | -9 |
| figure | unresolved | 49 | 58 | +9 |
| figure | rejected | 13 | 13 | +0 |
| mixed | verified | 1 | 1 | +0 |
| mixed | unresolved | 49 | 49 | +0 |
| mixed | rejected | 19 | 19 | +0 |
| table | verified | 0 | 0 | +0 |
| table | unresolved | 60 | 60 | +0 |
| table | rejected | 29 | 29 | +0 |
| text | verified | 0 | 0 | +0 |
| text | unresolved | 3 | 3 | +0 |
| text | rejected | 1 | 1 | +0 |

## Original figure-route verified fate

- Original figure-route verified records: 9
- After Fix 6 status counts: {'unresolved': 9}
- Guard reason counts: {'figure_route_table_endpoint': 5, 'endpoint_value_from_shared_hint': 4, 'endpoint_value_time_context_mismatch': 4, 'weak_figure_mapping_grounding': 4, 'figure_condition_not_source_grounded': 4}

| record_id | extractor | formulation | endpoint | before | after | guard_reasons |
|---|---|---|---:|---|---|---|
| record_2b009f46d9d5 | table | IBULEVE™ Speed Relief | 23.282442092895508 µg/cm² @ 10.0 min | verified | unresolved | figure_route_table_endpoint|endpoint_value_from_shared_hint|endpoint_value_time_context_mismatch |
| record_9b88081c5362 | figure | Ibuprofen Solution (PEG 300) | 16.183204650878906 µg/cm² @ 48.0 h | verified | unresolved | weak_figure_mapping_grounding|figure_condition_not_source_grounded |
| record_9e8b3aa49269 | table | Ibuprofen Solution (Isopropyl Alcohol) | 13.24427604675293 µg/cm² @ 10.0 min | verified | unresolved | figure_route_table_endpoint|endpoint_value_from_shared_hint|endpoint_value_time_context_mismatch |
| record_a93a374c2f20 | figure | Ibuprofen Solution (Isopropyl Alcohol) | 13.24427604675293 µg/cm² @ 48.0 h | verified | unresolved | weak_figure_mapping_grounding|figure_condition_not_source_grounded |
| record_b073c5f64b07 | figure | IBULEVE™ Speed Relief | 23.282442092895508 µg/cm² @ 48.0 h | verified | unresolved | weak_figure_mapping_grounding|figure_condition_not_source_grounded |
| record_b6963719efff | table | Ibuprofen Solution (PEG 300) | 16.183204650878906 µg/cm² @ 10.0 min | verified | unresolved | figure_route_table_endpoint|endpoint_value_from_shared_hint|endpoint_value_time_context_mismatch |
| record_e5a5cd848fa6 | table | IBUGEL™ | 280.0 ug/cm2 @ 10.0 min | verified | unresolved | figure_route_table_endpoint|endpoint_value_from_shared_hint|endpoint_value_time_context_mismatch |
| record_e606e9d0847c | table | IBUGEL™ | 280.0 µg/cm2 @ 6.0 h | verified | unresolved | figure_route_table_endpoint |
| record_fb1af90cc9e4 | figure | IBUGEL™ | 21.450382232666016 µg/cm² @ 48.0 h | verified | unresolved | weak_figure_mapping_grounding|figure_condition_not_source_grounded |

## Figure failure taxonomy

| failure_reason | before | after | delta |
|---|---:|---:|---:|
| ambiguous_api_concentration | 25 | 25 | +0 |
| figure_digitization_failed | 7 | 7 | +0 |
| insufficient_evidence | 24 | 24 | +0 |
| missing_api_concentration | 8 | 8 | +0 |
| missing_area | 19 | 19 | +0 |
| missing_endpoint | 12 | 12 | +0 |
| not_target_api | 9 | 9 | +0 |
| not_target_api_concentration | 17 | 17 | +0 |
| not_target_device | 2 | 2 | +0 |
| not_target_study_type | 7 | 7 | +0 |
| source_context_inconsistent | 0 | 59 | +59 |
| unit_normalization_failed | 6 | 6 | +0 |

## Outputs

- `outputs\full_run_15_schema_table_fix\fix6_rescore\verified_records_fix6.jsonl`
- `outputs\full_run_15_schema_table_fix\fix6_rescore\verified_records_fix6.csv`
- `outputs\full_run_15_schema_table_fix\fix6_rescore\status_comparison.csv`
- `outputs\full_run_15_schema_table_fix\fix6_rescore\figure_verified_fate.csv`
- `outputs\full_run_15_schema_table_fix\fix6_rescore\fix6_rescore_summary.json`
