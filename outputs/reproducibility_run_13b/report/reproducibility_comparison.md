# Reproducibility: full_run_13 vs 13b

Run 13b uses the same corpus CSV, V1 policy, model family, figure VLM setting, patching, table promotion, long-run mode, CSV export, and LLM adjudication flags as full_run_13. The current codebase includes later no-op-by-default policy/ablation controls, so this is best read as same runtime configuration under the current framework version.

## Overall

| Metric | Run 13 | Run 13b | Delta |
|---|---:|---:|---:|
| assembled | 79 | 90 | +11 |
| verified | 4 | 2 | -2 |
| unresolved | 48 | 65 | +17 |
| rejected | 27 | 23 | -4 |

## Record-Level Agreement

| ?? | ? |
|---|---:|
| ??? verified ? record ? | 0 |
| Run 13 verified ? 13b ??? | 4 |
| Run 13b verified ? 13 ??? | 2 |
| Record-level agreement rate | 0.000 |
| Semantic verified agreement rate | 0.000 |

## Route-Level Stability

| Route | Run 13 verified | Run 13b verified | Agreement |
|---|---:|---:|---:|
| table | 0 | 0 | 1.000 |
| text | 0 | 0 | 1.000 |
| mixed | 0 | 0 | 1.000 |
| figure | 4 | 2 | 0.500 |

## Failure Taxonomy Stability

| failure_reason | Run 13 | Run 13b | Delta | Relative delta |
|---|---:|---:|---:|---:|
| missing_api_concentration | 1 | 6 | +5 | +500.0% |
| missing_endpoint_time | 2 | 0 | -2 | -100.0% |
| figure_digitization_failed | 8 | 3 | -5 | -62.5% |
| missing_endpoint | 11 | 7 | -4 | -36.4% |
| missing_area | 14 | 19 | +5 | +35.7% |
| insufficient_evidence | 54 | 73 | +19 | +35.2% |

## Cost

| Metric | Run 13 | Run 13b | Delta |
|---|---:|---:|---:|
| total tokens | 3838632 | 3907396 | +68764 |
| elapsed seconds | 5003.045 | 5724.300 | +721.255 |

## Key Observation

The run is not record-stable: verified count changed from 4 to 2 and no verified record IDs overlapped. Route-level outcome remains figure-only, but LLM triage/routing/extraction variability is material enough that paper-level conclusions should rely on aggregate comparisons and fixed artifacts/replays when isolating a single module change.
