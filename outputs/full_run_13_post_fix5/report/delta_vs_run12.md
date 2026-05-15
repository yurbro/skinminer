# Full Run Delta: full_run_12 → full_run_13

## Overall

| Metric | full_run_12 | full_run_13 | Delta |
|---|---:|---:|---:|
| assembled | 95 | 79 | -16 |
| verified | 8 | 4 | -4 |
| unresolved | 66 | 48 | -18 |
| rejected | 21 | 27 | +6 |

## By Route

### Routing

| Route | full_run_12 | full_run_13 | Delta |
|---|---:|---:|---:|
| figure | 19 | 24 | +5 |
| mixed | 4 | 6 | +2 |
| table | 18 | 13 | -5 |
| text | 11 | 9 | -2 |
| unresolved | 487 | 477 | -10 |

### Extractor Outputs

| Output | full_run_12 | full_run_13 | Delta |
|---|---:|---:|---:|
| table records | 67 | 64 | -3 |
| text records | 14 | 11 | -3 |
| figure records | 28 | 9 | -19 |

## Failure Taxonomy Changes

Largest increases:

- `ambiguous_api_concentration`: `33 -> 42` (`+9`)
- `figure_digitization_failed`: `2 -> 8` (`+6`)
- `not_target_api`: `9 -> 16` (`+7`)
- `missing_endpoint`: `8 -> 11` (`+3`)

Largest decreases:

- `insufficient_evidence`: `64 -> 54` (`-10`)
- `not_target_api_concentration`: `16 -> 10` (`-6`)
- `missing_api_concentration`: `7 -> 1` (`-6`)
- `missing_area`: `19 -> 14` (`-5`)
- `not_target_device`: `5 -> 3` (`-2`)

Interpretation: post-Fix-5 code is less likely to let weak figure rows masquerade as confident outputs, but more likely to expose figure-specific failure modes explicitly.

## Figure Pipeline

| Metric | full_run_12 | full_run_13 | Delta |
|---|---:|---:|---:|
| triage artifacts | 20 | 22 | +2 |
| triage has permeation plot true | n/a | 19 | n/a |
| triage digitize candidates | 17 | 19 | +2 |
| digitized curves | 31 | 25 | -6 |
| digitized endpoints ok | 31 | 25 | -6 |
| digitized endpoints failed | 0 | 9 | +9 |
| digitization no output | 0 | 6 | +6 |
| mapped curves | 31 | 12 | -19 |
| unmapped curves | 0 | 13 | +13 |
| VLM readings total | 0 | 26 | +26 |
| VLM readings readable | 0 | 21 | +21 |
| VLM used as final | 0 | 8 | +8 |

### New Figure Failure Signals in full_run_13

- digitization failures:
  - `digitization_no_output = 6`
  - `fail_missing_axis_range = 3`
- mapping failures:
  - `underconstrained_label_space_3_curves_2_labels = 3`
  - `underconstrained_label_space_4_curves_1_labels = 4`
  - `underconstrained_label_space_6_curves_2_labels = 6`
- VLM reconciliation:
  - `cv_only = 9`
  - `cv_vlm_disagreement = 4`
  - `vlm_only = 8`
  - `unreadable = 5`

## LLM Adjudication

`full_run_12` had adjudication disabled. `full_run_13` processed `33` rows:

- candidate reasons:
  - `recoverable_unresolved:ambiguous_api_concentration = 26`
  - `recoverable_unresolved:missing_endpoint = 6`
  - `recoverable_unresolved:unit_normalization_failed = 1`
- recommendations:
  - `unresolved = 27`
  - `rejected = 6`

This second-opinion layer did not rescue any rows; it behaved as a conservative risk filter.

## Cost

| Metric | full_run_12 | full_run_13 | Delta |
|---|---:|---:|---:|
| elapsed seconds | 5110.9 | 5003.0 | -107.9 |
| total tokens | 3,557,327 | 3,838,632 | +281,305 |

The token increase is mainly due to new `figure_vlm` and `llm_adjudicate` stages.

## Key Observations

1. The biggest change is not more verified rows; it is a safer figure stack. `figure records` fell from `28` to `9`, while explicit figure failure and VLM observability rose sharply.
2. Post-Fix-5 logic reduced unresolved and missing-area style ambiguity, but it also converted previously permissive figure outputs into `underconstrained` or failed figure rows.
3. VLM is now active in the full baseline and produces readable outputs, but it is not yet translating into more verified rows.
4. Adjudication added useful audit structure but currently acts only as a conservative unresolved triage layer.
5. `full_run_13` is therefore a better experimental baseline than `full_run_12`, even though its verified count is lower.
