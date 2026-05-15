# Run Report: run_7513c9b9fbec

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `78`
- Final records evaluated: `78`
- Actually verified: `6`
- Final unresolved: `49`
- Final rejected: `23`

## Route Distribution
- figure: 23
- mixed: 9
- table: 17
- text: 13
- unresolved: 484

## Extractor Outputs
- figure: 7
- table: 68
- text: 7

## Verification Outcomes
- rejected: 23
- unresolved: 49
- verified: 6

## Scope Buckets
- out_of_scope: 12
- recoverable_unresolved: 41
- strict_in_scope: 6
- useful_but_out_of_scope: 19

## Scope Tags
- non_target_api: 12
- recoverable_api_basis: 26
- recoverable_area: 4
- recoverable_endpoint: 4
- recoverable_endpoint_time: 5
- recoverable_figure_digitization: 2
- recoverable_support_gap: 29
- recoverable_unit_normalization: 2
- recoverable_unresolved: 41
- useful_api_concentration_out_of_scope: 10
- useful_but_out_of_scope: 19
- useful_device_out_of_scope: 3
- useful_endpoint_out_of_scope: 1
- useful_study_type_out_of_scope: 9

## Failure Taxonomy
- ambiguous_api_concentration: 32
- figure_digitization_failed: 5
- insufficient_evidence: 56
- missing_api_concentration: 7
- missing_area: 12
- missing_endpoint: 9
- missing_endpoint_time: 9
- not_target_api: 12
- not_target_api_concentration: 12
- not_target_device: 5
- not_target_study_type: 10
- percent_only: 18
- unit_normalization_failed: 3

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 19
- figure_digitization_failed: 5
- insufficient_evidence: 28
- missing_api_concentration: 6
- missing_area: 7
- missing_endpoint: 7
- missing_endpoint_time: 6
- not_target_api: 8
- not_target_api_concentration: 4
- not_target_device: 1
- not_target_study_type: 8
- percent_only: 10
- unit_normalization_failed: 3
### mixed
- ambiguous_api_concentration: 1
- insufficient_evidence: 16
- missing_api_concentration: 1
- missing_area: 3
- missing_endpoint: 2
- missing_endpoint_time: 2
- not_target_api: 3
- not_target_api_concentration: 4
- not_target_device: 4
- percent_only: 7
### table
- ambiguous_api_concentration: 12
- insufficient_evidence: 7
- missing_area: 2
- missing_endpoint_time: 1
- not_target_api: 1
- not_target_api_concentration: 4
- not_target_study_type: 2
- percent_only: 1
### text
- insufficient_evidence: 5

## Figure Stage Counts
- digitization_no_output: 4
- digitized_curves: 24
- digitized_endpoints_failed: 6
- digitized_endpoints_ok: 24
- mapped_curves: 8
- triage_artifacts: 20
- triage_digitize_candidates: 16
- triage_has_permeation_plot_true: 16
- unmapped_curves: 16
- vlm_readings_readable: 25
- vlm_readings_total: 29
- vlm_used_as_final: 13

## Figure Gate Counts
- routed_candidates: 31
- after_gate: 23
- skipped:missing_explicit_figure_signal: 8

## Figure Triage Routes
- digitize: 16
- skip: 4

## Figure Plot Presence
- false: 4
- true: 16

## Figure Triage Signals
- digitizable:no: 4
- endpoint_curve_present:no: 4
- recommended_route:skip: 4
- ticks_readable:no: 1
- ticks_readable:uncertain: 4
- why_not_digitizable:calibration_curve_not_target: 1
- why_not_digitizable:the_curve_data_is_not_clearly_visible_or_properly_formatted_for_digitization: 1
- why_not_digitizable:the_figure_lacks_quantitative_curves_that_could_indicate_an_endpoint_regarding_i: 1
- why_not_digitizable:the_figure_presents_a_scatter_plot_but_lacks_clear_numerical_readouts_specific_d: 1

## Figure Digitization Statuses
- digitization_no_output: 4
- fail_missing_axis_range: 2
- ok: 24

## Figure Mapping Statuses
- underconstrained_labels: 16
- vision_mapped: 8

## Figure VLM Grounding Statuses
- figure_label_space: 6
- figure_label_space_only: 16
- none: 6
- source_label_space: 1

