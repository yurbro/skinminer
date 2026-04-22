# Schema Extension And Table Extraction Diagnosis

Date: 2026-04-11

## 1. Schema Changes Completed

Changed files:

| File | Change |
|---|---|
| `schemas/models.py` | Added new condition fields to `ConditionSpec` with backward-compatible defaults. |
| `assembly/assemble_records.py` | Preserves the new condition fields when merging records. |
| `README.md` | Documented `formulation.components` and the expanded `conditions` fields. |
| `README.en.md` | Same documentation update in English. |

New `ConditionSpec` fields:

| Field | Type | Default |
|---|---|---|
| `membrane_type` | `str` | `""` |
| `membrane_source` | `str` | `""` |
| `membrane_thickness_um` | `float | None` | `None` |
| `receptor_medium` | `str` | `""` |
| `dose_type` | `str` | `""` |
| `dose_amount` | `str` | `""` |

Compatibility checks:

- `python -m py_compile schemas/models.py assembly/assemble_records.py run_pipeline.py` passed.
- Existing `full_run_14_v2_policy` `table_records.jsonl`, `assembled_records.jsonl`, and `verified_records.jsonl` all validate against the expanded `Record` schema.

No verification, policy, failure taxonomy, gold-set, prompt, or extractor logic was changed.

## 2. `FormulationSpec.components` Current Use

`FormulationSpec.components` already exists and is populated in current runs, but prompt coverage is incomplete.

Observed component population:

| Run | File | Records | Records with components | Component rows |
|---|---|---:|---:|---:|
| `full_run_14_v2_policy` | `table_records.jsonl` | 60 | 44 | 88 |
| `full_run_14_v2_policy` | `text_records.jsonl` | 13 | 13 | 23 |
| `full_run_14_v2_policy` | `figure_records.jsonl` | 7 | 5 | 18 |
| `experiment_E2_gpt54` | `table_records.jsonl` | 70 | 48 | 120 |
| `full_run_13_post_fix5` | `table_records.jsonl` | 64 | 45 | 104 |

Current extractor support:

| Extractor | Current state |
|---|---|
| Text | Has an `ingredients` field and maps it to `FormulationSpec.components`, but the user prompt does not explicitly request full vehicle/excipient composition. |
| Table | Has `FormulationRow.components` and maps it to `FormulationSpec.components`; prompt asks for formulation composition tables but does not explicitly require every excipient/component row. |
| Figure | Figure records inherit `source_record.formulation`, so components can propagate from table records. VLM context currently passes label spaces and page text, not membrane/receptor/dose context. |

Conclusion: schema is sufficient for excipients/vehicle components. The next change should be prompt/schema-output alignment in text/table intermediate models, not a `FormulationSpec` schema expansion.

## 3. Target Paper Diagnosis: `10.1208/s12249-013-9995-4`

Recent runs inspected:

| Run | Target table raw outputs | Main behavior |
|---|---:|---|
| `full_run_13_post_fix5` | 4 | Mixed flux/amount extraction; F1 value/time mismatch. |
| `full_run_14_v2_policy` | 6 | Omitted F4-F8; assigned some 72 h values to wrong time labels and to N rows. |
| `experiment_E8_relaxed_scope` | 4 | Extracted flux rows instead of the cumulative amount endpoint; omitted most rows. |
| `experiment_E2_gpt54` | 14 | Extracted F1-F8 cumulative amount rows correctly at 72 h and N1-N6 composition rows without endpoints. |

### 3.1 Was Table II Fully Passed To The LLM?

Yes for `full_run_14_v2_policy`.

The selected table window was:

- source: `html/html_remote`
- locators: `Table 3`, `Table 1`, `Table 2`, `Table 4`
- content length: 3,009 chars
- input row lines: 40

The `Table 2` block included all F1-F8 rows:

| Label | Flux | 24 h | 48 h | 72 h |
|---|---:|---:|---:|---:|
| F1 | 26.0 | 298.0 | 536.5 | 1142.4 |
| F2 | 29.7 | 155.9 | 580.2 | 1178.9 |
| F3 | 19.3 | 140.2 | 543.5 | 759.6 |
| F4 | 19.3 | 132.3 | 464.8 | 734.4 |
| F5 | 14.1 | 312.3 | 542.5 | 799.5 |
| F6 | 19.8 | 148.8 | 551.2 | 808.0 |
| F7 | 12.5 | 123.9 | 260.1 | 387.9 |
| F8 | 17.7 | 132.3 | 464.8 | 734.4 |

Conclusion: F4-F8 were not lost because of Table II window truncation. They were omitted by the LLM extraction output.

### 3.2 Duplicate / Wrong-Time Source

For `full_run_14_v2_policy`, the extractor raw output was already wrong before assembly:

| Raw label | Extractor endpoint | Extractor time | Issue |
|---|---:|---:|---|
| N1 | 1142.4 µg | 72 h | Endpoint copied from F1 72 h onto an N formulation row. |
| N2 | 1178.9 µg | 72 h | Endpoint copied from F2 72 h onto an N formulation row. |
| N3 | 759.6 µg | 72 h | Endpoint copied from F3 72 h onto an N formulation row. |
| F1 | 1142.4 µg | 24 h | Endpoint value is 72 h, time says 24 h. |
| F2 | 1178.9 µg | 48 h | Endpoint value is 72 h, time says 48 h. |
| F3 | 759.6 µg | 72 h | Correct row among the extracted F rows. |

Assembly did not create these errors:

- `table_raw.jsonl`: 6 rows for this DOI.
- `table_records.jsonl`: 6 rows for this DOI.
- `assembled_records.jsonl`: 6 rows for this DOI.

Exact same-formulation / same-value / different-time duplicate groups were not found in recent inspected runs. However, `assembly._record_key()` currently includes both endpoint time and endpoint value, so if the extractor emits same-label same-value different-time rows, assembly will preserve them rather than deduplicate them.

### 3.3 Incomplete Extraction Source

Incomplete extraction is extractor-stage LLM omission, not window truncation for Table II.

Evidence:

- `full_run_14_v2_policy` Table II input contains F1-F8, but extractor returned only F1-F3.
- `experiment_E8_relaxed_scope` returned 4 rows and selected flux endpoints instead of the cumulative amount endpoint.
- `experiment_E2_gpt54` over the same selected tables returned all F1-F8 cumulative endpoint rows at 72 h, showing the input can support complete extraction.

Secondary window issue:

- HTML table parsing currently caps each table at `max_rows=18` without an explicit truncation marker.
- In this target paper, Table III is truncated at N6 because of the HTML row cap. That is not the cause of missing F4-F8 from Table II, but it can cause incomplete extraction for larger formulation/composition tables in other papers.

## 4. Other-Paper Screening

Across `full_run_14_v2_policy` table extraction:

- No exact same-label / same-endpoint-value / different-time duplicate groups were found in `table_records.jsonl` or `assembled_records.jsonl`.
- Many PDF-backed table windows show `page_text_truncated` because PDF page text is capped at 4,500 chars per selected page.
- HTML-backed windows can silently hit the 18-row-per-table cap; observed examples include `10.1208/s12249-013-9995-4` and `10.4103/jomfp.jomfp_253_19`.

Top output-count papers in `full_run_14_v2_policy`:

| DOI | Input window signal | Output records | Diagnostic note |
|---|---|---:|---|
| `10.1208/s12249-013-9995-4` | 40 input row lines, HTML row cap on one selected block | 6 | Table II complete but LLM omitted F4-F8 and mismatched time/value. |
| `10.1038/s41598-019-43082-0` | PDF page text truncated | 3 | Possible PDF page-window loss. |
| `10.1371/journal.pone.0299965` | PDF page window | 3 | No obvious row cap flag. |
| `10.1039/d0ra00100g` | PDF page text truncated | 2 | Possible PDF page-window loss. |
| `10.4103/jomfp.jomfp_253_19` | 45 input row lines, HTML row cap on one selected block | 1 | Likely risk of incomplete table coverage. |

