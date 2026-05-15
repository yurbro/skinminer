# E3 Claude v2 Rescore Summary

Input records: 72
Policy: v2_accept_wv

| Metric | v1 Claude | v2 Claude | Delta |
| --- | --- | --- | --- |
| verified | 0 | 24 | 24 |
| unresolved | 62 | 38 | -24 |
| rejected | 10 | 10 | 0 |
| table verified | 0 | 24 | 24 |

## v2 Failure Taxonomy

| Failure reason | Count |
| --- | --- |
| ambiguous_api_concentration | 25 |
| source_context_inconsistent | 24 |
| insufficient_evidence | 9 |
| not_target_study_type | 7 |
| percent_only | 7 |
| figure_digitization_failed | 6 |
| missing_endpoint | 6 |
| not_target_device | 3 |
| unit_normalization_failed | 3 |
| ambiguous_mapping | 2 |
| missing_api_concentration | 2 |
| not_target_api_concentration | 2 |
| missing_area | 1 |
