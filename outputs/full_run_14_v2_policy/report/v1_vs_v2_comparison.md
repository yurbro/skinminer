# Policy Comparison: V1 strict 5% w/w -> V2 accept 5% w/v

Input and model control: both runs use `outputs/full_run_12_full/corpus.csv` and the model configuration recorded in `full_run_13_post_fix5/run_manifest.jsonl`. In that manifest every LLM stage, including figure VLM, is `gpt-4o-mini`; the only configured policy change in full_run_14 is `v2_accept_wv`.

## Overall

| Metric | V1 full_run_13 | V2 full_run_14 | Delta |
|---|---:|---:|---:|
| assembled/final records | 79 | 75 | -4 |
| verified | 4 | 10 | +6 |
| unresolved | 48 | 43 | -5 |
| rejected | 27 | 22 | -5 |

## Verified Breakdown By Route

| Route | V1 verified | V2 verified | Delta |
|---|---:|---:|---:|
| table | 0 | 6 | +6 |
| text | 0 | 0 | +0 |
| mixed | 0 | 0 | +0 |
| figure | 4 | 4 | +0 |
| total | 4 | 10 | +6 |

## New Verified Records In V2

| record_id | doi | route | label | api_concentration | api_basis | endpoint | gold coverage |
|---|---|---|---|---|---|---|---|
| record_851ab860659f | 10.1208/s12249-013-9995-4 | table | F2 | 5 % w/v | w/v | 1178.9 μg | in old gold |
| record_8ad9e33e54f0 | 10.1016/j.ijpharm.2016.03.043 | figure | IBULEVE™ Speed Relief 5% Spray | 5 % w/w | w/w | 42 μg/cm² | not in old gold |
| record_8b2e8239ff2b | 10.1208/s12249-013-9995-4 | table | N2 | 5 % w/v | w/v | 1178.9 μg | not in old gold |
| record_8b7dd5d8bd7f | 10.1016/j.ijpharm.2016.03.043 | figure | IBUGEL™ | 5 % w/w | w/w | 3 μg/cm² | not in old gold |
| record_9d98bd27f9f7 | 10.1208/s12249-013-9995-4 | table | F3 | 5 % w/v | w/v | 759.6 μg | in old gold |
| record_ace3746b1600 | 10.1208/s12249-013-9995-4 | table | F1 | 5 % w/v | w/v | 1142.4 μg | in old gold |
| record_e8222f4e4c6c | 10.1208/s12249-013-9995-4 | table | N1 | 5 % w/v | w/v | 1142.4 μg | not in old gold |
| record_f4fb84fa1eb7 | 10.1208/s12249-013-9995-4 | table | N3 | 5 % w/v | w/v | 759.6 μg | not in old gold |

## V2 New Verified Source Analysis

- Observed new verified vs V1 by record_id: `8` across `2` papers.
- Policy-relevant table w/v gains: `6` records from DOI `10.1208/s12249-013-9995-4`.
- Same-record V1 `ambiguous_api_concentration` -> V2 verified flips: `4` records.
- Full-run table extractor emitted `6` target rows for that paper; the earlier controlled E2 replay emitted 8 rows, so full-run gain is 6 rather than 8.
- Assembly concentration propagation used in final V2 verified records: `0`. In this full run the table extractor already emitted `5% w/v`; the assembly fix remains useful for replay cases where concentration appears only in same-paper composition rows.
- Concentration basis among policy gains: `{'w/v': 6}`.
- V2 verified API names: `{'ibuprofen': 4, 'Ibuprofen': 6}`; no non-ibuprofen verified row was observed.

## Lost V1 Verified Records

These are figure-route run-churn records, not w/v policy effects.

| record_id | doi | route | label | api_concentration | endpoint |
|---|---|---|---|---|---|
| record_1f7ffa0296ea | 10.1016/j.ijpharm.2016.03.043 | figure | Isopropyl Alcohol Solution | 5 % w/w | 136 μg/cm² |
| record_af2bc3931fdb | 10.1016/j.ijpharm.2016.03.043 | figure | PEG 300 Solution | 5 % w/w | 136 μg/cm² |

## Failure Taxonomy Changes

| failure_reason | V1 | V2 | Delta |
|---|---:|---:|---:|
| missing_api_concentration | 1 | 1 | +0 |
| ambiguous_api_concentration | 42 | 26 | -16 |
| not_target_api_concentration | 10 | 10 | +0 |
| insufficient_evidence | 54 | 54 | +0 |
| not_target_api | 16 | 11 | -5 |
| percent_only | 6 | 2 | -4 |
| missing_area | 14 | 17 | +3 |
| not_target_study_type | 12 | 9 | -3 |
| figure_digitization_failed | 8 | 5 | -3 |
| missing_endpoint | 11 | 9 | -2 |
| not_target_device | 3 | 5 | +2 |
| unit_normalization_failed | 3 | 1 | -2 |

## Figure Pipeline Comparison

| Metric | V1 | V2 | Delta |
|---|---:|---:|---:|
| figure records | 9 | 7 | -2 |
| vlm_used_as_final | 8 | 7 | -1 |
| figure verified | 4 | 4 | +0 |

## Cost Comparison

| Metric | V1 | V2 | Delta |
|---|---:|---:|---:|
| total tokens | 3838632 | 3631862 | -206770 |
| elapsed seconds | 5003.045 | 5456.629 | +453.584 |
| LLM adjudication requests | 33 | 20 | -13 |

## Key Observations

1. Net verified increased from 4 to 10 (+6). The route-level gain is entirely table (+6); figure verified count stayed at 4 despite record-id churn.
2. The policy-relevant gain is concentrated in one paper, DOI `10.1208/s12249-013-9995-4`, and all six policy-gain records use `5% w/v` ibuprofen.
3. Assembly propagation did not fire for final V2 verified records in this full run because 4o-mini directly extracted the table concentration on those rows. The assembly fix is still validated by the controlled E2 replay path where concentration is separated into same-paper table rows.
4. `ambiguous_api_concentration` dropped from 42 to 26. This is consistent with accepting `5% w/v`, but the separate full runs also show routing/extraction stochasticity, so record-level deltas should not be interpreted as purely policy-only effects.
5. V2 should be treated as the provisional next baseline if the target definition accepts `5% w/v` or `50 mg/mL`; final default promotion should wait for supplemental annotation of the new V2 positives.
