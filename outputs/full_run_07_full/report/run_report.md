# Run Report: run_c8e16e412ed1

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Assembled records: `124`
- Final records evaluated: `124`
- Actually verified: `32`
- Final unresolved: `32`
- Final rejected: `60`

## Route Distribution
- figure: 13
- mixed: 11
- table: 13
- text: 10
- unresolved: 495

## Extractor Outputs
- figure: 25
- table: 77
- text: 25

## Verification Outcomes
- rejected: 60
- unresolved: 32
- verified: 32

## Failure Taxonomy
- figure_digitization_failed: 7
- insufficient_evidence: 12
- missing_api_concentration: 4
- missing_area: 36
- missing_endpoint: 16
- missing_endpoint_time: 4
- not_target_api: 27
- not_target_device: 43
- not_target_study_type: 18
- percent_only: 12
- unit_normalization_failed: 19

## Failure Taxonomy By Route
### figure
- figure_digitization_failed: 7
- insufficient_evidence: 6
- missing_area: 10
- missing_endpoint: 2
- not_target_api: 13
- not_target_device: 21
- not_target_study_type: 12
- percent_only: 7
- unit_normalization_failed: 18
### mixed
- insufficient_evidence: 6
- missing_api_concentration: 4
- missing_area: 5
- missing_endpoint: 14
- missing_endpoint_time: 4
- not_target_api: 6
- not_target_device: 10
- not_target_study_type: 4
- percent_only: 3
- unit_normalization_failed: 1
### table
- missing_area: 16
- not_target_api: 8
- not_target_device: 7
- not_target_study_type: 2
- percent_only: 2
### text
- missing_area: 5
- not_target_device: 5

## Figure Stage Counts
- digitized_curves: 26
- digitized_endpoints_failed: 1
- digitized_endpoints_ok: 26
- mapped_curves: 26
- triage_artifacts: 14
- triage_digitize_candidates: 14
- unmapped_curves: 0

## Figure Gate Counts
- routed_candidates: 23
- after_gate: 15
- skipped:missing_explicit_figure_signal: 8

## Figure Triage Routes
- digitize: 14

## Figure Triage Signals
- endpoint_curve_present:no: 1

## Figure Digitization Statuses
- fail_missing_axis_range: 1
- ok: 26

