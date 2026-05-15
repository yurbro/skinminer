# Run Report: run_a6c442d62ea0

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `233`
- Final records evaluated: `233`
- Actually verified: `10`
- Final unresolved: `161`
- Final rejected: `62`

## Route Distribution
- figure: 13
- mixed: 8
- table: 16
- text: 11
- unresolved: 483

## Extractor Outputs
- figure: 16
- table: 220
- text: 11

## Verification Outcomes
- rejected: 62
- unresolved: 161
- verified: 10

## Scope Buckets
- out_of_scope: 49
- recoverable_unresolved: 136
- strict_in_scope: 10
- useful_but_out_of_scope: 38

## Scope Tags
- non_target_api: 49
- recoverable_api_basis: 115
- recoverable_area: 13
- recoverable_endpoint: 12
- recoverable_figure_digitization: 7
- recoverable_support_gap: 75
- recoverable_unit_normalization: 13
- recoverable_unresolved: 136
- useful_api_concentration_out_of_scope: 29
- useful_but_out_of_scope: 38
- useful_device_out_of_scope: 6
- useful_study_type_out_of_scope: 7

## Failure Taxonomy
- ambiguous_api_concentration: 102
- figure_digitization_failed: 7
- insufficient_evidence: 140
- missing_api_concentration: 55
- missing_area: 44
- missing_endpoint: 20
- not_target_api: 49
- not_target_api_concentration: 44
- not_target_device: 6
- not_target_study_type: 20
- percent_only: 19
- unit_normalization_failed: 13

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 25
- figure_digitization_failed: 7
- insufficient_evidence: 24
- missing_api_concentration: 8
- missing_area: 19
- missing_endpoint: 12
- not_target_api: 9
- not_target_api_concentration: 17
- not_target_device: 2
- not_target_study_type: 7
- unit_normalization_failed: 6
### mixed
- ambiguous_api_concentration: 10
- insufficient_evidence: 58
- missing_api_concentration: 30
- missing_endpoint: 8
- not_target_api: 16
- not_target_api_concentration: 22
- not_target_device: 3
- not_target_study_type: 8
- percent_only: 19
- unit_normalization_failed: 7
### table
- ambiguous_api_concentration: 67
- insufficient_evidence: 54
- missing_api_concentration: 17
- missing_area: 25
- not_target_api: 24
- not_target_api_concentration: 5
- not_target_study_type: 5
### text
- insufficient_evidence: 4
- not_target_device: 1

## Figure Stage Counts
- digitization_no_output: 3
- digitized_curves: 9
- digitized_endpoints_failed: 6
- digitized_endpoints_ok: 9
- mapped_curves: 9
- triage_artifacts: 12
- triage_digitize_candidates: 11
- triage_has_permeation_plot_true: 11
- unmapped_curves: 0
- vlm_readings_readable: 18
- vlm_readings_total: 24
- vlm_used_as_final: 13

## Figure Gate Counts
- routed_candidates: 20
- after_gate: 13
- skipped:missing_explicit_figure_signal: 7

## Figure Triage Routes
- digitize: 11
- skip: 1

## Figure Plot Presence
- false: 1
- true: 11

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 2
- recommended_route:skip: 1
- ticks_readable:uncertain: 2
- why_not_digitizable:calibration_curve_not_target: 1

## Figure Digitization Statuses
- digitization_no_output: 3
- fail_missing_axis_range: 3
- ok: 9

## Figure Mapping Statuses
- vision_mapped: 9

## Figure VLM Grounding Statuses
- figure_label_space: 1
- figure_label_space_only: 4
- source_label_space: 16
- ungrounded: 3

