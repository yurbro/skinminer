# Paper to repository mapping

This document maps the manuscript, published repository labels, archived run directories, source files, and reproducible commands. It is the canonical naming reference for the other repository documents.

Paper title: *SkinMiner: LLM-powered data mining to accelerate formulation design for skin products*  
Status as of 2026-10-12: Submitted to *International Journal of Pharmaceutics* on 12 October 2026  
Corresponding author: Tao Chen

Submission is confirmed by the author-verification email reported by the author on 12 October 2026. A submission acknowledgement or assigned manuscript number does not establish editorial handling, external peer review, or acceptance; none of those later stages has been independently confirmed as of that date. Update each stage only when supported by a dated journal-system record or editorial communication.

## Historical title mapping

| Title | Role |
|---|---|
| *SkinMiner: LLM-powered data mining to accelerate formulation design for skin products* | Formal submission title, 12 October 2026; use for current manuscript references |
| *SkinMiner: An LLM-powered data mining framework for dermal drug formulations* | Earlier repository/manuscript working title; retained here for provenance |

The earlier `Manuscript under review` label was not supported by independent evidence of journal peer review. The title and status correction does not change run labels, archived paths, figure/table mappings, or reported experimental results below.

## Run labels

Public documentation and paths use the readable labels in the first column. The archived names appear here only to preserve provenance.

| Readable label | Archived source directory | Manuscript role |
|---|---|---|
| `gpt-extended-baseline` | `outputs/full_run_16_post_all_fixes` | GPT Extended baseline, first Extended repeat, GPT policy sensitivity |
| `claude-extended-baseline` | `outputs/experiment_E3_claude_v2` | Claude Extended baseline and Claude policy sensitivity |
| `gpt-extended-rerun-1` | `outputs/reproducibility_run_16a` | Extended and Strict repeat 2 |
| `gpt-extended-rerun-2` | `outputs/reproducibility_run_16b` | Extended and Strict repeat 3 |
| `gpt-extended-rerun-3` | `outputs/reproducibility_run_16c` | Extended and Strict repeat 4 |
| `gpt-extended-rerun-4` | `outputs/reproducibility_run_16d` | Extended and Strict repeat 5 |
| `demo2-bolla-pdf-entry` | `outputs/phase2_demo2_audit/bolla_full_real` | Bolla PDF entry-point audit for Demo 2 |
| `single-pass-text-gpt-4o-mini` | `outputs/experiment_single_pass` | SP-1, extracted text input |
| `single-pass-pdf-gpt-4o-mini` | `outputs/experiment_single_pass_pdf_4omini` | SP-2, full PDF input |
| `single-pass-pdf-gpt-5-4-mini` | `outputs/experiment_single_pass_pdf_gpt54` | SP-3, full PDF input |
| `single-pass-pdf-claude-sonnet-4-6` | `outputs/experiment_single_pass_pdf_claude` | SP-4, full PDF input |

## Acceptance policies

`policy_level` records the first policy at which a record is accepted. Manuscript results at a policy level use the cumulative set through that level. For example, Extended includes records first accepted at Strict or Extended.

| Code policy | Stored first level | Manuscript label | Cumulative levels used for scoring |
|---|---|---|---|
| `v1_strict_ibuprofen_5pct` | `v1` | Strict | `{v1}` |
| `v2_accept_wv` | `v2` | Extended | `{v1, v2}` |
| `v3_any_ibuprofen_concentration` | `v3` | Any-concentration | `{v1, v2, v3}` |
| `v4_accept_flux` | `v4` | Flux-augmented | `{v1, v2, v3, v4}` |

The Round-2 loader exposes both `first_level_filter` and `cumulative_levels` in its output so the aggregation is auditable.

## Reproduction command keys

Run commands from the repository root with the locked environment described in [reproducibility.md](reproducibility.md).

### Evaluation metrics

```bash
python -m evaluation.score_run \
  --gold-format round2 \
  --provider gpt \
  --policy-level v2 \
  --gold-csv evaluation/gold/gold_set_round2_annotation.csv
```

For Claude, add the provider aggregate:

```bash
python -m evaluation.score_run \
  --gold-format round2 \
  --provider claude \
  --policy-level v2 \
  --gold-csv evaluation/gold/gold_set_round2_annotation.csv \
  --provider-metrics-csv evaluation/data/provider_policy_reference.csv
```

### Paper figure bundle

