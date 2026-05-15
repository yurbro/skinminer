# Verification Ceiling Diagnosis

## Summary Statistics

| Category | E2 total | Analyzed rows |
|---|---:|---:|
| A: patched but unresolved | 27 | 27 |
| B: near-verified non-figure | 43 | 15 |
| C: adjudication-verified but pipeline-unresolved | 8 | 8 |

Note: for Category B I screened all 43 non-figure unresolved rows, then treated the 15 single-failure rows as the first-tier near-verified set. A broader <=2-failure screen contains 42 rows, but most second-tier rows are not truly one gate away from strict verified.
Counts in this memo are pipeline-row counts. The E2 final output contains 2 duplicated unresolved mixed-route record IDs (`record_aafef845b3d5`, `record_ebb642102709`), so unique-ID counts are slightly smaller for Categories A and B.

## Category A: Patched But Unresolved

### Pattern Summary

- Total rows: 27. All 27 are `mixed` route rows; none are table-only, text-only, or figure-only.
- `patch_endpoint_value` was applied on 17 of the 27 rows, `patch_endpoint_time` on 14, and `patch_area` on 1.
- The patched field usually survives verification. Rows with a successful endpoint-value patch and still `missing_endpoint`: 0.
- Rows with a successful endpoint-time patch and still `missing_endpoint_time`: 0.
- Rows with a successful area patch and still `missing_area`: 0.
- Diagnosis: patchers are mostly filling one field and then exposing the next blocking gate; they are not being directly rejected by verification.

| failure_reason | Count |
|---|---:|
| insufficient_evidence | 16 |
| missing_area | 11 |
| ambiguous_api_concentration | 9 |
| unit_normalization_failed | 8 |
| percent_only | 3 |
| missing_api_concentration | 1 |
| not_target_api_concentration | 1 |

Most common failure-pattern combinations in Category A:
- insufficient_evidence, unit_normalization_failed: 7
- ambiguous_api_concentration, missing_area: 7
- insufficient_evidence: 4
- insufficient_evidence, missing_area: 3
- insufficient_evidence, percent_only: 2
- ambiguous_api_concentration: 1
- ambiguous_api_concentration, unit_normalization_failed: 1
- missing_api_concentration, missing_area: 1
- not_target_api_concentration, percent_only: 1

### Representative Examples (Top 5)

| record_id | doi | route | patched fields | remaining failure_reasons | evidence summary | interception judgment |
|---|---|---|---|---|---|---|
| record_a04ba214b2b4 | 10.1002/14651858.cd001177.pub2 | mixed | endpoint.value + endpoint.time + diffusion_area_cm2 | insufficient_evidence | All three patchers succeed, but the row is still review-level evidence about ibuprofen wound dressings, not a primary Franz IVPT record. The device evidence snippet itself says no diffusion-cell language appears in the supplied text. | reasonable |
| record_15fef3ae98c5 | 10.1039/d0ra00100g | mixed | endpoint.value | insufficient_evidence; unit_normalization_failed | Table 5 gives a 24 h ibuprofen value, but the final row still carries endpoint_unit=ug with no normalized amount-per-area value and no explicit strict 5% w/w basis. The patch recovered a number, not a fully policy-ready endpoint. | reasonable |
| record_62f977a76d06 | 10.1186/2050-6511-13-5 | mixed | endpoint.time | insufficient_evidence | The patcher recovers the 6 h timepoint, but the endpoint is still flux (Jmax), not the strict amount endpoint. This is not a case where verification rejected a complete amount record. | reasonable |
| record_aafef845b3d5 | 10.1371/journal.pone.0130253 | mixed | endpoint.time | ambiguous_api_concentration; missing_area | The recovered timepoint sits on an adsorption/materials row (100 mg dm-3; mg g-1 min-1 style endpoint), not a dermal Franz amount-permeated record. The remaining gates are doing scope protection, not rejecting a nearly-complete strict record. | reasonable |
| record_1d4d89a4dd06 | 10.1038/s41598-022-05912-6 | mixed | endpoint.value | insufficient_evidence; missing_area | The patcher lifts a 1 mg / 2 h DPBS release value, but the row still lacks a diffusion area and the supplied evidence does not actually show a Franz-cell permeation setup. This remains a release-style engineering record, not a clean strict keep. | reasonable |

## Category B: Near-Verified Non-Figure

### Screening Criteria

- Start from all 43 non-figure unresolved rows in E2: table=8, text=2, mixed=33.
- Broad screen: keep rows with <=2 failure reasons. This leaves 42 rows.
- First-tier near-verified set: rows with exactly 1 failure reason. This leaves 15 rows and is the table below.
- Second-tier rows with 2 failure reasons were kept for pattern summary only; most of them have overlapping structural issues rather than one final gate.

