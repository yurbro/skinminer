# Reproducibility

This repository separates deterministic evaluation and demo reconstruction from API-dependent corpus mining. The commands below identify which results run offline and which require external services.

## Environment

Use Python 3.11. The validated Demo 1 environment used:

| Package | Version |
|---|---:|
| Python | 3.11.9 |
| NumPy | 1.26.4 |
| SciPy | 1.11.4 |
| scikit-learn | 1.5.0 |
| Matplotlib | 3.8.2 |

Install the pinned direct dependencies with:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
```

`pyproject.toml` carries compatible version ranges for normal development. `requirements-lock.txt` pins the imported direct dependencies for result verification. It is not a machine-specific `pip freeze` dump.

## Deterministic checks

Run the evaluation regression suite:

```bash
python -B -m unittest discover -s evaluation/tests -v
```

Expected result: 9 tests pass. The suite asserts cumulative policy semantics, GPT v1 through v4 metrics, Claude Extended metrics, the undefined Claude Strict precision, and input contracts for the 130-row gold CSV.

Recompute the GPT Extended metrics:

```bash
python -m evaluation.score_run \
  --gold-format round2 \
  --provider gpt \
  --policy-level v2 \
  --gold-csv evaluation/gold/gold_set_round2_annotation.csv
```

Expected values are 25 verified, 70 unresolved, 12 rejected, 25 scope true positives, 0 scope false positives, 100% scope precision, 24 scope-and-value true positives, and 96% end-to-end precision.

## Demo 1 reconstruction

```bash
python demos/demo1/rebuild_demo1.py
```

The script reads 17 archived records, uses 5 Part I records for training, and evaluates 12 Part II records. It regenerates Table 4, few-shot results, predictions, Fig. 10, and a machine-readable run summary.

Expected validation status:

- Table 4: 4 EXACT count cells, 16 ROUNDING_MATCH continuous cells, 0 MISMATCH.
- Few-shot targets: 3 ROUNDING_MATCH, 0 MISMATCH.
- Ridge composition-only: RMSE 0.206, R² -0.58, Spearman 0.615, Pearson 0.675, 9/12 within twofold.
- Ridge composition plus solubility: RMSE 0.199, R² -0.47, Spearman 0.706, Pearson 0.734, 9/12 within twofold.
- GPR composition-only: RMSE 0.332, R² -3.10, Spearman 0.601, Pearson 0.378, 5/12 within twofold.
- GPR composition plus solubility: RMSE 0.329, R² -3.03, Spearman 0.218, Pearson 0.392, 5/12 within twofold.

### Demo 1 assumptions

The reconstruction makes the following explicit choices:

- It reads the archived `log10_J_mean` and `log10_solubility` values instead of recalculating them from rounded display columns.
- It uses the archived 0 to 100 volume-percent composition scale.
- It fits each `StandardScaler` only on the applicable training set.
- Ridge uses alpha 1.0, an intercept, the automatic solver, tolerance 1e-4, and seed 42.
- GPR uses `ConstantKernel × Matern(nu=2.5) + WhiteKernel`, five optimizer restarts, `normalize_y=True`, alpha 1e-10, and seed 42.
- The within-twofold threshold is exactly 0.301 in log10 units.
- Few-shot calibration uses k values 3 and 5, 80 repeats per group, `SeedSequence(42)`, and sample SD with `ddof=1`.

### GPR version drift

The archived modelling environment used scikit-learn 1.7.0, NumPy 2.2.6, and SciPy 1.15.3. The validated reconstruction uses the versions listed above. Ridge predictions agree with archived high-precision predictions to about 6e-10. GPR optimization terminates at slightly different points because L-BFGS-B and Gaussian-process defaults can vary across library versions.

The largest per-record GPR prediction difference is about 4.76e-4. All manuscript-displayed GPR cells still round to the reported values. `normalize_y=True` is the decisive archived-result assumption. Setting it to false produces RMSE values far from Table 4.

Fig. 10 preserves scientific content and output dimensions. Minor differences remain in spacing, density-bin rendering, marker appearance, alpha blending, and anti-aliasing.

## Table 3 audit

```bash
python demos/demo1/table3_stats.py \
  --records-csv demos/demo1/data/watkinson_audit/master_table_v15_normalized.csv \
  --reference-csv demos/demo1/table3_paper_reference.csv \
  --output-csv demos/demo1/outputs/table3_rebuilt.csv \
  --summary-json demos/demo1/outputs/table3_summary.json
```

Expected total: 47 records across ten paper and source-table groups. The script compares both record counts and manuscript-rounded J ranges.

## Demo 2

The Demo 2 directory preserves the original mirror topology because scripts resolve data relative to their own location.

Main transfer figure:

```bash
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_4feature.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_figure.py
```

Ratio sweep and feature space:

```bash
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_sweep.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_lines_redraw.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_mechanism.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_feature_space_figure.py
```

The main transfer result expects Spearman 0.43, conventional R² -0.32, and 3/8 predictions within twofold. The protocol comparison flags 5/8 dimensions. The feature-space result expects 88.8165% variance in PC1 plus PC2, 0/8 literature points inside the in-house four-dimensional hyperrectangle, and a centroid distance of 1.8954 pooled SD.

## Randomness

Randomness enters through LLM responses, GPR optimizer restarts, few-shot subset sampling, and some figure or table routing choices. Demo 1 fixes seed 42 and records all child seeds. Demo 2 scripts define their seeds in the script headers and persist result JSON or CSV files. API-dependent pipeline runs can still vary because hosted models and remote sources change.

## External services

Full pipeline execution can require Europe PMC, Unpaywall, OpenAI, and optionally Anthropic. Store credentials outside version control. The OpenAI and Anthropic SDKs read their standard API-key environment variables. Scouting utilities read `NCBI_EMAIL`. The Unpaywall resolver accepts a contact email at the access layer.

## Published boundaries

The repository does not contain source PDFs, remote source caches, record-level run JSONL, or raw Claude audit workbooks. These assets are excluded for copyright, privacy, and repository-size reasons. Aggregate result files support the manuscript mappings listed in [paper_mapping.md](paper_mapping.md).

Table 2 stable-core and Jaccard values remain static report-derived summaries. The five aggregate run reports are public, while the record sets required for a fresh set-intersection calculation remain in restricted archival storage.
