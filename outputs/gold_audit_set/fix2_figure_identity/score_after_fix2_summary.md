# Round-1 Gold Audit Scoring Summary

- Total labeled rows: `71`
- Unique papers: `23`
- Predicted positives (`verified`): `7`
- Gold positives (`gold_keep_record = yes`): `14`
- Precision: `1.000`
- Recall: `0.500`
- F1: `0.667`
- Scope precision: `1.000`
- End-to-end precision: `0.000`

## By Route

| Route | Count | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| table | 18 | 0.000 | 0.000 | 0.000 |
| text | 4 | 0.000 | 0.000 | 0.000 |
| mixed | 18 | 0.000 | 0.000 | 0.000 |
| figure | 31 | 1.000 | 0.500 | 0.667 |

## Recoverable Failure Rates In Unresolved

| failure_reason | count | gold_keep=yes | recoverable_rate |
|---|---:|---:|---:|
| figure_digitization_failed | 4 | 3 | 0.750 |
| unit_normalization_failed | 5 | 3 | 0.600 |
| not_target_api_concentration | 8 | 4 | 0.500 |
| missing_endpoint | 10 | 3 | 0.300 |
| insufficient_evidence | 35 | 0 | 0.000 |
| ambiguous_api_concentration | 26 | 0 | 0.000 |
| missing_area | 6 | 0 | 0.000 |
| missing_api_concentration | 3 | 0 | 0.000 |
| missing_endpoint_time | 2 | 0 | 0.000 |
| percent_only | 1 | 0 | 0.000 |