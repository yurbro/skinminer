# E4 Delta: baseline (full_run_13) -> CV-only (E4)

## Overall

| Metric | Baseline (VLM enabled) | E4 (CV-only) | Delta |
|---|---:|---:|---:|
| assembled | 79 | 80 | +1 |
| verified | 4 | 4 | +0 |
| unresolved | 48 | 48 | +0 |
| rejected | 27 | 28 | +1 |

## Figure Pipeline Comparison

| Metric | Baseline | E4 | Delta |
|---|---:|---:|---:|
| figure records | 9 | 10 | +1 |
| digitized_endpoints_ok | 25 | 34 | +9 |
| mapped_curves | 12 | 10 | -2 |
| unmapped_curves | 13 | 24 | +11 |
| vlm_used_as_final | 8 | 0 | -8 |

## Failure Taxonomy Changes

| failure_reason | Baseline | E4 | Delta |
|---|---:|---:|---:|
| ambiguous_api_concentration | 42 | 45 | +3 |
| insufficient_evidence | 54 | 57 | +3 |
| figure_digitization_failed | 8 | 6 | -2 |
| not_target_api_concentration | 10 | 8 | -2 |
| missing_area | 14 | 15 | +1 |
| not_target_study_type | 12 | 13 | +1 |

## Baseline VLM-Final Artifact Fate (8 rows)

| DOI | Figure | Label | Baseline linked final status | E4 final status | E4 route | E4 failure_reason |
|---|---|---|---|---|---|---|
| 10.1021/acs.molpharmaceut.0c00720 | Figure 2 | Dark | no_final_record | no_final_record | none | no_matching_record |
| 10.1021/acs.molpharmaceut.0c00720 | Figure 2 | UV light exposure | no_final_record | no_final_record | none | no_matching_record |
| 10.1248/cpb.c21-00033 | Figure 3 | IL Preparation #2 | unresolved | unresolved | figure | ambiguous_api_concentration |
| 10.1016/j.ijpharm.2016.03.043 | 1 | PG | no_final_record | no_final_record | none | no_matching_record |
| 10.1007/s11095-014-1318-2 | fig2 | 10% w/w | no_final_record | no_final_record | none | no_matching_record |
| 10.1007/s11095-014-1318-2 | fig2 | 20% | no_final_record | no_final_record | none | no_matching_record |
| 10.1007/s11095-014-1318-2 | fig2 | 5% w/w | no_final_record | no_final_record | none | no_matching_record |
| 10.1007/s11095-014-1318-2 | fig2 | placebo | no_final_record | no_final_record | none | no_matching_record |

## Key Observations

- Overall final outcomes were nearly unchanged: assembled 79 -> 80 (+1), verified 4 -> 4 (+0), unresolved 48 -> 48 (+0), rejected 27 -> 28 (+1).
- Disabling VLM removed all final VLM contributions by construction (`vlm_used_as_final` 8 -> 0), but it did not reduce the verified count; the net end-state change was one extra rejected row and one extra assembled/figure row.
- The CV-only figure funnel shifted toward more raw CV output but weaker downstream mapping: digitized endpoints OK 25 -> 34, mapped curves 12 -> 10, unmapped curves 13 -> 24.
- For the 8 baseline artifacts where VLM had been selected as the final figure path, E4 produced no matching final record for 7/8 and produced unresolved figure rows for 1/8; none became verified and none became rejected in the final E4 output.
- Gold-set metrics were unchanged (`precision=1.000`, `recall=0.500`, `F1=0.667`, `end-to-end precision=0.000`), so the current 71-row audit set does not show measurable quality gain from the VLM path either way.