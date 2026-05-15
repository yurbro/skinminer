# Figure Value Error ????

?????11 ?
?????2026-04-05

?????? 11 ????? direct figure digitization error?????`5/11` ? `figure` extractor ?????`6/11` ??? `table` extractor ? shared-hint ??? `figure route` paper ?? record?

---

## Record 1: `record_47710103a12d`

**Paper:** `10.1016/j.ejpb.2020.05.013` | https://pure.hud.ac.uk/ws/files/20412617/for_PURE_3D_diffusion_cell_FULL_Manuscript.pdf
**Route:** `figure` | **Extractor:** `figure`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 261.17059326171875 |
| endpoint_unit | ug |
| endpoint_time_value | 12.0 |
| endpoint_time_unit | hours |
| endpoint_kind | amount_total |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?200 | Original paper Fig. 11(a), p.16 |
| ?? endpoint_unit | ?g/mL | Original paper Fig. 11(a), p.16 |
| ???? | ???? 31%?261.17 vs ~200?????/?????pipeline ?? `ug total`???? `?g/mL` ??? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | trace=figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a; page=14; figure_id=10; subplot=a; has_permeation_plot=True; digitizable=yes; selected_image=outputs\validation_observability_run\figure\triage_images\10.1016_j.ejpb.2020.05.013__p14.jpg |
| calibration | image_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ejpb.2020.05.013__p14.jpg; source_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ejpb.2020.05.013__p14.jpg; x=[0.0, 200.0] ; y=[0.0, 1000.0] ; y_kind=amount_total; q_final=261.17059326171875 |
| digitization | status=ok; endpoint=261.17059326171875  @ 200.0 ; overlay=outputs\validation_observability_run\figure\digitize_overlays\paper_b451e1b601ac__cluster_1.png |
| mapping | mapped_to=5% Ibuprofen Gel; confidence=0.85; status=vision_mapped; rationale=The curve endpoint value aligns with the characteristics of a formulation containing Ibuprofen, specifically the 5% concentration. | zoom_source=digitized_crop |

### Root cause ??
| ?? | ??? |
|---|---|
| figure_misidentified | high |
| unit_mismatch | high |

### ????
Triage ??? p.14 ? Figure 10(a) ???????? p.16 ? Figure 11(a) ?????digitization ????????????/???????? 12 h ? permeation endpoint ???

