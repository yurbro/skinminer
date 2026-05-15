# E2 Delta: baseline (GPT-4o-mini) -> E2 (GPT-5.4-mini/5.4)

## Overall

| Metric | Baseline (4o-mini) | E2 (5.4-mini/5.4) | Delta |
|---|---:|---:|---:|
| assembled | 79 | 61 | -18 |
| verified | 4 | 4 | +0 |
| unresolved | 48 | 47 | -1 |
| rejected | 27 | 10 | -17 |
| triaged_rows | 529 | 267 | -262 |
| route_decisions | 529 | 267 | -262 |

## By Route

| Route | Baseline verified | E2 verified | Baseline unresolved | E2 unresolved |
|---|---:|---:|---:|---:|
| table | 0 | 0 | 10 | 8 |
| text | 0 | 0 | 9 | 2 |
| mixed | 0 | 0 | 4 | 33 |
| figure | 4 | 4 | 25 | 4 |

## Failure Taxonomy Changes

| failure_reason | Baseline | E2 | Delta |
|---|---:|---:|---:|
| insufficient_evidence | 54 | 24 | -30 |
| ambiguous_api_concentration | 42 | 23 | -19 |
| figure_digitization_failed | 8 | 1 | -7 |
| not_target_api_concentration | 10 | 3 | -7 |
| missing_endpoint | 11 | 3 | -8 |
| missing_area | 14 | 20 | +6 |
| missing_api_concentration | 1 | 9 | +8 |
| unit_normalization_failed | 3 | 9 | +6 |
| not_target_api | 16 | 7 | -9 |
| not_target_study_type | 12 | 3 | -9 |
| percent_only | 6 | 4 | -2 |
| ambiguous_mapping | 0 | 1 | +1 |
| missing_endpoint_time | 2 | 0 | -2 |
| not_target_device | 3 | 0 | -3 |

## Figure Pipeline

| Metric | Baseline | E2 | Delta |
|---|---:|---:|---:|
| figure records | 9 | 4 | -5 |
| triage_artifacts | 22 | 7 | -15 |
| triage_has_permeation_plot_true | 19 | 4 | -15 |
| triage_digitize_candidates | 19 | 4 | -15 |
| digitized_curves | 25 | 7 | -18 |
| digitized_endpoints_ok | 25 | 7 | -18 |
| digitized_endpoints_failed | 9 | 2 | -7 |
| digitization_no_output | 6 | 2 | -4 |
| mapped_curves | 12 | 7 | -5 |
| unmapped_curves | 13 | 0 | -13 |
| vlm_readings_total | 26 | 7 | -19 |
| vlm_readings_readable | 21 | 7 | -14 |
| vlm_used_as_final | 8 | 3 | -5 |

## Non-Figure Verified Breakthrough?

| Route | E2 verified count | Notes |
|---|---:|---|
| table | 0 | no verified records |
| text | 0 | no verified records |
| mixed | 0 | no verified records |

## Cost Comparison

| Metric | Baseline | E2 | Delta |
|---|---:|---:|---:|
| total input tokens | 3,669,068 | 1,255,385 | -2,413,683 |
| total output tokens | 169,564 | 249,629 | +80,065 |
| total tokens | 3,838,632 | 1,505,014 | -2,333,618 |
| elapsed seconds | 5003 | 3668 | -1,335 |
| estimated API cost | $0.652 | $2.082 | $1.430 |

## Key Observations

1. Verified output did not improve: baseline and E2 both end at 4 verified records.
2. The two largest unresolved buckets shrank numerically but mostly because the pipeline became much more selective upstream: insufficient_evidence 54 -> 24, ambiguous_api_concentration 42 -> 23.
3. Non-figure routes still produced zero verified records in E2; the verified=0 deadlock for table/text/mixed was not broken.
4. Figure VLM became cleaner but not more valuable end-to-end: vlm_used_as_final 8 -> 3, mapped_curves 12 -> 7, figure verified records stayed at 4.
5. E2 cut total token usage sharply (3,838,632 -> 1,505,014) but increased estimated spend ($0.652 -> $2.082), because GPT-5.4-mini/5.4 pricing is much higher per token and the run gained no additional verified yield.
