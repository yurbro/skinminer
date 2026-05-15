# SkinMiner Codex Handoff - Updated 2026-04-24

## 1. Project State

SkinMiner is in close-out mode. The planned architecture work, fix packet, evaluation packet, policy sensitivity study, single-pass comparison, Claude integration, reproducibility reruns, and PhD closure demonstration are complete. The remaining work is paper writing, selective manual interpretation, and any explicitly approved follow-on pilot.

## 2. Architecture Summary

Core pipeline: `corpus -> rule triage -> LLM triage -> content access -> routing -> extractors (text/table/figure) -> assembly -> verification -> patchers -> final verification -> reports`.

Compared with the 2026-04-09 handoff, three architecture additions are now part of the stable system:

- Provider abstraction in `utils/llm_client.py`, with `openai` and `anthropic` support across all structured LLM stages.
- A four-layer policy stack: `v1_strict_ibuprofen_5pct`, `v2_accept_wv`, `v3_any_ibuprofen_concentration`, `v4_accept_flux`.
- Single-pass comparison scripts: `experiments/single_pass_extract.py` and `experiments/single_pass_pdf_extract.py`.

## 3. Current Pipeline Configuration

The frozen baseline definition is in `reports/baseline_definition.md`.

- Corpus: `outputs/full_run_12_full/corpus.csv` (`1828` rows)
- Run profile: `balanced_full`
- GPT baseline provider/model: `openai` + `gpt-4o-mini` for all stages
- Claude baseline provider/model: `anthropic` + `claude-sonnet-4-6` for all stages
- Frozen prompt assets:
  `triage.abstract_relevance=2026-03-28.v1`,
  `routing.structured_first=2026-03-28.v1`,
  `extractors.text.structured_fields=2026-04-11.v1`,
  `extractors.table.structured_tables=2026-04-11.v1`,
  `extractors.figure.triage=2026-04-06.v1`,
  `extractors.figure.vlm_digitize=2026-04-11.v1`,
  `extractors.figure.curve_map=2026-03-28.v1`,
  `verification.llm_adjudication=2026-04-03.v1`

## 4. Frozen Baselines

| Baseline | Run | Output | Provider / model | Assembled | v1 verified | v2 verified |
|---|---|---|---|---:|---:|---:|
| GPT baseline | `full_run_16_post_all_fixes` | `outputs/full_run_16_post_all_fixes/` | OpenAI / `gpt-4o-mini` | 239 | 1 | 25 |
| Claude baseline | `experiment_E3_claude_v2` | `outputs/experiment_E3_claude_v2/` | Anthropic / `claude-sonnet-4-6` | 93 | 0 | 24 |

Freeze rule: do not modify extraction, assembly, patchers, figure logic, or verification logic after this point. New scientific scope questions should be answered by policy rescoring from `patched_area.jsonl`, not by rerunning extraction.

## 5. Completed Fixes

| Fix | Change | Main files | Effect |
|---|---|---|---|
| Fix 1 | tiered digitize candidate search | `extractors/figure/digitize.py` | improved early figure recall and routing discipline |
| Fix 2 | calibration curve hard gate | `extractors/figure/triage.py`, `extractors/figure/digitize.py` | removed the known calibration false-positive route |
| Fix 3a | tighter subplot contract | `extractors/figure/triage.py` | repaired panel identity before digitization |
| Fix 4 | raw-tail cleanup + underconstrained mapping gate | `extractors/figure/digitize.py`, `extractors/figure/map_curves.py` | blocked unsafe many-to-few figure mapping |
| Fix 5 | VLM series identity + figure-local grounding | `extractors/figure/vlm_digitize.py`, `extractors/figure/build_records.py` | enabled grounded `vlm_only` figure records |
| Fix 6 | source binding guard | `verification/source_binding_guard.py`, `verification/verify_records.py` | blocks cross-source contamination before final policy classification |
| Fix 3b | calibration-gate retry | `extractors/figure/triage.py`, `extractors/figure/build_records.py`, `extractors/figure/models.py` | retries alternate pages after calibration rejection and can recover one clean figure paper |

## 6. Schema Extension

`ConditionSpec` now includes:
`membrane_type`, `membrane_source`, `membrane_thickness_um`, `receptor_medium`, `dose_type`, `dose_amount`.

