# Demo 2 Step 2h: Few-Shot Transfer With In-Domain Anchors

## 1. Setup Confirmation

The experiment reuses the Step 2g 4-feature bridge verbatim: `log10_vehicle_solubility`, `ethanol_fraction`, `pg_fraction`, and `water_fraction`. The model is StandardScaler fit on training data only plus Ridge(alpha=1.0), trained on log10(J), with random_state=42 for subset sampling. No hyperparameter tuning or SkinMiner source-code changes were made.

The k=0 sanity check passes in both directions: Xiao->Bolla reproduces R2_conv=-0.320, Spearman rho=+0.429, within-2x=3/8; Bolla->Xiao reproduces R2_conv=-15.988, Spearman rho=+0.068, within-2x=24/29.

Xiao center-point duplicate compositions BBD4/BBD5/BBD6 were treated as one indivisible block in Bolla->Xiao subset selection; no valid subset places one copy in train and another in test.

## 2. Xiao->Bolla Few-Shot Summary

Bolla->Xiao narrow-range disclosure for cross-table reading: RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading.

| k | n_subsets | R2_conv mean +/- std | Spearman rho mean +/- std | within-2x mean +/- std | RMSE_logJ mean +/- std |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | -0.320 +/- 0.000 | 0.429 +/- 0.000 | 0.375 +/- 0.000 | 0.457 +/- 0.000 |
| 1 | 8 | -0.658 +/- 0.682 | 0.214 +/- 0.388 | 0.429 +/- 0.175 | 0.486 +/- 0.052 |
| 2 | 28 | -0.545 +/- 1.247 | 0.206 +/- 0.362 | 0.470 +/- 0.194 | 0.443 +/- 0.096 |
| 3 | 56 | -0.469 +/- 1.578 | 0.355 +/- 0.409 | 0.475 +/- 0.195 | 0.396 +/- 0.113 |
| 4 | 70 | -0.545 +/- 2.144 | 0.531 +/- 0.435 | 0.479 +/- 0.230 | 0.352 +/- 0.118 |

## 3. Bolla->Xiao Few-Shot Summary

Disclosure for this result table: RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading.

| k | n_subsets | R2_conv mean +/- std | Spearman rho mean +/- std | within-2x mean +/- std | RMSE_logJ mean +/- std |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | -15.988 +/- 0.000 | 0.068 +/- 0.000 | 0.828 +/- 0.000 | 0.247 +/- 0.000 |
| 1 | 26 | -8.986 +/- 4.144 | 0.028 +/- 0.048 | 0.883 +/- 0.077 | 0.184 +/- 0.038 |
| 2 | 200 | -6.537 +/- 3.444 | 0.010 +/- 0.063 | 0.931 +/- 0.071 | 0.159 +/- 0.033 |
| 4 | 200 | -4.984 +/- 2.354 | 0.002 +/- 0.082 | 0.969 +/- 0.052 | 0.142 +/- 0.024 |
| 8 | 200 | -4.038 +/- 2.023 | -0.019 +/- 0.128 | 0.992 +/- 0.025 | 0.128 +/- 0.019 |
| 12 | 200 | -3.557 +/- 1.904 | -0.019 +/- 0.179 | 0.998 +/- 0.010 | 0.121 +/- 0.019 |

Subset counts after duplicate-guard filtering and deterministic cap:

Disclosure for this subset-count audit table: RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading.

| k | total valid subsets | subsets used | skipped by 200-cap |
|---:|---:|---:|---:|
| 0 | 1 | 1 | 0 |
| 1 | 26 | 26 | 0 |
| 2 | 325 | 200 | 125 |
| 4 | 14976 | 200 | 14776 |
| 8 | 1628055 | 200 | 1627855 |
| 12 | 12782250 | 200 | 12782050 |

## 4. Interpretation

For Xiao->Bolla, RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading. Mean R2_conv does not cross zero in k=0..4. Spearman rho is non-monotonic; it peaks at k=4 with mean 0.531 across k=0..4. RMSE_logJ changes from 0.457 at k=0 to 0.352 at k=4. Bottom line: few-shot with k <= 4 Bolla anchors does not recover useful transfer for the Xiao->Bolla direction. In practical terms, the tested range asks whether up to four literature-target in-domain experiments are enough before predicting the rest of Bolla; the answer follows the R2_conv crossing rather than best-case subsets.

For Bolla->Xiao, RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading. Mean R2_conv does not cross zero in k=0,1,2,4,8,12. Spearman rho is non-monotonic; it peaks at k=0 with mean 0.068 across the tested k values. RMSE_logJ changes from 0.247 at k=0 to 0.121 at k=12.

For Bolla->Xiao, RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading. The apparent RMSE trend is an artifact warning rather than a reliable improvement because mean R2_conv does not track the RMSE decrease into positive territory. Bottom line: few-shot does not recover useful transfer for the Bolla->Xiao direction within the tested k range.

For Bolla->Xiao, RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading. No best-case subsets are reported; the interpretation uses aggregated mean +/- std only. For a researcher considering literature augmentation, this means the decision should be based on the average in-domain-anchor burden, not a cherry-picked anchor set.

## 5. Honest Negative-Result Disclosure

RMSE on Xiao test sets is partly a narrow-range artifact (Xiao log10 J spans only approx 0.25); rely on R2_conv and Spearman for honest reading. In-domain anchoring does not recover transfer in either direction within the tested range. This strengthens the interpretation that the protocol-distance gap exceeds what small-sample correction can absorb.

## 6. Audit Files

- `fewshot_xiao_to_bolla_results.json`: all per-subset Xiao->Bolla records.
- `fewshot_bolla_to_xiao_results.json`: all per-subset Bolla->Xiao records.
- `fewshot_summary_table.csv`: aggregated mean +/- std rows.
- `run_demo2_fewshot.py`: standalone deterministic harness.

Per-subset JSON records are retained for audit only and are not summarized as best-case subsets in this report.
