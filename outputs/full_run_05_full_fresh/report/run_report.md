# Run Report: run_b1098bdc4ef2

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Assembled records: `90`
- Final records evaluated: `90`
- Actually verified: `13`
- Final unresolved: `38`
- Final rejected: `39`

## Route Distribution
- figure: 18
- mixed: 10
- table: 9
- text: 9
- unresolved: 488

## Extractor Outputs
- figure: 22
- table: 61
- text: 13

## Verification Outcomes
- rejected: 39
- unresolved: 38
- verified: 13

## Failure Taxonomy
- figure_digitization_failed: 9
- insufficient_evidence: 12
- missing_api_concentration: 8
- missing_area: 41
- missing_endpoint: 6
- missing_endpoint_time: 1
- not_target_api: 11
- not_target_device: 36
- not_target_study_type: 13
- percent_only: 7
- unit_normalization_failed: 4

## Failure Taxonomy By Route
### figure
- figure_digitization_failed: 8
- insufficient_evidence: 6
- missing_area: 33
- missing_endpoint: 3
- missing_endpoint_time: 1
- not_target_api: 3
- not_target_device: 15
- not_target_study_type: 9
- percent_only: 3
- unit_normalization_failed: 4
### mixed
- figure_digitization_failed: 1
- insufficient_evidence: 3
- missing_api_concentration: 8
- missing_area: 5
- missing_endpoint: 3
- not_target_api: 7
- not_target_device: 11
- not_target_study_type: 3
- percent_only: 1
### table
- missing_area: 2
- not_target_api: 1
- not_target_device: 6
- not_target_study_type: 1
- percent_only: 3
### text
- insufficient_evidence: 3
- missing_area: 1
- not_target_device: 4

## Figure Stage Counts
- digitized_curves: 27
- digitized_endpoints_failed: 1
- digitized_endpoints_ok: 27
- mapped_curves: 26
- triage_artifacts: 19
- triage_digitize_candidates: 17
- unmapped_curves: 1

## Figure Gate Counts
- routed_candidates: 28
- after_gate: 20
- skipped:missing_explicit_figure_signal: 8

## Figure Triage Routes
- digitize: 17
- skip: 1
- text_table_maybe: 1

## Figure Triage Signals
- digitizable:no: 2
- endpoint_curve_present:no: 2
- recommended_route:skip: 1
- recommended_route:text_table_maybe: 1
- ticks_readable:no: 2
- ticks_readable:uncertain: 1
- why_not_digitizable:no_curves_or_endpoints_present_in_the_image: 1
- why_not_digitizable:no_discernible_endpoint_curves_for_digitization: 1

## Figure Digitization Statuses
- fail_missing_axis_range: 1
- ok: 27

## Figure Mapping Statuses
- unmapped: 1
- vision_mapped: 26

## LLM Reliability
- none

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-03-28.v1
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1

