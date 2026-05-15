# SD Outlier Diagnostic

## Record

- `record_id`: `record_073219db157b`
- Paper: `10.1159/000231528`
- Source table: `Table 3`
- Vehicle composition: `50:25:25:0:0`

## Values

- Extracted `J_sd`: `4.1`
- Reference `J_sd`: `84.1`
- `SD_relative_error_pct`: `-95.12`
- `J_within_2pct`: `True`
- `J_relative_error_pct`: `0.01`

## Diagnosis

The flux mean is accurate while the SD is not: `J_mean` is within tolerance, but the extracted SD is `4.1` instead of the reference `84.1`. This indicates an isolated SD-number extraction issue, not a systematic extraction bias affecting the full record.
