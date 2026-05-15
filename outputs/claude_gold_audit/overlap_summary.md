# Claude Gold Audit: Overlap Summary

## Policy Buckets

| Policy   |   Claude verified |   Inheritable from GPT gold |   Need new annotation |
|:---------|------------------:|----------------------------:|----------------------:|
| v2       |                24 |                          24 |                     0 |
| v3       |                38 |                          24 |                    14 |
| v4       |                47 |                          25 |                    22 |

## New Annotation Effort

- Unique Claude records requiring new annotation: 22
- Estimated effort at 3-5 minutes per record: 66-110 minutes (1.1-1.8 hours)

## Match Reason Counts

- `doi_formulation_time_value_match`: 25
- `no_gpt_record_same_doi`: 14
- `same_doi_no_formulation_match`: 6
- `same_doi_formulation_time_no_value_match`: 2

## Outputs

- `outputs/claude_gold_audit/overlap_analysis.csv`
- `outputs/claude_gold_audit/claude_annotation_packet.xlsx`

Phase 3/4 are intentionally not run until `claude_annotation_packet_FILLED.xlsx` is available.