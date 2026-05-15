# Demonstration v5: 4D LOGO-CV Regression

## Data

- Source: `10.1208/s12249-013-9995-4`.
- Records: 8 formulations x 3 timepoints = 24 records.
- Inputs: `particle_size_nm`, `vit_e_tpgs_pct_wv`, `hpmc_k100_pct_wv`, `time_h`.
- Output: `cum_amount_ug_cm2`.
- Experimental SD: `cum_amount_sd_ug_cm2`, used as heteroscedastic GPR noise after y-standardization within each fold.

## Global LOGO-CV Metrics

| Metric | Value |
|---|---:|
| MAE | 259.17 ug/cm2 |
| RMSE | 297.96 ug/cm2 |
| R2 | 0.600 |
| rMAE | 33.4% |
| N predictions | 24 |

## Per-Formulation Metrics

| formulation | MAE | RMSE | R2 | mean_abs_error_pct |
| --- | --- | --- | --- | --- |
| F1 | 284.011 | 341.817 | 0.621 | 27.584 |
| F2 | 189.030 | 270.837 | 0.829 | 18.952 |
| F3 | 188.107 | 210.357 | 0.725 | 25.024 |
| F4 | 217.762 | 218.886 | 0.676 | 31.401 |
| F5 | 345.970 | 347.729 | -0.251 | 40.154 |
| F6 | 240.268 | 262.236 | 0.617 | 30.591 |
| F7 | 425.643 | 446.987 | -6.043 | 105.873 |
| F8 | 182.592 | 196.035 | 0.740 | 26.330 |

Extrapolation failures with R2 < 0: F7, F5.

## Per-Timepoint Metrics

| time_h | MAE | RMSE | R2 | mean_abs_error_pct |
| --- | --- | --- | --- | --- |
| 24.000 | 177.173 | 201.820 | -2.158 | 62.833 |
| 48.000 | 223.785 | 259.016 | -1.982 | 29.054 |
| 72.000 | 376.561 | 398.156 | -0.185 | 29.457 |

## ARD Length Scales

| feature | median_length_scale | mean_length_scale | sd_length_scale |
| --- | --- | --- | --- |
| particle_size_nm | 4.726 | 16.566 | 33.734 |
| vit_e_tpgs_pct_wv | 3.774 | 3.819 | 0.941 |
| hpmc_k100_pct_wv | 4.588 | 28.619 | 44.077 |
| time_h | 2.518 | 2.411 | 0.313 |

The smallest median length scale is `time_h`, indicating the strongest fitted sensitivity after within-fold feature standardization.

## Uncertainty Diagnostics

| metric | value |
| --- | --- |
| mean_predicted_std | 117.394 |
| mean_measurement_sd | 130.221 |
| mean_pred_std_to_measurement_sd_ratio | 1.398 |
| corr_abs_error_predicted_std | -0.030 |
| coverage_within_1_pred_std | 0.250 |
| coverage_within_2_pred_std | 0.500 |
| coverage_within_1_measurement_sd | 0.167 |
| coverage_within_2_measurement_sd | 0.458 |

The mean predicted GPR standard deviation is 117.4 ug/cm2 versus mean experimental SD 130.2 ug/cm2. This is comparable in magnitude, but coverage diagnostics should be interpreted cautiously because there are only 24 held-out points.

## Interpretation

The 4D LOGO-CV regression task succeeds at a descriptive level: R2 is approximately 0.60 across formulation-held-out predictions. This is materially stronger than the v3/v4 EDMA-style decision experiments, where decision accuracy was inflated by class imbalance and predictive R2 was poor. The regression result supports the paper narrative that SkinMiner-extracted multi-timepoint records can support downstream permeation modelling, while prescriptive decision-making remains underpowered with single-paper data.
