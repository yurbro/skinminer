# E3 Delta: GPT-4o-mini (full_run_16) -> Claude Sonnet 4.6 (E3)

Generated: 2026-04-16

## Scope Notes

- GPT baseline: `outputs/full_run_16_post_all_fixes`, model `gpt-4o-mini`, provider inferred as OpenAI, input path `['outputs\\full_run_12_full\\corpus.csv']`.
- Claude E3: `outputs/experiment_E3_claude`, model `claude-sonnet-4-6`, provider `anthropic`, input path `['data\\corpus_ibuprofen.csv']`.
- The two runs are not corpus-identical: baseline has 1828 corpus rows; E3 has 1769 corpus rows. Interpret deltas as cross-run operational deltas, not a controlled same-corpus ablation.
- Claude actual cost below is aggregated from `long_run/events.jsonl` and includes the interrupted first table attempt during integration. Effective final-resume usage after routing is lower: 179612 input / 70243 output tokens, about `$1.59` excluding the already-incurred first run.
- Pricing assumptions: GPT-4o mini `$0.15`/`$0.6` per 1M input/output tokens from https://platform.openai.com/docs/pricing/; Claude Sonnet 4.6 `$3.0`/`$15.0` per MTok input/output from https://platform.claude.com/docs/en/about-claude/pricing.

## Overall

| Metric | GPT-4o-mini | Claude Sonnet | Delta |
| --- | --- | --- | --- |
| corpus_rows | 1828 | 1769 | -59 |
| rule_pass_rows | 749 | 729 | -20 |
| triaged_rows | 536 | 216 | -320 |
| route_decisions | 536 | 216 | -320 |
| assembled | 239 | 72 | -167 |
| verified (v1) | 1 | 0 | -1 |
| unresolved | 179 | 62 | -117 |
| rejected | 59 | 10 | -49 |

## By Route

| Route | GPT total | GPT verified | GPT unresolved | GPT rejected | Claude total | Claude verified | Claude unresolved | Claude rejected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| figure | 73 | 1 | 49 | 23 | 32 | 0 | 29 | 3 |
| mixed | 85 | 0 | 65 | 20 | 12 | 0 | 5 | 7 |
| table | 74 | 0 | 58 | 16 | 28 | 0 | 28 | 0 |
| text | 7 | 0 | 7 | 0 | 0 | 0 | 0 | 0 |

## Table Extraction Comparison

| Metric | GPT-4o-mini | Claude | Delta |
| --- | --- | --- | --- |
| table records | 252 | 77 | -175 |
| table verified (v2 rescore) | 24 | 24 | 0 |
| table route records after final v1 verify | 74 | 28 | -46 |

### Table Records By Paper

| DOI/paper | GPT table records | Claude table records | Delta |
| --- | --- | --- | --- |
| 10.4103/jomfp.jomfp_253_19 | 19 | 0 | -19 |
| 10.1186/2050-6511-13-5 | 18 | 3 | -15 |
| 10.1016/j.ejpb.2020.05.013 | 10 | 0 | -10 |
| 10.1038/s41598-024-57883-5 | 10 | 0 | -10 |
| 10.1371/journal.pone.0118536 | 10 | 0 | -10 |
| 10.1007/s11095-024-03747-6 | 9 | 0 | -9 |
| 10.1208/s12249-015-0474-y | 9 | 0 | -9 |
| 10.1371/journal.pone.0156931 | 9 | 0 | -9 |
| 10.1016/j.ijpharm.2016.03.043 | 8 | 16 | 8 |
| 10.3762/bjoc.9.104 | 8 | 0 | -8 |
| 10.1039/d0ra00100g | 7 | 0 | -7 |
| 10.3390/molecules28207156 | 7 | 0 | -7 |
| 10.1016/j.ijpharm.2019.118975 | 6 | 0 | -6 |
| 10.1523/jneurosci.15-04-02768.1995 | 6 | 0 | -6 |
| 10.1186/s13065-022-00901-2 | 5 | 0 | -5 |
| 10.3390/membranes13030355 | 5 | 0 | -5 |
| 10.1007/s13346-022-01182-x | 4 | 0 | -4 |
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
| 10.1007/s43440-023-00460-w | 2 | 0 | -2 |
| 10.1038/s41598-020-74885-1 | 2 | 0 | -2 |
| 10.1248/bpb.b19-00221 | 2 | 0 | -2 |
| 10.1371/journal.pone.0130253 | 2 | 0 | -2 |
| 10.3389/fchem.2021.767923 | 2 | 0 | -2 |
| 10.1007/s11095-008-9785-y | 5 | 6 | 1 |
| 10.1021/acs.molpharmaceut.0c00720 | 4 | 3 | -1 |
| 10.1038/s41598-022-05912-6 | 0 | 1 | 1 |
| 10.1248/cpb.c21-00033 | 11 | 12 | 1 |
| 10.1007/s11095-020-02887-9 | 2 | 2 | 0 |
| 10.1208/s12249-013-9995-4 | 24 | 24 | 0 |
| 10.18433/j3160b | 3 | 3 | 0 |

