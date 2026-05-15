# Figure Branch Diagnosis for Full Run 15

Date: 2026-04-12

Scope: diagnostic only. No code changes were made.

## 1. Route-Level Caveat

`route=figure` is not equivalent to `provenance.extractor_name=figure`.

| run | figure-route verified | extractor=table | extractor=figure | VLM-produced verified |
| --- | ---: | ---: | ---: | ---: |
| full_run_13_post_fix5 | 4 | 4 | 0 | 0 |
| full_run_15_schema_table_fix | 9 | 5 | 4 | 0 |

The apparent increase from 4 to 9 is therefore not a pure figure-branch precision improvement. It is a mixed effect of table extraction, assembly, patching, and CV figure extraction.

Record-id comparison is also unstable: only `record_e5a5cd848fa6` is common between the two runs. Full_run15 adds 8 new figure-route verified record IDs and drops 3 old ones, yielding a net +5.

## 2. Figure Verified Increment

All 9 full_run15 figure-route verified records come from one paper:

`10.1016/j.ijpharm.2016.03.043`

Original paper check:

The paper's Figure 1 reports cumulative ibuprofen permeation for human skin (A), porcine skin (B), silicone (C), and PAMPA 1 uL/cm2 (D). The text states that after 6 h, silicone and PAMPA are about 140 ug/cm2, porcine/human maxima are about 80/40 ug/cm2, and PG is significantly higher in human skin. Figure 3 reports PAMPA dose experiments; the text states that for 3 uL commercial formulations, about 280 ug/cm2 permeated at 6 h.

| record_id | extractor/path | formulation | pipeline endpoint | record-level value verdict | reason |
| --- | --- | --- | --- | --- | --- |
| record_e5a5cd848fa6 | table + patch shared hint | IBUGEL | 280 ug/cm2 @ 10 min | incorrect | 280 ug/cm2 is a 6 h PAMPA/Figure 3 narrative value, while 10 min is copied from analytical/HPLC context. |
| record_2b009f46d9d5 | table + CV shared hint | IBULEVE Speed Relief | 23.28 ug/cm2 @ 10 min | incorrect | Endpoint value is copied from a Figure 1A CV cluster, but endpoint time is an unrelated 10 min method context. |
| record_9e8b3aa49269 | table + CV shared hint | Ibuprofen Solution (Isopropyl Alcohol) | 13.24 ug/cm2 @ 10 min | incorrect | Same endpoint/time mismatch; formulation label is under-specified for PG vs PEG formulation. |
| record_b6963719efff | table + CV shared hint | Ibuprofen Solution (PEG 300) | 16.18 ug/cm2 @ 10 min | incorrect | Numeric value may be plausible for Figure 1A PEG 300 at 48 h, but the record time is wrong. |
| record_e606e9d0847c | table | IBUGEL | 280 ug/cm2 @ 6 h | not acceptable as record-level correct | 280 ug/cm2 is a narrative summary for commercial formulations in PAMPA dose studies, not a grounded formulation-specific Figure 1 endpoint; condition fields conflict with the cited Figure 1 context. |
| record_fb1af90cc9e4 | CV digitization + curve mapping | IBUGEL | 21.45 ug/cm2 @ 48 h | uncertain numeric, incorrect context | The selected page/subplot is Figure 1A, but condition grounding says PAMPA/finite dose; mapping omits the PG formulation as a first-class label. |
| record_b073c5f64b07 | CV digitization + curve mapping | IBULEVE Speed Relief | 23.28 ug/cm2 @ 48 h | likely incorrect | Prior gold notes put the spray endpoint around 12-13 ug/cm2; current mapping assigns a higher CV cluster to IBULEVE. |
| record_a93a374c2f20 | CV digitization + curve mapping | Ibuprofen Solution (Isopropyl Alcohol) | 13.24 ug/cm2 @ 48 h | incorrect or under-grounded | Original paper has two isopropyl-alcohol solutions, PG and PEG 300. The record label does not preserve which one this is; PG should be the higher human-skin curve. |
| record_9b88081c5362 | CV digitization + curve mapping | Ibuprofen Solution (PEG 300) | 16.18 ug/cm2 @ 48 h | numerically plausible, context incorrect | Value is plausible for Figure 1A PEG 300, but condition grounding still says PAMPA/finite-dose context rather than human skin Figure 1A. |

