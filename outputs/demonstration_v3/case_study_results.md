# Single-Paper EDMA Case Study: Application to SkinMiner-Extracted Literature

## Source Paper

- DOI: `10.1208/s12249-013-9995-4`
- Topic: ibuprofen nanosuspension formulations from Kallakunta et al., AAPS PharmSciTech, 2013.
- Data shape: 8 formulations x 3 timepoints = 24 records.
- API concentration: 5% w/v ibuprofen.
- Membrane: dermatomed porcine skin.
- Diffusion area: 0.64 cm2.
- SD values: manually extracted from Table II and used as true experimental noise.

## Data Validation

- Manual records: 24
- SkinMiner records for this DOI: 24
- Matched formulation x timepoint keys: 24
- Maximum absolute difference: 2.84217e-14 ug/cm2
- Consistent within tolerance: True

The validation table is saved as `validation_manual_vs_skinminer.csv`. The cumulative amount values are identical after converting the Table II units from ug to ug/cm2 by dividing by 0.64.

## Method

The model uses the same Gaussian process family as Paper 1: `ConstantKernel * RBF`, scenario-specific input dimensions, `n_restarts_optimizer = 10`, and `normalize_y = True`. Leave-one-formulation-out cross-validation was used. The decision threshold is `T = 0.2`: `PoE < 0.2` is classified as Stop; otherwise Continue.

Feature order for the learned length scales is Scenario A: `[particle size, TPGS, HPMC, 24 h amount, 48 h amount]`; Scenario B: `[particle size, TPGS, HPMC, 24 h amount]`. Scenario A uses `alpha = sd72^2 + sd24^2 + sd48^2`; Scenario B uses `alpha = sd72^2 + sd24^2`.

## Scenario A: Decision Using 24 h + 48 h Data

This scenario trains a formulation-level model `[PS, TPGS, HPMC, 24 h amount, 48 h amount] -> 72 h amount` using the other seven formulations. It represents a 48 h decision point.

| formulation_label | actual_72h_ug_cm2 | pred_72h_ug_cm2 | std_72h_ug_cm2 | poe | decision | actual_label | outcome | correct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | 1785.00 | 1205.96 | 13.36 | 0.00 | Stop | should_stop | TN | True |
| F2 | 1842.03 | 1197.81 | 12.74 | 0.00 | Stop | should_continue | FN | False |
| F3 | 1186.88 | 1291.41 | 15.61 | 0.00 | Stop | should_stop | TN | True |
| F4 | 1147.50 | 1297.03 | 15.54 | 0.00 | Stop | should_stop | TN | True |
| F5 | 1249.22 | 1282.50 | 15.67 | 0.00 | Stop | should_stop | TN | True |
| F6 | 1262.50 | 1280.60 | 15.68 | 0.00 | Stop | should_stop | TN | True |
| F7 | 606.09 | 1374.38 | 11.28 | 0.00 | Stop | should_stop | TN | True |
| F8 | 1147.50 | 1297.03 | 15.54 | 0.00 | Stop | should_stop | TN | True |

| Metric | Value |
| --- | --- |
| Accuracy | 7/8 = 87.5% |
| Type I error | 1 |
| Type II error | 0 |
| Stop / Continue | 8 / 0 |
| Lead Rate | 33.3% |
| RMSE | 418.0 ug/cm2 |
| R2 | -0.306 |
| Median length_scale | 43.38;0.1084;4.468;0.1765;1.203 |
| Folds with convergence warnings | 0 |

## Scenario B: Decision Using 24 h Only

This scenario trains a formulation-level model `[PS, TPGS, HPMC, 24 h amount] -> 72 h amount`. It represents the earlier 24 h decision point and is closest to the EDMA setup in Paper 1.

| formulation_label | actual_72h_ug_cm2 | pred_72h_ug_cm2 | std_72h_ug_cm2 | poe | decision | actual_label | outcome | correct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | 1785.00 | 1205.96 | 12.14 | 0.00 | Stop | should_stop | TN | True |
| F2 | 1842.03 | 1197.81 | 11.58 | 0.00 | Stop | should_continue | FN | False |
| F3 | 1186.88 | 1291.41 | 14.19 | 0.00 | Stop | should_stop | TN | True |
| F4 | 1147.50 | 1297.03 | 14.12 | 0.00 | Stop | should_stop | TN | True |
| F5 | 1249.22 | 1282.50 | 14.25 | 0.00 | Stop | should_stop | TN | True |
| F6 | 1262.50 | 1280.60 | 14.25 | 0.00 | Stop | should_stop | TN | True |
| F7 | 606.09 | 1374.38 | 10.25 | 0.00 | Stop | should_stop | TN | True |
| F8 | 1147.50 | 1297.03 | 14.12 | 0.00 | Stop | should_stop | TN | True |

| Metric | Value |
| --- | --- |
| Accuracy | 7/8 = 87.5% |
| Type I error | 1 |
| Type II error | 0 |
| Stop / Continue | 8 / 0 |
| Lead Rate | 66.7% |
| RMSE | 418.0 ug/cm2 |
| R2 | -0.306 |
| Median length_scale | 75.79;21.37;0.07069;0.05337 |
| Folds with convergence warnings | 0 |

## GPR Model Quality

| Metric | Scenario A | Scenario B |
| --- | --- | --- |
| RMSE (ug/cm2) | 417.978 | 417.978 |
| R2 | -0.306 | -0.306 |
| Median length_scale | 43.38;0.1084;4.468;0.1765;1.203 | 75.79;21.37;0.07069;0.05337 |
| Warning folds | 0 | 0 |

Convergence note: Model fitting completed for all folds with no convergence warnings.

## Comparison with Paper 1

| Metric | Paper 1 baseline | This case study, Scenario A | This case study, Scenario B |
|---|---:|---:|---:|
| Accuracy | 5/5 = 100.0% | 7/8 = 87.5% | 7/8 = 87.5% |
| Type I error | 0 | 1 | 1 |
| Type II error | 0 | 0 | 0 |
| Lead Rate | 96.4% | 33.3% | 66.7% |

## Interpretation

This case study demonstrates that SkinMiner-derived literature data can be connected to the EDMA workflow when formulation factors, timepoints, endpoint values, and experimental SD are available. The result is a focused feasibility demonstration rather than a general performance claim.

Key limitations:

- The SD values are manually extracted from Table II, not produced by the current SkinMiner schema. This directly motivates a schema extension for endpoint uncertainty.
- The experiment contains only eight formulations, so statistical inference is limited.
- The result is from a single paper and cannot be generalized to other APIs, membranes, or formulation systems.
- The TPGS/HPMC nanosuspension system is not the same as the Paper 1 Poloxamer system, so the comparison is methodological rather than formulation-equivalent.

## Generated Outputs

- Source data: `source_paper_data.csv`
- Data validation: `validation_manual_vs_skinminer.csv`
- Scenario A results: `scenario_a_lofo_results.csv`
- Scenario B results: `scenario_b_24h_results.csv`
- Metrics: `scenario_metrics.csv`
- Figure 1: `figures/fig_case_study.png` and `figures/fig_case_study.pdf`
- Figure 2: `figures/fig_decision_timeline.png` and `figures/fig_decision_timeline.pdf`
