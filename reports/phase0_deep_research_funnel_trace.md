# Phase 0 Deep Research Funnel Trace

## 1. Executive summary

Strict DOI/title resolution found 7 direct DOI matches, 0 title fallback matches, and 5 unresolved candidates. Attrition is entirely early: 5 corpus misses, 2 rule-filter rejects, 2 content-access failures, and 3 router-unresolved papers. None reached extraction, assembly, patching, or v1-v4 verification. Bolla 2020 is in corpus, passes rule and LLM triage, and has OA HTML/PDF, but routing stayed unresolved because Franz was not confirmed and the barrier was classified as synthetic Strat-M.

## 2. 12-paper funnel table

| dr_rank | first_author_year | journal | primary_doi | doi_resolution | corpus_doi | in_corpus | corpus_pmid | corpus_pmcid | passed_rule_filter | llm_triage_label | llm_triage_confidence | content_access_status | content_access_backend | route_decision | route_confidence | n_text_records | n_table_records | n_figure_records | n_assembled_records | n_patched_records | v1_status_breakdown | v2_status_breakdown | v3_status_breakdown | v4_status_breakdown | failure_stage | failure_reason_short |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Bolla_2020 | Pharmaceutics | 10.3390/pharmaceutics12020151 | direct_doi_match | 10.3390/pharmaceutics12020151 | true | 32069850 | PMC7076669 | true | relevant | 0.9 | status=downloaded; preferred_format=html; available_formats=html,pdf; notes=legacy_pdf_reused_local | html_local | unresolved | 0.2 | 0 | 0 | 0 | 0 | 0 | na | na | na | na | router_unresolved | notes=The document appears to be a study focusing on ibuprofen permeation through a synthetic membrane.; franz_confirmed=no; barrier_category=synthetic_membrane; endpoint_carrier=unknown; formulation_carrier=unknown |
| 2 | Chen_2006 | Int J Pharm | 10.1016/j.ijpharm.2006.02.015 | direct_doi_match | 10.1016/j.ijpharm.2006.02.015 | true | 16600540 |  | true | relevant | 0.95 | status=unresolved; preferred_format=unresolved; available_formats=none | missing | unresolved | 0.0 | 0 | 0 | 0 | 0 | 0 | na | na | na | na | content_access_fail | status=unresolved; preferred_format=unresolved; available_formats=none |
| 3 | Theochari_2021 | J Mol Liquids | 10.1016/j.molliq.2021.116021 | not_found |  | false |  |  | na | na | na | na | na | na | na | 0 | 0 | 0 | 0 | 0 | na | na | na | na | corpus_miss | no direct DOI match and no title keyword fallback match in corpus title column |
| 4 | Salim_2012 | Int J Nanomedicine | 10.2147/ijn.s34700 | direct_doi_match | 10.2147/ijn.s34700 | true | 22973096 | PMC3439863 | true | relevant | 0.95 | status=downloaded; preferred_format=html; available_formats=html,pdf; notes=legacy_pdf_reused_local | html_local | unresolved | 0.2 | 0 | 0 | 0 | 0 | 0 | na | na | na | na | router_unresolved | notes=Extraction from the provided content is limited; more specific sections on methods, results, or discussions are needed for thorough analy...; franz_confirmed=no; barrier_category=uncertain; endpoint_carrier=unknown; formulation_carrier=unknown |
| 5 | Salim_2018 | Mater. Today Proc. | (not confidently known) | not_found |  | false |  |  | na | na | na | na | na | na | na | 0 | 0 | 0 | 0 | 0 | na | na | na | na | corpus_miss | no direct DOI match and no title keyword fallback match in corpus title column |
| 6 | Stahl_2011 | BMC Pharmacology | 10.1186/1471-2210-11-12 | direct_doi_match | 10.1186/1471-2210-11-12 | true | 22168832 | PMC3259031 | false | na | na | na | na | na | na | 0 | 0 | 0 | 0 | 0 | na | na | na | na | rule_filter_reject | rule_relevance_label=not_relevant; hints=\bin vitro\b,\bpermeat,\bdiffus,\btransdermal\b,\bskin\b; exclusions=\boral\b,\bplasma\b |
| 7 | Pradal_2020 | J Pain Research | 10.2147/jpr.s262390 | direct_doi_match | 10.2147/jpr.s262390 | true | 33177865 | PMC7650811 | true | relevant | 0.95 | status=downloaded; preferred_format=html; available_formats=html,pdf; notes=failed_download:pdf | html_local | unresolved | 0.0 | 0 | 0 | 0 | 0 | 0 | na | na | na | na | router_unresolved | notes=missing_structured_and_pdf_router_source:blocked:html_local:captcha;blocked:html_remote:captcha |
| 8 | Vlaia_2014 | Rev Chim Bucharest | (not confidently known) | not_found |  | false |  |  | na | na | na | na | na | na | na | 0 | 0 | 0 | 0 | 0 | na | na | na | na | corpus_miss | no direct DOI match and no title keyword fallback match in corpus title column |
| 9 | Djekic_2019 | J Pharm Sci | 10.1016/j.xphs.2018.10.054 | direct_doi_match | 10.1016/j.xphs.2018.10.054 | true | 30395827 |  | true | relevant | 0.9 | status=unresolved; preferred_format=unresolved; available_formats=none | missing | unresolved | 0.0 | 0 | 0 | 0 | 0 | 0 | na | na | na | na | content_access_fail | status=unresolved; preferred_format=unresolved; available_formats=none |
| 10 | Djekic_2016 | Eur J Pharm Sci | 10.1016/j.ejps.2016.05.024; 10.1016/j.ejps.2016.05.020 | not_found |  | false |  |  | na | na | na | na | na | na | na | 0 | 0 | 0 | 0 | 0 | na | na | na | na | corpus_miss | no direct DOI match and no title keyword fallback match in corpus title column; author/year near-match exists but was not counted by the requested DOI/title resolver: 10.1016/j.ejps.2016.05.005 (Formulation of hydrogel-thickened nonionic microemulsions with... |
| 11 | Hadgraft_2003 | Skin Pharmacol Appl Skin Physiol | 10.1159/000069759 | direct_doi_match | 10.1159/000069759 | true | 12677093 |  | false | na | na | na | na | na | na | 0 | 0 | 0 | 0 | 0 | na | na | na | na | rule_filter_reject | rule_relevance_label=not_relevant; hints=\bin vitro\b,\bdiffus,\btopical\b,\bskin\b; exclusions=\bin vivo\b |
| 12 | Herkenne_2007 | J Invest Dermatol | 10.1038/sj.jid.5700587; 10.1038/jid.2007.196 | not_found |  | false |  |  | na | na | na | na | na | na | na | 0 | 0 | 0 | 0 | 0 | na | na | na | na | corpus_miss | title keyword fallback was ambiguous: 2 title rows matched, with no unique 2007 row; author/year near-match exists but was not counted by the requested DOI/title resolver: 10.1038/sj.jid.5700491 (Ibuprofen transport into and through skin from topical formul... |

## 3. failure_stage distribution

| failure_stage | count | bar |
| --- | --- | --- |
| corpus_miss | 5 | ##### |
| router_unresolved | 3 | ### |
| content_access_fail | 2 | ## |
| rule_filter_reject | 2 | ## |

## 4. Bolla 2020 deep-dive

### 4.1 Corpus diagnosis

| field | value |
| --- | --- |
| doi | 10.3390/pharmaceutics12020151 |
| title | Evaluation of Formulation Parameters on Permeation of Ibuprofen from Topical Formulations Using Strat-M<sup>®</sup> Membrane. |
| year | 2020 |
| pmid | 32069850 |
| pmcid | PMC7076669 |
| journal | blank in corpus.csv |
| authors | Bolla PK, Clark BA, Juluri A, Cheruvu HS, Renukuntla J. |
| url | https://doi.org/10.3390/pharmaceutics12020151 |

Abstract from corpus.csv:

```text
Topical drug delivery is an attractive alternative to conventional methods because of advantages such as non-invasive delivery, by-pass of first pass metabolism, and improved patient compliance. However, several factors such as skin, physicochemical properties of the drug, and vehicle characteristics influence the permeation. Within a formulation, critical factors such as concentration of drug, physical state of drug in the formulation, and organoleptic properties affect the flux across the skin. The aim of the study was to develop and investigate topical semisolid preparations (creams and gels) with ibuprofen as the model drug and investigate the effect of various formulation parameters on the in-vitro performance across the Strat-M<sup>®</sup> membrane using flow-through cells. In addition, the physical stability of the developed formulations was investigated by studying viscosity, pH, and appearance. All the formulations developed in the study had appealing appearance with smooth texture and no signs of separation. Viscosity and pH of the formulations were acceptable. Cumulative amount of drug permeated at the end of 24 h was highest for clear gel (3% <i>w</i>/<i>w</i> ibuprofen; F6: 739.6 ± 36.1 µg/cm<sup>2</sup>) followed by cream with high concentration of ibuprofen in suspended form (5% <i>w</i>/<i>w</i>; F3: 320.8 ± 17.53 µg/cm<sup>2</sup>), emulgel (3% <i>w</i>/<i>w</i> ibuprofen; F5: 178.5 ± 34.5 µg/cm<sup>2</sup>), and cream with solubilized ibuprofen (3% <i>w</i>/<i>w</i>; F2A: 163.2 ± 9.36 µg/cm<sup>2</sup>). Results from this study showed that permeation of ibuprofen was significantly influenced by formulation parameters such as concentration of ibuprofen (3% vs. 5% <i>w</i>/<i>w</i>), physical state of ibuprofen (solubilized vs. suspended), formulation type (cream vs. gel), mucoadhesive agents, and viscosity (high vs. low). Thus, findings from this study indicate that pharmaceutical formulation scientists should explore these critical factors during the early development of any new topical drug product in order to meet pre-determined quality target product profile.
```

### 4.2 Rule and LLM triage

Bolla passed the deterministic rule filter. Rule hints were `\bpermeat, \btopical\b, \bskin\b, \bmembrane\b` and exclusions were `none`. The LLM triage label was `relevant` with confidence `0.9`.

### 4.3 Content access

| field | value |
| --- | --- |
| paper_id | paper_701029bf55bc |
| status | downloaded |
| preferred_format | html |
| available_formats | html, pdf |
| local_paths | {"html": "papers\\html\\10.3390_pharmaceutics12020151__c5e94d827e.html", "pdf": "papers\\pdf\\10.3390_pharmaceutics12020151__795b0a9f10.pdf"} |
| access_urls | {"html": "https://europepmc.org/articles/PMC7076669", "pdf": "https://europepmc.org/articles/PMC7076669?pdf=render"} |
| notes | legacy_pdf_reused_local |

### 4.4 Router decision

| field | value |
| --- | --- |
| paper_id | paper_701029bf55bc |
| route | unresolved |
| route_confidence | 0.2 |
| endpoint_carrier | unknown |
| formulation_carrier | unknown |
| notes | The document appears to be a study focusing on ibuprofen permeation through a synthetic membrane. |
| raw_labels.paper_type | uncertain |
| raw_labels.mentions_ibuprofen | yes |
| raw_labels.mentions_diffusion_cell | yes |
| raw_labels.franz_confirmed | no |
| raw_labels.where_diffusion_cell | Strat-M® Membrane |
| raw_labels.where_franz | unknown |
| raw_labels.study_type | IVPT |
| raw_labels.barrier_category | synthetic_membrane |
| raw_labels.barrier_name_raw | Strat-M® Membrane |
| raw_labels.endpoint_found | uncertain |
| raw_labels.endpoint_time_found | uncertain |
| raw_labels.endpoint_carrier | unknown |
| raw_labels.formulation_carrier | unknown |
| raw_labels.router_source_backend | pdf_local |
| raw_labels.router_source_ref | papers\pdf\10.3390_pharmaceutics12020151__795b0a9f10.pdf |

The router record exists but the route is `unresolved`; therefore downstream extraction did not run for this DOI in the frozen baseline artifacts.

### 4.5 Extractor output

| modality | records |
| --- | --- |
| text | 0 |
| table | 0 |
| figure | 0 |
| assembled | 0 |
| patched_area | 0 |

No text/table/figure records exist for Bolla 2020, so there are no extracted formulation labels, endpoint values, devices, membranes, or receptor media to list from the baseline outputs.

### 4.6 Verifier status

| policy | verified | status_breakdown | failure_reasons |
| --- | --- | --- | --- |
| v1 | 0 | na | na |
| v2 | 0 | na | na |
| v3 | 0 | na | na |
| v4 | 0 | na | na |

Because no patched_area records exist for Bolla 2020, v1-v4 did not evaluate any Bolla extraction records. The specific checks for `non_franz_device`, `concentration_not_5pct_ww`, and unusual receptor medium were therefore not reached in these artifacts.

### 4.7 Expected-vs-observed Table 7 comparison

| formulation | expected_24h_amount_ug_cm2 | extracted_record_found | v4_verified |
| --- | --- | --- | --- |
| F1A | 59.1 | false | false |
| F1B | 43.4 | false | false |
| F2A | 163.2 | false | false |
| F2B | 77.5 | false | false |
| F3 | 320.8 | false | false |
| F4 | 82.0 | false | false |
| F5 | 178.5 | false | false |
| F6 | 739.6 | false | false |

| metric | count |
| --- | --- |
| Expected Table 7 records | 8 |
| Actual assembled records | 0 |
| v1 verified records | 0 |
| v2 verified records | 0 |
| v3 verified records | 0 |
| v4 verified records | 0 |

## 5. Aggregate summary

### 5.1 Funnel attrition

| failure_stage | count | bar |
| --- | --- | --- |
| corpus_miss | 5 | ##### |
| router_unresolved | 3 | ### |
| content_access_fail | 2 | ## |
| rule_filter_reject | 2 | ## |

### 5.2 Low-hanging fruit

None in the strict 12-paper trace. No candidate reached assembled_records or patched_area, so there is no zero-manual-cost rescue path through v2/v3/v4 rescoring for these resolved rows.

### 5.3 Corpus/query expansion and resolver fixes

| paper | strict_status | recommended_action |
| --- | --- | --- |
| Theochari_2021 | corpus_miss | Add DOI 10.1016/j.molliq.2021.116021 and terms: ibuprofen, microemulsion, chitosan, Journal of Molecular Liquids. |
| Salim_2018 | corpus_miss | Add terms: PIC method, ibuprofen nanoemulsion, phase inversion composition, Salim 2018. |
| Vlaia_2014 | corpus_miss | Add terms: Nurofen, Tuffryn, ibuprofen, Rev Chim Bucharest, Vlaia. |
| Djekic_2016 | corpus_miss | Resolver correction likely needed: corpus contains Djekic 2016 as DOI 10.1016/j.ejps.2016.05.005; add terms hydrogel-thickened nonionic microemulsions and Djekic. |
| Herkenne_2007 | corpus_miss | Resolver correction likely needed: corpus contains Herkenne 2007 as DOI 10.1038/sj.jid.5700491; add terms ibuprofen transport into and through skin, in vitro-in vivo comparison. |

Author/year near-matches found in corpus.csv but not counted in the main strict DOI/title table:

| candidate | near_match_doi | year | title | note |
| --- | --- | --- | --- | --- |
| Djekic_2016 | 10.1016/j.ejps.2016.05.005 | 2016 | Formulation of hydrogel-thickened nonionic microemulsions with enhanced percutaneous delivery of ibuprofen assessed in vivo in rats. | not counted in main table because requested DOI/title resolver did not match it |
| Herkenne_2007 | 10.1038/sj.jid.5700491 | 2007 | Ibuprofen transport into and through skin from topical formulations: in vitro-in vivo comparison. | not counted in main table because requested DOI/title resolver did not match it |

## 6. Known limitations / open questions

| item | status |
| --- | --- |
| Stage artifacts | All requested baseline JSONL artifacts were present; no stage_artifact_missing condition was observed. |
| Rescore artifacts | v2, v3, and v4 verified_records.jsonl files were found under outputs/full_run_16_post_all_fixes/*_rescore/. |
| Content status vocabulary | This run uses status=downloaded as the successful content-access state, not the literal status=success. |
| Strict resolver | Main table resolution uses DOI candidates plus title-keyword fallback only. Author/year near-matches are reported separately and not counted. |
| Uncertain DOI rows | Salim_2018 and Vlaia_2014 remain unresolved under DOI/title matching. |
| Djekic_2016 and Herkenne_2007 | Likely intended corpus rows exist with different DOIs, but the prompt-provided DOI/title fallback did not uniquely resolve them. |

### Artifact inventory

| artifact | status | records |
| --- | --- | --- |
| outputs/full_run_16_post_all_fixes/rule_pass.jsonl | present | 749 |
| outputs/full_run_16_post_all_fixes/rule_fail.jsonl | present | 1079 |
| outputs/full_run_16_post_all_fixes/llm_triage.jsonl | present | 749 |
| outputs/full_run_16_post_all_fixes/content_access.jsonl | present | 536 |
| outputs/full_run_16_post_all_fixes/route_decisions.jsonl | present | 536 |
| outputs/full_run_16_post_all_fixes/text_records.jsonl | present | 10 |
| outputs/full_run_16_post_all_fixes/table_records.jsonl | present | 252 |
| outputs/full_run_16_post_all_fixes/figure_records.jsonl | present | 10 |
| outputs/full_run_16_post_all_fixes/assembled_records.jsonl | present | 239 |
| outputs/full_run_16_post_all_fixes/patched_area.jsonl | present | 239 |
| outputs/full_run_16_post_all_fixes/verified_records.jsonl | present | 239 |
| outputs/full_run_16_post_all_fixes/v2_rescore/verified_records.jsonl | present | 239 |
| outputs/full_run_16_post_all_fixes/v3_rescore/verified_records.jsonl | present | 239 |
| outputs/full_run_16_post_all_fixes/v4_rescore/verified_records.jsonl | present | 239 |
