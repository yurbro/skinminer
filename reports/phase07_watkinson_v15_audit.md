# Phase 0.7 Watkinson v1.5 Verified Records Audit

Date: 2026-05-10

## Executive Summary

Overall audit verdict: **RED**.

The v1.5 deterministic Watkinson forward run has the expected 47 verified records and the expected per-paper and per-table counts. J mean extraction for the 28 silicone occluded standard-protocol ground-truth rows passes 28/28 within +/-2%; J SD passes 27/28 within +/-5%.

The records are **not modelling-ready by strict current fields**. The actual `occlusion` field is `unknown` for all 47 records, so main-task coverage is 0/28 even though table matching and flux extraction are largely correct. Structured formulation components are also absent from `formulation.components`; this audit reconstructs composition deterministically from `formulation.label` plus table context for reporting and the master CSV.

## 1. Per-Paper Distribution

| DOI | Expected | Actual | Match |
| --- | --- | --- | --- |
| 10.1159/000183922 (Part I) | 13 | 13 | PASS |
| 10.1159/000231528 (Part II) | 20 | 20 | PASS |
| 10.1159/000315139 (Part III) | 14 | 14 | PASS |
| Total | 47 | 47 | PASS |

## 2. Per-Table Distribution

Source table was recoverable from `provenance.metadata.table_id` for 47/47 records.

| Paper | DOI | Source table | Description | Expected | Actual | Match |
| --- | --- | --- | --- | --- | --- | --- |
| Part I | 10.1159/000183922 | Table 3 | silicone, EtOH:water, occluded, untreated | 5 | 5 | PASS |
| Part I | 10.1159/000183922 | Table 4 | silicone, EtOH:water, occluded, ethanol-pretreated | 3 | 3 | PASS |
| Part I | 10.1159/000183922 | Table 5 | human epidermis, EtOH:water, occluded | 5 | 5 | PASS |
| Part II | 10.1159/000231528 | Table 2 | silicone, PG:water, occluded | 10 | 10 | PASS |
| Part II | 10.1159/000231528 | Table 3 | silicone, EtOH:PG:water, occluded | 2 | 2 | PASS |
| Part II | 10.1159/000231528 | Table 4 | silicone, EtOH:PG:water, non-occluded | 2 | 2 | PASS |
| Part II | 10.1159/000231528 | Table 5 | human epidermis, PG:water, occluded | 4 | 4 | PASS |
| Part II | 10.1159/000231528 | Table 6 | human epidermis, EtOH:PG:water, occluded | 2 | 2 | PASS |
| Part III | 10.1159/000315139 | Table 3 | silicone, MO/MG, occluded | 11 | 11 | PASS |
| Part III | 10.1159/000315139 | Table 4 | human epidermis, MO/MG, occluded | 3 | 3 | PASS |

Per-table distribution match count: **10/10**.

## 3. Composition Parsing

Field discovery before parsing:

| Field/search result | Count |
| --- | --- |
| formulation.label_nonempty | 47 |
| formulation.components_nonempty | 0 |
| formulation.composition_present | 0 |
| formulation.notes_nonempty | 0 |
| conditions.notes_nonempty | 0 |
| provenance.metadata.table_id_present | 47 |
| vehicle_context_in_evidence_snippets | 47 |

No record has non-empty `formulation.components` or an explicit structured composition object. The parse below uses the ratio in `formulation.label` and the solvent family implied by `(doi, source_table)`; vehicle context is present in table/evidence snippets.

| Paper | Table | Vehicle | Record found | Parsed components | Expected | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| Part I | Table 3 | 0:100 | record_2abb314c7b9a | ethanol_vv=0, water_vv=100 | ethanol_vv=0, water_vv=100 | PASS |
| Part I | Table 3 | 100:0 | record_3a82944abc56 | ethanol_vv=100, water_vv=0 | ethanol_vv=100, water_vv=0 | PASS |
| Part II | Table 2 | 70:30 | record_bc629b7ee4f2 | PG_vv=70, water_vv=30 | PG_vv=70, water_vv=30 | PASS |
| Part II | Table 3 | 25:25:50 | record_6b4ab72b9a59 | ethanol_vv=25, PG_vv=25, water_vv=50 | ethanol_vv=25, PG_vv=25, water_vv=50 | PASS |
| Part II | Table 3 | 50:25:25 | record_073219db157b | ethanol_vv=50, PG_vv=25, water_vv=25 | ethanol_vv=50, PG_vv=25, water_vv=25 | PASS |
| Part III | Table 3 | 60/40 | record_00cea63f02f2 | MO_vv=60, MG_vv=40 | MO_vv=60, MG_vv=40 | PASS |

Composition anchors: **6/6** parsed correctly; binary anchors **4/4**, ternary anchors **2/2**.

## 4. Coverage Ratio

