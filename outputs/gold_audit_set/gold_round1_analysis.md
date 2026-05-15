# Gold Round 1 Analysis

????????? `outputs/gold_audit_set/gold_set_seed_round1.csv`?????? `gold_round1_correction_log.md`?

## 1.1 ????

| ?? | ?? |
|---|---:|
| ???? | 71 |
| gold_keep_record = yes | 14 |
| gold_keep_record = no | 57 |
| ??????? paper ? | 23 |

## 1.2 ? pipeline verification_status ?????

| pipeline status | ?? | gold_keep = yes | gold_keep = no | ?? |
|---|---:|---:|---:|---|
| verified | 10 | 10 | 0 | -> ??? precision |
| unresolved | 56 | 4 | 52 | -> gold_keep = yes ??? false negative / recall loss |
| rejected | 5 | 0 | 5 | -> gold_keep = yes ????? |

## 1.3 ? route ?????

| route | ?? | gold_keep = yes | gold_keep = no | gold_keep = yes ?? |
|---|---:|---:|---:|---:|
| table | 18 | 0 | 18 | 0.000 |
| text | 4 | 0 | 4 | 0.000 |
| mixed | 18 | 0 | 18 | 0.000 |
| figure | 31 | 14 | 17 | 0.452 |

## 1.4 ? route ? pipeline status ????

| route | verified ? keep=yes | verified ? keep=no | unresolved ? keep=yes | unresolved ? keep=no |
|---|---:|---:|---:|---:|
| table | 0 | 0 | 0 | 13 |
| text | 0 | 0 | 0 | 4 |
| mixed | 0 | 0 | 0 | 18 |
| figure | 10 | 0 | 4 | 17 |

## 1.5 Scope gate ????????

| ?? | yes | no | uncertain | ??? (yes/total) |
|---|---:|---:|---:|---:|
| gold_target_api_ok | 65 | 6 | 0 | 0.915 |
| gold_5pct_ww_ok | 14 | 57 | 0 | 0.197 |
| gold_franz_ok | 38 | 33 | 0 | 0.535 |
| gold_ivpt_ivrt_ok | 38 | 33 | 0 | 0.535 |
| gold_amount_endpoint_ok | 39 | 32 | 0 | 0.549 |
| gold_endpoint_time_ok | 41 | 30 | 0 | 0.577 |
| gold_endpoint_value_correct | 9 | 62 | 0 | 0.127 |
| gold_area_ok | 25 | 46 | 0 | 0.352 |

## 1.6 False negative ?????unresolved ? gold_keep = yes ????

| record_id | doi | route | failure_reasons | scope_tags | ?? gold ???? yes | gold_notes ?? |
|---|---|---|---|---|---|---|
| record_62962b5f0280 | 10.1208/s12249-019-1584-8 | figure | not_target_api_concentration | useful_but_out_of_scope, useful_api_concentration_out_of_scope | gold_target_api_ok, gold_5pct_ww_ok, gold_franz_ok, gold_ivpt_ivrt_ok, gold_amount_endpoint_ok, gold_endpoint_time_ok | conclusion: yes; evidence: Fig.3a; Reason: the api_concentration was extracted as 1% w/w. the paper states 5 % w/w in Table I, diffusion area is 1.6 cm^2. |
| record_96e92dcd41dd | 10.1208/s12249-019-1584-8 | figure | not_target_api_concentration | useful_but_out_of_scope, useful_api_concentration_out_of_scope | gold_target_api_ok, gold_5pct_ww_ok, gold_franz_ok, gold_ivpt_ivrt_ok, gold_amount_endpoint_ok, gold_endpoint_time_ok | conclusion: yes; evidence: Fig.3a; Reason: the api_concentration was extracted as 1% w/w. the paper states 5 % w/w in Table I, diffusion area is 1.6 cm^3. |
| record_c3fdc7aafe21 | 10.1208/s12249-019-1584-8 | figure | not_target_api_concentration | useful_but_out_of_scope, useful_api_concentration_out_of_scope | gold_target_api_ok, gold_5pct_ww_ok, gold_franz_ok, gold_ivpt_ivrt_ok, gold_amount_endpoint_ok, gold_endpoint_time_ok | conclusion: yes; evidence: Fig.3a; Reason: the api_concentration was extracted as 1% w/w. the paper states 5 % w/w in Table I, diffusion area is 1.6 cm^4. |
| record_c846ed69a806 | 10.1208/s12249-019-1584-8 | figure | not_target_api_concentration | useful_but_out_of_scope, useful_api_concentration_out_of_scope | gold_target_api_ok, gold_5pct_ww_ok, gold_franz_ok, gold_ivpt_ivrt_ok, gold_amount_endpoint_ok, gold_endpoint_time_ok | conclusion: no; evidence: Fig.3a; Reason: endpoint is not correct by extraction, the api_concentration was extracted as 1% w/w. the paper states 5 % w/w in Table I, diffusion area is 1.6 cm^5. |

