# E3 Delta: GPT-4o-mini full_run_16 -> Claude Sonnet 4.6 same-corpus rerun

Generated: 2026-04-17

## Corpus Check

- Corpus identity confirmed: `yes`.
- GPT baseline input CSV: `['outputs\\full_run_12_full\\corpus.csv']`.
- Claude E3 v2 input CSV: `['outputs\\full_run_12_full\\corpus.csv']`.
- Both runs report corpus rows `1828` and rule-pass rows `749`; Claude E3 v2 reports corpus rows `1828` and rule-pass rows `749`.
- This report is now a same-corpus operational comparison; the main variable is provider/model (`gpt-4o-mini` vs `claude-sonnet-4-6`).

## Scope Notes

- GPT baseline: `outputs/full_run_16_post_all_fixes`, provider `openai` inferred from legacy manifest, model `gpt-4o-mini`, policy `v1_strict_ibuprofen_5pct`.
- Claude E3 v2: `outputs/experiment_E3_claude_v2`, provider `anthropic`, model `claude-sonnet-4-6`, policy `v1_strict_ibuprofen_5pct`.
- Both runs enabled `balanced_full`, LLM triage, content download, auto PDF download, figure branch, VLM, patchers, table promotion, LLM adjudication, long-run mode, and CSV export.
- Pricing assumptions: GPT-4o mini `$0.15`/`$0.60` per 1M uncached input/output tokens from OpenAI prompt-caching pricing; Claude Sonnet 4.6 `$3`/`$15` per MTok input/output from Anthropic pricing. No cache discount was applied to either run estimate.

## Overall

| Metric | GPT-4o-mini | Claude Sonnet | Delta |
| --- | --- | --- | --- |
| corpus_rows | 1828 | 1828 | 0 |
| rule_pass_rows | 749 | 749 | 0 |
| triaged_rows | 536 | 220 | -316 |
| route_decisions | 536 | 220 | -316 |
| assembled | 239 | 93 | -146 |
| verified (v1) | 1 | 0 | -1 |
| unresolved | 179 | 83 | -96 |
| rejected | 59 | 10 | -49 |
| llm_adjudication_rows | 90 | 48 | -42 |

## By Route

| Route | GPT total | GPT verified | GPT unresolved | GPT rejected | Claude total | Claude verified | Claude unresolved | Claude rejected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| figure | 73 | 1 | 49 | 23 | 30 | 0 | 30 | 0 |
| mixed | 85 | 0 | 65 | 20 | 33 | 0 | 23 | 10 |
| table | 74 | 0 | 58 | 16 | 28 | 0 | 28 | 0 |
| text | 7 | 0 | 7 | 0 | 2 | 0 | 2 | 0 |

## V2 Rescore

| Metric | GPT v1 | GPT v2 | Claude v1 | Claude v2 |
| --- | --- | --- | --- | --- |
| verified total | 1 | 25 | 0 | 24 |
| unresolved total | 179 | 155 | 83 | 59 |
| rejected total | 59 | 59 | 10 | 10 |
| table verified | 0 | 24 | 0 | 24 |
| figure verified | 1 | 1 | 0 | 0 |

## Table Extraction Comparison

| Metric | GPT-4o-mini | Claude | Delta |
| --- | --- | --- | --- |
| table records | 252 | 87 | -165 |
| table route records after final v1 verify | 74 | 28 | -46 |
| table verified after v2 rescore | 24 | 24 | 0 |

### Table Records By Paper

| DOI/paper | GPT table records | Claude table records | Delta |
| --- | --- | --- | --- |
| 10.4103/jomfp.jomfp_253_19 | 19 | 0 | -19 |
| 10.1038/s41598-024-57883-5 | 10 | 0 | -10 |
| 10.1371/journal.pone.0118536 | 10 | 0 | -10 |
| 10.1007/s11095-024-03747-6 | 9 | 0 | -9 |
| 10.1016/j.ejpb.2020.05.013 | 10 | 1 | -9 |
| 10.1186/2050-6511-13-5 | 18 | 9 | -9 |
| 10.1208/s12249-015-0474-y | 9 | 0 | -9 |
| 10.1371/journal.pone.0156931 | 9 | 0 | -9 |
| 10.3762/bjoc.9.104 | 8 | 0 | -8 |
| 10.1039/d0ra00100g | 7 | 0 | -7 |
| 10.3390/molecules28207156 | 7 | 0 | -7 |
| 10.1016/j.ijpharm.2019.118975 | 6 | 0 | -6 |
| 10.1523/jneurosci.15-04-02768.1995 | 6 | 0 | -6 |
| 10.1186/s13065-022-00901-2 | 5 | 0 | -5 |
| 10.3390/membranes13030355 | 5 | 0 | -5 |
| 10.21203/rs.3.rs-3773667/v1 | 4 | 0 | -4 |
| 10.3389/fphar.2024.1355283 | 4 | 0 | -4 |
| 10.3389/fphys.2016.00263 | 4 | 0 | -4 |
| 10.1002/14651858.cd001177.pub2 | 3 | 0 | -3 |
| 10.1016/j.jhazmat.2021.125554 | 3 | 0 | -3 |
| 10.1038/srep08114 | 3 | 0 | -3 |
| 10.1172/jci2614 | 3 | 0 | -3 |
| 10.1186/s12951-020-00718-y | 3 | 0 | -3 |
| 10.1208/s12249-019-1481-1 | 7 | 4 | -3 |
| 10.1208/s12249-019-1584-8 | 6 | 3 | -3 |
| 10.1593/neo.121890 | 3 | 0 | -3 |
| 10.1007/s11095-020-02887-9 | 2 | 0 | -2 |
| 10.1007/s43440-023-00460-w | 2 | 0 | -2 |
| 10.1038/s41598-020-74885-1 | 2 | 0 | -2 |
| 10.1248/bpb.b19-00221 | 2 | 0 | -2 |
| 10.1371/journal.pone.0130253 | 2 | 0 | -2 |
| 10.3389/fchem.2021.767923 | 2 | 0 | -2 |
| 10.1007/s13346-022-01182-x | 4 | 3 | -1 |
| 10.1021/acs.molpharmaceut.0c00720 | 4 | 3 | -1 |
| 10.1208/s12249-013-9995-4 | 24 | 24 | 0 |
| 10.18433/j3160b | 3 | 3 | 0 |
| 10.1007/s11095-008-9785-y | 5 | 6 | 1 |
| 10.1038/s41598-022-05912-6 | 0 | 1 | 1 |
| 10.1248/cpb.c21-00033 | 11 | 12 | 1 |
| 10.1016/j.ijpharm.2016.03.043 | 8 | 18 | 10 |

