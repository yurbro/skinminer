# Watkinson Three-PDF SkinMiner Extraction Dry-Run

## 1. Executive Summary
Decision: **RED**. The aggregate verified-record count is 39/47 (83%), but this is not modelling-ready. The main-task complete-field coverage is 0/28 = 0.000; composition anchors pass 3/6; numeric J spot-checks pass 2/10. The verifier accepted all final records, but key table values, SDs, barrier/protocol fields, and replicate fields are not reliable.
Entry point used: manual ContentAccess local PDF workaround from the router stage (`manual_corpus_workaround=true`), using policy `v4_accept_flux`.

## 2. SkinMiner PDF Entry Point Used
`run_pipeline.py --help` exposes `--input-csv`, `--policy`, content download flags, and model flags, but no direct `--pdf` or `--input-pdf` upload flag. `scripts/` is absent. `access/resolve_content.py` resolves OA URLs and downloads into `papers/`, but does not consume `papers/uploaded_external/*.pdf` from the input CSV. Therefore this run used the documented fallback strategy: a minimal manual corpus and explicit `ContentAccess(local_paths={'pdf': ...})`, then direct invocation of the router, extractor, assembly, patching, and verifier modules. SkinMiner source code was not changed.

## 3. Watkinson_2009_I Diagnostic
| field | value |
| --- | --- |
| DOI | 10.1159/000183922 |
| route | mixed |
| expected permeation records | 13 |
| table/text/figure records | 10 / 5 / 0 |
| assembled records | 15 |
| verified records | 15 |
| verification status counts | {"verified": 15} |
| unique endpoint kinds | amount_per_area; flux |
| unique J units | ug/cm2/h |
| unique membranes | Silicone Membrane; Skin; epidermis |
| replicates | MISSING |

Composition anchors:
| table | vehicle | record | parsed | correct |
| --- | --- | --- | --- | --- |
| Table 3 | 0:100 | record_abc4d817d2a3 | {"ethanol_vv": 0.0, "PG_vv": null, "water_vv": 100.0, "MO_vv": null, "MG_vv": null} | True |
| Table 3 | 100:0 | record_d11a5c8c2530 | {"ethanol_vv": 100.0, "PG_vv": null, "water_vv": 0.0, "MO_vv": null, "MG_vv": null} | True |

Numerical J anchors:
| table | vehicle | expected_J | extracted_J | ratio | within_1pct | record |
| --- | --- | --- | --- | --- | --- | --- |
| Table 3 | 0:100 | 186.0 | 2.7 | 0.0145 | False | record_abc4d817d2a3 |
| Table 3 | 100:0 | 1495.0 | 116.0 | 0.0776 | False | record_d11a5c8c2530 |
| Table 5 | 0:100 | 24.0 | 2.7 | 0.1125 | False | record_c04f6407efcb |

Protocol/API/replicates: no structured occlusion, pretreatment, or replicate-count field was captured. API state/concentration values: `ethanol-water formulations|0.0|mg/ml|0 mg/ml; |None||`.

## 4. Watkinson_2009_II Diagnostic
| field | value |
| --- | --- |
| DOI | 10.1159/000231528 |
| route | table |
| expected permeation records | 20 |
| table/text/figure records | 13 / 0 / 0 |
| assembled records | 13 |
| verified records | 13 |
| verification status counts | {"verified": 13} |
| unique endpoint kinds | amount_per_area |
| unique J units | ug/cm2/h |
| unique membranes | silicone |
| replicates | MISSING |

Composition anchors:
| table | vehicle | record | parsed | correct |
| --- | --- | --- | --- | --- |
| Table 2 | 70:30 | record_3f3d207c6b22 | {"ethanol_vv": null, "PG_vv": 70.0, "water_vv": 30.0, "MO_vv": null, "MG_vv": null} | True |
| Table 3 | 25:25:50 | null | null | False |
| Table 3 | 50:25:25 | null | null | False |

Numerical J anchors:
| table | vehicle | expected_J | extracted_J | ratio | within_1pct | record |
| --- | --- | --- | --- | --- | --- | --- |
| Table 2 | 50:50 | 277.1 | null | null | False | null |
| Table 2 | 70:30 | 443.3 | 443.38 | 1.0002 | True | record_3f3d207c6b22 |
| Table 3 | 25:25:50 | 525.8 | null | null | False | null |
| Table 5 | 100:0 | 133.8 | 133.88 | 1.0006 | True | record_3d597be2c17f |

