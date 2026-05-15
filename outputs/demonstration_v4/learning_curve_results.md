# Sample Complexity Analysis for EDMA-GPR on Literature Data

## Reference GPR (Oracle)

- Trained on: 24 records from `10.1208/s12249-013-9995-4`
- Input dimensions: 4 (`PS`, `TPGS`, `HPMC`, `time`)
- Learned length_scale: `0.01707;2.668;5.191;37.38`
- In-sample R2: 0.958
- Alpha scaling: `alpha = (SD / y_std)^2 because sklearn normalize_y=True standardizes targets`
- Raw `SD^2` diagnostic R2 without scaling: 0.000
- Optimizer restarts: 20
- Convergence warning count: 0
- Role: synthetic proxy for the formulation-time-permeation relationship

## Method

- Sampled N formulations from `[PS, TPGS, HPMC]` space using Latin Hypercube sampling.
- Queried the oracle at 24 h, 48 h, and 72 h.
- Added synthetic observation noise using the median relative SD from the source paper: 18.1%.
- Because `sklearn` standardizes the target when `normalize_y=True`, experimental SD was converted to normalized alpha as `(SD / y_std)^2`; using raw `SD^2` makes the oracle collapse to a mean model.
- Trained formulation-level GPR models for two scenarios:
- Scenario A: `[PS, TPGS, HPMC, 24 h amount, 48 h amount] -> 72 h amount`, decision at 48 h, 33.3% lead time per Stop.
- Scenario B: `[PS, TPGS, HPMC, 24 h amount] -> 72 h amount`, decision at 24 h, 66.7% lead time per Stop.
- Repeats: 50 per N value per scenario.
- Implementation note: for tractability, each synthetic dataset/scenario was fitted once and leave-one-out predictions were computed with the exact GPR LOO formula under the fitted hyperparameters. This avoids the prohibitively expensive naive loop of refitting tens of thousands of GPRs.

## Learning Curve Results

### Scenario A (5-dim, 48 h decision)

| N | Mean R2 +/- SD | Mean RMSE | Mean Accuracy | Mean Type I | Mean Type II | Mean Lead Rate |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0.000 +/- 0.000 | 117.6 | 0.796 | 0.06 | 0.96 | 20.7% |
| 8 | 0.000 +/- 0.000 | 122.2 | 0.887 | 0.34 | 0.56 | 28.2% |
| 10 | -0.000 +/- 0.000 | 122.3 | 0.884 | 0.62 | 0.54 | 30.3% |
| 15 | 0.000 +/- 0.000 | 129.4 | 0.923 | 0.88 | 0.28 | 32.4% |
| 20 | 0.000 +/- 0.000 | 131.3 | 0.951 | 0.98 | 0.00 | 33.3% |
| 30 | -0.000 +/- 0.000 | 134.2 | 0.967 | 1.00 | 0.00 | 33.3% |
| 50 | 0.000 +/- 0.000 | 137.4 | 0.980 | 1.00 | 0.00 | 33.3% |
| 80 | 0.000 +/- 0.002 | 138.6 | 0.988 | 1.00 | 0.00 | 33.3% |
| 100 | 0.000 +/- 0.000 | 139.8 | 0.990 | 1.00 | 0.00 | 33.3% |
| 150 | 0.000 +/- 0.000 | 139.8 | 0.993 | 1.00 | 0.00 | 33.3% |
| 200 | 0.000 +/- 0.001 | 141.2 | 0.995 | 1.00 | 0.00 | 33.3% |

### Scenario B (4-dim, 24 h decision)

