# Run Report: run_a2cf65651c54

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `279`
- Final records evaluated: `279`
- Actually verified: `9`
- Final unresolved: `171`
- Final rejected: `99`

## Route Distribution
- figure: 19
- mixed: 9
- table: 19
- text: 8
- unresolved: 475

## Extractor Outputs
- figure: 14
- table: 279
- text: 16

## Verification Outcomes
- rejected: 99
- unresolved: 171
- verified: 9

## Scope Buckets
- out_of_scope: 44
- recoverable_unresolved: 145
- strict_in_scope: 9
- useful_but_out_of_scope: 81

## Scope Tags
- non_target_api: 44
- recoverable_api_basis: 100
- recoverable_area: 23
- recoverable_endpoint: 21
- recoverable_endpoint_time: 1
- recoverable_figure_digitization: 5
- recoverable_source_context: 33
- recoverable_support_gap: 84
- recoverable_unresolved: 145
- useful_api_concentration_out_of_scope: 37
- useful_but_out_of_scope: 81
- useful_device_out_of_scope: 23
- useful_endpoint_out_of_scope: 1
- useful_study_type_out_of_scope: 32

## Failure Taxonomy
- ambiguous_api_concentration: 106
- figure_digitization_failed: 5
- insufficient_evidence: 162
- missing_api_concentration: 66
- missing_area: 61
- missing_endpoint: 37
- missing_endpoint_time: 1
- not_target_api: 44
- not_target_api_concentration: 51
- not_target_device: 34
- not_target_study_type: 46
- percent_only: 23
- source_context_inconsistent: 88
- unit_normalization_failed: 22

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 41
- figure_digitization_failed: 5
- insufficient_evidence: 73
- missing_api_concentration: 11
- missing_area: 32
- missing_endpoint: 20
- not_target_api: 23
- not_target_api_concentration: 30
- not_target_device: 22
- not_target_study_type: 15
- source_context_inconsistent: 88
- unit_normalization_failed: 7
### mixed
- ambiguous_api_concentration: 10
- insufficient_evidence: 36
- missing_api_concentration: 28
- missing_area: 18
- missing_endpoint: 16
- not_target_api: 18
- not_target_api_concentration: 10
- not_target_device: 4
- not_target_study_type: 19
- unit_normalization_failed: 7
### table
- ambiguous_api_concentration: 55
- insufficient_evidence: 51
- missing_api_concentration: 27
- missing_area: 11
- not_target_api: 3
- not_target_api_concentration: 11
- not_target_device: 8
- not_target_study_type: 12
- percent_only: 23
- unit_normalization_failed: 8
### text
- insufficient_evidence: 2
- missing_endpoint: 1
- missing_endpoint_time: 1

## Figure Stage Counts
- digitization_no_output: 4
- digitized_curves: 22
- digitized_endpoints_failed: 6
- digitized_endpoints_ok: 22
- mapped_curves: 11
- triage_artifacts: 19
- triage_digitize_candidates: 15
- triage_has_permeation_plot_true: 15
- unmapped_curves: 11
- vlm_readings_readable: 22
- vlm_readings_total: 33
- vlm_used_as_final: 18

## Figure Gate Counts
- routed_candidates: 28
- after_gate: 20
- skipped:missing_explicit_figure_signal: 8

## Figure Triage Routes
- digitize: 15
- skip: 4

## Figure Plot Presence
- false: 4
- true: 15

## Figure Triage Signals
- digitizable:no: 3
- endpoint_curve_present:no: 5
- recommended_route:skip: 4
- ticks_readable:no: 3
- ticks_readable:uncertain: 5
- why_not_digitizable:figure_does_not_contain_any_curves_or_endpoints_related_to_ibuprofen: 1
- why_not_digitizable:no_relevant_figure_or_data_provided_in_the_input_image: 1
- why_not_digitizable:the_plot_lacks_clear_axis_labels_and_numerical_values_preventing_precise_digitiz: 1

## Figure Digitization Statuses
- digitization_no_output: 4
- fail_missing_axis_range: 2
- ok: 22

## Figure Mapping Statuses
- underconstrained_labels: 11
- vision_mapped: 11

