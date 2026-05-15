# Fix 4 Proposal: Locked-Subplot Value Path

## Goal

Fix the remaining direct figure-value errors **after** page and subplot identity are already correct.

This fix should target only the IJPharm-style direct value path:

- locked subplot is correct
- direct digitization runs on the intended panel
- values are still wrong because the extracted clusters are noisy and mapping is underconstrained

This fix does **not** attempt to solve:

- paper-level reject-and-retry (`Fix 3b`)
- table/text cross-modal contamination
- broad verification policy changes

## Proposed Scope

Only touch:

- [digitize.py](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\extractors\figure\digitize.py)
- [models.py](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\extractors\figure\models.py)
- [map_curves.py](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\extractors\figure\map_curves.py)

Do **not** touch:

- `triage.py`
- `assembly`
- `verification`
- `patch_endpoint`

## Fix 4a: Robust endpoint extraction from locked subplot

### Problem

Current `curve_xy` clusters mix:

- marker centers
- error bars
- horizontal artifacts
- tail spikes

and `q_final` is effectively read from the raw tail of that mixed cluster.

### Change

Inside `digitize.py`, after cluster extraction:

1. Build a **sanitized centerline** per cluster:
   - bin points by `x`
   - within each `x` bin, keep a robust central `y` representative rather than all raw points
   - suppress obvious vertical error-bar segments and isolated spikes

2. Compute the endpoint from a **right-edge sampling window**, not from the last raw point:
   - sample the cluster within `x >= x_max - Δ`
   - use a robust statistic on that tail window
   - record both raw and sanitized endpoint values for observability

3. If the cluster tail is unstable, mark it explicitly rather than trusting it silently.

### New observability fields

Add to the digitization artifact:

- `curve_point_count_raw`
- `curve_point_count_sanitized`
- `endpoint_value_raw`
- `endpoint_value_sanitized`
- `endpoint_sampling_status`
  - `stable_tail`
  - `unstable_tail`
  - `too_sparse`

This keeps the next evaluation round auditable.

## Fix 4b: Prevent many-to-few forced mapping

### Problem

For IJPharm subplot A:

- detected curves: `4`
- allowed formulation labels: `2`

Current `map_curves.py` still forces all four curves into those two labels.

### Change

Add a hard guard in `map_curves.py`:

- if `detected_curve_count > allowed_formulation_label_count`
- and no additional safe label source exists
- mark the trace as `underconstrained_labels`
- do **not** force all curves into the small label set

For the retained subset, only map curves when the label space is plausibly complete enough.

### New observability fields

Add to mapping output:

- `mapping_label_space_status`
  - `complete`
  - `underconstrained`
- `detected_curve_count`
- `allowed_label_count`

## Expected Effect

This fix is designed to improve **direct figure end-to-end precision**, not recall.

Expected gains:

- remove phantom `~27 µg/cm²` rows created from noisy tail artifacts
- stop assigning PG/PEG300-like curves to commercial labels when only two labels are available
- make any surviving direct figure rows more likely to have numerically plausible endpoints

Expected non-goals:

- it will not recover the EJPB retry gap
- it will not fix `record_e5a5cd848fa6` / `record_2b009f46d9d5` style cross-modal contamination

## Evaluation Plan

Use the same workflow as Fix 1 / Fix 2 / Fix 3a:

1. rerun the validation subset
2. rebuild a conservative gold overlay
3. rerun `evaluation.score_run`
4. produce a delta report

Primary success criterion:

- `end-to-end precision` rises above `0.000`

Secondary success criteria:

- fewer direct figure false positives on IJPharm
- new observability fields clearly show whether surviving rows come from stable-tail sampling and non-underconstrained mapping