### Replay artifacts ??
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ejpb.2020.05.013__p9.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ejpb.2020.05.013__p11.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ejpb.2020.05.013__p14.jpg`
- `outputs\validation_observability_run\figure\digitize_crops\figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.png`
- `outputs\validation_observability_run\figure\digitize_masks\figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.png`
- `outputs\validation_observability_run\figure\digitize_overlays\paper_b451e1b601ac__cluster_1.png`
- `outputs\validation_observability_run\figure\mapping_zooms\figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.jpg`

---

## Record 2: `record_cc84e1bf6e4e`

**Paper:** `10.1016/j.ejpb.2020.05.013` | https://pure.hud.ac.uk/ws/files/20412617/for_PURE_3D_diffusion_cell_FULL_Manuscript.pdf
**Route:** `figure` | **Extractor:** `table`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 261.17059326171875 |
| endpoint_unit | ug |
| endpoint_time_value | 12.0 |
| endpoint_time_unit | h |
| endpoint_kind | amount_total |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?200 | Original paper Fig. 11(a), p.16 |
| ?? endpoint_unit | ?g/mL | Original paper Fig. 11(a), p.16 |
| ???? | ?????????? 31%????/????? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | ? record ? record-level triage trace????? paper-level route anchor? |
| calibration | ? record-level digitized curve?value ?? direct figure digitization ??? |
| digitization | ? record-level endpoint row??? value ?? table/shared-hint/text ??? |
| mapping | ? record-level figure mapping??? record ?? direct figure extractor ??? |

### Root cause ??
| ?? | ??? |
|---|---|
| figure_misidentified | high |
| other | medium |

### ????
? record ???? figure trace?`patch_endpoint_value` ?? shared hint ??? `record_47710103a12d` ????? cluster_1 ????? calibration-curve ????????? table-backed record?

### Replay artifacts ??
- `outputs/validation_observability_run/figure/triage_images/10.1016_j.ejpb.2020.05.013__p14.jpg`
- `outputs/validation_observability_run/figure/digitize_crops/figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.png`
- `outputs/validation_observability_run/figure/digitize_masks/figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.png`
- `outputs/validation_observability_run/figure/digitize_overlays/paper_b451e1b601ac__cluster_1.png`
- `outputs/validation_observability_run/figure/mapping_zooms/figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.jpg`

---

## Record 3: `record_e04ec91b3e26`

**Paper:** `10.1016/j.ejpb.2020.05.013` | https://pure.hud.ac.uk/ws/files/20412617/for_PURE_3D_diffusion_cell_FULL_Manuscript.pdf
**Route:** `figure` | **Extractor:** `table`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 261.17059326171875 |
| endpoint_unit | ug |
| endpoint_time_value | 12.0 |
| endpoint_time_unit | h |
| endpoint_kind | amount_total |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?200 | Original paper Fig. 11(a), p.16 |
| ?? endpoint_unit | ?g/mL | Original paper Fig. 11(a), p.16 |
| ???? | ?????????? 31%????/????? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | ? record ? record-level triage trace????? paper-level route anchor? |
| calibration | ? record-level digitized curve?value ?? direct figure digitization ??? |
| digitization | ? record-level endpoint row??? value ?? table/shared-hint/text ??? |
| mapping | ? record-level figure mapping??? record ?? direct figure extractor ??? |

### Root cause ??
| ?? | ??? |
|---|---|
| figure_misidentified | high |
| other | medium |

### ????
? record ???? figure trace??? endpoint ?? misidentified calibration figure ? shared hint????? record ??? endpoint evidence?

### Replay artifacts ??
- `outputs/validation_observability_run/figure/triage_images/10.1016_j.ejpb.2020.05.013__p14.jpg`
- `outputs/validation_observability_run/figure/digitize_crops/figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.png`
- `outputs/validation_observability_run/figure/digitize_masks/figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.png`
- `outputs/validation_observability_run/figure/digitize_overlays/paper_b451e1b601ac__cluster_1.png`
- `outputs/validation_observability_run/figure/mapping_zooms/figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a.jpg`

---

## Record 4: `record_1d882e0e9090`

**Paper:** `10.1016/j.ijpharm.2016.03.043` | https://discovery.ucl.ac.uk/id/eprint/1477393/1/MANUSCRIPTREVISION.pdf
**Route:** `figure` | **Extractor:** `figure`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 36.438011169433594 |
| endpoint_unit | μg/cm² |
| endpoint_time_value | 48.0 |
| endpoint_time_unit | hours |
| endpoint_kind | amount_per_area |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | PG ?32?PEG300 ?16?17 | Original paper Fig. 1(A), p.7, 48 h |
| ?? endpoint_unit | ?g/cm? | Original paper Fig. 1(A), p.7, 48 h |
| ???? | ??????????????36.44 ?? PG ?? 14%??? PEG300 ?? 115%? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | trace=figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f; page=7; figure_id=1; subplot=A; has_permeation_plot=True; digitizable=yes; selected_image=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg |
| calibration | image_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; source_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; x=[0.0, 48.0] hours; y=[0.0, 50.0] μg/cm²; y_kind=amount_total; q_final=36.438011169433594 |
| digitization | status=ok; endpoint=36.438011169433594 μg/cm² @ 48.0 hours; overlay=outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_4.png |
| mapping | mapped_to=Isopropyl alcohol solutions (PEG 300, PG); confidence=0.92; status=vision_mapped; rationale=The endpoint aligns with expectations of isopropyl alcohol solutions, indicating high permeability. | zoom_source=digitized_crop |

### Root cause ??
| ?? | ??? |
|---|---|
| mapping_error | high |
| figure_misidentified | high |

### ????
? record ? formulation label ? PG ? PEG300 ?????????????? Fig. 1(A) ??? 4 ???????? digitization source_path/overlay ?? p.11 ??????? p.7 ?????????????????????

### Replay artifacts ??
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p10.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg`
- `outputs\validation_observability_run\figure\digitize_crops\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_masks\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_4.png`
- `outputs\validation_observability_run\figure\mapping_zooms\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.jpg`

