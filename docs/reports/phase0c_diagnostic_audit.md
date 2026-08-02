# Phase 0c Diagnostic Audit

Deterministic audit only: existing SkinMiner outputs, PubMed/EPMC/Crossref metadata, DOI matching, and structured-field counts. No full-text PDFs were downloaded, no pipeline stage was rerun, and no LLM calls were made.

## 1. Pool Flow

| Stage | Paper count |
|---|---:|
| PubMed/EPMC theoretical universe (from Phase 0a Track B query) | 140 |
| SkinMiner retrieval corpus (ibuprofen subset) | 1828 |
| Survived triage | 536 |
| Survived access | 302 |
| Produced >= 1 assembled record | 38 |
| Verified at v2 | 2 |
| Verified at v3 | 8 |
| Verified at v4 | 10 |
| **Stage 1 audit pool (>= 1 record any provenance)** | 40 |

## 2. Track A Findings

Total `n_blocked_ibuprofen_papers`: `234`.
Subscription-tier distribution: likely_subscribed=188, now_oa=21, unlikely_subscribed=19, possibly_subscribed=6.
Top-tier candidates realistically fetchable in 1-2 weeks: `20` (capped at 20 manual PDFs).

Top 10 access-rescue candidates:
| doi | title | journal | publisher | year | subscription_tier | original_block_reason | current_oa_status | oa_url_if_any | priority_rank |
|---|---|---|---|---|---|---|---|---|---|
| 10.1016/j.carbpol.2025.124499 | Exploring new buccal films based on hydroxyethyl cellulose and Linecaps® combination fo... | Carbohydrate Polymers | Elsevier BV | 2026 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1016/j.carbpol.2025.124499 | 1 |
| 10.3390/pharmaceutics18020220 | Impact of Drug Hydrophilicity on Transdermal Delivery by Nanoemulsions. | Pharmaceutics | MDPI AG | 2026 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.3390/pharmaceutics18020220 | 2 |
| 10.1208/s12249-026-03373-y | Personalized 3D-Printed Finger Splints Derived from CT Data Incorporating Multi-Drug Bi... | AAPS PharmSciTech | Springer Science and Business Media LLC | 2026 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1208/s12249-026-03373-y | 3 |
| 10.1016/j.ijpharm.2024.125102 | Spatial separation of different drug substances in one microneedle array patch by combi... | International Journal of Pharmaceutics | Elsevier BV | 2025 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1016/j.ijpharm.2024.125102 | 4 |
| 10.1016/j.xphs.2025.103837 | Validating Otto: a Franz diffusion cell autosampler to automate in vitro permeation stu... | Journal of Pharmaceutical Sciences | Elsevier BV | 2025 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1016/j.xphs.2025.103837 | 5 |
| 10.1016/j.ejps.2024.106726 | Equivalence assessment of creams with quali-quantitative differences in light of the EM... | European Journal of Pharmaceutical Sciences | Elsevier BV | 2024 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1016/j.ejps.2024.106726 | 6 |
| 10.1208/s12249-024-02831-9 | Evaluation of Emulgel and Nanostructured Lipid Carrier-Based Gel Formulations for Trans... | AAPS PharmSciTech | Springer Science and Business Media LLC | 2024 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1208/s12249-024-02831-9 | 7 |
| 10.1016/j.scitotenv.2023.169863 | Occurrence and fate of CECs (OMPs, ARGs and pathogens) during decentralised treatment o... | Science of The Total Environment | Elsevier BV | 2024 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1016/j.scitotenv.2023.169863 | 8 |
| 10.1016/j.fitote.2024.106273 | Two new flavonoids from the leaves of Garcinia smeathmannii, in vitro and in silico ant... | Fitoterapia | Elsevier BV | 2024 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1016/j.fitote.2024.106273 | 9 |
| 10.1016/j.ijpharm.2023.122720 | 3D-printed EVA-based patches manufactured by direct powder extrusion for personalized t... | International Journal of Pharmaceutics | Elsevier BV | 2023 | now_oa | unresolved_no_resolved_oa_content | crossref_oa | https://doi.org/10.1016/j.ijpharm.2023.122720 | 10 |

## 3. Track B Findings