```bash
python experiments/plot_paper_figures.py \
  --fig7b-data results/paper_figures/fig7b_provider_policy_metrics.csv \
  --output-dir results/paper_figures
```

This command regenerates the static figure bundle from the published summaries. Some plots also depend on the retained report summaries documented below. It does not recover excluded record-level JSONL.

### Table 3 audit

```bash
python demos/demo1/table3_stats.py \
  --records-csv demos/demo1/data/watkinson_audit/master_table_v15_normalized.csv \
  --reference-csv demos/demo1/table3_paper_reference.csv \
  --output-csv demos/demo1/outputs/table3_rebuilt.csv \
  --summary-json demos/demo1/outputs/table3_summary.json
```

### Demo 1

```bash
python demos/demo1/rebuild_demo1.py
```

### Demo 2 main transfer figure

```bash
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_4feature.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_figure.py
```

### Demo 2 ratio sweep and feature space

```bash
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_sweep.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_lines_redraw.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_mechanism.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_feature_space_figure.py
```

## Manuscript figures and tables

| Manuscript item | Reported values or purpose | Published source files | Reproduction command |
|---|---|---|---|
| Fig. 6 | Corpus flow: 1,828; 749/1,079; 536/213; 56/480; 38/18; 2/36 | `results/paper_figures/figA_sankey_data.csv`, `figA_pipeline_architecture.pdf`, `figA_pipeline_architecture.png` | Paper figure bundle |
| Fig. 7A | Value agreement, R² 0.9652 shown as 0.97; value accuracy 24/25, 96% | `results/paper_figures/figF_value_accuracy_data.csv`, `figF_value_accuracy.pdf`, `figF_value_accuracy.png`; `evaluation/gold/gold_set_round2_annotation.csv` | Paper figure bundle and Evaluation metrics |
| Fig. 7B | Two providers across four cumulative acceptance levels | `results/paper_figures/fig7b_provider_policy_metrics.csv`, `table_policy_sensitivity.csv`, `figD_policy_sensitivity.pdf`, `figD_policy_sensitivity.png` | Paper figure bundle |
| Fig. 8 | Pipeline and SP-1 to SP-4 coverage and cost | `results/paper_figures/table_single_pass.csv`, `table_resource_comparison.csv`, `figC_single_pass_comparison.pdf`, `figC_single_pass_comparison.png`; five readable run directories | Paper figure bundle |
| Fig. 9 | Demo 2 transfer result and protocol red flags | `demos/demo2/outputs/phase2_demo2_modelling/figure_demo2_main.pdf`, `.png`, `transfer_4feature_xiao_to_bolla.csv`, `protocol_distance.json`, `demo2_figure_report.md` | Demo 2 main transfer figure |
| Fig. 10 | Demo 1 zero-shot predictions and few-shot calibration | `demos/demo1/outputs/fig10_demo1_rebuilt.pdf`, `.png`, `predictions_zero_shot_rebuilt.csv`, `fewshot_results_rebuilt.csv` | Demo 1 |
| Table 2 | Strict repeats 1,1,1,4,9; Extended repeats 25,25,25,28,33; mean, SD, CV, stable core and Jaccard | `results/paper_figures/table_reproducibility.csv`; `results/runs/gpt-extended-baseline/` and `gpt-extended-rerun-1` through `-4` | Paper figure bundle. Stable-core and Jaccard remain static report-derived summaries because no standalone set aggregation CLI is published |
| Table 3 | 47 Watkinson records across ten paper and source-table groups | `demos/demo1/data/watkinson_audit/master_table_v15_normalized.csv`, `demos/demo1/table3_paper_reference.csv` | Table 3 audit |
| Table 4 | Four model and feature rows, five metrics per row | `demos/demo1/outputs/table4_rebuilt.csv`, `table4_comparison.csv` | Demo 1 |

### Fig. 7B points

| Provider | Level | Verified | Scope precision |
|---|---|---:|---:|
| GPT | Strict | 1 | 100% |
| GPT | Extended | 25 | 100% |
| GPT | Any-concentration | 47 | 53.1915% |
| GPT | Flux-augmented | 51 | 49.0196% |
| Claude | Strict | 0 | N.A. |
| Claude | Extended | 24 | 100% |
| Claude | Any-concentration | 38 | 63.1579% |
| Claude | Flux-augmented | 47 | 59.5745% |

### Fig. 8 values

