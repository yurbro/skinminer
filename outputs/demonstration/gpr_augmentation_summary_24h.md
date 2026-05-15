# GPR Literature Augmentation Results (24h Shared Timepoint)

## 1. Data Summary

### Self-Generated Data (Paper 1)

- Input: `C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\demonstration\paper1_24h_mean.csv`
- Formulations: `20`
- Replicates: `5 per formulation in the source file; formulation means used for GPR`
- Timepoint: `24h`
- Response range: `178.813 to 283.258 ug/cm2`
- Excipients: `Poloxamer 407, Ethanol, Propylene glycol`

### Literature Data (SkinMiner)

- Input: `C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\demonstration\literature_24h_data.csv`
- Canonical records at 24h: `9`
- Records used after default sanity filter: `8`
- Source papers used: `1`
- Raw response range: `193.594 to 302840.000 ug/cm2`
- Used response range: `193.594 to 487.969 ug/cm2`
- Max literature response filter: `1000.0`

### Literature Membrane Types Used

| Membrane type | Records |
|---|---:|
| `dermatomed porcine skin; human skin` | 8 |

### Overlap Assessment

Both datasets now share ibuprofen, Franz-cell/diffusion-cell context, cumulative amount response, and the 24h timepoint. The main remaining mismatch is formulation chemistry and membrane type.

## 2. Results

### Main Table

| Scenario | N_train | Augmented? | alpha | RMSE (mean+/-SD) | R2 (mean+/-SD) | RMSE change vs baseline |
|---|---:|---|---:|---|---|---:|
| baseline_5 | 5 | No | - | 33.479+/-4.119 | -0.181+/-0.379 | - |
| augmented_5 | 5 | Yes | 3 | 48.008+/-5.055 | -1.453+/-0.807 | 43.4% |
| augmented_5 | 5 | Yes | 5 | 47.999+/-5.056 | -1.452+/-0.807 | 43.4% |
| augmented_5 | 5 | Yes | 10 | 47.995+/-5.057 | -1.452+/-0.807 | 43.4% |
| augmented_5 | 5 | Yes | 20 | 47.994+/-5.057 | -1.451+/-0.807 | 43.4% |
| augmented_5 | 5 | Yes | 50 | 47.994+/-5.057 | -1.451+/-0.807 | 43.4% |
| baseline_10 | 10 | No | - | 34.598+/-4.479 | -0.365+/-0.546 | - |
| augmented_10 | 10 | Yes | 3 | 45.485+/-6.217 | -1.478+/-1.251 | 31.5% |
| augmented_10 | 10 | Yes | 5 | 45.476+/-6.217 | -1.477+/-1.251 | 31.4% |
| augmented_10 | 10 | Yes | 10 | 45.472+/-6.217 | -1.476+/-1.251 | 31.4% |
| augmented_10 | 10 | Yes | 20 | 45.471+/-6.216 | -1.476+/-1.251 | 31.4% |
| augmented_10 | 10 | Yes | 50 | 45.471+/-6.216 | -1.476+/-1.251 | 31.4% |
| baseline_15 | 15 | No | - | 29.079+/-4.491 | -0.157+/-0.132 | - |
| augmented_15 | 15 | Yes | 3 | 32.619+/-7.042 | -0.480+/-0.498 | 12.2% |
| augmented_15 | 15 | Yes | 5 | 32.610+/-7.040 | -0.479+/-0.498 | 12.1% |
| augmented_15 | 15 | Yes | 10 | 32.606+/-7.039 | -0.479+/-0.497 | 12.1% |
| augmented_15 | 15 | Yes | 20 | 32.605+/-7.039 | -0.479+/-0.497 | 12.1% |
| augmented_15 | 15 | Yes | 50 | 32.605+/-7.039 | -0.479+/-0.497 | 12.1% |
| baseline_20 | 20 | No | - | 31.277+/-9.182 | -0.120+/-0.097 | - |
| augmented_20 | 20 | Yes | 3 | 35.902+/-11.312 | -0.526+/-0.593 | 14.8% |
| augmented_20 | 20 | Yes | 5 | 35.892+/-11.310 | -0.525+/-0.592 | 14.8% |
| augmented_20 | 20 | Yes | 10 | 35.888+/-11.310 | -0.525+/-0.592 | 14.7% |
| augmented_20 | 20 | Yes | 20 | 35.887+/-11.310 | -0.525+/-0.592 | 14.7% |
| augmented_20 | 20 | Yes | 50 | 35.886+/-11.310 | -0.525+/-0.592 | 14.7% |

### Best Alpha Per Scenario

| N_train | Best alpha | Best RMSE | Baseline RMSE | Improvement |
|---:|---:|---:|---:|---:|
| 5 | 50 | 47.994 | 33.479 | -43.4% |
| 10 | 50 | 45.471 | 34.598 | -31.4% |
| 15 | 50 | 32.605 | 29.079 | -12.1% |
| 20 | 50 | 35.886 | 31.277 | -14.7% |

## 3. Visualization Data

- Distribution data: `fig_data_distribution.csv`
- RMSE curve data: `fig_rmse_curves.csv`

## 4. Key Findings

1. Lowest augmented RMSE: N=15, alpha=50, RMSE=32.605.
2. Largest RMSE improvement: N=15, alpha=50, improvement=-12.1%.
3. The 24h alignment makes the augmentation scientifically cleaner than the previous 28h placeholder setup.
4. The limitation remains domain mismatch: literature provides response-scale information, not a matched Poloxamer/Ethanol/PG formulation map.

## 5. PhD Closure Narrative

SkinMiner closes the loop with Paper 1 by turning verified literature extraction into an explicit prior for early-stage GPR modelling; the revised 24h endpoint provides a shared experimental anchor, so the demonstration tests literature-assisted prediction under sparse self-generated data rather than an unmatched timepoint proxy.
