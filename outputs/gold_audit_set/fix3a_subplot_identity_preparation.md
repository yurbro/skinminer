# Fix 3a Preparation: Triage Subplot Identity Tightening

Date: 2026-04-06

## Scope

This note proposes **Fix 3a only**:

- tighten `figure triage -> digitize` subplot identity for multi-panel figures
- do **not** yet add paper-level retry/search (`Fix 3b`)
- do **not** yet touch cross-modal contamination in `assembly` or `patchers`

No code is changed in this note.

---

## Observed Problem

In the Fix 2 validation run:

- IJPharm (`10.1016/j.ijpharm.2016.03.043`) triage produced:
  - `page_number = 7`
  - `figure_id = 1`
  - `subplot = "A, B, C, D"`
  - `recommended_route = digitize`
- `digitize.py` only activates subplot locking when the normalized subplot is a **single** `A/B/C/D`
- because triage emitted a multi-value string, digitization never entered a real single-panel lock
- resulting figure endpoint artifacts show:
  - `candidate_tier = triage_primary`
  - `subplot_lock_failed = false`
  - crop still covers the full multi-panel figure block

So the current failure is not:

- cross-page fallback stealing the wrong page
- nor silent subplot-lock fallback

It is:

- **triage contract failure**: triage returns a multi-panel label where digitization requires a single target panel

---

## Why Fix 3a Is the Right Next Step

Fix 2 already proved two things:

1. the calibration semantic gate is correct
   - EJPB false positives are now removed
2. IJPharm is still wrong because the chosen page is right, but the chosen subplot is not singular

That means the narrowest high-value next fix is:

- make triage emit **exactly one target subplot** for digitizable multi-panel figures

This is the most direct path to restoring end-to-end precision above zero without reopening the larger paper-level retry problem.

---

## Current Contract Gap

Current `FigureTriageResult` allows:

- `subplot: str = ""`

But it does not require that:

- the value be singular
- the value be machine-actionable for downstream crop locking

So outputs like:

- `A, B, C, D`
- `A;B;C;D`
- `Figure 4`

all pass through as plain strings.

For digitization, these values are not equivalent:

- `A` is actionable
- `A, B, C, D` is ambiguous
- `Figure 4` is page-level only

This mismatch is the direct source-binding gap for IJPharm.

---

## Proposed Fix 3a

### Code Scope

Primary files:

- `extractors/figure/triage.py`
- `extractors/figure/models.py`

No direct logic change proposed yet in:

- `extractors/figure/digitize.py`
- `assembly/*`
- `patchers/*`

`digitize.py` should continue to consume a single-panel subplot when provided.

### Behavior Change

For `recommended_route = digitize` on multi-panel pages:

- triage must emit **one and only one** target subplot
- the value should be restricted to a low-cardinality machine-usable form:
  - `A`
  - `B`
  - `C`
  - `D`
  - or empty if no trustworthy panel can be selected

### Prompt-Level Change

Strengthen the triage instruction:

- if the selected figure page contains multiple panels, choose the **single best target subplot**
- do not return comma-separated or semicolon-separated subplot lists
- if several panels are plausible, choose the single best panel in reading order and explain ambiguity in notes

Recommended decision policy:

1. prefer the panel that contains the clearest ibuprofen cumulative/permeation curve
2. prefer a panel whose axes and legend are readable enough for digitization
3. if multiple panels remain plausible, choose the first valid panel in reading order (`A` before `B` before `C` before `D`)
4. record in notes that the subplot choice was ambiguous

This keeps the contract simple and deterministic.

### Parse/Normalization Change

Add a triage-side normalization helper so downstream code receives a stable contract even if the model still emits a list-like string.

Suggested behavior:

- canonicalize:
  - `(a)` -> `A`
  - `a` -> `A`
  - `A;B;C;D` -> multi-value parse
  - `A, B, C, D` -> multi-value parse
- if a single valid panel is present, store that panel
- if multiple valid panels are present:
  - choose the first in reading order
  - preserve the original raw value in a separate field
  - explicitly mark that coercion happened

### New Observability Fields

Add to `FigureTriageArtifact`:

- `subplot_raw: str`
- `subplot_selection_status: Literal["single", "coerced_from_multi", "ambiguous_none"]`

Recommended semantics:

- `single`
  - model already returned a single actionable panel
- `coerced_from_multi`
  - model returned multiple panels and triage normalized to the first valid panel
- `ambiguous_none`
  - triage could not reduce to a trustworthy single panel

This is useful for the next gold evaluation round because it separates:

- true single-panel success
- forced-but-explicit ambiguity
- unresolved subplot identity

---

## Expected Effect

### Likely Positive Effect

For IJPharm-like papers:

- digitization will finally receive `subplot = A` instead of `A, B, C, D`
- the existing Fix 2 subplot-lock path can then actually engage
- direct figure rows should become more source-bound than they are now

### What It Will Not Solve

Fix 3a alone will not solve:

- EJPB paper-level retry after calibration rejection
- cross-modal contamination rows with no record-level figure trace
- papers that truly need more than one subplot per paper to represent all valid endpoints

So this is a precision-oriented direct-figure fix, not a full recall fix.

---

## Risks

1. **Forced first-panel choice may be wrong**
   - if triage still sees multiple plausible panels, choosing `A` may help some rows and hurt others
   - this is why `subplot_selection_status` must be logged

2. **Single-trace-per-paper limitation remains**
   - some papers contain multiple valid permeation subplots
   - Fix 3a does not solve that structural limitation

3. **False confidence if ambiguity is hidden**
   - this is why multi-value coercion must be explicit, not silent

---

## Recommendation

Proceed with Fix 3a as a narrow triage-contract fix:

1. strengthen prompt to require a single target subplot
2. normalize multi-value subplot strings into one actionable panel
3. log the raw subplot and whether coercion occurred

Then rerun the same validation/gold-eval loop and check:

- whether IJPharm direct figure rows move from `subplot=A,B,C,D` to a true single-panel trace
- whether `end-to-end precision` rises above `0.000`
- whether the new gains are coming from direct figure rows rather than contamination rows
