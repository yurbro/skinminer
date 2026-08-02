# Demo 2 Figure 3.6.1 Report

## Data Sources Read

- Panel A predictions: `transfer_4feature_xiao_to_bolla.csv`
- Panel B red-flag values: hardcoded binary v3.4 protocol-distance rule from `codex_prompt_demo2_figure_v34.md`

No modelling was rerun; the figure uses existing 4-feature predictions and the specified binary red-flag vector.

## Panel A Coordinates Verified Against CSV

| record_id | logJ_actual | logJ_pred | within_2x |
|---|---:|---:|---:|
| F1A | 0.431363764159 | 1.066039549121 | 0 |
| F1B | 0.352182518111 | 1.053286662095 | 0 |
| F2A | 0.871572935546 | 1.117142595379 | 1 |
| F2B | 0.559906625036 | 1.114322886884 | 0 |
| F3 | 1.326130956711 | 1.149982015328 | 1 |
| F4 | 0.731588765187 | 1.133775831839 | 0 |
| F5 | 0.869818207979 | 0.969656779340 | 1 |
| F6 | 1.571126277084 | 1.114125323683 | 0 |

Headline metrics annotated: Spearman rho = +0.43, R2_conv = -0.32, within-2x = 3/8.
Panel A includes a faint OLS fit line for logJ_pred ~ logJ_actual, clipped to the observed literature x-range.

## Panel B Red-Flag List

| dimension | red_flag | rationale | grouping |
|---|---:|---|---|
| Composition paradigm | 1 | different coarse class | flagged |
| Diffusion-cell class | 1 | static vs dynamic (different coarse class) | flagged |
| Receptor medium | 1 | aqueous vs ethanolic (different coarse class) | flagged |
| Donor dose | 1 | 30x ratio (>2x threshold) | flagged |
| Effective diffusion area | 1 | 2.56x ratio (>2x threshold) | flagged |
| Run duration | 0 | 1.25x ratio (<2x) | compatible |
| Active substance | 0 | same molecule and salt form | compatible |
| Membrane | 0 | identical (Strat-M) | compatible |

Panel B was redesigned from a continuous protocol-distance bar chart into a categorical red-flag list. No mean line or continuous distance score is shown. Summary: 5 of 8 dimensions flagged.

## Outputs

- `figure_demo2_main.pdf`
- `figure_demo2_main.png`

<!-- RATIO_LINES_REDRAW_START -->

## Ratio-Sweep Line Figure Redraw

The ratio-sweep line figure was redrawn from `ratio_sweep_summary.csv` only; no model fitting or analysis was rerun.

Published figure rendering:

- error bars replaced by same-colour shaded +/-SD bands;
- Panel A uses a broken y-axis to separate the extreme lit=8, n=8 cell from the main -5.7 to 0.65 region;
- a single horizontal legend is placed below both panels;
- the source-derived marginal annotation reports -0.714 R2_conv per added literature record;
- the global suptitle was removed and the panel dimensions match the published figure size;
- panel titles, fonts, palette, line styles, and filled markers were revised for main-paper readability.

Data verification: all 25 unique `(lit, n)` cells were read unchanged from `ratio_sweep_summary.csv`; source SHA-256 `768bc8ea632564fe3908b27260a45a4989c6527305db2fad1f59d7e495706b01`.

The release package regenerates `figure_ratio_sweep_lines.pdf` and `figure_ratio_sweep_lines.png` directly. Legacy figure variants are not required or distributed.

<!-- RATIO_LINES_REDRAW_END -->

<!-- FIG362_REDRAW_START -->

## Figure 3.6.2: Feature-Space Redraw

The Step 2i feature-space visualisation was redrawn as a main-paper figure without rerunning PCA or changing any record coordinates or analysis values.

Published figure rendering:

- filled markers and filled range bars throughout;
- formulation-class dataset legend using `in-house` and `literature` labels;
- dashed convex hulls for visual orientation;
- source-verified annotations: 0/8 literature points inside the in-house 4D feature hyperrectangle, centroid distance 1.9 pooled SD, and PC1+PC2 variance 88.8%;
- font, panel labels, and blue/orange palette matched to Fig. 3.6.1;
- publication outputs renamed to `figure_demo2_feature_space.pdf` and `figure_demo2_feature_space.png`;
- legacy supplementary figure variants are not required or distributed.

All 29 in-house records and all 8 literature records are plotted. Literature formulations F1A-F6 and representative in-house records RUN1-RUN4 are labelled with leader lines.

<!-- FIG362_REDRAW_END -->
