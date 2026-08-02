# Demo 2 Step 2m: Sample-Size-Matched Literature-Value Comparison

## 1. Setup and Sanity Checks

The comparison uses the unchanged 4-feature bridge (`log10_vehicle_solubility`, `ethanol_fraction`, `pg_fraction`, `water_fraction`), log10(J), StandardScaler fitted on training rows only, and Ridge(alpha=1.0). At each m, configuration A trains on m in-house records and configuration B trains on all 8 literature records plus m-8 in-house records. Both evaluate only on held-out in-house records.

The prompt's phrase `BBD F4/F5/F6` maps to the actual record IDs BBD4/BBD5/BBD6. These three identical center-point compositions were always included together or excluded together. Leakage guard: PASS.

Subset records retained for audit: 1026 for configuration A and 1001 for configuration B.

**Pure A, m=28 sanity diagnostic.** There are only 26 valid unique 28-of-29 training sets under the indivisible-center rule. Every valid split leaves one non-center record for testing, so per-subset R2_conv and rank correlations are mathematically undefined. Pooling the 26 unique held-out predictions gives R2_conv=-0.218 and Spearman rho=-0.044. This is within the requested -0.40 to -0.10 range and differs from the all-29 grouped-LOOCV R2_conv by 0.008. It is a diagnostic, not a subset mean.

**Mixed B, m=20 sanity check.** The 8-literature + 12-in-house cell exactly reuses the Step 2h k=12 subset sequence: True. Its R2_conv is -3.557 +/- 1.904; maximum difference from the prior summary is 3.809e-13. Status: PASS.

Configuration A and B have matched total training sizes but different held-out in-house test sizes. R2_conv is normalized within each test set, but the differing test composition remains a caveat. No best-case subsets are reported.

## 2. Configuration A: Pure In-House

| m | n_subsets | R2_conv mean +/- std | RMSE_logJ mean +/- std | Spearman rho mean +/- std | within-2x mean +/- std |
|---:|---:|---:|---:|---:|---:|
| 8 | 200 | -1.266 +/- 4.452 | 0.080 +/- 0.034 | -0.007 +/- 0.196 | 0.995 +/- 0.041 |
| 12 | 200 | -0.621 +/- 0.794 | 0.072 +/- 0.011 | 0.008 +/- 0.226 | 1.000 +/- 0.000 |
| 16 | 200 | -0.489 +/- 0.576 | 0.069 +/- 0.010 | 0.023 +/- 0.259 | 1.000 +/- 0.000 |
| 20 | 200 | -0.445 +/- 0.571 | 0.069 +/- 0.012 | 0.062 +/- 0.320 | 1.000 +/- 0.000 |
| 24 | 200 | -0.651 +/- 0.845 | 0.064 +/- 0.019 | 0.072 +/- 0.500 | 1.000 +/- 0.000 |
| 28 | 26 | undefined per subset; pooled diagnostic -0.218 | 0.053 +/- 0.044 | undefined per subset; pooled diagnostic -0.044 | 1.000 +/- 0.000 |

Subset-count audit:

| m | total valid | used | skipped by 200 cap |
|---:|---:|---:|---:|
| 8 | 1628055 | 200 | 1627855 |
| 12 | 12782250 | 200 | 12782050 |
| 16 | 15712335 | 200 | 15712135 |
| 20 | 3354780 | 200 | 3354580 |
| 24 | 66105 | 200 | 65905 |
| 28 | 26 | 26 | 0 |

## 3. Configuration B: Mixed Literature and In-House