Coverage uses the normalized audit barrier (`conditions.membrane_type` and source table) because the top-level `barrier` field is route-level and ambiguous in this batch. Occlusion is not inferred; it is the strict record value.

| Metric | Value | Meaning |
| --- | --- | --- |
| n_silicone | 33 | criterion 1 pass after audit barrier normalization |
| n_silicone_occluded | 0 | criteria 1+2 pass; strict record occlusion only |
| n_with_flux_endpoint | 0 | criteria 1+2+3 pass |
| n_with_flux_unit | 0 | criteria 1+2+3+4 pass |
| n_modelling_ready | 0 | all five criteria pass |
| coverage_ratio | 0/28 = 0.000 | PASS if >= 0.93 |

Independent of the failed occlusion gate, 47/47 records have a flux endpoint and 47/47 have a flux-equivalent unit.

Barrier field discovery:

| Top-level barrier value | Count |
| --- | --- |
| human skin | 33 |
| silicone membrane and human skin | 14 |

| conditions.membrane_type value | Count |
| --- | --- |
| silicone membrane | 33 |
| human epidermis | 14 |

## 5. Occlusion Field Distribution

| Value | Count | Expected |
| --- | --- | --- |
| occluded | 0 | 42 |
| non_occluded | 0 | 2 |
| pretreated | 0 | 3 |
| unknown | 47 | 0 |
| Total | 47 | 47 |

The `unknown=47` result is the main RED finding: the schema has an occlusion field, but this run did not populate it. It also does not distinguish ethanol-pretreated rows or non-occluded ternary rows, so strict Phase 1 filtering cannot be done from current records without a PR-D/manual protocol annotation step.

## 6. Multi-Endpoint Capture

| Length | Count | Meaning |
| --- | --- | --- |
| 1 | 24 | single endpoint |
| 2 | 23 | typically J + kp |

| Kind | Count |
| --- | --- |
| flux | 47 |
| cumulative_amount | 0 |
| permeability_coefficient | 23 |
| partition_parameter | 0 |
| diffusion_parameter | 0 |
| other | 0 |

All records have a flux endpoint, but only 23/47 also have `permeability_coefficient`. No `partition_parameter` (Kh) or `diffusion_parameter` (D/h2) endpoints were captured. These endpoints should not be used as Phase 1 features from the current run without further extraction work.

## 7. Extended J Accuracy for 28 Main-Task Rows

