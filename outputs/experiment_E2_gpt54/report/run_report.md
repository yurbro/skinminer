# Run Report: run_66124c59c30d

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-5.4-mini', 'routing': 'gpt-5.4-mini', 'text_extract': 'gpt-5.4-mini', 'table_extract': 'gpt-5.4-mini', 'figure_triage': 'gpt-5.4-mini', 'figure_vlm': 'gpt-5.4', 'figure_map': 'gpt-5.4-mini', 'llm_adjudicate': 'gpt-5.4-mini'}`
- Assembled records: `61`
- Final records evaluated: `61`
- Actually verified: `4`
- Final unresolved: `47`
- Final rejected: `10`

## Route Distribution
- figure: 3
- mixed: 10
- table: 6
- text: 10
- unresolved: 238

## Extractor Outputs
- figure: 4
- table: 70
- text: 7

## Verification Outcomes
- rejected: 10
- unresolved: 47
- verified: 4

## Scope Buckets
- out_of_scope: 7
- recoverable_unresolved: 46
- strict_in_scope: 4
- useful_but_out_of_scope: 4

## Scope Tags
- non_target_api: 7
- recoverable_api_basis: 25
- recoverable_area: 14
- recoverable_endpoint: 3
- recoverable_figure_digitization: 1
- recoverable_mapping: 1
- recoverable_support_gap: 21
- recoverable_unit_normalization: 9
- recoverable_unresolved: 46
- useful_api_concentration_out_of_scope: 1
- useful_but_out_of_scope: 4
- useful_endpoint_out_of_scope: 1
- useful_study_type_out_of_scope: 3

## Failure Taxonomy
- ambiguous_api_concentration: 23
- ambiguous_mapping: 1
- figure_digitization_failed: 1
- insufficient_evidence: 24
- missing_api_concentration: 9
- missing_area: 20
- missing_endpoint: 3
- not_target_api: 7
- not_target_api_concentration: 3
- not_target_study_type: 3
- percent_only: 4
- unit_normalization_failed: 9

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 3
- ambiguous_mapping: 1
- missing_area: 3
### mixed
- ambiguous_api_concentration: 15
- figure_digitization_failed: 1
- insufficient_evidence: 20
- missing_api_concentration: 1
- missing_area: 14
- missing_endpoint: 3
- not_target_api: 5
- not_target_api_concentration: 3
- percent_only: 3
- unit_normalization_failed: 9
### table
- ambiguous_api_concentration: 5
- insufficient_evidence: 2
- missing_api_concentration: 8
- missing_area: 3
- not_target_api: 2
- not_target_study_type: 3
### text
- insufficient_evidence: 2
- percent_only: 1

## Figure Stage Counts
- digitization_no_output: 2
- digitized_curves: 7
- digitized_endpoints_failed: 2
- digitized_endpoints_ok: 7
- mapped_curves: 7
- triage_artifacts: 7
- triage_digitize_candidates: 4
- triage_has_permeation_plot_true: 4
- unmapped_curves: 0
- vlm_readings_readable: 7
- vlm_readings_total: 7
- vlm_used_as_final: 3

## Figure Gate Counts
- routed_candidates: 13
- after_gate: 8
- skipped:low_route_confidence: 1
- skipped:missing_explicit_figure_signal: 4

## Figure Triage Routes
- digitize: 4
- skip: 3

## Figure Plot Presence
- false: 3
- true: 4

## Figure Triage Signals
- digitizable:no: 3
- endpoint_curve_present:no: 1
- recommended_route:skip: 3
- why_not_digitizable:calibration_curve_not_target: 2
- why_not_digitizable:selected_page_contains_fig_4_a_grouped_bar_chart_with_error_bars_rather_than_an_: 1

## Figure Digitization Statuses
- digitization_no_output: 2
- ok: 7

## Figure Mapping Statuses
- vision_mapped: 7

