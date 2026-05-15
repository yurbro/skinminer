# Full Run 15 Comparison vs Full Run 14 and V2 Rescore

`full_run_14_v2_policy` used the earlier extraction code with v2 concentration policy. `full_run_15_schema_table_fix_v1` uses the schema/table fix under v1. `full_run_15_schema_table_fix_v2_rescore` re-verifies full_run15 post-patcher records under v2 without re-running model extraction.

## Headline Metrics

| run | table_records | text_records | figure_records | assembled | verified | unresolved | rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full_run_14_v2_policy | 60 | 13 | 7 | 75 | 10 | 43 | 22 |
| full_run_15_schema_table_fix_v1 | 220 | 11 | 16 | 233 | 10 | 161 | 62 |
| full_run_15_schema_table_fix_v2_rescore | 220 | 11 | 16 | 233 | 34 | 137 | 62 |

Compared with full_run14 v2, full_run15 v2-rescore changes are: assembled +158, verified +24, unresolved +94, rejected +40.

Within full_run15, switching only v1 -> v2 changes statuses as:

| transition | count |
| --- | --- |
| rejected->rejected | 62 |
| unresolved->unresolved | 137 |
| unresolved->verified | 24 |
| verified->verified | 10 |


Transition detail CSV: `outputs\full_run_15_schema_table_fix\v2_rescore\v1_to_v2_status_transitions.csv`.

Route-level final status:

| run | route | verified | unresolved | rejected |
| --- | --- | ---: | ---: | ---: |
| full_run_14_v2_policy | figure | 4 | 12 | 13 |
| full_run_14_v2_policy | mixed | 0 | 22 | 5 |
| full_run_14_v2_policy | table | 6 | 8 | 4 |
| full_run_14_v2_policy | text | 0 | 1 | 0 |
| full_run_15_schema_table_fix_v1 | figure | 9 | 49 | 13 |
| full_run_15_schema_table_fix_v1 | mixed | 1 | 49 | 19 |
| full_run_15_schema_table_fix_v1 | table | 0 | 60 | 29 |
| full_run_15_schema_table_fix_v1 | text | 0 | 3 | 1 |
| full_run_15_schema_table_fix_v2_rescore | figure | 9 | 49 | 13 |
| full_run_15_schema_table_fix_v2_rescore | mixed | 1 | 49 | 19 |
| full_run_15_schema_table_fix_v2_rescore | table | 24 | 36 | 29 |
| full_run_15_schema_table_fix_v2_rescore | text | 0 | 3 | 1 |

## Table Route Completeness vs Full Run 14

Table records increased from 60 to 220 (+160). Largest DOI-level increases:

| doi_or_paper_id | full_run_14_table_records | full_run_15_table_records | delta_15_vs_14 |
| --- | --- | --- | --- |
| 10.1208/s12249-013-9995-4 | 6 | 24 | 18 |
| 10.4103/jomfp.jomfp_253_19 | 1 | 19 | 18 |
| 10.1248/cpb.c21-00033 | 1 | 11 | 10 |
| 10.1038/s41598-024-57883-5 | 2 | 10 | 8 |
| 10.1007/s13346-022-01182-x | 2 | 9 | 7 |
| 10.1208/s12249-015-0474-y | 1 | 8 | 7 |
| 10.3762/bjoc.9.104 | 1 | 8 | 7 |
| 10.1371/journal.pone.0156931 | 0 | 7 | 7 |
| 10.1016/j.ijpharm.2016.03.043 | 2 | 8 | 6 |
| 10.1016/j.ejpb.2020.05.013 | 1 | 7 | 6 |
| 10.1038/srep08114 | 0 | 6 | 6 |
| 10.1042/bj2700039 | 0 | 6 | 6 |
| 10.3390/membranes12080762 | 0 | 6 | 6 |
| 10.3390/pharmaceutics16111465 | 0 | 6 | 6 |
| 10.1039/d0ra00100g | 2 | 7 | 5 |


## New Field Fill Rates After Schema/Table Fix

Full_run15 assembled records:

| field | filled/total | rate |
| --- | --- | --- |
| membrane_type | 205/233 | 88.0% |
| membrane_source | 151/233 | 64.8% |
| membrane_thickness_um | 134/233 | 57.5% |
| receptor_medium | 124/233 | 53.2% |
| dose_type | 154/233 | 66.1% |
| dose_amount | 208/233 | 89.3% |


Full_run15 v2-rescore verified-only records:

| field | filled/total | rate |
| --- | --- | --- |
| membrane_type | 34/34 | 100.0% |
| membrane_source | 34/34 | 100.0% |
| membrane_thickness_um | 10/34 | 29.4% |
| receptor_medium | 25/34 | 73.5% |
| dose_type | 34/34 | 100.0% |
| dose_amount | 34/34 | 100.0% |


## Failure Taxonomy Shift

Top absolute taxonomy shifts for full_run15 v2-rescore vs full_run14 v2:

| failure_reason | full_run_13_post_fix5_v1 | full_run_14_v2_policy | full_run_15_schema_table_fix_v1 | full_run_15_schema_table_fix_v2_rescore | delta_15_v2_rescore_vs_14 |
| --- | --- | --- | --- | --- | --- |
| insufficient_evidence | 54 | 54 | 140 | 140 | 86 |
| missing_api_concentration | 1 | 1 | 55 | 55 | 54 |
| ambiguous_api_concentration | 42 | 26 | 102 | 78 | 52 |
| not_target_api | 16 | 11 | 49 | 49 | 38 |
| not_target_api_concentration | 10 | 10 | 44 | 44 | 34 |
| missing_area | 14 | 17 | 44 | 44 | 27 |
| percent_only | 6 | 2 | 19 | 19 | 17 |
| unit_normalization_failed | 3 | 1 | 13 | 13 | 12 |
| missing_endpoint | 11 | 9 | 20 | 20 | 11 |
| not_target_study_type | 12 | 9 | 20 | 20 | 11 |
| figure_digitization_failed | 8 | 5 | 7 | 7 | 2 |
| not_target_device | 3 | 5 | 6 | 6 | 1 |


Top policy-only shifts within full_run15 (v2-rescore minus v1):

| failure_reason | full_run_13_post_fix5_v1 | full_run_14_v2_policy | full_run_15_schema_table_fix_v1 | full_run_15_schema_table_fix_v2_rescore | delta_15_v2_rescore_vs_15_v1 |
| --- | --- | --- | --- | --- | --- |
| ambiguous_api_concentration | 42 | 26 | 102 | 78 | -24 |
| figure_digitization_failed | 8 | 5 | 7 | 7 | 0 |
| insufficient_evidence | 54 | 54 | 140 | 140 | 0 |
| missing_api_concentration | 1 | 1 | 55 | 55 | 0 |
| missing_area | 14 | 17 | 44 | 44 | 0 |
| missing_endpoint | 11 | 9 | 20 | 20 | 0 |
| missing_endpoint_time | 2 | 0 | 0 | 0 | 0 |
| not_target_api | 16 | 11 | 49 | 49 | 0 |
| not_target_api_concentration | 10 | 10 | 44 | 44 | 0 |
| not_target_device | 3 | 5 | 6 | 6 | 0 |
| not_target_study_type | 12 | 9 | 20 | 20 | 0 |
| percent_only | 6 | 2 | 19 | 19 | 0 |


Interpretation: v2 policy removes the concentration-basis blocker for many of the newly extracted table rows. The schema/table fix therefore mainly increases candidate coverage; v2 determines how many of those additional concentration-basis rows become verified rather than unresolved.
