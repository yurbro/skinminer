# Fix 5 Proposal: VLM Legend Grounding Before Reconciliation

## Why Fix 5 Is Needed

The diagnosis in:

- [fix5_vlm_cv_only_diagnosis.md](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\fix5_vlm_cv_only_diagnosis.md)

shows two different failure modes inside the current VLM path:

1. `IJPharm` (`10.1016/j.ijpharm.2016.03.043`)
   - VLM crop is locked correctly
   - but there is no usable subplot-local legend in the crop
   - and the downstream allowed label space is the wrong one for subplot A

2. `CPB` (`10.1248/cpb.c21-00033`)
   - VLM can see the symbol legend and return values
   - but the returned values are often bound to the wrong legend symbol
   - downstream grounding also fails because the pipeline label space is collapsed to one aggregate label

Therefore Fix 5 should target **figure-local label grounding and series identity**, not reconciliation thresholds.

## Fix 5 Scope

This fix should remain narrow:

- keep the current `locked subplot` VLM entry point
- do **not** change verification or reconciliation policy yet
- do **not** broaden VLM use beyond direct figure rows

Files likely in scope:

- [extractors/figure/vlm_digitize.py](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\extractors\figure\vlm_digitize.py)
- [extractors/figure/models.py](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\extractors\figure\models.py)
- [extractors/figure/build_records.py](C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\extractors\figure\build_records.py)

## Proposed Changes

### Fix 5a: Separate `series identity` from `formulation label`

The first version asks VLM to jump directly to `formulation_label`. That is too brittle.

Instead, VLM should return:

- `series_marker_raw`
  - symbol or marker identity, e.g. `○`, `■`, `green triangles`, `purple circles`
- `series_label_raw`
  - nearby legend text if visible
- `series_rank_hint`
  - optional ordering hint such as `highest_at_48h`, `second_lowest`, etc.
- `endpoint_value`
- `endpoint_time`
- `endpoint_unit`

Then a deterministic grounding step should map:

- `series_marker_raw / series_label_raw`

to downstream formulation labels.

This makes the pipeline auditable:

- VLM reads what is visually present
- grounding maps that visual identity into the formulation schema

### Fix 5b: Add figure-local grounding context

For current failures, downstream `allowed_formulation_labels` are sometimes paper-level or table-level, not subplot-level.

So the VLM context packet should be extended with:

- subplot-local figure caption text
- same-page legend/caption snippet if available
- paper/table formulation labels as a separate optional list

Important distinction:

- `figure_label_space`
  - labels visually present for this subplot or panel
- `source_label_space`
  - labels imported from table/text records

The grounding step should prefer:

1. `figure_label_space`
2. then `source_label_space`

This is especially important for IJPharm, where subplot A is formulation-driven but the current imported label space is dose-driven.

### Fix 5c: Symbol-aware binding for CPB-like plots

For symbol-legend plots, the prompt should explicitly require:

- one reading per symbol
- no reuse of the same top curve value across multiple symbols
- `series_marker_raw` must be attached to each returned row

The post-processor should reject rows if:

- multiple symbol rows collapse to the same high endpoint without sufficient visual rationale
- or the marker-level binding is internally inconsistent

This is still a precision-first fix. Suspicious rows should remain non-final.

## What Fix 5 Does Not Change

- No reconciliation threshold changes
- No automatic promotion of VLM rows into `verified`
- No expansion to non-locked subplots
- No page retry logic

## Expected Outcome

If Fix 5 works:

- `IJPharm` should stop failing purely because of wrong downstream label space
- `CPB` should expose clearer `marker -> value` rows
- VLM rows will become diagnosable as:
  - `grounded_and_usable`
  - `readable_but_ungrounded`
  - `marker_binding_inconsistent`

The immediate success criterion is not a large recall jump.

The immediate success criterion is:

- at least some `cv_only` rows become `vlm_readable_and_grounded`
- while preserving current precision

## Recommendation

Proceed with Fix 5 as a **label grounding and series identity** repair, not as a reconciliation change.

Only after this step should we revisit whether readable VLM rows deserve broader downstream use.
