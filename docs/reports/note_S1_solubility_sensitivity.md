# Solubility Sensitivity Analysis (Note S1)

## Solubility construction methods

1. **Log-linear log space**: baseline values already used in §3.5.1, with `log10(S_mix) = (1-f_PG) * log10(0.09) + f_PG * log10(157.5)`.
2. **Linear raw space**: `S_mix = (1-f_PG) * 0.09 + f_PG * 157.5`, then transformed to `log10(S_mix)`.
3. **Quadratic with midpoint anchor**: `log10(S) = -1.698 * f_PG^2 + 4.941 * f_PG - 1.046`, anchored at 0% PG, 50% PG, and 100% PG.

## Results

| Method | RMSE_logJ | Spearman ρ | Pearson r | Within 2× |
| --- | --- | --- | --- | --- |
| 1. Log-linear log space (Yalkowsky 1999, used in §3.5.1) | 0.199 | 0.706 | 0.734 | 9/12 |
| 2. Linear raw space | 0.232 | 0.706 | 0.740 | 9/12 |
| 3. Quadratic with midpoint anchor | 0.207 | 0.706 | 0.735 | 9/12 |

Spearman ρ range: 0.706 to 0.706
All three above n=12 threshold (ρ₀.₀₅ = 0.587): yes

## Interpretation

The §3.5.1 within-domain transfer finding (Spearman ρ = 0.706) is robust to solubility model choice across the three constructions tested. All three methods produce the same rank correlation (0.706), while the magnitude metrics shift modestly because only the PG/water solubility feature values change.

## Supplementary Table S5

- Rows: 17
- Source counts: `{'PartII_Table1 (aqueous anchor)': 1, 'Manrique log-linear estimate': 8, 'PartII §4.1 (1750× aqueous)': 1, 'PartI_Table1': 5, 'PartII_Table1': 2}`
- The two pure-water rows are retained separately because the PG/water and EtOH/water series use distinct literature sources.

## File hashes

- `outputs/supplementary/table_S5_solubility_values.csv`: `828c6cdee5fa679ddd18246665dfbef2e9e4b0d2117e1315bba84e859eee64bc`
- `outputs/supplementary/note_S1_solubility_sensitivity.json`: `563dc06bbc250ee4dc70d2424c9fffc5839c20d3d7fbf9d5ed37c19bbc727870`
- `outputs/supplementary/note_S1_solubility_sensitivity_predictions.csv`: `b711d659506ff64838d2fb5db7d83667cd83d7de2fe1235d78581aac77ab6272`
- `outputs/phase1_step2_redo/dataset.csv`: `f6434cd1a02995ff85cc0978ec971971a140b7a2897985ecad8c6fadbd74b528`

The report file itself is covered by the deterministic rerun check rather than embedded as a self-referential hash.
