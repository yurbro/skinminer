# Claude Per-Policy Precision

- Annotation workbook: `outputs\claude_gold_audit\claude_annotation_packet.xlsx`
- Combined labels: `outputs/claude_gold_audit/claude_precision_combined_labels.csv`

| policy   |   verified |   tp |   fp |   uncertain |   precision_pct |   inherited_labels |   new_annotations |
|:---------|-----------:|-----:|-----:|------------:|----------------:|-------------------:|------------------:|
| v2       |         24 |   24 |    0 |           0 |           100.0 |                 24 |                 0 |
| v3       |         38 |   24 |   14 |           0 |            63.2 |                 24 |                14 |
| v4       |         47 |   28 |   19 |           0 |            59.6 |                 25 |                22 |

Precision is calculated as `TP / verified` for each policy bucket; uncertain labels are counted separately and remain in the denominator.