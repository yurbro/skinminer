# Phase 1 Step 2: F2 Cross-Vehicle-Domain Modelling

## 1. Background and Task Definition

A formulation scientist often has permeation data for hydrophilic cosolvent systems and wants to reason about a lipophilic vehicle that was not observed in the original training domain. The F2 task tests that setting directly: train on hydrophilic silicone membrane records and predict lipophilic silicone membrane log-flux.

All training and test permeation records used here were extracted automatically by SkinMiner v1.5 from the three Watkinson PDFs supplied through the PDF batch workflow. The modelling table is the deterministic Phase 1 normalized master table, not a manually edited JSONL baseline.

Formally, F2 trains on 17 hydrophilic, silicone, occluded records from Watkinson Part I and Part II and evaluates on 11 lipophilic, silicone, occluded records from Watkinson Part III. The target is `log10(J_mean)` in ug/cm2/h.

## 2. Methods

### 2.1 Data

The training set contains 17 records: Part I Table 3 (5), Part II Table 2 (10), and Part II Table 3 (2). The test set contains 11 records from Part III Table 3. All records are v4_accept_flux verified records propagated through the Phase 0.7 and Step 1 normalization tables.

The solubility table contains 28 entries: measured Watkinson Table 1 values where available, two Part III log-space interpolations, and ten PG/water values estimated by a Manrique/Yalkowsky log-linear cosolvent model. This PG/water solubility block is an explicit estimation, using fixed Part II section 4.1 endpoints of 0.09 mg/mL in water and 157.5 mg/mL in pure PG.

### 2.2 Features

The fixed feature vector was `[ethanol_vv, PG_vv, water_vv, MO_vv, MG_vv, total_polar_vv, total_apolar_vv, log10_solubility]`. Ridge features were standardized with `StandardScaler` fit on the training set only.

### 2.3 Models

Two models were evaluated. The baseline predicts the training mean log-flux for every test record. Ridge regression selected its alpha by leave-one-out cross-validation on the 17 training records, searching alpha values `[0.01, 0.1, 1.0, 10.0, 100.0]`.

### 2.4 Evaluation

Evaluation was performed once on the held-out Part III lipophilic test set. Metrics were RMSE in log10 flux, MAE in log10 flux, Spearman rank correlation, Pearson correlation, and the count of predictions within two-fold tolerance in original flux space.

## 3. Results

Leave-one-out cross-validation selected alpha = 1.0.

The mean baseline achieved RMSE_logJ = 0.172, MAE_logJ = 0.156, Spearman rho = 0.000, Pearson r = 0.000, and 11/11 predictions within 2x.

Ridge achieved RMSE_logJ = 0.106, MAE_logJ = 0.093, Spearman rho = -0.264, Pearson r = -0.151, and 11/11 predictions within 2x.

Key finding: Ridge regression trained on hydrophilic vehicle literature predicts lipophilic vehicle log-flux with RMSE = 0.106, achieving 11/11 predictions within 2x tolerance and Spearman rank correlation -0.264.

The audit verdict for this predefined F2 task is **RED**.

## 4. Figure

`outputs/phase1_step2_F2/figure_F2_main.pdf` and `.png` contain the two-panel F2 figure. Panel A compares predicted and actual Part III log-flux values with a one-to-one line and two-fold tolerance band. Panel B shows the train and test log-flux distributions; the target ranges overlap even though the composition domain shifts from polar cosolvent vehicles to MO/MG vehicles.

## 5. Discussion / Limitations

This is a deliberately small cross-domain demonstration. The split contains only 17 training records and 11 test records, and the composition features undergo a severe domain shift: the training set is entirely polar cosolvent space, while the test set is entirely lipophilic MO/MG space.

Solubility is the main bridging feature, but the PG/water block is estimated rather than measured. That assumption is transparent and reproducible, but it should not be treated as hidden experimental data. The model is also limited to a single deterministic Ridge fit; no few-shot tuning, ensemble modelling, or test-set resampling was used.

The skin-transfer question is intentionally excluded from F2 and is handled by the separate F3 silicone-vs-skin task.

## 6. Conclusion

SkinMiner v1.5 provides enough structured Watkinson records to run an honest hydrophilic-to-lipophilic silicone membrane prediction experiment. Under the frozen feature set and LOOCV-selected Ridge model, the result is reported as measured, with no post hoc feature additions or alpha tuning.

## Reproducibility Files

- `outputs/phase1_step2_F2/solubility_table.csv`
- `outputs/phase1_step2_F2/feature_table.csv`
- `outputs/phase1_step2_F2/predictions.csv`
- `outputs/phase1_step2_F2/metrics.json`
- `outputs/phase1_step2_F2/figure_F2_main.pdf`
- `outputs/phase1_step2_F2/figure_F2_main.png`
- `outputs/phase1_step2_F2/figure_F2_main_metadata.json`

## Feature-Space Diagnostics

Train log10 solubility range: [-1.046, 3.4665710723863543]. Test log10 solubility range: [1.5050142400841071, 2.224351745013417]. Overlap: True.

Missing solubility rows: 0.