### Near-Verified Records (Tier 1: single-failure rows)

| record_id | doi | route | failure_reasons | what is still missing before strict verified |
|---|---|---|---|---|
| record_4d928769e5da | 10.1002/14651858.cd001177.pub2 | mixed | ambiguous_api_concentration | Needs an unambiguous strict 5% w/w (or 50 mg/g) concentration basis. Current evidence is dose/area or review-level wording, not a strict formulation concentration. |
| record_b357c03adc16 | 10.1016/j.ejpb.2020.05.013 | mixed | insufficient_evidence | Looks close on paper, but the endpoint is still typed as unknown and the current evidence does not contain a numeric amount endpoint; this is not a clean verifier false negative. |
| record_62f977a76d06 | 10.1186/2050-6511-13-5 | mixed | insufficient_evidence | Only one failure code is shown, but the endpoint is flux rather than amount. This is not truly one gate away from strict verified. |
| record_2ea2f8995520 | 10.1186/2050-6511-13-5 | mixed | insufficient_evidence | Only one failure code is shown, but the endpoint is flux rather than amount. This is not truly one gate away from strict verified. |
| record_110ca1b5d0fb | 10.1186/2050-6511-13-5 | mixed | insufficient_evidence | Only one failure code is shown, but the endpoint is flux rather than amount. This is not truly one gate away from strict verified. |
| record_ace3746b1600 | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F1; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_851ab860659f | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F2; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_9d98bd27f9f7 | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F3; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_2578ce137ea3 | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F4; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_fb8b2beb150c | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F5; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_58c983118f05 | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F6; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_7843cfa292ef | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F7; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_0aa946056083 | 10.1208/s12249-013-9995-4 | table | missing_api_concentration | Needs strict concentration evidence for formulation F8; these eight table rows all come from the same paper and are the clearest non-figure near-verified cluster. |
| record_a04ba214b2b4 | 10.1002/14651858.cd001177.pub2 | mixed | insufficient_evidence | Only one failure code is shown after multiple patches, but the underlying row is still review-derived evidence rather than a primary strict IVPT record. |
| record_9cb15ea03fc7 | 10.1016/j.colsurfa.2022.129611 | text | insufficient_evidence | Only one failure code is shown, but the text route still looks like a materials-release paper with no solid formulation concentration or diffusion-area grounding. |

Second-tier two-failure screen (not listed row-by-row below) is dominated by these patterns:
- insufficient_evidence, unit_normalization_failed: 7
- ambiguous_api_concentration, missing_area: 7
- insufficient_evidence, missing_area: 3
- insufficient_evidence, percent_only: 3
- ambiguous_api_concentration, missing_endpoint: 2
- ambiguous_api_concentration, insufficient_evidence: 2
- ambiguous_api_concentration, unit_normalization_failed: 1
- missing_api_concentration, missing_area: 1
- not_target_api_concentration, percent_only: 1

### Pattern Summary

- Yes, non-figure rows that are formally one failure code away from verified do exist: 15 rows total.
- But only 8/15 are high-value first-pass candidates: the eight table rows from `10.1208/s12249-013-9995-4`, all blocked only by `missing_api_concentration`.
- There are 0 non-figure rows blocked only by `missing_area`.
- There is 1 row blocked only by `ambiguous_api_concentration`, but it is a review/dose-style record (`0.5 mg/cm2`) rather than a clean strict 5% w/w formulation candidate.
- Six single-failure rows are blocked only by `insufficient_evidence`, but several of them are not true one-gate misses: some are flux-only rows, one is review-derived, and one text row still looks like a materials-release paper.
- The closest non-figure row in the current artifacts is `record_b357c03adc16` (`10.1016/j.ejpb.2020.05.013`), but even there the endpoint is still typed as `unknown`, so this is a normalization/typing problem rather than a clean verifier false rejection.
- For the eight `missing_api_concentration` table rows, deciding whether they are true false rejections would require reopening the original formulation-composition evidence outside the currently selected pages. I therefore treat them as high-value recovery targets, not confirmed over-conservative blocks.

## Category C: Adjudication Disagrees

### The 8 Adjudication-Verified Records

