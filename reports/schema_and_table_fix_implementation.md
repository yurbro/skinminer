# Schema And Table Fix Implementation

Date: 2026-04-11

## Changed Scope

Implemented the approved Fix A + Fix B. No full run was executed.

Changed files:

| File | Change |
|---|---|
| `schemas/models.py` | Added membrane, receptor medium, and dose fields to `ConditionSpec`. |
| `assembly/assemble_records.py` | Preserves the new condition fields when records are merged. |
| `extractors/text/extract_fields.py` | Added new condition fields to the text extraction output model and strengthened prompt requirements. |
| `extractors/text/normalize_fields.py` | Maps text-extracted condition fields into `Record.conditions`. |
| `extractors/table/extractor.py` | Added condition fields, stronger row/timepoint prompt, HTML row cap and truncation metadata, condition-context snippets, and deterministic wide-timepoint expansion. |
| `extractors/figure/vlm_digitize.py` | Passes known condition context into the VLM prompt and forbids inferring new condition fields from the crop. |
| `README.md` / `README.en.md` | Documented the schema and table extraction architecture changes. |

## Prompt Versions Bumped

| Prompt asset | Old version | New version |
|---|---|---|
| `extractors.text.structured_fields` | `2026-03-28.v1` | `2026-04-11.v1` |
| `extractors.table.structured_tables` | `2026-03-28.v1` | `2026-04-11.v1` |
| `extractors.figure.vlm_digitize` | `2026-04-08.v2` | `2026-04-11.v1` |

`run_pipeline.py` already records `PROMPT_ASSETS` into manifest metadata, so future runs will record these bumped versions automatically.

## Table Extraction Changes

The table prompt now explicitly requires:

- every relevant data row;
- no representative-row summarization;
- one record per formulation x timepoint when endpoint values are reported in multiple time columns;
- exact time/value alignment from the same column;
- cumulative amount preference over flux/Jss when both are present;
- no endpoint copying between unrelated composition/stability rows and endpoint rows;
- excipient/vehicle component extraction;
- membrane, receptor medium, and dose fields when source-backed.

HTML table extraction now reads up to 60 rows per table. If a row cap or window char cap is hit, `table_truncated` and `truncation_notes` are written into `table_raw.jsonl` and table record provenance metadata.

Structured wide endpoint tables with cumulative amount time columns are conservatively expanded after LLM extraction into deterministic formulation x timepoint records. This protects against LLM column-alignment failures for tables like `10.1208/s12249-013-9995-4` Table II.

## Smoke Test

Smoke target: `10.1208/s12249-013-9995-4`

Command path: direct one-paper `extract_batch()` over the content handle and route decision from `outputs/full_run_14_v2_policy`.

Output directory:

- `outputs/schema_table_fix_smoke_20260411d/table_raw.jsonl`
- `outputs/schema_table_fix_smoke_20260411d/table_records.jsonl`
- `outputs/schema_table_fix_smoke_20260411d/table_records.csv`

Smoke result:

| Metric | Result |
|---|---:|
| total records | 24 |
| expected F labels found | F1-F8 |
| missing expected label/time cells | 0 |
| mismatched expected values | 0 |
| duplicate record IDs | 0 |
| table_truncated | false |
| raw notes | `deterministic_wide_timepoint_rows=24` |

Expected endpoint matrix recovered:

| Label | 24 h | 48 h | 72 h |
|---|---:|---:|---:|
| F1 | 298.0 | 536.5 | 1142.4 |
| F2 | 155.9 | 580.2 | 1178.9 |
| F3 | 140.2 | 543.5 | 759.6 |
| F4 | 132.3 | 464.8 | 734.4 |
| F5 | 312.3 | 542.5 | 799.5 |
| F6 | 148.8 | 551.2 | 808.0 |
| F7 | 123.9 | 260.1 | 387.9 |
| F8 | 132.3 | 464.8 | 734.4 |

Sample condition fields from the smoke output:

| Field | Value |
|---|---|
| `membrane_type` | `dermatomed porcine skin` |
| `membrane_source` | `porcine` |
| `receptor_medium` | `PBS (pH 7.4)` |
| `dose_type` | `infinite` |
| `dose_amount` | `infinite dose` |

## Verification

Commands/checks run:

- `python -m py_compile schemas/models.py assembly/assemble_records.py extractors/table/extractor.py extractors/text/extract_fields.py extractors/text/normalize_fields.py extractors/figure/vlm_digitize.py run_pipeline.py`
- Existing `full_run_14_v2_policy` JSONL records validate against the expanded `Record` schema.
- Smoke output validates against the expanded `Record` schema, with 24 unique record IDs.

## Notes

The smoke test is intentionally one-paper only. A future full run will change table record counts because wide timepoint tables now emit multiple endpoint-time records instead of a single final or misaligned row.
