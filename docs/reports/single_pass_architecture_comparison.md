# Single-Pass Architecture Comparison

## 1. Scope and Baseline

This comparison uses the same Round2 DOI subset of `29` unique papers and the same annotation file `outputs/gold_audit_set/round2/gold_set_round2_annotation.csv`.

The modular baseline is the post-fix pipeline gold audit in `reports/gold_evaluation_round2.md`. Its key reference numbers are:

- Gold keep-record recovery: `25/25 = 100.0%`
- End-to-end value-correct recovery on the keep-record set: `24/25 = 96.0%`
- Verified precision on the annotated Tier1 sample: `25/51 = 49.0%`
- Verified end-to-end precision on the annotated Tier1 sample: `24/51 = 47.1%`

For the single-pass runs, precision is not directly observable in the same way because there is no verifier/gating layer. The most comparable metrics are therefore:

- Positive-side recovery: gold TP coverage and value correctness
- Precision-risk proxies: annotated FP matches, unmatched extra records, and gold-negative DOI that still emitted records
- Cost and structured-output stability

## 2. Experiment Summary

| Run | Input | Model | Successful papers | Raw records | Gold TP covered | Value correct | Annotated FP matches | Extra unmatched | Gold-negative DOI with output | Tokens | Cost |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SP-1 | text + HTML tables | `gpt-4o-mini` | `27/29` (`2` source-poor empty) | `151` | `7/25 = 28.0%` | `7/24 = 29.2%` | `9` | `134` | `17/27` | `448,155` | `$0.0850` |
| SP-2 | raw PDF | `gpt-4o-mini` | `29/29` | `106` | `9/25 = 36.0%` | `9/24 = 37.5%` | `3` | `94` | `18/27` | `5,479,257` | `$0.8375` |
| SP-3 | raw PDF | `gpt-5.4-mini` | `29/29` | `288` | `24/25 = 96.0%` | `24/24 = 100.0%` | `18` | `222` | `18/27` | `775,296` | `$0.9734` |
| SP-4 | raw PDF | `claude-sonnet-4-6` | `23/29` | `132` | `0/25 = 0.0%` | `0/24 = 0.0%` | `5` | `124` | `11/27` | `1,073,320` | `$4.1983` |

Notes:

- `Value correct` uses the `24` value-anchored Round2 gold rows, matching the existing evaluation design.
- SP-4 had `29/29` callable PDFs, but only `23/29` returned parseable JSON. The six structured-output failures were:
  `10.1016/j.ijpharm.2016.03.043`, `10.1016/j.jpba.2019.04.040`, `10.1186/2050-6511-13-5`, `10.1208/s12249-013-9995-4`, `10.1208/s12249-019-1481-1`, `10.21203/rs.3.rs-3773667/v1`.

## 3. Readout

### 3.1 Best single-pass variant

SP-3 is the only single-pass variant that approaches the modular pipeline on positive-side recovery. It recovered `24/25` gold keep-record rows and was `24/24` correct on the value-anchored gold rows. On the positive side alone, this is near-parity with the modular baseline.

That said, SP-3 is not production-safe as a standalone architecture. It emitted `288` raw records, matched `18` annotated false-positive rows, produced `222` unmatched extra records, and emitted records on `18/27` gold-negative DOI. The experiment shows that strong raw extraction is possible, but it also shows that the verifier/gating layer is still doing essential work.

### 3.2 GPT-4o-mini results

SP-1 and SP-2 are both materially below the modular baseline on recall/value recovery. SP-1 text-only reached `7/25` TP coverage; SP-2 raw PDF improved this only to `9/25`.

SP-2 did reduce the immediate precision-risk proxies versus SP-1 (`3` annotated FP matches vs `9`, and `94` extras vs `134`), but the gain in positive recovery was too small to justify the much higher billed token count. In this setup, raw PDF alone does not rescue `gpt-4o-mini`.

### 3.3 Claude result

SP-4 is not competitive in the current setup. Even after fixing rate-limit retry behavior and rerunning failed DOI, it still ended at `23/29` parseable papers and `0/25` gold TP coverage.

This should be interpreted as a structured-output failure mode in this exact prompt/schema configuration, not as a general claim about Claude quality. For this experiment, however, the observed result is clear: it is both the most expensive run and the weakest by the gold-matching metric.

### 3.4 Cost observations

Two cost facts matter:

1. SP-3 was only slightly more expensive than SP-2 (`$0.9734` vs `$0.8375`) while delivering a much larger recovery gain (`24/25` vs `9/25`).
2. SP-2 billed far more tokens than SP-3 (`5.48M` vs `0.78M`) despite being the weaker model/run. This is an observed API-accounting result from the run outputs, not an assumption.

So if the project ever revisits single-pass seriously, the viable direction is not "cheaper PDF single-pass with 4o-mini"; it is "stronger PDF single-pass with 5.4-mini, then add verification."

## 4. Architecture Conclusion

The modular pipeline remains the better production architecture.

Reasons:

1. It still gives the strongest precision-controlled outcome: `25/25` gold keep-record recovery, `24/25` value-correct recovery, and explicit verified precision `25/51 = 49.0%` on the annotated Tier1 sample.
2. It has route provenance, field-level evidence, verifier decisions, and failure taxonomy. Single-pass only gives a free-text `source_evidence` field, which is not enough for robust source binding or automated gating.
3. The best single-pass run, SP-3, demonstrates strong extraction capacity but also demonstrates why verification cannot be removed. Its recall is good; its raw record stream is still too noisy.

The highest-leverage next architecture, if the project wants one, is therefore not a standalone single-pass replacement. It is a hybrid:

- Use raw-PDF `gpt-5.4-mini` single-pass as a high-recall proposal generator
- Feed those proposals into the existing modular verification/gating stack
- Keep the modular provenance model as the acceptance layer

## 5. Artifact Map

- Modular baseline: `reports/gold_evaluation_round2.md`
- SP-1 gold evaluation: `outputs/experiment_single_pass/single_pass_vs_gold_evaluation.md`
- SP-1 pipeline comparison: `outputs/experiment_single_pass/single_pass_vs_pipeline_comparison.md`
- SP-2 gold evaluation: `outputs/experiment_single_pass_pdf_4omini/single_pass_vs_gold_evaluation.md`
- SP-2 pipeline comparison: `outputs/experiment_single_pass_pdf_4omini/single_pass_vs_pipeline_comparison.md`
- SP-3 gold evaluation: `outputs/experiment_single_pass_pdf_gpt54/single_pass_vs_gold_evaluation.md`
- SP-3 pipeline comparison: `outputs/experiment_single_pass_pdf_gpt54/single_pass_vs_pipeline_comparison.md`
- SP-4 gold evaluation: `outputs/experiment_single_pass_pdf_claude/single_pass_vs_gold_evaluation.md`
- SP-4 pipeline comparison: `outputs/experiment_single_pass_pdf_claude/single_pass_vs_pipeline_comparison.md`
