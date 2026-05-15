# VLM Value Extraction Proposal

## Scope

This proposal covers **Step 1 only** for the new VLM-based figure value extraction path.

It does **not** change pipeline code yet.

The first implementation scope is intentionally narrow:

- only `figure` route
- only **direct figure rows**
- only when subplot identity is already locked
- only when `candidate_tier = triage_primary`
- only when `subplot_lock_failed = false`

This keeps the first VLM path focused on the exact IJPharm-style failure mode that remains after Fix 1–4.

## Why This Direction Is Reasonable

After Fix 1–4, the main figure errors are no longer page-selection or subplot-selection errors. They are now downstream errors in:

- curve separation
- curve-to-label mapping
- endpoint value reading

The current CV path decomposes the problem into many brittle steps. A VLM can instead read the **locked subplot + legend + axes** directly and produce formulation-specific values in one pass.

This is consistent with current OpenAI vision guidance and limitations:

- OpenAI’s image/vision guide documents image-input support and token accounting for multimodal models such as GPT-4o and GPT-4.1, including the `detail` cost model and image-token calculation formula.  
  Source: [Images and vision](https://developers.openai.com/api/docs/guides/images-vision)
- The same guide also warns that models may struggle with graphs where colors/styles vary, which means we should treat the VLM as a **parallel extraction path with reconciliation**, not as an unconditional replacement.  
  Source: [Images and vision limitations](https://developers.openai.com/api/docs/guides/images-vision)

## 1. Input Definition

### Required image input

- locked subplot crop
- same crop that the figure path already selected after:
  - page selection
  - figure selection
  - subplot lock

### Required structured context

- `paper_id`
- `doi`
- `figure_id`
- `page_number`
- `subplot`
- `candidate_tier`
- `subplot_lock_failed`
- `axes_x_label`
- `axes_x_unit`
- `x_min`
- `x_max`
- `axes_y_label`
- `axes_y_unit`
- `y_kind`
- `target_timepoint_h`
- `expected_endpoint_kind`
- `expected_endpoint_unit`
- `known_formulation_labels`

### Label context rule

For v1, the VLM input should carry **two label layers**:

1. `known_formulation_labels`
   - preferred labels from table/text extraction
2. `legend_labels_hint`
   - optional raw labels or legend snippets already available from figure triage or nearby text

This is important because some current failures are caused by incomplete table-side label coverage.

## 2. Prompt Design

### Recommended model choice

Primary recommendation for v1:

- `gpt-4o`

Reason:

- official model page describes GPT-4o as the “versatile, high-intelligence flagship model” and a strong general multimodal default
- it supports image input and structured outputs

Source:

- [GPT-4o model page](https://developers.openai.com/api/docs/models/gpt-4o)

Cost-sensitive alternative for ablation:

- `gpt-4.1`

Reason:

- image input supported
- structured outputs supported
- lower text-token pricing than GPT-4o

Source:

- [GPT-4.1 model page](https://developers.openai.com/api/docs/models/gpt-4.1)

### System prompt

```text
You read a single locked subplot from a drug-permeation figure and extract formulation-specific endpoint values.

You must work conservatively.

Rules:
1. First identify the axis meaning, units, and whether the subplot is a permeation/release/calibration/other plot.
2. Then identify how many distinct formulation curves are actually readable in the subplot.
3. Then match readable curves to formulation labels using legend text, color/style, and nearby labels.
4. Only read values for the requested timepoint.
5. If you cannot read a curve reliably, say so instead of guessing.
6. If the available label set is incomplete, report that explicitly.
7. Return only structured JSON matching the schema.
```

### User prompt template

```text
You are given one locked subplot crop from a paper.

Paper:
- DOI: {doi}
- Figure: {figure_id}
- Page: {page_number}
- Subplot: {subplot}

Known context:
- Expected endpoint kind: {expected_endpoint_kind}
- Expected endpoint unit: {expected_endpoint_unit}
- Target timepoint (hours): {target_timepoint_h}
- X axis hint: {axes_x_label} [{axes_x_unit}], range {x_min} to {x_max}
- Y axis hint: {axes_y_label} [{axes_y_unit}], y_kind={y_kind}

Known formulation labels:
{known_formulation_labels_bullets}

Legend label hints (may be incomplete):
{legend_labels_hint_bullets}

Tasks:
1. Describe the subplot semantic type.
2. Describe the x-axis and y-axis in plain language.
3. Describe the legend or other curve-identification cues.
4. Count how many distinct readable curves are present.
5. For each formulation that can be matched reliably, read the value at {target_timepoint_h} h.
6. If a formulation cannot be matched or read reliably, mark it unreadable.
7. If the provided formulation label set appears incomplete, set the quality flag `underconstrained_labels`.

Do not infer values from unrelated panels.
Do not return a value when confidence is low.
```

### Structured output schema

```json
{
  "subplot_semantic_type": "permeation_plot | release_plot | calibration_curve | formulation_schematic | other",
  "axis_summary": {
    "x_label": "",
    "x_unit": "",
    "y_label": "",
    "y_unit": "",
    "target_timepoint_h": 48
  },
  "legend_summary": {
    "legend_present": true,
    "curve_count_readable": 4,
    "legend_notes": ""
  },
  "readings": [
    {
      "formulation_label": "IBUGEL",
      "legend_label_raw": "IBUGEL",
      "legend_match_basis": "color + legend text",
      "timepoint_h": 48,
      "value": 15.5,
      "unit": "µg/cm²",
      "confidence": "high",
      "readability": "readable",
      "notes": ""
    }
  ],
  "quality_flags": [
    "underconstrained_labels",
    "legend_unclear",
    "axis_unclear",
    "curve_overlap_high",
    "target_timepoint_not_visible",
    "unreadable"
  ]
}
```

### Prompting note

The prompt should require the model to **explicitly output**:

- semantic type
- axis summary
- legend summary
- readable curve count
- final readings

That gives us an auditable decomposition without requiring free-form hidden reasoning.

## 3. Integration Position

### New module

Recommended new module:

- `extractors/figure/vlm_digitize.py`

### Recommended integration point

Recommended call site:

- inside `extractors/figure/build_records.py`
- after subplot identity is locked
- after crop contract is known
- before final figure record construction

### Practical pipeline shape

```text
triage
  -> subplot lock
  -> shared locked subplot crop
  -> CV digitize path
  -> VLM value path
  -> reconciliation
  -> final figure-backed endpoint rows
```

### Why here

This keeps:

- `triage`
- `assembly`
- `verification`
- `patchers`

unchanged for v1, matching the requested scope.

It also makes it easy to A/B compare:

- CV only
- VLM only
- reconciled

## 4. Reconciliation Strategy

The reviewer’s initial reconciliation idea is directionally good, but for v1 I recommend a **more conservative precision-first variant**.

### Recommended v1 rules

1. If CV is `underconstrained_labels`
   - use VLM if VLM returns readable matched values
   - mark `cv_vlm_agreement = vlm_only`

2. If CV has no usable direct figure endpoint
   - use VLM if readable
   - mark `cv_vlm_agreement = vlm_only`

3. If CV and VLM both produce a value for the same formulation/timepoint and differ by `<= 15%`
   - keep CV value
   - mark `cv_vlm_agreement = agree`
   - store delta

4. If CV and VLM both produce a value but differ by `> 15%`
   - **do not auto-promote either one as trusted final figure value in v1**
   - emit `cv_vlm_disagreement`
   - leave the final endpoint unresolved for direct figure use

5. If VLM says unreadable
   - keep CV only if CV is not underconstrained and already passes direct figure sanity checks
   - otherwise leave unresolved

### Why this is better than “always prefer VLM on disagreement”

Current project state is still precision-first.  
If we automatically overwrite CV with VLM on disagreement, we risk replacing one opaque figure error with another.

So the first version should use VLM as:

- a rescue path when CV is structurally broken
- a confirmation path when CV and VLM agree
- a disagreement detector otherwise

## 5. Cost Estimate

### Image-token basis

OpenAI’s vision guide gives the image-token formula for GPT-4o / GPT-4.1:

- base tokens: `85`
- tile tokens: `170`

For a typical locked subplot crop around `1024 x 768` with `detail = high`, this is usually:

- 4 tiles
- `170 * 4 + 85 = 765` image tokens

Source:

- [Images and vision: image token accounting](https://developers.openai.com/api/docs/guides/images-vision)

### Per-image estimate

Assumption for one VLM call:

- image input: `765` tokens
- text input/context: `500–800` tokens
- structured output: `250–450` tokens

#### If using GPT-4.1

Using official pricing:

- input: `$2.00 / 1M`
- output: `$8.00 / 1M`

Approximate cost:

- image input: `765 * 2 / 1e6 ≈ $0.0015`
- text input (600): `600 * 2 / 1e6 ≈ $0.0012`
- output (350): `350 * 8 / 1e6 ≈ $0.0028`
- total: about **`$0.0055` per subplot**

Source:

- [GPT-4.1 model page](https://developers.openai.com/api/docs/models/gpt-4.1)
- [Pricing page](https://developers.openai.com/api/docs/pricing)

#### If using GPT-4o

Using official pricing:

- input: `$2.50 / 1M`
- output: `$10.00 / 1M`

Approximate cost:

- image input: `765 * 2.5 / 1e6 ≈ $0.0019`
- text input (600): `600 * 2.5 / 1e6 ≈ $0.0015`
- output (350): `350 * 10 / 1e6 ≈ $0.0035`
- total: about **`$0.0069` per subplot**

Source:

- [GPT-4o model page](https://developers.openai.com/api/docs/models/gpt-4o)
- [Pricing page](https://developers.openai.com/api/docs/pricing)

### Full-run impact

Using the current figure-paper scale from earlier runs (`~19` figure-route papers):

- if 1 locked subplot per paper:
  - GPT-4.1: about **`$0.10–$0.11`**
  - GPT-4o: about **`$0.13`**
- if 1.5 locked subplots per paper:
  - GPT-4.1: about **`$0.15–$0.16`**
  - GPT-4o: about **`$0.19–$0.20`**

So the incremental cost is modest enough for targeted validation runs.

## 6. Required New Observability Fields

At minimum, the VLM artifact should include:

- `extraction_method`: `cv` / `vlm` / `cv_vlm_reconciled`
- `vlm_model`
- `vlm_model_version_or_snapshot`
- `vlm_prompt_asset_id`
- `vlm_prompt_version`
- `vlm_raw_response`
- `vlm_subplot_semantic_type`
- `vlm_curve_count_readable`
- `vlm_quality_flags`
- `cv_vlm_agreement`: `agree` / `disagree` / `vlm_only` / `cv_only`
- `cv_vlm_delta_pct`
- `vlm_readability_status`
- `vlm_used_as_final`: `true/false`

For each formulation reading:

- `formulation_label`
- `legend_label_raw`
- `legend_match_basis`
- `timepoint_h`
- `value`
- `unit`
- `confidence`
- `notes`

## 7. Prompt Version Tracking

The new VLM path must follow the same tracking discipline as other modules:

- `PROMPT_ASSET_ID`
- `PROMPT_VERSION`

And those must appear in:

- `run_manifest.jsonl`
- `report/run_report.md`
- `report/run_report.json`

Suggested asset id:

- `extractors.figure.vlm_digitize`

Suggested initial version:

- `2026-04-08.v1`

## 8. Initial Judgment On IJPharm

My current judgment is: **yes, this case is a good candidate for VLM recovery**.

Reason:

- the page is now correct
- the subplot is now correct
- calibration figures are already gated out
- the remaining problem is exactly the kind of holistic graph-reading task a VLM can do better than CV fragments

However, the official vision limitations page also warns that models can struggle with graphs where colors/styles vary, so I would expect:

- likely `approximate` values first
- not guaranteed perfect exact values
- strong need for disagreement gating in v1

So my expectation is:

- IJPharm is a plausible win case for VLM
- but v1 should still be conservative on `cv_vlm_disagreement`

## 9. One Design Adjustment I Recommend

I recommend one change to the reviewer’s draft reconciliation requirements:

- when CV and VLM disagree by `> 15%`, do **not** automatically trust VLM in v1

Instead:

- mark `cv_vlm_disagreement`
- keep the row unresolved unless one side is structurally disqualified

That better matches the current precision-first phase of the project.

## 10. Recommended Next Step

If approved, implementation should proceed in this order:

1. add `vlm_digitize.py`
2. add new artifact schema for VLM readings
3. integrate into `build_records.py` as a parallel path for direct locked-subplot rows only
4. add reconciliation logic
5. rerun the validation run
6. rerun the gold delta report against the same audit subset
