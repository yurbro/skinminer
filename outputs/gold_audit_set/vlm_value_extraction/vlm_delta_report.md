# VLM Value Extraction Delta Report

## Scope

This run introduced the first parallel VLM value path for locked-subplot direct figure rows only.

- VLM path is enabled only after subplot lock succeeds.
- Input context includes crop width/height and source render DPI when available from the existing PDF render path.
- Reconciliation is conservative: CV/VLM disagreement does not auto-promote a direct figure row.

Validation run: [validation_observability_run_vlm1](c:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\validation_observability_run_vlm1)

## Metric Delta vs Fix 4

| Metric | Fix 4 | VLM v1 | Delta |
|---|---:|---:|---:|
| precision | 1.000 | 1.000 | +0.000 |
| recall | 0.500 | 0.500 | +0.000 |
| F1 | 0.667 | 0.667 | +0.000 |
| scope precision | 1.000 | 1.000 | +0.000 |
| end-to-end precision | 0.000 | 0.000 | +0.000 |
| verified count | 7 | 7 | +0 |

## Validation Run Observability

- VLM readings total: `11`
- VLM readings readable: `10`
- VLM used as final: `0`
- VLM reconciliation statuses: `{"cv_only": 9, "cv_vlm_disagreement": 1, "unreadable": 1}`

## Interpretation

- The VLM path is live and producing structured reading artifacts.
- Prompt/version tracking is live in manifest/report under `extractors.figure.vlm_digitize`.
- Crop resolution and source render DPI are now included in the VLM context packet.
- On this validation subset, `vlm_used_as_final = 0`, so the new path did not yet change the accepted direct-figure rows.
- The unchanged gold metrics indicate that the current first-pass VLM reader is still blocked by label grounding and conservative reconciliation rather than by wiring failures.
- Concretely, most readable VLM rows stayed in `cv_only` because their legend labels did not ground to the formulation label space used downstream; one readable row hit `cv_vlm_disagreement`; one row remained unreadable.

## Conclusion

The first VLM implementation is structurally correct but evaluation-neutral on the current gold audit subset. The next improvement should target label grounding / legend-to-formulation alignment and the reconciliation gate, not more basic VLM plumbing.
