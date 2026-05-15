# V2 Gold Audit Scoring Summary

Status: provisional. Existing 71-row gold labels are post-Fix-5 / V1-scope labels; V2 w/v policy gains require supplemental annotation before final precision can be computed.

- Existing labeled rows: `71`
- Existing gold positives: `14`
- Existing-label predicted positives: `7`
- Existing-label precision: `1.000`
- Existing-label recall: `0.500`
- Existing-label F1: `0.667`
- Existing-label scope precision: `1.000`
- Existing-label end-to-end precision: `0.000`

## V2 Coverage

- V2 full-run verified total: `10`
- V2 verified by route: `{'figure': 4, 'table': 6}`
- New verified vs full_run_13 by record_id: `8`
- Policy-relevant table w/v gains: `6`
- New verified in existing gold by record_id: `3`
- New verified absent from existing gold by record_id: `5`
- Supplemental candidates file: `outputs\full_run_14_v2_policy\gold_evaluation\v2_supplemental_annotation_candidates.csv`

## Diagnostic Only

Strict record-id projection onto old labels is not a valid V2 policy score because old labels do not encode the new w/v acceptance criterion and several record contents changed between runs.

- Diagnostic precision: `0.400`
- Diagnostic recall: `0.143`
- Diagnostic F1: `0.211`
