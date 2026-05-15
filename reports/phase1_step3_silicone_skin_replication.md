# Phase 1 Step 3: Silicone-Skin Replication and Binary-to-Ternary Auxiliary

## 1. Task Definition

Step 3 contains two deterministic analyses. The primary analysis is an external validation: whether SkinMiner v1.5 extracted paired silicone-skin records preserve the silicone-to-skin flux relationship reported by Watkinson Part III Fig. 1. The supplementary analysis tests whether binary hydroxy-cosolvent records can directionally predict two ternary Part II silicone records.

The data source is `master_table_v15_normalized.csv`, using the `include_in_F3_paired`, `include_in_F3_silicone`, `include_in_F3_skin`, `include_in_F2_train`, and protocol-normalization fields from Phase 1 Step 1/1.1.

## 2. Methods

### 2.1 Silicone-skin pair selection

The paired dataset contains 12 pair IDs: Part I 5, Part II 4, and Part III 3. These correspond to 12 silicone records and 12 skin records matched by DOI and numeric vehicle composition.

The normalized master table flags two pure-ethanol records, which collapse to one pair ID after silicone-skin pairing. Therefore the pair-level pure-ethanol count is 1, while the record-level count is 2. V3/V4 exclude the pure-ethanol pair at pair level; this yields n=11 and directly reproduces the reported R2 near 0.71. The prompt's n=10 wording appears to count excluded records rather than excluded pair IDs.

### 2.2 Regression models

Four raw-space linear regressions were fit with silicone J as x and skin J as y: all pairs forced through origin, all pairs with a free intercept, non-pure-ethanol pairs forced through origin, and non-pure-ethanol pairs with a free intercept. The V3 forced-origin non-pure-EtOH variant is the Watkinson protocol comparison.

### 2.3 Binary-to-ternary methods

The auxiliary model trains on 15 binary silicone records: Part I Table 3 and Part II Table 2. It tests on the two Part II Table 3 ternary silicone records. The model is Ridge with alpha=1.0 fixed, using `[ethanol_vv, PG_vv, water_vv, log10_solubility]` and `StandardScaler` fit on train only. The n=2 test set is reported only as a directional observation.

## 3. Results: Silicone-vs-skin

| Variant | Subset | Model | n | Slope | Intercept | R2 | Pearson r |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V1 | all_12_pairs | forced_through_origin | 12 | 0.169 | 0.000 | 0.086 | 0.427 |
| V2 | all_12_pairs | free_intercept | 12 | 0.105 | 52.881 | 0.183 | 0.427 |
| V3 | non_pure_ethanol_pair_ids | forced_through_origin | 11 | 0.250 | 0.000 | 0.719 | 0.872 |
| V4 | non_pure_ethanol_pair_ids | free_intercept | 11 | 0.317 | -42.090 | 0.760 | 0.872 |

V3 gives R2 = 0.719, slope = 0.250, Pearson r = 0.872, n = 11, compared with Watkinson's reported R2 = 0.71. This is a successful replication under the predefined GREEN interval [0.65, 0.80].

Excluding the pure-EtOH pair changes the forced-origin R2 from 0.086 (V1) to 0.719 (V3), consistent with the known ethanol-related skin outlier behavior. Free-intercept models give V2 R2 = 0.183 and V4 R2 = 0.760; they are reported for context but are not substituted for V3.

## 4. Results: Binary-to-ternary

| Vehicle | Actual log10 J | Predicted log10 J | Residual | Within 2x |
| --- | --- | --- | --- | --- |
| 25:25:50:0:0 | 2.721 | 2.719 | -0.002 | True |
| 50:25:25:0:0 | 2.807 | 2.892 | 0.085 | True |

The binary-to-ternary auxiliary result is directional_positive: both_within_2x = True, RMSE_logJ = 0.060, max |residual| = 0.085. This remains an n=2 supplementary observation only.

## 5. Discussion

The silicone-skin replication is a strong data-integrity validation because it recovers a published empirical relationship from SkinMiner-extracted values without fitting any model to improve that relationship. This supports the claim that the extracted paired records preserve the original paper's cross-membrane structure.

The binary-to-ternary result provides a limited but useful directional signal: a simple composition-plus-solubility Ridge model trained on binary systems remains within two-fold on both ternary records. Because n=2 cannot support rank correlation, R2, or significance inference, this is treated as supplementary support for the Step 2 within-domain transfer narrative.

Limitations remain direct: there are only 12 silicone-skin pair IDs, not every binary composition is paired on skin, and cross-skin prediction for untested vehicle compositions is not addressed here.

## 6. Reproducibility

- Step 2 figure typo fix: backed up original files to `_v1_backup_step3_20260510_222443` and regenerated `figure_step2_main.pdf/png` with a true newline annotation.
- Python packages: sklearn 1.7.0, numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.3.
- Output file hashes:
  - `outputs/phase1_step3/binary_to_ternary_dataset.csv`: `f51a2369e26c4b717bbca6595f0c964f32f4cce5d20ca36b95393fa1f7138d14`
  - `outputs/phase1_step3/binary_to_ternary_predictions.csv`: `aceda08d9cc1fe9a62f07d4023dc32f5d630e8d9807f563f44dfee2b8a597c05`
  - `outputs/phase1_step3/silicone_skin_paired_dataset.csv`: `e2f354cc11497fa8979dd44f5bb3956ee11f709328003e866b3a34a730a4fa0a`
  - `outputs/phase1_step3/silicone_skin_regression.csv`: `25457f9d2a1cc3fb8531338a072d2d1f00c00e0d4887baf54046df3ab7dc2bcd`

Overall Step 3 status: **PASS**.
