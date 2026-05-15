# V4 Rescore: gpt

Rescore input: `outputs\full_run_16_post_all_fixes\patched_area.jsonl`. LLM stages were not rerun; only verification policy changed.
Previous layer: `v3`
Current policy: `v4`

## Status Delta

| Metric | v3 | v4 | Delta |
| --- | --- | --- | --- |
| verified | 47 | 51 | 4 |
| unresolved | 133 | 129 | -4 |
| rejected | 59 | 59 | 0 |
| table verified | 33 | 33 | 0 |
| figure verified | 1 | 1 | 0 |
| text verified | 5 | 6 | 1 |
| mixed verified | 8 | 11 | 3 |

## Verified Endpoint Kinds

| Endpoint kind | Verified count |
| --- | --- |
| amount_total | 33 |
| amount_per_area | 14 |
| jss | 3 |
| flux | 1 |

## Failure Taxonomy

| Failure reason | Count |
| --- | --- |
| insufficient_evidence | 122 |
| source_context_inconsistent | 65 |
| not_target_api | 37 |
| missing_area | 37 |
| not_target_api_concentration | 27 |
| not_target_device | 27 |
| percent_only | 19 |
| missing_endpoint | 12 |
| missing_endpoint_time | 10 |
| unit_normalization_failed | 8 |
| missing_api_concentration | 6 |
| not_target_study_type | 4 |
| figure_digitization_failed | 2 |

## New Verified Records

- New verified vs v3: `4`
- Flux/Jss/Kp/Papp-like new verified: `4`

| record_id | doi | route | label | api_raw | endpoint_kind | endpoint_unit | endpoint_value | time_value | time_unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| record_2c9fa747f279 | 10.1007/s11095-008-9785-y | mixed | text_1 | 10 mg/ml | jss | - | 2.99 | 0.5 | hr |
| record_8cbb8eafc69e | 10.1016/j.jpba.2019.04.040 | text | text_1 | Ibuprofen formulation with Acetone treatment | flux | mg/cm2/h | 0.1 | 1.0 | h |
| record_f1bd4b546c11 | 10.1208/s12249-015-0474-y | mixed | text_1 | N/A | jss | ug/(cm2 h) | 113.09 | 8.0 | h |
| record_e6ee5fbe2ba0 | 10.1208/s12249-015-0474-y | mixed | text_2 | N/A | jss | ug/(cm2 h) | 169.85 | 8.0 | h |
