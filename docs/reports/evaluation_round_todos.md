# Future Evaluation Round TODOs

Round 2 makes the framework easier to benchmark, but it does not yet implement a full evaluation suite.

## Ready Now

- `Record.route_confidence`
- `Record.extractor_confidence`
- `Record.mapping_confidence`
- `Record.verification_support_rate`
- `Record.failure_reasons`
- `Record.provenance`
- `Record.patches`
- run-level route, verification, failure, and patch counts in the generated report
- per-module malformed-output / retry tracking in long-run summaries and reports
- blockage summaries for access, unresolved routing, extractor source errors, and patch outcomes
- versioned query profiles and prompt assets recorded in the manifest and report
- evaluation scaffolding under `evaluation/`, including fixture and gold-label templates
- typed gold-label validation via `evaluation.validate_gold_labels`
- lightweight run-vs-gold scoring via `evaluation.score_run`

## Next Evaluation Round

- Compare route decisions and extractor outcomes across model variants.
- Add record-level gold labels for endpoint value, endpoint time, device, barrier, and API concentration.
- Evaluate patcher precision versus recall by failure bucket.
- Add benchmark fixtures for text-only, table-only, figure-only, and mixed-route papers.
- Measure agreement between direct extraction and patched extraction.
- Add replay checks for figure overlays and curve-to-formulation mappings.
- Add automated schema validation and scoring against `evaluation/gold_labels.schema.json`.
