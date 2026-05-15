# Literature 24h Data Summary

## Filtering

- Source CSV: `C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\demonstration\literature_permeation_data_full.csv`
- Total records before 24h filtering: `217`
- Raw records within 23-25h: `50`
- Canonical records after record_id dedupe: `9`
- Records used by the default GPR sanity filter (0-1000 ug/cm2): `8`

The default GPR run excludes one extreme 24h value above 1000 ug/cm2 because it is not comparable with the Paper 1 response scale. The excluded record remains in `literature_24h_data.csv` for auditability.

## DOI And Formulation Coverage

| DOI | Records | Formulations |
|---|---:|---|
| `10.1208/s12249-013-9995-4` | 8 | F1, F2, F3, F4, F5, F6, F7, F8 |
| `10.1039/d0ra00100g` | 1 | rac-IBU |

## Response Range

- Paper 1 24h mean range: `178.813 to 283.258 ug/cm2`
- Literature 24h canonical range, including audit outlier: `193.594 to 302840.000 ug/cm2`
- Literature 24h default GPR range: `193.594 to 487.969 ug/cm2`
- 24h response ranges overlap after sanity filtering: `yes`

## Membrane Types In Default GPR Literature Set

| Membrane type | Records |
|---|---:|
| `dermatomed porcine skin; human skin` | 8 |

## Interpretation

The 24h intersection is materially better than the earlier 28h setup because both Paper 1 and SkinMiner literature records now share an ibuprofen Franz-cell cumulative amount endpoint at the same timepoint.
The main residual mismatch is still formulation domain and membrane domain: Paper 1 uses Poloxamer 407 / ethanol / propylene glycol on Strat-M, while the usable literature block is porcine skin formulations from one paper.
