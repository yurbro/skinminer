# Demonstration v6: In-Context Learning for Permeation Prediction

## Supplement Update: GPT-5.4 Added

This supplement appends GPT-5.4 to the existing GPT-4o-mini and Claude Sonnet 4.6 ICL experiment. The previous two-model results were not rerun; their original outputs were backed up with `_2models` suffixes before recomputing the combined summary.

- Added model string: `gpt-5.4`.
- New GPT-5.4 calls completed/logged: 96/96.
- Total calls now completed/logged: 288/288.
- Parse failure calls: 0; failure rate: 0.0%.
- GPT-5.4 estimated cost: $0.8228.
- Total estimated cost including original V6 runs: $1.2869.
- Cost note: estimates use API token usage and configured rates; GPT-5.4 is set to input $15/M tokens and output $60/M tokens.

## Summary Metrics

| model_label | condition_label | R2 | RMSE | MAE | n_valid | n_failed_parse | parse_fail_calls | cost_usd_estimate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-4o-mini | No context | -0.988 | 664.067 | 555.545 | 24 | 0 | 0 | 0.001 |
| GPT-4o-mini | General | 0.500 | 332.934 | 256.936 | 24 | 0 | 0 | 0.001 |
| GPT-4o-mini | ICL | 0.832 | 193.093 | 127.809 | 24 | 0 | 0 | 0.003 |
| GPT-4o-mini | Permuted ICL | 0.729 | 245.214 | 175.663 | 24 | 0 | 0 | 0.003 |
| Claude Sonnet 4.6 | No context | -1.884 | 799.976 | 677.338 | 24 | 0 | 0 | 0.090 |
| Claude Sonnet 4.6 | General | 0.763 | 229.202 | 173.285 | 24 | 0 | 0 | 0.098 |
| Claude Sonnet 4.6 | ICL | 0.651 | 278.309 | 208.663 | 24 | 0 | 0 | 0.134 |
| Claude Sonnet 4.6 | Permuted ICL | 0.607 | 295.461 | 200.294 | 24 | 0 | 0 | 0.134 |
| GPT-5.4 | No context | -1.301 | 714.450 | 583.553 | 24 | 0 | 0 | 0.102 |
| GPT-5.4 | General | 0.586 | 303.051 | 239.245 | 24 | 0 | 0 | 0.137 |
| GPT-5.4 | ICL | 0.718 | 250.075 | 209.637 | 24 | 0 | 0 | 0.292 |
| GPT-5.4 | Permuted ICL | 0.564 | 311.074 | 212.832 | 24 | 0 | 0 | 0.292 |

## GPT-5.4 Condition Summary

| condition_label | R2 | RMSE | MAE | n_valid | parse_fail_calls | cost_usd_estimate |
| --- | --- | --- | --- | --- | --- | --- |
| No context | -1.301 | 714.450 | 583.553 | 24 | 0 | 0.102 |
| General | 0.586 | 303.051 | 239.245 | 24 | 0 | 0.137 |
| ICL | 0.718 | 250.075 | 209.637 | 24 | 0 | 0.292 |
| Permuted ICL | 0.564 | 311.074 | 212.832 | 24 | 0 | 0.292 |

## Permutation Validation

| model_label | test | p_value | icl_mean_fold_mae | permuted_icl_mean_fold_mae | n_folds |
| --- | --- | --- | --- | --- | --- |
| GPT-4o-mini | ICL MAE < permuted ICL MAE | 0.074 | 127.809 | 175.663 | 8 |
| Claude Sonnet 4.6 | ICL MAE < permuted ICL MAE | 0.320 | 208.663 | 200.294 | 8 |
| GPT-5.4 | ICL MAE < permuted ICL MAE | 0.527 | 209.637 | 212.832 | 8 |

The permutation control tests whether LLMs use the structured examples rather than relying only on generic priors. If ICL is not better than permuted ICL, the evidence for true example use is weak.

## Best Condition

Best condition by R2: `GPT-4o-mini` with `ICL`.

- R2: 0.832
- RMSE: 193.1 ug/cm2
- MAE: 127.8 ug/cm2
- V5 GPR baseline R2: 0.600

## Three-Model Interpretation

The three-model comparison separates two claims. First, structured context improves numerical anchoring relative to no-context prompting for all models. Second, the stricter ICL-vs-permuted-ICL diagnostic remains the key test of whether the examples provide formulation-response signal rather than only range information.

## Per-Formulation Breakdown

