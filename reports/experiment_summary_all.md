# Final Experiment Summary

Date: 2026-04-11

This summary consolidates the closing experiment packet for the SkinMiner framework. Counts are final verification statuses from each run's `verify_final` stage unless noted otherwise.

## Core Results

| Experiment | Variable | verified | unresolved | rejected | Key finding |
|---|---|---:|---:|---:|---|
| Baseline (`full_run_13`, v1) | baseline | 4 | 48 | 27 | Post-Fix-5 baseline; verified output remains figure-only. |
| E2 (`GPT-5.4`) | model | 4 | 47 | 10 | No verified-yield gain; non-figure routes still produced zero verified records. |
| E4 (`CV-only`) | VLM ablation | 4 | 48 | 28 | Removing VLM did not change verified count; downstream mapping became weaker. |
| V2 (`full_run_14`) | policy accepts `5% w/v` / `50 mg/mL` | 10 | 43 | 22 | Net +6 verified, entirely table-route gains from `5% w/v` records. |
| E8 (`any concentration`) | relaxed concentration policy | 14 | 37 | 23 | Net +10 verified vs v1; 12 new verified records from 5 papers, no non-ibuprofen verified rows observed. |
| E6 (`no patching`) | patching ablation | 6 | 49 | 23 | No verified-count loss; patching mainly reshaped evidence/failure taxonomy under this corpus. |
| E7 (`no promotion`) | table-support promotion ablation | 4 | 47 | 22 | No verified-count loss; table route stayed at 0 verified under v1. |
| E3 (`Claude`) | model vendor | n/a | n/a | n/a | Not run; integration assessed at 730-1,110 LOC and requires a provider abstraction. |
| Reproducibility (`13b`) | same runtime config | 2 | 65 | 23 | Not record-stable; verified count changed 4 -> 2 with zero verified record-id overlap. |

## Main Conclusions

The only intervention that clearly increased verified yield was policy relaxation. V2 recovered table-route `5% w/v` cases, and E8 recovered additional lower/unspecified concentration cases while keeping the non-concentration gates. This indicates that the verification ceiling is currently dominated by policy scope and concentration interpretation rather than raw model capability.

Model substitution alone did not solve the bottleneck. E2 preserved verified=4 despite using the GPT-5.4 configuration, and E4 showed that removing the VLM path did not reduce verified count in the current audit/run setting. Non-figure extraction remains the main unresolved route-quality target.

The ablations do not show direct verified-count dependence on patching or table-support promotion in the current fresh runs. E6 and E7 are still useful because they identify where patching/promotion affects evidence completion, failure buckets, and metadata, but their final verified deltas are confounded by run-to-run LLM stochasticity.

The reproducibility run is the main caution for the Results section: aggregate route-level conclusions are usable, but record-level comparisons across independent fresh LLM runs are unstable. For module-level claims, prefer fixed intermediate artifacts or replay-style controlled comparisons.

## Key Artifacts

| Artifact | Path |
|---|---|
| V2 supplemental annotation packet | `outputs/gold_audit_set/v2_supplemental/v2_annotation_packet.md` |
| V2 supplemental CSV | `outputs/gold_audit_set/v2_supplemental/v2_annotation_candidates.csv` |
| V2 policy comparison | `outputs/full_run_14_v2_policy/report/v1_vs_v2_comparison.md` |
| E8 vs v1 delta | `outputs/experiment_E8_relaxed_scope/report/delta_vs_v1_baseline.md` |
| E8 vs v2 delta | `outputs/experiment_E8_relaxed_scope/report/delta_vs_v2.md` |
| E6 patching ablation | `outputs/experiment_E6_no_patching/report/E6_delta_vs_baseline.md` |
| E7 promotion ablation | `outputs/experiment_E7_no_promotion/report/E7_delta_vs_baseline.md` |
| E3 Claude workload assessment | `reports/E3_claude_integration_assessment.md` |
| Reproducibility comparison | `outputs/reproducibility_run_13b/report/reproducibility_comparison.md` |

## Experiment Notes

V2 should remain provisional until the supplemental annotation is completed, because its main gain depends on accepting `w/v` concentration basis as scientifically valid for the target definition.

E8 is best framed as a ceiling/scope-sensitivity experiment, not as a proposed default policy. It explicitly accepts any ibuprofen concentration, including rows with concentration recorded as `n/a` when `api_name=ibuprofen` and other gates pass. Under the current no-verification-logic-change constraint, salts or derivatives only pass if upstream extraction normalizes their `api_name` to `ibuprofen`.

E3 was intentionally stopped at assessment. A credible Claude run requires Anthropic SDK dependency management, structured-output compatibility checks, image payload conversion, usage normalization, manifest/resume safeguards, and README updates.
