# SkinMiner Codex Handoff — 2026-04-09

## 1. Project State

SkinMiner is now a mature package-based pipeline with stable schemas, centralized strict policy, working evaluation tooling, and a figure branch that has gone through five controlled fixes plus a VLM parallel path. The system is no longer in ad hoc debugging mode; it is in evaluation-driven iteration.

## 2. Architecture Summary

Pipeline: `corpus -> triage -> access -> detection/router -> extractors(text/table/figure) -> assembly -> verification -> patchers -> reports`. Main entry points are [run_pipeline.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\run_pipeline.py) and [schemas/models.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\schemas\models.py). Suggested reading order is in [README.en.md](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\README.en.md).

## 3. Current Pipeline Configuration

Current baseline is `run_profile=balanced_full`, `policy=v1_strict_ibuprofen_5pct`, default stage models `gpt-4o-mini`, structured-first routing/text/table, PDF-backed figure extraction, optional audit-only LLM adjudication, and optional stage model overrides in [configs/run_profiles.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\configs\run_profiles.py). Strict policy lives in [policies/v1_strict_ibuprofen_5pct.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\policies\v1_strict_ibuprofen_5pct.py).

## 4. Evaluation Infrastructure

Round-1 gold audit set is [gold_set_seed_round1.csv](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\gold_set_seed_round1.csv): `71` labeled rows from `23` papers, figure-heavy and stratified. Evaluation tools are [evaluation/score_run.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\evaluation\score_run.py), [evaluation/gold_audit.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\evaluation\gold_audit.py), and [evaluation/validate_gold_labels.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\evaluation\validate_gold_labels.py). Labels include six scope gates plus value correctness and final keep/no-keep.

## 5. Round 1 Evaluation Results (Post-Fix-5)

Post-Fix-5 audited metrics are:

- scope precision: `1.000`
- end-to-end precision: `0.000`
- recall: `0.500`
- F1: `0.667`
- predicted positives: `7`
- gold positives: `14`

Verified rows in the audit set are figure-route only; non-figure verified rows are zero. Top recoverable unresolved buckets are:

- `figure_digitization_failed`: `0.750`
- `unit_normalization_failed`: `0.600`
- `not_target_api_concentration`: `0.500`
- `missing_endpoint`: `0.300`

`insufficient_evidence` and `ambiguous_api_concentration` both have recoverable rate `0.000`.

## 6. Completed Fixes (Fix 1–5)

| Fix | Change | Files | Effect |
|---|---|---|---|
| Fix 1 | Tiered digitize candidate search | `digitize.py` | temporary end-to-end precision bump to `0.2` |
| Fix 2 | `calibration_curve` hard gate + `figure_semantic_type` | `triage.py`, `digitize.py` | removed EJPB calibration false positives |
| Fix 3a | multi-panel subplot contract tightened to single panel | `triage.py` | structural subplot identity repair |
| Fix 4 | raw-tail cleanup + `underconstrained_labels` gate | `digitize.py`, `map_curves.py` | prevented unsafe many-to-few mapping |
| Fix 5 | VLM series identity separation + figure-local grounding | `vlm_digitize.py`, `build_records.py` | first grounded direct `vlm_only` figure row |

Each fix has a delta package under `outputs/gold_audit_set/`.

## 7. VLM Parallel Path Status

VLM path is implemented in [extractors/figure/vlm_digitize.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\extractors\figure\vlm_digitize.py). It is enabled only for locked-subplot direct figure rows, runs in parallel with CV, and uses a precision-first reconciliation policy: CV/VLM disagreement remains unresolved. Prompt asset is `extractors.figure.vlm_digitize 2026-04-08.v2`. After Fix 5, validation-run observability shows `vlm_readings_total=13`, `vlm_readings_readable=12`, `vlm_used_as_final=2`. IJPharm now yields a grounded `vlm_only` row; CPB remains blocked by symbol-binding.

## 8. What We Learned

- Scope gate is correct; it should not be loosened just to increase yield.
- Figure value errors are primarily `source-binding failure`, not generic CV weakness.
- Fixes 1–5 repaired much of the page/figure/subplot chain, but dense multi-curve figures still hit method limits.
- VLM helps with some direct rows, but legend/symbol grounding remains a bottleneck.
- Additional figure-precision work now has diminishing returns.
- Recoverable unresolved rows are concentrated in a few buckets rather than spread broadly.

## 9. What Has NOT Been Done Yet

### 9.1 Experiments and evaluation

- No full post-Fix-5 full-run baseline yet
- No model-backend comparison
- No ablation study
- No strict-vs-relaxed policy comparison
- No cost-efficiency study
- Gold set is still small and figure-heavy

### 9.2 Unfinished fixes

- Fix 3b: triage reject-and-retry for recall recovery
- Narrow `not_target_api_concentration` promotion
- Cross-modal contamination audit and repair
- `unit_normalization_failed` diagnosis and targeted fix

### 9.3 Scope expansion

- No relaxed concentration policy
- No supplementary-material branch
- No non-OA acquisition

## 10. Recommended Next Steps (Priority Order)

1. Run one full post-Fix-5 baseline (`full_run_13`)
2. Expand gold set to `120–150` rows with stronger non-figure coverage
3. Design experiment matrix for backend, ablation, and figure-method comparisons
4. Run comparisons
5. Apply Fix 3b and the narrow unresolved-promotion fix
6. Consolidate evaluation
7. Write the paper

## 11. Do Not Redo

Do not rebuild or relabel round-1 gold from scratch. Do not redo Fix 1–5 diagnosis or VLM proposal work. Do not redo adjudication prompt tracking, figure silent-loss logging, or `has_permeation_plot` observability. Existing outputs in `outputs/gold_audit_set/` and `outputs/validation_observability_run_*` are the canonical history.

## 12. Key Files For New Conversation

1. [reports/codex_handoff_2026-04-09.md](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\reports\codex_handoff_2026-04-09.md)
2. [evaluation_round1_conclusions.md](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\evaluation_round1_conclusions.md)
3. [fix5_phase_evaluation.md](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\fix5_vlm_label_grounding\fix5_phase_evaluation.md)
4. [score_after_fix5_summary.md](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\gold_audit_set\fix5_vlm_label_grounding\score_after_fix5_summary.md)
5. [README.en.md](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\README.en.md)
6. [schemas/models.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\schemas\models.py)
7. [v1_strict_ibuprofen_5pct.py](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\policies\v1_strict_ibuprofen_5pct.py)
