# E6 Patching Ablation: no patching vs full_run_13

Variable under test: `--no-patching` skips `patch_api_concentration`, `patch_endpoint_value`, `patch_endpoint_time`, and `patch_area`. Policy and model configuration follow `full_run_13_post_fix5`; this is a fresh LLM run, so routing/extraction stochasticity is a residual confound.

## Manifest Check

- Output dir: `outputs\experiment_E6_no_patching`
- Policy: `v1_strict_ibuprofen_5pct`
- Model: `gpt-4o-mini`
- `patching_enabled`: `False`
- `table_promotion_enabled`: `True`

## Overall

| Metric | full_run_13 baseline | E6 no patching | Delta |
|---|---:|---:|---:|
| final records | 79 | 78 | -1 |
| verified | 4 | 6 | +2 |
| unresolved | 48 | 49 | +1 |
| rejected | 27 | 23 | -4 |

## Initial vs Final Verification

| Run | Initial verified | Final verified | Patch-stage verified delta |
|---|---:|---:|---:|
| full_run_13 | 4 | 4 | +0 |
| E6 no patching | 6 | 6 | +0 |

## Verified By Route

| Route | full_run_13 | E6 no patching | Delta |
|---|---:|---:|---:|
| table | 0 | 1 | +1 |
| text | 0 | 0 | +0 |
| mixed | 0 | 0 | +0 |
| figure | 4 | 5 | +1 |

## Patch Applications

| Patcher | full_run_13 applied | E6 applied | Delta |
|---|---:|---:|---:|
| patch_area | 12 | 0 | -12 |
| patch_endpoint_time | 18 | 0 | -18 |
| patch_endpoint_value | 28 | 0 | -28 |
| total | 58 | 0 | -58 |

## Failure Taxonomy Changes

| failure_reason | full_run_13 | E6 no patching | Delta |
|---|---:|---:|---:|
| percent_only | 6 | 18 | +12 |
| ambiguous_api_concentration | 42 | 32 | -10 |
| missing_endpoint_time | 2 | 9 | +7 |
| missing_api_concentration | 1 | 7 | +6 |
| not_target_api | 16 | 12 | -4 |
| figure_digitization_failed | 8 | 5 | -3 |
| insufficient_evidence | 54 | 56 | +2 |
| missing_area | 14 | 12 | -2 |
| not_target_api_concentration | 10 | 12 | +2 |
| not_target_study_type | 12 | 10 | -2 |
| missing_endpoint | 11 | 9 | -2 |
| not_target_device | 3 | 5 | +2 |

## Record-Level Verified Churn

- Both runs verified by record_id: `1`
- Verified in baseline but not E6: `3`
- Verified in E6 but not baseline: `5`

Baseline-only verified:
- `record_1f7ffa0296ea` 10.1016/j.ijpharm.2016.03.043 figure Isopropyl Alcohol Solution endpoint=136.0 μg/cm²
- `record_a28c8f99f0f6` 10.1016/j.ijpharm.2016.03.043 figure IBULEVE™ Speed Relief 5% Spray endpoint=136.0 μg/cm²
- `record_af2bc3931fdb` 10.1016/j.ijpharm.2016.03.043 figure PEG 300 Solution endpoint=136.0 μg/cm²

E6-only verified:
- `record_0f56b717243c` 10.1016/j.ijpharm.2016.03.043 figure PG Solution endpoint=280.0 µg/cm²
- `record_2b009f46d9d5` 10.1016/j.ijpharm.2016.03.043 figure IBULEVE™ Speed Relief endpoint=136.0 µg/cm²
- `record_2b9c8aaaa23e` 10.1016/j.ijpharm.2016.03.043 figure PEG Solution endpoint=100.0 µg/cm²
- `record_6dfc615833ab` 10.1016/j.ijpharm.2016.03.043 figure PEG Solution endpoint=16.183204650878906 µg/cm²
- `record_a39c83e1f599` 10.1016/j.ijpharm.2019.118975 table IBU 5% endpoint=50.0 μg/cm²

## Cost

| Metric | full_run_13 | E6 no patching | Delta |
|---|---:|---:|---:|
| total tokens | 3838632 | 3941833 | +103201 |
| elapsed seconds | 5003.045 | 5685.084 | +682.039 |

## Interpretation

- In this fresh no-patching run, final verified did not decrease versus full_run_13; it increased from 4 to 6 because upstream LLM triage/routing/extraction differed from the baseline run.
- Within full_run_13 itself, patching did not increase verified count (`initial=4`, `final=4`), although it applied many evidence patches and changed failure details.
- Therefore E6 does not show a positive verified-count contribution from patching under this corpus/model setting; its contribution is better described as evidence completion and failure-taxonomy reshaping rather than direct verified uplift.
- The largest baseline patch activity was endpoint, time, and area recovery; see the patch-application table above for field-level contribution.
