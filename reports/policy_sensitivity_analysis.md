# Policy Sensitivity Analysis

Date: 2026-04-17

## Method

- No new LLM extraction was run for this analysis.
- All policy layers were rescored from each baseline run's `patched_area.jsonl`.
- GPT baseline rescore input: `outputs/full_run_16_post_all_fixes/patched_area.jsonl`.
- Claude baseline rescore input: `outputs/experiment_E3_claude_v2/patched_area.jsonl`.
- v4 inherits v3 concentration scope and additionally accepts flux/Jss plus explicitly grounded Kp/Papp/permeability coefficient endpoints while preserving the ibuprofen, Franz/IVPT/IVRT, and endpoint-time gates.

## GPT Baseline (full_run_16)

| Policy | Scope | verified | unresolved | rejected | table verified | figure verified | text verified | mixed verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1 strict | 5% w/w, amount only | 1 | 179 | 59 | 0 | 1 | 0 | 0 |
| v2 accept_wv | + w/v | 25 | 155 | 59 | 24 | 1 | 0 | 0 |
| v3 any_conc | any ibuprofen concentration | 47 | 133 | 59 | 33 | 1 | 5 | 8 |
| v4 accept_flux | + flux/Jss/Kp/Papp | 51 | 129 | 59 | 33 | 1 | 6 | 11 |

## Claude Baseline (E3_claude_v2)

| Policy | Scope | verified | unresolved | rejected | table verified | figure verified | text verified | mixed verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1 strict | 5% w/w, amount only | 0 | 83 | 10 | 0 | 0 | 0 | 0 |
| v2 accept_wv | + w/v | 24 | 59 | 10 | 24 | 0 | 0 | 0 |
| v3 any_conc | any ibuprofen concentration | 38 | 45 | 10 | 24 | 0 | 0 | 14 |
| v4 accept_flux | + flux/Jss/Kp/Papp | 47 | 36 | 10 | 24 | 0 | 0 | 23 |

## Cross-Policy Progression

### GPT Baseline (full_run_16)

| Step | additional verified | routes | top papers |
| --- | --- | --- | --- |
| v1 strict -> v2 accept_wv | 24 | table:24 | 10.1208/s12249-013-9995-4:24 |
| v2 accept_wv -> v3 any_conc | 22 | mixed:8, table:9, text:5 | 10.1208/s12249-019-1481-1:6, 10.1523/jneurosci.5741-07.2008:5, 10.1007/s11095-008-9785-y:5, 10.1186/2050-6511-13-5:3, 10.1248/bpb.b19-00221:2, 10.1039/d0ra00100g:1 |
| v3 any_conc -> v4 accept_flux | 4 | mixed:3, text:1 | 10.1208/s12249-015-0474-y:2, 10.1007/s11095-008-9785-y:1, 10.1016/j.jpba.2019.04.040:1 |

### Claude Baseline (E3_claude_v2)

| Step | additional verified | routes | top papers |
| --- | --- | --- | --- |
| v1 strict -> v2 accept_wv | 24 | table:24 | 10.1208/s12249-013-9995-4:24 |
| v2 accept_wv -> v3 any_conc | 14 | mixed:14 | 10.1248/cpb.c21-00033:11, 10.1186/2050-6511-13-5:3 |
| v3 any_conc -> v4 accept_flux | 9 | mixed:9 | 10.1186/2050-6511-13-5:6, 10.1248/cpb.c21-00033:3 |

## V4 New Verified Analysis

### GPT Baseline (full_run_16)

- New v4 verified vs v3: `4`
- Flux/Jss/Kp/Papp-like among new v4 verified: `4`
- Source papers for flux-like new verified: `3`
- Non-ibuprofen verified records under v4: `0`

| Endpoint kind | Count |
| --- | --- |
| jss | 3 |
| flux | 1 |

