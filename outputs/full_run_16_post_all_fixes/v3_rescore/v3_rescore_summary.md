# V3 Rescore: gpt

Rescore input: `outputs\full_run_16_post_all_fixes\patched_area.jsonl`. LLM stages were not rerun; only verification policy changed.
Previous layer: `v2`
Current policy: `v3`

## Status Delta

| Metric | v2 | v3 | Delta |
| --- | --- | --- | --- |
| verified | 25 | 47 | 22 |
| unresolved | 155 | 133 | -22 |
| rejected | 59 | 59 | 0 |
| table verified | 24 | 33 | 9 |
| figure verified | 1 | 1 | 0 |
| text verified | 0 | 5 | 5 |
| mixed verified | 0 | 8 | 8 |

## Verified Endpoint Kinds

| Endpoint kind | Verified count |
| --- | --- |
| amount_total | 33 |
| amount_per_area | 14 |

## Failure Taxonomy

| Failure reason | Count |
| --- | --- |
| insufficient_evidence | 126 |
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

- New verified vs v2: `22`
- Flux/Jss/Kp/Papp-like new verified: `5`

| record_id | doi | route | label | api_raw | endpoint_kind | endpoint_unit | endpoint_value | time_value | time_unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| record_cf8f689281a3 | 10.1007/s11095-008-9785-y | mixed | Ibuprofen 750 ug/cm2 | Ibuprofen saturated solution in 75:25 propylene glycol/water | amount_per_area | ug/cm2 | 0.77 | 0.5 | hours |
| record_376e82e8f4c3 | 10.1007/s11095-008-9785-y | mixed | Ibuprofen 750 ug/cm2 | Ibuprofen saturated solution in 75:25 propylene glycol/water | amount_per_area | ug/cm2 | 0.75 | 1.0 | hours |
| record_f4ad6fc69336 | 10.1007/s11095-008-9785-y | mixed | Ibuprofen 750 ug/cm2 | Ibuprofen saturated solution in 75:25 propylene glycol/water | amount_per_area | ug/cm2 | 0.74 | 2.0 | hours |
| record_1b7997ecf760 | 10.1007/s11095-008-9785-y | mixed | Ibuprofen 750 ug/cm2 | Ibuprofen saturated solution in 75:25 propylene glycol/water | amount_per_area | ug/cm2 | 0.73 | 3.0 | hours |
| record_d39ce62be933 | 10.1007/s11095-008-9785-y | mixed | Ibuprofen 750 ug/cm2 | Ibuprofen saturated solution in 75:25 propylene glycol/water | amount_per_area | ug/cm2 | 0.72 | 4.0 | hours |
| record_797d3caa1991 | 10.1039/d0ra00100g | table | rac-IBU |  | amount_total | mg IBU cm2 | 302.84 | 24.0 | h |
| record_256fed3f4d2f | 10.1186/2050-6511-13-5 | mixed | Ibuprofen Control |  | amount_per_area | ug/cm2/h | 167.78 | 6.0 | hours |
| record_fb26829467a8 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen 200 um |  | amount_per_area | ug/cm2/h | 368.69 | 6.0 | hours |
| record_dea378194778 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen 300 um |  | amount_per_area | ug/cm2/h | 431.52 | 6.0 | hours |
| record_f4db8f371df4 | 10.1208/s12249-019-1481-1 | table | Ibuprofen 1,3-BG 1:1 | - | amount_per_area | ug/cm2 | 50.0 | 1.0 | h |
| record_73e793f7cfd0 | 10.1208/s12249-019-1481-1 | table | Ibuprofen DPG 1:1 | - | amount_per_area | ug/cm2 | 70.0 | 2.0 | h |
| record_489d1193529e | 10.1208/s12249-019-1481-1 | table | Ibuprofen PEG60 1:1 | - | amount_per_area | ug/cm2 | 90.0 | 3.0 | h |
| record_dc75f062c81e | 10.1208/s12249-019-1481-1 | table | Ibuprofen Control | - | amount_per_area | ug/cm2 | 20.0 | 1.0 | h |
| record_d8d2b57596ab | 10.1208/s12249-019-1481-1 | table | Ibuprofen Glycerin 1:1 | - | amount_per_area | ug/cm2 | 100.0 | 2.0 | h |
| record_32062e7155cc | 10.1208/s12249-019-1481-1 | table | Ibuprofen Mixed Vehicle | - | amount_per_area | ug/cm2 | 110.0 | 3.0 | h |
| record_1bd324e90169 | 10.1248/bpb.b19-00221 | table | Ibuprofen | 3.83 mg/mL | amount_total | mg | 3.83 | 0.0 | min |
| record_05c22499eb1a | 10.1248/bpb.b19-00221 | table | Ibuprofen | 3.83 mg/mL | amount_total | mg | 3.83 | 120.0 | min |
| record_0c86a8a8bb55 | 10.1523/jneurosci.5741-07.2008 | text | text_1 | 40 mg/kg | amount_total | mg | 40.0 | 30.0 | min |
| record_9ef995c91d9b | 10.1523/jneurosci.5741-07.2008 | text | text_2 | 40 mg/kg | amount_total | mg | 40.0 | 30.0 | min |
| record_3cafd2b883f5 | 10.1523/jneurosci.5741-07.2008 | text | text_3 | 40 mg/kg | amount_total | mg | 40.0 | 30.0 | min |
| record_4306a8808b9e | 10.1523/jneurosci.5741-07.2008 | text | text_4 | 40 mg/kg | amount_total | mg | 40.0 | 30.0 | min |
| record_971a466d8370 | 10.1523/jneurosci.5741-07.2008 | text | text_5 | 40 mg/kg | amount_total | mg | 40.0 | 30.0 | min |