The implementation report (`reports/schema_and_table_fix_implementation.md`) confirms that the target-paper smoke test populates `membrane_type`, `membrane_source`, `receptor_medium`, `dose_type`, and `dose_amount` with source-backed values, for example `dermatomed porcine skin`, `porcine`, `PBS (pH 7.4)`, `infinite`, and `infinite dose`.

Round 2 gold quality on the `25` true-positive GPT verified rows is strong for the new fields that were explicitly audited in `reports/gold_evaluation_round2.md`: membrane `25/25` correct, receptor medium `24/25`, and dose type `24/25`. Excipient composition is still usually partial rather than complete.

## 7. Table Extraction Improvement

The table/text prompt bump to `2026-04-11.v1` introduced explicit all-row extraction, explicit multi-timepoint handling, excipient extraction, new condition-field extraction, and deterministic wide-timepoint expansion. HTML table cap increased from `18` to `60` rows, and `table_truncated` plus `truncation_notes` are now written into provenance metadata.

Result: table records increased from `64` in `full_run_13_post_fix5` to `252` in the frozen GPT baseline, a `+294%` increase. The target paper `10.1208/s12249-013-9995-4` is now fully recovered as `F1-F8 x 24/48/72 h = 24` table records, and those same `24` rows are the stable v2 common core across all five reproducibility runs.

## 8. Policy System

| Policy | Scope | GPT verified | Claude verified |
|---|---|---:|---:|
| `v1` | 5% w/w, amount only | 1 | 0 |
| `v2` | `v1` + `5% w/v` / `50 mg/mL` | 25 | 24 |
| `v3` | any ibuprofen concentration | 47 | 38 |
| `v4` | `v3` + flux / Jss / Kp / Papp | 51 | 47 |

Recommended paper policy is `v2`. On Round 2 gold, `v1+v2` gives `25/25 = 100.0%` keep-record precision and `24/25 = 96.0%` end-to-end precision. Wider scopes are useful for sensitivity analysis, but cumulative precision falls to `53.2%` at `v3` and `49.0%` at `v4`.

## 9. Experiment Results Summary

Paper-ready comparison should use the frozen `full_run_16_post_all_fixes` GPT baseline, the same run rescored under `v2`, and the frozen Claude baseline rescored under `v2`. `E2/E4/E6/E7/E8` remain historical `full_run_13`-family ablations that are useful for mechanism interpretation, not as strict like-for-like comparisons against the frozen baseline.

| Experiment | Variable | Verified | Key finding |
|---|---|---:|---|
| GPT baseline (`v1`) | frozen post-all-fixes baseline | 1 | extraction freeze reference point |
| GPT baseline (`v2`) | `v1` + accept `5% w/v` / `50 mg/mL` | 25 | paper-default precision/coverage operating point |
| Claude baseline (`v2`) | same frozen corpus, Anthropic all-stage run | 24 | same `24` stable table core as GPT, but no figure verified |
| E2 | model swap to GPT-5.4 | 4 | no verified-yield gain; non-figure verified stayed at 0 |
| E4 | CV-only figure path | 4 | removing VLM did not improve audited outcomes |
| E6 | no patching | 6 | no evidence that patchers were the verified bottleneck |
| E7 | no table-support promotion | 4 | verified count unchanged under this ablation |
| E8 | relaxed concentration scope | 14 | +10 verified vs `full_run_13` v1, but not suitable as default policy |
| Reproducibility | 5 fresh reruns | `27.20 +/- 3.49` (`v2` mean +/- SD) | `v2` stable core remains `24`, while `v1` remains unstable |

## 10. Single-Pass Architecture Comparison

Round 2 single-pass comparison uses the same `29` papers and the same annotation file as the modular evaluation.

