# Demonstration v6: In-Context Learning for Permeation Prediction

## Experiment Summary

This experiment evaluates whether SkinMiner-extracted structured records can serve as in-context examples for numerical LLM prediction. This is in-context learning (ICL), not retrieval-augmented generation (RAG). A true RAG system over the full SkinMiner corpus remains future work.

- Data: 8 formulations x 3 timepoints from `10.1208/s12249-013-9995-4`.
- Cross-validation: leave-one-formulation-out.
- Models: GPT-4o-mini and Claude Sonnet 4.6.
- Conditions: no context, general context, ICL, and permuted ICL.
- Repeats: 3 per model x condition x fold.
- Planned calls completed/logged: 192/192.
- Parse failure calls: 0; failure rate: 0.0%.
- Estimated total cost: $0.4641 using configured per-token prices.

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

## Permutation Validation

| model_label | test | p_value | icl_mean_fold_mae | permuted_icl_mean_fold_mae | n_folds |
| --- | --- | --- | --- | --- | --- |
| GPT-4o-mini | ICL MAE < permuted ICL MAE | 0.074 | 127.809 | 175.663 | 8 |
| Claude Sonnet 4.6 | ICL MAE < permuted ICL MAE | 0.320 | 208.663 | 200.294 | 8 |

The permutation control tests whether LLMs use the structured examples rather than relying only on generic priors. If ICL is not better than permuted ICL, the evidence for true example use is weak.

## Best Condition

Best condition by R2: `GPT-4o-mini` with `ICL`.

- R2: 0.832
- RMSE: 193.1 µg/cm²
- MAE: 127.8 µg/cm²
- V5 GPR baseline R2: 0.600

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

## Failure Analysis

Parse failures are counted at the LLM-call level and at the 24-point evaluation level. Raw responses are saved under `raw_responses/` for audit. Numerical predictions outside plausible monotonic permeation trends were not post-corrected; this is intentional to evaluate raw ICL behaviour.

## Honest Judgment

This is a small, single-paper ICL experiment. It does not prove that LLMs have learned formulation science, and it should not be described as RAG. The key diagnostic is ICL versus permuted ICL. If the best ICL condition does not clearly exceed permuted ICL for the same model, the structured examples did not provide strong usable signal. If it does, the result supports a narrower claim: SkinMiner records can be used as structured demonstrations that improve LLM numerical predictions in a constrained, single-paper setting.
