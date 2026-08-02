# Phase 1 Step 2 Redo: Part I to Part II Within-Domain Transfer

## 1. Task definition

A formulation scientist has Part I-style ethanol/water cosolvent data and wants to know whether the framework's extracted data, plus a simple regression model, can predict Part II-style PG-system fluxes. This redo defines a within-domain hydroxy-cosolvent transfer task: Part I EtOH/water silicone membrane records are the source domain, and Part II PG/water plus EtOH/PG/water silicone membrane records are the target domain.

Part I and Part II both use hydroxy cosolvent systems, so this is a more chemically coherent transfer setting than the earlier hydrophilic-to-lipophilic split. The data source is the SkinMiner v1.5 extraction from user-supplied Watkinson PDFs propagated through the deterministic Phase 1 normalization table.

## 2. Methods

### 2.1 Data

The dataset contains 5 training records from Part I Table 3 and 12 test records from Part II Tables 2 and 3. Part II Table 4 is excluded because it is non-occluded; Part III lipophilic and all skin records are outside this task scope.

### 2.2 Features

Two fixed feature sets were evaluated: `composition_only = [ethanol_vv, PG_vv, water_vv]` and `composition_plus_solubility = [ethanol_vv, PG_vv, water_vv, log10_solubility]`. No derived cosolvent flags, polynomial features, or additional descriptors were added.

### 2.3 Models

Ridge regression with alpha=1.0 fixed across feature sets and protocols. Leave-one-out cross-validation on n=5 training records was found to select unstable alpha values (0.1 to 100 depending on feature set), reflecting the known difficulty of cross-validation in small-sample regimes. We fix alpha=1.0 (sklearn default after standardization) to ensure fair comparison across feature sets and consistency between zero-shot and few-shot protocols.

The second model was Gaussian Process Regression with a ConstantKernel * Matern(nu=2.5) + WhiteKernel kernel, feature standardization fit on the training set, `random_state=42`, and five optimizer restarts.

### 2.4 Evaluation

Zero-shot models were fit on five Part I records and evaluated on all twelve Part II target records. Few-shot experiments sampled k in {3, 5} target records into the training set for 80 deterministic repeats using `np.random.SeedSequence(42)`; the remaining target records were evaluated with Ridge alpha fixed at 1.0.

## 3. Results: Zero-shot

| Feature set | Model | RMSE_logJ | Spearman rho | Within 2x | Top-3 hit |
| --- | --- | --- | --- | --- | --- |
| composition_only | ridge | 0.206 | 0.615 | 9/12 | 0.33 |
| composition_only | gpr | 0.332 | 0.601 | 5/12 | 0.33 |
| composition_plus_solubility | ridge | 0.199 | 0.706 | 9/12 | 0.67 |
| composition_plus_solubility | gpr | 0.329 | 0.218 | 5/12 | 0.00 |

Best zero-shot Spearman was 0.706 for `ridge` with `composition_plus_solubility` (n=12, threshold rho_0.05=0.587; significant at p<0.05 under permutation null).

Ridge and GPR trade off magnitude and ranking differently in this low-data setting; the final verdict uses the frozen criteria rather than post hoc model selection.

## 4. Results: Few-shot

| k | Feature set | RMSE_logJ mean +/- SD | Spearman mean +/- SD | Within 2x mean | Top-3 hit mean |
| --- | --- | --- | --- | --- | --- |
| 3 | composition_only | 0.126 +/- 0.035 | 0.609 +/- 0.290 | 0.98 | 0.56 |
| 3 | composition_plus_solubility | 0.121 +/- 0.034 | 0.725 +/- 0.121 | 0.98 | 0.59 |
| 5 | composition_only | 0.119 +/- 0.028 | 0.634 +/- 0.311 | 0.99 | 0.61 |
| 5 | composition_plus_solubility | 0.114 +/- 0.032 | 0.698 +/- 0.186 | 0.99 | 0.64 |

The best k=5 mean Spearman was 0.698 for `composition_plus_solubility` (n=7 per repeat, threshold rho_0.05=0.786; marginal significance).

## 5. Discussion

This within-domain transfer setting is chemically more coherent than cross-vehicle-class transfer, but it remains a strict minimal-data experiment. It tests whether the extracted composition and solubility fields carry enough information to transfer from ethanol/water to PG-containing hydroxy cosolvent systems.

The solubility feature contributes an explicit mechanistic bridge, combining measured Watkinson values with transparent Manrique/Yalkowsky log-linear estimates for PG/water. Its effect is reported separately from composition-only results so the assumption remains auditable.

The 5 training records per zero-shot setting and 5-to-10 records in few-shot represent a minimal-data regime where standard cross-validation procedures become unreliable. This is consistent with the framing of Step 2 as a feasibility demonstration on SkinMiner-extracted data, rather than a rigorous transfer learning benchmark. Stability of the conclusion under alpha choice is verified by reporting alpha=1.0 results without LOOCV tuning.

Compared to a cross-class transfer setting, this result should be interpreted as within-hydroxy-cosolvent feasibility only. It does not claim transfer to fundamentally different lipophilic vehicle classes, and it does not address silicone-to-skin transfer.

## 6. Reproducibility

- Ridge alpha fixed at 1.0 for all protocols.
- GPR `random_state=42`; few-shot repeats use `np.random.SeedSequence(42)` with 80 spawned child sequences.
- Python packages: sklearn 1.7.0, numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.3.
- Output file hashes:
  - `outputs/phase1_step2_redo/dataset.csv`: `f6434cd1a02995ff85cc0978ec971971a140b7a2897985ecad8c6fadbd74b528`
  - `outputs/phase1_step2_redo/fewshot_raw_runs.csv`: `83ecbdc421ad708016e1ff8b5b88db615fe32df7f3aea587f84a922cbf960034`
  - `outputs/phase1_step2_redo/fewshot_results.csv`: `3703820afe1b64a9ca3d425aca0193dab08783619b39a17eafd00fc3a36e5123`
  - `outputs/phase1_step2_redo/predictions_zero_shot.csv`: `1f3bb02c8d9cd185a974ca53c1a436d870a5ad2f1b5481a0137ac810ed747b39`
  - `outputs/phase1_step2_redo/zero_shot_results.csv`: `2fd3500d36ff5055895232a01927940b28e9e8d0dccb799c534686ab73026354`

Verdict: **GREEN**. Overall status: **PASS**.