---

## Record 5: `record_339f642dd0cd`

**Paper:** `10.1016/j.ijpharm.2016.03.043` | https://discovery.ucl.ac.uk/id/eprint/1477393/1/MANUSCRIPTREVISION.pdf
**Route:** `figure` | **Extractor:** `figure`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 30.459407806396484 |
| endpoint_unit | μg/cm² |
| endpoint_time_value | 48.0 |
| endpoint_time_unit | hours |
| endpoint_kind | amount_per_area |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?12?13 | Original paper Fig. 1(A), p.7, spray at 48 h |
| ?? endpoint_unit | ?g/cm? | Original paper Fig. 1(A), p.7, spray at 48 h |
| ???? | pipeline ??????? 2.4x? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | trace=figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f; page=7; figure_id=1; subplot=A; has_permeation_plot=True; digitizable=yes; selected_image=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg |
| calibration | image_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; source_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; x=[0.0, 48.0] hours; y=[0.0, 50.0] μg/cm²; y_kind=amount_total; q_final=30.459407806396484 |
| digitization | status=ok; endpoint=30.459407806396484 μg/cm² @ 48.0 hours; overlay=outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_2.png |
| mapping | mapped_to=IBULEVE™ Speed Relief 5% Spray; confidence=0.9; status=vision_mapped; rationale=The higher endpoint suggests better permeation, which aligns with the properties of a spray. | zoom_source=digitized_crop |

### Root cause ??
| ?? | ??? |
|---|---|
| mapping_error | high |
| figure_misidentified | high |

### ????
Figure 1(A) ???? spray ???? pipeline ????? cluster ????? `IBULEVE? Speed Relief 5% Spray`?????? cluster ? overlay/source_path ?? p.11 ??????? mapping ??? source binding ?????

### Replay artifacts ??
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p10.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg`
- `outputs\validation_observability_run\figure\digitize_crops\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_masks\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_2.png`
- `outputs\validation_observability_run\figure\mapping_zooms\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.jpg`

---

## Record 6: `record_437e38b169f5`

**Paper:** `10.1016/j.ijpharm.2016.03.043` | https://discovery.ucl.ac.uk/id/eprint/1477393/1/MANUSCRIPTREVISION.pdf
**Route:** `figure` | **Extractor:** `table`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 90.0 |
| endpoint_unit | µg/cm² |
| endpoint_time_value | 6.0 |
| endpoint_time_unit | h |
| endpoint_kind | amount_per_area |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | PG ?12?PEG300 ?6 | Original paper Fig. 1(A), p.7, 6 h |
| ?? endpoint_unit | ?g/cm? | Original paper Fig. 1(A), p.7, 6 h |
| ???? | 90 ?? PG ?? 7.5x??? PEG300 ?? 15x? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | ? record ? record-level triage trace????? paper-level route anchor? |
| calibration | ? record-level digitized curve?value ?? direct figure digitization ??? |
| digitization | ? record-level endpoint row??? value ?? table/shared-hint/text ??? |
| mapping | ? record-level figure mapping??? record ?? direct figure extractor ??? |

### Root cause ??
| ?? | ??? |
|---|---|
| figure_misidentified | high |
| wrong_timepoint_read | high |

### ????
? record ?? figure extractor ????? figure-route paper ?? table-backed record????? 90 ???????`1 ?L application` ???????????? 6 h ? endpoint????????? figure/experiment context ?????? digitization ???

### Replay artifacts ??
- ? record-level replay artifact

---

## Record 7: `record_982332825448`

**Paper:** `10.1016/j.ijpharm.2016.03.043` | https://discovery.ucl.ac.uk/id/eprint/1477393/1/MANUSCRIPTREVISION.pdf
**Route:** `figure` | **Extractor:** `figure`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 6.261798858642578 |
| endpoint_unit | μg/cm² |
| endpoint_time_value | 48.0 |
| endpoint_time_unit | hours |
| endpoint_kind | amount_per_area |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?10?11 | Original paper Fig. 1(A), p.7, IBUGEL at 48 h |
| ?? endpoint_unit | ?g/cm? | Original paper Fig. 1(A), p.7, IBUGEL at 48 h |
| ???? | pipeline ??????? 0.6x? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | trace=figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f; page=7; figure_id=1; subplot=A; has_permeation_plot=True; digitizable=yes; selected_image=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg |
| calibration | image_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; source_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; x=[0.0, 48.0] hours; y=[0.0, 50.0] μg/cm²; y_kind=amount_total; q_final=6.261798858642578 |
| digitization | status=ok; endpoint=6.261798858642578 μg/cm² @ 48.0 hours; overlay=outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_1.png |
| mapping | mapped_to=IBUGEL™; confidence=0.85; status=vision_mapped; rationale=The endpoint is moderate, consistent with the characteristics of a gel formulation. | zoom_source=digitized_crop |

### Root cause ??
| ?? | ??? |
|---|---|
| figure_misidentified | high |

### ????
Triage trace ??? Fig. 1(A) human skin?? digitization overlay/source_path ??? p.11 ???/????????????????????????????????????????? IBUGEL ???

### Replay artifacts ??
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p10.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg`
- `outputs\validation_observability_run\figure\digitize_crops\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_masks\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_1.png`
- `outputs\validation_observability_run\figure\mapping_zooms\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.jpg`

