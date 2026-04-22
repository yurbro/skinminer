# SkinMiner Experiment Design v1

## 1. Experiment Goals

The paper should answer five questions:

1. What is end-to-end extraction quality under the current strict policy?
2. How much do model choice and backend strength affect routing and extraction quality?
3. What is the contribution of key modules such as patching, table-support promotion, and the VLM figure path?
4. Does the VLM parallel path improve figure outcomes relative to CV-only behavior?
5. What quality-cost tradeoff does the framework achieve?

`full_run_13_post_fix5` is the current post-Fix-5 baseline. It is stricter and more observable than `full_run_12_full`, but it verifies only `4` records and shifts many figure rows into explicit failed or unresolved states. That makes it a suitable baseline for controlled experiments even though it is not the highest-yield historical run.

## 2. Experiment Matrix

| ID | Variable | Configuration | Feasible now? | Expected token cost | Priority | Purpose |
|---|---|---|---|---|---|---|
| E1 | baseline | post-Fix-5 `balanced_full` | yes, already done as `full_run_13_post_fix5` | ~`3.84M` tokens | highest | reference line |
| E2 | LLM backend | replace `gpt-4o-mini` with `gpt-4o` or `gpt-4.1` for `routing + extraction` stages | yes via stage model flags | ~`2.94M` tokens on upgraded stages, ~`3.84M` total | high | model-capability comparison |
| E3 | LLM backend | Claude Sonnet for routing/extraction | no, requires provider integration | unknown until integration | low | cross-vendor comparison |
| E4 | figure method | CV-only, disable VLM path | not yet; needs a runtime flag | ~`3.59M` total | highest | quantify VLM gain |
| E5 | figure method | VLM-only, bypass CV mapping path | not yet; needs larger code change | ~`3.67M` total | medium | isolate VLM independent value |
| E6 | ablation | disable targeted patching | not yet; needs a runtime flag | nearly unchanged token cost | high | quantify patcher contribution |
| E7 | ablation | disable table-support promotion | not yet; needs a runtime flag | nearly unchanged token cost | high | quantify support-promotion contribution |
| E8 | policy | relaxed policy: any ibuprofen concentration | not yet; needs new policy and policy selection flag | similar to baseline | medium | assess scope expansion |

### Notes on feasibility

- E2 is the easiest model experiment because [run_pipeline.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\run_pipeline.py) already supports stage-level overrides such as `--routing-model`, `--table-model`, `--text-model`, `--figure-triage-model`, `--figure-vlm-model`, and `--figure-map-model`.
- E3 is not currently practical because the codebase is OpenAI-client specific.
- E4, E6, and E7 are the most valuable next engineering toggles because they are directly tied to current methodological claims.

## 3. Gold Set Expansion Plan

Current gold set has `71` rows and is figure-heavy: `31 figure`, `18 table`, `18 mixed`, `4 text`. That is enough for round-1 diagnosis but not enough for backend and ablation experiments.

### Recommended target

Target `125–130` rows in the next expansion round.

### Recommended additions

Add roughly `55–60` rows, mainly from non-figure routes:

- `+20 to +25` text
- `+12 to +15` table
- `+12 to +15` mixed
- `+5 to +10` figure diagnostic rows

### How to sample from `full_run_13_post_fix5`

Immediate high-value additions from `full_run_13_post_fix5`:

- all `9` text unresolved rows
- all `10` table unresolved rows
- all `4` mixed unresolved rows
- all `6` non-figure rejected rows

This gives `29` non-figure additions immediately. The remaining `25–30` rows should be drawn from:

- figure unresolved/rejected rows with `figure_digitization_failed`, `underconstrained_labels`, `cv_only`, `cv_vlm_disagreement`, or `vlm_only`
- one more post-baseline run after a CV-only or recall-recovery branch, to fill the text and mixed shortage

### Annotation dimensions

Core gold schema should remain stable. Add any new figure-specific fields in a supplemental sheet, not in the core table. The most useful optional diagnostics are:

- `gold_figure_series_id`
- `gold_cv_value`
- `gold_vlm_value`
- `gold_value_source_modality`

## 4. Evaluation Metrics

Paper-level reporting should include:

- per-route precision / recall / F1
- overall precision / recall / F1
- scope precision and end-to-end precision separately
- figure funnel metrics:
  - triage-to-digitize conversion
  - digitization success rate
  - mapping success rate
  - VLM readability rate
  - CV/VLM agreement rate
- failure taxonomy distributions
- recoverable rate by unresolved bucket
- total token usage and stage-level token usage
- approximate per-record token cost:
  - total tokens / assembled records
  - figure-stage tokens / figure records
- run-to-run stability:
  - at least two repeated runs of the same config for variance on `verified`, `unresolved`, and major failure buckets

## 5. Execution Plan

### Recommended order

1. Treat E1 as complete: `full_run_13_post_fix5` is the current baseline.
2. Expand the gold set.
3. Add two lightweight toggles:
   - CV-only
   - patching off
4. Run E4 and E6 first.
5. Add table-support-promotion toggle and run E7.
6. Run E2 with a stronger OpenAI model on routing and extraction.
7. Decide whether E8 is needed for a scope-expansion appendix.
8. Leave E3 and E5 for later unless the paper explicitly needs them.

### Parallelization

- Gold-set expansion can proceed while experiment toggles are being added.
- E4, E6, and E7 can run in parallel after their flags exist.
- E2 should run after gold expansion so its gains can be scored immediately.

### Expected timing

Using `full_run_13_post_fix5` as reference:

- one full baseline-like run: about `5000s` wall-clock
- E4/E6/E7: similar wall-clock to baseline
- E2: similar wall-clock, likely higher API cost
- gold expansion and annotation: one separate human workstream

## Highest-Priority Experiments

1. E4 `CV-only` vs current baseline: most direct test of whether VLM helps the figure branch.
2. E6 patching ablation: tests whether the current verified/unresolved split depends materially on patch recovery.
3. E2 stronger OpenAI backend on routing + extraction: best model-capability comparison with existing infrastructure.
