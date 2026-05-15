# Cold-Start Validation: Literature Prior for EDMA

## Data Summary
- Total ibuprofen records: `30`
- Papers: `3`
- Time points covered: `6 h, 12 h, 24 h, 48 h, 72 h`
- Endpoint value range: `168` to `2.39e+03` ug/cm2

## Prior Distribution
- Overall P10/P25/P50/P75/P90: `207` / `369` / `666` / `1.09e+03` / `1.31e+03` ug/cm2

| endpoint_time_h | n_records | mean | std | min | p25 | p50 | p75 | p90 | max |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 | 5 | 354 | 109 | 168 | 369 | 369 | 432 | 432 | 432 |
| 12 | 1 | 2.39e+03 | 0 | 2.39e+03 | 2.39e+03 | 2.39e+03 | 2.39e+03 | 2.39e+03 | 2.39e+03 |
| 24 | 8 | 282 | 121 | 194 | 207 | 226 | 299 | 472 | 488 |
| 48 | 8 | 770 | 160 | 406 | 726 | 843 | 852 | 875 | 907 |
| 72 | 8 | 1.28e+03 | 391 | 606 | 1.15e+03 | 1.22e+03 | 1.39e+03 | 1.8e+03 | 1.84e+03 |

## Leave-One-Paper-Out Results

| Held-out paper | n | True ybest | Prior P75 | Relative error | In P25-P75 range? |
|---|---:|---:|---:|---:|---|
| 10.1016/j.ejpb.2020.05.013 | 1 | 2.39e+03 | 907 | 62.0% | no |
| 10.1186/2050-6511-13-5 | 5 | 432 | 1.15e+03 | 165.9% | yes |
| 10.1208/s12249-013-9995-4 | 24 | 1.84e+03 | 432 | 76.6% | no |

## Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| Range coverage (P25-P75) | 33.3% | Share of held-out papers whose true ybest falls inside the literature-prior interquartile range. |
| Mean relative error of P75 | 101.5% | Error when prior P75 is used as the initial ybest estimate. |
| Estimated experiments saved | 5-10 | The prior substitutes for the initial empirical observations normally needed to estimate a response distribution before EDMA starts. |

## Threshold Transferability

Formal PoE cannot be reconstructed from extracted endpoint records alone because no posterior uncertainty is available. As a deterministic proxy, the analysis asks whether final-time formulations exceed the leave-one-paper-out prior P75, and whether they exceed it by at least 20%.

| DOI | final time (h) | n final formulations | prior P75 | final ybest | share > prior P75 | share > 1.2 x prior P75 |
|---|---:|---:|---:|---:|---:|---:|
| 10.1208/s12249-013-9995-4 | 72 | 8 | 432 | 1.84e+03 | 100.0% | 100.0% |

## Conclusion

The literature prior is useful as a weak cold-start response-scale prior, not as a reliable quantitative ybest estimator. The leave-one-paper-out results show substantial cross-study heterogeneity, so the practical value is to set an initial response scale and benchmark expectations before EDMA starts, while still requiring early system-specific observations.
