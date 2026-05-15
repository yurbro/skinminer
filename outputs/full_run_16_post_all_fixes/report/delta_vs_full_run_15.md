# Delta Comparison: full_run_16_post_all_fixes vs full_run_15_schema_table_fix

## Headline Metrics

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


## Status By Route

|route|status|full_run_15|full_run_16|delta|
|---|---|---|---|---|
|figure|rejected|13|23|10|
|figure|unresolved|49|49|0|
|figure|verified|9|1|-8|
|mixed|rejected|19|20|1|
|mixed|unresolved|49|65|16|
|mixed|verified|1|0|-1|
|table|rejected|29|16|-13|
|table|unresolved|60|58|-2|
|text|rejected|1|0|-1|
|text|unresolved|3|7|4|


## Figure/VLM Metrics

|run|figure_records_final|figure_verified_final|figure_unresolved_final|figure_rejected_final|vlm_readings_total|vlm_readings_readable|vlm_used_as_final|mapped_curves|unmapped_curves|
|---|---|---|---|---|---|---|---|---|---|
|full_run_15|71|9|49|13|24|18|13|9|0|
|full_run_16|73|1|49|23|20|13|6|10|7|


## Fix 3b Retry Records In full_run_16

|record_id|doi|status|formulation_label|endpoint_value|endpoint_unit|endpoint_time|endpoint_time_unit|normalized_value|normalized_unit|retry_reason|retry_candidate_page|retry_result|figure_extraction_method|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|record_e3375489a6c9|10.1016/j.ejpb.2020.05.013|verified|5% w/w Ibuprofen gel|250.0|ug/mL|720.0|min|2388.5350318471337|ug/cm^2|calibration_curve_not_target|16|recovered_digitizable|vlm_retry_cv_disagreement|

This is the expected Fix 3b retry recovery from Figure 11/page 16. The recovered endpoint is VLM-derived and differed from the earlier targeted smoke value (250 ug/mL here vs 200 ug/mL in the smoke run), so the retry mechanism works but endpoint-value precision remains VLM-sensitive.


## Source Context Guard Triggers In full_run_16

- Total records with `source_context_inconsistent`: 65

|route|status|records|
|---|---|---|
|figure|rejected|20|
|figure|unresolved|45|


## New Field Fill Rate: Final Records

|field|full_run_15_filled|full_run_16_filled|delta_filled|
|---|---|---|---|
|dose_amount|208/233|210/239|2|
|dose_type|154/233|190/239|36|
|excipient_component_present|141/233|113/239|-28|
|membrane_source|151/233|156/239|5|
|membrane_thickness_um|134/233|120/239|-14|
|membrane_type|205/233|191/239|-14|
|receptor_medium|124/233|99/239|-25|
|receptor_volume_ml|105/233|61/239|-44|


## New Field Fill Rate: Table Extractor Records

|field|full_run_15_filled|full_run_16_filled|delta_filled|
|---|---|---|---|
|dose_amount|195/220|233/252|38|
|dose_type|149/220|202/252|53|
|excipient_component_present|129/220|125/252|-4|
|membrane_source|137/220|175/252|38|
|membrane_thickness_um|118/220|143/252|25|
|membrane_type|192/220|204/252|12|
|receptor_medium|113/220|108/252|-5|
|receptor_volume_ml|0/220|0/252|0|


## Failure Taxonomy Delta

|failure_reason|full_run_15|full_run_16|delta|
|---|---|---|---|
|ambiguous_api_concentration|102|100|-2|
|figure_digitization_failed|7|2|-5|
|insufficient_evidence|140|122|-18|
|missing_api_concentration|55|73|18|
|missing_area|44|37|-7|
|missing_endpoint|20|12|-8|
|missing_endpoint_time|0|10|10|
|not_target_api|49|37|-12|
|not_target_api_concentration|44|37|-7|
|not_target_device|6|27|21|
|not_target_study_type|20|4|-16|
|percent_only|19|19|0|
|source_context_inconsistent|0|65|65|
|unit_normalization_failed|13|8|-5|


## full_run_16 Verified Records

|record_id|doi|route|label|endpoint|normalized|retry|
|---|---|---|---|---|---|---|
|record_e3375489a6c9|10.1016/j.ejpb.2020.05.013|figure|5% w/w Ibuprofen gel|250.0 ug/mL @ 720.0 min|2388.5350318471337 ug/cm^2|True|