| m | n_subsets | R2_conv mean +/- std | RMSE_logJ mean +/- std | Spearman rho mean +/- std | within-2x mean +/- std |
|---:|---:|---:|---:|---:|---:|
| 8 | 1 | -15.988 +/- 0.000 | 0.247 +/- 0.000 | 0.068 +/- 0.000 | 0.828 +/- 0.000 |
| 12 | 200 | -4.984 +/- 2.354 | 0.142 +/- 0.024 | 0.002 +/- 0.082 | 0.969 +/- 0.052 |
| 16 | 200 | -4.038 +/- 2.023 | 0.128 +/- 0.019 | -0.019 +/- 0.128 | 0.992 +/- 0.025 |
| 20 | 200 | -3.557 +/- 1.904 | 0.121 +/- 0.019 | -0.019 +/- 0.179 | 0.998 +/- 0.010 |
| 24 | 200 | -3.485 +/- 2.223 | 0.119 +/- 0.022 | -0.012 +/- 0.239 | 0.999 +/- 0.008 |
| 28 | 200 | -4.134 +/- 3.652 | 0.119 +/- 0.022 | 0.011 +/- 0.275 | 1.000 +/- 0.000 |

Subset-count audit:

| m | in-house anchors | total valid | used | skipped by 200 cap |
|---:|---:|---:|---:|---:|
| 8 | 0 | 1 | 1 | 0 |
| 12 | 4 | 14976 | 200 | 14776 |
| 16 | 8 | 1628055 | 200 | 1627855 |
| 20 | 12 | 12782250 | 200 | 12782050 |
| 24 | 16 | 15712335 | 200 | 15712135 |
| 28 | 20 | 3354780 | 200 | 3354580 |

## 4. Direct Head-to-Head Comparison

| m | Pure A R2_conv | Mixed B R2_conv | Pure A rho | Mixed B rho | R2 head-to-head |
|---:|---:|---:|---:|---:|---|
| 8 | -1.266 +/- 4.452 | -15.988 +/- 0.000 | -0.007 +/- 0.196 | 0.068 +/- 0.000 | A higher; 1-SD bars separated |
| 12 | -0.621 +/- 0.794 | -4.984 +/- 2.354 | 0.008 +/- 0.226 | 0.002 +/- 0.082 | A higher; 1-SD bars separated |
| 16 | -0.489 +/- 0.576 | -4.038 +/- 2.023 | 0.023 +/- 0.259 | -0.019 +/- 0.128 | A higher; 1-SD bars separated |
| 20 | -0.445 +/- 0.571 | -3.557 +/- 1.904 | 0.062 +/- 0.320 | -0.019 +/- 0.179 | A higher; 1-SD bars separated |
| 24 | -0.651 +/- 0.845 | -3.485 +/- 2.223 | 0.072 +/- 0.500 | -0.012 +/- 0.239 | A higher; 1-SD bars overlap |
| 28 | -0.218 (pooled) | -4.134 +/- 3.652 | -0.044 (pooled) | 0.011 +/- 0.275 | A pooled diagnostic > B mean |

The `m=28` pure point is shown as a pooled diagnostic rather than a mean +/- std and is excluded from formal error-bar separation claims.

## 5. Interpretation

Across the formally comparable m values with defined per-subset R2_conv (m=8, 12, 16, 20, 24), pure in-house has the higher mean at m=8, 12, 16, 20, 24. Mixed training has an equal or higher mean at no formally comparable m value.

Using non-overlap of mean +/- 1 SD intervals as the requested descriptive separation criterion, pure in-house is separated from mixed at m=8, 12, 16, 20. This is descriptive rather than a formal paired significance test because the two configurations use different test sets.

At m=28, the pure pooled diagnostic R2_conv is -0.218, compared with mixed mean -4.134; this supports the same direction but is not included in the mean +/- std comparison.

R2_conv is the primary result. Spearman rho is retained as a secondary ordering diagnostic; near-zero or crossing rank correlations do not override a consistently worse mixed-training R2_conv.

**Bottom line.** For this Xiao-Bolla pair under the fixed 4-feature Ridge protocol, the sample-size-matched comparison supports negative literature augmentation value for predicting in-house flux: pure in-house training has higher mean R2_conv at every formally comparable matched size.

This conclusion is bounded to this specific Xiao-Bolla dataset pair, target, feature bridge, and Ridge model. It does not imply that literature data is generally useless or harmful.

## Outputs

- `sample_matched_pure_inhouse_results.json`
- `sample_matched_mixed_results.json`
- `sample_matched_summary.csv`
- `figure_sample_matched_comparison.pdf`
- `figure_sample_matched_comparison.png`
- `run_demo2_sample_matched.py`
