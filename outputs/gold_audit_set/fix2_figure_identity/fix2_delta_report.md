# Fix 2 Delta Report

## Scope

This report compares Fix 1 against Fix 2 on the round-1 gold audit set. Fix 2 added a semantic gate in figure triage (`figure_semantic_type`) and subplot-aware locking in digitization, with explicit `subplot_lock_failed` tracking. The validation subset was rerun into `outputs/validation_observability_run_fix2`, then conservatively overlaid into `outputs/gold_audit_set/fix2_figure_identity/gold_set_seed_round1_after_fix2.csv`.

## Metric Delta

| Metric | Fix 1 | Fix 2 | Delta |
|---|---:|---:|---:|
| precision | 1.000 | 1.000 | 0.000 |
| recall | 0.714 | 0.500 | -0.214 |
| F1 | 0.833 | 0.667 | -0.167 |
| scope precision | 1.000 | 1.000 | 0.000 |
| end-to-end precision | 0.200 | 0.000 | -0.200 |
| verified count | 10 | 7 | -3 |
| value-correct yes/approx | 2 | 0 | -2 |

## Main Outcome

- Fix 2 successfully removed the three EJPB calibration-curve false positives from `verified`; they are now `unresolved` with `missing_endpoint + unit_normalization_failed + figure_digitization_failed`.
- Precision stayed at `1.000` because all remaining `verified` rows are still in-scope according to the gold audit.
- Recall dropped from `0.714` to `0.500` because those three EJPB rows no longer produce a retained endpoint record.
- End-to-end precision dropped from `0.200` back to `0.000`: the two IJPharm rows that were only `approximate` under Fix 1 are no longer approximately correct after the new run.
- The new observability fields show why: IJPharm digitization still runs with `candidate_tier=triage_primary`, but triage now emits `subplot="A, B, C, D"`, so `subplot_lock_failed` stays `false` and the subplot lock never actually engages.

## Targeted Rows

| Gold record_id | Fix2 status | Fix2 endpoint | value verdict | Note |
|---|---|---|---|---|
| `record_1d882e0e9090` | verified | 18.625953674316406 μg/cm² @ 48.0 h | no | Closest retained fix2 row used conservatively; still value-wrong. |
| `record_339f642dd0cd` | verified | 26.946565628051758 μg/cm² @ 48.0 h | no | Mapped to current spray-48h fix2 row; still value-wrong. |
| `record_437e38b169f5` | verified | 60.0 μg/cm² @ 6.0 h | no | Closest retained fix2 row used conservatively; still value-wrong. |
| `record_47710103a12d` | unresolved | ? | no | EJPB calibration figure gated out; no endpoint survives. |
| `record_982332825448` | verified | 38.0 μg/cm² @ 48.0 h | no | Mapped to current IBUGEL-labelled fix2 row; still value-wrong. |
| `record_a28c8f99f0f6` | verified | 38.0 μg/cm² @ 48.0 h | no | Closest retained fix2 row used conservatively; still value-wrong. |
| `record_ca0291b430fe` | verified | 26.946565628051758 μg/cm² @ 48.0 h | no | Mapped to current spray-48h fix2 row; still value-wrong. |
| `record_cc84e1bf6e4e` | unresolved | ? | no | EJPB calibration figure gated out; no endpoint survives. |
| `record_e04ec91b3e26` | unresolved | ? | no | EJPB calibration figure gated out; no endpoint survives. |
| `record_e5a5cd848fa6` | verified | 38.0 μg/cm² @ 48.0 h | no | Closest retained fix2 row used conservatively; still value-wrong. |

## Interpretation

Fix 2 is still useful, but not for the original reason. It **does** fix the EJPB triage semantic mistake: a calibration curve is no longer allowed to survive as a permeation endpoint. However, it does **not** yet solve the IJPharm direct-figure value problem, because the current triage-to-digitize handoff no longer identifies a single subplot. The downstream digitizer therefore remains bound to a multi-panel `A, B, C, D` crop, and the new `subplot_lock_failed` flag never fires because no single-subplot lock was attempted.

The next fix should therefore move one step earlier than digitization fallback: tighten the triage output contract so that digitization receives a single page + single subplot identity for direct figure records, or explicitly marks the subplot as ambiguous before any value is trusted.