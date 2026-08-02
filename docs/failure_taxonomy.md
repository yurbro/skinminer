# Failure taxonomy

SkinMiner distinguishes transport failures, structural parsing failures, scientific scope errors, numeric interpretation errors, and audit limitations. A record can be valid JSON and still be scientifically unusable.

## Corpus and access failures

| Failure | Signal | Consequence | Mitigation |
|---|---|---|---|
| Bibliographic false positive | Query match lacks a dermal diffusion study | Unnecessary routing and extraction | Rule triage, LLM triage, and gold scope audit |
| No usable full text | OA resolver finds no permitted HTML, XML, or PDF | Paper remains unresolved | Preserve DOI and access status; retry through permitted sources |
| Incomplete page source | Remote HTML or XML omits tables or figures | Missing modalities or fields | Route to another available representation and record backend provenance |

## Routing failures

| Failure | Signal | Consequence | Mitigation |
|---|---|---|---|
| Wrong modality | Relevant endpoint is in a figure while routing selects text | Missing endpoint or irrelevant value | Multi-route detection and route-specific audit |
| Calibration figure selected | Analytical calibration resembles a permeation profile | Non-target values enter figure extraction | Figure classification and retry on alternate candidate pages |
| Table truncation | Large table exceeds row or page limits | Partial formulation coverage | Truncation markers and unresolved status |

## Extraction failures

### Text and table routes

- A formulation label can detach from its endpoint row.
- Units can attach to the wrong numeric column.
- Multi-level headers can collapse concentration, time, and endpoint semantics.
- Narrative methods can be mistaken for measured results.
- A table can report a formulation recipe without reporting a dermal endpoint.

Typed schemas catch malformed structures. Verification must still assess scientific meaning.

### Figure digitization

Figure-derived values have additional error sources:

- panel selection errors
- axis-origin and scale calibration errors
- linear versus logarithmic axis confusion
- curve-color or marker assignment errors
- legend-to-formulation mismatches
- pixel quantization and anti-aliasing
- overlapping curves and sparse markers
- time-unit and area-normalization errors

The reproducibility runs show that figure-derived endpoints are less stable than text and table records. The same scientific profile produced endpoint estimates such as 150.76 and 250.0 in different runs when candidate selection or digitization changed. Treat figure values as auditable estimates and preserve the panel, axis, and curve provenance.

## Assembly and verification failures

| Failure | Example | Result |
|---|---|---|
| Record fragmentation | Formulation and endpoint arrive from separate modalities | Duplicate or incomplete records |
| Incorrect merge | Similar formulation labels refer to different experimental arms | Cross-arm contamination |
| Wrong active ingredient | Ibuprofen appears only as comparator or background | Scope false positive |
| Wrong device | Microneedle, release bottle, or non-Franz system passes lexical checks | Scope false positive |
| Wrong endpoint | Solubility, concentration, calibration, or percent release is treated as permeated amount | Endpoint false positive |
| Wrong unit basis | mg/kg, mg/mL, µg/cm², and flux units are conflated | Magnitude and scope error |
| Missing endpoint time | A value lacks a defensible time point | Unresolved record |

## Patcher risks

Patchers target recurring errors with deterministic rules. An over-broad patch can modify a valid record, while a narrow patch can miss a variant. Each patch therefore records its reason and leaves the original provenance auditable. Regression tests should cover both the intended correction and a nearby negative case.

## SP-4 silent failure

SP-4 did not fail through wholesale JSON serialization. It returned schema-valid output for 23 of 29 PDFs and emitted 132 parseable records. The failure was silent at the scientific layer:

- 0 of 25 gold true positives were recovered.
- 8 emitted records aligned with 5 annotated out-of-scope gold rows.
- 124 records had no record-level gold counterpart.
- Six paper calls left no usable structured record set.
- Common errors involved study scope, active ingredient, endpoint selection, units, and unsupported record proliferation.

Schema validation alone therefore overstates success. A single-pass system needs semantic matching, scope evaluation, and negative audits in addition to parse-rate monitoring.

## Evaluation limitations

The 130-row Round-2 gold CSV is a stratified audit sample. Extra single-pass records that do not match a gold row are not automatically proven false positives. Statements such as 18 annotated negative matches describe interaction with the sampled annotations, not an exhaustive error count across every emitted record.

The Fig. 7A R² uses 24 exact manual labels as equality anchors and one near label as an independent numeric value. The 96% value-accuracy result is the more direct manual correctness measure.

## Triage checklist

When a result looks plausible but unexpected, check in this order:

1. Confirm DOI, active ingredient, study type, and device scope.
2. Confirm source modality, table or figure locator, and experimental arm.
3. Confirm endpoint kind, numeric value, unit, time, and area basis.
4. Confirm cumulative policy membership.
5. Compare against the gold sample and inspect unmatched outputs separately.
6. Retain an unresolved status when the source cannot support a unique interpretation.

