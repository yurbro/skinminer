# Full Run 16 Post-All-Fixes Summary

Configuration: same corpus as full_run_13, all stages `gpt-4o-mini`, `balanced_full`, policy `v1`, figure + VLM + patchers + adjudication + long-run mode enabled.

## Core Outputs

|metric|full_run_13|full_run_16|delta|
|---|---|---|---|
|corpus_rows|1828|1828|0|
|triaged_rows|529|536|7|
|route_decisions|529|536|7|
|table_records|64|252|188|
|text_records|11|10|-1|
|figure_records|9|10|1|
|assembled_records|79|239|160|
|verified|4|1|-3|
|unresolved|48|179|131|
|rejected|27|59|32|
|patch_count|220|572|352|
|llm_adjudication_rows|33|90|57|


## Compared With full_run_15

|metric|full_run_15|full_run_16|delta|
|---|---|---|---|
|corpus_rows|1828|1828|0|
|triaged_rows|531|536|5|
|route_decisions|531|536|5|
|table_records|220|252|32|
|text_records|11|10|-1|
|figure_records|16|10|-6|
|assembled_records|233|239|6|
|verified|10|1|-9|
|unresolved|161|179|18|
|rejected|62|59|-3|
|patch_count|593|572|-21|
|llm_adjudication_rows|96|90|-6|


## Verified Records In full_run_16

|record_id|doi|route|label|endpoint|normalized|retry|
|---|---|---|---|---|---|---|
|record_e3375489a6c9|10.1016/j.ejpb.2020.05.013|figure|5% w/w Ibuprofen gel|250.0 ug/mL @ 720.0 min|2388.5350318471337 ug/cm^2|True|

Note: this is the Fix 3b calibration-gate retry recovery from Figure 11/page 16. The same paper's earlier targeted smoke test read 200 ug/mL at the same time point, while this full run read 250 ug/mL, so the VLM endpoint value still shows run-to-run variability.


## V2 Rescore Headline

|policy|verified|unresolved|rejected|
|---|---|---|---|
|v1_full_run_16|1|179|59|
|v2_rescore|25|155|59|


## Report Files

- `run_report.md`: complete pipeline run report.

- `delta_vs_full_run_15.md`: delta from schema/table-fix full run.

- `delta_vs_full_run_13.md`: cumulative delta from post-Fix-5 baseline.

- `../v2_rescore/v2_rescore_summary.md`: v2 policy rescore.