| model_label | condition | fold | R2 | RMSE | MAE | n_valid |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Sonnet 4.6 | general_context | F1 | 0.780 | 260.455 | 183.265 | 3 |
| Claude Sonnet 4.6 | general_context | F2 | 0.760 | 321.050 | 253.525 | 3 |
| Claude Sonnet 4.6 | general_context | F3 | 0.896 | 129.197 | 75.305 | 3 |
| Claude Sonnet 4.6 | general_context | F4 | 0.964 | 73.025 | 67.555 | 3 |
| Claude Sonnet 4.6 | general_context | F5 | 0.093 | 296.143 | 280.481 | 3 |
| Claude Sonnet 4.6 | general_context | F6 | 0.863 | 156.889 | 129.194 | 3 |
| Claude Sonnet 4.6 | general_context | F7 | -2.375 | 309.410 | 280.058 | 3 |
| Claude Sonnet 4.6 | general_context | F8 | 0.870 | 138.867 | 116.899 | 3 |
| Claude Sonnet 4.6 | icl | F1 | 0.938 | 137.948 | 115.781 | 3 |
| Claude Sonnet 4.6 | icl | F2 | 0.893 | 214.905 | 192.778 | 3 |
| Claude Sonnet 4.6 | icl | F3 | 0.719 | 212.626 | 143.392 | 3 |
| Claude Sonnet 4.6 | icl | F4 | 0.851 | 148.700 | 122.566 | 3 |
| Claude Sonnet 4.6 | icl | F5 | -1.436 | 485.256 | 464.615 | 3 |
| Claude Sonnet 4.6 | icl | F6 | 0.931 | 111.355 | 92.528 | 3 |
| Claude Sonnet 4.6 | icl | F7 | -7.166 | 481.321 | 459.635 | 3 |
| Claude Sonnet 4.6 | icl | F8 | 0.949 | 87.013 | 78.010 | 3 |
| Claude Sonnet 4.6 | no_context | F1 | -2.066 | 972.496 | 836.835 | 3 |
| Claude Sonnet 4.6 | no_context | F2 | -1.324 | 999.677 | 804.596 | 3 |
| Claude Sonnet 4.6 | no_context | F3 | -2.776 | 779.361 | 682.149 | 3 |
| Claude Sonnet 4.6 | no_context | F4 | -2.563 | 726.266 | 628.390 | 3 |
| Claude Sonnet 4.6 | no_context | F5 | -6.472 | 849.938 | 798.287 | 3 |
| Claude Sonnet 4.6 | no_context | F6 | -2.715 | 817.068 | 713.644 | 3 |
| Claude Sonnet 4.6 | no_context | F7 | -3.560 | 359.656 | 330.265 | 3 |
| Claude Sonnet 4.6 | no_context | F8 | -2.515 | 721.369 | 624.542 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F1 | 0.717 | 295.638 | 258.635 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F2 | 0.619 | 404.843 | 307.222 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F3 | 0.840 | 160.669 | 151.455 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F4 | 0.978 | 57.041 | 54.899 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F5 | 0.801 | 138.605 | 100.524 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F6 | 0.808 | 185.565 | 165.750 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F7 | -11.698 | 600.184 | 507.747 | 3 |
| Claude Sonnet 4.6 | permuted_icl | F8 | 0.972 | 64.350 | 56.122 | 3 |
| GPT-4o-mini | general_context | F1 | 0.935 | 141.924 | 115.226 | 3 |
| GPT-4o-mini | general_context | F2 | 0.881 | 226.286 | 197.292 | 3 |
| GPT-4o-mini | general_context | F3 | 0.778 | 188.874 | 147.760 | 3 |
| GPT-4o-mini | general_context | F4 | -0.064 | 396.860 | 373.177 | 3 |
| GPT-4o-mini | general_context | F5 | 0.654 | 183.025 | 162.135 | 3 |
| GPT-4o-mini | general_context | F6 | 0.880 | 146.872 | 122.083 | 3 |
| GPT-4o-mini | general_context | F7 | -10.342 | 567.247 | 464.635 | 3 |
| GPT-4o-mini | general_context | F8 | -0.658 | 495.382 | 473.177 | 3 |
| GPT-4o-mini | icl | F1 | 0.824 | 232.752 | 206.670 | 3 |
| GPT-4o-mini | icl | F2 | 0.957 | 136.663 | 112.333 | 3 |
| GPT-4o-mini | icl | F3 | 0.988 | 44.534 | 33.281 | 3 |
| GPT-4o-mini | icl | F4 | 0.875 | 135.952 | 93.510 | 3 |
| GPT-4o-mini | icl | F5 | 0.248 | 269.573 | 268.059 | 3 |
| GPT-4o-mini | icl | F6 | 0.998 | 17.298 | 16.639 | 3 |
| GPT-4o-mini | icl | F7 | -3.653 | 363.310 | 291.635 | 3 |
| GPT-4o-mini | icl | F8 | 1.000 | 0.361 | 0.344 | 3 |
| GPT-4o-mini | no_context | F1 | -1.347 | 850.802 | 729.635 | 3 |
| GPT-4o-mini | no_context | F2 | -0.794 | 878.337 | 697.396 | 3 |
| GPT-4o-mini | no_context | F3 | -0.760 | 532.101 | 451.719 | 3 |
| GPT-4o-mini | no_context | F4 | -1.983 | 664.578 | 573.412 | 3 |
| GPT-4o-mini | no_context | F5 | -3.916 | 689.386 | 651.526 | 3 |
| GPT-4o-mini | no_context | F6 | -1.482 | 667.819 | 575.328 | 3 |
| GPT-4o-mini | no_context | F7 | -4.735 | 403.365 | 371.853 | 3 |
| GPT-4o-mini | no_context | F8 | -0.512 | 473.079 | 393.490 | 3 |
| GPT-4o-mini | permuted_icl | F1 | 0.786 | 256.822 | 208.302 | 3 |
| GPT-4o-mini | permuted_icl | F2 | 0.834 | 267.547 | 191.556 | 3 |
| GPT-4o-mini | permuted_icl | F3 | 0.895 | 129.789 | 113.983 | 3 |
| GPT-4o-mini | permuted_icl | F4 | 0.909 | 115.861 | 95.566 | 3 |
| GPT-4o-mini | permuted_icl | F5 | 0.694 | 172.046 | 147.281 | 3 |
| GPT-4o-mini | permuted_icl | F6 | 0.775 | 201.272 | 172.639 | 3 |
| GPT-4o-mini | permuted_icl | F7 | -7.187 | 481.922 | 377.635 | 3 |
| GPT-4o-mini | permuted_icl | F8 | 0.927 | 104.278 | 98.344 | 3 |
| GPT-5.4 | general_context | F1 | 0.777 | 261.998 | 249.253 | 3 |
| GPT-5.4 | general_context | F2 | 0.747 | 330.086 | 306.181 | 3 |
| GPT-5.4 | general_context | F3 | -0.244 | 447.376 | 373.385 | 3 |
| GPT-5.4 | general_context | F4 | 0.914 | 112.813 | 107.899 | 3 |
| GPT-5.4 | general_context | F5 | -1.768 | 517.348 | 493.281 | 3 |
| GPT-5.4 | general_context | F6 | 0.730 | 220.240 | 194.861 | 3 |
| GPT-5.4 | general_context | F7 | 0.961 | 33.373 | 29.253 | 3 |
| GPT-5.4 | general_context | F8 | 0.818 | 164.250 | 159.844 | 3 |
| GPT-5.4 | icl | F1 | 0.846 | 218.290 | 204.892 | 3 |
| GPT-5.4 | icl | F2 | 0.854 | 250.623 | 192.847 | 3 |
| GPT-5.4 | icl | F3 | 0.667 | 231.359 | 199.392 | 3 |
| GPT-5.4 | icl | F4 | 0.848 | 149.997 | 120.955 | 3 |
| GPT-5.4 | icl | F5 | -0.031 | 315.774 | 313.281 | 3 |
| GPT-5.4 | icl | F6 | 0.888 | 141.876 | 133.750 | 3 |
| GPT-5.4 | icl | F7 | -5.197 | 419.272 | 379.635 | 3 |
| GPT-5.4 | icl | F8 | 0.877 | 134.838 | 132.344 | 3 |
| GPT-5.4 | no_context | F1 | -1.974 | 957.755 | 823.347 | 3 |
| GPT-5.4 | no_context | F2 | -1.316 | 997.912 | 801.885 | 3 |
| GPT-5.4 | no_context | F3 | -1.658 | 653.922 | 557.497 | 3 |
| GPT-5.4 | no_context | F4 | -1.375 | 592.984 | 497.156 | 3 |
| GPT-5.4 | no_context | F5 | -4.223 | 710.602 | 665.281 | 3 |
| GPT-5.4 | no_context | F6 | -1.609 | 684.687 | 583.728 | 3 |
| GPT-5.4 | no_context | F7 | -1.683 | 275.863 | 249.476 | 3 |
| GPT-5.4 | no_context | F8 | -1.305 | 584.203 | 490.056 | 3 |
| GPT-5.4 | permuted_icl | F1 | 0.847 | 217.547 | 178.559 | 3 |
| GPT-5.4 | permuted_icl | F2 | 0.684 | 368.672 | 277.778 | 3 |
| GPT-5.4 | permuted_icl | F3 | 0.663 | 232.705 | 192.830 | 3 |
| GPT-5.4 | permuted_icl | F4 | 0.934 | 98.937 | 98.733 | 3 |
| GPT-5.4 | permuted_icl | F5 | 0.767 | 150.102 | 126.802 | 3 |
| GPT-5.4 | permuted_icl | F6 | 0.720 | 224.186 | 186.528 | 3 |
| GPT-5.4 | permuted_icl | F7 | -14.802 | 669.538 | 570.191 | 3 |
| GPT-5.4 | permuted_icl | F8 | 0.960 | 76.656 | 71.233 | 3 |

## Honest Judgment

This remains a small, single-paper ICL experiment, not RAG. GPT-5.4 broadens the model comparison to a stronger OpenAI model, but the interpretation depends on the permutation control. If GPT-5.4 ICL does not clearly beat permuted ICL, the honest conclusion is that the records are useful for range anchoring but do not yet prove reliable example-based formulation-response learning. If it does beat permuted ICL, the claim can be strengthened for capable models, while still limiting the scope to a constrained single-paper setting.