| Method | Gold keep-record recovery | Value-correct recovery | Cost | Readout |
|---|---|---|---|---|
| Modular pipeline (`v2`) | `25/25 = 100.0%` | `24/25 = 96.0%` | not cost-normalized in the comparison report | best precision-controlled acceptance layer |
| SP-1 text (`gpt-4o-mini`) | `7/25 = 28.0%` | `7/24 = 29.2%` | `$0.0850` | too weak on recall |
| SP-2 PDF (`gpt-4o-mini`) | `9/25 = 36.0%` | `9/24 = 37.5%` | `$0.8375` | more expensive than SP-1, still weak |
| SP-3 PDF (`gpt-5.4-mini`) | `24/25 = 96.0%` | `24/24 = 100.0%` | `$0.9734` | strongest single-pass extractor, but still too noisy alone |
| SP-4 PDF (`claude-sonnet-4-6`) | `0/25 = 0.0%` | `0/24 = 0.0%` | `$4.1983` | worst recovery and highest cost in this setup |

Main conclusion: SP-3 is the only credible single-pass extractor, but the paper should not position it as a replacement. The stronger claim is hybrid: high-recall SP-3 proposal generation plus the existing modular verification stack.

## 11. Gold Set Evaluation (Round 2)

Round 2 annotation contains `130` rows across four tiers.

| Scope view | Verified | TP | FP | Precision |
|---|---:|---:|---:|---:|
| `v1 only` | 1 | 1 | 0 | 100.0% |
| `v1+v2` | 25 | 25 | 0 | 100.0% |
| `v3` incremental vs `v2` | 22 | 0 | 22 | 0.0% |
| `v4` incremental vs `v3` | 4 | 0 | 4 | 0.0% |
| `v4 total` | 51 | 25 | 26 | 49.0% |

Additional Round 2 findings:

- End-to-end precision at `v2`: `24/25 = 96.0%`
- Unresolved sample: `0/44` false negatives observed
- Rejection correctness: `12/12 = 100.0%`
- Claude-only verified sample: `0/23` true positives
- Route precision at GPT `v4`: table `72.7%`, figure `100%`, text `0%`, mixed `0%`

## 12. Reproducibility (5 Runs)

`reports/reproducibility_analysis.md` is now the canonical variability reference.

- `v1` verified mean +/- SD: `3.20 +/- 3.49`, `CV = 109.15%`
- `v2` verified mean +/- SD: `27.20 +/- 3.49`, `CV = 12.84%`
- Stable `v2` common core: `24` records
- Common-core route / DOI: all `24` are table-route and all come from `10.1208/s12249-013-9995-4`
- `v1` pairwise agreement: `0.0000` across all 10 run pairs
- `v2` pairwise agreement: `0.6486` to `0.9231`
- New outlier run: `16d` with `9` v1 verified and `33` v2 verified

## 13. Provider Abstraction

Claude integration is complete.

- Entry point: `utils/llm_client.py`
- CLI: `run_pipeline.py --llm-provider {openai, anthropic}`
- All 8 structured LLM stages now use the same provider-neutral parse wrapper
- Anthropic path uses `messages.parse()` first and falls back to tool-based structured output when needed
- `utils/manifest.py` records provider package versions, including `anthropic`

This means GPT and Claude baselines now differ only by provider/model, not by pipeline shape.

## 14. PhD Demonstration Close-Out

The final PhD demonstration was reframed from direct heterogeneous response ranking to structured literature reconnaissance plus condition comparability assessment.

- Updated Paper 1 dataset: `150` rows, `30` formulations, `5` replicates per formulation
- Design groups: `BBD=15`, `LHS=10`, `BO=4`, `OPT=1`
- Search space: all `239` assembled records from the frozen GPT baseline, filtered by a topical/transdermal plausibility guard
- Excipient-match funnel: Level 1 exact match `0`, Level 2 same excipient system `0`, Level 3 partial excipient overlap `26`, Level 4 same API + device `80`

Critical closure result: no extracted record in the current corpus matches `ibuprofen + Franz/diffusion cell + Poloxamer / ethanol / propylene glycol`, and no exact match remains once `Strat-M` / synthetic membrane is also required.

This is now the recommended scientific framing for Paper 4: SkinMiner adds literature intelligence after optimisation. It does not justify direct heterogeneous augmentation of response values across mismatched membrane, excipient, and dose systems.

## 15. Known Limitations