| N | Mean R2 +/- SD | Mean RMSE | Mean Accuracy | Mean Type I | Mean Type II | Mean Lead Rate |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0.000 +/- 0.000 | 117.6 | 0.796 | 0.06 | 0.96 | 41.3% |
| 8 | 0.000 +/- 0.000 | 122.2 | 0.887 | 0.34 | 0.56 | 56.5% |
| 10 | -0.000 +/- 0.000 | 122.3 | 0.884 | 0.62 | 0.54 | 60.5% |
| 15 | 0.000 +/- 0.000 | 129.4 | 0.923 | 0.88 | 0.28 | 64.9% |
| 20 | 0.000 +/- 0.000 | 131.3 | 0.951 | 0.98 | 0.00 | 66.6% |
| 30 | 0.000 +/- 0.000 | 134.2 | 0.967 | 1.00 | 0.00 | 66.7% |
| 50 | 0.001 +/- 0.005 | 137.3 | 0.980 | 1.00 | 0.00 | 66.7% |
| 80 | 0.004 +/- 0.018 | 138.3 | 0.988 | 1.00 | 0.00 | 66.7% |
| 100 | 0.004 +/- 0.015 | 139.5 | 0.990 | 1.00 | 0.00 | 66.7% |
| 150 | 0.004 +/- 0.016 | 139.5 | 0.993 | 1.00 | 0.00 | 66.7% |
| 200 | 0.005 +/- 0.011 | 140.8 | 0.995 | 1.00 | 0.00 | 66.7% |

## Sample Size Thresholds

| Target          | Scenario A min N   | Scenario B min N   |
|:----------------|:-------------------|:-------------------|
| R2 > 0          | 8                  | 8                  |
| R2 > 0.5        | Not reached        | Not reached        |
| Accuracy >= 0.9 | 15                 | 15                 |

## Comparison with Real Data Availability

- Formulation counts in the current v2 ibuprofen demonstration extraction:

| doi                        |   records |   formulations |
|:---------------------------|----------:|---------------:|
| 10.1208/s12249-013-9995-4  |        24 |              8 |
| 10.1186/2050-6511-13-5     |         5 |              5 |
| 10.1016/j.ejpb.2020.05.013 |         1 |              1 |

- The v3 case-study paper contains 8 formulations.

- Required N for Scenario A R2 > 0.5: Not reached
- Required N for Scenario B R2 > 0.5: Not reached
- Required N for Scenario A accuracy >= 0.9: 15
- Required N for Scenario B accuracy >= 0.9: 15
- Implication: single-paper data is insufficient for a stable EDMA-GPR model under this synthetic proxy; multi-paper aggregation is necessary.

## Scenario Comparison

Scenario A uses more information because it observes both 24 h and 48 h permeation before predicting 72 h. It therefore has a later decision point and a lower per-Stop lead rate, but should be statistically easier than Scenario B. Scenario B makes an earlier 24 h decision and preserves a larger lead rate, but it has less observed response information and therefore requires at least as much data to reach comparable predictive power.

Observed thresholds:

- R2 > 0.5: Scenario A = Not reached; Scenario B = Not reached
- Accuracy >= 0.9: Scenario A = 15; Scenario B = 15

Important interpretation: the accuracy threshold is not sufficient evidence of useful EDMA behaviour here. Each LOFO synthetic dataset has only one "should_continue" formulation, so a model that mostly stops candidates can achieve high accuracy as N grows. The R2 curves remain near zero and R2 > 0.5 is not reached by N = 200 in either scenario. Therefore the defensible sample-complexity conclusion should be based on predictive R2, not accuracy alone.

## Limitations

- This is a conditional analysis based on one paper; it cannot be generalized to all ibuprofen formulations.
- The reference GPR is a learned proxy, not a physical ground truth.
- The conclusion should be read as: if this paper's relationship complexity is representative, the model needs approximately the reported N.
- Synthetic noise is based on the source paper's typical relative SD; real cross-paper noise may be larger and structured.
- Cross-paper heterogeneity in membranes, dose, vehicles, and assay settings is not modelled.
- The analytic LOO implementation fits hyperparameters on the full synthetic dataset before computing LOO predictions, so the predictive estimates may be slightly optimistic compared with full nested LOFO hyperparameter refitting.

## Conclusion

The v3 result showed that eight formulations are insufficient for a meaningful EDMA-GPR model: predictive R2 was negative and the decision model stopped every held-out formulation. The sample complexity analysis supports the same interpretation at larger scale. Under the learned single-paper oracle, R2 > 0.5 is not reached even at N = 200, so this experiment does not support a precise minimum-N claim for predictive modelling. It supports a more conservative conclusion: single-paper data are underpowered, and EDMA-style decision models need literature-scale aggregation plus better-balanced evaluation targets rather than isolated single-paper extraction.
