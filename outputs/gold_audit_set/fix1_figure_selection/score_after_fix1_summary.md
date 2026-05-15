# Round-1 Gold Audit Scoring Summary

- Total labeled rows: `71`
- Unique papers: `23`
- Predicted positives (`verified`): `10`
- Gold positives (`gold_keep_record = yes`): `14`
- Precision: `1.000`
- Recall: `0.714`
- F1: `0.833`
- Scope precision: `1.000`
- End-to-end precision: `0.200`

## By Route

| Route | Count | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| table | 18 | 0.000 | 0.000 | 0.000 |
| text | 4 | 0.000 | 0.000 | 0.000 |
| mixed | 18 | 0.000 | 0.000 | 0.000 |
| figure | 31 | 1.000 | 0.714 | 0.833 |

## Recoverable Failure Rates In Unresolved

| failure_reason | count | gold_keep=yes | recoverable_rate |
|---|---:|---:|---:|
| not_target_api_concentration | 8 | 4 | 0.500 |
| insufficient_evidence | 35 | 0 | 0.000 |
| ambiguous_api_concentration | 26 | 0 | 0.000 |
| missing_endpoint | 7 | 0 | 0.000 |
| missing_area | 6 | 0 | 0.000 |
| missing_api_concentration | 3 | 0 | 0.000 |
| unit_normalization_failed | 2 | 0 | 0.000 |
| missing_endpoint_time | 2 | 0 | 0.000 |
| figure_digitization_failed | 1 | 0 | 0.000 |
| percent_only | 1 | 0 | 0.000 |