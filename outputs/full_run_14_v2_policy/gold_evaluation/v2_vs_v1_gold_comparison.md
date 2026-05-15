# V2 vs V1 Gold Comparison

The existing 71-row gold audit CSV is figure-heavy and uses post-Fix-5 / V1-style labels. It does not contain a V2-specific `5% w/v` acceptance label, so V2 policy gains are not counted as final true/false positives here. The table below is the comparable existing-label score; V2 true precision requires supplemental annotation.

| Metric | V1 baseline | V2 existing-label comparable | Delta |
|---|---:|---:|---:|
| precision | 1.000 | 1.000 | +0.000 |
| recall | 0.500 | 0.500 | +0.000 |
| F1 | 0.667 | 0.667 | +0.000 |
| scope precision | 1.000 | 1.000 | +0.000 |
| end-to-end precision | 0.000 | 0.000 | +0.000 |
| verified count in scored audit CSV | 7 | 7 | +0 |

## V2 New Verified Coverage

- V2 full-run verified total: `10` (`{'figure': 4, 'table': 6}`).
- New verified vs V1 by record_id: `8`; in existing gold by record_id: `3`; absent by record_id: `5`.
- Policy-relevant table w/v gains: `6`; in existing gold by record_id: `3`; absent by record_id: `3`.
- The 3 policy-gain rows already present by `record_id` have old V1-scope labels and old extracted values (`1% w/v` rows), so they still need V2 re-annotation rather than automatic reuse.
- Supplemental candidate CSV: `outputs\full_run_14_v2_policy\gold_evaluation\v2_supplemental_annotation_candidates.csv`.

## Diagnostic Strict Record-ID Projection

This diagnostic treats old V1 labels as if they applied to V2 and treats missing record IDs as not predicted. It is useful only to expose run-churn and label incompatibility; it is not the reported V2 policy score.

| Metric | Diagnostic V2 on old labels |
|---|---:|
| predicted positives | 5 |
| TP | 2 |
| FP | 3 |
| FN | 12 |
| precision | 0.400 |
| recall | 0.143 |
| F1 | 0.211 |

## Annotation Recommendation

Prioritize the six table `5% w/v` policy-gain records from DOI `10.1208/s12249-013-9995-4`. If the goal is to score all observed V2 additions, also annotate the two new figure-route churn records from DOI `10.1016/j.ijpharm.2016.03.043`.
