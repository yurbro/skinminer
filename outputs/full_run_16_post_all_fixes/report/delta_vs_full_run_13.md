# Delta Comparison: full_run_16_post_all_fixes vs full_run_13_post_fix5

## Headline Metrics

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


## Status By Route

|route|status|full_run_13|full_run_16|delta|
|---|---|---|---|---|
|figure|rejected|21|23|2|
|figure|unresolved|25|49|24|
|figure|verified|4|1|-3|
|mixed|rejected|2|20|18|
|mixed|unresolved|4|65|61|
|table|rejected|4|16|12|
|table|unresolved|10|58|48|
|text|unresolved|9|7|-2|


## Figure/VLM Metrics

|run|figure_records_final|figure_verified_final|figure_unresolved_final|figure_rejected_final|vlm_readings_total|vlm_readings_readable|vlm_used_as_final|mapped_curves|unmapped_curves|
|---|---|---|---|---|---|---|---|---|---|
|full_run_13|50|4|25|21|26|21|8|12|13|
|full_run_16|73|1|49|23|20|13|6|10|7|


## New Field Fill Rate: Final Records

|field|full_run_13_filled|full_run_16_filled|delta_filled|
|---|---|---|---|
|dose_amount|0/79|210/239|210|
|dose_type|0/79|190/239|190|
|excipient_component_present|33/79|113/239|80|
|membrane_source|0/79|156/239|156|
|membrane_thickness_um|0/79|120/239|120|
|membrane_type|0/79|191/239|191|
|receptor_medium|0/79|99/239|99|
|receptor_volume_ml|28/79|61/239|33|


## New Field Fill Rate: Table Extractor Records

|field|full_run_13_filled|full_run_16_filled|delta_filled|
|---|---|---|---|
|dose_amount|0/64|233/252|233|
|dose_type|0/64|202/252|202|
|excipient_component_present|32/64|125/252|93|
|membrane_source|0/64|175/252|175|
|membrane_thickness_um|0/64|143/252|143|
|membrane_type|0/64|204/252|204|
|receptor_medium|0/64|108/252|108|
|receptor_volume_ml|0/64|0/252|0|


## Failure Taxonomy Delta

|failure_reason|full_run_13|full_run_16|delta|
|---|---|---|---|
|ambiguous_api_concentration|42|100|58|
|figure_digitization_failed|8|2|-6|
|insufficient_evidence|54|122|68|
|missing_api_concentration|1|73|72|
|missing_area|14|37|23|
|missing_endpoint|11|12|1|
|missing_endpoint_time|2|10|8|
|not_target_api|16|37|21|
|not_target_api_concentration|10|37|27|
|not_target_device|3|27|24|
|not_target_study_type|12|4|-8|
|percent_only|6|19|13|
|source_context_inconsistent|0|65|65|
|unit_normalization_failed|3|8|5|


## full_run_16 Verified Records

|record_id|doi|route|label|endpoint|normalized|retry|
|---|---|---|---|---|---|---|
|record_e3375489a6c9|10.1016/j.ejpb.2020.05.013|figure|5% w/w Ibuprofen gel|250.0 ug/mL @ 720.0 min|2388.5350318471337 ug/cm^2|True|

Note: this verified record is the Fix 3b calibration-gate retry recovery. Its endpoint value is VLM-derived and should be treated as precision-risk until figure value extraction is stabilized.
