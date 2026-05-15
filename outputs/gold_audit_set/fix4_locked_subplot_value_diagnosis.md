# Fix 4 Locked-Subplot Value Diagnosis

## Scope

This diagnosis focuses on the IJPharm paper:

- DOI: `10.1016/j.ijpharm.2016.03.043`
- validation run: [validation_observability_run_fix3a](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a)

The goal is to diagnose the rows whose page/subplot identity is already correct after Fix 3a, but whose endpoint values are still wrong.

## Important Separation

There are **two different error families** inside the IJPharm outputs:

1. **Direct locked-subplot figure rows**
   - These come from `figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f`
   - They are true direct outputs from locked subplot `A`
   - They produce four curve clusters in [figure_curves.jsonl](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a\figure_curves.jsonl)

2. **Cross-modal contamination rows**
   - `record_e5a5cd848fa6`
   - `record_2b009f46d9d5`
   - These are **not** direct locked-subplot outputs
   - `record_e5a5cd848fa6` is table-backed (`280 µg/cm² @ 6 h`)
   - `record_2b009f46d9d5` had no endpoint in `assembled_records`, then `patch_endpoint_value` promoted `27.0229 µg/cm²` from shared hints into a `6 h` row

So the direct locked-subplot value path should be diagnosed on the **four cluster-backed rows**, not on the two contaminated `6 h` rows.

## 1. How many curves were detected on locked subplot A?

Digitization on locked subplot `A` detected **4 clusters**:

| curve_id | point_count | t_last | q_final |
|---|---:|---:|---:|
| `cluster_1` | 529 | 48.0 h | 27.0229 µg/cm² |
| `cluster_2` | 501 | 48.0 h | 26.9466 µg/cm² |
| `cluster_3` | 148 | 48.0 h | 18.6260 µg/cm² |
| `cluster_4` | 506 | 48.0 h | 41.4504 µg/cm² |

The full point data have been exported to:

- [fix4_ijpharm_value_path_curve_points.json](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\fix4_ijpharm_value_path_curve_points.json)

## 2. What do the detected curves actually look like?

The locked subplot image is:

- [p7 triage image](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a\figure\triage_images\10.1016_j.ijpharm.2016.03.043__p7.jpg)

The locked crop is:

- [digitize crop](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a\figure\digitize_crops\figure_trace_paper_7008480bdcae_1_7_A_543a3a2add8f.png)

The critical observation is that the four detected clusters are **not four clean centerlines**:

- `cluster_1` and `cluster_2` are large noisy clusters with hundreds of points, including:
  - long horizontal bands around `y ≈ 21–24`
  - late spikes around `y ≈ 41`
  - terminal drops to `~27`
- `cluster_3` is smaller and visually closer to a real lower curve
- `cluster_4` contains a real high-curve tail near `~41`, but also mixes in mid-level and horizontal artifact segments

This means the current `curve_xy` output is not a clean curve trace. It is a mixture of:

- marker centers
- error bars
- local horizontal artifacts
- tail spikes

So even before mapping, the value path is unstable.

## 3. How were the curves mapped?

The current mapping file is:

- [figure_curve_map.jsonl](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a\figure_curve_map.jsonl)

For IJPharm, the mapping output is:

| curve_id | mapped_formulation_label | mapping_status |
|---|---|---|
| `cluster_1` | `IBULEVE™ Speed Relief` | `vision_mapped` |
| `cluster_2` | `IBULEVE™ Speed Relief` | `vision_mapped` |
| `cluster_3` | `IBUGEL™` | `vision_mapped` |
| `cluster_4` | `IBUGEL™` | `vision_mapped` |

### Is that mapping correct?

No, not at paper level.

The original subplot `A` visibly contains **four formulations**, not two:

- IBUGEL
- IBULEVE
- PG
- PEG 300

But the mapping stage only sees:

- `allowed_formulation_labels = ["IBUGEL™", "IBULEVE™ Speed Relief"]`

because the table branch only emitted two source rows for this paper.

