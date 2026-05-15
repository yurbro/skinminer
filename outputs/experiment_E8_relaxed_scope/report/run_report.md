# Run Report: run_c52010923951

- Model: `gpt-4o-mini`
- Policy: `v3_any_ibuprofen_concentration`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `74`
- Final records evaluated: `74`
- Actually verified: `14`
- Final unresolved: `37`
- Final rejected: `23`

## Route Distribution
- figure: 19
- mixed: 6
- table: 23
- text: 12
- unresolved: 492

## Extractor Outputs
- figure: 4
- table: 70
- text: 11

## Verification Outcomes
- rejected: 23
- unresolved: 37
- verified: 14

## Scope Buckets
- out_of_scope: 14
- recoverable_unresolved: 37
- strict_in_scope: 14
- useful_but_out_of_scope: 9

## Scope Tags
- non_target_api: 14
- recoverable_area: 6
- recoverable_endpoint: 3
- recoverable_figure_digitization: 2
- recoverable_other: 1
- recoverable_support_gap: 33
- recoverable_unresolved: 37
- useful_but_out_of_scope: 9
- useful_device_out_of_scope: 3
- useful_study_type_out_of_scope: 6

## Failure Taxonomy
- figure_digitization_failed: 2
- insufficient_evidence: 54
- missing_area: 14
- missing_endpoint: 4
- missing_endpoint_time: 1
- not_target_api: 14
- not_target_api_concentration: 9
- not_target_device: 3
- not_target_study_type: 7
- percent_only: 7
- unit_normalization_failed: 1

## Failure Taxonomy By Route
### figure
- figure_digitization_failed: 2
- insufficient_evidence: 17
- missing_area: 11
- missing_endpoint: 2
- not_target_api: 5
- not_target_api_concentration: 2
- not_target_device: 2
- not_target_study_type: 6
- percent_only: 6
- unit_normalization_failed: 1
### mixed
- insufficient_evidence: 12
- missing_area: 1
- missing_endpoint: 1
- not_target_api: 4
- not_target_api_concentration: 2
### table
- insufficient_evidence: 19
- missing_area: 2
- not_target_api: 5
- not_target_api_concentration: 5
- not_target_study_type: 1
- percent_only: 1
### text
- insufficient_evidence: 6
- missing_endpoint: 1
- missing_endpoint_time: 1
- not_target_device: 1

## Figure Stage Counts
- digitization_no_output: 8
- digitized_curves: 9
- digitized_endpoints_failed: 8
- digitized_endpoints_ok: 9
- mapped_curves: 7
- triage_artifacts: 18
- triage_digitize_candidates: 15
- triage_has_permeation_plot_true: 15
- unmapped_curves: 2
- vlm_readings_readable: 13
- vlm_readings_total: 15
- vlm_used_as_final: 8

## Figure Gate Counts
- routed_candidates: 24
- after_gate: 19
- skipped:missing_explicit_figure_signal: 5

## Figure Triage Routes
- digitize: 15
- skip: 3

## Figure Plot Presence
- false: 3
- true: 15

## Figure Triage Signals
- digitizable:no: 3
- endpoint_curve_present:no: 4
- recommended_route:skip: 3
- ticks_readable:uncertain: 5
- why_not_digitizable:calibration_curve_not_target: 1
- why_not_digitizable:graph_does_not_depict_mean_sem_values_over_a_concentration_range_for_ibuprofen_i: 1
- why_not_digitizable:no_curves_are_present_panels_show_sem_images_only: 1

## Figure Digitization Statuses
- digitization_no_output: 8
- ok: 9

## Figure Mapping Statuses
- underconstrained_labels: 2
- vision_mapped: 7

## Figure VLM Grounding Statuses
- figure_label_space: 7
- figure_label_space_only: 6
- source_label_space: 2