Protocol/API/replicates: no structured occlusion, pretreatment, or replicate-count field was captured. API state/concentration values: `|None||`.

## 5. Watkinson_2011_III Diagnostic
| field | value |
| --- | --- |
| DOI | 10.1159/000315139 |
| route | table |
| expected permeation records | 14 |
| table/text/figure records | 11 / 0 / 0 |
| assembled records | 11 |
| verified records | 11 |
| verification status counts | {"verified": 11} |
| unique endpoint kinds | amount_per_area |
| unique J units | ug/cm2/h |
| unique membranes | human epidermis |
| replicates | MISSING |

Composition anchors:
| table | vehicle | record | parsed | correct |
| --- | --- | --- | --- | --- |
| Table 3 | 60/40 | null | null | False |

Numerical J anchors:
| table | vehicle | expected_J | extracted_J | ratio | within_1pct | record |
| --- | --- | --- | --- | --- | --- | --- |
| Table 3 | 0/100 | 623.8 | null | null | False | null |
| Table 3 | 100/0 | 579.4 | null | null | False | null |
| Table 4 | 100/0 | 83.1 | 579.48 | 6.9733 | False | record_c0494eca3907 |

Protocol/API/replicates: no structured occlusion, pretreatment, or replicate-count field was captured. API state/concentration values: `saturated solution|None||`.

## 6. Cross-Paper Consistency
| field | Watkinson_2009_I | Watkinson_2009_II | Watkinson_2011_III |
| --- | --- | --- | --- |
| device | Franz diffusion cell | Franz diffusion cell | Franz diffusion cell |
| membrane_type | Silicone Membrane; Skin; epidermis | silicone | human epidermis |
| temperature_c | MISSING | MISSING | MISSING |
| receptor_medium | pH 7.4 phosphate-buffered saline | MISSING | phosphate-buffered saline |
| receptor_volume_ml | 2.5 | 2.5 | MISSING |
The device label is consistent, but membrane/barrier, temperature, receptor medium, and receptor volume require manual normalization. Temperature is missing in all structured records; receptor volume is absent for Part III.

## 7. Master Table Draft Summary
| metric | value |
| --- | --- |
| n_total_extracted_permeation_records | 39 |
| n_silicone_occluded_main_task | 0 |
| n_with_complete_main_task_fields | 0 |
| coverage_ratio | 0/28 = 0.000 |
| decision | RED |
`outputs\watkinson_dryrun\master_table_draft.csv` contains 39 rows. `include_in_main_task` is false for all rows because no structured occlusion field was captured; `J_sd` is also empty for all rows.

## 8. Failure Modes Inventory
- No formal user-uploaded PDF entry point; dry-run required manual `ContentAccess` construction.
- PDF table text concatenates mean and SD values; the table extractor often selected SD or adjacent-column values as J.
- Part II Table 3/4/6 ternary records were not extracted; Part III Table 3 silicone records were not extracted.
- Part III Table 4 values were repeated/misaligned, and a silicone 100/0 J value appears under the human epidermis table.
- All final records were marked `verified`, so verifier acceptance did not catch row/column misalignment.
- `endpoint.kind` was usually normalized to `amount_per_area` despite flux units; v4 accepted the flux-like unit string.
- Occlusion, non-occlusion, ethanol pretreatment, and replicate count were not represented as structured fields.
- `patch_endpoint_time` can recover irrelevant analytical times; Part II records received 5 min from HPLC retention context.

## 9. Recommendations for Phase 1
- Treat this dry-run as RED; do not proceed to modelling from these records without a table-extraction fix or manual curation.
- Add a first-class local PDF upload/input entry point before production demonstrations.
- Extend the table schema for paired mean/SD columns and explicit endpoint families (`J`, `kp`, `Kh`, `D/h2`) instead of a single endpoint value.
- Add structured fields for `occlusion`, `pretreatment`, `replicates`, `temperature`, `receptor_medium`, and `receptor_volume`.
- Tighten verification so flux units set `endpoint.kind=flux` and table row/column alignment is checked before `verified` status.

## 10. Known Limitations
- Ground truth counts and anchor values were taken from the supplied task; this report did not re-count the PDFs.
- This is one LLM run with the repository default OpenAI baseline (`gpt-4o-mini`); stochastic extraction may vary.
- The master table parser only parses vehicle composition from extracted labels/components; it does not repair missing records or numeric values.
- Figure extraction was not triggered because no paper routed as `figure`; empty figure stage JSONL files are present.
