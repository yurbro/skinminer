# Demo 2 Step 2i: Mechanism Analysis

## Combined Mechanism Interpretation

The PC1-PC2 bounding boxes overlap geometrically, but none of the 8 literature observations falls inside the in-house PC1-PC2 box; likewise, 0/8 literature records fall inside the in-house four-dimensional feature hyperrectangle. The two dataset centroids are 1.90 pooled standard deviations apart in PC1-PC2 space, although all four marginal feature ranges overlap.
Bolla-internal LOOCV gives Ridge R2_conv=-0.101, rho=0.571, and GPR R2_conv=-0.564, rho=-0.762; Neither model passes the pre-specified internal-modellability threshold, so small-N target-side difficulty contributes alongside the feature-space mismatch; the evidence does not support a purely cross-dataset explanation.
Mechanistically, ridge is driven toward a narrow prediction range because the source-side linear signal is weak and every literature record lies outside the observed in-house multivariate feature envelope; the RBF GPR reverts toward its learned mean as kernel similarity decays away from training points.
Thus the observed near-constant ridge predictions and GPR prior-mean collapse are model-specific symptoms of the same distribution mismatch, with the Bolla LOOCV result determining whether limited target-side modellability is an additional contributor.

## Analysis A: Four-Feature Distribution

The combined 37-record feature matrix was standardised with StandardScaler fitted on all rows for visualisation only. This scaling was not used for transfer-model evaluation.

### Standardisation Parameters

| Feature | Mean | Scale |
|---|---:|---:|
| `log10_vehicle_solubility` | 0.665812 | 0.444392 |
| `ethanol_fraction` | 0.131511 | 0.070521 |
| `pg_fraction` | 0.129357 | 0.059094 |
| `water_fraction` | 0.373808 | 0.120153 |

### PCA Explained Variance

| Component | Explained variance ratio |
|---|---:|
| PC1 | 0.701140 |
| PC2 | 0.187025 |
| PC3 | 0.101269 |
| PC4 | 0.010566 |

### PCA Loadings

Component weights are the PCA eigenvector coefficients; correlation loadings additionally scale each coefficient by the square root of the component eigenvalue.

| Feature | PC1 weight | PC2 weight | PC1 correlation loading | PC2 correlation loading |
|---|---:|---:|---:|---:|
| `log10_vehicle_solubility` | 0.566840 | -0.073883 | 0.962371 | -0.064785 |
| `ethanol_fraction` | 0.360715 | 0.913119 | 0.612415 | 0.800675 |
| `pg_fraction` | 0.482853 | -0.329207 | 0.819779 | -0.288668 |
| `water_fraction` | -0.561632 | 0.228863 | -0.953529 | 0.200680 |

### Standardised Feature-Range Overlap

| Feature | in-house range | literature range | Overlap? | Shared interval | literature records inside in-house range |
|---|---:|---:|---|---:|---:|
| log10 solubility | [-0.958, 1.205] | [-2.646, 3.428] | yes | [-0.958, 1.205] | 5/8 |
| ethanol fraction | [-0.447, 0.971] | [-1.865, 2.389] | yes | [-0.447, 0.971] | 1/8 |
| PG fraction | [-0.497, 1.195] | [-2.189, 0.349] | yes | [-0.497, 0.349] | 3/8 |
| water fraction | [-1.030, 0.634] | [-3.111, 2.332] | yes | [-1.030, 0.634] | 1/8 |

### PC1-PC2 Bounding Boxes and Centroids

| Dataset | PC1 range | PC2 range | Centroid (PC1, PC2) |
|---|---:|---:|---:|
| in-house | [-1.300, 2.189] | [-0.853, 1.026] | (0.535, 0.105) |
| literature | [-4.539, 3.698] | [-1.567, 3.447] | (-1.939, -0.380) |

- PC1-PC2 bounding-box intersection area: 6.555110.
- Percentage of in-house bounding box intersected by literature box: 100.000%.
- Percentage of literature bounding box intersected by in-house box: 15.872%.
- Literature observations inside the in-house PC1-PC2 bounding box: 0/8.
- In-house observations inside the literature PC1-PC2 bounding box: 29/29.
- Literature observations inside the in-house four-dimensional feature hyperrectangle: 0/8.
- Centroid displacement in pooled-SD units: PC1=-1.811, PC2=-0.561; Euclidean distance=1.895.

