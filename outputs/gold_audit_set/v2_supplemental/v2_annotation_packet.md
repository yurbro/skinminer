# Gold Set Annotation Packet - V2 Supplemental

Supplemental annotation packet for 8 V2 full-run verified records that require human review before final V2 precision can be computed.

Source candidates: `outputs/full_run_14_v2_policy/gold_evaluation/v2_supplemental_annotation_candidates.csv`.
Target CSV to fill: `outputs/gold_audit_set/v2_supplemental/v2_annotation_candidates.csv`.

## Annotation Schema

Use the same yes/no/uncertain convention as round 1. New field: `gold_wv_basis_acceptable` records whether the w/v concentration basis is scientifically acceptable for the V2 policy target. For non-w/v rows, use `n_a` or leave a note if uncertain.

| Field | Allowed values | Meaning |
|---|---|---|
| gold_target_api_ok | yes / no / uncertain | Fill by human annotator. |
| gold_5pct_ww_ok | yes / no / uncertain | Fill by human annotator. |
| gold_wv_basis_acceptable | yes / no / uncertain / n_a | Fill by human annotator. |
| gold_franz_ok | yes / no / uncertain | Fill by human annotator. |
| gold_ivpt_ivrt_ok | yes / no / uncertain | Fill by human annotator. |
| gold_amount_endpoint_ok | yes / no / uncertain | Fill by human annotator. |
| gold_endpoint_time_ok | yes / no / uncertain | Fill by human annotator. |
| gold_endpoint_value_correct | yes / no / uncertain / approximate | Fill by human annotator. |
| gold_area_ok | yes / no / uncertain | Fill by human annotator. |
| gold_keep_record | yes / no / uncertain | Fill by human annotator. |
| gold_notes | free text | Fill by human annotator. |
| gold_scope_correct | yes / no / uncertain | Fill by human annotator. |
| gold_value_correct | yes / no / uncertain / approximate | Fill by human annotator. |

---

## Paper 1: 10.1208/s12249-013-9995-4

**Paper ID:** `paper_48cbfe0b170b`

**Paper URL:** https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3755145

**Route(s) in this paper:** table

**Status(es) in this paper:** verified

**Supplemental records in this paper:** 6

### Record 1/6: `record_851ab860659f`

| Field | Pipeline value |
|---|---|
| route | table |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | F2 |
| api_name | Ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/v |
| api_basis | w/v |
| endpoint_kind | amount_total |
| endpoint_value | 1178.9 |
| endpoint_unit | μg |
| endpoint_time_value | 48 |
| endpoint_time_unit | h |
| device | Franz diffusion cell |
| study_type | both |
| diffusion_area_cm2 | 0.64 |
| existing_gold_record_id | yes |
| existing_gold_keep_record | no |
| policy_gain | yes |
| supplemental_reason | present_in_gold_but_v1_label_not_v2_applicable |

**Evidence preview:**

> [formulation; Table 2] Drug content = 96.0, Flux μg/cm2/h = 29.7
> [endpoint; Table 2] Drug content = 96.0, Flux μg/cm2/h = 29.7
> [device; BLOCK 102] BLOCK 102
> [area; verify:area] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [receptor_volume; verify:receptor_volume] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [api_concentration; verify:api_concentration] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---

### Record 2/6: `record_8b2e8239ff2b`

| Field | Pipeline value |
|---|---|
| route | table |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | N2 |
| api_name | Ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/v |
| api_basis | w/v |
| endpoint_kind | amount_total |
| endpoint_value | 1178.9 |
| endpoint_unit | μg |
| endpoint_time_value | 72 |
| endpoint_time_unit | h |
| device | Franz diffusion cell |
| study_type | both |
| diffusion_area_cm2 | 0.64 |
| existing_gold_record_id | no |
| existing_gold_keep_record |  |
| policy_gain | yes |
| supplemental_reason | not_in_gold_policy_gain |

**Evidence preview:**

> [formulation; Table 2] Mean PS (nm) = 320.7, PDI = 0.236
> [endpoint; Table 2] Mean PS (nm) = 320.7, PDI = 0.236
> [device; BLOCK 102] BLOCK 102
> [area; verify:area] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [receptor_volume; verify:receptor_volume] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [api_concentration; verify:api_concentration] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---

### Record 3/6: `record_9d98bd27f9f7`

| Field | Pipeline value |
|---|---|
| route | table |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | F3 |
| api_name | Ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/v |
| api_basis | w/v |
| endpoint_kind | amount_total |
| endpoint_value | 759.6 |
| endpoint_unit | μg |
| endpoint_time_value | 72 |
| endpoint_time_unit | h |
| device | Franz diffusion cell |
| study_type | both |
| diffusion_area_cm2 | 0.64 |
| existing_gold_record_id | yes |
| existing_gold_keep_record | no |
| policy_gain | yes |
| supplemental_reason | present_in_gold_but_v1_label_not_v2_applicable |

**Evidence preview:**