?? false negative ???? `failure_reason`?

| failure_reason | ?????? false negative ? | ? false negative ????? |
|---|---:|---:|
| not_target_api_concentration | 4 | 1.000 |

## 1.7 Verified false positive ???verified ? gold_keep = no ????

???? verified false positive?

## 1.8 Rejected sanity check

| record_id | doi | gold_keep_record | gold_notes ?? |
|---|---|---|---|
| record_ad27c13dbfc5 | 10.1002/14651858.cd001177.pub2 | no | conclusion: no; Evidence: no; Reason: this paper is out of scope, it didn't use the standard experiments for test, even it's a review paper. |
| record_8e1fffe4c0d8 | 10.1016/j.ijpharm.2019.118975 | no | conclusion: no; evidence: Fig. 6 and Table 5, area states 0.636cm^2 in section "2.13 In vitro skin permeation study", concentration states in Table 1. |
| record_e3dfbeb3c6e6 | 10.1016/j.ijpharm.2019.118975 | no | conclusion: no; evidence: Fig. 6 and Table 5, area states 0.636cm^2 in section "2.13 In vitro skin permeation study", concentration states in Table 1. |
| record_4bf2d137203c | 10.1038/s41598-020-65845-w | no | conclusion: no; Evidence: no; Reason: this paper is out of scope, it didn't use the standard experiments for test. |
| record_80b4061123c9 | 10.1186/s12951-020-00718-y | no | conclusion: no; evidence: Fig. 9; reason: it's out of scope and without experiment description. |

## 1.9 Scope precision vs Value precision ???

| ?? | ?? | ?? |
|---|---:|---|
| verified ?? | 10 | |
| scope_correct = yes | 10 | Scope precision?verification ? scope ????? |
| scope_correct = yes ? value_correct = yes/approximate | 0 | End-to-end precision?scope ?????? |
| scope_correct = yes ? value_correct = no | 10 | Scope ??????? -> ??? extractor/digitizer |
| scope_correct = no | 0 | Scope ??? -> ??? verification |

## 1.10 Value error ????