| Configuration | Gold coverage | Cost in published summary |
|---|---:|---:|
| Modular pipeline | 25/25, 100% | USD 0.71, raw value 0.71382135 |
| SP-1 | 7/25, 28% | USD 0.0850 |
| SP-2 | 9/25, 36% | USD 0.8375 |
| SP-3 | 24/25, 96% | USD 0.9734 |
| SP-4 | 0/25, 0% | USD 4.1983 |

## Text results outside tables and figures

| Manuscript result | Value | Published source |
|---|---:|---|
| Extended value accuracy | 24/25, 96% | `evaluation/gold/gold_set_round2_annotation.csv`; Evaluation metrics command |
| Correct rejection sample | 12/12 | Same gold CSV and command |
| Unresolved sample retained by gold | 0/44 | Same gold CSV and command. This is a sampled audit statement |
| SP-3 emitted records | 288 | `results/runs/single-pass-pdf-gpt-5-4-mini/summary.json` |
| SP-3 gold coverage | 24/25 | Same summary and `single_pass_vs_gold_evaluation.md` |
| SP-3 annotated negative matches | 18 | Same summary and evaluation report. The 18 are annotated matches, not an exhaustive false-positive count across all 288 records |
| SP-4 emitted records | 132 | `results/runs/single-pass-pdf-claude-sonnet-4-6/summary.json` |
| SP-4 gold coverage | 0/25 | Same summary and evaluation report |
| SP-4 records matched to annotated out-of-scope rows | 8 records mapped to 5 gold rows | `results/runs/single-pass-pdf-claude-sonnet-4-6/sp4_gold_alignment.csv` |
| SP-4 records with no record-level gold match | 124 | Same matcher file and summary |

SP-4 produced 132 schema-valid records from 23 of 29 PDFs. Its failure was semantic: scope, active ingredient, endpoint selection, unit interpretation, and unsupported record proliferation. Eight records aligned with annotated out-of-scope rows, 124 had no record-level gold counterpart, and none matched a gold true positive.

## Demo scripts and manuscript sections

| Demo | Manuscript location | Primary scripts | Supporting scripts |
|---|---|---|---|
| Demo 1, Watkinson formulation modelling | Section 3.2; Table 3; Table 4; Fig. 10 | `demos/demo1/rebuild_demo1.py`, `demos/demo1/table3_stats.py` | Inputs and audit data under `demos/demo1/data/` |
| Demo 2, cross-protocol transfer | Section 3.3; Fig. 9; Supplementary Note S3 | `run_demo2_4feature.py`, `run_demo2_figure.py`, `run_demo2_ratio_sweep.py`, `run_demo2_mechanism.py` | Remaining CORE and SUPPORT scripts in `demos/demo2/outputs/phase2_demo2_modelling/` |

## Archived names embedded in published result content

The public directory names are clean. Twelve retained provenance fields still point to archived locations because they describe the inputs used when the reports were generated.

| Published file group | Embedded archived value | Interpretation |
|---|---|---|
| `results/runs/single-pass-text-gpt-4o-mini/single_pass_vs_gold_evaluation.md` | `outputs/experiment_single_pass/single_pass_results.jsonl` | Excluded record-level source |
| `results/runs/single-pass-pdf-gpt-4o-mini/` two Markdown reports | `outputs/experiment_single_pass_pdf_4omini` | Archived run provenance |
| `results/runs/single-pass-pdf-gpt-5-4-mini/` two Markdown reports | `outputs/experiment_single_pass_pdf_gpt54` | Archived run provenance |
| `results/runs/single-pass-pdf-claude-sonnet-4-6/` two Markdown reports | `outputs/experiment_single_pass_pdf_claude` | Archived run provenance |
| `results/paper_figures/table_single_pass.csv` | `outputs/experiment_single_pass/...` | Archived source column |
| `results/paper_figures/table_resource_comparison.csv` | Four archived single-pass summary paths | Archived source column |

These strings do not expose local absolute paths. They are retained only as provenance and resolve through the run-label table at the top of this document.

## Reproducibility boundaries

- The repository publishes aggregate run reports. Record-level JSONL remains in restricted external archival storage because it contains extensive source-derived text.
- Fig. 7A R² treats 24 exact manual labels as equality anchors and one near label as an independently parsed numeric value. The 96% value-accuracy result is the primary manual correctness statistic.
- Claude policy points come from the sanitized provider aggregate. The raw Claude audit package is not public.
- Table 2 stable-core and pairwise Jaccard values are traceable to static reports and the five retained run summaries. A dedicated set aggregation command is not included in this release.