> [formulation; Table 2] Drug content = 98.5, Flux μg/cm2/h = 19.3
> [endpoint; Table 2] Drug content = 98.5, Flux μg/cm2/h = 19.3
> [device; BLOCK 102] BLOCK 102
> [area; verify:area] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [receptor_volume; verify:receptor_volume] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [api_concentration; verify:api_concentration] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---

### Record 4/6: `record_ace3746b1600`

| Field | Pipeline value |
|---|---|
| route | table |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | F1 |
| api_name | Ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/v |
| api_basis | w/v |
| endpoint_kind | amount_total |
| endpoint_value | 1142.4 |
| endpoint_unit | μg |
| endpoint_time_value | 24 |
| endpoint_time_unit | h |
| device | Franz diffusion cell |
| study_type | both |
| diffusion_area_cm2 | 0.64 |
| existing_gold_record_id | yes |
| existing_gold_keep_record | no |
| policy_gain | yes |
| supplemental_reason | present_in_gold_but_v1_label_not_v2_applicable |

**Evidence preview:**

> [formulation; Table 2] Drug content = 96.4, Flux μg/cm2/h = 26.0
> [endpoint; Table 2] Drug content = 96.4, Flux μg/cm2/h = 26.0
> [device; BLOCK 102] BLOCK 102
> [area; verify:area] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [receptor_volume; verify:receptor_volume] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [api_concentration; verify:api_concentration] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---

### Record 5/6: `record_e8222f4e4c6c`

| Field | Pipeline value |
|---|---|
| route | table |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | N1 |
| api_name | Ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/v |
| api_basis | w/v |
| endpoint_kind | amount_total |
| endpoint_value | 1142.4 |
| endpoint_unit | μg |
| endpoint_time_value | 72 |
| endpoint_time_unit | h |
| device | Franz diffusion cell |
| study_type | both |
| diffusion_area_cm2 | 0.64 |
| existing_gold_record_id | no |
| existing_gold_keep_record |  |
| policy_gain | yes |
| supplemental_reason | not_in_gold_policy_gain |

**Evidence preview:**

> [formulation; Table 2] Mean PS (nm) = 396.8, PDI = 0.212
> [endpoint; Table 2] Mean PS (nm) = 396.8, PDI = 0.212
> [device; BLOCK 102] BLOCK 102
> [area; verify:area] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [receptor_volume; verify:receptor_volume] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [api_concentration; verify:api_concentration] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---

### Record 6/6: `record_f4fb84fa1eb7`

| Field | Pipeline value |
|---|---|
| route | table |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | N3 |
| api_name | Ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/v |
| api_basis | w/v |
| endpoint_kind | amount_total |
| endpoint_value | 759.6 |
| endpoint_unit | μg |
| endpoint_time_value | 72 |
| endpoint_time_unit | h |
| device | Franz diffusion cell |
| study_type | both |
| diffusion_area_cm2 | 0.64 |
| existing_gold_record_id | no |
| existing_gold_keep_record |  |
| policy_gain | yes |
| supplemental_reason | not_in_gold_policy_gain |

**Evidence preview:**

> [formulation; Table 2] Mean PS (nm) = 344.6, PDI = 0.245
> [endpoint; Table 2] Mean PS (nm) = 344.6, PDI = 0.245
> [device; BLOCK 102] BLOCK 102
> [area; verify:area] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [receptor_volume; verify:receptor_volume] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.
> [api_concentration; verify:api_concentration] The skin was stored at −80°C. Prior to each permeation experiment; the skins were allowed to thaw at room temperature. After washing and equilibration with PBS, the skin was mounted on static vertical Franz Diffusion cells—Permegear Inc., Bethlehem, PA (receptor volume 5.1 ml, donor area 0.64 cm 2 ) by clamping them between the donor and receptor compartments. The receptor compartment was filled with PBS (pH 7.4) and maintained at 37 ± 0.5°C with constant stirring at 600 RPM. Formulations were added to the donor compartment as an infinite dose to completely cover the membrane surface. Receptor samples were collected at predetermined time points and then replaced with equivalent amount of buffer. The drug content in the samples was analyzed by HPLC.

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---

## Paper 2: 10.1016/j.ijpharm.2016.03.043

**Paper ID:** `paper_7008480bdcae`

**Paper URL:** papers\pdf\10.1016_j.ijpharm.2016.03.043__d92e739f32.pdf

**Route(s) in this paper:** figure

**Status(es) in this paper:** verified

**Supplemental records in this paper:** 2

### Record 1/2: `record_8ad9e33e54f0`

| Field | Pipeline value |
|---|---|
| route | figure |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | IBULEVE™ Speed Relief 5% Spray |
| api_name | ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/w |
| api_basis | w/w |
| endpoint_kind | amount_per_area |
| endpoint_value | 42 |
| endpoint_unit | μg/cm² |
| endpoint_time_value | 48 |
| endpoint_time_unit | hours |
| device | Franz diffusion cell |
| study_type | IVPT |
| diffusion_area_cm2 | 1 |
| existing_gold_record_id | no |
| existing_gold_keep_record |  |
| policy_gain | no |
| supplemental_reason | not_in_gold_run_churn |

