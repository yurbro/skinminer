# Gold Set Round 2 Sampling Design

Date: 2026-04-17

## Inputs

- GPT v4 records: `outputs/full_run_16_post_all_fixes/v4_rescore/verified_records.jsonl`
- Claude v4 records: `outputs/experiment_E3_claude_v2/v4_rescore/verified_records.jsonl`
- No new LLM extraction was run. No baseline products were modified.

## Tier Counts

| Tier | Definition | Count |
| --- | --- | --- |
| Tier 1 | All GPT v4 verified records | 51 |
| Tier 2 | GPT v4 unresolved stratified sample | 44 |
| Tier 3 | GPT v4 rejected stratified sample | 12 |
| Tier 4 | Claude v4 verified records absent from GPT v4 verified by DOI + formulation label | 23 |
| Total | All annotation rows | 130 |

## Tier 2 Distribution

Tier 2 samples prioritize records closest to verification: fewer failure reasons first, then higher verification support rate. Small strata are fully included; large strata are sampled to maintain route coverage.

| Failure reason | Sample count |
| --- | --- |
| insufficient_evidence | 27 |
| source_context_inconsistent | 14 |
| missing_endpoint | 3 |

| Route | Sample count |
| --- | --- |
| figure | 18 |
| mixed | 13 |
| table | 12 |
| text | 1 |

| Failure reason | Route | Sample count |
| --- | --- | --- |
| source_context_inconsistent | figure | 14 |
| insufficient_evidence | mixed | 13 |
| insufficient_evidence | table | 12 |
| insufficient_evidence | figure | 2 |
| missing_endpoint | figure | 2 |
| missing_endpoint | text | 1 |

## Tier 3 Distribution

| Failure reason | Sample count |
| --- | --- |
| not_target_api | 5 |
| source_context_inconsistent | 4 |
| not_target_device | 3 |

## Tier 4 Claude-Only Verified

- Claude v4 verified records: `47`
- GPT v4 verified DOI + formulation keys: `30`
- Claude-only verified included: `23`

| DOI | Claude-only verified count |
| --- | --- |
| 10.1248/cpb.c21-00033 | 14 |
| 10.1186/2050-6511-13-5 | 9 |

## Overall Coverage

- Total annotation records: `130`
- Distinct papers: `29`
- Record cards: `130`
- Paper groups in packet: `29`

| Route | Count |
| --- | --- |
| mixed | 50 |
| table | 49 |
| figure | 24 |
| text | 7 |

## Outputs

- `gold_set_round2_design.md`: this sampling design
- `gold_set_round2_annotation.csv`: annotation CSV with blank `gold_*` columns
- `gold_set_round2_packet.md`: paper-grouped annotation packet
- `gold_set_round2_record_cards/`: one markdown card per sampled record