So mapping is **underconstrained by construction**:

- 4 detected curves
- only 2 allowed labels

This guarantees collapse of at least two real curves into the wrong formulation labels.

## 4. Which curve and timepoint produced the final endpoint values?

For the true direct figure rows, the pipeline records the endpoint as the cluster's `q_final` at `t_last = 48 h`.

| final record_id | formulation label | source curve | source timepoint | recorded endpoint_value |
|---|---|---|---|---:|
| `record_b073c5f64b07` | `IBULEVE™ Speed Relief` | `cluster_1` | `48 h` | `27.0229 µg/cm²` |
| `record_ea72818ca66b` | `IBULEVE™ Speed Relief` | `cluster_2` | `48 h` | `26.9466 µg/cm²` |
| `record_fb1af90cc9e4` | `IBUGEL™` | `cluster_3` | `48 h` | `18.6260 µg/cm²` |
| `record_bf2d5ce7bce2` | `IBUGEL™` | `cluster_4` | `48 h` | `41.4504 µg/cm²` |

For the two contaminated rows:

| final record_id | actual source |
|---|---|
| `record_e5a5cd848fa6` | table-backed `280 µg/cm² @ 6 h` statement, not locked subplot A |
| `record_2b009f46d9d5` | `patch_endpoint_value` promoted `27.0229 µg/cm²` from shared hints into a `6 h` row |

## 5. What should the correct values be?

From the original paper page 7, Figure 1(A) shows human skin cumulative amounts at `48 h`.

Relevant source:

- [PDF page 7](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\papers\pdf\10.1016_j.ijpharm.2016.03.043__d92e739f32.pdf)

Approximate visual readout of subplot `A` at `48 h`:

| visible curve | approximate correct 48 h endpoint |
|---|---:|
| PG (highest, green triangles) | `~38 µg/cm²` |
| PEG 300 (mid, circles) | `~17 µg/cm²` |
| IBUGEL (mid-low, diamonds) | `~15–16 µg/cm²` |
| IBULEVE (lowest, squares) | `~10–11 µg/cm²` |

These are also consistent with the paper text:

- human skin maximum permeation is `~40 µg/cm²`
- porcine skin maximum permeation is `~80 µg/cm²`

So the current direct outputs are wrong in the following way:

| source curve | current value | likely true interpretation | error type |
|---|---:|---|---|
| `cluster_1` | `27.0229` | no clean human-skin curve at this level; likely artifact/mixed trace | wrong curve / artifact contamination |
| `cluster_2` | `26.9466` | same as above | wrong curve / artifact contamination |
| `cluster_3` | `18.6260` | close to one real lower curve (`~17`), but then mapped to `IBUGEL` | mostly mapping error |
| `cluster_4` | `41.4504` | close to the highest human-skin curve (`PG`), not `IBUGEL` | wrong formulation mapping |

For the two contaminated `6 h` rows:

| record_id | current value | correct interpretation | error type |
|---|---:|---|---|
| `record_e5a5cd848fa6` | `280 @ 6 h` | generic commercial-formulation statement from text/table, not a direct per-formulation figure value | cross-modal contamination |
| `record_2b009f46d9d5` | `27.0229 @ 6 h` | `48 h` cluster value copied into a `6 h` unresolved row | wrong timepoint via shared-hint promotion |

## Diagnostic Conclusion

The remaining IJPharm errors are **not one single bug**.

There are two direct figure-path failures:

1. **Curve extraction is noisy**
   - the raw clusters are not clean centerlines
   - `q_final` is currently taken from a noisy terminal point

2. **Mapping is underconstrained**
   - 4 real subplot curves
   - only 2 allowed labels
   - so map-curves collapses four curves into two commercial formulations

And there is a separate non-direct problem:

3. **Cross-modal contamination**
   - shared hints and table text can still inject `6 h` endpoints that are not direct figure values

For Fix 4, the direct locked-subplot value path should focus on the first two issues. The contaminated `6 h` rows should be handled later as a separate cross-modal fix.