Strict record-level conclusion: none of the 9 should be treated as clean verified figure endpoints without correction. If annotation is endpoint-numeric-only, `record_9b88081c5362` and possibly `record_fb1af90cc9e4` need human confirmation rather than automatic `no`.

## 3. Cause of the Verified Increase

The net +5 verified count is mostly not caused by better figure value extraction.

Evidence:

| signal | full_run13 | full_run15 | interpretation |
| --- | ---: | ---: | --- |
| figure-route verified | 4 | 9 | Net +5. |
| actual figure-extractor verified | 0 | 4 | New CV records from Figure 1A. |
| table-derived figure-route verified | 4 | 5 | Table/patcher still contributes most verified count. |
| VLM-produced verified | 0 | 0 | VLM signal did not become verified records. |
| mapping failures | 13 underconstrained | 0 | Table label space improved grounding. |
| source-label-space VLM grounding | 3/26 | 16/24 | Table label context improved. |

Interpretation: table/schema changes improved label-space availability, reducing underconstrained mapping. However, final verified count still contains table-derived shared-hint contamination and CV mapping/context errors. LLM randomness may affect which pages/routes are selected, but the stronger label-space metrics point to a real table-extraction/grounding effect rather than pure randomness.

## 4. Figure Unresolved Failure Distribution

Primary `failure_reason` among figure-route unresolved:

| failure_reason | full_run13 | full_run15 | delta |
| --- | ---: | ---: | ---: |
| ambiguous_api_concentration | 11 | 20 | +9 |
| insufficient_evidence | 8 | 14 | +6 |
| not_target_api_concentration | 4 | 8 | +4 |
| missing_endpoint | 1 | 7 | +6 |
| unit_normalization_failed | 1 | 0 | -1 |

All failure codes among figure-route unresolved:

| failure_code | full_run13 | full_run15 | delta |
| --- | ---: | ---: | ---: |
| missing_endpoint | 2 | 12 | +10 |
| missing_api_concentration | 0 | 7 | +7 |
| missing_area | 2 | 9 | +7 |
| not_target_api_concentration | 4 | 10 | +6 |
| figure_digitization_failed | 2 | 7 | +5 |
| unit_normalization_failed | 1 | 6 | +5 |
| ambiguous_api_concentration | 16 | 20 | +4 |
| insufficient_evidence | 10 | 14 | +4 |
| percent_only | 2 | 0 | -2 |

The largest DOI contributors in full_run15 are:

| DOI | figure unresolved |
| --- | ---: |
| 10.1248/cpb.c21-00033 | 18 |
| 10.1208/s12249-019-1584-8 | 8 |
| 10.1016/j.ejpb.2020.05.013 | 7 |
| 10.3390/membranes12080762 | 7 |
| 10.1021/acs.molpharmaceut.0c00720 | 5 |

## 5. VLM Path Performance

| metric | full_run13 | full_run15 | delta |
| --- | ---: | ---: | ---: |
| vlm_readings_total | 26 | 24 | -2 |
| vlm_readings_readable | 21 | 18 | -3 |
| vlm_used_as_final | 8 | 13 | +5 |
| figure_records produced from VLM | 1/9 | 9/16 | +8 records |
| VLM-produced verified | 0 | 0 | 0 |

Reconciliation status:

| reconciliation_status | full_run13 | full_run15 |
| --- | ---: | ---: |
| vlm_only | 8 | 13 |
| cv_only | 9 | 3 |
| cv_vlm_disagreement | 4 | 2 |
| unreadable | 5 | 6 |

