# Round-1 Gold Audit Scoring Summary

- Total labeled rows: `71`
- Unique papers: `23`
- Predicted positives (`verified`): `2`
- Gold positives (`gold_keep_record = yes`): `14`
- Precision: `1.000`
- Recall: `0.143`
- F1: `0.250`
- Scope precision: `1.000`
- End-to-end precision: `0.000`

## By Route

| Route | Count | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| table | 18 | 0.000 | 0.000 | 0.000 |
| text | 5 | 0.000 | 0.000 | 0.000 |
| mixed | 17 | 0.000 | 0.000 | 0.000 |
| figure | 31 | 1.000 | 0.143 | 0.250 |

## Recoverable Failure Rates In Unresolved

| failure_reason | count | gold_keep=yes | recoverable_rate |
|---|---:|---:|---:|
| missing_prediction | 61 | 12 | 0.197 |
| missing_api_concentration | 4 | 0 | 0.000 |
| insufficient_evidence | 2 | 0 | 0.000 |
| percent_only | 1 | 0 | 0.000 |