# Demo 2 Step 2n: Configuration-Ratio Sweep

## 1. Setup and Sanity Checks

The 5 x 5 grid spans literature counts `lit={0,2,4,6,8}` and matched total training sizes `n={8,12,16,20,24}`, with `ih=n-lit`. Every model uses the unchanged 4-feature bridge, log10(J), StandardScaler fitted on training rows only, and Ridge(alpha=1.0). Evaluation is always on held-out in-house records.

BBD4/BBD5/BBD6 were treated as one indivisible center-point block in every in-house subset. Effective valid-subset counts therefore use `C(26, ih) + C(26, ih-3)` rather than treating all 29 in-house rows as independent choices. Leakage guard: PASS.

Boundary tolerance: 1.0e-06. All ten Step 2m boundary cells passed; worst-case aggregate metric difference=1.421e-14. The lit=0 cells exactly reproduce Configuration A subset sequences and the lit=8 cells exactly reproduce Configuration B subset sequences.

Total retained subset fits: 4801 across 25 cells. Only `(lit=8, n=8)` is exhaustive with one possible subset; every other cell uses 200 deterministic unique subsets.

## 2. Full 25-Cell Summary

| lit | ih | n | R2_conv mean +/- std | Spearman rho mean +/- std | n_test | n_subsets |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 8 | 8 | -1.266 +/- 4.452 | -0.007 +/- 0.196 | 21 | 200 |
| 0 | 12 | 12 | -0.621 +/- 0.794 | 0.008 +/- 0.226 | 17 | 200 |
| 0 | 16 | 16 | -0.489 +/- 0.576 | 0.023 +/- 0.259 | 13 | 200 |
| 0 | 20 | 20 | -0.445 +/- 0.571 | 0.062 +/- 0.320 | 9 | 200 |
| 0 | 24 | 24 | -0.651 +/- 0.845 | 0.072 +/- 0.500 | 5 | 200 |
| 2 | 6 | 8 | -2.946 +/- 2.657 | -0.092 +/- 0.188 | 23 | 200 |
| 2 | 10 | 12 | -2.064 +/- 1.950 | -0.041 +/- 0.232 | 19 | 200 |
| 2 | 14 | 16 | -1.571 +/- 1.585 | -0.040 +/- 0.257 | 15 | 200 |
| 2 | 18 | 20 | -1.830 +/- 2.423 | -0.066 +/- 0.292 | 11 | 200 |
| 2 | 22 | 24 | -1.927 +/- 2.757 | -0.072 +/- 0.383 | 7 | 200 |
| 4 | 4 | 8 | -4.718 +/- 2.829 | -0.068 +/- 0.128 | 25 | 200 |
| 4 | 8 | 12 | -3.519 +/- 2.342 | -0.043 +/- 0.158 | 21 | 200 |
| 4 | 12 | 16 | -2.769 +/- 2.303 | -0.006 +/- 0.190 | 17 | 200 |
| 4 | 16 | 20 | -2.543 +/- 2.045 | -0.023 +/- 0.240 | 13 | 200 |
| 4 | 20 | 24 | -2.566 +/- 2.731 | -0.034 +/- 0.305 | 9 | 200 |
| 6 | 2 | 8 | -6.532 +/- 4.798 | -0.021 +/- 0.082 | 27 | 200 |
| 6 | 6 | 12 | -3.974 +/- 2.176 | -0.017 +/- 0.115 | 23 | 200 |
| 6 | 10 | 16 | -3.462 +/- 1.917 | -0.044 +/- 0.168 | 19 | 200 |
| 6 | 14 | 20 | -3.302 +/- 2.183 | -0.034 +/- 0.203 | 15 | 200 |
| 6 | 18 | 24 | -3.500 +/- 3.050 | 0.006 +/- 0.239 | 11 | 200 |
| 8 | 0 | 8 | -15.988 +/- 0.000 | 0.068 +/- 0.000 | 29 | 1 |
| 8 | 4 | 12 | -4.984 +/- 2.354 | 0.002 +/- 0.082 | 25 | 200 |
| 8 | 8 | 16 | -4.038 +/- 2.023 | -0.019 +/- 0.128 | 21 | 200 |
| 8 | 12 | 20 | -3.557 +/- 1.904 | -0.019 +/- 0.179 | 17 | 200 |
| 8 | 16 | 24 | -3.485 +/- 2.223 | -0.012 +/- 0.239 | 13 | 200 |