---

## Record 8: `record_a28c8f99f0f6`

**Paper:** `10.1016/j.ijpharm.2016.03.043` | https://discovery.ucl.ac.uk/id/eprint/1477393/1/MANUSCRIPTREVISION.pdf
**Route:** `figure` | **Extractor:** `table`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 280.0 |
| endpoint_unit | µg/cm² |
| endpoint_time_value | 6.0 |
| endpoint_time_unit | h |
| endpoint_kind | amount_per_area |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?4?5 | Original paper Fig. 1(A), p.7, spray at 6 h |
| ?? endpoint_unit | ?g/cm? | Original paper Fig. 1(A), p.7, spray at 6 h |
| ???? | pipeline ??????? 56?70x? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | ? record ? record-level triage trace????? paper-level route anchor? |
| calibration | ? record-level digitized curve?value ?? direct figure digitization ??? |
| digitization | ? record-level endpoint row??? value ?? table/shared-hint/text ??? |
| mapping | ? record-level figure mapping??? record ?? direct figure extractor ??? |

### Root cause ??
| ?? | ??? |
|---|---|
| figure_misidentified | high |
| wrong_timepoint_read | high |

### ????
280 ?g/cm? ?? paper ? 3 ?L commercial formulations ?????????? Figure 3/????????????????? finite-dose figure-route record????? CV calibration????????/?? figure context ??????? record?

### Replay artifacts ??
- ? record-level replay artifact

---

## Record 9: `record_ca0291b430fe`

**Paper:** `10.1016/j.ijpharm.2016.03.043` | https://discovery.ucl.ac.uk/id/eprint/1477393/1/MANUSCRIPTREVISION.pdf
**Route:** `figure` | **Extractor:** `figure`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 30.490875244140625 |
| endpoint_unit | μg/cm² |
| endpoint_time_value | 48.0 |
| endpoint_time_unit | hours |
| endpoint_kind | amount_per_area |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?12?13 | Original paper Fig. 1(A), p.7, spray at 48 h |
| ?? endpoint_unit | ?g/cm? | Original paper Fig. 1(A), p.7, spray at 48 h |
| ???? | pipeline ??????? 2.4x? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | trace=figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f; page=7; figure_id=1; subplot=A; has_permeation_plot=True; digitizable=yes; selected_image=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg |
| calibration | image_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; source_path=outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg; x=[0.0, 48.0] hours; y=[0.0, 50.0] μg/cm²; y_kind=amount_total; q_final=30.490875244140625 |
| digitization | status=ok; endpoint=30.490875244140625 μg/cm² @ 48.0 hours; overlay=outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_3.png |
| mapping | mapped_to=IBULEVE™ Speed Relief 5% Spray; confidence=0.88; status=vision_mapped; rationale=Similar characteristics to IBULEVE™ Speed Relief based on endpoint. | zoom_source=digitized_crop |