Grounding status:

| grounding_status | full_run13 | full_run15 |
| --- | ---: | ---: |
| source_label_space | 3 | 16 |
| figure_label_space + figure_label_space_only | 10 | 5 |
| ungrounded | 7 | 3 |
| none | 6 | 0 |

Label grounding improved materially after the table/schema changes: source-label-space grounding rose from 11.5% to 66.7%, and ungrounded fell from 26.9% to 12.5%. However, this did not improve verified VLM output yet because the VLM outputs are either not selected for final verified records or remain blocked by non-value gates.

For `10.1016/j.ijpharm.2016.03.043`, VLM read Figure 1A as IBUGEL 40, IBULEVE 30, PG 25, PEG 300 20 ug/cm2 at 48 h. Those VLM values were not the final verified figure records; the verified actual figure records used CV curve values instead.

## 6. Current Figure Value Error vs Previous 11-Record Diagnosis

Previous 11-record diagnosis:

| root cause | count |
| --- | ---: |
| figure_misidentified | 7 |
| mapping_error | 3 |
| other | 1 |

Current full_run15 figure-route verified diagnosis:

| root cause | count | affected records |
| --- | ---: | --- |
| table/shared-hint source-context contamination | 5 | record_e5a5cd848fa6, record_2b009f46d9d5, record_9e8b3aa49269, record_b6963719efff, record_e606e9d0847c |
| CV curve-to-label / formulation grounding error | 4 | record_fb1af90cc9e4, record_b073c5f64b07, record_a93a374c2f20, record_9b88081c5362 |
| condition binding error | 9 | all 9 records have human-skin/PAMPA/dose/time context leakage or ambiguity |
| VLM signal not consumed | 4 direct figure records | VLM produced alternative readings for Figure 1A, but final verified records use CV values |

The error profile shifted. The earlier broad figure/page misidentification is reduced for the IJPharm paper: full_run15 selects Figure 1A page 7 correctly. The remaining problem is downstream binding: label mapping, condition binding, and table/patcher shared-hint contamination.

## 7. Fix 3b Potential Benefit

Calibration-gate cases in full_run15:

| DOI | primary selected figure | gate | same-paper permeation figure exists? | current records affected | conservative recoverable records |
| --- | --- | --- | --- | ---: | ---: |
| 10.1016/j.ejpb.2020.05.013 | Figure 10, page 14 | calibration_curve_not_target | yes, Figure 11(a) reports average IBU amount permeated vs time | 7 unresolved figure-route records | 1 clean figure endpoint record |

This is the same calibration-gate paper as full_run13. The same paper has Figure 11(a), a real permeation profile. A retry mechanism that rejects calibration Figure 10 and selects Figure 11(a) should recover at least one clean figure endpoint for the 5% w/w ibuprofen gel at 12 h. The 7 current full_run15 unresolved rows are inflated by table extraction of method/calibration time points; counting all 7 as recoverable would overstate the benefit unless the pipeline explicitly supports multi-timepoint figure extraction from the permeation profile.

## 8. Top-3 Figure Improvement Directions

1. Add record-level source binding and anti-contamination guards before verification.
   Do not allow table-route records to become figure-route verified via shared figure hints unless endpoint value, endpoint time, formulation, membrane/barrier, and dose come from the same figure/subplot context.

2. Fix figure label and condition grounding before improving numeric digitization.
   Full_run15 reduced underconstrained mapping, but still dropped or merged PG/PEG labels and assigned PAMPA/dose context to human-skin Figure 1A endpoints. The next precision gain is label/context correctness, not more CV smoothing.

3. Implement calibration-gate retry as a narrow recall fix.
   It applies to 1 paper in full_run15 and can likely recover 1 clean figure endpoint from Figure 11(a). This is useful but lower priority than source binding because it improves recall, while current verified records still contain precision errors.