## Figure Pipeline Comparison

| Metric | GPT-4o-mini | Claude | Delta |
| --- | --- | --- | --- |
| figure_records | 10 | 2 | -8 |
| vlm_readings_readable | 13 | 4 | -9 |
| vlm_used_as_final | 6 | 0 | -6 |
| figure_verified | 1 | 0 | -1 |
| fix3b_retry_triggered | 1 | 0 | -1 |

## New Field Fill Rate Comparison

| Field | GPT-4o-mini | Claude | Delta filled count |
| --- | --- | --- | --- |
| membrane_type | 191/239 (79.9%) | 72/72 (100.0%) | -119 |
| membrane_source | 156/239 (65.3%) | 69/72 (95.8%) | -87 |
| membrane_thickness_um | 120/239 (50.2%) | 36/72 (50.0%) | -84 |
| receptor_medium | 99/239 (41.4%) | 55/72 (76.4%) | -44 |
| dose_type | 190/239 (79.5%) | 53/72 (73.6%) | -137 |
| dose_amount | 210/239 (87.9%) | 69/72 (95.8%) | -141 |

## Failure Taxonomy Comparison

| Failure reason | GPT-4o-mini | Claude | Delta |
| --- | --- | --- | --- |
| insufficient_evidence | 122 | 9 | -113 |
| missing_api_concentration | 73 | 2 | -71 |
| ambiguous_api_concentration | 100 | 49 | -51 |
| source_context_inconsistent | 65 | 24 | -41 |
| not_target_api | 37 | 0 | -37 |
| missing_area | 37 | 1 | -36 |
| not_target_api_concentration | 37 | 2 | -35 |
| not_target_device | 27 | 3 | -24 |
| percent_only | 19 | 7 | -12 |
| missing_endpoint_time | 10 | 0 | -10 |
| missing_endpoint | 12 | 6 | -6 |
| unit_normalization_failed | 8 | 3 | -5 |
| figure_digitization_failed | 2 | 6 | 4 |
| not_target_study_type | 4 | 7 | 3 |
| ambiguous_mapping | 0 | 2 | 2 |

## Cost Comparison

| Metric | GPT-4o-mini | Claude actual incurred | Delta |
| --- | --- | --- | --- |
| total requests | 1166 | 817 | -349 |
| total input tokens | 3894133 | 1366420 | -2527713 |
| total output tokens | 216169 | 302527 | 86358 |
| estimated API cost | $0.71 | $8.64 | $7.92 |
| elapsed seconds | 6476 | events span includes 2 runs | n/a |

## Key Observations

1. Claude produced substantially fewer final records (`72` vs `239`) and no strict verified records under v1 (`0` vs `1`). The largest driver is upstream routing/triage narrowing: E3 kept `216` papers after LLM triage vs baseline `536`, and routed only `15` non-unresolved papers vs baseline `56`.
2. Claude table extraction is much smaller (`77` vs `252` records), despite correctly extracting the known 24-row nanosuspension smoke paper. This suggests the provider difference is dominated by paper triage/routing selectivity, not just per-table row omission.
3. Claude figure pipeline was much less active: `2` figure records vs `10`; no Fix 3b retry triggered in E3. VLM produced `4` readable readings and `0` used-as-final readings, compared with baseline `13` readable and `6` used-as-final.
4. Under v1, Claude produced no verified records. Under v2 rescore, Claude recovered `24` verified table records by accepting the broader w/v concentration basis.
5. Actual incurred Claude API cost was about `$8.64` vs GPT baseline about `$0.71`. This includes duplicated table work from the integration retry; even excluding that failed first run, Claude's effective post-resume token cost is about `$1.59` for only the resumed portion captured in the final summary.