## Figure Pipeline Comparison

| Metric | GPT-4o-mini | Claude | Delta |
| --- | --- | --- | --- |
| figure_records | 10 | 1 | -9 |
| routed_candidates | 23 | 12 | -11 |
| after_gate | 16 | 8 | -8 |
| triage_artifacts | 14 | 7 | -7 |
| digitized_curves | 17 | 4 | -13 |
| mapped_curves | 10 | 1 | -9 |
| vlm_readings_total | 20 | 4 | -16 |
| vlm_readings_readable | 13 | 4 | -9 |
| vlm_used_as_final | 6 | 4 | -2 |
| figure verified v1 | 1 | 0 | -1 |

## New Field Fill Rate Comparison

| Field | GPT-4o-mini | Claude | Delta filled count |
| --- | --- | --- | --- |
| membrane_type | 191/239 (79.9%) | 92/93 (98.9%) | -99 |
| membrane_source | 156/239 (65.3%) | 85/93 (91.4%) | -71 |
| membrane_thickness_um | 120/239 (50.2%) | 56/93 (60.2%) | -64 |
| receptor_medium | 99/239 (41.4%) | 77/93 (82.8%) | -22 |
| dose_type | 190/239 (79.5%) | 85/93 (91.4%) | -105 |
| dose_amount | 210/239 (87.9%) | 89/93 (95.7%) | -121 |

## Failure Taxonomy Comparison

| Failure reason | GPT-4o-mini | Claude | Delta |
| --- | --- | --- | --- |
| insufficient_evidence | 122 | 16 | -106 |
| missing_api_concentration | 73 | 6 | -67 |
| ambiguous_api_concentration | 100 | 53 | -47 |
| source_context_inconsistent | 65 | 26 | -39 |
| not_target_api | 37 | 0 | -37 |
| not_target_api_concentration | 37 | 0 | -37 |
| missing_area | 37 | 3 | -34 |
| not_target_device | 27 | 0 | -27 |
| percent_only | 19 | 7 | -12 |
| missing_endpoint_time | 10 | 1 | -9 |
| unit_normalization_failed | 8 | 0 | -8 |
| missing_endpoint | 12 | 6 | -6 |
| ambiguous_mapping | 0 | 1 | 1 |
| figure_digitization_failed | 2 | 4 | 2 |
| not_target_study_type | 4 | 10 | 6 |

## LLM Reliability

| Stage | GPT requests | Claude requests | GPT final failures | Claude final failures | GPT schema failures | Claude schema failures | GPT retries | Claude retries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| detection.router | 235 | 58 | 0 | 0 | 0 | 0 | 0 | 0 |
| extractors.figure.map_curves | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| extractors.figure.triage | 14 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| extractors.figure.triage.retry | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| extractors.figure.vlm_digitize | 8 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| extractors.table | 42 | 14 | 0 | 0 | 0 | 0 | 0 | 0 |
| extractors.text | 23 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| triage.llm_triage | 749 | 746 | 0 | 3 | 0 | 18 | 0 | 15 |
| verification.llm_adjudicate | 90 | 48 | 0 | 0 | 0 | 0 | 0 | 0 |

## Cost Comparison

| Metric | GPT-4o-mini | Claude Sonnet | Delta |
| --- | --- | --- | --- |
| total requests | 1166 | 883 | -283 |
| total input tokens | 3894133 | 1762256 | -2131877 |
| total output tokens | 216169 | 312090 | 95921 |
| estimated API cost | $0.71 | $9.97 | $9.25 |
| elapsed seconds | 6476 | 7563 | 1087 |

## Key Observations

1. Same-corpus confirmation is clean: both manifests point to `outputs\full_run_12_full\corpus.csv`, with `1828` corpus rows and `749` rule-pass rows.
2. Claude remained substantially more selective upstream: LLM triage kept `220` papers vs GPT `536`, and route distribution narrowed to figure `7`, mixed `5`, table `2`, text `3` vs GPT figure `15`, mixed `9`, table `18`, text `14`.
3. Extraction volume is much lower with Claude on the same corpus: table records `87` vs `252`, text records `5` vs `10`, and figure records `1` vs `10`.
4. Under v1, Claude produced `0` verified records vs GPT `1`. Under v2 rescore, Claude recovered `24` verified records, all table-route, while GPT v2 has `25` verified records including `1` figure record.
5. Claude incurred higher estimated API cost (`$9.97` vs `$0.71`) despite fewer downstream records, mainly because Claude token prices are higher and triage consumed `973704` input / `199432` output tokens.
6. Claude LLM triage had `3` final schema-validation failures after retries; downstream stages completed without final failures.
