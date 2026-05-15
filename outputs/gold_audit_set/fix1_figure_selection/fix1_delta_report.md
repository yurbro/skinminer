# Fix 1 Delta Report

## Scope

This report compares the round-1 gold-audit baseline against Fix 1, which only changed figure/page candidate selection in `extractors/figure/digitize.py` and added `candidate_tier` to digitization artifacts. The validation subset was rerun into `outputs/validation_observability_run_fix1`, then replayed into a conservative matched gold CSV at `outputs/gold_audit_set/fix1_figure_selection/gold_set_seed_round1_after_fix1.csv`. Exact `record_id` joins were used when possible; re-keyed validation rows used the manual mappings logged in `fix1_matching_log.md`.

## Metric Delta

| Metric | Fix before | Fix after | Delta |
|---|---:|---:|---:|
| scope precision | 1.000 | 1.000 | 0.000 |
| end-to-end precision | 0.000 | 0.200 | 0.200 |
| recall | 0.714 | 0.714 | 0.000 |
| verified count | 10 | 10 | 0 |
| value_correct = yes/approximate count | 0 | 2 | 2 |

## Main Outcome

- Scope metrics did not move: scope precision stayed at `1.000`, recall stayed at `0.714`, and verified count stayed at `10`.
- End-to-end precision improved from `0.000` to `0.200` because `gold_value_correct = yes/approximate` increased from `0` to `2`.
- The fix did **not** repair the 7 targeted `figure_misidentified` rows; it instead improved 2 non-target `mapping_error` rows on the same IJPharm paper.
- The new `candidate_tier` field is present in fix1 digitization artifacts and shows that the repaired IJPharm endpoints now came from `triage_primary`.
- The EJPB misidentified row also reports `candidate_tier = triage_primary`, which proves the remaining error is now upstream of fallback selection: triage itself is anchoring the wrong figure/page.

## The 7 targeted `figure_misidentified` rows

| Gold record_id | Mapped fix1 record | Before endpoint | After endpoint | After value verdict | Notes |
|---|---|---|---|---|---|
| `record_47710103a12d` | `record_4fcf67b3f8a8` | 261.17059326171875 ug | 261.17059326171875 ug/mL | no | Still wrong; EJPB digitization remains bound to p.14 calibration content. |
| `record_cc84e1bf6e4e` | `record_5d8638739de7` | 261.17059326171875 ug | 261.17059326171875 ug/mL | no | Still wrong; table-backed row inherits the same misidentified source. |
| `record_e04ec91b3e26` | `record_5d8638739de7` | 261.17059326171875 ug | 261.17059326171875 ug/mL | no | Still wrong; table-backed row still tied to the same EJPB source. |
| `record_437e38b169f5` | `record_af2bc3931fdb` | 90 µg/cm² | 90.0 µg/cm² | no | Still wrong; table contamination remains unchanged. |
| `record_982332825448` | `record_982332825448` | 6.261798858642578 μg/cm² | 6.859661102294922 µg/cm² | no | Still wrong; direct figure row improved slightly but remains below the gold value. |
| `record_a28c8f99f0f6` | `record_a28c8f99f0f6` | 280 µg/cm² | 91.0 µg/cm² | no | Still wrong; table-backed value dropped from 280 to 91 but is still far from the gold endpoint. |
| `record_e5a5cd848fa6` | `record_e5a5cd848fa6` | 280 µg/cm² | 136.0 µg/cm² | no | Still wrong; table-backed value dropped from 280 to 136 but remains far from the gold endpoint. |

## What actually improved

- `record_339f642dd0cd` improved from `30.46 ?g/cm?` to `14.44 ?g/cm?` and was re-labeled `approximate`.
- `record_ca0291b430fe` was conservatively mapped to the same repaired spray endpoint and also re-labeled `approximate`.
- Both improvements are outside the 7-row target set; they are better explained as downstream consequences on the IJPharm figure cluster after primary-page binding was enforced.

## Interpretation

Fix 1 partially improved value accuracy, but not through the expected path. The main target class (`figure_misidentified = 7`) was not repaired, which means the dominant remaining fault is not just ?cross-page fallback beats the right page?. Instead, at least for the EJPB case, the triage-selected primary itself is wrong. The next fix should therefore move one level earlier: tighten figure/page identity between triage and digitization, rather than only reordering fallback candidates.