| record_id | doi | route | label | api | api_raw | endpoint | time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| record_2c9fa747f279 | 10.1007/s11095-008-9785-y | mixed | text_1 | ibuprofen | 10 mg/ml | jss 2.99 - | 0.5 hr |
| record_8cbb8eafc69e | 10.1016/j.jpba.2019.04.040 | text | text_1 | ibuprofen | Ibuprofen formulation with Acetone treatment | flux 0.1 mg/cm2/h | 1.0 h |
| record_e6ee5fbe2ba0 | 10.1208/s12249-015-0474-y | mixed | text_2 | ibuprofen | N/A | jss 169.85 ug/(cm2 h) | 8.0 h |
| record_f1bd4b546c11 | 10.1208/s12249-015-0474-y | mixed | text_1 | ibuprofen | N/A | jss 113.09 ug/(cm2 h) | 8.0 h |

### Claude Baseline (E3_claude_v2)

- New v4 verified vs v3: `9`
- Flux/Jss/Kp/Papp-like among new v4 verified: `9`
- Source papers for flux-like new verified: `2`
- Non-ibuprofen verified records under v4: `0`

| Endpoint kind | Count |
| --- | --- |
| flux | 7 |
| jss | 2 |

| record_id | doi | route | label | api | api_raw | endpoint | time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| record_251f93e67bb6 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 300 um microneedle | ibuprofen | 80% saturated solution | flux 431.52 ug/cm2/h | 6.0 hours |
| record_625975cc9b8d | 10.1248/cpb.c21-00033 | mixed | ibuprofen-suspended aqueous solution (Av=1) | ibuprofen | ~3x solubility in water, stirred 37 degrees C 24h (suspended solution) | flux 2.35 umol/cm2/h | 8.0 h |
| record_93126011b4da | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - Control | ibuprofen | 80% saturated solution | flux 1.92 10-6 cm/s | 6.0 hours |
| record_a1bb31150869 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 200 um microneedle | ibuprofen | 80% saturated solution | flux 4.21 10-6 cm/s | 6.0 hours |
| record_b8450d40a00a | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 200 um microneedle | ibuprofen | 80% saturated solution | flux 368.69 ug/cm2/h | 6.0 hours |
| record_bb1cbf1d5f0b | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - 300 um microneedle | ibuprofen | 80% saturated solution | flux 5.27 10-6 cm/s | 6.0 hours |
| record_dd3d59a50f07 | 10.1248/cpb.c21-00033 | mixed | text_2 | ibuprofen | approximately 3x solubility in water; suspended (activity = 1.0) | jss 2.35 umol/cm2/h | 8.0 h |
| record_e0c6a4b1b913 | 10.1186/2050-6511-13-5 | mixed | Ibuprofen - Control | ibuprofen | 80% saturated solution | flux 167.78 ug/cm2/h | 6.0 hours |
| record_efda20e2468c | 10.1248/cpb.c21-00033 | mixed | text_1 | ibuprofen | molar fraction of ibuprofen = 0.5 (equimolar with lidocaine); 100% IL, no free ibuprofen | jss 1.18 umol/cm2/h | 8.0 h |

## Key Findings

1. GPT verified progression is `1 -> 25 -> 47 -> 51`.
2. Claude verified progression is `0 -> 24 -> 38 -> 47`.
3. Concentration relaxation contributes the largest gain for both baselines: v1->v2 recovers the shared 24 table records from `10.1208/s12249-013-9995-4`, while v2->v3 adds records from additional ibuprofen concentrations.
4. Endpoint-type relaxation adds `4` GPT records and `9` Claude records; all of these are flux/Jss/Kp/Papp-like by endpoint kind/unit/context in the current extracted records.
5. Under the widest v4 policy, GPT has `51` verified records and Claude has `47` verified records on the same frozen corpus, with Claude still missing GPT's figure verified record but gaining more mixed-route flux records.
6. No v4 verified record has a non-ibuprofen `api_name`, so this rescore did not surface an obvious non-target-API false positive under the available structured records.
