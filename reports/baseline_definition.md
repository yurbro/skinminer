# SkinMiner Baseline Definition

Date: 2026-04-17

## Frozen Baselines

### GPT Baseline

- Run: `full_run_16_post_all_fixes`
- Output: `outputs/full_run_16_post_all_fixes/`
- Provider: OpenAI
- Model: `gpt-4o-mini` (all stages)
- Corpus: `outputs/full_run_12_full/corpus.csv` (1828 rows)
- Rule-pass rows: 749
- Post-patch rescore input: `outputs/full_run_16_post_all_fixes/patched_area.jsonl` (239 records)
- Code version: post Fix 1-6 + Fix 3b + schema expansion + table extraction fix + Claude provider integration
- Policy: `v1_strict_ibuprofen_5pct`
- Prompt versions:
  - `triage.abstract_relevance`: `2026-03-28.v1`
  - `routing.structured_first`: `2026-03-28.v1`
  - `extractors.text.structured_fields`: `2026-04-11.v1`
  - `extractors.table.structured_tables`: `2026-04-11.v1`
  - `extractors.figure.triage`: `2026-04-06.v1`
  - `extractors.figure.vlm_digitize`: `2026-04-11.v1`
  - `extractors.figure.curve_map`: `2026-03-28.v1`
  - `verification.llm_adjudication`: `2026-04-03.v1`

### Claude Baseline

- Run: `experiment_E3_claude_v2`
- Output: `outputs/experiment_E3_claude_v2/`
- Provider: Anthropic
- Model: `claude-sonnet-4-6` (all stages)
- Corpus: `outputs/full_run_12_full/corpus.csv` (1828 rows, same as GPT)
- Rule-pass rows: 749
- Post-patch rescore input: `outputs/experiment_E3_claude_v2/patched_area.jsonl` (93 records)
- Code version: same as GPT baseline
- Policy: `v1_strict_ibuprofen_5pct`
- Prompt versions:
  - `triage.abstract_relevance`: `2026-03-28.v1`
  - `routing.structured_first`: `2026-03-28.v1`
  - `extractors.text.structured_fields`: `2026-04-11.v1`
  - `extractors.table.structured_tables`: `2026-04-11.v1`
  - `extractors.figure.triage`: `2026-04-06.v1`
  - `extractors.figure.vlm_digitize`: `2026-04-11.v1`
  - `extractors.figure.curve_map`: `2026-03-28.v1`
  - `verification.llm_adjudication`: `2026-04-03.v1`

## Freeze Rules

1. Do not modify extraction, verification, assembly, patchers, or figure pipeline logic after this freeze point.
2. Use policy rescore only to test different scientific scope definitions.
3. Treat `full_run_16_post_all_fixes` extraction products as the GPT baseline.
4. Treat `experiment_E3_claude_v2` extraction products as the Claude baseline.
5. New policies should rescore `patched_area.jsonl`; do not rerun LLM extraction.

## Extraction Products Available For Rescore

- GPT: `outputs/full_run_16_post_all_fixes/patched_area.jsonl`
- Claude: `outputs/experiment_E3_claude_v2/patched_area.jsonl`

## Readability Check

- GPT `patched_area.jsonl`: exists, readable, 239 validated `Record` objects.
- Claude `patched_area.jsonl`: exists, readable, 93 validated `Record` objects.
