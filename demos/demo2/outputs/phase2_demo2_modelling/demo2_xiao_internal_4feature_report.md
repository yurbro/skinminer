# Demo 2 Step 2k: Xiao-Internal 4-Feature LOOCV and Literature-Data Value

## Setup and Missing Comparison Cell

This analysis adds the missing Xiao-only reference under the exact Demo 2 main-line configuration: the 4-feature bridge (`log10_vehicle_solubility`, `ethanol_fraction`, `pg_fraction`, `water_fraction`), StandardScaler fitted on training rows only, Ridge(alpha=1.0), and log10(J) target. No SkinMiner source code or model hyperparameters were changed.

BBD4/BBD5/BBD6 are the identical 25/15/15/5/35 center-point triplet. They are held out together in one group fold and are never split between train and test. Leakage-guard status: PASS; zero violations.

Arithmetic clarification: with all 29 Xiao records retained, the center-group fold trains on 26 records and each of the 26 single-record folds trains on 28 records. The exact average is 27.926 training records per fold. The prompt's references to 25 records and an average of 27.6 are inconsistent with a full 29-record grouped LOOCV, so no center records were discarded to force those numbers.

## Xiao-Internal 4-Feature Grouped LOOCV

| Metric | Value |
|---|---:|
| R2_conv | -0.210078 |
| RMSE_logJ | 0.065900 |
| Spearman rho | -0.069492 |
| Pearson r | -0.139794 |
| within-2x | 29/29 (1.000000) |
| folds / pooled predictions | 27 / 29 |

The Xiao-internal R2_conv is negative (-0.210). All 29 predictions are within two-fold, but this is not evidence of strong modelling because Xiao log10(J) occupies a narrow range: the negative R2_conv and near-zero rank correlation show that the 4-feature model does not recover record-level variation better than the test-mean baseline.

This is consistent with earlier Xiao-internal findings that the in-house flux variation approaches measurement uncertainty. The value of this new cell is not novelty of sign, but a fair main-line-feature reference for the literature augmentation comparison.

## Literature-Data-Value Comparison

| Training set | n_train | Test set | R2_conv | RMSE_logJ | Spearman rho | within-2x |
|---|---:|---|---:|---:|---:|---:|
| Xiao-only (grouped LOOCV) | 26 for center-group fold; 28 for single-record folds | held-out Xiao (29 pooled predictions) | -0.210 | 0.066 | -0.069 | 29/29 |
| Bolla-only (zero-shot, k=0) | 8 Bolla | all 29 Xiao | -15.988 +/- 0.000 | 0.247 +/- 0.000 | 0.068 +/- 0.000 | 24/29 |
| Bolla + 12 Xiao (few-shot k=12 mean) | 8 Bolla + 12 Xiao | remaining 17 Xiao; varies across 200 subsets | -3.557 +/- 1.904 | 0.121 +/- 0.019 | -0.019 +/- 0.179 | 0.998 +/- 0.010 |

The k=0 and k=12 few-shot rows were read from `fewshot_summary_table.csv` and independently reaggregated from `fewshot_bolla_to_xiao_results.json`. Audit status: PASS.

## Interpretation

1. **Xiao-only performance.** Xiao-internal grouped LOOCV is negative: R2_conv=-0.210, RMSE_logJ=0.066, and Spearman rho=-0.069. The low RMSE and 29/29 within-2x result reflect the narrow Xiao response range; R2_conv remains the primary reading.

2. **Does Bolla-only training help Xiao prediction?** No. Relative to Xiao-only LOOCV, Bolla-only zero-shot changes R2_conv from -0.210 to -15.988 and RMSE_logJ from 0.066 to 0.247. This is substantially worse magnitude prediction. Spearman remains near zero in both cases, so Bolla does not add useful ordering signal.

3. **Does Bolla + 12 Xiao recover Xiao-only performance?** No. The mean k=12 R2_conv is -3.557 +/- 1.904, still well below Xiao-only -0.210; RMSE_logJ is 0.121 +/- 0.019, compared with Xiao-only 0.066. Mean Spearman is -0.019 +/- 0.179, which remains compatible with no ordering signal.

The k=12 comparison is approximate rather than exact: each few-shot model is evaluated on a different 17-record Xiao subset, whereas Xiao-only LOOCV pools predictions for all 29 records. The k=12 model also trains on 20 total records (8 Bolla + 12 Xiao), compared with 26 or 28 Xiao records per internal fold. The robust result is directional: adding out-of-distribution Bolla records does not approach the Xiao-only R2_conv or RMSE reference, and rank correlation remains near zero.

## Practical Bottom Line

For this specific Xiao-Bolla pair, literature data provides negative rather than positive augmentation value for predicting in-house flux under the fixed 4-feature Ridge protocol. Bolla-only training is dramatically worse than Xiao-only grouped LOOCV, and adding 12 Xiao anchors to Bolla does not recover Xiao-only performance.

This conclusion is deliberately bounded: it does not imply that literature data is useless in general. On this pair, literature data does not provide useful augmentation signal for in-house modelling because the in-house dataset's own flux variation approaches measurement uncertainty and adding out-of-distribution training records exacerbates rather than ameliorates the prediction problem.

Reducing experiments through literature augmentation requires the literature contribution to be at least neutral and preferably positive. That condition is not met here.

## Output Audit

- `xiao_internal_4feature_loocv_results.json`: 27 fold records, 29 pooled held-out predictions, aggregate metrics, and fold-level scaler/model audit.
- `literature_value_comparison.csv`: structured three-row comparison.
- `run_demo2_literature_value.py`: deterministic standalone harness.
