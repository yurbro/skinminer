# SkinMiner Evaluation Round 1: Conclusions

## 1. Evaluation design

Evaluation Round 1 followed a freeze-first workflow: core pipeline logic was frozen, observability gaps were patched, a stratified gold audit set was sampled, the set was manually annotated, and scoring separated scope correctness from endpoint-value correctness. This stopped proxy-driven tuning and forced diagnosis against human labels. A dedicated figure-value diagnosis then traced the source of all verified value errors. The result is a data-backed transition from heuristic debugging to controlled fix cycles.

## 2. Gold audit set structure

The corrected round-1 gold audit set contains `71` labeled records from `23` papers. It is intentionally figure-heavy: route counts are `31 figure`, `18 table`, `18 mixed`, and `4 text`. Status counts are `10 verified`, `56 unresolved`, and `5 rejected`. Sampling combined a figure-focused validation run with supplemental non-figure rows from `full_run_12_full`, so the set is stratified but not yet balanced.

## 3. Key quantitative findings

### 3.1 Scope precision vs end-to-end precision

Scope precision is `1.000`, while end-to-end precision is `0.000`. The `10` system-verified rows all satisfy the strict scope gates under human review, but none has a correct endpoint value. The blocking issue is therefore value accuracy, not scope acceptance.

### 3.2 Recall

Recall is `0.714`, with `14` gold positives and `10` recovered by the system. The remaining `4` false negatives all sit in `unresolved`, and all `4/4` are concentrated in the `not_target_api_concentration` bucket. Other unresolved buckets are non-recoverable in this audit set: `insufficient_evidence` contributes `35` rows with `0` gold positives, and `ambiguous_api_concentration` contributes `26` rows with `0` gold positives. Recall loss is therefore narrow rather than diffuse.

### 3.3 Verification status breakdown

`verified` is now precise on scope (`10/10` gold keep), `unresolved` contains the only remaining gold positives (`4/56`), and `rejected` shows no audit-set false kills (`0/5`). The scoring outcome supports keeping the current strict scope gate intact. It does not support broad relaxation of verification thresholds.

## 4. Root cause analysis: figure value errors

### 4.1 Error distribution

All `11` value-error rows in the audit set are on `figure`-route papers. Their primary root-cause breakdown is `figure_misidentified = 7`, `mapping_error = 3`, and `other = 1`. Only `5/11` are direct figure-extractor outputs; the other `6/11` are table-backed or shared-hint-contaminated records. This makes the figure route the dominant source of end-to-end precision loss.

### 4.2 Systemic diagnosis: source-binding failure

The unifying diagnosis is `source-binding failure`, not raw CV precision failure. In the main error cases, the pipeline binds a record to the wrong page, wrong figure, wrong subplot, or wrong context before digitization or downstream promotion happens. This explains why scope precision can be perfect while end-to-end precision remains zero.

### 4.3 Cross-modal contamination

Cross-modal contamination is a real secondary problem: `6/11` value-error rows are not direct figure outputs. Some were contaminated by exact-value propagation from a misidentified figure trace, while others were contaminated by table/text extraction on figure-route papers using narrative snippets from a different dose, timepoint, or experiment context. Fixing direct figure/page selection is necessary but not sufficient.

## 5. Conclusions

### 5.1 What works

The strict scope gate is working on this audit set. Scope precision is `1.000`, `verified` contains `10/10` true scope positives, and `rejected` contains `0/5` false kills. The failure taxonomy also isolates the only recoverable unresolved bucket as `not_target_api_concentration`.

### 5.2 What does not work

The current figure route does not deliver correct endpoint values. All `10` verified rows fail value accuracy, and all value errors are tied to figure-route papers. The highest-yield failure source is figure/page misselection (`7/11`), followed by mapping collapse (`3/11`) and cross-modal contamination (`6/11` overall, overlapping with the primary categories).

### 5.3 What was deprioritized and why

VLM fallback was deprioritized because the evidence does not indicate a vision-model recognition bottleneck. The dominant problem is wrong source selection and cross-modal binding, not inability to read a correctly chosen plot. Broad verification loosening was also deprioritized because scope precision is already `1.000`.

## 6. Recommended fix priority

1. Figure/page selection logic in `extractors/figure/digitize.py::_iter_image_candidates`
2. Curve-to-formulation mapping in `extractors/figure/map_curves.py::map_curves_to_formulations`
3. Assembly and cross-modal promotion source-binding audit
4. Narrow `not_target_api_concentration` promotion for unresolved recall
5. Re-evaluate VLM fallback only after the first three fixes

## 7. Methodological notes

This round explicitly separated scope correctness from value correctness, which proved essential: the system is accurate on scope but not on endpoint value. A correction log was retained because `11` human labels were fixed after initial annotation inconsistencies. The current gold set is still limited: it is figure-heavy and merges records from a validation run and `full_run_12_full`. Generated on `2026-04-06`, based on corrected `gold_set_seed_round1.csv`, `score_round1.json`, `score_round1_summary.md`, `gold_round1_analysis.md`, `gold_round1_correction_log.md`, `figure_value_error_diagnosis.md`, `figure_value_error_summary.md`, and `gold_set_sampling_summary.md`.
