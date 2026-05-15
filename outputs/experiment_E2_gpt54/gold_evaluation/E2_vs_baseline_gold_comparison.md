# E2 vs Baseline Gold Comparison

| Metric | Baseline | E2 | Delta |
|---|---:|---:|---:|
| precision | 1.000 | 1.000 | +0.000 |
| recall | 0.500 | 0.500 | +0.000 |
| f1 | 0.667 | 0.667 | +0.000 |
| scope_precision | 1.000 | 1.000 | +0.000 |
| end_to_end_precision | 0.000 | 0.000 | +0.000 |
| verified_count | 7 | 7 | +0 |
| value_correct_yes_or_approx | 0 | 0 | +0 |

## Interpretation

1. Gold-set metrics are unchanged relative to the post-Fix-5 baseline: precision 1.000, recall 0.500, F1 0.667, and end-to-end precision 0.000.
2. The 71-row audit set still credits only figure-route verified rows; E2 does not create any non-figure gold positives.
3. Stronger models reduce workload volume and some failure bucket counts, but they do not convert into additional audited keeps or better endpoint correctness.