## Figure VLM Reconciliation Statuses
- cv_only: 6
- cv_vlm_disagreement: 3
- no_source_record: 3
- unreadable: 4
- vlm_only: 13

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 28
- priority_bucket:high: 22
- priority_bucket:medium: 6
- review_focus:api_concentration_basis: 22
- review_focus:diffusion_area: 1
- review_focus:endpoint_time: 1
- review_focus:endpoint_value: 4
- recommended_status:rejected: 6
- recommended_status:unresolved: 22
- disagreement:scope_bucket_disagreement: 6
- disagreement:status_disagreement: 6

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
- downloaded: 242
- error: 1
- resolved: 85
- unresolved: 218
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- additional_content_needed_for_precise_extraction_details: 1
- content_does_not_mention_ibuprofen_or_diffusion_cell: 1
- content_extraction_not_possible_document_primarily_consists_of_administrative_an: 1
- content_extraction_not_possible_further_access_to_content_required_for_evaluatio: 1
- content_from_the_provided_source_is_not_extractable: 1
- content_not_available_for_specific_extraction: 1
- content_not_extractable_as_only_preliminary_structure_and_navigation_information: 1
- content_primarily_consists_of_navigation_and_help_links_no_substantive_data_rega: 1
- content_seems_to_focus_on_synthesis_and_properties_of_novel_amides_without_menti: 1
- data_appears_to_be_inaccessible_or_not_extractable_from_this_page: 1
- discussions_center_on_the_role_of_sodium_coupled_monocarboxylate_transporters_in: 1
- document_appears_to_be_an_access_page_without_relevant_extraction_content: 1
- document_appears_to_be_focused_on_pharmaceutical_pollutants_rather_than_ibuprofe: 1
- document_appears_to_contain_no_relevant_evidence: 1
- document_contains_no_specific_details_on_endpoints_or_formulations_relevant_to_i: 1
- document_does_not_contain_relevant_information_for_extraction: 1
- document_mainly_includes_navigation_and_site_information_no_extractable_content_: 1
- document_primarily_seems_to_provide_structural_details_and_lacks_direct_referenc: 1
- document_text_contains_structure_but_lacks_specific_extractable_endpoints_or_met: 1
- evidence_extraction_is_limited_due_to_lack_of_specific_structured_data_or_endpoi: 1
- evidence_extraction_is_limited_due_to_the_provided_document_fragment_being_unstr: 1
- evidence_for_franz_diffusion_cell_and_ibuprofen_presence_noted: 1
- evidence_of_ibuprofen_s_effect_on_neutrophil_migration_exists_but_lacks_detail_o: 1
- extraction_details_are_unclear_from_the_document_text_provided: 1
- extraction_details_not_well_defined_in_provided_text: 1
- extraction_route_is_uncertain_more_information_needed_from_the_document: 1
- extraction_route_not_clear_document_first_two_pages_contain_navigation_and_insti: 1
- further_content_extraction_is_required_for_detailed_evidence: 1
- initial_pages_do_not_contain_relevant_extractable_evidence: 1
- insufficient_content_available_for_detailed_extraction: 1
- insufficient_content_available_to_identify_extractable_evidence: 1
- insufficient_detailed_evidence_found_in_provided_excerpt: 1
- insufficient_evidence_related_to_ibuprofen_focus_on_different_compounds: 1
- insufficient_extractable_evidence_provided_in_the_source_text: 1
- insufficient_information_available: 1
- insufficient_information_available_from_the_document_provided: 1
- insufficient_information_for_detailed_extraction_content_mostly_consists_of_webs: 1
- insufficient_information_for_extraction: 1
- insufficient_information_found_in_the_provided_document_for_extraction: 1
- insufficient_information_from_the_provided_document_to_extract_relevant_evidence: 1
- insufficient_information_in_text_for_extraction: 1
- insufficient_information_to_determine_key_extraction_details: 1
- insufficient_information_to_determine_specific_details_about_ibuprofen_or_diffus: 1
- insufficient_information_to_extract_evidence_related_to_ibuprofen_or_dermal_form: 1
- irb_analysis_and_interactions_with_mil_88b_fe_suggested_for_ibuprofen_loading: 1
- missing_structured_and_pdf_router_source: 230
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 67
- missing_structured_and_pdf_router_source_html_remote_connecttimeout: 1
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- more_details_needed_from_the_document_to_extract_carrier_information: 1
- no_accessible_content_provided_to_assess_extraction_route: 1
- no_applicable_evidence_found_in_the_provided_text: 1
- no_clear_evidence_on_formulation_or_endpoint_in_the_provided_text: 1
- no_detailed_evidence_available_from_the_provided_excerpt: 1
- no_evidence_related_to_ibuprofen_or_formulation_details_found_in_the_document: 1
- no_extractable_evidence_available_from_the_provided_text: 1
- no_extractable_evidence_could_be_identified_in_the_provided_document_text: 1
- no_extractable_evidence_found_in_provided_document: 1
- no_extractable_evidence_found_in_provided_text: 2
- no_extractable_evidence_found_in_the_provided_document: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_identified_in_the_available_pages: 1
- no_extractable_evidence_present_in_the_provided_content: 1
- no_relevant_content_available_from_the_provided_document_sections: 1
- no_relevant_content_extracted_related_to_ibuprofen_or_formulations: 1
- no_relevant_content_found_in_provided_text: 1
- no_relevant_content_regarding_ibuprofen_or_dermal_formulations_identified: 1
- no_relevant_content_related_to_the_extraction_criteria_is_readable_from_the_prov: 1
- no_relevant_data_found_in_the_provided_document: 1
- no_relevant_data_found_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_data_related_to_ibuprofen_found_in_the_provided_document: 1
- no_relevant_data_related_to_ibuprofen_or_related_dermal_formulations_was_found_i: 1
- no_relevant_details_available_in_the_provided_sections: 1
- no_relevant_evidence_extractable_from_the_provided_document_text: 1
- no_relevant_evidence_extraction_available: 1
- no_relevant_evidence_extraction_can_be_performed_from_the_provided_text: 1
- no_relevant_evidence_for_ibuprofen_dermal_formulations_found: 1
- no_relevant_evidence_found_about_ibuprofen_or_diffusion_cells: 1
- no_relevant_evidence_found_in_the_provided_text: 1
- no_relevant_evidence_regarding_ibuprofen_was_found_in_the_provided_text_the_text: 1
- no_relevant_evidence_related_to_ibuprofen_extraction_found_in_the_document: 1
- no_relevant_evidence_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_relevant_evidence_related_to_ibuprofen_or_diffusion_cells_found_in_the_suppli: 1
- no_relevant_extractable_evidence_found_in_the_document: 1
- no_relevant_extractable_evidence_found_in_the_provided_document_text: 1
- no_relevant_extractable_evidence_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_extraction_available: 1
- no_relevant_extraction_evidence_found_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_found_for_ibuprofen_or_dermal_formulation: 1
- no_relevant_information_found_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_found_regarding_ibuprofen_or_diffusion_studies: 1
- no_relevant_information_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_found_in_the_document: 1
- no_relevant_information_provided_in_the_visible_document_text: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulation_found: 1
- no_relevant_sections_extracted_regarding_ibuprofen_or_dermal_formulation: 1
- no_significant_extractable_evidence_found_the_relevant_details_about_the_study_a: 1
- no_specific_evidence_extractable_from_the_text_provided: 1
- no_specific_extraction_evidence_found_related_to_ibuprofen: 1
- no_specific_extraction_points_for_ibuprofen_or_diffusion_cell_related_evidence_w: 1
- no_usable_data_or_extractable_evidence_found_in_the_provided_document: 1
- not_enough_evidence_for_endpoints_formulation_details_are_missing: 1
- not_enough_extractable_evidence_found_in_the_provided_document: 1
- paper_discusses_synergy_with_ibuprofen_but_lacks_specific_details_on_formulation: 1
- the_content_does_not_provide_specific_extraction_points_or_evidence: 1
- the_content_provided_does_not_contain_relevant_information_related_to_ibuprofen_: 1
- the_content_suggests_a_focus_on_ibuprofen_formulations_but_lacks_detailed_pathwa: 1
- the_document_appears_to_be_a_clinical_paper_but_lacks_specific_evidence_extracti: 1
- the_document_appears_to_be_focused_on_polystyrene_modified_carbon_nanotubes_in_d: 1
- the_document_appears_to_focus_on_crystallographic_textures_and_morphologies_of_i: 1
- the_document_contains_limited_extractable_evidence_based_on_the_provided_excerpt: 1
- the_document_did_not_provide_additional_usable_content_and_only_contained_naviga: 1
- the_document_discusses_mastocytosis_and_adverse_reactions_to_cyclooxygenase_inhi: 1
- the_document_does_not_appear_to_contain_information_relevant_to_ibuprofen_or_der: 1
- the_document_does_not_appear_to_contain_relevant_information_regarding_ibuprofen: 1
- the_document_does_not_appear_to_focus_on_ibuprofen_or_related_formulations: 1
- the_document_does_not_contain_relevant_evidence_for_ibuprofen_dermal_formulation: 1
- the_document_does_not_contain_relevant_extractable_evidence_pertaining_to_ibupro: 1
- the_document_does_not_contain_relevant_extractable_evidence_related_to_specific_: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_dermal_fo: 1
- the_document_does_not_explicitly_provide_details_on_formulations_or_endpoints_su: 1
- the_document_does_not_provide_any_structured_information_relevant_to_ibuprofen_o: 1
- the_document_does_not_provide_clear_endpoints_or_formulation_details_from_the_te: 1
- the_document_does_not_provide_relevant_information_about_ibuprofen_or_diffusion_: 1
- the_document_does_not_provide_specific_details_relevant_to_the_extraction_criter: 1
- the_document_does_not_provide_specific_evidence_related_to_ibuprofen_or_any_derm: 1
- the_document_does_not_provide_specific_evidence_related_to_ibuprofen_or_its_form: 1
- the_document_does_not_provide_sufficient_information: 1
- the_document_does_not_provide_sufficient_information_for_definitive_extraction_r: 1
- the_document_does_not_provide_sufficient_information_related_to_ibuprofen_or_dif: 1
- the_document_does_not_provide_sufficient_information_to_determine_relevant_extra: 1
- the_document_doesn_t_contain_relevant_information_for_extraction_regarding_ibupr: 1
- the_document_is_not_accessible_for_extraction_unclear_if_relevant_content_exists: 1
- the_document_mainly_discusses_polymer_membrane_properties_without_specific_menti: 1
- the_document_mostly_contains_navigation_elements_and_requires_further_extraction: 1
- the_document_primarily_consists_of_front_matter_and_doesn_t_contain_relevant_inf: 1
- the_document_primarily_consists_of_non_substantive_content_with_no_clear_mention: 1
- the_document_primarily_discusses_a_synoviocyte_model_and_its_response_to_ibuprof: 1
- the_document_primarily_discusses_tcm_plasters_and_does_not_appear_related_to_ibu: 1
- the_document_primarily_focuses_on_the_diffusivity_of_various_cyclodextrins_and_i: 1
- the_document_primarily_focuses_on_the_synthesis_of_lignin_based_hydrogels_no_dir: 1
- the_document_primarily_provides_metadata_without_relevant_content: 1
- the_document_provided_does_not_contain_relevant_extractable_evidence_related_to_: 1
- the_document_provided_is_not_visible_for_evidence_extraction: 1
- the_document_source_provided_does_not_contain_clear_extraction_routes_key_eviden: 1
- the_paper_did_not_pertain_to_ibuprofen_or_relevant_dermal_formulations: 1
- the_paper_discusses_the_effects_of_ibuprofen_but_does_not_provide_specific_detai: 1
- the_paper_discusses_the_synthesis_and_functionalization_of_a_metal_organic_frame: 1
- the_paper_does_not_provide_specific_details_about_ibuprofen_or_diffusion_cells: 1
- the_paper_focuses_on_a_hybrid_system_for_ibuprofen_removal_but_lacks_specific_de: 1
- the_paper_focuses_on_polyelectrolyte_coated_mesoporous_bioactive_glasses_and_doe: 1
- the_source_document_does_not_provide_specific_information_relevant_to_ibuprofen_: 1
- this_paper_discusses_new_derivatives_of_ibuprofen_but_does_not_provide_clear_evi: 1
- this_paper_discusses_the_synergy_of_ibuprofen_with_other_compounds_against_candi: 1
- this_paper_does_not_discuss_ibuprofen_or_diffusion_cells: 1
- this_paper_potentially_discusses_ibuprofen_formulations_but_lacks_specific_extra: 1
- unable_to_extract_explicit_evidence_due_to_lack_of_detail_in_the_source: 1
- unable_to_extract_relevant_evidence_regarding_ibuprofen_or_diffusion_cells_from_: 1
- unspecified: 29
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

## Patch Success Counts