## Figure VLM Reconciliation Statuses
- cv_only: 3
- cv_vlm_disagreement: 2
- unreadable: 6
- vlm_only: 13

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 96
- priority_bucket:high: 85
- priority_bucket:medium: 11
- review_focus:api_concentration_basis: 75
- review_focus:diffusion_area: 6
- review_focus:endpoint_value: 12
- review_focus:unit_normalization: 3
- recommended_status:rejected: 7
- recommended_status:unresolved: 89
- disagreement:scope_bucket_disagreement: 7
- disagreement:status_disagreement: 7

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
- downloaded: 223
- resolved: 82
- unresolved: 226
### Access Reasons
- none
### Unresolved Route Reasons
- assuming_relevance_to_ibuprofen_formulations_based_on_title: 1
- content_appears_to_be_a_navigation_or_contact_page_no_evidence_related_to_ibupro: 1
- content_appears_to_be_primarily_a_header_or_introductory_service_page: 1
- content_does_not_provide_sufficient_structured_evidence_for_extraction_further_d: 1
- content_doesn_t_provide_relevant_extractable_evidence_about_ibuprofen_or_drug_de: 1
- content_extraction_is_limited_due_to_the_initial_pages_being_unavailable_further: 1
- content_from_the_first_two_pages_does_not_provide_extractable_evidence: 1
- detailed_extractable_evidence_not_provided_in_the_snippet: 1
- detailed_extraction_not_possible_from_the_provided_segment_as_it_lacks_specific_: 1
- document_appears_to_be_an_article_on_a_zn_based_mof_with_no_direct_mention_of_ib: 1
- document_appears_to_be_generic_content_or_navigation_without_specific_research_d: 1
- document_appears_to_not_contain_relevant_information_for_extraction: 1
- document_content_is_insufficient_for_specific_extraction_details: 1
- document_content_is_not_extractable_from_the_provided_pages: 1
- document_content_lacks_specific_details_for_structured_extraction: 1
- document_does_not_contain_relevant_information_related_to_ibuprofen_or_dermal_fo: 1
- document_does_not_contain_relevant_information_related_to_the_extraction_framewo: 1
- document_primarily_consists_of_webpage_content_and_doesn_t_contain_evidence_rela: 1
- evidence_extraction_not_applicable_insufficient_content: 1
- evidence_extraction_routes_unsure_due_to_insufficient_specific_information_in_th: 1
- extractable_evidence_could_potentially_exist_but_details_are_not_available_in_th: 1
- extractable_evidence_is_limited_and_requires_further_analysis_of_additional_page: 1
- extraction_route_requires_further_detailed_review_of_the_paper_content: 1
- focus_on_an_inhalable_formulation_of_ibuprofen_that_demonstrates_bactericidal_vi: 1
- further_details_needed_for_precise_extraction: 1
- information_on_ibuprofen_and_its_dermal_formulation_is_not_present: 1
- insufficient_content_available_to_determine_extraction_routes: 1
- insufficient_content_for_making_specific_extraction_decisions: 1
- insufficient_data_for_detailed_extraction: 1
- insufficient_details_in_the_provided_text_to_determine_clear_extraction_routes: 1
- insufficient_evidence_in_the_provided_text: 1
- insufficient_information_available_for_detailed_extraction: 1
- insufficient_information_available_from_the_document_provided: 1
- insufficient_information_available_in_the_provided_document_for_extraction: 1
- insufficient_information_available_in_the_provided_document_text: 1
- insufficient_information_available_in_the_provided_text: 1
- insufficient_information_for_extraction: 1
- insufficient_information_from_the_document_to_provide_clear_extraction_routes: 1
- insufficient_information_from_the_provided_text: 1
- insufficient_information_provided_in_the_document_summary: 1
- insufficient_information_to_determine_specific_extraction_details: 1
- missing_structured_and_pdf_router_source: 239
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 63
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- need_to_access_and_analyze_complete_content_for_better_extraction: 1
- no_evidence_extractable_from_the_document_as_content_is_not_provided: 1
- no_evidence_extractable_in_the_given_text: 1
- no_explicit_content_available_for_extraction: 1
- no_explicit_evidence_extractable_further_review_needed_for_detailed_content: 1
- no_extractable_evidence_found_in_provided_text: 3
- no_extractable_evidence_found_in_the_provided_document_text: 1
- no_extractable_evidence_identified_from_provided_text: 1
- no_extractable_evidence_related_to_ibuprofen: 1
- no_extractable_evidence_related_to_ibuprofen_found_in_the_provided_text: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cell: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cells_in_provided_text: 1
- no_information_relevant_to_ibuprofen_or_diffusion_cells_found_in_the_provided_do: 1
- no_relevant_content_available_for_extraction: 1
- no_relevant_data_available_in_the_provided_document: 1
- no_relevant_data_on_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_extractable: 1
- no_relevant_evidence_found_in_the_provided_document: 1
- no_relevant_evidence_found_regarding_ibuprofen_formulations: 1
- no_relevant_evidence_found_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_dermal_formulation: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_on_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_on_ibuprofen_or_diffusion_cell_was_found: 1
- no_relevant_evidence_regarding_ibuprofen_formulations_present: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_in_the_availabl: 1
- no_relevant_evidence_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_relevant_extraction_evidence_found: 1
- no_relevant_extraction_evidence_identified_from_the_document: 1
- no_relevant_extraction_found_in_the_provided_text: 1
- no_relevant_extraction_information_found_in_the_provided_text: 1
- no_relevant_extraction_information_found_related_to_ibuprofen_or_diffusion_cell: 1
- no_relevant_information_available_on_pages_provided: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_diffusion_methodologies: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_diffusion_studies: 1
- no_relevant_information_for_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_on_ibuprofen_or_its_dermal_formulation_found: 1
- no_relevant_information_on_ibuprofen_or_related_diffusion_studies_found_in_the_p: 1
- no_specific_details_about_the_paper_content_are_provided_in_the_source_text: 1
- no_specific_details_are_provided_regarding_diffusion_cells_or_methods: 1
- no_specific_details_regarding_ibuprofen_or_diffusion_cells_were_found_in_the_doc: 1
- no_specific_evidence_extraction_routes_found: 1
- no_specific_evidence_found_related_to_ibuprofen_or_a_diffusion_cell: 1
- no_specific_evidence_on_ibuprofen_or_diffusion_cells_identified: 1
- no_specific_evidence_related_to_ibuprofen_or_diffusion_cells_found_in_the_provid: 1
- no_specific_extractable_evidence_found_in_the_available_text: 1
- no_specific_locators_for_relevant_evidence_identified_further_content_is_require: 1
- only_the_title_indicates_the_use_of_ibuprofen_further_extraction_is_needed_for_m: 1
- paper_focuses_on_molecular_dynamics_and_diffusivity_related_to_cyclodextrin_and_: 1
- source_document_content_does_not_provide_sufficient_evidence_details: 1
- the_content_does_not_provide_relevant_data_for_extraction: 1
- the_document_appears_to_be_a_chapter_in_a_book_with_limited_information_on_ibupr: 1
- the_document_appears_to_be_a_procedural_or_introductory_page_and_does_not_provid: 1
- the_document_appears_to_contain_minimal_extractable_information_regarding_the_re: 1
- the_document_appears_to_discuss_novel_nsaids_and_their_potential_applications_wi: 1
- the_document_contains_navigation_and_technical_information_but_lacks_content_rel: 1
- the_document_contains_no_extractable_evidence_related_to_the_formulation_of_ibup: 1
- the_document_content_appears_limited_and_specific_details_regarding_methods_or_r: 1
- the_document_content_does_not_provide_specific_information_relevant_to_the_extra: 1
- the_document_does_not_contain_extractable_evidence_related_to_ibuprofen_or_diffu: 1
- the_document_does_not_contain_extractable_evidence_related_to_oa_or_ibuprofen_de: 1
- the_document_does_not_contain_relevant_content_on_ibuprofen_or_any_specific_diff: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_formulati: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_any_sp: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_dermal: 1
- the_document_does_not_contain_specific_evidence_related_to_ibuprofen_or_diffusio: 1
- the_document_does_not_include_content_indicating_a_study_on_ibuprofen_or_related: 1
- the_document_does_not_provide_clear_evidence_extraction_opportunities_due_to_lac: 1
- the_document_does_not_provide_clear_evidence_regarding_ibuprofen_or_diffusion_ce: 1
- the_document_does_not_provide_explicit_evidence_for_extraction: 1
- the_document_does_not_provide_extractable_evidence_regarding_ibuprofen_or_relate: 1
- the_document_does_not_provide_information_about_diffusion_cell_experiments_or_en: 1
- the_document_does_not_provide_relevant_information_about_ibuprofen_or_diffusion_: 1
- the_document_does_not_provide_relevant_information_for_extraction_it_appears_to_: 1
- the_document_does_not_provide_specific_evidence_on_ibuprofen_or_related_formulat: 1
- the_document_does_not_provide_specific_evidence_related_to_dermal_formulations_o: 1
- the_document_does_not_provide_sufficient_evidence_regarding_ibuprofen_or_specifi: 1
- the_document_doesn_t_provide_sufficient_information_regarding_ibuprofen_or_any_d: 1
- the_document_lacks_specific_details_related_to_formulations_or_results_that_coul: 1
- the_document_largely_consists_of_navigation_and_does_not_provide_substantial_sci: 1
- the_document_only_contains_a_placeholder_for_the_publisher_s_interface_and_does_: 1
- the_document_primarily_consists_of_page_structure_with_no_extractable_evidence_r: 1
- the_document_primarily_contains_javascript_related_content_and_does_not_provide_: 1
- the_document_primarily_discusses_pharmaceuticals_in_wastewater_and_their_removal: 1
- the_document_primarily_discusses_the_lack_of_analgesic_properties_in_pf_05089771: 1
- the_document_primarily_discusses_the_regulation_of_membrane_associated_serine_pr: 1
- the_document_primarily_focuses_on_biodegradable_subcutaneous_implants_and_does_n: 1
- the_information_provided_does_not_appear_to_relate_specifically_to_ibuprofen_or_: 1
- the_paper_discusses_ibuprofen_as_a_plasticizer_but_does_not_provide_information_: 1
- the_paper_discusses_synergy_with_ibuprofen_but_does_not_focus_on_dermal_applicat: 1
- the_paper_discusses_the_role_of_sodium_coupled_monocarboxylate_transporters_smct: 1
- the_paper_title_suggests_a_focus_on_ibuprofen_in_the_context_of_a_pharmacologica: 1
- the_provided_document_does_not_contain_relevant_information_for_the_oa_only_ibup: 1
- the_study_compares_ibuprofen_diffusion_using_franz_diffusion_cells: 1
- the_text_provided_does_not_contain_sufficient_evidence_for_extraction: 1
- this_document_appears_to_focus_on_the_synthesis_and_functionalization_of_a_metal: 1
- this_document_consists_mainly_of_non_relevant_content_and_does_not_contain_extra: 1
- this_is_the_initial_page_with_no_substantive_content_related_to_the_paper_s_find: 1
- unable_to_extract_specific_information_from_the_provided_text_due_to_lack_of_sub: 1
- uncertain_on_specific_endpoints_and_formulation_details: 1
- unspecified: 36
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
- skipped: 216
#### patch_area
- applied: 7
- skipped: 102
#### patch_endpoint_time
- applied: 72
#### patch_endpoint_value
- applied: 61
- skipped: 135

## Patch Success Counts
- patch_area: 7
- patch_endpoint_time: 72
- patch_endpoint_value: 61