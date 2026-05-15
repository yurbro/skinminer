# Phase 0b Stage 1 Ibuprofen Audit

Zero-cost audit generated from existing JSONL outputs only. No extractor, PDF, API, or LLM call was made.

## 1. Pool Composition

- Total unique DOIs in ibuprofen union pool: `40`
- DOI provenance breakdown: GPT v2 `2`, Claude v2 `1`, GPT v3-only `6`, GPT v4-only `3`, unresolved-only `30`, rejected-only `0`.
- Histogram of n_records_total per paper: 1=`7`, 2-4=`14`, 5-9=`9`, 10+=`10`.
- Near-miss API names flagged for manual review: `S(+) ibuprofen` (7), `R(-) ibuprofen` (2), `Ibuprofen amyl ester` (1), `Ibuprofen propyl ester` (1), `Ibuprofen hexyl ester` (1), `Ibuprofen ethyl ester` (1), `Ibuprofen butyl ester` (1), `Ibuprofen isopropyl ester` (1).
- Ibuprofen-like API names excluded by the pool regex: none.

Top 10 papers by n_records_total:

| doi                           |   n_records_total |   n_records_v2 |   n_records_v3_only |   n_records_v4_only |   n_records_unresolved | provenance_mix                                               |
|:------------------------------|------------------:|---------------:|--------------------:|--------------------:|-----------------------:|:-------------------------------------------------------------|
| 10.1016/j.ijpharm.2016.03.043 |                27 |              0 |                   0 |                   0 |                     27 | unresolved:27                                                |
| 10.1186/2050-6511-13-5        |                27 |              0 |                   3 |                   0 |                     24 | verified_v3_gpt_only:3, unresolved:24                        |
| 10.1208/s12249-013-9995-4     |                24 |             24 |                   0 |                   0 |                      0 | verified_v2_gpt:24                                           |
| 10.4103/jomfp.jomfp_253_19    |                19 |              0 |                   0 |                   0 |                     19 | unresolved:19                                                |
| 10.1248/cpb.c21-00033         |                14 |              0 |                   0 |                   0 |                     14 | unresolved:14                                                |
| 10.1007/s11095-008-9785-y     |                12 |              0 |                   5 |                   1 |                      6 | verified_v3_gpt_only:5, verified_v4_gpt_only:1, unresolved:6 |
| 10.1016/j.ejpb.2020.05.013    |                12 |              1 |                   0 |                   0 |                     11 | verified_v2_gpt:1, unresolved:11                             |
| 10.1208/s12249-019-1481-1     |                10 |              0 |                   6 |                   0 |                      4 | verified_v3_gpt_only:6, unresolved:4                         |
| 10.1208/s12249-019-1584-8     |                10 |              0 |                   0 |                   0 |                     10 | unresolved:10                                                |
| 10.1038/s41598-024-57883-5    |                10 |              0 |                   0 |                   0 |                     10 | unresolved:10                                                |

## 2. Internal Modelling Viability

- Papers with internal_factor_variation=True: `1`
- Papers with modelling_candidate_score >= 50: `10`

Top 10 papers by modelling score:

| doi                                |   n_records_total | internal_factor_variation   |   modelling_candidate_score | formulation_factor_summary                                                                                                          |
|:-----------------------------------|------------------:|:----------------------------|----------------------------:|:------------------------------------------------------------------------------------------------------------------------------------|
| 10.1208/s12249-013-9995-4          |                24 | False                       |                          75 | polymer_hpmc:1coded level;surfactant_tpgs:1coded level                                                                              |
| 10.1208/s12249-019-1481-1          |                10 | True                        |                          75 | cosolvent_pg:4wt%,30%;cosolvent_water:40%;cosolvent_glycerin:24wt%,45%,60%,65%,70%,...                                              |
| 10.4103/jomfp.jomfp_253_19         |                19 | False                       |                          65 | none                                                                                                                                |
| 10.1016/j.ejpb.2020.05.013         |                12 | False                       |                          65 | none                                                                                                                                |
| 10.1016/j.ijpharm.2016.03.043      |                27 | False                       |                          55 | cosolvent_pg:qualitative;cosolvent_etoh:qualitative                                                                                 |
| 10.1038/s41598-024-57883-5         |                10 | False                       |                          55 | none                                                                                                                                |
| 10.1208/s12249-019-1584-8          |                10 | False                       |                          55 | cosolvent_water:qualitative;cosolvent_other:10% (w/w);surfactant_other:4% (w/w);enhancer_azone:qualitative;nano_carrier:qualitative |
| 10.1523/jneurosci.15-04-02768.1995 |                 9 | False                       |                          55 | none                                                                                                                                |
| 10.1371/journal.pone.0156931       |                 8 | False                       |                          55 | none                                                                                                                                |
| 10.1039/d0ra00100g                 |                 8 | False                       |                          50 | none                                                                                                                                |

## 3. Cross-Paper Compatibility

- Ordered pair counts: STRONG `0`, MODERATE `0`, WEAK `0`, INCOMPATIBLE `650`.

STRONG and MODERATE pairs:

_None._

Best candidate pair: `10.1007/s11095-008-9785-y` -> `10.1208/s12249-019-1481-1` (INCOMPATIBLE), n_records 12 + 10, scores 40 + 75, shared numeric buckets: 2.

## 4. Honest Reality Check

Stage 2-only gaps for the top candidate pair:

- 10.1007/s11095-008-9785-y: 5 ibuprofen records have no numeric endpoint value in structured fields.
- 10.1007/s11095-008-9785-y: endpoint units vary across records (-; mg; ug/cm^2).
- 10.1007/s11095-008-9785-y: 1 records were not table-sourced; Stage 2 should re-check table/text alignment.
- 10.1208/s12249-019-1481-1: no obvious structured-field gap; Stage 2 would mainly verify extraction fidelity from tables/methods.

Rough Stage 2 order: 2 papers x 2 passes (tables + methods/results text) x ~8,000 input tokens = ~32,000 input tokens, ~4,000-8,000 output tokens.

## 5. GO/NO-GO Recommendation

NO-GO: No STRONG pair exists and the MODERATE evidence does not satisfy the Stage 2 threshold.

RECOMMENDATION: NO-GO | No STRONG pair exists and the MODERATE evidence does not satisfy the Stage 2 threshold.