### Root cause ??
| ?? | ??? |
|---|---|
| mapping_error | high |
| figure_misidentified | high |

### ????
? `record_339f642dd0cd` ?????????????? spray ? cluster??? allowed labels ?? 3 ??????? 4 ????????? spray record ?????/???

### Replay artifacts ??
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p10.jpg`
- `outputs\validation_observability_run\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p11.jpg`
- `outputs\validation_observability_run\figure\digitize_crops\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_masks\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png`
- `outputs\validation_observability_run\figure\digitize_overlays\paper_7008480bdcae__cluster_3.png`
- `outputs\validation_observability_run\figure\mapping_zooms\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.jpg`

---

## Record 10: `record_e5a5cd848fa6`

**Paper:** `10.1016/j.ijpharm.2016.03.043` | https://discovery.ucl.ac.uk/id/eprint/1477393/1/MANUSCRIPTREVISION.pdf
**Route:** `figure` | **Extractor:** `table`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 280.0 |
| endpoint_unit | µg/cm² |
| endpoint_time_value | 6.0 |
| endpoint_time_unit | h |
| endpoint_kind | amount_per_area |
| verification_status | verified |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?4?5 | Original paper Fig. 1(A), p.7, IBUGEL at 6 h |
| ?? endpoint_unit | ?g/cm? | Original paper Fig. 1(A), p.7, IBUGEL at 6 h |
| ???? | pipeline ??????? 56?70x? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | ? record ? record-level triage trace????? paper-level route anchor? |
| calibration | ? record-level digitized curve?value ?? direct figure digitization ??? |
| digitization | ? record-level endpoint row??? value ?? table/shared-hint/text ??? |
| mapping | ? record-level figure mapping??? record ?? direct figure extractor ??? |

### Root cause ??
| ?? | ??? |
|---|---|
| figure_misidentified | high |
| wrong_timepoint_read | high |

### ????
??? 280 ???? Fig. 1(A) ? gel ??????? paper ???? 3 ?L commercial-formulation ?????? record ?? route=figure??? value error ??????????????

### Replay artifacts ??
- ? record-level replay artifact

---

## Record 11: `record_c846ed69a806`

**Paper:** `10.1208/s12249-019-1584-8` | https://link.springer.com/content/pdf/10.1208/s12249-019-1584-8.pdf
**Route:** `figure` | **Extractor:** `table`

### Pipeline ??
| ?? | ? |
|---|---|
| endpoint_value | 0.5 |
| endpoint_unit | mg/cm^2 |
| endpoint_time_value | 24.0 |
| endpoint_time_unit | h |
| endpoint_kind | amount_per_area |
| verification_status | unresolved |

### ???????????
| ?? | ? | ????/?/??? |
|---|---|---|
| ?? endpoint_value | ?0.37 | Original paper Fig. 3(a), p.6, ME/Gel at 24 h |
| ?? endpoint_unit | mg/cm? | Original paper Fig. 3(a), p.6, ME/Gel at 24 h |
| ???? | pipeline ? 0.50 mg/cm???? 35%??? formulation concentration ?????? 1% ??? Table I ?? 5% w/w? | ??????/?? |

### Figure ?????
| ?? | ???? |
|---|---|
| triage | ? record ? record-level triage trace????? paper-level route anchor? |
| calibration | ? record-level digitized curve?value ?? direct figure digitization ??? |
| digitization | ? record-level endpoint row??? value ?? table/shared-hint/text ??? |
| mapping | ? record-level figure mapping??? record ?? direct figure extractor ??? |

### Root cause ??
| ?? | ??? |
|---|---|
| other | high |
| figure_misidentified | medium |

### ????
? record ? table extractor ???endpoint evidence ????? Table I ? formulation ?????? permeation endpoint??????? paper ? figure trace ?? p.2 ? Fig. 1 ???/?????? digitizable target????? permeation figure ? p.6 ? Fig. 3(a)?????????????? + figure ???????????

### Replay artifacts ??
- ? record-level replay artifact
