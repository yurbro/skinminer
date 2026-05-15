# Full Run 15 Delta vs Full Run 13

Baseline: `outputs/full_run_13_post_fix5` (v1, post-Fix-5). Current: `outputs/full_run_15_schema_table_fix` (v1, schema/table prompt fix).

## Headline Metrics

| run | table_records | text_records | figure_records | assembled | verified | unresolved | rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full_run_13_post_fix5_v1 | 64 | 11 | 9 | 79 | 4 | 48 | 27 |
| full_run_15_schema_table_fix_v1 | 220 | 11 | 16 | 233 | 10 | 161 | 62 |

Delta full_run15 vs full_run13: assembled +154, verified +6, unresolved +113, rejected +35.

Route-level final status:

| run | route | verified | unresolved | rejected |
| --- | --- | ---: | ---: | ---: |
| full_run_13_post_fix5_v1 | figure | 4 | 25 | 21 |
| full_run_13_post_fix5_v1 | mixed | 0 | 4 | 2 |
| full_run_13_post_fix5_v1 | table | 0 | 10 | 4 |
| full_run_13_post_fix5_v1 | text | 0 | 9 | 0 |
| full_run_15_schema_table_fix_v1 | figure | 9 | 49 | 13 |
| full_run_15_schema_table_fix_v1 | mixed | 1 | 49 | 19 |
| full_run_15_schema_table_fix_v1 | table | 0 | 60 | 29 |
| full_run_15_schema_table_fix_v1 | text | 0 | 3 | 1 |

## Table Route Completeness

Table records increased from 64 to 220 (+156). The largest DOI-level increases are:

| doi_or_paper_id | full_run_13_table_records | full_run_15_table_records | delta_15_vs_13 |
| --- | --- | --- | --- |
| 10.1208/s12249-013-9995-4 | 4 | 24 | 20 |
| 10.4103/jomfp.jomfp_253_19 | 1 | 19 | 18 |
| 10.1038/s41598-024-57883-5 | 1 | 10 | 9 |
| 10.1208/s12249-015-0474-y | 0 | 8 | 8 |
| 10.1007/s13346-022-01182-x | 2 | 9 | 7 |
| 10.3762/bjoc.9.104 | 1 | 8 | 7 |
| 10.1248/cpb.c21-00033 | 5 | 11 | 6 |
| 10.1016/j.ejpb.2020.05.013 | 1 | 7 | 6 |
| 10.1038/srep08114 | 0 | 6 | 6 |
| 10.1042/bj2700039 | 0 | 6 | 6 |
| 10.3390/membranes12080762 | 0 | 6 | 6 |
| 10.3390/pharmaceutics16111465 | 0 | 6 | 6 |
| 10.1039/d0ra00100g | 2 | 7 | 5 |
| 10.1186/2050-6511-13-5 | 1 | 6 | 5 |
| 10.1016/j.ijpharm.2016.03.043 | 4 | 8 | 4 |


Full per-paper table deltas are in `outputs\full_run_15_schema_table_fix\report\table_record_count_delta.csv`.

## New Field Fill Rates

New schema fields are expected to be absent or effectively zero in full_run13. Full_run15 fill rates below are measured on current records.

Table records:

| field | filled/total | rate |
| --- | --- | --- |
| membrane_type | 192/220 | 87.3% |
| membrane_source | 137/220 | 62.3% |
| membrane_thickness_um | 118/220 | 53.6% |
| receptor_medium | 113/220 | 51.4% |
| dose_type | 149/220 | 67.7% |
| dose_amount | 195/220 | 88.6% |


Assembled records:

| field | filled/total | rate |
| --- | --- | --- |
| membrane_type | 205/233 | 88.0% |
| membrane_source | 151/233 | 64.8% |
| membrane_thickness_um | 134/233 | 57.5% |
| receptor_medium | 124/233 | 53.2% |
| dose_type | 154/233 | 66.1% |
| dose_amount | 208/233 | 89.3% |


Verified-only records:

| field | filled/total | rate |
| --- | --- | --- |
| membrane_type | 10/10 | 100.0% |
| membrane_source | 10/10 | 100.0% |
| membrane_thickness_um | 10/10 | 100.0% |
| receptor_medium | 1/10 | 10.0% |
| dose_type | 10/10 | 100.0% |
| dose_amount | 10/10 | 100.0% |


Full fill-rate table: `outputs\full_run_15_schema_table_fix\report\new_field_fill_rates.csv`.

## Failure Taxonomy Shift

Top absolute taxonomy shifts vs full_run13:

| failure_reason | full_run_13_post_fix5_v1 | full_run_14_v2_policy | full_run_15_schema_table_fix_v1 | full_run_15_schema_table_fix_v2_rescore | delta_15_v1_vs_13 |
| --- | --- | --- | --- | --- | --- |
| insufficient_evidence | 54 | 54 | 140 | 140 | 86 |
| ambiguous_api_concentration | 42 | 26 | 102 | 78 | 60 |
| missing_api_concentration | 1 | 1 | 55 | 55 | 54 |
| not_target_api_concentration | 10 | 10 | 44 | 44 | 34 |
| not_target_api | 16 | 11 | 49 | 49 | 33 |
| missing_area | 14 | 17 | 44 | 44 | 30 |
| percent_only | 6 | 2 | 19 | 19 | 13 |
| unit_normalization_failed | 3 | 1 | 13 | 13 | 10 |
| missing_endpoint | 11 | 9 | 20 | 20 | 9 |
| not_target_study_type | 12 | 9 | 20 | 20 | 8 |
| not_target_device | 3 | 5 | 6 | 6 | 3 |
| missing_endpoint_time | 2 | 0 | 0 | 0 | -2 |


Interpretation: the table prompt now extracts many more per-formulation/per-timepoint records, so unresolved/rejected counts increase in absolute terms. The useful signal is that verified also increases under the same v1 policy, while many new extracted rows remain blocked by concentration-basis ambiguity or evidence sufficiency gates.
