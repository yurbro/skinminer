# E8 Relaxed Scope Delta vs full_run_14 V2 policy

Variable under test: `v3_any_ibuprofen_concentration`, which keeps the non-concentration V1 gates and accepts any explicitly ibuprofen concentration. This is a fresh full run, so LLM stochasticity remains a residual confound in record-level comparisons.

## Manifest Check

- Output dir: `outputs\experiment_E8_relaxed_scope`
- Policy: `v3_any_ibuprofen_concentration`
- Model: `gpt-4o-mini`
- `patching_enabled`: `True`
- `table_promotion_enabled`: `True`

## Overall

| Metric | full_run_14 V2 policy | E8 relaxed scope | Delta |
|---|---:|---:|---:|
| final records | 75 | 74 | -1 |
| verified | 10 | 14 | +4 |
| unresolved | 43 | 37 | -6 |
| rejected | 22 | 23 | +1 |

## Verified By Route

| Route | full_run_14 V2 policy | E8 | Delta |
|---|---:|---:|---:|
| table | 6 | 3 | -3 |
| text | 0 | 0 | +0 |
| mixed | 0 | 1 | +1 |
| figure | 4 | 10 | +6 |

## New Verified Records in E8

- New verified by record_id: `11` from `5` papers.
- Lost verified from full_run_14 V2 policy: `7`.
- Concentration distribution among new verified: `{'0.1/0.9 to 0.9/0.1': 1, '5 % w/w w/w': 3, '1 % w/w w/w': 4, 'n/a': 3}`
- Non-ibuprofen verified in E8: `0`

| record_id | doi | route | label | api_name | concentration | endpoint |
|---|---|---|---|---|---|---|
| record_01db7816996b | 10.1248/cpb.c21-00033 | figure | Ibuprofen IL Preparation | Ibuprofen | 0.1/0.9 to 0.9/0.1 | 10 mg |
| record_11e1060dff8a | 10.1016/j.ijpharm.2016.03.043 | figure | PG with Ibuprofen | Ibuprofen | 5 % w/w w/w | 50 µg/cm² |
| record_21f5c1d577fe | 10.1208/s12249-019-1584-8 | figure | Ibuprofen-Loaded Microemulsion-Based HA Hydrogel (ME/Gel) | Ibuprofen | 1 % w/w w/w | 36 mg/cm² |
| record_5290a8861f9d | 10.1039/d0ra00100g | table | Ibuprofen Cumulative Mass Data | Ibuprofen | n/a | 215.19 mg IBU cm−2 |
| record_8407354dd430 | 10.1208/s12249-019-1584-8 | figure | Ibuprofen-Loaded Microemulsion (ME) | Ibuprofen | 1 % w/w w/w | 290 μg/cm² |
| record_b01078f51908 | 10.1039/d0ra00100g | table | Ibuprofen Release Study | Ibuprofen | n/a | 382.35 mg IBU cm−2 |
| record_c0f9bf24103e | 10.1016/j.rinphs.2012.10.001 | mixed | Ibuprofen 1% | Ibuprofen | 1 % w/w w/w | 0.5 mg/cm² |
| record_d2c312dcd674 | 10.1039/d0ra00100g | table | Ibuprofen Skin Penetration Study | Ibuprofen | n/a | 341.2 mg IBU cm−2 |
| record_d43f2966ed52 | 10.1016/j.ijpharm.2016.03.043 | figure | PG with Ibuprofen | Ibuprofen | 5 % w/w w/w | 50 µg/cm² |
| record_d4f4148d882d | 10.1016/j.ijpharm.2016.03.043 | figure | Isopropyl Alcohol with Ibuprofen | Ibuprofen | 5 % w/w w/w | 38 µg/cm2 |
| record_f0359ab9e58a | 10.1208/s12249-019-1584-8 | figure | Ibuprofen-Loaded Microemulsion (ME) | Ibuprofen | 1 % w/w w/w | 24 mg/cm² |

## Failure Taxonomy Changes

| failure_reason | reference | E8 | Delta |
|---|---:|---:|---:|
| ambiguous_api_concentration | 26 | 0 | -26 |
| missing_endpoint | 9 | 4 | -5 |
| percent_only | 2 | 7 | +5 |
| missing_area | 17 | 14 | -3 |
| not_target_api | 11 | 14 | +3 |
| figure_digitization_failed | 5 | 2 | -3 |
| not_target_study_type | 9 | 7 | -2 |
| not_target_device | 5 | 3 | -2 |
| not_target_api_concentration | 10 | 9 | -1 |
| missing_api_concentration | 1 | 0 | -1 |

## Cost

| Metric | reference | E8 | Delta |
|---|---:|---:|---:|
| total tokens | 3631862 | 3640967 | +9105 |
| elapsed seconds | 5456.629 | 5569.776 | +113.147 |

## Interpretation

- E8 increases verified output by relaxing only the concentration gate, while keeping the Franz / IVPT-IVRT / amount endpoint / endpoint time constraints.
- The key buckets to watch are `ambiguous_api_concentration` and `not_target_api_concentration`; reductions there indicate records rescued by the relaxed concentration policy.
- Any verified row whose API name is not ibuprofen should be treated as a policy false-positive risk and manually audited.
