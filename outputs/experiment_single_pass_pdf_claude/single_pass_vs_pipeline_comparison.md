# Single-Pass vs Modular Pipeline Comparison

## 1. Experiment Setup
- Modular baseline: Round2 GPT v4 verified annotation from the post-fix modular pipeline.
- Single-pass baseline: one end-to-end PDF extraction prompt per model-callable DOI, using `claude-sonnet-4-6`.
- Same Round2 DOI subset: `29` unique papers.
- The model received raw PDF inputs, which include PDF text and page/image context available to the API. No separate extracted text/table appendix was supplied.
- Structured-output success: `23/29` callable PDFs returned parseable JSON; the remaining `6` papers failed at JSON parsing and are excluded from the single-pass match metrics.

## 2. Coverage Comparison
| Method | Gold TP denominator | Covered TP | Coverage |
| --- | ---: | ---: | ---: |
| Modular pipeline | 25 | 25 | 100.0% |
| Single-pass | 25 | 0 | 0.0% |

## 3. Value Accuracy Comparison
| Method | Records compared | Value correct | Value incorrect/missing | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Modular pipeline | 25 | 24 | 1 | 96.0% |
| Single-pass | 24 value-anchored gold TP | 0 | 24 | 0.0% |

## 4. Scope Accuracy
- Modular pipeline GPT v4 verified precision on Tier1 annotation: `25/51 = 49.0%`.
- Modular pipeline end-to-end precision on Tier1 annotation: `24/51 = 47.1%`.
- Single-pass emitted `132` raw records. It matched `5` annotated false-positive rows and emitted records for `11` gold-negative DOI.
- Single-pass has no verification gate, so raw output precision cannot be estimated exactly from the sampled gold set; unmatched extra records require manual review.

## 5. False Positive Analysis
- Annotated FP matches: `5` rows. Details are in `single_pass_annotated_fp_matches.csv`.
- Extra unmatched single-pass records: `124` rows. Details are in `single_pass_extra_records.csv`.

## 6. Field Completeness
| Field | Modular pipeline TP quality from Round2 | Single-pass matched TP fill rate |
| --- | --- | ---: |
| membrane | 25/25 correct | 0/0 = n/a |
| receptor medium | 24/25 correct | 0/0 = n/a |
| dose | 24/25 correct | 0/0 = n/a |
| excipient | 24/25 partial, 1 uncertain | 0/0 = n/a |

## 7. Cost Comparison
| Method | Total Tokens | Estimated / Actual Cost | Time |
| --- | ---: | ---: | ---: |
| Modular Pipeline (full run reference) | ~3.8M | ~$0.71 | ~5000s |
| Single-pass (Round2 DOI subset) | 1,073,320 actual billed tokens | $4.1983 actual API cost | not benchmarked |

## 8. Traceability Comparison
- Modular pipeline has field-level evidence items, route provenance, verification status, and failure reasons.
- Single-pass has one free-text `source_evidence` field per record. This is useful but weaker for automated source binding and gate-level diagnosis.

## 9. Key Findings
1. Single-pass covered `0/25` Round2 gold keep-records under the DOI+label+time matching rule.
2. Single-pass value accuracy on value-anchored gold TP rows was `0/24 = 0.0%`.
3. Single-pass produced `5` matches to annotated false-positive rows and `124` unmatched extras, so it still needs a verification/gating layer for precision.
4. The modular pipeline remains stronger for traceability because every accepted field carries structured evidence and verifier status.
