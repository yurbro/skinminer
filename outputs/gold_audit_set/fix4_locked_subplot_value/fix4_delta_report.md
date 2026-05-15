# Fix 4 Delta Report

## Scope

Fix 4 targeted the locked-subplot value path only:

- `digitize.py`: sanitize cluster centerlines and sample endpoint values from a stable right-tail window
- `map_curves.py`: stop forcing many-to-few mapping when `detected_curve_count > allowed_label_count` and emit `underconstrained_labels` instead
- `models.py`: add raw/sanitized value observability and mapping label-space observability

The validation subset was rerun into [validation_observability_run_fix4](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix4), then conservatively overlaid into [gold_set_seed_round1_after_fix4.csv](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\fix4_locked_subplot_value\gold_set_seed_round1_after_fix4.csv).

## Metric Delta

| Metric | Fix 3a | Fix 4 | Delta |
|---|---:|---:|---:|
| precision | 1.000 | 1.000 | +0.000 |
| recall | 0.500 | 0.500 | +0.000 |
| F1 | 0.667 | 0.667 | +0.000 |
| scope precision | 1.000 | 1.000 | +0.000 |
| end-to-end precision | 0.000 | 0.000 | +0.000 |
| verified count | 7 | 7 | +0 |

## IJPharm Locked-Subplot Value Path

Fix 4 materially changed the direct subplot-A endpoint values, even though the gold precision metrics stayed flat.

| curve_id | raw endpoint | sanitized endpoint | sampling status | mapped formulation |
|---|---:|---:|---|---|
| cluster_1 | 27.0229 | 23.2824 | stable_tail | IBULEVE™ Speed Relief 5% Spray |
| cluster_2 | 26.9466 | 13.2443 | stable_tail | Ibuprofen in PEG 300 Solution |
| cluster_3 | 18.6260 | 21.4504 | stable_tail | IBULEVE™ Speed Relief 5% Spray |
| cluster_4 | 41.4504 | 16.1832 | stable_tail | Ibuprofen in Propylene Glycol Solution |

The sanitized values are more plausible than the raw tail-point readings:

- `cluster_4`: `41.45 -> 16.18`
- `cluster_2`: `26.95 -> 13.24`
- `cluster_1`: `27.02 -> 23.28`
- `cluster_3`: `18.63 -> 21.45`

But the gold-set metrics do not move because the remaining verified IJPharm rows are still value-wrong under the conservative audit overlay. The failure has shifted from raw tail sampling toward curve identity / formulation assignment and cross-modal value reuse.

## underconstrained_labels Confirmation

Fix 4 emitted `5` `underconstrained_labels` mapping artifacts across `2` papers:

- `10.1208/s12249-019-1584-8`
- `10.1248/cpb.c21-00033`

There were `0` verified rows carrying one of those underconstrained curve trace IDs.

This confirms the requested behavior: once a figure is marked `underconstrained_labels`, it does **not** survive into a verified direct-figure row.

In the validation run, the affected papers only survive through unresolved paper-level rows:

- `10.1248/cpb.c21-00033` -> `record_b187ebe51002` (`unresolved`)
- `10.1208/s12249-019-1584-8` -> `record_c3fdc7aafe21`, `record_7fd439bfefc2` (`unresolved`)

## Conclusion

Fix 4 is **correct as a value-path and safety fix**, but **neutral on gold metrics** under the current conservative overlay.

- It improves raw endpoint extraction inside the locked subplot.
- It adds the correct guardrail for underconstrained label spaces.
- It confirms that underconstrained figure rows now fall into unresolved behavior rather than verified behavior.
- It does not yet recover end-to-end precision because the remaining IJPharm errors are now downstream in curve identity, formulation assignment, and cross-modal contamination.

The next fix should therefore target **curve identity / mapping correctness after subplot lock**, not more tail smoothing and not Fix 3b page retry yet.