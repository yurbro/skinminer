# Fix 5 Phase Evaluation

## Summary Judgment

After Fix 5, the figure stack is in a much better **diagnostic** state, but it is not yet yielding proportional **audited** gains.

- Fix 1-4 established safe selection, calibration gating, subplot lock, and underconstrained-label handling.
- Fix 5 established figure-local VLM grounding and produced the first grounded direct `vlm_only` figure row on `IJPharm`.
- Round-1 gold metrics remain unchanged under conservative overlay.

## Decision

**Recommendation: stop deep figure-precision work here for now and pivot to higher-leverage priorities.**

## Why Pivot Now

1. The remaining figure errors are no longer broad plumbing errors.
   - `CPB` is now a symbol-binding problem.
   - `EJPB` is now a recall / retry problem.
   - `IJPharm` needs a cleaner gold row-identity contract before new direct VLM rows can be scored fairly.

2. The likely next figure fixes are narrower and more expensive.
   - `Fix 3b` would target recall recovery.
   - a `CPB`-style symbol-binding fix would be highly paper/legend specific.
   - neither is likely to move round-1 gold as efficiently as broader project tasks.

3. The project already has enough figure evidence for the paper narrative.
   - You can now document a clear sequence of diagnosis-driven fixes.
   - You can show which figure issues were solved and which remain out of scope for this round.

## Recommended Next Priority Order

1. **Fix 3b recall recovery**
   - recover figure papers where calibration gate removed the wrong primary but a true permeation figure exists elsewhere in the same paper
   - this is the most plausible remaining figure task with recall upside

2. **Full-run evaluation with the current post-Fix-5 codebase**
   - rerun a full pipeline baseline once
   - quantify whether the safer figure stack changes overall verified/unresolved/rejected behavior

3. **Paper writing / methods and evaluation sections**
   - freeze the current figure narrative
   - document the round-1 gold audit, Fix 1-5 sequence, and the decision to stop at diminishing returns

## Not Recommended As Immediate Next Step

- another deep figure precision fix before doing either full-run evaluation or writing
- reconciliation relaxation without a new gold-backed justification
- further VLM prompt tuning in isolation

## Practical Interpretation

Fix 5 is a good place for a checkpoint:

- The figure pipeline is no longer a black box.
- The next figure improvements are real but optional.
- The project can now reasonably pivot from figure micro-precision toward broader end-to-end evaluation and writing.