| record_id | doi | route | pipeline status | adjudication recommended | adjudication rationale summary | pipeline failure_reasons | judgment |
|---|---|---|---|---|---|---|---|
| record_ad187da7e0eb | 10.1021/acs.molpharmaceut.0c00720 | mixed | unresolved | verified | The paper is clearly about ibuprofen in a Franz diffusion cell IVPT context, and the evidence explicitly states a permeability experiment on an '8 mM aqueous solution of P+-Ibuprofen ion-... | ambiguous_api_concentration, missing_endpoint | pipeline more defensible: Adjudication admits the record is 8 mM, not 5% w/w, and the numeric amount endpoint is still missing. |
| record_001772de13ae | 10.1021/acs.molpharmaceut.0c00720 | mixed | unresolved | verified | This paper is clearly in-scope for the strict pipeline on device and endpoint: it reports Franz cell assays / permeation through membranes for ibuprofen, with IVPT-like membrane transport... | ambiguous_api_concentration, insufficient_evidence | pipeline more defensible: Adjudication recommends verified even though its own rationale says concentration_5pct_ww is not satisfied. |
| record_52276b96d370 | 10.1021/acs.molpharmaceut.0c00720 | mixed | unresolved | verified | The paper is clearly within the strict topical scope: ibuprofen, Franz cell assays, and IVPT/transport through model membranes. The evidence explicitly states a 8 mM aqueous solution of P... | ambiguous_api_concentration, insufficient_evidence | pipeline more defensible: Same issue as above: 8 mM ion-pair record, not strict 5% w/w, and endpoint typing remains ambiguous. |
| record_3c299c3e0864 | 10.1016/j.ejpb.2020.05.013 | mixed | unresolved | verified | The paper clearly matches the strict scope: ibuprofen, 5% w/w gel, Franz-cell-similitude diffusion cell, IVPT/permeation study, quantitative amount endpoint, and a stated endpoint time of... | missing_endpoint, unit_normalization_failed, figure_digitization_failed | pipeline more defensible: The rationale acknowledges that the exact numeric endpoint value is not present in the supplied evidence. Strict verified should not be granted without that value. |
| record_15fef3ae98c5 | 10.1039/d0ra00100g | mixed | unresolved | verified | The paper clearly reports an ibuprofen formulation tested in Franz diffusion cells under IVPT conditions, with a 24 h cumulative mass endpoint. The evidence snippet explicitly gives 24 h ... | insufficient_evidence, unit_normalization_failed | pipeline more defensible: Adjudication waives both concentration uncertainty and unit-normalization problems; that is too permissive for strict verified. |
| record_16ab943d4192 | 10.1039/d0ra00100g | mixed | unresolved | verified | This record is a strict-scope match for ibuprofen, Franz diffusion cell, IVPT, amount endpoint, and 24 h endpoint time. The evidence packet directly supports the device and endpoint: Tabl... | insufficient_evidence, unit_normalization_failed | pipeline more defensible: The row still lacks a strict 5% w/w basis and carries unresolved unit consistency issues. |
| record_556c1b23e090 | 10.1039/d0ra00100g | mixed | unresolved | verified | This is a strict in-scope Franz cell IVPT study of ibuprofen with an amount endpoint at 24 h. The evidence explicitly states skin permeation experiments were performed in Franz diffusion ... | insufficient_evidence, unit_normalization_failed | pipeline more defensible: Same pattern: endpoint value exists, but strict concentration support is still absent and adjudication relaxes that requirement. |
| record_1b45aa397221 | 10.1039/d0ra00100g | mixed | unresolved | verified | The record is in scope for an ibuprofen Franz-cell IVPT study with an amount endpoint at 24 h. The evidence explicitly shows Franz diffusion cells, porcine skin permeation, and Table 5 re... | insufficient_evidence, unit_normalization_failed | pipeline more defensible: Same pattern: the rationale itself says concentration cannot be verified from the supplied fragments. |

### Pattern Summary

- All 8 Category C rows are `mixed` route rows; there are no table-only, text-only, or figure-only adjudication-to-verified disagreements.
- 3/8 are the same `10.1021/acs.molpharmaceut.0c00720` ion-pair paper. In all three, adjudication explicitly acknowledges `8 mM`, not `5% w/w`, but still drifts toward verified language.
- 4/8 are `10.1039/d0ra00100g` rows. Their rationales explicitly admit missing concentration certainty and/or unit inconsistency, yet still recommend `verified`.
- The remaining 1/8 (`10.1016/j.ejpb.2020.05.013`) admits that the exact numeric endpoint value is not present in the supplied evidence but still recommends `verified`.
- Manual judgment: 0/8 are clear cases where adjudication should override the pipeline. 8/8 are better explained as adjudication being more permissive than the strict verifier, often in ways that contradict its own sub-findings.
- Therefore Category C does not support giving adjudication override authority in the current strict pipeline.