- Figure value precision remains weak on dense multi-curve mapping; both CV and VLM still fail on some label-binding tasks.
- Figure verified output is not stable run to run; Fix `3b` retry only fired in `3/5` reproducibility runs.
- The same figure paper can still produce endpoint variance, for example `150.76` vs `250.0 ug/mL` in different runs.
- `source_context_inconsistent` remains a major unresolved bucket in the GPT baseline.
- Field coverage beyond the verified set is not yet separately audited in a dedicated report, especially for receptor medium and full excipient composition.
- Excipient extraction is usually partial rather than formulation-complete.
- `v3` and `v4` widen scientific scope but introduce many false positives from endpoint, study-type, and device mismatches.
- Validation is ibuprofen-only. No second-drug pilot has been run.
- Retrieval remains OA / Europe PMC centric. Non-OA acquisition, Scopus, and WoS are not yet integrated.

## 16. Key Files

### Reports

- `reports/codex_handoff_2026-04-09.md`
- `reports/baseline_definition.md`
- `reports/gold_evaluation_round2.md`
- `reports/policy_sensitivity_analysis.md`
- `reports/reproducibility_analysis.md`
- `reports/single_pass_architecture_comparison.md`
- `reports/schema_and_table_fix_implementation.md`
- `reports/experiment_summary_all.md` (legacy pre-freeze ablation summary)
- `outputs/demonstration/benchmarking_analysis.md`
- `outputs/demonstration/demonstration_final_summary.md`

### Experiment Outputs

- `outputs/full_run_16_post_all_fixes/`
- `outputs/experiment_E3_claude_v2/`
- `outputs/experiment_E2_gpt54/`
- `outputs/experiment_E4_cv_only/`
- `outputs/experiment_E6_no_patching/`
- `outputs/experiment_E7_no_promotion/`
- `outputs/experiment_E8_relaxed_scope/`
- `outputs/experiment_single_pass/`
- `outputs/experiment_single_pass_pdf_4omini/`
- `outputs/experiment_single_pass_pdf_gpt54/`
- `outputs/experiment_single_pass_pdf_claude/`
- `outputs/reproducibility_run_16a/`, `16b/`, `16c/`, `16d/`
- `outputs/gold_audit_set/round2/`
- `outputs/demonstration/`
- `outputs/paper_figures/`

### Key Source Files

- `run_pipeline.py`
- `schemas/models.py`
- `utils/llm_client.py`
- `verification/verify_records.py`
- `verification/source_binding_guard.py`
- `policies/v1_strict_ibuprofen_5pct.py`
- `policies/v2_accept_wv.py`
- `policies/v3_any_ibuprofen_concentration.py`
- `policies/v4_accept_flux.py`
- `extractors/table/extractor.py`
- `extractors/figure/triage.py`
- `extractors/figure/vlm_digitize.py`
- `extractors/figure/build_records.py`
- `experiments/single_pass_extract.py`
- `experiments/single_pass_pdf_extract.py`
- `experiments/prepare_benchmarking_demo_v2.py`
- `experiments/plot_demonstration_figures.py`
- `experiments/plot_paper_figures.py`

## 17. Recommended Next Steps

1. Write the paper around the `v2` operating point. Use `v3`/`v4` only as sensitivity analysis, not as the main claimed extraction scope.
2. In the architecture discussion, frame SP-3 as a high-recall proposal generator plus modular verification, not as a replacement pipeline.
3. In the PhD closure discussion, frame SkinMiner as a literature reconnaissance and comparability tool, not as evidence for direct cross-study response augmentation.
4. Run a second-drug pilot only after the target molecule and evaluation scope are agreed with the supervisor.
5. Expand the gold set toward more non-figure and non-table-heavy coverage only if another paper revision requires stronger negative-space evidence.
6. Improve excipient extraction quality if formulation-composition reporting becomes central to the paper.

## 18. Do Not Redo

The following work is complete and should not be repeated unless there is a paper-driven reason to reproduce it exactly:

- Fix 1-6 plus Fix 3b diagnosis, implementation, and targeted smoke work
- Schema extension and table extraction improvement
- E2 / E3 / E4 / E6 / E7 / E8 experiment packet
- SP-1 / SP-2 / SP-3 / SP-4 single-pass packet
- Round 2 gold annotation and evaluation
- 5-run reproducibility study
- 4-layer policy sensitivity analysis on frozen GPT and Claude baselines
- Baseline freeze and provider abstraction integration
- PhD closure benchmarking / comparability demonstration
- Paper figure and table generation in `outputs/paper_figures/`