## 3. Per-n Cross-Sections

### n=8

Best mean R2_conv: lit=0, ih=8, -1.266. Ranking: lit=0 > lit=2 > lit=4 > lit=6 > lit=8.

Monotonic non-increasing as lit rises: yes. Literature-positive mean cells versus lit=0: none. Cells exceeding lit=0 by at least one combined SD: none.

### n=12

Best mean R2_conv: lit=0, ih=12, -0.621. Ranking: lit=0 > lit=2 > lit=4 > lit=6 > lit=8.

Monotonic non-increasing as lit rises: yes. Literature-positive mean cells versus lit=0: none. Cells exceeding lit=0 by at least one combined SD: none.

### n=16

Best mean R2_conv: lit=0, ih=16, -0.489. Ranking: lit=0 > lit=2 > lit=4 > lit=6 > lit=8.

Monotonic non-increasing as lit rises: yes. Literature-positive mean cells versus lit=0: none. Cells exceeding lit=0 by at least one combined SD: none.

### n=20

Best mean R2_conv: lit=0, ih=20, -0.445. Ranking: lit=0 > lit=2 > lit=4 > lit=6 > lit=8.

Monotonic non-increasing as lit rises: yes. Literature-positive mean cells versus lit=0: none. Cells exceeding lit=0 by at least one combined SD: none.

### n=24

Best mean R2_conv: lit=0, ih=24, -0.651. Ranking: lit=0 > lit=2 > lit=4 > lit=8 > lit=6.

Monotonic non-increasing as lit rises: no. Literature-positive mean cells versus lit=0: none. Cells exceeding lit=0 by at least one combined SD: none.

## 4. Marginal Value of Literature

Each value below is the change in mean R2_conv per added literature record over an adjacent two-record step. Positive values improve R2_conv; negative values worsen it.

| n | lit 0->2 | lit 2->4 | lit 4->6 | lit 6->8 | classification |
|---:|---:|---:|---:|---:|---|
| 8 | -0.840 | -0.886 | -0.907 | -4.728 | negative throughout |
| 12 | -0.722 | -0.727 | -0.228 | -0.505 | negative throughout |
| 16 | -0.541 | -0.599 | -0.347 | -0.288 | negative throughout |
| 20 | -0.692 | -0.357 | -0.379 | -0.127 | negative throughout |
| 24 | -0.638 | -0.320 | -0.467 | +0.008 | mixed / non-monotonic |

## 5. Direct Answer: Can Literature Reduce In-House Experiments?

No. Across all 25 cells, no lit>0 configuration exceeds the corresponding lit=0 mean R2_conv. Pure in-house training is highest at every n, so literature data does not reduce the required in-house experiments for this pair under this protocol.

## 6. Outcome Scenario

**Scenario 3 (weak non-monotonicity): lit=0 remains highest, but at least one adjacent intermediate-literature step reverses direction.**

The grid is technically non-monotonic without a literature cell beating pure in-house. The largest positive adjacent reversal is n=24, lit=6->8 (delta R2_conv=+0.015); this is far smaller than the cell standard deviations (3.050 and 2.223) and the destination remains 2.834 R2 units below lit=0. It is not evidence of a positive literature sweet spot, but it prevents a literal claim that every adjacent literature increment monotonically worsens the mean.

This judgement is bounded to the Xiao-Bolla pair, the four-feature bridge, log10(J), and Ridge(alpha=1.0). It does not generalize to literature data as a whole.

## Outputs

- `ratio_sweep_results.json`
- `ratio_sweep_summary.csv`
- `figure_ratio_sweep_lines.pdf` and `.png`
- `figure_ratio_sweep_heatmap.pdf` and `.png`
- `run_demo2_ratio_sweep.py`
