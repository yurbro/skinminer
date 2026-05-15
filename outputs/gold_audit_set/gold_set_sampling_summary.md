# Gold Set Sampling Summary

## Decision
The follow-up sampling request is reasonable and consistent with the current code freeze, because it only samples from existing run outputs and produces evaluation assets without modifying pipeline logic.

## Inputs
- Existing figure-heavy seed: `outputs/validation_observability_run/report/gold_set_seed_figure_validation.csv`
- Supplemental run outputs: `outputs/full_run_12_full/verified_records.jsonl`
- Random seed: `42`

## Stratified Sampling Outcome

| Stratum | Definition | Candidate count in `full_run_12_full` | Actual selected | Mode | Notes |
|---|---|---:|---:|---|---|
| A | verified + table | 0 | 0 | exhaustive | No non-figure verified table records were available. |
| B | verified + text/mixed | 0 | 0 | exhaustive | No non-figure verified text/mixed records were available. |
| C | unresolved + table | 13 | 13 | exhaustive | Leftover quota from empty A/B strata redistributed here. |
| D | unresolved + text/mixed | 22 | 22 | exhaustive | Leftover quota from empty A/B strata redistributed here. |
| E | unresolved + targeted failure coverage | 0 dedicated | 0 | not separately sampled | Top failure buckets were already covered within exhaustive C/D inclusion, so no duplicate E rows were added. |
| F | rejected + any non-figure route | 5 | 5 | exhaustive | All non-figure rejected rows were included as sanity-check samples. |

## Failure-Bucket Coverage Achieved Within C/D
- `recoverable_support_gap / insufficient_evidence`: 31 rows
- `recoverable_api_basis / ambiguous_api_concentration`: 15 rows
- `recoverable_endpoint / missing_endpoint`: 6 rows

All three required unresolved failure patterns reached the requested minimum coverage within strata C/D, so no dedicated E oversampling was necessary.

## Merge Strategy
- Figure route was **not** resampled from `full_run_12_full`.
- The existing validation-run figure seed (`31` rows) was retained as the figure component of round 1.
- Supplemental sampling from `full_run_12_full` added `40` non-figure rows.
- Final merged audit seed contains `71` rows.

## Schema Alignment Applied
The existing figure seed was aligned to the requested round-1 schema.

Applied adjustments:
- Collapsed `evidence_preview_1`, `evidence_preview_2`, and `source_notes_preview` into a single `evidence_preview` column.
- Added blank `gold_endpoint_value_correct` column.
- Removed extra seed-only columns from the merged output schema, including `seed_group`, `seed_note`, `scope_bucket`, `api_concentration_raw`, `normalized_value`, `normalized_unit`, `verification_support_rate`, and `gold_decision`.
- Preserved existing `paper_url` values from the validation seed.
- Filled supplemental `paper_url` values from `content_access.jsonl` using preferred OA URLs, falling back to DOI URLs where needed.

## Sort Order
The final CSV is sorted by:
1. `route`: `table -> text -> mixed -> figure`
2. `verification_status`: `verified -> unresolved -> rejected`
3. `doi`, then `record_id`

## Annotation Guidance
CSV files do not support reliable header comments, so the annotation instructions are recorded here instead of inline in the file.

- Judge each gold column independently.
- `gold_keep_record` should be `yes` only when the strict-scope fields are all satisfied: target API, `5% w/w`, Franz, IVPT/IVRT, amount endpoint, and endpoint time.
- Use `gold_endpoint_value_correct = approximate` when the extracted endpoint value is close but differs only by rounding or minor formatting.
- Use `gold_area_ok = n_a` when neither the paper nor the pipeline reports diffusion area.
- Always inspect `paper_url`; do not annotate solely from `evidence_preview`.
