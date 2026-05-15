# E7 Table-Support Promotion Ablation: no table promotion vs full_run_13

Variable under test: `--no-table-promotion` disables assembly-time table-support promotion into non-table records. Patching, policy, model configuration, figure pipeline, and adjudication remain enabled. This is a fresh LLM run, so upstream stochasticity is a residual confound.

## Manifest Check

- Output dir: `outputs\experiment_E7_no_promotion`
- Policy: `v1_strict_ibuprofen_5pct`
- Model: `gpt-4o-mini`
- `patching_enabled`: `True`
- `table_promotion_enabled`: `False`

## Overall

| Metric | full_run_13 baseline | E7 no promotion | Delta |
|---|---:|---:|---:|
| final records | 79 | 73 | -6 |
| verified | 4 | 4 | +0 |
| unresolved | 48 | 47 | -1 |
| rejected | 27 | 22 | -5 |

## Verified By Route

| Route | full_run_13 | E7 no promotion | Delta |
|---|---:|---:|---:|
| table | 0 | 0 | +0 |
| text | 0 | 0 | +0 |
| mixed | 0 | 0 | +0 |
| figure | 4 | 4 | +0 |

## Table-Support Metadata

| Metric | full_run_13 | E7 no promotion | Delta |
|---|---:|---:|---:|
| records with `table_support_record_ids` route=text | 0 | 0 | +0 |
| records with `table_support_record_ids` route=mixed | 0 | 0 | +0 |
| records with `table_support_record_ids` route=figure | 0 | 0 | +0 |
| records with `table_support_record_ids` route=table | 0 | 0 | +0 |
| promoted-support records with formulation_label | 0 | 0 | +0 |
| promoted-support records with api_concentration_value | 0 | 0 | +0 |
| promoted-support records with diffusion_area_cm2 | 0 | 0 | +0 |
| promoted-support records with support_evidence | 0 | 0 | +0 |

## Failure Taxonomy Changes

| failure_reason | full_run_13 | E7 no promotion | Delta |
|---|---:|---:|---:|
| not_target_api | 16 | 6 | -10 |
| figure_digitization_failed | 8 | 2 | -6 |
| ambiguous_api_concentration | 42 | 38 | -4 |
| missing_area | 14 | 18 | +4 |
| missing_endpoint | 11 | 7 | -4 |
| insufficient_evidence | 54 | 51 | -3 |
| not_target_api_concentration | 10 | 13 | +3 |
| percent_only | 6 | 4 | -2 |
| not_target_device | 3 | 5 | +2 |

## Record-Level Verified Churn

- Both runs verified by record_id: `1`
- Verified in baseline but not E7: `3`
- Verified in E7 but not baseline: `3`

Baseline-only verified:
- `record_1f7ffa0296ea` 10.1016/j.ijpharm.2016.03.043 figure Isopropyl Alcohol Solution endpoint=136.0 μg/cm²
- `record_af2bc3931fdb` 10.1016/j.ijpharm.2016.03.043 figure PEG 300 Solution endpoint=136.0 μg/cm²
- `record_e5a5cd848fa6` 10.1016/j.ijpharm.2016.03.043 figure IBUGEL™ endpoint=136.0 μg/cm²

E7-only verified:
- `record_5bc4d003491f` 10.1016/j.ijpharm.2016.03.043 figure IBUGEL™ (Ibuprofen 5% w/w) endpoint=11.0 µg/cm2
- `record_8ad9e33e54f0` 10.1016/j.ijpharm.2016.03.043 figure IBULEVE™ Speed Relief 5% Spray endpoint=28.0 μg/cm²
- `record_9c767c2806d6` 10.1016/j.ijpharm.2016.03.043 figure IBUGEL™ (Ibuprofen 5% w/w) endpoint=42.0 μg/cm²

## Cost

| Metric | full_run_13 | E7 no promotion | Delta |
|---|---:|---:|---:|
| total tokens | 3838632 | 3443207 | -395425 |
| elapsed seconds | 5003.045 | 5643.683 | +640.638 |

## Interpretation

- Final verified count matched baseline at 4, with figure remaining the only verified route in this V1-scope ablation.
- Disabling table promotion removed `table_support_record_ids` metadata from final records, but it did not reduce verified count in this run.
- Table route verified remains 0 under V1, consistent with the expectation that this promotion primarily affects text/mixed/figure support rather than creating table verified records under strict 5% w/w policy.
- As with E6, fresh-run stochasticity affects route/extraction counts, so record-level churn should be interpreted cautiously.
