# V3 Rescore: claude

Rescore input: `outputs\experiment_E3_claude_v2\patched_area.jsonl`. LLM stages were not rerun; only verification policy changed.
Previous layer: `v2`
Current policy: `v3`

## Status Delta

| Metric | v2 | v3 | Delta |
| --- | --- | --- | --- |
| verified | 24 | 38 | 14 |
| unresolved | 59 | 45 | -14 |
| rejected | 10 | 10 | 0 |
| table verified | 24 | 24 | 0 |
| figure verified | 0 | 0 | 0 |
| text verified | 0 | 0 | 0 |
| mixed verified | 0 | 14 | 14 |

## Verified Endpoint Kinds

| Endpoint kind | Verified count |
| --- | --- |
| amount_total | 38 |

## Failure Taxonomy

| Failure reason | Count |
| --- | --- |
| source_context_inconsistent | 26 |
| insufficient_evidence | 11 |
| not_target_study_type | 10 |
| percent_only | 7 |
| missing_endpoint | 6 |
| figure_digitization_failed | 4 |
| missing_area | 3 |
| missing_endpoint_time | 1 |
| ambiguous_mapping | 1 |

## New Verified Records

- New verified vs v2: `14`
- Flux/Jss/Kp/Papp-like new verified: `0`

| record_id | doi | route | label | api_raw | endpoint_kind | endpoint_unit | endpoint_value | time_value | time_unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| record_201abe3c58a1 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - Control | 80% saturated solution | amount_total | mg | 23.4 | 6.0 | hours |
| record_b595315133cb | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 200 um microneedle | 80% saturated solution | amount_total | mg | 23.4 | 6.0 | hours |
| record_f8d0d6249889 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 300 um microneedle | 80% saturated solution | amount_total | mg | 23.4 | 6.0 | hours |
| record_59930f2888d3 | 10.1248/cpb.c21-00033 | mixed | #0 | LID/IBU ratio 0/1.0 (at preparation); LID/IBU as IL 0/0; Dissolved LID/IBU 0/0; Suspended LID/IBU 0/1.0 | amount_total | mg | 10.0 | 8.0 | h |
| record_68421bba5cec | 10.1248/cpb.c21-00033 | mixed | #1 | LID/IBU ratio 0.1/0.9 (at preparation); LID/IBU as IL 0.1/0.1; Dissolved LID/IBU 0/0.26; Suspended LID/IBU 0/0.54 | amount_total | mg | 10.0 | 8.0 | h |
| record_680d383d11b3 | 10.1248/cpb.c21-00033 | mixed | #2 | LID/IBU ratio 0.2/0.8 (at preparation); LID/IBU as IL 0.2/0.2; Dissolved LID/IBU 0/0.52; Suspended LID/IBU 0/0.08 | amount_total | mg | 10.0 | 8.0 | h |
| record_1a4b21f6917f | 10.1248/cpb.c21-00033 | mixed | #3 | LID/IBU ratio 0.3/0.7 (at preparation); LID/IBU as IL 0.3/0.3; Dissolved LID/IBU 0/0.4; Suspended LID/IBU 0/0 | amount_total | mg | 10.0 | 8.0 | h |
| record_c823d905d9ab | 10.1248/cpb.c21-00033 | mixed | #4 | LID/IBU ratio 0.4/0.6 (at preparation); LID/IBU as IL 0.4/0.4; Dissolved LID/IBU 0/0.2; Suspended LID/IBU 0/0 | amount_total | mg | 10.0 | 8.0 | h |
| record_7490da0d3c66 | 10.1248/cpb.c21-00033 | mixed | #5 | LID/IBU ratio 0.5/0.5 (at preparation); LID/IBU as IL 0.5/0.5; Dissolved LID/IBU 0/0; Suspended LID/IBU 0/0 | amount_total | mg | 10.0 | 8.0 | h |
| record_1781048540af | 10.1248/cpb.c21-00033 | mixed | #6 | LID/IBU ratio 0.6/0.4 (at preparation); LID/IBU as IL 0.4/0.4; Dissolved LID/IBU 0.2/0; Suspended LID/IBU 0/0 | amount_total | mg | 10.0 | 8.0 | h |
| record_b0d3bc96b995 | 10.1248/cpb.c21-00033 | mixed | #7 | LID/IBU ratio 0.7/0.3 (at preparation); LID/IBU as IL 0.3/0.3; Dissolved LID/IBU 0.4/0; Suspended LID/IBU 0/0 | amount_total | mg | 10.0 | 8.0 | h |
| record_b2c674a09bff | 10.1248/cpb.c21-00033 | mixed | #8 | LID/IBU ratio 0.8/0.2 (at preparation); LID/IBU as IL 0.2/0.2; Dissolved LID/IBU 0.38/0; Suspended LID/IBU 0.22/0 | amount_total | mg | 10.0 | 8.0 | h |
| record_42659813bb90 | 10.1248/cpb.c21-00033 | mixed | #9 | LID/IBU ratio 0.9/0.1 (at preparation); LID/IBU as IL 0.1/0.1; Dissolved LID/IBU 0.19/0; Suspended LID/IBU 0.61/0 | amount_total | mg | 10.0 | 8.0 | h |
| record_f7c477c76555 | 10.1248/cpb.c21-00033 | mixed | #10 | LID/IBU ratio 1.0/0 (at preparation); LID/IBU as IL 0/0; Dissolved LID/IBU 0/0; Suspended LID/IBU 1.0/0 | amount_total | mg | 10.0 | 8.0 | h |
