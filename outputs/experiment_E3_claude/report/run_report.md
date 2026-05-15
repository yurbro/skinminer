# Run Report: run_7944dad21a76

- Model: `claude-sonnet-4-6`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'claude-sonnet-4-6', 'routing': 'claude-sonnet-4-6', 'text_extract': 'claude-sonnet-4-6', 'table_extract': 'claude-sonnet-4-6', 'figure_triage': 'claude-sonnet-4-6', 'figure_vlm': 'claude-sonnet-4-6', 'figure_map': 'claude-sonnet-4-6', 'llm_adjudicate': 'claude-sonnet-4-6'}`
- Assembled records: `72`
- Final records evaluated: `72`
- Actually verified: `0`
- Final unresolved: `62`
- Final rejected: `10`

## Route Distribution
- figure: 8
- mixed: 3
- table: 2
- text: 2
- unresolved: 201

## Extractor Outputs
- figure: 2
- table: 77
- text: 1

## Verification Outcomes
- rejected: 10
- unresolved: 62

## Scope Buckets
- recoverable_unresolved: 60
- useful_but_out_of_scope: 12

## Scope Tags
- recoverable_api_basis: 41
- recoverable_area: 1
- recoverable_endpoint: 6
- recoverable_figure_digitization: 6
- recoverable_mapping: 2
- recoverable_source_context: 21
- recoverable_support_gap: 9
- recoverable_unit_normalization: 3
- recoverable_unresolved: 60
- useful_api_concentration_out_of_scope: 2
- useful_but_out_of_scope: 12
- useful_device_out_of_scope: 3
- useful_endpoint_out_of_scope: 3
- useful_study_type_out_of_scope: 7

## Failure Taxonomy
- ambiguous_api_concentration: 49
- ambiguous_mapping: 2
- figure_digitization_failed: 6
- insufficient_evidence: 9
- missing_api_concentration: 2
- missing_area: 1
- missing_endpoint: 6
- not_target_api_concentration: 2
- not_target_device: 3
- not_target_study_type: 7
- percent_only: 7
- source_context_inconsistent: 24
- unit_normalization_failed: 3

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 14
- ambiguous_mapping: 2
- figure_digitization_failed: 6
- insufficient_evidence: 6
- missing_api_concentration: 2
- missing_area: 1
- missing_endpoint: 6
- not_target_device: 3
- percent_only: 3
- source_context_inconsistent: 24
- unit_normalization_failed: 3
### mixed
- ambiguous_api_concentration: 7
- insufficient_evidence: 3
- not_target_api_concentration: 2
- not_target_study_type: 7
### table
- ambiguous_api_concentration: 28
- percent_only: 4

## Figure Stage Counts
- digitization_no_output: 0
- digitized_curves: 4
- digitized_endpoints_failed: 0
- digitized_endpoints_ok: 4
- mapped_curves: 4
- triage_artifacts: 9
- triage_digitize_candidates: 2
- triage_has_permeation_plot_true: 2
- unmapped_curves: 0
- vlm_readings_readable: 4
- vlm_readings_total: 4
- vlm_used_as_final: 0

## Figure Gate Counts
- routed_candidates: 11
- after_gate: 11

## Figure Triage Routes
- digitize: 2
- skip: 7

## Figure Plot Presence
- false: 7
- true: 2

## Figure Triage Signals
- digitizable:no: 7
- digitizable:uncertain: 1
- endpoint_curve_present:no: 7
- recommended_route:skip: 7
- ticks_readable:no: 6
- why_not_digitizable:figure_1_contains_only_photographs_of_microneedle_roller_equipment_and_applicati: 1
- why_not_digitizable:page_23_figure_1_is_a_schematic_flow_diagram_showing_study_design_timelines_form: 1
- why_not_digitizable:page_2_contains_characterization_figures_chemical_structure_particle_size_distri: 1
- why_not_digitizable:page_3_contains_only_schematic_illustrations_figure_1_and_figure_2_depicting_mic: 1
- why_not_digitizable:page_6_fig_1_contains_only_cad_microscopy_images_of_3d_printed_microneedle_struc: 1
- why_not_digitizable:page_contains_only_chemical_structure_diagrams_and_a_physicochemical_parameters_: 1
- why_not_digitizable:page_contains_only_text_and_chemical_structure_diagrams_figure_1_repeating_units: 1

## Figure Digitization Statuses
- ok: 4

## Figure Mapping Statuses
- vision_mapped: 4

## Figure VLM Grounding Statuses
- figure_label_space: 4

## Figure VLM Reconciliation Statuses
- cv_vlm_agree: 2
- cv_vlm_disagreement: 2

## LLM Reliability
### detection.router
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 55
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.table
- api_failures: 0
- attempt_failures: 1
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 8
- retried_requests: 0
- retries_attempted: 1
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 1
- transport_failures: 0
### triage.llm_triage
- api_failures: 0
- attempt_failures: 23
- auth_failures: 0
- final_failures: 3
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 726
- retried_requests: 1
- retries_attempted: 20
- retry_successes: 1
- schema_validation_failures: 23
- timeout_failures: 0
- transport_failures: 0

## LLM Adjudication Audit
- rows: 0
- priority_bucket:none
- review_focus:none
- none
- disagreement:none

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
- downloaded: 52
- resolved: 37
- unresolved: 127
### Access Reasons
- none
### Unresolved Route Reasons
- document_appears_to_be_a_book_chapter_on_microneedle_iontophoresis_combinations_: 1
- document_content_is_only_europe_pmc_navigation_ui_text_with_no_actual_paper_body: 1
- document_failed_to_load_only_a_hhs_vulnerability_disclosure_page_was_returned_th: 1
- document_text_appears_to_be_only_a_europe_pmc_navigation_interface_page_with_no_: 1
- document_text_is_almost_entirely_a_europe_pmc_navigation_ui_page_with_no_article: 1
- document_text_is_almost_entirely_europe_pmc_navigation_ui_boilerplate_the_title_: 1
- document_text_is_incomplete_only_europe_pmc_navigation_menu_pages_were_captured_: 1
- document_text_is_only_a_europe_pmc_navigation_interface_page_with_no_scientific_: 1
- document_text_is_only_europe_pmc_navigation_header_pages_with_no_scientific_cont: 1
- document_text_is_only_europe_pmc_navigation_interface_pages_with_no_actual_paper: 1
- document_text_is_only_europe_pmc_navigation_ui_boilerplate_with_no_paper_content: 1
- document_text_is_only_europe_pmc_navigation_ui_pages_with_no_actual_paper_conten: 1
- document_text_is_only_the_europe_pmc_navigation_header_page_with_no_article_cont: 1
- document_text_is_only_the_europe_pmc_navigation_header_pages_with_no_actual_pape: 1
- document_text_is_only_the_europe_pmc_navigation_ui_pages_with_no_actual_paper_co: 1
- document_text_is_truncated_to_only_europe_pmc_navigation_ui_pages_pages_1_2_no_a: 1
- document_text_is_truncated_to_only_the_europe_pmc_navigation_header_pages_no_act: 1
- document_text_not_supplied_beyond_page_1_placeholder_title_indicates_comparison_: 1
- document_text_only_contains_europe_pmc_navigation_ui_boilerplate_no_scientific_c: 2
- document_text_only_contains_europe_pmc_navigation_ui_boilerplate_with_no_actual_: 1
- full_paper_text_not_retrieved_only_europe_pmc_navigation_pages_were_supplied_pap: 1
- missing_structured_and_pdf_router_source: 132
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 29
- only_ethos_landing_page_content_retrieved_full_thesis_text_unavailable_due_to_po: 1
- only_europe_pmc_navigation_landing_page_content_was_retrieved_no_actual_paper_bo: 1
- only_europe_pmc_navigation_pages_were_retrieved_no_actual_paper_content_is_avail: 1
- only_europe_pmc_navigation_pages_were_supplied_the_actual_article_body_was_not_r: 1
- only_page_1_placeholder_was_provided_no_substantive_text_extracted_title_mention: 1
- the_document_content_is_inaccessible_only_the_ethos_portal_landing_page_is_retur: 1
- the_document_text_only_contains_europe_pmc_navigation_ui_boilerplate_and_does_no: 1
- the_document_text_only_contains_europe_pmc_navigation_ui_elements_and_no_actual_: 4
- the_document_text_retrieved_is_only_the_europe_pmc_navigation_header_pages_and_d: 1
- the_pdf_appears_to_have_only_rendered_the_europe_pmc_navigation_ui_pages_rather_: 1
- the_pdf_only_rendered_europe_pmc_navigation_interface_pages_pages_1_2_no_actual_: 1
- the_supplied_document_text_contains_only_europe_pmc_navigation_ui_boilerplate_ac: 2
- the_supplied_document_text_contains_only_europe_pmc_navigation_ui_boilerplate_an: 2
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
- skipped: 62
#### patch_area
- skipped: 7
#### patch_endpoint_time
- applied: 21
#### patch_endpoint_value
- applied: 43
- skipped: 39

## Patch Success Counts
- patch_endpoint_time: 21
- patch_endpoint_value: 43