## Blockage Summary
### Access Statuses
- downloaded: 227
- error: 1
- resolved: 79
- unresolved: 227
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- content_appears_non_extractable_requires_further_review_of_the_full_document: 1
- content_appears_primarily_as_introductory_text_and_navigation_details: 1
- content_does_not_have_relevant_information_for_ibuprofen_or_diffusion_studies: 1
- content_does_not_provide_specific_extractable_evidence_regarding_diffusion_cells: 1
- content_from_pdf_not_fully_available_for_detailed_extraction: 1
- content_not_available_for_extraction: 1
- content_primarily_contains_navigation_and_tool_information_no_extractable_eviden: 1
- content_primarily_includes_clinical_monitoring_and_innovation_in_transdermal_del: 1
- document_appears_to_be_partially_processed_relevant_content_is_not_visible: 1
- document_contains_no_explicit_evidence_regarding_ibuprofen_dermal_formulation: 1
- document_content_is_primarily_about_the_effects_of_ibuprofen_on_red_blood_cells_: 1
- document_does_not_contain_relevant_data_regarding_ibuprofen_or_diffusion_cells: 1
- document_does_not_provide_extractable_evidence_related_to_ibuprofen: 1
- document_fragments_do_not_provide_the_necessary_details_for_extraction: 1
- document_lacks_substantial_details_for_extraction: 1
- document_pages_do_not_contain_relevant_experimental_or_formulation_data: 1
- document_primarily_discusses_the_effects_of_endotoxin_on_cgrp_release_without_sp: 1
- document_seems_to_contain_administrative_content_and_lacks_relevant_scientific_d: 1
- evidence_extraction_cannot_be_performed_due_to_lack_of_content: 1
- evidence_extraction_cannot_be_performed_due_to_lack_of_specific_content_in_the_d: 1
- evidence_extraction_not_applicable_as_no_extractable_evidence_available: 1
- evidence_extraction_not_feasible_from_provided_text_content_primarily_consists_o: 1
- extractable_evidence_is_not_present_in_the_provided_document_text: 1
- extractable_evidence_not_clearly_defined_in_the_text_provided: 1
- focus_is_primarily_on_pharmacological_influence_and_safety_of_ibuprofen_in_relat: 1
- focus_on_ibuprofen_transmembrane_diffusion_using_franz_diffusion_cells: 1
- focus_on_in_vitro_microbiological_and_drug_release_aspects: 1
- focused_on_metal_organic_frameworks_for_dermal_application_details_on_specific_f: 1
- full_content_from_the_document_is_necessary_to_extract_specific_evidence: 1
- info_about_formulation_parameters_and_permeation_but_specific_details_on_extract: 1
- initial_findings_from_a_clinical_investigation_are_likely_to_contain_relevant_de: 1
- initial_pages_do_not_contain_relevant_data_further_pages_may_be_needed_for_extra: 1
- initial_pages_do_not_contain_relevant_evidence: 1
- insufficient_content_in_provided_document_text_for_detailed_extraction: 1
- insufficient_evidence_present_in_the_document_for_extraction: 1
- insufficient_extractable_evidence_from_the_given_document_segments: 1
- insufficient_information_available_for_detailed_routes: 1
- insufficient_information_for_detailed_extraction: 1
- insufficient_information_from_the_provided_text: 1
- insufficient_information_in_the_document: 1
- insufficient_information_in_the_text_to_extract_relevant_details_regarding_ibupr: 1
- insufficient_information_to_determine_extraction_route_based_on_the_provided_doc: 1
- insufficient_information_to_extract_relevant_evidence_regarding_ibuprofen_or_its: 1
- limited_detail_in_extraction_due_to_partial_content: 1
- limited_information_available_to_determine_specific_extraction_routes: 1
- missing_structured_and_pdf_router_source: 237
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 63
- missing_structured_and_pdf_router_source_html_remote_connectionerror: 1
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- more_evidence_needed_from_the_document_for_precise_extraction: 1
- no_clear_evidence_regarding_ibuprofen_or_diffusion_cell_additional_context_neede: 1
- no_clear_extractable_evidence_location_identified: 1
- no_evidence_extractable_related_to_ibuprofen_or_diffusion_cell: 1
- no_extractable_content_found_in_the_document: 1
- no_extractable_evidence_available_from_the_provided_text: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_in_the_document_provided: 1
- no_extractable_evidence_found_in_the_provided_document_content: 1
- no_extractable_evidence_found_in_the_provided_text: 2
- no_extractable_evidence_related_to_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_content_detected_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_content_for_ibuprofen_or_diffusion_cell_information: 1
- no_relevant_content_identifiable_from_the_provided_text_for_extraction: 1
- no_relevant_data_found_about_ibuprofen_or_diffusion_cells: 1
- no_relevant_data_on_ibuprofen_or_diffusion_methods_found_in_pages_provided: 1
- no_relevant_data_on_ibuprofen_or_formulations_found_in_the_provided_text: 1
- no_relevant_evidence_extracted_regarding_ibuprofen_or_diffusion_cells_from_the_p: 1
- no_relevant_evidence_for_ibuprofen_dermal_formulation_extraction_found_in_the_pr: 1
- no_relevant_evidence_found_in_the_provided_text: 1
- no_relevant_evidence_found_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_regarding_ibuprofen_or_diffusion_cells_found_in_the_documen: 1
- no_relevant_evidence_regarding_ibuprofen_or_diffusion_cells_was_found_in_the_pro: 1
- no_relevant_extractable_evidence_apparent_from_the_provided_text: 1
- no_relevant_extraction_points_identified_in_the_provided_document_text: 1
- no_relevant_information_extracted: 1
- no_relevant_information_for_ibuprofen_dermal_formulation_extraction: 1
- no_relevant_information_found_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_information_found_regarding_ibuprofen_or_diffusion_methods: 1
- no_relevant_information_is_extracted_from_the_initial_pages_of_the_document: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_extracted_from_the_docum: 1
- no_relevant_information_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_specific_evidence_extractable_related_to_ibuprofen_or_diffusion_cell: 1
- no_specific_information_on_ibuprofen_or_diffusion_cells_present_in_the_text: 1
- no_specific_structured_evidence_is_provided_in_the_document: 1
- no_structured_evidence_extracted_from_the_content_provided: 1
- paper_discusses_chronotherapeutic_drug_delivery_and_mentions_ibuprofen_but_lacks: 1
- paper_discusses_ibuprofen_functionalized_membranes_evidence_extraction_routes_ma: 1
- paper_focuses_on_antibacterial_activities_and_does_not_involve_ibuprofen_or_derm: 1
- paper_focuses_primarily_on_biodegradation_of_nsaids_including_ibuprofen_in_envir: 1
- relevant_evidence_regarding_ibuprofen_formulation_is_likely_present_but_not_extr: 1
- source_document_lacks_visible_content_or_structured_data_for_meaningful_extracti: 1
- technical_note_on_ibuprofen_release_methods: 1
- the_content_appears_to_be_introductory_or_navigational_with_no_specific_extracti: 1
- the_content_does_not_provide_relevant_information_for_the_extraction_related_to_: 1
- the_content_does_not_provide_sufficient_details_about_studies_relating_to_ibupro: 1
- the_document_appears_to_be_focused_on_the_characterization_of_a_mucilage_polymer: 1
- the_document_appears_to_be_inaccessible_as_it_contains_only_europe_pmc_navigatio: 1
- the_document_appears_to_be_primarily_focused_on_the_evaluation_of_hydrogels_for_: 1
- the_document_appears_to_be_unrelated_to_ibuprofen_or_dermal_formulations: 1
- the_document_appears_to_discuss_spray_drying_of_nanocomposites_no_relevant_conte: 1
- the_document_appears_to_focus_on_crohn_s_disease_and_does_not_provide_relevant_e: 1
- the_document_appears_to_lack_specific_details_regarding_formulations_and_endpoin: 1
- the_document_content_does_not_provide_sufficient_evidence_for_extraction_related: 1
- the_document_content_is_not_sufficient_to_extract_concrete_evidence_regarding_ib: 1
- the_document_context_is_primarily_about_synthesis_and_functionalization_with_unc: 1
- the_document_does_not_contain_any_information_relevant_to_oa_or_ibuprofen_dermal: 1
- the_document_does_not_contain_relevant_evidence_for_oa_or_ibuprofen: 1
- the_document_does_not_provide_clear_evidence_findings_or_methodologies_related_t: 1
- the_document_does_not_provide_clear_evidence_related_to_a_dermal_formulation_or_: 1
- the_document_does_not_provide_enough_information_to_classify_extraction_routes_o: 1
- the_document_does_not_provide_enough_information_to_determine_extraction_details: 1
- the_document_does_not_provide_extractable_evidence_related_to_ibuprofen_or_a_dif: 1
- the_document_does_not_provide_relevant_extractable_evidence_regarding_ibuprofen_: 1
- the_document_is_a_webpage_related_to_europe_pmc_not_the_actual_content_of_the_pa: 1
- the_document_is_mostly_about_the_platform_and_does_not_contain_extractable_evide: 1
- the_document_is_primarily_a_review_and_does_not_provide_specific_experimental_da: 1
- the_document_is_primarily_introductory_and_lacks_specific_experimental_findings_: 1
- the_document_only_includes_a_front_page_with_no_relevant_information_extracted: 1
- the_document_primarily_contains_administrative_and_navigation_information_with_n: 1
- the_document_primarily_discusses_an_injectable_hydrogel_formulation_involving_ib: 1
- the_document_primarily_discusses_ibuprofen_timing_in_the_context_of_hand_surgery: 1
- the_document_primarily_discusses_theoretical_analysis_and_does_not_clearly_suppo: 1
- the_document_primarily_focuses_on_a_hydrogel_for_drug_delivery_but_lacks_explici: 1
- the_document_primarily_seems_to_contain_navigational_content_or_possibly_an_erro: 1
- the_document_provided_does_not_contain_specific_extractable_evidence_related_to_: 1
- the_document_provided_does_not_contain_sufficient_extractable_evidence_or_struct: 1
- the_document_provides_limited_visible_information_regarding_endpoints_and_formul: 1
- the_paper_discusses_responses_to_ibuprofen_among_other_compounds_but_does_not_me: 1
- the_paper_does_not_mention_ibuprofen_or_provide_clear_evidence_from_an_endpoint: 1
- the_paper_focuses_on_the_effects_of_nonsteroidal_antiinflammatory_drugs_includin: 1
- the_paper_s_content_does_not_appear_to_relate_to_ibuprofen_or_dermal_formulation: 1
- the_paper_seems_to_focus_on_the_permeability_of_frog_skin_to_chemicals_and_penet: 1
- the_paper_title_suggests_a_focus_on_bioactive_coatings_for_drug_delivery_but_doe: 1
- the_provided_text_does_not_contain_clear_evidence_or_structured_sections_for_ext: 1
- the_review_discusses_sodium_coupled_monocarboxylate_transporters_smcts_particula: 1
- the_text_does_not_provide_sufficient_extractable_evidence_or_specific_details_re: 1
- this_document_discusses_microneedle_iontophoresis_combinations_but_does_not_expl: 1
- this_extraction_route_primarily_focuses_on_general_mentions_of_ibuprofen_and_ass: 1
- unable_to_extract_relevant_specifics_regarding_ibuprofen_or_diffusion_methodolog: 1
- unable_to_extract_specific_experimental_or_endpoint_details_from_the_current_tex: 1
- unspecified: 47
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
- applied: 2
- skipped: 8
#### patch_area
- applied: 2
- skipped: 58
#### patch_endpoint_time
- applied: 27
- skipped: 1
#### patch_endpoint_value
- applied: 15
- skipped: 6

## Patch Success Counts
- patch_api_concentration: 2
- patch_area: 2
- patch_endpoint_time: 27
- patch_endpoint_value: 15