## Figure VLM Reconciliation Statuses
- cv_vlm_disagreement: 5
- unreadable: 2
- vlm_only: 8

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 9
- priority_bucket:high: 5
- priority_bucket:medium: 4
- review_focus:diffusion_area: 6
- review_focus:endpoint_value: 3
- recommended_status:rejected: 2
- recommended_status:unresolved: 7
- disagreement:scope_bucket_disagreement: 2
- disagreement:status_disagreement: 2

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
- downloaded: 243
- error: 1
- resolved: 79
- unresolved: 229
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- content_does_not_provide_sufficient_information_for_evidence_extraction: 1
- content_from_the_document_is_primarily_about_hydrogel_carriers_and_does_not_spec: 1
- content_is_not_provided_beyond_pages_1_2_related_to_europe_pmc_functionality: 1
- content_is_unavailable_details_needed_to_assess_extraction_are_not_present: 1
- content_lacks_relevant_information_regarding_ibuprofen_diffusion_cell_study_type: 1
- content_not_available_for_extraction_from_provided_text_primarily_consists_of_na: 1
- content_not_extractable_from_provided_document_text: 1
- content_primarily_discusses_neutrophil_migration_and_effects_of_nsaids_without_s: 1
- data_extraction_details_are_unclear_due_to_the_content_provided: 1
- document_appears_to_consist_primarily_of_navigation_and_administrative_content_w: 1
- document_contains_limited_content_for_extraction: 1
- document_content_does_not_provide_relevant_information_based_on_the_required_cri: 1
- document_did_not_provide_relevant_content_for_extraction: 1
- document_does_not_appear_to_provide_relevant_evidence_for_extraction_regarding_i: 1
- document_does_not_provide_clear_evidence_regarding_specific_endpoints_or_study_t: 1
- document_focus_on_ft_ir_imaging_in_microfluidic_devices_no_specific_reference_to: 1
- document_information_is_primarily_about_a_hydrogel_system_and_its_impact_on_woun: 1
- document_primarily_contains_introductory_information_and_does_not_provide_extrac: 1
- evidence_extraction_not_applicable_as_relevant_content_for_ibuprofen_formulation: 1
- evidence_extraction_not_applicable_from_the_provided_document_text: 1
- evidence_extraction_requires_further_details_from_the_main_text: 1
- evidence_needs_further_extraction_from_subsequent_text: 1
- extraction_route_is_compromised_due_to_lack_of_specific_evidence_in_visible_text: 1
- focus_on_partitioning_of_nsaids_in_lipid_membranes_as_per_molecular_dynamics_stu: 1
- initial_page_review_further_extraction_needed: 1
- insufficient_content_available_for_extraction_from_the_provided_document: 1
- insufficient_evidence_details_provided_in_the_document: 1
- insufficient_evidence_extraction_due_to_lack_of_relevant_content: 1
- insufficient_evidence_in_provided_content: 1
- insufficient_information_available_for_extraction: 1
- insufficient_information_from_the_document_to_identify_extractable_evidence: 1
- insufficient_information_provided_in_the_document: 1
- insufficient_information_to_determine_specific_routes_or_endpoints: 1
- missing_structured_and_pdf_router_source: 238
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 65
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- need_to_access_further_content_for_detailed_extraction: 1
- no_detailed_information_available_regarding_study_specifics_or_methodologies: 1
- no_evidence_related_to_ibuprofen_or_diffusion_cell_focus_on_bezafibrate_derivati: 1
- no_explicit_extractable_evidence_detected_in_the_provided_pages: 1
- no_explicit_mention_of_ibuprofen_or_specific_diffusion_methods_more_details_requ: 1
- no_extractable_evidence_found_based_on_the_provided_text: 1
- no_extractable_evidence_found_in_current_text: 1
- no_extractable_evidence_found_in_provided_text: 1
- no_extractable_evidence_found_in_the_supplied_document: 1
- no_extractable_evidence_found_in_the_visible_text: 1
- no_extractable_evidence_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_extractable_evidence_from_the_provided_text_document_appears_inaccessible_or_: 1
- no_extractable_evidence_identified: 1
- no_extractable_evidence_regarding_ibuprofen_or_diffusion_cells: 1
- no_extractable_evidence_related_to_ibuprofen_or_a_diffusion_cell_found: 1
- no_mention_of_ibuprofen_or_diffusion_cells_found_in_the_provided_document: 1
- no_relevant_content_found_in_the_document_to_extract_evidence: 1
- no_relevant_data_extracted_from_the_provided_document_text: 1
- no_relevant_data_extracted_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_data_on_ibuprofen_or_diffusion_cells: 1
- no_relevant_data_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_data_related_to_ibuprofen_or_diffusion_cell_in_the_document: 1
- no_relevant_data_related_to_ibuprofen_or_diffusion_cells_found_in_the_document: 1
- no_relevant_evidence_extractable_from_the_text_provided: 1
- no_relevant_evidence_extracted: 1
- no_relevant_evidence_extracted_related_to_ibuprofen: 1
- no_relevant_evidence_extraction_available: 1
- no_relevant_evidence_extraction_found_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_evidence_for_ibuprofen_or_diffusion_cell_found: 1
- no_relevant_evidence_found_in_the_provided_document_text: 1
- no_relevant_evidence_found_in_the_provided_segments: 1
- no_relevant_evidence_related_to_ibuprofen_or_diffusion_cells_found_in_available_: 1
- no_relevant_evidence_related_to_ibuprofen_or_diffusion_studies_found_in_the_prov: 1
- no_relevant_extractable_evidence_found_in_the_provided_document_text: 1
- no_relevant_extractable_evidence_identified_in_the_document: 1
- no_relevant_extraction_evidence_found_in_the_document: 1
- no_relevant_extraction_evidence_found_in_the_provided_text: 1
- no_relevant_extraction_found_regarding_ibuprofen_dermal_formulations: 1
- no_relevant_information_extracted_from_the_provided_document: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_diffusion_studies: 1
- no_relevant_information_found_regarding_ibuprofen_or_aspects_related_to_dermal_f: 1
- no_relevant_information_found_regarding_ibuprofen_or_related_formulations: 1
- no_relevant_information_found_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_found_in_the_provided_te: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_in_the_provided_t: 1
- no_relevant_information_regarding_ibuprofen_or_its_dermal_formulation_found: 1
- no_relevant_information_regarding_ibuprofen_was_found: 1
- no_specific_endpoints_or_formulation_details_found_in_the_provided_text: 1
- no_specific_evidence_related_to_ibuprofen_or_diffusion_cell_methodologies_was_id: 1
- no_specific_extractable_evidence_related_to_ibuprofen_or_dermal_formulations_ide: 1
- no_specific_extractable_evidence_was_provided: 1
- no_specific_information_on_ibuprofen_or_dermal_formulations_found_in_the_excerpt: 1
- only_front_matter_extracted_no_evidence_available_yet: 1
- only_partial_content_from_the_document_is_available_needs_full_context_for_accur: 1
- only_the_title_to_assess_relevance: 1
- paper_does_not_provide_relevant_information_regarding_ibuprofen_or_dermal_formul: 1
- the_content_primarily_pertains_to_surgical_timing_and_does_not_provide_measurabl: 1
- the_document_appears_not_to_support_direct_evidence_extraction_as_it_s_primarily: 1
- the_document_appears_to_be_a_pubmed_central_page_and_the_actual_content_regardin: 1
- the_document_appears_to_be_a_systematic_review_but_does_not_mention_specific_for: 1
- the_document_appears_to_be_an_introduction_or_overview_without_extractable_evide: 1
- the_document_appears_to_be_inaccessible_and_primarily_contains_navigation_and_me: 1
- the_document_appears_to_be_inaccessible_or_lacks_specific_content_related_to_ext: 1
- the_document_appears_to_be_primarily_introductory_or_navigational_lacking_specif: 1
- the_document_appears_to_be_unavailable_or_inaccessible_for_specific_details: 1
- the_document_appears_to_be_unstructured_with_no_direct_evidence_related_to_ibupr: 1
- the_document_appears_to_primarily_discuss_tcm_plasters_against_primary_dysmenorr: 1
- the_document_content_does_not_provide_sufficient_details_for_extraction_it_prima: 1
- the_document_discusses_ibuprofen_s_interactions_and_loading_in_a_metal_organic_f: 1
- the_document_does_not_appear_to_provide_relevant_information_on_ibuprofen_or_rel: 1
- the_document_does_not_contain_relevant_evidence_regarding_ibuprofen_or_diffusion: 1
- the_document_does_not_contain_specific_evidence_relating_to_ibuprofen_or_diffusi: 1
- the_document_does_not_contain_specific_information_about_ibuprofen_diffusion_cel: 1
- the_document_does_not_contain_sufficient_information_to_identify_specific_endpoi: 1
- the_document_does_not_directly_contain_relevant_experimental_data_or_structured_: 1
- the_document_does_not_have_extractable_evidence_related_to_the_targeted_aspects: 1
- the_document_does_not_mention_ibuprofen_or_any_diffusion_cells: 1
- the_document_does_not_provide_any_relevant_information_about_ibuprofen_or_the_ex: 1
- the_document_does_not_provide_clear_evidence_or_information_related_to_ibuprofen: 1
- the_document_does_not_provide_clear_evidence_or_specific_structured_details_abou: 1
- the_document_does_not_provide_extractable_evidence: 1
- the_document_does_not_provide_sufficient_information_for_detailed_extraction: 1
- the_document_does_not_provide_sufficient_information_to_determine_relevant_extra: 1
- the_document_is_not_accessible_for_extraction: 1
- the_document_is_primarily_informational_and_does_not_contain_structured_evidence: 1
- the_document_lacks_specific_details_related_to_ibuprofen_or_diffusion_cells: 1
- the_document_primarily_consists_of_navigation_and_informational_content_no_relev: 1
- the_document_primarily_consists_of_site_navigation_and_lacks_substantive_content: 1
- the_document_primarily_contains_navigation_tools_and_does_not_provide_substantia: 1
- the_document_primarily_discusses_betamethasone_and_hiv_infection_no_relevant_ibu: 1
- the_document_primarily_discusses_hypothalamic_prostaglandins_and_their_role_in_b: 1
- the_document_primarily_discusses_pharmaceuticals_in_wastewater_and_their_removal: 1
- the_document_primarily_focuses_on_mucilage_as_a_mucoadhesive_polymer_without_dis: 1
- the_document_primarily_relates_to_a_nanocarrier_for_drug_release_but_does_not_me: 1
- the_document_provided_does_not_contain_relevant_details_regarding_ibuprofen_or_r: 1
- the_document_provided_does_not_offer_specific_information_regarding_diffusion_ce: 1
- the_document_provided_lacks_relevant_content_for_extraction: 1
- the_document_review_indicates_that_it_is_about_a_drug_release_study_but_lacks_sp: 1
- the_document_s_content_primarily_consists_of_web_interface_elements_and_does_not: 1
- the_document_text_does_not_provide_relevant_evidence_regarding_ibuprofen_or_diff: 1
- the_paper_appears_to_focus_on_the_design_of_nanoemulsions_for_intravenous_admini: 1
- the_paper_discusses_mast_cell_mediator_release_associated_with_cyclooxygenase_in: 1
- the_paper_discusses_methods_but_lacks_clear_endpoint_identification: 1
- the_paper_discusses_synergy_of_ibuprofen_with_fluconazole_but_does_not_provide_s: 1
- the_paper_does_not_provide_specific_evidence_related_to_ibuprofen_dermal_formula: 1
- the_paper_focuses_on_a_clinical_trial_of_a_dysmenorrhea_patch_and_appears_to_hav: 1
- the_paper_focuses_on_dexamethasone_and_its_effects_on_amyloid_beta_protein_with_: 1
- the_paper_provides_information_on_the_role_of_slc5a8_as_a_transporter_for_variou: 1
- the_pdf_does_not_display_relevant_information_for_extraction_in_the_provided_con: 1
- the_provided_text_does_not_contain_relevant_evidence_related_to_ibuprofen_dermal: 1
- the_relevant_extraction_points_are_unclear_due_to_a_lack_of_specific_details_in_: 1
- the_section_does_not_have_sufficient_details_about_diffusion_or_formulation: 1
- the_text_does_not_provide_clear_details_about_diffusion_cells_or_endpoint_findin: 1
- the_text_does_not_provide_sufficient_information_to_make_definitive_extractions: 1
- this_is_a_review_paper_and_does_not_contain_direct_evidence_regarding_ibuprofen_: 1
- this_paper_does_not_discuss_ibuprofen_or_relevant_diffusion_methodologies: 1
- this_paper_focuses_on_the_synthesis_of_a_metal_organic_framework_for_ibuprofen_d: 1
- this_study_examines_the_synergy_of_ibuprofen_among_other_compounds_against_candi: 1
- unable_to_extract_evidence_due_to_unavailability_of_detailed_text_and_tables: 1
- uncertain_information_regarding_specific_experimental_details_and_formulations: 1
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
- skipped: 35
#### patch_area
- applied: 10
- skipped: 29
#### patch_endpoint_time
- applied: 20
- skipped: 1
#### patch_endpoint_value
- applied: 24
- skipped: 34

## Patch Success Counts
- patch_area: 10
- patch_endpoint_time: 20
- patch_endpoint_value: 24