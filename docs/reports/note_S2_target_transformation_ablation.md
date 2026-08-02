# §3.5.1 R² Supplement and Target Transformation Ablation

## Motivation

Reviewer-anticipated questions:
1. What is the R² of the §3.5.1 transfer model? (Complement Spearman ρ and within-2× already reported.)
2. Does the log₁₀(J) target transformation affect the within-domain transfer finding (Spearman ρ = 0.706)?

## R² definitions used

- **R²_conventional**: sklearn `r2_score` with test-set mean as baseline (1 − SSE / Σ(actual − test_mean)²). Reviewer default. Can be negative when predictions are distributed more widely than test self-variance.
- **R²_generalisation**: train-set mean as baseline (1 − SSE / Σ(actual − train_mean)²). Measures improvement over "predict the training-set average" strategy. Always ≤ 1; positive values mean the model beats the train-mean naive predictor.

Both are reported because they answer different questions: R²_conventional asks whether the model beats a perfect test-set centre prediction; R²_generalisation asks whether it beats predicting just the train mean.

## Task A: §3.5.1 main R² supplement

Re-fit all four §3.5.1 configurations and compute both R²s and Spearman ρ².

### Sanity check: all four settings reproduce §3.5.1 main results

| Setting | RMSE_logJ replicated | ρ replicated | Pearson r replicated | within_2x replicated |
|---|---|---|---|---|
| Ridge composition_only | 0.206 [PASS] | 0.615 [PASS] | 0.675 [PASS] | 9/12 [PASS] |
| Ridge composition_plus_solubility | 0.199 [PASS] | 0.706 [PASS] | 0.734 [PASS] | 9/12 [PASS] |
| GPR composition_only | 0.332 [PASS] | 0.601 [PASS] | 0.378 [PASS] | 5/12 [PASS] |
| GPR composition_plus_solubility | 0.329 [PASS] | 0.218 [PASS] | 0.392 [PASS] | 5/12 [PASS] |

### Updated Table 3.5.2 with R² (two definitions) and Spearman ρ²

| Model | Feature set | RMSE_logJ | R² (conv) | R² (gen) | Spearman ρ | Spearman ρ² | Pearson r | Within 2× |
|---|---|---|---|---|---|---|---|---|
| Ridge | composition_only | 0.206 | -0.579 | 0.683 | 0.615 | 0.379 | 0.675 | 9/12 |
| Ridge | composition_plus_solubility | 0.199 | -0.473 | 0.704 | 0.706 | 0.499 | 0.734 | 9/12 |
| GPR | composition_only | 0.332 | -3.097 | 0.177 | 0.601 | 0.361 | 0.378 | 5/12 |
| GPR | composition_plus_solubility | 0.329 | -3.026 | 0.191 | 0.218 | 0.048 | 0.392 | 5/12 |

### Interpretation of two R²s in this regime

The test set log₁₀(J) range is narrow (about 0.54 dex). R²_conventional can be negative because it uses the test-set mean as a hard baseline. R²_generalisation uses the train mean; in this transfer task the train mean is shifted from the target-domain test mean, so a model can score positively against that practical cross-domain baseline while still having negative conventional R².

## Task B: Target transformation ablation (log vs raw J)

Single-variable comparison: re-fit §3.5.1's best zero-shot configuration (Ridge α=1.0, composition_plus_solubility features) with J as target instead of log₁₀(J). All other settings are identical.

### Results

| Configuration | Target | Model | RMSE in target | R²_conv (target) | R²_gen (target) | Spearman ρ | RMSE_log_residual | Within 2× | Within 1.5× |
|---|---|---|---|---|---|---|---|---|---|
| log_ridge | log₁₀(J) | Ridge alpha=1.0 | 0.199 | -0.473 | 0.704 | 0.706 | 0.199 | 9/12 | 9/12 |
| log_baseline | log₁₀(J) | train-mean baseline | 0.366 | -3.977 | 0.000 | n/a | 0.366 | 4/12 | 3/12 |
| raw_ridge | J (µg cm⁻² h⁻¹) | Ridge alpha=1.0 | 282.092 | -3.226 | 0.669 | 0.650 | 0.269 | 9/12 | 6/12 |
| raw_baseline | J (µg cm⁻² h⁻¹) | train-mean baseline | 490.170 | -11.760 | 0.000 | n/a | 0.455 | 3/12 | 1/12 |

### Key findings

- Spearman ρ comparison: log_ridge (0.7062937063) vs raw_ridge (0.6503496503) — rank invariance: violated
- RMSE_log_residual: log_ridge 0.199 vs raw_ridge 0.269
- within_2x: log_ridge 9/12 vs raw_ridge 9/12
- Ridge beats baseline (R²_gen > 0): log space yes, raw space yes

## Interpretation

The log-target and raw-target Ridge fits do not preserve identical ranks after refitting: Spearman ρ changes from 0.706 to 0.650. The raw-target fit also has a 1.36× higher fold-change error when both are evaluated in raw J space. The log transformation is therefore retained as the better scale for magnitude calibration, while the positive rank-order transfer signal remains present under the raw target.

## Train means

- log₁₀(J) train mean: `2.8009461420`
- raw J train mean: `792.4000000000` µg cm⁻² h⁻¹

## File hashes

- `outputs/supplementary/Table_3_5_2_with_R2.csv`: `299b9d70d99d5f35162b513fd03f19d25c0ad81e625c6d9aedef2d0267720e8c`
- `outputs/supplementary/note_S2_target_transformation_ablation.json`: `5410b60800a7a7ba348b85eb413c135264d6ae62fc005989c141035c6f44552c`
- `outputs/supplementary/note_S2_target_transformation_predictions.csv`: `7008ded657738afe481e529ae78b05bf7ec37a0e75f51c78328a7370acc2a1c2`
- `outputs/phase1_step2_redo/dataset.csv`: `f6434cd1a02995ff85cc0978ec971971a140b7a2897985ecad8c6fadbd74b528`

The report file itself is covered by the deterministic rerun check rather than embedded as a self-referential hash.