Conclusion: the target issue is primarily LLM extraction behavior, but table-window truncation is a real broader risk, especially for large HTML tables and long PDF page text.

## 5. Proposed Fix Plan Awaiting Confirmation

Do not implement yet. Recommended sequence:

### Fix A: Prompt And Intermediate Schema Alignment

Modify `extractors/table/extractor.py`:

- Add explicit instructions: extract every relevant formulation row; do not summarize or select representative rows.
- Specify wide time-column handling: for rows with multiple endpoint time columns, produce one record per formulation per endpoint time, or if target policy wants only the final time, explicitly choose the final cumulative amount column and state that choice in `notes`.
- Prefer cumulative amount endpoint over flux/Jss when both are present for V2/E8 verified-yield experiments.
- Add explicit instructions to keep formulation/composition rows separate from endpoint rows unless a shared formulation label links them.
- Add intermediate fields for membrane/receptor/dose if table titles/footnotes contain them, then map those fields into `ConditionSpec`.

Modify `extractors/text/extract_fields.py`:

- Add intermediate output fields for `membrane_type`, `membrane_source`, `membrane_thickness_um`, `receptor_medium`, `dose_type`, and `dose_amount`.
- Explicitly request vehicle/excipient composition and evidence items for those fields.
- Map the new fields in `extractors/text/normalize_fields.py`.

Modify figure VLM context only after table/text can populate condition context:

- Pass known `membrane_type`, `receptor_medium`, and `dose_type` from source table/text records into `_build_context_packet()`.
- Let figure records continue inheriting `source_record.conditions`.

### Fix B: Table Window Safety

Modify HTML/PDF windowing conservatively:

- Raise HTML `_extract_html_rows(max_rows=18)` to a safer value, for example 60.
- Add an explicit `...[rows truncated]` marker if a table is capped.
- Consider increasing `max_chars_total` from 28,000 only if the added row cap marker still shows relevant truncation.
- For PDF pages, keep the current cap for cost control but add better truncation diagnostics into `table_raw` metadata.

### Fix C: Conservative Post-Extraction Guardrails

Add a table extractor post-processing check:

- Flag or drop exact duplicates only when `doi + formulation_label + endpoint_kind + endpoint_value + endpoint_unit` repeats with different `endpoint_time_value` and the evidence snippet does not contain a time-specific column value.
- Do not delete legitimate multi-timepoint records when endpoint values differ.
- Add a diagnostic note rather than silently mutating when confidence is low.

### Fix D: Assembly Guardrail

If post-extraction dedupe is not enough, add an assembly-level diagnostic for duplicate label/value/time conflicts. It should not change verification/policy/failure taxonomy.

## 6. Prompt Versions Affected If Approved

Expected prompt version bumps:

| Prompt asset | Current version | Expected action |
|---|---|---|
| `extractors.text.structured_fields` | `2026-03-28.v1` | bump after adding condition/excipient extraction instructions. |
| `extractors.table.structured_tables` | `2026-03-28.v1` | bump after row-completeness, time-column, and condition-context instructions. |
| `extractors.figure.vlm_digitize` | `2026-04-08.v2` | bump if VLM context starts carrying membrane/receptor/dose fields. |

`run_pipeline.py` already records prompt versions in `PROMPT_ASSETS` and stores them in manifest `stage_metrics["prompt_assets"]`, so version bumps should automatically appear in future run manifests once constants are updated.

## 7. Recommendation

Approve Fix A + Fix B first. They address the confirmed root causes: LLM omission/misalignment and silent row-window caps. Hold Fix C as a conservative safety net after rerunning the target paper, because recent runs did not show exact same-label duplicate records, only extractor-stage row omission and endpoint/time misalignment.
