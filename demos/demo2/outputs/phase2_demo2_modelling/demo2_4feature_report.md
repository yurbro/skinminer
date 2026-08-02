# Demo 2 Step 2g: 4-Feature Bridge Control

## Setup

This control keeps the existing Yalkowsky `log10_vehicle_solubility` feature and adds independent PG and water fractions to remove ethanol's privileged status. The 4-feature bridge is `log10_vehicle_solubility`, `ethanol_fraction`, `pg_fraction`, and `water_fraction`. All model settings match the 2-feature run.

## Feature Sanity

| Dataset | Feature | min | max | mean | non-zero variance? |
|---|---|---:|---:|---:|---|
| Xiao | pg_fraction | 0.100 | 0.200 | 0.150 | yes |
| Xiao | water_fraction | 0.250 | 0.450 | 0.342 | yes |
| Bolla | pg_fraction | 0.000 | 0.150 | 0.056 | yes |
| Bolla | water_fraction | 0.000 | 0.654 | 0.487 | yes |

Both added features have non-zero variance in both datasets.

### Bolla PG/Water Per Record

| record_id | pg_fraction | water_fraction |
|---|---:|---:|
| F1A | 0.150000 | 0.479000 |
| F1B | 0.150000 | 0.529000 |
| F2A | 0.000000 | 0.644000 |
| F2B | 0.000000 | 0.654000 |
| F3 | 0.000000 | 0.450000 |
| F4 | 0.000000 | 0.514000 |
| F5 | 0.000000 | 0.630000 |
| F6 | 0.150000 | 0.000000 |

## Sanity Check: 2-Feature Ridge/log10 Reproduction

- Xiao->Bolla 2-feature Ridge/log10: R2_conv=-0.413, Spearman=-0.548, within-2x=3/8.
- Bolla->Xiao 2-feature Ridge/log10: R2_conv=-2.363, Spearman=-0.235, within-2x=29/29.
Sanity status: PASS.

## Table A: Primary Ridge/log10 Head-to-Head

| Direction | Feature set | R2_conv | RMSE_logJ | Spearman rho | within-2x |
|---|---|---:|---:|---:|---:|
| Xiao->Bolla | 2-feature (main line) | -0.413 | 0.473 | -0.548 | 3/8 |
| Xiao->Bolla | 4-feature (this run) | -0.320 | 0.457 | 0.429 | 3/8 |
| Bolla->Xiao | 2-feature (main line) | -2.363 | 0.110 | -0.235 | 29/29 |
| Bolla->Xiao | 4-feature (this run) | -15.988 | 0.247 | 0.068 | 24/29 |

## Table B: Solubilised Bolla Records Under Xiao->Bolla Ridge/log10

| Bolla record | logJ_actual | 2-feature pred | 4-feature pred | delta 4-2 |
|---|---:|---:|---:|---:|
| F2A | 0.872 | 1.095 | 1.117 | 0.022316 |
| F2B | 0.560 | 1.095 | 1.114 | 0.019411 |
| F6 | 1.571 | 1.000 | 1.114 | 0.114613 |

## Table C: Full 4-Feature Model x Target Grid

| Direction | Model | Target | R2_conv | RMSE (own space) | Spearman rho | Pearson r | within-2x | non-physical | mean sigma (GPR) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| xiao_to_bolla | ridge | log10 | -0.320 | 0.457 | 0.429 | 0.346 | 3/8 | 0 |  |
| xiao_to_bolla | ridge | raw | 0.066 | 11.069 | 0.595 | 0.405 | 3/8 | 0 |  |
| xiao_to_bolla | gpr | log10 | -0.228 | 0.441 | NA | NA | 4/8 | 0 | 0.061 |
| xiao_to_bolla | gpr | raw | -0.000 | 11.455 | NA | NA | 3/8 | 0 | 1.527 |
| bolla_to_xiao | ridge | log10 | -15.988 | 0.247 | 0.068 | 0.056 | 24/29 | 0 |  |
| bolla_to_xiao | ridge | raw | -6.553 | 4.127 | -0.023 | 0.012 | 28/29 | 0 |  |
| bolla_to_xiao | gpr | log10 | -10.063 | 0.199 | -0.192 | 0.008 | 28/29 | 0 | 0.411 |
| bolla_to_xiao | gpr | raw | -10.570 | 5.108 | -0.116 | -0.072 | 25/29 | 0 | 9.641 |

## Interpretation

1. Does adding PG and water fractions change the negative-transfer conclusion?

Partially. The primary Ridge/log10 cells remain negative in both directions, but the stronger all-model/all-target negative-sign claim is not invariant: xiao_to_bolla ridge/raw R2_conv=0.066, rho=0.595, within=3/8.

2. Do F2A/F2B/F6 predictions separate under 4-feature?

F2A and F2B separate by 0.002820 log10 units under 4-feature Ridge/log10. The maximum absolute movement among F2A/F2B/F6 relative to 2-feature is 0.114613 log10 units.

3. Does the 2-feature bridge over-collapse the chemistry?

Yes, at least for per-record interpretation: PG and water expose formulation differences hidden by the 2-feature bridge. However, the aggregate transfer metrics remain poor, so the additional chemistry does not overcome the protocol-distance mismatch.

4. Recommendation

Use the 4-feature bridge as an important interpretability/sensitivity control because it treats ethanol, PG, and water symmetrically as shared composition axes and exposes hidden per-record chemistry. Keep the primary conclusion anchored to the log10-target transfer results: those remain negative under both 2-feature and 4-feature bridges. Do not claim that every secondary target/model cell remains negative, because 4-feature Xiao->Bolla Ridge/raw is positive.

## Output Files

- `transfer_4feature_xiao_to_bolla.csv`
- `transfer_4feature_bolla_to_xiao.csv`
- `transfer_4feature_results.json`
- `demo2_4feature_report.md`