Total `n_papers_with_high_potential`: `4`.
Top 10 re-extraction targets:
| doi | n_records_total | pct_records_with_numeric_composition | pct_records_with_components_list | n_distinct_numeric_component_values | provenance_mix | re_extraction_potential | expected_lift_class | est_llm_input_tokens |
|---|---|---|---|---|---|---|---|---|
| 10.1186/2050-6511-13-5 | 27 | 0.0 | 0.0 | 0 | mixed=27 | 65 | high | 20000 |
| 10.4103/jomfp.jomfp_253_19 | 19 | 0.0 | 100.0 | 0 | table=19 | 65 | high | 8000 |
| 10.1016/j.ejpb.2020.05.013 | 12 | 100.0 | 100.0 | 2 | mixed=12 | 65 | high | 29000 |
| 10.1038/s41598-024-57883-5 | 10 | 0.0 | 100.0 | 0 | mixed=10 | 65 | high | 20000 |
| 10.1208/s12249-013-9995-4 | 24 | 100.0 | 100.0 | 3 | mixed=24 | 55 | medium | 8000 |
| 10.1016/j.ijpharm.2016.03.043 | 27 | 33.3 | 100.0 | 1 | mixed=27 | 50 | medium | 29000 |
| 10.1007/s11095-008-9785-y | 12 | 91.7 | 100.0 | 4 | table=6; mixed=5; text=1 | 50 | medium | 62000 |
| 10.1208/s12249-019-1481-1 | 10 | 100.0 | 100.0 | 16 | mixed=10 | 50 | medium | 20000 |
| 10.1208/s12249-019-1584-8 | 10 | 30.0 | 60.0 | 5 | mixed=10 | 50 | medium | 23000 |
| 10.1523/jneurosci.15-04-02768.1995 | 9 | 11.1 | 11.1 | 9 | mixed=9 | 45 | medium | 20000 |

Estimated top-10 input tokens: `239000`. Estimated input-only cost: GPT-5-class `$0.5975`; Claude Sonnet `$0.7170`. Input-token cost only; assumes OpenAI GPT-5.4 input at $2.50/M tokens and Claude Sonnet 4.5 input at $3.00/M tokens from official pricing pages checked on 2026-04-30: https://openai.com/api/pricing/ and https://platform.claude.com/docs/en/about-claude/pricing.

## 4. Track C Findings

SkinMiner retrieval query verbatim:

```text
(TITLE:"ibuprofen" OR ABSTRACT:"ibuprofen") AND (permeation OR permeat* OR diffusion OR "in vitro" OR release) AND (skin OR membrane OR topical OR transdermal OR "diffusion cell")
```

Phase 0a Track B unique DOI count: `131`.
SkinMiner corpus DOI count: `1827`.
Missed papers (Phase 0a Track B - SkinMiner corpus): `62`.

Top 5 missed papers:
| doi | title | journal | year | miss_reason | phase0a_oa |
|---|---|---|---|---|---|
| 10.1002/bdd.2194 | Hydrogel increases diclofenac skin permeation and absorption. | Biopharmaceutics &amp; Drug Disposition | 2019 | wrong_api_keyword | True |
| 10.1007/s10856-025-06965-5 | Application of chitosan-based nanogels for dermal and transdermal delivery systems. | Journal of Materials Science: Materials in Medicine | 2025 | wrong_api_keyword | True |
| 10.1007/s13346-021-01077-3 | Microneedle-based insulin transdermal delivery system: current status and translation c... | Drug Delivery and Translational Research | 2022 | wrong_method_keyword | True |
| 10.1016/j.ajps.2024.101012 | Deep-insights: Nanoengineered gel-based localized drug delivery for arthritis management. | Asian Journal of Pharmaceutical Sciences | 2025 | wrong_method_keyword | True |
| 10.1016/j.bioactmat.2026.03.054 | Next-generation epidermal patches: Bridging 3D and multidimensional printing for biomed... | Bioactive Materials | 2026 | wrong_method_keyword | True |

This is logged for paper Discussion section. NOT actioned in this window.

## 5. Decision Recommendation

Recommend manually downloading the top 5-15 PDFs from Track A and re-injecting them. This is bounded to a 3-7 day action and may add 15-25 papers to the accessible pool; if internal-factor variation still fails, the negative result becomes a stronger limitations discussion.

RECOMMENDATION: GO-ACCESS | Track A has 209 now-OA/likely-subscribed rescue candidates, while Track B has only 4 high-potential re-extraction targets.