## Figure VLM Grounding Statuses
- figure_label_space_only: 16
- source_label_space: 17

## Figure VLM Reconciliation Statuses
- cv_vlm_disagreement: 4
- unreadable: 11
- vlm_only: 18

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 97
- priority_bucket:high: 70
- priority_bucket:medium: 27
- review_focus:api_concentration_basis: 67
- review_focus:diffusion_area: 12
- review_focus:endpoint_value: 18
- recommended_status:rejected: 19
- recommended_status:unresolved: 78
- disagreement:scope_bucket_disagreement: 18
- disagreement:status_disagreement: 19

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
- downloaded: 292
- error: 14
- unresolved: 224
### Access Reasons
- failed_download_html: 1
- failed_download_pdf: 25
- resolve_error_connectionerror: 1
- seed_pdf_url_from_metadata: 7
### Unresolved Route Reasons
- case_report_of_kounis_syndrome_with_ibuprofen_implicated: 1
- content_does_not_appear_to_be_relevant_to_ibuprofen_dermal_formulation: 1
- content_does_not_provide_clear_evidence_for_any_specific_extraction_or_analysis: 1
- content_extraction_not_possible_from_the_provided_text: 1
- content_from_the_document_extracted_indicates_that_information_is_related_to_in_: 1
- document_contains_no_relevant_content_to_extract_evidence_regarding_ibuprofen_or: 1
- document_content_does_not_provide_specific_information_to_determine_extraction_r: 1
- document_content_refers_primarily_to_the_structure_of_the_pdf_without_specific_d: 1
- document_does_not_provide_sufficient_information_for_extraction: 1
- document_not_fully_extracted_no_structured_evidence_from_the_visible_text: 1
- document_primarily_contains_metadata_with_no_extractable_evidence: 1
- evidence_extraction_requires_further_text_analysis: 1
- extractable_evidence_not_found_in_the_provided_text: 1
- extraction_route_cannot_be_definitively_determined_with_provided_information: 1
- extraction_route_remains_unclear_without_additional_context_from_the_paper: 1
- focuses_on_the_validation_of_franz_diffusion_cell_system_for_drug_permeation_stu: 1
- full_details_about_endpoints_and_formulations_are_not_visible_in_the_current_tex: 1
- further_details_may_require_review_of_supplementary_materials_or_figures: 1
- initial_content_indicates_membrand_interaction_but_lacks_clear_structured_eviden: 1
- initial_pages_do_not_provide_detailed_evidence_or_structured_data_related_to_der: 1
- initial_pages_do_not_provide_relevant_content_or_evidence: 1
- insufficient_content_available_to_extract_relevant_evidence: 1
- insufficient_detail_available_in_the_provided_text: 1
- insufficient_detail_provided_in_the_extractable_evidence: 1
- insufficient_extractable_evidence_from_provided_document_text: 1
- insufficient_extractable_evidence_in_the_provided_text: 1
- insufficient_extractable_evidence_related_to_ibuprofen_formulation: 1
- insufficient_information_available_from_the_document_to_determine_evidence_extra: 1
- insufficient_information_available_from_the_provided_text: 1
- insufficient_information_available_in_the_provided_document: 1
- insufficient_information_extracted_from_the_document: 1
- insufficient_information_for_extraction: 1
- insufficient_information_in_document_snippet: 1
- insufficient_information_in_the_provided_text: 2
- insufficient_information_on_extraction_routes_from_the_present_document: 1
- insufficient_information_provided_in_the_document_to_make_definitive_conclusions: 1
- insufficient_information_to_extract_evidence_related_to_ibuprofen_or_dermal_form: 1
- insufficient_text_provided_to_identify_extraction_routes_or_details: 1
- lacks_specific_information_about_ibuprofen_diffusion_cell_and_endpoints: 1
- missing_structured_and_pdf_router_source: 237
- missing_structured_and_pdf_router_source_blocked_html_local_captcha_blocked_html: 64
- missing_structured_and_pdf_router_source_html_remote_httperror: 1
- no_actionable_content_available_only_a_notification_regarding_javascript_use_on_: 1
- no_concrete_evidence_regarding_ibuprofen_or_diffusion_cell_found_in_the_provided: 1
- no_detailed_content_provided_for_insights_on_methodologies_or_results: 1
- no_evidence_of_ibuprofen_or_diffusion_cell_mentioned_in_the_provided_text: 1
- no_explicit_extractable_evidence_found_on_this_page: 1
- no_explicit_formulation_or_endpoint_data_identified_in_extracted_text: 1
- no_extractable_evidence_found_in_the_document_provided: 1
- no_extractable_evidence_found_in_the_provided_pages: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_identified_in_the_provided_text: 1
- no_extractable_evidence_related_to_ibuprofen_dermal_formulations_found_in_the_pr: 1
- no_extractable_evidence_related_to_ibuprofen_found: 1
- no_extractable_evidence_related_to_oa_or_ibuprofen: 1
- no_references_to_ibuprofen_or_related_formulations_are_present_in_the_content_pr: 1
- no_relevant_content_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_data_extractable_from_the_provided_text: 1
- no_relevant_data_for_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_appears_extractable_from_the_document_provided: 1
- no_relevant_evidence_extractable_from_the_supported_text: 1
- no_relevant_evidence_found_in_the_document: 1
- no_relevant_evidence_found_in_the_provided_document: 1
- no_relevant_evidence_related_to_ibuprofen_found_in_the_provided_text: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulation_identified: 1
- no_relevant_evidence_related_to_ibuprofen_was_identified: 1
- no_relevant_extractable_evidence_appears_in_the_text_provided: 1
- no_relevant_extractable_evidence_found_in_the_provided_document: 1
- no_relevant_extractable_evidence_on_ibuprofen_or_diffusion_cells: 1
- no_relevant_extraction_could_be_done_from_the_provided_document_text: 1
- no_relevant_extraction_evidence_found_in_the_provided_text: 3
- no_relevant_extraction_evidence_regarding_ibuprofen_dermal_formulation_found: 1
- no_relevant_extraction_points_found_related_to_ibuprofen_or_dermal_formulation: 1
- no_relevant_extraction_routes_found_the_document_appears_to_focus_on_nanoparticl: 1
- no_relevant_information_about_ibuprofen_or_diffusion_cell_found: 1
- no_relevant_information_available_from_the_document: 1
- no_relevant_information_for_ibuprofen_extraction: 1
- no_relevant_information_found_in_the_document: 1
- no_relevant_information_found_regarding_ibuprofen_or_dermal_formulation: 1
- no_relevant_information_found_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_information_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_is_found_in_t: 1
- no_relevant_information_was_identified_related_to_ibuprofen_or_diffusion_cells_i: 1
- no_specific_data_extractable_from_provided_text: 1
- no_specific_evidence_extraction_locations_provided_in_the_pages: 1
- no_specific_evidence_or_data_regarding_ibuprofen_diffusion_cells_or_any_relevant: 1
- no_specific_evidence_regarding_ibuprofen_or_diffusion_cell_in_the_provided_conte: 1
- no_specific_information_available_document_content_mainly_includes_navigation_an: 1
- not_clear_if_any_relevant_evidence_regarding_ibuprofen_is_present: 1
- only_the_first_two_pages_are_visible_and_they_do_not_contain_any_relevant_inform: 1
- paper_discusses_layered_sodium_carboxymethylcellulose_film_wound_dressings_with_: 1
- paper_discusses_the_synthesis_and_functionalization_of_a_framework_for_drug_deli: 1
- relevant_content_is_not_accessible_from_the_provided_text: 1
- the_document_appears_to_be_focused_on_pharmaceutical_pollutants_and_agro_industr: 1
- the_document_appears_to_be_primarily_a_technical_overview_of_polyelectrolyte_com: 1
- the_document_appears_to_be_primarily_focused_on_clinical_investigation_findings_: 1
- the_document_appears_to_be_primarily_informational_without_specific_experimental: 1
- the_document_appears_to_be_related_to_bioactive_glasses_and_not_specifically_foc: 1
- the_document_appears_to_focus_on_nanocomposites_for_inhalation_with_no_indicatio: 1
- the_document_appears_to_lack_relevant_extraction_information: 1
- the_document_contains_mostly_blank_or_general_information_pages_with_no_specific: 1
- the_document_content_does_not_provide_clear_evidence_for_required_extraction: 1
- the_document_content_does_not_provide_extractable_evidence_only_introductory_inf: 1
- the_document_content_does_not_provide_specific_evidence_related_to_ibuprofen_der: 1
- the_document_content_is_currently_inaccessible_for_detailed_extraction: 1
- the_document_content_is_not_provided_further_text_extraction_required: 1
- the_document_did_not_provide_relevant_information_regarding_ibuprofen_or_diffusi: 1
- the_document_does_not_contain_any_relevant_content_extractable_for_ibuprofen_der: 1
- the_document_does_not_contain_extractable_evidence: 1
- the_document_does_not_contain_relevant_information_for_an_oa_only_ibuprofen_derm: 1
- the_document_does_not_contain_relevant_information_for_ibuprofen_dermal_formulat: 1
- the_document_does_not_mention_ibuprofen_or_related_diffusion_methods: 1
- the_document_does_not_provide_clear_evidence_related_to_diffusivity_or_barriers: 1
- the_document_does_not_provide_concrete_details_or_extraction_points_based_on_the: 1
- the_document_does_not_provide_information_related_to_ibuprofen_or_any_relevant_e: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_or_relate: 1
- the_document_does_not_provide_specific_evidence_related_to_ibuprofen_or_dermal_f: 1
- the_document_does_not_provide_specific_evidence_related_to_ibuprofen_or_diffusio: 1
- the_document_does_not_provide_sufficient_information_for_extraction: 1
- the_document_doesn_t_provide_clear_extractable_evidence_relevant_to_the_formulat: 1
- the_document_doesn_t_provide_sufficient_information_for_concrete_extraction: 1
- the_document_is_only_available_as_a_pdf_and_contains_no_extractable_structured_e: 1
- the_document_primarily_contains_metadata_and_no_extractable_evidence_related_to_: 1
- the_document_primarily_discusses_ibuprofen_s_effects_but_lacks_specific_experime: 1
- the_document_primarily_discusses_molecular_dynamics_simulations_and_does_not_exp: 1
- the_document_primarily_discusses_the_interaction_of_flurbiprofen_and_ibuprofen_n: 1
- the_document_primarily_provides_background_information_and_does_not_seem_to_cont: 1
- the_document_provided_does_not_contain_detailed_information_regarding_ibuprofen_: 1
- the_document_provided_does_not_contain_relevant_details_on_ibuprofen_or_its_derm: 1
- the_document_provided_does_not_contain_relevant_information_regarding_ibuprofen_: 1
- the_paper_discusses_the_pharmacological_potential_of_kyotorphin_and_its_derivati: 1
- the_paper_does_not_provide_clear_evidence_related_to_the_defined_criteria: 1
- the_paper_does_not_seem_relevant_to_an_oa_only_ibuprofen_dermal_formulation: 1
- the_paper_focuses_on_the_modulation_of_the_acute_phase_response_by_naproxen_not_: 1
- the_provided_document_text_does_not_contain_sufficient_content_for_extraction: 1
- the_study_discusses_the_removal_of_ibuprofen_ibu_via_the_mbr_uv_cl2_system_detai: 1
- this_document_does_not_contain_relevant_information_for_an_oa_ibuprofen_dermal_f: 1
- this_paper_appears_to_focus_on_antibacterial_activities_and_does_not_mention_ibu: 1
- this_paper_examines_the_effects_of_ibuprofen_among_other_contaminants_on_membran: 1
- unable_to_extract_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_: 1
- unspecified: 33
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
- applied: 11
- skipped: 223
#### patch_area
- applied: 9
- skipped: 140
#### patch_endpoint_time
- applied: 64
- skipped: 1
#### patch_endpoint_value
- applied: 87
- skipped: 169

## Patch Success Counts
- patch_api_concentration: 11
- patch_area: 9
- patch_endpoint_time: 64
- patch_endpoint_value: 87