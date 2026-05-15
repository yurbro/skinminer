# V4 Rescore: claude

Rescore input: `outputs\experiment_E3_claude_v2\patched_area.jsonl`. LLM stages were not rerun; only verification policy changed.
Previous layer: `v3`
Current policy: `v4`

## Status Delta

| Metric | v3 | v4 | Delta |
| --- | --- | --- | --- |
| verified | 38 | 47 | 9 |
| unresolved | 45 | 36 | -9 |
| rejected | 10 | 10 | 0 |
| table verified | 24 | 24 | 0 |
| figure verified | 0 | 0 | 0 |
| text verified | 0 | 0 | 0 |
| mixed verified | 14 | 23 | 9 |

## Verified Endpoint Kinds

| Endpoint kind | Verified count |
| --- | --- |
| amount_total | 38 |
| flux | 7 |
| jss | 2 |

## Failure Taxonomy

| Failure reason | Count |
| --- | --- |
| source_context_inconsistent | 26 |
| not_target_study_type | 10 |
| percent_only | 7 |
| missing_endpoint | 6 |
| figure_digitization_failed | 4 |
| missing_area | 3 |
| insufficient_evidence | 2 |
| missing_endpoint_time | 1 |
| ambiguous_mapping | 1 |

## New Verified Records

- New verified vs v3: `9`
- Flux/Jss/Kp/Papp-like new verified: `9`

| record_id | doi | route | label | api_raw | endpoint_kind | endpoint_unit | endpoint_value | time_value | time_unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| record_e0c6a4b1b913 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - Control | 80% saturated solution | flux | ug/cm2/h | 167.78 | 6.0 | hours |
| record_b8450d40a00a | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 200 um microneedle | 80% saturated solution | flux | ug/cm2/h | 368.69 | 6.0 | hours |
| record_251f93e67bb6 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 300 um microneedle | 80% saturated solution | flux | ug/cm2/h | 431.52 | 6.0 | hours |
| record_93126011b4da | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - Control | 80% saturated solution | flux | 10-6 cm/s | 1.92 | 6.0 | hours |
| record_a1bb31150869 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 200 um microneedle | 80% saturated solution | flux | 10-6 cm/s | 4.21 | 6.0 | hours |
| record_bb1cbf1d5f0b | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 300 um microneedle | 80% saturated solution | flux | 10-6 cm/s | 5.27 | 6.0 | hours |
| record_625975cc9b8d | 10.1248/cpb.c21-00033 | mixed | ibuprofen-suspended aqueous solution (Av=1) | ~3x solubility in water, stirred 37 degrees C 24h (suspended solution) | flux | umol/cm2/h | 2.35 | 8.0 | h |
| record_efda20e2468c | 10.1248/cpb.c21-00033 | mixed | text_1 | molar fraction of ibuprofen = 0.5 (equimolar with lidocaine); 100% IL, no free ibuprofen | jss | umol/cm2/h | 1.18 | 8.0 | h |
| record_dd3d59a50f07 | 10.1248/cpb.c21-00033 | mixed | text_2 | approximately 3x solubility in water; suspended (activity = 1.0) | jss | umol/cm2/h | 2.35 | 8.0 | h |
