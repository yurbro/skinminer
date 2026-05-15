# Fix 3a Delta Report

## Scope

This report compares Fix 2 against Fix 3a on the round-1 gold audit set.

Fix 3a targeted the triage-to-digitize subplot identity contract only:

- triage now emits a single subplot for multi-panel figures
- `subplot_raw` is preserved for observability
- `subplot_selection_status` records whether the subplot was already single or coerced from a multi-panel response

The validation subset was rerun into [validation_observability_run_fix3a](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a), then conservatively overlaid into [gold_set_seed_round1_after_fix3a.csv](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\fix3a_subplot_identity\gold_set_seed_round1_after_fix3a.csv).

## Metric Delta

| Metric | Fix 2 | Fix 3a | Delta |
|---|---:|---:|---:|
| precision | 1.000 | 1.000 | 0.000 |
| recall | 0.500 | 0.500 | 0.000 |
| F1 | 0.667 | 0.667 | 0.000 |
| scope precision | 1.000 | 1.000 | 0.000 |
| end-to-end precision | 0.000 | 0.000 | 0.000 |
| verified count | 7 | 7 | 0 |
| value-correct yes/approx | 0 | 0 | 0 |

## What Fix 3a Did Correctly

- The EJPB calibration row remains correctly gated out:
  - triage now marks it as `figure_semantic_type=calibration_curve`
  - `recommended_route=skip`
  - the gold overlay still maps the three EJPB rows to one unresolved calibration-gated artifact, which is the correct behavior

- The IJPharm triage contract ambiguity is now removed:
  - Fix 2 problem: triage could emit `subplot="A, B, C, D"`
  - Fix 3a behavior: triage now emits `subplot_raw="A"` and `subplot_selection_status="single"` for the retained IJPharm trace
  - digitization now runs with:
    - `candidate_tier=triage_primary`
    - `subplot="A"`
    - `subplot_lock_failed=false`

This means the system is no longer silently digitizing a multi-panel figure under an ambiguous `A, B, C, D` contract.

## Why The Gold Metrics Stayed Flat

Although the subplot contract is now correct, the value errors did not improve.

The retained IJPharm direct-figure rows still produce value-wrong endpoints such as:

- `27.0229 µg/cm² @ 48 h`
- `26.9466 µg/cm² @ 48 h`
- `18.6260 µg/cm² @ 48 h`
- `41.4504 µg/cm² @ 48 h`

while the gold audit still marks the corresponding rows as value-wrong.

So the error has moved downstream:

- **Fix 2 problem:** page/semantic identity was still partially wrong
- **Fix 3a outcome:** page/subplot identity is now explicit and locked
- **Remaining problem:** curve selection, legend-to-formulation assignment, or endpoint value extraction inside the locked subplot is still wrong

In other words, Fix 3a was a necessary plumbing fix, but not yet a metric-moving fix.

## Validation-Run Interpretation

The validation run itself improved structurally:

- `Actually verified: 12`
- `Final unresolved: 17`
- `Final rejected: 3`

and its artifacts are now much more diagnostic than under Fix 2. The critical new signals are:

- [figure_triage.jsonl](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a\figure_triage.jsonl)
  - IJPharm retained trace: `subplot_raw="A"`, `subplot_selection_status="single"`
- [figure_endpoints.jsonl](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_fix3a\figure_endpoints.jsonl)
  - direct digitized rows: `candidate_tier=triage_primary`, `subplot_lock_failed=false`

That is the main positive result of Fix 3a: the next failure analysis can now focus on locked-subplot value extraction instead of panel identity ambiguity.

## Conclusion

Fix 3a should be considered **successful as a contract and observability fix**, but **neutral on gold-set metrics**.

It eliminated the multi-panel subplot ambiguity, confirmed that digitization is staying on the triage-primary image, and showed that the remaining IJPharm errors are not caused by subplot fallback.

The next fix should therefore target the value path inside the now-correct single-subplot flow:

- curve-to-formulation assignment
- endpoint-value selection within the locked subplot
- value-level sanity checks before a direct figure row is trusted
