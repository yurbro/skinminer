# E3 Claude v2 Rescore Summary

Input records: `patched_area.jsonl` from `outputs/experiment_E3_claude_v2`; LLM stages were not rerun.
Policy: `v2_accept_wv`

| Metric | v1 Claude | v2 Claude | Delta |
| --- | --- | --- | --- |
| verified | 0 | 24 | 24 |
| unresolved | 83 | 59 | -24 |
| rejected | 10 | 10 | 0 |
| table verified | 0 | 24 | 24 |
| figure verified | 0 | 0 | 0 |

## v2 Failure Taxonomy

| Failure reason | Count |
| --- | --- |
| ambiguous_api_concentration | 29 |
| source_context_inconsistent | 26 |
| insufficient_evidence | 16 |
| not_target_study_type | 10 |
| percent_only | 7 |
| missing_endpoint | 6 |
| missing_api_concentration | 6 |
| figure_digitization_failed | 4 |
| missing_area | 3 |
| missing_endpoint_time | 1 |
| ambiguous_mapping | 1 |

## V2 Verified Records

| record_id | doi | route | label | api_raw | endpoint | normalized |
| --- | --- | --- | --- | --- | --- | --- |
| record_d16c057fc54f | 10.1208/s12249-013-9995-4 | table | F1 | 5% (w/v) | 298.0 ug @ 24.0 h | 465.625 ug/cm^2 |
| record_453da10d1ec5 | 10.1208/s12249-013-9995-4 | table | F1 | 5% (w/v) | 536.5 ug @ 48.0 h | 838.28125 ug/cm^2 |
| record_3ec6644ba612 | 10.1208/s12249-013-9995-4 | table | F1 | 5% (w/v) | 1142.4 ug @ 72.0 h | 1785.0 ug/cm^2 |
| record_6ef7cb7d4ade | 10.1208/s12249-013-9995-4 | table | F2 | 5% (w/v) | 155.9 ug @ 24.0 h | 243.59375 ug/cm^2 |
| record_3672e05a60e6 | 10.1208/s12249-013-9995-4 | table | F2 | 5% (w/v) | 580.2 ug @ 48.0 h | 906.5625 ug/cm^2 |
| record_7f1a8e76ddde | 10.1208/s12249-013-9995-4 | table | F2 | 5% (w/v) | 1178.9 ug @ 72.0 h | 1842.03125 ug/cm^2 |
| record_dc0536190cb0 | 10.1208/s12249-013-9995-4 | table | F3 | 5% (w/v) | 140.2 ug @ 24.0 h | 219.06249999999997 ug/cm^2 |
| record_94fdeacead82 | 10.1208/s12249-013-9995-4 | table | F3 | 5% (w/v) | 543.5 ug @ 48.0 h | 849.21875 ug/cm^2 |
| record_a8b14ec9c84e | 10.1208/s12249-013-9995-4 | table | F3 | 5% (w/v) | 759.6 ug @ 72.0 h | 1186.875 ug/cm^2 |
| record_59963ee27e78 | 10.1208/s12249-013-9995-4 | table | F4 | 5% (w/v) | 132.3 ug @ 24.0 h | 206.71875 ug/cm^2 |
| record_eb5e98f7f8bb | 10.1208/s12249-013-9995-4 | table | F4 | 5% (w/v) | 464.8 ug @ 48.0 h | 726.25 ug/cm^2 |
| record_764e4aa71249 | 10.1208/s12249-013-9995-4 | table | F4 | 5% (w/v) | 734.4 ug @ 72.0 h | 1147.5 ug/cm^2 |
| record_83a3f9b0e06e | 10.1208/s12249-013-9995-4 | table | F5 | 5% (w/v) | 312.3 ug @ 24.0 h | 487.96875 ug/cm^2 |
| record_bbc291658e05 | 10.1208/s12249-013-9995-4 | table | F5 | 5% (w/v) | 542.5 ug @ 48.0 h | 847.65625 ug/cm^2 |
| record_9424b5553135 | 10.1208/s12249-013-9995-4 | table | F5 | 5% (w/v) | 799.5 ug @ 72.0 h | 1249.21875 ug/cm^2 |
| record_c83676244c03 | 10.1208/s12249-013-9995-4 | table | F6 | 5% (w/v) | 148.8 ug @ 24.0 h | 232.5 ug/cm^2 |
| record_cff9534403d5 | 10.1208/s12249-013-9995-4 | table | F6 | 5% (w/v) | 551.2 ug @ 48.0 h | 861.25 ug/cm^2 |
| record_d9fc1e579464 | 10.1208/s12249-013-9995-4 | table | F6 | 5% (w/v) | 808.0 ug @ 72.0 h | 1262.5 ug/cm^2 |
| record_8451385f5434 | 10.1208/s12249-013-9995-4 | table | F7 | 5% (w/v) | 123.9 ug @ 24.0 h | 193.59375 ug/cm^2 |
| record_771853ae9097 | 10.1208/s12249-013-9995-4 | table | F7 | 5% (w/v) | 260.1 ug @ 48.0 h | 406.40625 ug/cm^2 |
| record_1bf5e1e73737 | 10.1208/s12249-013-9995-4 | table | F7 | 5% (w/v) | 387.9 ug @ 72.0 h | 606.09375 ug/cm^2 |
| record_f014c92e4f9a | 10.1208/s12249-013-9995-4 | table | F8 | 5% (w/v) | 132.3 ug @ 24.0 h | 206.71875 ug/cm^2 |
| record_6a484a2ea1ad | 10.1208/s12249-013-9995-4 | table | F8 | 5% (w/v) | 464.8 ug @ 48.0 h | 726.25 ug/cm^2 |
| record_6378b97946c2 | 10.1208/s12249-013-9995-4 | table | F8 | 5% (w/v) | 734.4 ug @ 72.0 h | 1147.5 ug/cm^2 |
