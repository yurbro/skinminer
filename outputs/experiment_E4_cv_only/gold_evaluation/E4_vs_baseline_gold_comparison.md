# E4 vs Baseline Gold Comparison

| Metric | Baseline | E4 (CV-only) | Delta | Note |
|---|---:|---:|---:|---|
| scope precision | 1.000 | 1.000 | +0.000 | Verified rows satisfying all strict scope gates under gold audit. |
| end-to-end precision | 0.000 | 0.000 | +0.000 | Verified rows whose values are gold-correct or approximate. |
| recall | 0.500 | 0.500 | +0.000 | Gold keep=yes rows recovered as verified. |
| F1 | 0.667 | 0.667 | +0.000 | Harmonic mean of precision and recall. |
| verified count | 7 | 7 | 0 | Audit rows predicted as verified. |
| value_correct = yes/approximate | 0 | 0 | 0 | Verified rows with gold-correct or approximate endpoint values. |

## Baseline VLM-Final Artifact Fate (8 rows)

| DOI | Figure | Label | Baseline linked final status | E4 final status | E4 route | E4 failure_reason | Note |
|---|---|---|---|---|---|---|---|
| 10.1021/acs.molpharmaceut.0c00720 | Figure 2 | Dark | no_final_record | no_final_record | none | no_matching_record | No matching final record in E4. |
| 10.1021/acs.molpharmaceut.0c00720 | Figure 2 | UV light exposure | no_final_record | no_final_record | none | no_matching_record | No matching final record in E4. |
| 10.1248/cpb.c21-00033 | Figure 3 | IL Preparation #2 | unresolved | unresolved | figure | ambiguous_api_concentration | Matched by paper_id + formulation.label. |
| 10.1016/j.ijpharm.2016.03.043 | 1 | PG | no_final_record | no_final_record | none | no_matching_record | No matching final record in E4. |
| 10.1007/s11095-014-1318-2 | fig2 | 10% w/w | no_final_record | no_final_record | none | no_matching_record | No matching final record in E4. |
| 10.1007/s11095-014-1318-2 | fig2 | 20% | no_final_record | no_final_record | none | no_matching_record | No matching final record in E4. |
| 10.1007/s11095-014-1318-2 | fig2 | 5% w/w | no_final_record | no_final_record | none | no_matching_record | No matching final record in E4. |
| 10.1007/s11095-014-1318-2 | fig2 | placebo | no_final_record | no_final_record | none | no_matching_record | No matching final record in E4. |

## Interpretation

- The audited gold metrics are numerically identical to the post-Fix-5 baseline.
- `vlm_used_as_final` changed from 8 to 0, but the 71-row gold audit did not move on precision, recall, F1, or end-to-end precision.
- Under paper+label matching, 7/8 baseline VLM-final artifacts no longer yield any final E4 record, while 1/8 still survive as unresolved figure rows.