Overlapping feature ranges: log10 solubility, ethanol fraction, PG fraction, water fraction. Disjoint feature ranges: none.

Verdict: The PC1-PC2 bounding boxes overlap geometrically, but none of the 8 literature observations falls inside the in-house PC1-PC2 box, and no literature record lies inside the in-house four-dimensional hyperrectangle. Because every marginal range overlaps, the separation is multivariate and driven by feature combinations and extremes rather than by one wholly disjoint feature. This supports out-of-distribution test exposure as a proximate mechanism for negative cross-protocol transfer.

## Analysis B: Bolla-Internal LOOCV

Each fold trains on seven Bolla records and predicts the eighth. StandardScaler is fitted on the seven-record training fold only. R2_conv is sklearn R2 computed once over all eight concatenated held-out predictions; RMSE is in log10(J); within-2x means absolute log10 residual <= log10(2).

### Per-Fold Predictions

| Held out | logJ actual | Ridge pred | Ridge residual | Ridge abs residual | Ridge within-2x | GPR pred | GPR residual | GPR abs residual | GPR within-2x |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| F1A | 0.431364 | 0.593323 | 0.161959 | 0.161959 | yes | 0.897371 | 0.466008 | 0.466008 | no |
| F1B | 0.352183 | 0.537128 | 0.184946 | 0.184946 | yes | 0.908723 | 0.556541 | 0.556541 | no |
| F2A | 0.871573 | 0.580712 | -0.290861 | 0.290861 | yes | 0.564010 | -0.307563 | 0.307563 | no |
| F2B | 0.559907 | 0.686616 | 0.126709 | 0.126709 | yes | 0.871702 | 0.311795 | 0.311795 | no |
| F3 | 1.326131 | 0.945452 | -0.380679 | 0.380679 | no | 0.733011 | -0.593120 | 0.593120 | no |
| F4 | 0.731589 | 1.056737 | 0.325148 | 0.325148 | no | 1.191830 | 0.460241 | 0.460241 | no |
| F5 | 0.869818 | 1.847086 | 0.977267 | 0.977267 | no | 0.834839 | -0.034979 | 0.034979 | yes |
| F6 | 1.571126 | 1.400453 | -0.170673 | 0.170673 | yes | 0.734652 | -0.836474 | 0.836474 | no |

### Aggregate Metrics

| Model | R2_conv | RMSE_logJ | Spearman rho | Pearson r | within-2x |
|---|---:|---:|---:|---:|---:|
| RIDGE | -0.100958 | 0.417719 | 0.571429 | 0.541017 | 5/8 |
| GPR | -0.564185 | 0.497900 | -0.761905 | -0.446444 | 1/8 |

Verdict: Bolla internal modellability is not demonstrated; the result is inconclusive at n=8 and indicates target-side difficulty. A model is called internally modellable here only if pooled LOOCV R2_conv > 0.3 and Spearman rho > 0.5; qualifying models: none.

Important caveat: only eight records are available for four input features. LOOCV therefore has very limited statistical power, and a modest positive score would still be compatible with chance. Scores below the stated threshold are interpreted as inconclusive rather than proof that Bolla is definitively unmodellable.

## Path to Paper

The feature-space analysis provides the clearer direct mechanism-level evidence because it quantifies the geometric relationship between source and target: 0/8 literature points inside the in-house PC1-PC2 box, 0/8 inside the in-house four-dimensional hyperrectangle, and a 1.90-pooled-SD centroid separation. The Bolla-internal LOOCV adds the necessary target-side control: Neither model passes the pre-specified internal-modellability threshold, so small-N target-side difficulty contributes alongside the feature-space mismatch; the evidence does not support a purely cross-dataset explanation.

Together, these analyses answer the supervisor's symptoms-versus-mechanism concern. The cross-dataset prediction collapse is linked directly to feature-space distribution mismatch, while the internal control determines whether the eight-record target dataset also lacks enough stable structure for independent modelling.

## Output Audit

- Step 2g feature-value sanity check: PASS; 148 values compared; maximum absolute difference=4.808e-13.
- `feature_space_pca.csv`
- `feature_space_overlap_metrics.json`
- `bolla_internal_loocv_results.json`
- `figure_feature_space.pdf`
- `figure_feature_space.png`
- `run_demo2_mechanism.py`