## Figure Mapping Statuses
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
- downloaded: 229
- error: 1
- resolved: 82
- unresolved: 230
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- content_appears_to_be_a_review_not_directly_extracting_experimental_data: 1
- content_appears_to_be_primarily_about_drug_separation_modeling_specifics_about_i: 1
- content_appears_to_pertain_to_microemulsions_and_drug_delivery_but_does_not_spec: 1
- content_does_not_provide_extraction_specificities: 1
- content_does_not_relate_to_ibuprofen_or_diffusion_studies: 1
- content_extraction_inconclusive_due_to_lack_of_specific_evidence_details: 1
- content_may_discuss_formulation_but_lacks_explicit_evidence_extractable: 1
- details_on_endpoints_and_formulations_not_extractable_from_the_provided_text: 1
- document_content_does_not_provide_sufficient_information_for_extraction: 1
- document_content_primarily_contains_navigation_and_access_information_rather_tha: 1
- document_does_not_provide_relevant_details_for_extraction: 1
- document_lacks_relevant_information_regarding_ibuprofen_diffusion_cells_and_endp: 1
- document_lacks_specific_evidence_about_ibuprofen_or_relevant_diffusion_cells: 1
- document_provides_no_relevant_information_regarding_ibuprofen_or_dermal_formulat: 1
- document_text_does_not_provide_discernible_data_related_to_ibuprofen_or_diffusio: 1
- evidence_from_structured_title_indicates_focus_on_ibuprofen_and_franz_diffusion_: 1
- evidence_not_extractable_from_the_provided_text: 1
- extractable_information_on_ibuprofen_formulation_and_endpoint_is_unclear: 1
- extraction_evidence_is_limited_based_on_the_provided_content: 1
- extraction_routes_cannot_be_determined_due_to_insufficient_information_in_the_pr: 1
- focus_on_validation_of_diffusion_cell_system_for_permeation_studies: 1
- insufficient_content_from_the_document_to_extract_specific_evidence: 1
- insufficient_content_provided_to_determine_relevant_evidence_regarding_ibuprofen: 1
- insufficient_data_available_for_extraction: 1
- insufficient_data_on_formulation_and_endpoints: 1
- insufficient_detail_in_provided_text_to_confirm_relevant_extraction_points: 1
- insufficient_detailed_evidence_available: 1
- insufficient_evidence_in_the_document: 1
- insufficient_evidence_present_in_document_for_extraction: 1
- insufficient_extractable_evidence_in_the_provided_text: 1
- insufficient_information_in_the_text_to_derive_specific_evidence: 1
- insufficient_information_provided_in_the_document_to_identify_key_details_releva: 1
- insufficient_information_provided_in_the_text_to_determine_extraction_route: 1
- insufficient_information_regarding_ibuprofen_or_diffusion_studies: 1
- insufficient_information_to_determine_extraction_routes: 1
- insufficient_information_to_extract_relevant_evidence: 1
- lacks_specific_evidence_related_to_ibuprofen_or_diffusion_cells_in_the_provided_: 1
- limited_information_available_for_extraction: 1
- missing_structured_and_pdf_router_source: 243
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 64
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- needs_to_access_further_sections_for_detailed_extraction: 1
- no_evidence_related_to_ibuprofen_diffusion_cell_or_endpoints_found: 1
- no_extractable_content_found_related_to_ibuprofen: 1
- no_extractable_evidence_could_be_identified_and_the_document_context_is_not_full: 1
- no_extractable_evidence_found: 2
- no_extractable_evidence_found_in_provided_text: 1
- no_extractable_evidence_found_in_the_document: 1
- no_extractable_evidence_found_in_the_provided_document_text: 1
- no_extractable_evidence_found_in_the_provided_text: 2
- no_extractable_evidence_identified_due_to_incomplete_document_content: 1
- no_information_directly_extractable_from_provided_text: 1
- no_relevant_content_for_oa_or_ibuprofen_focuses_on_skin_cancers_and_molecular_me: 1
- no_relevant_content_related_to_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_content_was_found_in_the_provided_document_text: 1
- no_relevant_data_found_in_the_document_section_provided: 1
- no_relevant_data_related_to_ibuprofen_or_diffusion_studies_in_the_provided_text: 1
- no_relevant_evidence_available_in_the_extracted_text: 1
- no_relevant_evidence_extractable_from_the_provided_text: 1
- no_relevant_evidence_extracted: 2
- no_relevant_evidence_found_in_the_provided_document: 1
- no_relevant_evidence_found_in_the_provided_text: 1
- no_relevant_evidence_related_to_ibuprofen_dermal_formulation_found: 1
- no_relevant_extractable_evidence_found: 1
- no_relevant_extractable_evidence_found_in_the_provided_text: 2
- no_relevant_extractable_evidence_found_in_the_supplied_text: 1
- no_relevant_extractable_evidence_related_to_ibuprofen_dermal_formulation: 1
- no_relevant_extraction_evidence_found: 1
- no_relevant_extraction_information_found_in_the_document: 1
- no_relevant_extraction_points_found_the_document_focuses_on_catalytic_ozonation_: 1
- no_relevant_information_about_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_available_from_the_provided_text: 1
- no_relevant_information_available_regarding_ibuprofen_diffusion_cells_or_endpoin: 1
- no_relevant_information_detected_from_the_document_provided: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_dermal_formulation_in_t: 1
- no_relevant_information_found_in_the_document_regarding_ibuprofen_or_formulation: 1
- no_relevant_information_found_in_the_provided_pages: 1
- no_relevant_information_found_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_is_present_in: 1
- no_relevant_information_related_to_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_specific_evidence_about_ibuprofen_or_its_formulation_found_document_appears_t: 1
- no_specific_evidence_extractable_at_this_time: 1
- no_specific_evidence_extractable_from_the_provided_text: 1
- no_specific_extractable_evidence_found_in_the_visible_text: 1
- no_specific_references_to_ibuprofen_or_diffusion_cells_detected_in_the_provided_: 1
- no_visible_information_about_ibuprofen_diffusion_cells_or_specific_endpoints: 1
- only_a_partial_view_of_the_document_is_available: 1
- only_the_initial_pages_were_scanned_no_relevant_data_found: 1
- page_content_suggests_some_interaction_study_but_lacks_clarity_on_barried_types_: 1
- paper_discusses_adaptations_related_to_ibuprofen_but_lacks_clear_extractable_evi: 1
- paper_focuses_on_intravenous_administration_of_hydrophobic_apis_no_relevant_info: 1
- paper_focuses_on_topical_treatments_for_pain_details_on_ibuprofen_formulations_m: 1
- the_content_does_not_provide_sufficient_extractable_evidence_about_ibuprofen_or_: 1
- the_document_appears_to_be_a_clinical_investigation_but_specific_details_regardi: 1
- the_document_appears_to_be_a_review_on_metal_organic_frameworks_and_does_not_spe: 1
- the_document_appears_to_be_a_web_page_with_no_relevant_study_data: 1
- the_document_appears_to_be_an_article_listing_with_no_relevant_extractable_evide: 1
- the_document_appears_to_be_from_a_website_hosting_basic_information_rather_than_: 1
- the_document_appears_to_be_mostly_navigation_and_does_not_provide_specific_study: 1
- the_document_appears_to_be_primarily_introductory_and_does_not_contain_specific_: 1
- the_document_appears_to_focus_on_the_synthesis_and_functionalization_of_a_metal_: 1
- the_document_appears_to_only_have_page_numbers_and_metadata_that_are_not_directl: 1
- the_document_content_from_the_link_provided_does_not_contain_relevant_informatio: 1
- the_document_does_not_contain_relevant_extractable_evidence_related_to_the_speci: 1
- the_document_does_not_contain_relevant_information: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_dermal: 1
- the_document_does_not_contain_specific_evidence_related_to_ibuprofen_diffusion_c: 1
- the_document_does_not_explicitly_mention_ibuprofen_or_any_diffusion_cells: 1
- the_document_does_not_provide_clear_endpoints_or_diffusion_details: 1
- the_document_does_not_provide_clear_information_about_ibuprofen_or_related_formu: 1
- the_document_does_not_provide_clear_information_relevant_to_the_extraction_point: 1
- the_document_does_not_provide_explicit_information_related_to_ibuprofen_diffusio: 1
- the_document_does_not_provide_extractable_evidence_relevant_to_ibuprofen_dermal_: 1
- the_document_does_not_provide_measurable_data_or_evidence_specific_to_ibuprofen: 1
- the_document_does_not_provide_relevant_evidence_for_ibuprofen_or_related_dermal_: 1
- the_document_does_not_provide_relevant_information_related_to_dermal_formulation: 1
- the_document_does_not_provide_sufficient_details_for_more_specific_extraction: 1
- the_document_does_not_provide_sufficient_information_for_detailed_extraction: 1
- the_document_does_not_provide_sufficient_information_related_to_ibuprofen_or_dif: 1
- the_document_does_not_provide_sufficient_information_to_extract_clear_evidence_r: 1
- the_document_does_not_relate_to_ibuprofen_or_dermal_formulations: 1
- the_document_doesn_t_contain_specific_evidence_related_to_ibuprofen_or_diffusion: 1
- the_document_extracts_provided_do_not_contain_relevant_information_on_ibuprofen_: 1
- the_document_mainly_includes_navigation_elements_and_does_not_provide_any_substa: 1
- the_document_mainly_provides_a_service_update_rather_than_specific_research_cont: 1
- the_document_only_contains_metadata_and_lacks_actual_content_for_extraction: 1
- the_document_primarily_appears_to_be_access_related_content_rather_than_the_rese: 1
- the_document_primarily_consists_of_backend_information_without_extractable_evide: 1
- the_document_primarily_consists_of_non_structured_content_and_does_not_provide_c: 1
- the_document_primarily_contains_metadata_and_does_not_provide_clear_evidence_for: 1
- the_document_primarily_contains_metadata_and_lacks_specific_details_relevant_for: 1
- the_document_primarily_discusses_a_mucilage_from_lepidium_sativum_and_does_not_a: 1
- the_document_primarily_discusses_ibuprofen_delivered_via_nanoparticles_for_cance: 1
- the_document_primarily_provides_an_overview_without_structured_evidence_on_the_e: 1
- the_document_provided_consists_only_of_metadata_and_does_not_contain_any_content: 1
- the_document_provided_does_not_contain_useful_evidence_for_extraction_it_consist: 1
- the_document_requires_javascript_to_function_contents_not_directly_extractable: 1
- the_document_seems_to_be_a_cover_page_or_a_placeholder_without_any_research_cont: 1
- the_document_seems_to_be_structured_incorrectly_making_it_difficult_to_extract_s: 1
- the_document_text_provided_is_limited_and_does_not_contain_sufficient_informatio: 1
- the_paper_does_not_focus_on_dermal_formulations_or_ibuprofen: 1
- the_paper_focuses_on_a_chitosan_based_hydrogel_formulation_for_ibuprofen_but_spe: 1
- the_paper_focuses_on_the_theoretical_analysis_of_a_bioreactor_without_practical_: 1
- the_paper_investigates_cytotoxic_activity_of_drug_conjugates_but_lacks_details_o: 1
- this_paper_is_a_review_of_therapeutic_options_for_chronic_rhinosinusitis_in_cyst: 1
- unspecified: 38
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
- applied: 7
- skipped: 4
#### patch_area
- applied: 11
- skipped: 61
#### patch_endpoint_time
- applied: 26
- skipped: 4
#### patch_endpoint_value
- applied: 14
- skipped: 16

## Patch Success Counts
- patch_api_concentration: 7
- patch_area: 11
- patch_endpoint_time: 26
- patch_endpoint_value: 14