# Run Report: run_7d4793100498

- Model: `claude-sonnet-4-6`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'claude-sonnet-4-6', 'routing': 'claude-sonnet-4-6', 'text_extract': 'claude-sonnet-4-6', 'table_extract': 'claude-sonnet-4-6', 'figure_triage': 'claude-sonnet-4-6', 'figure_vlm': 'claude-sonnet-4-6', 'figure_map': 'claude-sonnet-4-6', 'llm_adjudicate': 'claude-sonnet-4-6'}`
- Assembled records: `93`
- Final records evaluated: `93`
- Actually verified: `0`
- Final unresolved: `83`
- Final rejected: `10`

## Route Distribution
- figure: 7
- mixed: 5
- table: 2
- text: 3
- unresolved: 203

## Extractor Outputs
- figure: 1
- table: 87
- text: 5

## Verification Outcomes
- rejected: 10
- unresolved: 83

## Scope Buckets
- recoverable_unresolved: 83
- useful_but_out_of_scope: 10

## Scope Tags
- recoverable_api_basis: 49
- recoverable_area: 1
- recoverable_endpoint: 6
- recoverable_endpoint_time: 1
- recoverable_figure_digitization: 4
- recoverable_mapping: 1
- recoverable_source_context: 26
- recoverable_support_gap: 15
- recoverable_unresolved: 83
- useful_but_out_of_scope: 10
- useful_study_type_out_of_scope: 10

## Failure Taxonomy
- ambiguous_api_concentration: 53
- ambiguous_mapping: 1
- figure_digitization_failed: 4
- insufficient_evidence: 16
- missing_api_concentration: 6
- missing_area: 3
- missing_endpoint: 6
- missing_endpoint_time: 1
- not_target_study_type: 10
- percent_only: 7
- source_context_inconsistent: 26

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 5
- ambiguous_mapping: 1
- figure_digitization_failed: 4
- insufficient_evidence: 1
- missing_api_concentration: 4
- missing_area: 1
- missing_endpoint: 4
- percent_only: 3
- source_context_inconsistent: 26
### mixed
- ambiguous_api_concentration: 20
- insufficient_evidence: 14
- missing_area: 2
- not_target_study_type: 10
### table
- ambiguous_api_concentration: 28
- percent_only: 4
### text
- insufficient_evidence: 1
- missing_api_concentration: 2
- missing_endpoint: 2
- missing_endpoint_time: 1

## Figure Stage Counts
- digitization_no_output: 0
- digitized_curves: 4
- digitized_endpoints_failed: 0
- digitized_endpoints_ok: 4
- mapped_curves: 1
- triage_artifacts: 7
- triage_digitize_candidates: 1
- triage_has_permeation_plot_true: 1
- unmapped_curves: 3
- vlm_readings_readable: 4
- vlm_readings_total: 4
- vlm_used_as_final: 4

## Figure Gate Counts
- routed_candidates: 12
- after_gate: 8
- skipped:missing_explicit_figure_signal: 4

## Figure Triage Routes
- digitize: 1
- skip: 6

## Figure Plot Presence
- false: 6
- true: 1

## Figure Triage Signals
- digitizable:no: 6
- endpoint_curve_present:no: 5
- endpoint_curve_present:uncertain: 1
- recommended_route:skip: 6
- ticks_readable:no: 4
- why_not_digitizable:figure_2d_is_a_bar_chart_discrete_time_points_1_h_24_h_10_days_showing_apparent_: 1
- why_not_digitizable:page_3_contains_only_schematic_diagrams_figure_1_and_figure_2_illustrating_micro: 1
- why_not_digitizable:page_contains_only_a_schematic_diagram_figure_4_of_the_diffusion_cell_measuremen: 1
- why_not_digitizable:page_contains_only_chemical_structure_diagrams_locust_bean_gum_xanthan_tween_20_: 1
- why_not_digitizable:this_is_a_particle_size_distribution_plot_intensity_vs_size_not_a_transdermal_pe: 1
- why_not_digitizable:this_is_a_schematic_protocol_diagram_figure_1_showing_study_design_timelines_not: 1

## Figure Digitization Statuses
- ok: 4

## Figure Mapping Statuses
- unmapped: 3
- vision_mapped: 1

## Figure VLM Grounding Statuses
- figure_label_space_only: 4

## Figure VLM Reconciliation Statuses
- vlm_only: 4

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 48
- priority_bucket:high: 44
- priority_bucket:medium: 4
- review_focus:api_concentration_basis: 43
- review_focus:diffusion_area: 1
- review_focus:endpoint_value: 4
- recommended_status:rejected: 48
- disagreement:scope_bucket_disagreement: 48
- disagreement:status_disagreement: 48

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-04-06.v1
- extractors.figure.vlm_digitize: 2026-04-11.v1
- extractors.table.structured_tables: 2026-04-11.v1
- extractors.text.structured_fields: 2026-04-11.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1
- verification.llm_adjudication: 2026-04-03.v1

## Blockage Summary
### Access Statuses
- downloaded: 87
- error: 5
- unresolved: 128
### Access Reasons
- failed_download_pdf: 10
- seed_pdf_url_from_metadata: 2
### Unresolved Route Reasons
- document_appears_to_be_a_book_chapter_methods_in_molecular_biology_series_on_mic: 1
- document_appears_to_be_a_europe_pmc_navigation_interface_page_with_no_substantiv: 1
- document_content_is_essentially_a_landing_stub_page_for_the_ethos_british_librar: 1
- document_text_is_almost_entirely_absent_only_page_1_header_metadata_visible_the_: 1
- document_text_is_almost_entirely_europe_pmc_navigation_ui_boilerplate_no_scienti: 1
- document_text_is_essentially_just_the_europe_pmc_navigation_header_pages_with_no: 1
- document_text_is_incomplete_only_europe_pmc_navigation_header_pages_were_capture: 1
- document_text_is_incomplete_only_europe_pmc_navigation_ui_pages_were_captured_no: 1
- document_text_is_only_a_europe_pmc_navigation_landing_page_with_no_article_conte: 2
- document_text_is_only_a_europe_pmc_navigation_ui_page_with_no_article_content_th: 1
- document_text_is_only_europe_pmc_navigation_interface_pages_with_no_scientific_c: 1
- document_text_is_only_europe_pmc_navigation_ui_boilerplate_no_paper_content_was_: 1
- document_text_is_only_europe_pmc_navigation_ui_boilerplate_with_no_actual_paper_: 3
- document_text_is_only_navigation_ui_content_from_europe_pmc_website_no_actual_pa: 1
- document_text_is_only_the_europe_pmc_navigation_header_pages_with_no_actual_pape: 1
- document_text_is_only_the_europe_pmc_navigation_landing_page_interface_no_actual: 1
- document_text_is_only_the_europe_pmc_navigation_ui_pages_no_actual_paper_content: 1
- document_text_is_truncated_to_navigation_ui_elements_from_europe_pmc_website_no_: 1
- document_text_not_supplied_beyond_title_title_indicates_comparison_of_regenerate: 1
- document_text_only_contains_europe_pmc_navigation_interface_content_the_actual_p: 1
- document_text_only_contains_europe_pmc_navigation_ui_boilerplate_and_the_article: 1
- document_text_only_contains_europe_pmc_navigation_ui_boilerplate_no_actual_paper: 1
- document_text_only_contains_europe_pmc_navigation_ui_boilerplate_with_no_actual_: 3
- document_text_only_contains_europe_pmc_navigation_ui_content_no_paper_body_was_r: 1
- missing_structured_and_pdf_router_source: 133
- missing_structured_and_pdf_router_source_blocked_html_local_captcha_blocked_html: 29
- only_europe_pmc_navigation_header_content_was_retrieved_from_the_pdf_no_actual_p: 1
- only_europe_pmc_navigation_header_pages_were_retrieved_no_full_article_content_i: 1
- only_europe_pmc_navigation_ui_pages_were_captured_no_actual_paper_content_is_ava: 1
- only_europe_pmc_navigation_ui_pages_were_captured_the_actual_paper_content_about: 1
- only_the_europe_pmc_navigation_header_pages_were_captured_in_the_pdf_extract_the: 1
- the_document_text_only_contains_europe_pmc_navigation_interface_boilerplate_with: 1
- the_document_text_only_contains_europe_pmc_navigation_ui_elements_and_no_actual_: 1
- the_document_text_only_contains_europe_pmc_website_navigation_ui_elements_and_no: 1
- the_document_text_retrieved_is_only_the_europe_pmc_navigation_header_pages_and_d: 1
- the_html_document_only_contains_ethos_database_metadata_and_a_notice_about_a_cyb: 1
- the_pdf_appears_to_have_only_rendered_the_europe_pmc_navigation_header_pages_wit: 1
- the_supplied_document_text_contains_only_europe_pmc_navigation_ui_boilerplate_ac: 1
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
- skipped: 73
#### patch_area
- skipped: 11
#### patch_endpoint_time
- applied: 19
- skipped: 1
#### patch_endpoint_value
- applied: 47
- skipped: 43

## Patch Success Counts
- patch_endpoint_time: 19
- patch_endpoint_value: 47