| Paper/Table | Vehicle | Expected J_mean | Extracted J_mean | Mean ratio | Mean +/-2% | Expected J_sd | Extracted J_sd | SD ratio | SD +/-5% | Record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Part I Table 3 | 0:100 | 186 | 186 | 1 | PASS | 11 | 11 | 1 | PASS | record_2abb314c7b9a |
| Part I Table 3 | 25:75 | 420 | 420 | 1 | PASS | 2.5 | 2.5 | 1 | PASS | record_c5c947facd5e |
| Part I Table 3 | 50:50 | 916 | 916 | 1 | PASS | 79 | 79 | 1 | PASS | record_9d951ad8e97f |
| Part I Table 3 | 75:25 | 945 | 945 | 1 | PASS | 61 | 61 | 1 | PASS | record_6addda23f9bf |
| Part I Table 3 | 100:0 | 1495 | 1495 | 1 | PASS | 116 | 116 | 1 | PASS | record_3a82944abc56 |
| Part II Table 2 | 0:100 | 185.5 | 185.58 | 1.0004313 | PASS | 10.94 | 10.94 | 1 | PASS | record_b178d612dacc |
| Part II Table 2 | 10:90 | 225.4 | 225.48 | 1.0003549 | PASS | 31.47 | 31.47 | 1 | PASS | record_50358ab6a9ca |
| Part II Table 2 | 20:80 | 229.5 | 229.58 | 1.0003486 | PASS | 14.2 | 14.2 | 1 | PASS | record_fbbd43bde2f5 |
| Part II Table 2 | 30:70 | 216 | 216.08 | 1.0003704 | PASS | 22.47 | 22.47 | 1 | PASS | record_937d3e534888 |
| Part II Table 2 | 40:60 | 277.1 | 277.18 | 1.0002887 | PASS | 31.22 | 31.22 | 1 | PASS | record_9002f53353a8 |
| Part II Table 2 | 60:40 | 355.4 | 355.48 | 1.0002251 | PASS | 36.34 | 36.34 | 1 | PASS | record_3738ac92928d |
| Part II Table 2 | 70:30 | 443.3 | 443.38 | 1.0001805 | PASS | 19.86 | 19.86 | 1 | PASS | record_bc629b7ee4f2 |
| Part II Table 2 | 80:20 | 245.2 | 245.28 | 1.0003263 | PASS | 28.55 | 28.55 | 1 | PASS | record_8308d93e2200 |
| Part II Table 2 | 90:10 | 219.6 | 219.68 | 1.0003643 | PASS | 22.32 | 22.32 | 1 | PASS | record_d1ff98d4c972 |
| Part II Table 2 | 100:0 | 297.1 | 297.18 | 1.0002693 | PASS | 29.43 | 29.43 | 1 | PASS | record_f34719333f70 |
| Part II Table 3 | 25:25:50 | 525.8 | 525.88 | 1.0001521 | PASS | 37.3 | 37.3 | 1 | PASS | record_6b4ab72b9a59 |
| Part II Table 3 | 50:25:25 | 641.1 | 641.18 | 1.0001248 | PASS | 84.1 | 4.1 | 0.048751486 | FAIL | record_073219db157b |
| Part III Table 3 | 0/100 | 623.8 | 623.88 | 1.0001282 | PASS | 67.7 | 67.7 | 1 | PASS | record_cb52be540c78 |
| Part III Table 3 | 10/90 | 439.9 | 439.98 | 1.0001819 | PASS | 23.9 | 23.9 | 1 | PASS | record_727c284f387d |
| Part III Table 3 | 20/80 | 569.6 | 569.68 | 1.0001404 | PASS | 63.5 | 63.5 | 1 | PASS | record_d89ce76d4e73 |
| Part III Table 3 | 30/70 | 573.5 | 573.58 | 1.0001395 | PASS | 55 | 55 | 1 | PASS | record_fd14bfeef86b |
| Part III Table 3 | 40/60 | 409.4 | 409.48 | 1.0001954 | PASS | 13.6 | 13.6 | 1 | PASS | record_251b349f4982 |
| Part III Table 3 | 50/50 | 311.9 | 311.98 | 1.0002565 | PASS | 33.8 | 33.8 | 1 | PASS | record_7c57e0a8f5f4 |
| Part III Table 3 | 60/40 | 675.1 | 675.18 | 1.0001185 | PASS | 66.8 | 66.8 | 1 | PASS | record_00cea63f02f2 |
| Part III Table 3 | 70/30 | 646.9 | 646.98 | 1.0001237 | PASS | 9.9 | 9.9 | 1 | PASS | record_5aa5cbaf50a8 |
| Part III Table 3 | 80/20 | 519.1 | 519.18 | 1.0001541 | PASS | 20.2 | 20.2 | 1 | PASS | record_7f58f7aeb93b |
| Part III Table 3 | 90/10 | 457 | 457.08 | 1.0001751 | PASS | 53.5 | 53.5 | 1 | PASS | record_efe20315f4cc |
| Part III Table 3 | 100/0 | 579.4 | 579.48 | 1.0001381 | PASS | 35.3 | 35.3 | 1 | PASS | record_0ae15e6cd56d |

J_mean within +/-2%: **28/28**. J_sd within +/-5%: **27/28**.

The only SD failure is Part II Table 3, vehicle 50:25:25: extracted SD 4.1 vs expected 84.1. The mean for that row is correct, so this is likely a mean/SD concatenation or digit-loss issue in table parsing.

## 8. Master Table v1.5

Wrote `outputs/phase07_audit/master_table_v15.csv` with exactly the requested columns and 47 rows. `include_in_main_task` is false for every row because strict `occlusion == "occluded"` never passes in the current records.

## 9. Failure Mode Inventory

Wrote `outputs/phase07_audit/failure_inventory.csv` with 142 issue rows covering 47 records with at least one issue.

Main failure classes:

- `occlusion_field_mismatch`: 47
- `composition_not_structured`: 47
- `multi_endpoint_incomplete`: 47
- `J_mean_or_sd_off_by_gt10pct`: 1

## 10. Recommendations for Phase 1

- Strict main-task usable records from current fields: **0/28**. Numerically recoverable J-mean rows after table/protocol matching: **28/28**.
- Strict skin secondary-task usable records from current fields: **0/14** because occlusion is also unknown for all human epidermis records.
- PR-D should populate `occlusion` with `occluded`, `non_occluded`, and `pretreated`, and should keep pretreated/non-occluded rows out of the standard-protocol training subset.
- PR-D should normalize top-level `barrier` from row/table context or make downstream code use `conditions.membrane_type`; the current top-level field is not reliable enough for filtering.
- PR-D should emit structured vehicle components, not only a ratio label, so Phase 1 does not depend on table-specific parsing rules.
- Multi-endpoint extraction should be extended before modelling with kp/Kh/Dh2. Current kp coverage is partial and Kh/Dh2 coverage is zero.
- The Part II Table 3 50:25:25 SD error should be added as a regression anchor before relying on SD values.

## Files Written

- `reports/phase07_watkinson_v15_audit.md`
- `outputs/phase07_audit/master_table_v15.csv`
- `outputs/phase07_audit/per_record_audit.json`
- `outputs/phase07_audit/failure_inventory.csv`
