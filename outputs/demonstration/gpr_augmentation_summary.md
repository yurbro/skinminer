# GPR Literature Augmentation Results

## Experiment Setup

- Own data: `C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\demonstration\paper1_placeholder_data.csv`
- Literature data: `C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\demonstration\literature_permeation_data_gpr.csv`
- Placeholder own data used: `False`
- Kernel mode: `paper_like`
- Literature pseudo-feature mode: `center_jitter`
- Alpha factors tested for augmented runs: `[3.0, 5.0, 10.0, 20.0]`
- Scenario matrix: `['baseline_5', 'augmented_5', 'baseline_10', 'augmented_10', 'baseline_15', 'augmented_15', 'baseline_20', 'augmented_20']`

## Results Table

| Scenario | Train size | Augmented? | Alpha factor | RMSE (mean±SD) | R² (mean±SD) | Improvement vs baseline |
|---|---:|---|---:|---|---|---|
| baseline_5 | 5 | No | — | 24.115±1.571 | -0.146±0.223 | — |
| augmented_5 | 5 | Yes | 20 | 4791.714±177.013 | -45128.897±6747.675 | -19770.0% |
| baseline_10 | 10 | No | — | 23.622±2.387 | -0.219±0.395 | — |
| augmented_10 | 10 | Yes | 20 | 3403.578±104.143 | -25271.410±6691.782 | -14308.5% |
| baseline_15 | 15 | No | — | 22.707±3.262 | -0.166±0.187 | — |
| augmented_15 | 15 | Yes | 20 | 2435.605±72.094 | -14198.156±4573.086 | -10626.2% |
| baseline_20 | 20 | No | — | 22.614±3.479 | -0.191±0.271 | — |
| augmented_20 | 20 | Yes | 20 | 2327.743±84.086 | -13181.135±4354.060 | -10193.6% |

## Alpha Factor Sensitivity

| alpha_factor | RMSE improvement at n=5 | RMSE improvement at n=10 | RMSE improvement at n=15 | RMSE improvement at n=20 |
|---:|---:|---:|---:|---:|
| 3 | -20219.2% | -14809.7% | -11233.7% | -10796.1% |
| 5 | -19928.7% | -14483.5% | -10838.9% | -10404.8% |
| 10 | -19800.9% | -14342.4% | -10668.3% | -10235.9% |
| 20 | -19770.0% | -14308.5% | -10626.2% | -10193.6% |

## Key Findings

1. Strongest augmented scenario: `augmented_20` with RMSE `2327.743`.
2. Largest RMSE improvement vs baseline: `-10193.6%` at train size `20` and alpha `20`.
3. Because literature points are injected as noisy response priors, any gain should be interpreted as regularization under sparse data rather than exact formulation transfer.
4. The main limitation is domain mismatch: Paper 1 uses Poloxamer 407 / ethanol / PG on Strat-M, while the literature set is mostly porcine and non-matching excipient systems.
