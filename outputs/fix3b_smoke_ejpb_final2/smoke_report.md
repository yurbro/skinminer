# Fix 3b calibration retry smoke test

- DOI: `10.1016/j.ejpb.2020.05.013`
- Scope: single-paper targeted smoke test; no full run.
- Input context: `outputs/full_run_15_schema_table_fix` content/route/table records.
- Output dir: `outputs/fix3b_smoke_ejpb_final2`

## Result

- Figure records produced: `1`
- Verification counts after unit fix: `{'verified': 1}`
- Final status: `verified`
- Failure reasons: `[]`
- Source-binding guard reasons: `[]`

## Recovered Record

- Record ID: `record_e3375489a6c9`
- Formulation: `5% w/w Ibuprofen Gel`
- Endpoint: `200.0 µg/mL @ 720.0 min`
- Normalized endpoint: `1910.828025477707 ug/cm^2`
- Diffusion area: `3.14 cm^2`
- Receptor volume: `30.0 mL`
- Figure extraction method: `vlm_retry_cv_disagreement`
- VLM grounding status: `source_label_space`
- CV/VLM delta: `24.618%`

## Retry Observability

- Retry triggered: `True`
- Retry reason: `calibration_curve_not_target`
- Retry source figure/page: `10` / `14`
- Retry candidate pages: `[16, 15, 17]`
- Retry selected page: `16`
- Retry result: `recovered_digitizable`

## Artifacts

- `figure_triage.jsonl`
- `figure_endpoints.jsonl`
- `figure_vlm_readings.jsonl`
- `figure_records.jsonl`
- `verified_records_after_unitfix.jsonl`
