# Fix 5 Delta Report

## Scope

Fix 5 targeted **VLM series identity and figure-local grounding** after subplot lock:

- VLM now returns `series_marker_raw`, `series_label_raw`, and `series_rank_hint`
- grounding prefers `figure_label_space` before `source_label_space`
- `IJPharm` can now emit grounded direct VLM rows from locked subplot A
- reconciliation policy itself was **not** loosened

Validation run: [validation_observability_run_fix5](c:/Users/yz02380/OneDrive - University of Surrey/Science Research/Codes/SkinMiner/outputs/validation_observability_run_fix5)

Gold overlay: [gold_set_seed_round1_after_fix5.csv](c:/Users/yz02380/OneDrive - University of Surrey/Science Research/Codes/SkinMiner/outputs/gold_audit_set/fix5_vlm_label_grounding/gold_set_seed_round1_after_fix5.csv)

## Gold Metric Delta vs VLM v1

| Metric | VLM v1 | Fix 5 | Delta |
|---|---:|---:|---:|
| precision | 1.000 | 1.000 | +0.000 |
| recall | 0.500 | 0.500 | +0.000 |
| F1 | 0.667 | 0.667 | +0.000 |
| scope precision | 1.000 | 1.000 | +0.000 |
| end-to-end precision | 0.000 | 0.000 | +0.000 |
| verified count | 7 | 7 | +0 |

## Validation Run Structural Delta vs VLM v1

| Signal | VLM v1 | Fix 5 | Delta |
|---|---:|---:|---:|
| VLM readings total | 11 | 13 | +2 |
| VLM readings readable | 10 | 12 | +2 |
| VLM used as final | 0 | 2 | +2 |
| `cv_only` | 9 | 8 | -1 |
| `cv_vlm_disagreement` | 1 | 2 | +1 |
| `vlm_only` | 0 | 2 | +2 |

New grounding statuses observed in Fix 5:

- `figure_label_space: 3`
- `figure_label_space_only: 1`
- `ungrounded: 8`
- `none: 1`

## Interpretation

Fix 5 is **structurally successful** but **evaluation-neutral**.

What clearly improved:

- locked-subplot VLM is now extracting figure-local series identity instead of jumping straight to downstream formulation labels
- `IJPharm` now produces a grounded `vlm_only` direct figure row (`record_9c767c2806d6`, `15.0 ?g/cm? @ 48 h`)
- observability is much better: we can now separate readable-but-ungrounded rows from figure-label-grounded rows

Why the gold metrics did not move:

- this round used a **conservative no-remap gold overlay**
- the existing round-1 gold rows do not provide a clean one-to-one target for the new `IJPharm` VLM-only row family
- `CPB` remains blocked by symbol-to-curve binding, not just label grounding
- `EJPB` remains blocked by figure recovery / retry rather than post-lock value reading

So Fix 5 changed the **plumbing and diagnosability**, but did not yet create a gold-comparable audited gain large enough to move round-1 metrics.

## What Fix 5 Tells Us

1. VLM plumbing is no longer the problem.
2. Figure-local grounding can work on `IJPharm`.
3. Remaining figure work is now high-effort:
   - `CPB`: legend symbol -> curve binding
   - `EJPB`: recall recovery / reject-and-retry (Fix 3b)
   - row-identity contract if we want future gold overlays to count new direct VLM rows cleanly

## Conclusion

Fix 5 did **not** deliver a material audited metric improvement on round-1 gold.

That does **not** mean the work was wasted. It means the figure pipeline has reached a point of sharply diminishing returns:

- observability is strong
- one direct VLM grounding case now works
- but the remaining blockers are narrow, expensive, and paper-specific

This is a reasonable stopping point for deep figure-precision work unless the next milestone specifically requires better direct-figure end-to-end precision.
