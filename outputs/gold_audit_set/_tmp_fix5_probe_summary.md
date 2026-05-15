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
| text | 7 | 0.000 | 0.000 | 0.000 |
| mixed | 18 | 0.000 | 0.000 | 0.000 |
| figure | 28 | 1.000 | 0.636 | 0.778 |

## Recoverable Failure Rates In Unresolved

| failure_reason | count | gold_keep=yes | recoverable_rate |
|---|---:|---:|---:|
| not_target_api_concentration | 8 | 4 | 0.500 |
| insufficient_evidence | 54 | 3 | 0.056 |
| missing_api_concentration | 16 | 0 | 0.000 |
| ambiguous_api_concentration | 12 | 0 | 0.000 |
| missing_area | 6 | 0 | 0.000 |
| missing_endpoint | 6 | 0 | 0.000 |
| percent_only | 3 | 0 | 0.000 |
| unit_normalization_failed | 2 | 0 | 0.000 |
| missing_endpoint_time | 2 | 0 | 0.000 |