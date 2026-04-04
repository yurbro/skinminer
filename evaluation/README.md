# Evaluation Fixtures And Gold Labels

This directory stores reproducible evaluation assets for later benchmarking rounds.

Current scope:

- no fixed benchmark split yet
- lightweight validation and scoring utilities now exist
- fixture and gold-label templates are available

Recommended layout:

- `fixtures/`
  - source fixture bundles grouped by modality
- `templates/fixture_manifest_template.json`
  - template manifest describing fixture membership and scope
- `templates/gold_labels_template.jsonl`
  - record-level gold label template in JSONL form
- `gold_labels.schema.json`
  - JSON Schema for future validation of gold label files

Suggested fixture buckets:

- `text_only`
- `table_only`
- `figure_only`
- `mixed`

Suggested annotation targets:

- route
- study type
- device
- barrier
- API concentration
- endpoint value
- endpoint time
- area
- verification outcome

CLI utilities:

- `python -m evaluation.validate_gold_labels --gold-jsonl <path>`
- `python -m evaluation.score_run --gold-jsonl <gold.jsonl> --predicted-jsonl <records.jsonl> --output-json <summary.json>`

Important:

- Keep gold labels separate from pipeline outputs.
- Prefer stable fixture IDs rather than run-specific paths.
- Store enough source provenance to replay disagreements.
