# Fix 5 Diagnosis: `cv_only` VLM Rows

## Scope

This diagnosis focuses on the `9` VLM reading artifacts in:

- [figure_vlm_readings.jsonl](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_vlm1\figure_vlm_readings.jsonl)

with:

- `reconciliation_status = cv_only`

The goal is to answer:

1. What VLM label was returned, what CV/pipeline label space existed downstream, and why did they not match?
2. If the label is manually aligned, is the VLM value itself accurate enough to be useful?

## High-Level Conclusion

The `9` `cv_only` artifacts split into two distinct cases:

1. `1` IJPharm row (`10.1016/j.ijpharm.2016.03.043`)
   - This is primarily a **label-space/context failure**.
   - The locked subplot crop does not contain a usable legend.
   - The downstream allowed label space is also wrong for subplot A: it contains dose labels (`1 µL application`, `30 µL application`) rather than the actual subplot-A formulation series.
   - VLM did not return a usable value, so value precision is not assessable here.

2. `8` CPB rows (`10.1248/cpb.c21-00033`)
   - This is **not pure label grounding**.
   - VLM successfully read multiple series-like values from the plot, but attached them to the wrong legend symbols.
   - After manual alignment, only `2/8` values are reasonably close to the visually correct value; the rest are wrong by large margins.
   - Therefore, the next fix should target **legend/series binding**, not reconciliation alone.

## Per-Row Diagnosis

### 1. IJPharm: `10.1016/j.ijpharm.2016.03.043`

Artifact:

- `trace_id = figure_trace_paper_7008480bdcae_7_7_A_f67307c007d3::cluster_1`
- `candidate_tier = triage_primary`
- `subplot_lock_failed = false`
- `readability_status = partially_readable`

#### Returned by VLM

- `formulation_label = ""`
- `legend_label_raw = ""`
- `endpoint_value = null`
- `notes = "Legend includes unknown formulations."`

#### CV / pipeline-side label space

From:

- [figure_curve_map.jsonl](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_vlm1\figure_curve_map.jsonl)

Allowed labels were:

- `30 µL application`
- `1 µL application`

These are not the actual formulation series visible in subplot A. From earlier direct figure diagnosis, subplot A corresponds to four formulation curves, approximately:

- `PG`
- `PEG 300`
- `IBUGEL`
- `IBULEVE`

#### Why it did not match

- The crop itself does not expose a readable legend.
- The downstream label space is paper/table-derived and does not describe the subplot-A series.
- Therefore this row fails before value comparison; VLM has nothing reliable to ground against.

#### If manually aligned, is the VLM value usable?

- No direct comparison is possible because VLM returned no endpoint value for this row.
- This is a **context/grounding failure**, not yet a measurable value-precision failure.

#### Row-level conclusion

- Primary issue: `label_space_context_failure`
- Value accuracy status: `not_assessable`

---

### 2. CPB: `10.1248/cpb.c21-00033`

All `8` remaining `cv_only` artifacts come from the same locked subplot crop:

- `trace_id = figure_trace_paper_567266ad0643_3_4_A_96f8362717a6::cluster_1`
- `candidate_tier = triage_primary`
- `subplot_lock_failed = false`

The crop clearly shows a symbol legend:

- `#1 (○)`
- `#2 (□)`
- `#3 (△)`
- `#4 (◇)`
- `#5 (×)`
- `#6 (◆)`
- `#7 (▲)`
- `#8 (■)`

#### Returned by VLM

For all `8` rows:

- `formulation_label = ""`
- `legend_match_basis = ""`
- `quality_flags = ["labels_not_exhausted"]`

The VLM did at least recognize symbol-like legend identities via `legend_label_raw`, and it returned endpoint values at `8 h`.

#### CV / pipeline-side label space

From:

- [figure_curve_map.jsonl](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_vlm1\figure_curve_map.jsonl)

Allowed labels were collapsed to a single aggregate label:

- `IL preparations #0 to #9`

That means the downstream pipeline had no one-to-one label space for individual series (`#1`, `#2`, ... `#8`).

#### Why it did not match

This failure has two layers:

1. **Pipeline-side grounding failure**
   - VLM identified legend symbols, but downstream only exposed one aggregate label.
   - So even a correct symbol-level read could not ground to a usable formulation label.

2. **VLM symbol-to-value binding failure**
   - The numeric values were not consistently attached to the correct legend symbols.
   - So even after manual symbol alignment, most values are still wrong.

#### Manual alignment check

Below, “correct value” means an approximate visual reading from the original locked subplot at `8 h`.

| Legend symbol | Intended series | VLM value | Approx. correct value | Approx. delta | Diagnosis |
|---|---|---:|---:|---:|---|
| `○` | `Preparation #1` | `75` | `~2` | `+~73` | wrong curve |
| `□` | `Preparation #2` | `28` | `~3` | `+~25` | wrong curve |
| `△` | `Preparation #3` | `40` | `~9-10` | `+~30` | wrong curve |
| `◇` | `Preparation #4` | `20` | `~19-20` | `~0` | approximately correct |
| `×` | `Preparation #5` | `65` | `~31-32` | `+~33` | wrong curve |
| `◆` | `Preparation #6` | `55` | `~48-50` | `+~5-7` | close but high |
| `▲` | `Preparation #7` | `35` | `~68-70` | `-~33` | wrong curve |
| `■` | `Preparation #8` | `40` | `~74-75` | `-~34` | wrong curve |

#### CPB conclusion

- This is **not** a case where the VLM value is already good and only the final label grounding is missing.
- The VLM can see the plot and return numbers, but the association between `legend symbol -> series -> endpoint value` is mostly wrong.
- The only rows that look numerically usable are:
  - `◇` / `Preparation #4`
  - `◆` / `Preparation #6` (roughly close, but still biased high)

#### Row-level conclusion

- Primary issue: `symbol_to_curve_binding_failure`
- Value accuracy status: `partially_usable_but_not_reliable`

## Consolidated Answer

### Is this only a label grounding problem?

No.

- IJPharm is mostly a label-space/context problem.
- CPB is both:
  - downstream label grounding failure, and
  - VLM legend-symbol/value binding failure.

### Is VLM value precision already good enough to use directly?

Not yet.

- For IJPharm, VLM did not return a usable value.
- For CPB, `6/8` symbol-specific values are clearly wrong by large margins.

So the next step should not just relax reconciliation. It should first improve:

1. figure-local label space / legend grounding
2. series identity binding inside the VLM value path

before any broader use of VLM outputs in final direct figure rows.
