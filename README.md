# SkinMiner

SkinMiner turns dermal drug formulation literature into structured, policy-audited records with traceable evidence.

> **Paper:** *SkinMiner: An LLM-powered data mining framework for dermal drug formulations*  
> **Authors:** `<TO_FILL>`  
> **Status:** [Manuscript under review]

## What this does

SkinMiner discovers candidate papers, resolves permitted full text, routes evidence to text, table, or figure extractors, and assembles typed formulation records. It verifies each record against explicit scientific acceptance policies. It preserves evidence locators and failure reasons for audit. The repository also provides a processed gold set, aggregate paper results, and two reproducible modelling demos.

## Pipeline overview

```text
corpus → triage → access → routing → extractors → assembly → verification → patchers → reports
```

See [docs/architecture.md](docs/architecture.md) for stage contracts and data flow.

## Installation

SkinMiner supports Python 3.11 and 3.12. Python 3.11 matches the validated reconstruction environment.

```bash
git clone https://github.com/yurbro/skinminer.git
cd skinminer
python -m venv .venv
```

Activate the environment before installing or running SkinMiner. On POSIX shells:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the package:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

`pyproject.toml` defines the minimal imported dependencies with compatible version ranges. `requirements-lock.txt` pins the direct dependencies used for verification. Use the lock file when reproducing manuscript results:

```bash
python -m pip install -r requirements-lock.txt
```

Copy the environment template and fill the required values:

```bash
cp .env.example .env
```

Set `OPENAI_API_KEY` for OpenAI extraction and `UNPAYWALL_EMAIL` for Unpaywall access. Set `ANTHROPIC_API_KEY` only when selecting the Anthropic provider. The repository does not commit `.env`. Load its values into your shell before running API-dependent commands.

## Quick start

Validate the bundled synthetic fixture offline:

```bash
python -B -m evaluation.validate_gold_labels --gold-jsonl evaluation/fixtures/gold_labels.small.jsonl
```

Expected output: `Validated gold-label entries: 1`. This command does not use the network or consume model tokens.

## Reproducing the paper

### Evaluation metrics

```bash
python -m evaluation.score_run \
  --gold-format round2 \
  --provider gpt \
  --policy-level v2 \
  --gold-csv evaluation/gold/gold_set_round2_annotation.csv
```

Expected key values: 25 verified, 25 scope true positives, 0 scope false positives, 100% scope precision, 24 scope-and-value true positives, and 96% end-to-end precision. The same audit reports 12/12 correct rejections and 0/44 unresolved rows marked for retention.

### Demo 1

```bash
python demos/demo1/rebuild_demo1.py
```

Expected key values: all 20 Table 4 cells match at displayed precision. The script reports 4 EXACT and 16 ROUNDING_MATCH cells. At k=5, it reproduces RMSE 0.114 and Spearman SD values 0.186 with solubility and 0.311 without solubility.

### Demo 2

```bash
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_4feature.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_figure.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_sweep.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_lines_redraw.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_mechanism.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_feature_space_figure.py
```

Expected key values: Xiao to Bolla transfer gives Spearman 0.43, conventional R² -0.32, and 3/8 predictions within twofold. The protocol audit flags 5/8 dimensions. PC1 and PC2 explain 88.8% of feature-space variance, and 0/8 literature points lie inside the in-house four-dimensional hyperrectangle.

The full number-to-file trace appears in [docs/paper_mapping.md](docs/paper_mapping.md). Reproducibility assumptions and version sensitivity appear in [docs/reproducibility.md](docs/reproducibility.md).

## Repository layout

```text
access/          Resolve permitted article content and source provenance.
assembly/        Merge extracted fragments into canonical records.
configs/         Define run and query profiles.
corpus/          Build and freeze bibliographic corpora.
data/frozen/     Store the released bibliographic corpus snapshot.
demos/demo1/     Rebuild Watkinson Table 3, Table 4, few-shot results, and Fig. 10.
demos/demo2/     Reproduce cross-protocol transfer, ratio sweep, and feature-space analyses.
detection/       Route evidence to text, table, figure, or mixed extraction.
docs/            Document architecture, policies, failures, provenance, and reproduction.
evaluation/      Load the gold set, score cumulative policies, and run regression tests.
experiments/     Provide retained paper-analysis and audit scripts.
extractors/      Extract structured records from text, tables, and figures.
patchers/        Apply narrow deterministic record corrections.
policies/        Implement the four acceptance levels.
reports/         Build aggregate run reports.
results/         Store curated aggregate run reports and paper-figure inputs.
schemas/         Define shared Pydantic data contracts.
triage/          Filter and prioritize candidate papers.
utils/           Provide I/O, model-client, manifest, resume, and unit helpers.
verification/    Verify scope and adjudicate ambiguous records.
```

## What is not in this repository

The public repository excludes:

- source-paper PDFs because redistribution rights vary by publisher
- figure page images, crops, masks, overlays, and mapping zooms because they reproduce source material
- record-level run JSONL because it contains extensive source-derived text and creates a large archive
- the raw Claude audit package because it contains source-derived text and third-party contact information

The aggregate files needed for manuscript figures and metrics remain public. Restricted record-level research artifacts are intended for a controlled Zenodo or OSF archive. Request metadata or access instructions through the repository issue tracker. Access remains subject to copyright, privacy, and research-governance review.

## Licensing

SkinMiner source code is licensed under the [Apache License 2.0](LICENSE). The [NOTICE](NOTICE) file records project attribution, funding, and the separate terms that apply to the released gold-standard data.

The gold-standard data under `evaluation/` is released under CC BY 4.0 as described in [LICENSE-DATA](LICENSE-DATA). Apache-2.0 does not apply to that data. Third-party bibliographic metadata and source-derived text retain their source terms. The processed gold CSV records provenance in `source_license`, `source_license_url`, `source_license_source`, `source_license_checked_at`, and `verbatim_action`.

The gold-data release keeps bibliographic titles and factual concentration strings. It keeps annotator-authored notes. It keeps source quotations when the recorded source license permits redistribution. It replaces non-permitted quotations with a DOI, page, and figure or table locator.

## Citation

```bibtex
@article{skinminer2026,
  author = {<TO_FILL>},
  title = {SkinMiner: An LLM-powered data mining framework for dermal drug formulations},
  year = {2026},
  note = {Manuscript under review},
  url = {https://github.com/yurbro/skinminer}
}
```

GitHub citation metadata is available in [CITATION.cff](CITATION.cff).

## Acknowledgements

This work was jointly funded by the China Scholarship Council and the University of Surrey, Grant No. 202306440060.