**Evidence preview:**

> [formulation; Table 2] At 48 h, maximum ibuprofen permeation in human skin ranged from 11–38 µg/cm2
> [endpoint; Table 2] At 48 h, maximum ibuprofen permeation in human skin ranged from 11–38 µg/cm2
> [endpoint; 1 p.7] vlm_label=IBULEVE™ Speed Relief 5% Spray; legend=▴; quality_flags=
> [device; PAGE 5] PAGE 5
> [api_concentration; verify:api_concentration] 2 Abstract 30 Human skin remains the membrane of choice when conducting in vitro studies to determine 31 dermal penetration of active pharmaceutical ingredients or xenobiotics. However there are ethical and 32 safety issues associated with obtaining human tissue. For these reasons synthetic membranes, cell 33 culture models or in silico predictive algorithms have been researched intensively as alternative 34 approaches to predict dermal exposure in man. Porcine skin has also been recommended as an 35 acceptable surrogate for topical or transdermal delivery research. Here we examine the in vitro 36 permeation of a model active, ibuprofen, using human or porcine skin, as well as the Parallel Artificial 37 Membrane Permeation Assay (PAMPA) model and silicone membrane. Finite dose studies were 38 conducted in all models using commercial ibuprofen formulations and simple volatile ibuprofen 39 ...
> [endpoint_time; verify:endpoint_time] 9 amounts of ibuprofen permeated through silicone membrane from the commercial gel formulation at 4 197 and 6 h compared with all other formulations (p<0.05). 198 Figure 3 shows cumulative amounts of drug and percentages permeated for three different 199 doses (1, 3 and 30 µL) of all formulations evaluated in the PAMPA model. 200 201

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---

### Record 2/2: `record_8b7dd5d8bd7f`

| Field | Pipeline value |
|---|---|
| route | figure |
| verification_status | verified |
| failure_reasons |  |
| scope_tags |  |
| formulation_label | IBUGEL™ |
| api_name | ibuprofen |
| api_concentration_value | 5 |
| api_concentration_unit | % w/w |
| api_basis | w/w |
| endpoint_kind | amount_per_area |
| endpoint_value | 3 |
| endpoint_unit | μg/cm² |
| endpoint_time_value | 48 |
| endpoint_time_unit | hours |
| device | Franz diffusion cell |
| study_type | IVPT |
| diffusion_area_cm2 | 1 |
| existing_gold_record_id | no |
| existing_gold_keep_record |  |
| policy_gain | no |
| supplemental_reason | not_in_gold_run_churn |

**Evidence preview:**

> [formulation; Table 2] At 48 h, maximum ibuprofen permeation in human skin ranged from 11–38 µg/cm2
> [endpoint; Table 2] At 48 h, maximum ibuprofen permeation in human skin ranged from 11–38 µg/cm2
> [endpoint; 1 p.7] vlm_label=IBUGEL™; legend=◻; quality_flags=
> [device; PAGE 5] PAGE 5
> [api_concentration; verify:api_concentration] 2 Abstract 30 Human skin remains the membrane of choice when conducting in vitro studies to determine 31 dermal penetration of active pharmaceutical ingredients or xenobiotics. However there are ethical and 32 safety issues associated with obtaining human tissue. For these reasons synthetic membranes, cell 33 culture models or in silico predictive algorithms have been researched intensively as alternative 34 approaches to predict dermal exposure in man. Porcine skin has also been recommended as an 35 acceptable surrogate for topical or transdermal delivery research. Here we examine the in vitro 36 permeation of a model active, ibuprofen, using human or porcine skin, as well as the Parallel Artificial 37 Membrane Permeation Assay (PAMPA) model and silicone membrane. Finite dose studies were 38 conducted in all models using commercial ibuprofen formulations and simple volatile ibuprofen 39 ...
> [endpoint_time; verify:endpoint_time] 9 amounts of ibuprofen permeated through silicone membrane from the commercial gel formulation at 4 197 and 6 h compared with all other formulations (p<0.05). 198 Figure 3 shows cumulative amounts of drug and percentages permeated for three different 199 doses (1, 3 and 30 µL) of all formulations evaluated in the PAMPA model. 200 201

**Annotation fields:**

| Annotation field | Value |
|---|---|
| gold_target_api_ok |  |
| gold_5pct_ww_ok |  |
| gold_wv_basis_acceptable |  |
| gold_franz_ok |  |
| gold_ivpt_ivrt_ok |  |
| gold_amount_endpoint_ok |  |
| gold_endpoint_time_ok |  |
| gold_endpoint_value_correct |  |
| gold_area_ok |  |
| gold_keep_record |  |
| gold_notes |  |
| gold_scope_correct |  |
| gold_value_correct |  |

---