| record_id | doi | route | endpoint_kind | endpoint_value (pipeline) | endpoint_unit | gold_notes ?? |
|---|---|---|---|---|---|---|
| record_47710103a12d | 10.1016/j.ejpb.2020.05.013 | figure | amount_total | 261.17059326171875 | ug | conclusion: no; evidence: section 2.2.6 and Fig. 11(a); Reason: the area is 3.14 cm^2, endpoint was extracted 261.17059 μg, but the paper states approximately 200 μg/cm².  |
| record_cc84e1bf6e4e | 10.1016/j.ejpb.2020.05.013 | figure | amount_total | 261.17059326171875 | ug | conclusion: no; evidence: section 2.2.6 and Fig. 11(a); Reason: the area is 3.14 cm^2, endpoint was extracted 261.17059 μg, but the paper states approximately 200 μg/cm². |
| record_e04ec91b3e26 | 10.1016/j.ejpb.2020.05.013 | figure | amount_total | 261.17059326171875 | ug | conclusion: no; evidence: section 2.2.6 and Fig. 11(a); Reason: the area is 3.14 cm^2, endpoint was extracted 261.17059 μg, but the paper states approximately 200 μg/cm². |
| record_1d882e0e9090 | 10.1016/j.ijpharm.2016.03.043 | figure | amount_per_area | 36.438011169433594 | μg/cm² | conclusion: no; Evidence: Fig. 1; Reason: the endpoint is no correct by Figure, paper states Ibuprofen (blue) permeates the Human skin in Figure 1(A), but it seem the Figure-Agent misatched y-axis (actually belongs to Fig. 1(B)) in the extraction progress. |
| record_339f642dd0cd | 10.1016/j.ijpharm.2016.03.043 | figure | amount_per_area | 30.459407806396484 | μg/cm² | conclusion: no; Evidence: Fig. 1; Reason: the endpoint is no correct by Figure, paper states Ibuprofen (blue) permeates the Porcine skin in Figure 1(B). |
| record_437e38b169f5 | 10.1016/j.ijpharm.2016.03.043 | figure | amount_per_area | 90 | µg/cm² | conclusion: no; Evidence: Fig. 1; Reason: the endpoint is no correct by Figure, paper states Ibuprofen (blue) permeates the Human skin in Figure 1(A), but it seem the Figure-Agent misatched y-axis (actually belongs to Fig. 1(B)) in the extraction progress. |
| record_982332825448 | 10.1016/j.ijpharm.2016.03.043 | figure | amount_per_area | 6.261798858642578 | μg/cm² | conclusion: no; Evidence: Fig. 1; Reason: the endpoint is no correct by Figure, paper states Ibuprofen (blue) permeates the Porcine skin in Figure 1(B). |
| record_a28c8f99f0f6 | 10.1016/j.ijpharm.2016.03.043 | figure | amount_per_area | 280 | µg/cm² | conclusion: no; Evidence: Fig. 1; Reason: the endpoint is no correct by Figure, paper states Ibuprofen (blue) permeates the Human skin in Figure 1(A), but it seem the Figure-Agent misatched y-axis (actually belongs to Fig. 1(B)) in the extraction progress. |
| record_ca0291b430fe | 10.1016/j.ijpharm.2016.03.043 | figure | amount_per_area | 30.490875244140625 | μg/cm² | conclusion: no; Evidence: Fig. 1; Reason: the endpoint is no correct by Figure, paper states Ibuprofen (blue) permeates the Porcine skin in Figure 1(B). |
| record_e5a5cd848fa6 | 10.1016/j.ijpharm.2016.03.043 | figure | amount_per_area | 280 | µg/cm² | conclusion: no; Evidence: Fig. 1; Reason: the endpoint is no correct by Figure, paper states Ibuprofen (blue) permeates the Human skin in Figure 1(A), but it seem the Figure-Agent misatched y-axis (actually belongs to Fig. 1(B)) in the extraction progress. |
| record_c846ed69a806 | 10.1208/s12249-019-1584-8 | figure | amount_per_area | 0.5 | mg/cm^2 | conclusion: no; evidence: Fig.3a; Reason: endpoint is not correct by extraction, the api_concentration was extracted as 1% w/w. the paper states 5 % w/w in Table I, diffusion area is 1.6 cm^5. |

Value error route ???

| route | value error ?? |
|---|---:|
| figure | 11 |

## 1.11 ???? false negative ??

| pipeline status | ?? | gold_keep = yes????? | gold_keep = no????? |
|---|---:|---:|---:|
| unresolved | 56 | 4 | 52 |

- ??? unresolved false negative ???`4`
- ????? top failure_reason bucket?`not_target_api_concentration`?4/4?

## 1.12 ????

- ????? precision?`1.000`?recall?`0.714`?F1?`0.833`?
- ??? scope precision?`1.000`?end-to-end precision?`0.000`?
- ??????????? verification scope??? figure route ? endpoint value ???
- verified ??? scope ??????? 10/10 verified ?? value ???
- unresolved ? recall loss ?????????? `not_target_api_concentration`?
- rejected ??????????????