## Figure VLM Grounding Statuses
- figure_label_space: 4
- figure_label_space_only: 3

## Figure VLM Reconciliation Statuses
- cv_vlm_agree: 1
- cv_vlm_disagreement: 3
- vlm_only: 3

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 28
- priority_bucket:high: 17
- priority_bucket:medium: 11
- review_focus:api_concentration_basis: 16
- review_focus:diffusion_area: 4
- review_focus:endpoint_value: 1
- review_focus:unit_normalization: 7
- recommended_status:rejected: 18
- recommended_status:unresolved: 2
- recommended_status:verified: 8
- disagreement:scope_bucket_disagreement: 28
- disagreement:status_disagreement: 26

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-04-06.v1
- extractors.figure.vlm_digitize: 2026-04-08.v2
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1
- verification.llm_adjudication: 2026-04-03.v1

## Blockage Summary
### Access Statuses
- downloaded: 85
- resolved: 40
- unresolved: 142
### Access Reasons
- none
### Unresolved Route Reasons
- cochrane_review_title_indicates_a_review_article_about_topical_agents_or_dressin: 1
- missing_structured_and_pdf_router_source: 147
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 31
- only_bibliographic_ethos_update_text_was_supplied_but_the_title_clearly_indicate: 1
- only_europe_pmc_boilerplate_is_visible_in_the_supplied_pages_no_article_body_tab: 1
- only_europe_pmc_boilerplate_navigation_was_provided_for_the_pdf_pages_no_article: 1
- only_europe_pmc_boilerplate_pages_are_present_in_the_supplied_text_no_article_co: 1
- only_europe_pmc_landing_page_boilerplate_is_present_in_the_supplied_text_no_arti: 3
- only_europe_pmc_landing_page_boilerplate_was_supplied_no_article_content_methods: 1
- only_europe_pmc_landing_page_navigation_text_is_present_in_the_supplied_pdf_text: 1
- only_europe_pmc_landing_page_text_is_visible_in_the_supplied_pdf_extract_not_the: 1
- only_europe_pmc_landing_page_text_was_supplied_not_the_article_content_no_extrac: 1
- only_europe_pmc_site_boilerplate_is_present_in_the_supplied_pdf_text_no_article_: 1
- only_europe_pmc_site_navigation_text_is_available_in_the_provided_pdf_pages_the_: 1
- only_europe_pmc_wrapper_landing_text_is_present_in_the_supplied_pdf_pages_no_art: 1
- only_europe_pmc_wrapper_text_is_present_in_the_supplied_pdf_pages_the_article_co: 1
- only_europe_pmc_wrapper_text_was_supplied_not_the_article_content_ibuprofen_is_c: 1
- only_front_matter_europe_pmc_boilerplate_is_visible_in_the_supplied_pages_so_ext: 1
- only_front_matter_europe_pmc_navigation_text_was_supplied_no_abstract_methods_ta: 1
- only_the_europe_pmc_landing_page_text_is_visible_in_the_supplied_pdf_text_no_art: 1
- only_the_first_page_indicator_was_supplied_and_no_readable_article_text_was_incl: 1
- only_the_title_and_europe_pmc_boilerplate_are_visible_in_the_supplied_text_the_t: 1
- only_the_title_header_snippet_was_supplied_paper_is_a_primary_experimental_percu: 1
- only_the_title_page_was_supplied_the_title_strongly_indicates_an_in_vitro_permea: 1
- supplied_pdf_text_appears_to_be_europe_pmc_landing_navigation_content_only_not_t: 1
- supplied_pdf_text_is_not_the_article_content_only_europe_pmc_boilerplate_navigat: 1
- supplied_pdf_text_is_only_europe_pmc_navigation_landing_page_content_not_the_art: 1
- supplied_pdf_text_is_only_europe_pmc_site_boilerplate_navigation_not_article_con: 1
- supplied_text_appears_to_be_only_europe_pmc_webpage_boilerplate_for_the_article_: 1
- supplied_text_contains_only_europe_pmc_navigation_landing_page_content_and_no_ar: 1
- supplied_text_contains_only_europe_pmc_navigation_notice_pages_and_no_article_co: 1
- supplied_text_only_contains_europe_pmc_boilerplate_navigation_pages_not_the_arti: 1
- the_supplied_html_is_only_an_ethos_catalog_update_page_not_the_thesis_content_no: 1
- the_supplied_pdf_text_appears_to_be_only_europe_pmc_boilerplate_navigation_pages: 1
- the_supplied_pdf_text_appears_to_be_only_europe_pmc_header_navigation_pages_not_: 1
- the_supplied_pdf_text_appears_to_be_only_europe_pmc_landing_page_boilerplate_for: 1
- the_supplied_pdf_text_appears_to_contain_only_europe_pmc_webpage_boilerplate_for: 1
- the_supplied_pdf_text_appears_to_contain_only_europe_pmc_wrapper_boilerplate_pag: 1
- the_supplied_pdf_text_contains_only_europe_pmc_boilerplate_pages_and_no_article_: 1
- the_supplied_pdf_text_is_just_europe_pmc_page_chrome_boilerplate_and_does_not_in: 1
- the_supplied_pdf_text_is_only_europe_pmc_boilerplate_and_the_article_title_ibupr: 1
- the_supplied_pdf_text_is_only_europe_pmc_navigation_placeholder_content_from_pag: 1
- the_supplied_pdf_text_only_contains_europe_pmc_boilerplate_header_content_and_no: 1
- the_supplied_pdf_text_only_contains_europe_pmc_interface_boilerplate_on_pages_1_: 1
- the_supplied_text_appears_to_be_europe_pmc_navigation_header_content_rather_than: 1
- the_supplied_text_appears_to_be_only_europe_pmc_page_header_content_and_does_not: 1
- the_supplied_text_appears_to_be_only_europe_pmc_pdf_wrapper_pages_and_not_the_ar: 1
- the_supplied_text_contains_only_europe_pmc_navigation_page_boilerplate_not_the_a: 1
- the_supplied_text_contains_only_europe_pmc_site_boilerplate_and_no_article_conte: 1
- the_supplied_text_is_only_europe_pmc_boilerplate_navigation_and_does_not_include: 1
- the_supplied_text_is_only_europe_pmc_boilerplate_navigation_pages_not_the_articl: 1
- the_supplied_text_is_only_europe_pmc_navigation_landing_page_content_not_the_art: 1
- the_supplied_text_is_only_europe_pmc_pdf_wrapper_pages_and_does_not_include_arti: 1
- the_supplied_text_is_only_front_matter_contents_for_a_book_chapter_and_does_not_: 1
- the_supplied_text_only_contains_europe_pmc_webpage_boilerplate_and_no_article_co: 1
- the_title_indicates_a_synthesis_formulation_focused_article_on_ibuprofenates_but: 1
- title_and_available_text_indicate_an_ibuprofen_materials_surface_morphology_pape: 1
- title_explicitly_states_comparative_study_of_transmembrane_diffusion_and_permeat: 1
- title_indicates_a_review_style_article_about_cutaneous_administration_and_drug_d: 1
- title_indicates_an_experimental_paper_on_polymer_ibuprofen_sodium_silica_gel_com: 1
### Extractor Source / Error Blockages
#### table
- status:none
- error_type:none
- source_backend:none
#### text
- status:none
- error_type:none
- source_backend:none
### Patch Statuses
#### patch_api_concentration
- skipped: 54
#### patch_area
- applied: 1
- skipped: 37
#### patch_endpoint_time
- applied: 21
#### patch_endpoint_value
- applied: 30
- skipped: 30

## Patch Success Counts
- patch_area: 1
- patch_endpoint_time: 21
- patch_endpoint_value: 30