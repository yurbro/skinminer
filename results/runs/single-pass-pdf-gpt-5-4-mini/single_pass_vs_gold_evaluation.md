# Single-Pass vs Gold Set Evaluation

## 1. Setup
- Annotation file: `outputs\gold_audit_set\round2\gold_set_round2_annotation.csv`
- Results file: `outputs\experiment_single_pass_pdf_gpt54\single_pass_results.jsonl`
- Model: `gpt-5.4-mini`
- Input mode: raw PDF via document/file input; no extracted text/table appendix was supplied.
- PDF availability: all 29 papers had callable PDFs in this run.

## 2. Run Summary
- Papers in scope: `29`
- Paper status counts: `{'ok': 29}`
- Single-pass records emitted: `288`
- Actual usage from completed LLM calls: input `670,791`, output `104,505`, total `775,296` tokens.

## 3. Gold True Positive Coverage
- Gold keep-record rows: `25`
- Covered by single-pass match on DOI + formulation label + endpoint time: `24/25 = 96.0%`
- Value-anchored gold TP rows: `24`. One keep-record has `gold_value_correct=no`, so it is excluded from value-accuracy denominator.
- Covered value-anchored rows: `24/24 = 100.0%`
- Value-correct among all value-anchored gold rows: `24/24 = 100.0%`
- Value-correct among covered value-anchored rows: `24/24 = 100.0%`

## 4. Annotated False Positive Interaction
- Annotated `gold_keep_record=no` rows matched by single-pass: `18/105`
- Single-pass extra records not matched to any Round2 annotation row: `222`
- Extra records are not automatically counted as false positives because the Round2 annotation set is a sample, not an exhaustive paper-level gold database.

## 5. Scope Signal
- Gold-negative DOI count in Round2 annotation: `27`
- Gold-negative DOI with at least one single-pass record: `18`
- Gold-negative DOI emitting records: `['10.1007/s11095-008-9785-y', '10.1007/s11095-020-02887-9', '10.1007/s11095-024-03747-6', '10.1007/s13346-022-01182-x', '10.1016/j.ijpharm.2016.03.043', '10.1016/j.ijpharm.2019.118975', '10.1016/j.jpba.2019.04.040', '10.1021/acs.molpharmaceut.0c00720', '10.1038/s41598-020-74885-1', '10.1038/s41598-024-57883-5', '10.1039/d0ra00100g', '10.1186/2050-6511-13-5', '10.1208/s12249-015-0474-y', '10.1208/s12249-019-1481-1', '10.1248/bpb.b19-00221', '10.1248/cpb.c21-00033', '10.18433/j3160b', '10.21203/rs.3.rs-3773667/v1']`

## 6. Field Completeness On Matched Gold TP
- Matched gold TP records: `24`
- Membrane field non-empty: `24/24 = 100.0%`
- Receptor medium non-empty: `24/24 = 100.0%`
- Dose field non-empty: `24/24 = 100.0%`
- Excipient composition non-empty: `24/24 = 100.0%`

## 7. Evaluation Caveats
- Endpoint value accuracy is computed only for gold keep-record rows whose pipeline value was manually marked correct. The Round2 CSV does not contain an independent normalized gold numeric field for every row.
- The matching key follows the task specification: DOI + formulation label + endpoint time. Source evidence and units are retained in `single_pass_gold_matches.csv` for manual audit.
