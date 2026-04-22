# Gold Set Round 2 Evaluation Report

## 1. Summary

The Round 2 manual annotation contains 130 rows across four tiers. For the GPT v4 verified set, manual review found 25 true positives and 26 false positives, giving an overall v4 precision of 49.0%. Precision is high at the v2 scope (25/25 = 100.0%) but drops after v3/v4 scope relaxation. The unresolved and rejected samples did not contain any gold keep records, while Claude-only v4 verified records contributed no additional true positives in this annotated sample.

## 2. Precision By Policy Level

| Policy scope | Verified records included | TP | FP | Precision |
| --- | --- | --- | --- | --- |
| v1 only | 1 | 1 | 0 | 100.0% |
| v1+v2 | 25 | 25 | 0 | 100.0% |
| v1+v2+v3 | 47 | 25 | 22 | 53.2% |
| v1+v2+v3+v4 (all) | 51 | 25 | 26 | 49.0% |

TP is `gold_keep_record=yes`; FP is `gold_keep_record=no`. The v1 row contains one figure-route record that is scope-correct but value-inaccurate, so it counts as keep-record precision TP but not as end-to-end TP below.

## 3. Scope Precision vs End-to-End Precision

| Policy scope | Verified records included | Scope TP | Scope precision | Scope+value TP | End-to-end precision |
| --- | --- | --- | --- | --- | --- |
| v1 only | 1 | 1 | 100.0% | 0 | 0.0% |
| v1+v2 | 25 | 25 | 100.0% | 24 | 96.0% |
| v1+v2+v3 | 47 | 25 | 53.2% | 24 | 51.1% |
| v1+v2+v3+v4 (all) | 51 | 25 | 49.0% | 24 | 47.1% |

Scope precision uses `gold_scope_correct=yes`. End-to-end precision requires both `gold_scope_correct=yes` and `gold_value_correct=yes`.

## 4. Recall Estimation

- Tier 2 unresolved sample size: `44`
- Gold keep records in unresolved sample: `0`
- Estimated unresolved false-negative rate in the sampled unresolved set: `0.0%`
- Sample-based recall over annotated GPT verified TP plus unresolved keep-records: `100.0%` (25/25)

No false negatives were observed in the unresolved sample. This should be interpreted as a sampled estimate, not a proof that the full unresolved pool contains zero recoverable records.

## 5. Rejection Correctness

- Tier 3 rejected sample size: `12`
- Correct rejections (`gold_keep_record=no`): `12`
- Rejection correctness: `100.0%`

## 6. Cross-Vendor Comparison (Claude-Only)

- Tier 4 Claude-only verified sample size: `23`
- Gold keep records: `0`
- Claude-only precision in this sample: `0.0%`
- Route distribution: `{'mixed': 23}`
- Paper distribution: `{'10.1186/2050-6511-13-5': 9, '10.1248/cpb.c21-00033': 14}`

Claude-only v4 verified records did not contribute additional true positives under the completed manual annotation. They are concentrated in `10.1248/cpb.c21-00033` and `10.1186/2050-6511-13-5`.

## 7. Precision By Route

| Route | Total verified (GPT v4) | TP | FP | Precision |
| --- | --- | --- | --- | --- |
| table | 33 | 24 | 9 | 72.7% |
| figure | 1 | 1 | 0 | 100.0% |
| text | 6 | 0 | 6 | 0.0% |
| mixed | 11 | 0 | 11 | 0.0% |

Table-route verified records dominate the true positives. The single figure-route verified record is scope-correct but not endpoint-value correct, so route precision by `gold_keep_record` is 100% while end-to-end value accuracy for that route is not.

## 8. False Positive Error Pattern Analysis

There are `26` false positives among GPT v4 verified records. The pattern counts below are multi-label; one record can contribute to more than one error pattern.

| Error pattern | Count | Share of 26 FP |
| --- | --- | --- |
| Endpoint value incorrect | 20 | 76.9% |
| Concentration missing or incorrect | 19 | 73.1% |
| Device wrong / non-Franz | 13 | 50.0% |
| Endpoint time incorrect | 13 | 50.0% |
| In vivo / DPK / non-IVPT assay mistaken as IVPT | 11 | 42.3% |
| Endpoint kind incorrect | 10 | 38.5% |
| Non-target API or ibuprofen not target drug | 7 | 26.9% |

Top error modes are endpoint value errors, concentration extraction/scope errors, and device / endpoint-time errors. Scope relaxation in v3/v4 introduced many records from non-IVPT, in vivo/DPK, non-target API, or non-Franz contexts.

## 9. New Field Quality

The table below is computed on the `25` true-positive GPT verified records (`gold_keep_record=yes`).

| Field | Correct | Partial | Wrong | Not reported / N/A / uncertain |
| --- | --- | --- | --- | --- |
| membrane | 25 | 0 | 0 | 0 |
| receptor_medium | 24 | 0 | 1 | 0 |
| dose_type | 24 | 0 | 1 | 0 |
| excipient | 0 | 24 | 0 | 1 |

Membrane, receptor medium, and dose type are mostly correct in true positives. Excipient composition is usually only partial because the pipeline often captures coded formulation factors rather than full composition.

## 10. Key Findings For Paper

1. The strict v2-level scope is highly precise: v1+v2 reaches `25/25 = 100.0%` keep-record precision and `24/25 = 96.0%` end-to-end precision.
2. The widest v4 policy increases candidate coverage but substantially lowers precision: GPT v4 verified precision is `25/51 = 49.0%`, and end-to-end precision is `24/51 = 47.1%`.
3. No recoverable true positives were found in the Tier 2 unresolved sample (`0/44`), suggesting high recall within the sampled unresolved strata.
4. Rejection quality was high in the sampled rejected tier: `12/12 = 100.0%` correct rejections.
5. Claude-only v4 verified records did not add extra true positives in the annotated sample (`0/23`), indicating that Claude's additional mixed-route flux records were not useful positives under the gold criteria.
