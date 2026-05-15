# Run Report: run_641fa8baadd3

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `81`
- Final records evaluated: `81`
- Actually verified: `9`
- Final unresolved: `31`
- Final rejected: `41`

## Route Distribution
- figure: 18
- mixed: 5
- table: 14
- text: 11
- unresolved: 484

## Extractor Outputs
- figure: 19
- table: 53
- text: 13

## Verification Outcomes
- rejected: 41
- unresolved: 31
- verified: 9

## Scope Buckets
- out_of_scope: 4
- recoverable_unresolved: 27
- strict_in_scope: 9
- useful_but_out_of_scope: 41

## Scope Tags
- non_target_api: 4
- recoverable_api_basis: 15
- recoverable_area: 2
- recoverable_support_gap: 19
- recoverable_unresolved: 27
- useful_api_concentration_out_of_scope: 12
- useful_but_out_of_scope: 41
- useful_device_out_of_scope: 37
- useful_endpoint_out_of_scope: 2
- useful_study_type_out_of_scope: 9

## Failure Taxonomy
- ambiguous_api_concentration: 33
- figure_digitization_failed: 5
- insufficient_evidence: 48
- missing_api_concentration: 1
- missing_area: 16
- missing_endpoint: 12
- missing_endpoint_time: 6
- not_target_api: 4
- not_target_api_concentration: 14
- not_target_device: 40
- not_target_study_type: 9
- percent_only: 3

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 15
- figure_digitization_failed: 5
- insufficient_evidence: 24
- missing_area: 9
- missing_endpoint: 5
- not_target_api: 1
- not_target_api_concentration: 8
- not_target_device: 21
- not_target_study_type: 6
- percent_only: 3
### mixed
- ambiguous_api_concentration: 5
- insufficient_evidence: 12
- missing_area: 3
- missing_endpoint: 5
- missing_endpoint_time: 4
- not_target_api: 2
- not_target_api_concentration: 2
- not_target_device: 7
- not_target_study_type: 1
### table
- ambiguous_api_concentration: 13
- insufficient_evidence: 3
- missing_api_concentration: 1
- missing_area: 3
- not_target_api: 1
- not_target_api_concentration: 4
- not_target_device: 10
- not_target_study_type: 2
### text
- insufficient_evidence: 9
- missing_area: 1
- missing_endpoint: 2
- missing_endpoint_time: 2
- not_target_device: 2

## Figure Stage Counts
- digitized_curves: 19
- digitized_endpoints_failed: 2
- digitized_endpoints_ok: 19
- mapped_curves: 19
- triage_artifacts: 17
- triage_digitize_candidates: 16
- unmapped_curves: 0

## Figure Gate Counts
- routed_candidates: 22
- after_gate: 18
- skipped:missing_explicit_figure_signal: 4

## Figure Triage Routes
- digitize: 16
- skip: 1

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 2
- recommended_route:skip: 1
- ticks_readable:no: 2
- why_not_digitizable:no_clear_endpoint_curves_for_digitization_found: 1
- why_not_digitizable:undefined: 1

## Figure Digitization Statuses
- fail_missing_axis_range: 2
- ok: 19

## Figure Mapping Statuses
- vision_mapped: 19

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 0
- priority_bucket:none
- review_focus:none
- none
- disagreement:none

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-03-28.v1
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1

## Blockage Summary
### Access Statuses
- downloaded: 223
- error: 1
- resolved: 90
- unresolved: 218
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- additional_text_extraction_needed_for_specific_evidence: 1
- content_does_not_appear_to_contain_relevant_evidence_for_ibuprofen_formulations: 1
- content_does_not_provide_clear_evidence_regarding_ibuprofen_diffusion_cells_or_e: 1
- content_does_not_provide_relevant_information_for_extraction: 1
- content_extraction_inconclusive_from_provided_pages: 1
- content_extraction_not_possible_document_appears_to_have_a_technical_focus_not_d: 1
- content_from_pages_1_2_is_primarily_navigation_and_does_not_provide_relevant_sci: 1
- content_is_not_extractable_lacks_relevant_information_about_ibuprofen_or_diffusi: 1
- content_is_primarily_related_to_the_effect_of_vehicles_on_percutaneous_absorptio: 1
- content_not_extractable_due_to_lack_of_substantive_content_in_the_provided_text: 1
- content_primarily_consists_of_technical_and_navigation_details_lacking_substanti: 1
- content_provided_does_not_give_information_on_formulations_or_endpoints: 1
- detailed_extraction_is_not_possible_from_provided_text_further_information_requi: 1
- document_appears_to_be_largely_introductory_and_lacks_specific_extractable_evide: 1
- document_content_does_not_provide_relevant_evidence_for_ibuprofen_dermal_formula: 1
- document_content_is_insufficient_to_determine_explicit_evidence_extraction_route: 1
- document_does_not_contain_evidence_related_to_ibuprofen_or_dermal_formulations: 1
- document_does_not_provide_specific_sections_with_extractable_evidence_on_ibuprof: 1
- document_does_not_seem_relevant_to_ibuprofen_dermal_formulations: 1
- document_extracts_no_clear_structured_data: 1
- document_provides_insufficient_detail_for_extraction: 1
- document_text_does_not_provide_relevant_details_for_extraction: 1
- evidence_extraction_not_possible_from_the_available_content: 1
- evidence_extraction_requires_further_details_from_the_body_of_the_paper_currentl: 1
- evidence_not_extractable_from_the_provided_document: 1
- extractable_evidence_is_uncertain_due_to_restricted_document_access: 1
- extractable_evidence_regarding_ibuprofen_and_formulation_characteristics_is_pres: 1
- extraction_route_currently_unclear_from_provided_content: 1
- full_text_not_available_extractable_evidence_cannot_be_determined_from_provided_: 1
- ibuprofen_is_mentioned_as_a_non_steroidal_anti_inflammatory_drug_that_interacts_: 1
- insufficient_content_available_for_detailed_extraction: 1
- insufficient_content_available_for_extraction: 1
- insufficient_content_from_the_document_retrieved: 1
- insufficient_detail_available_for_deeper_extraction: 1
- insufficient_information_available_for_extraction: 1
- insufficient_information_available_from_the_document_to_extract_relevant_evidenc: 1
- insufficient_information_available_to_determine_extraction_routes_for_oa_related: 1
- insufficient_information_extracted_from_the_document_for_further_classification: 1
- insufficient_information_for_extraction_from_the_document: 1
- insufficient_information_to_determine_extraction_routes: 1
- insufficient_information_to_determine_relevant_extraction_pathways: 1
- insufficient_information_to_determine_specific_extraction_details: 1
- insufficient_information_to_extract_relevant_evidence_related_to_ibuprofen_or_de: 1
- insufficient_relevant_content_to_determine_extraction_specifics: 1
- limited_extractable_evidence_from_provided_text_primarily_focused_on_ibuprofen_a: 1
- minimal_extractable_evidence_due_to_incomplete_content: 1
- missing_structured_and_pdf_router_source: 231
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 70
- missing_structured_and_pdf_router_source_html_remote_connecttimeout: 1
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- need_to_check_internal_sections_for_specific_experimental_details: 1
- needs_further_examination_of_the_paper_for_specific_diffusion_or_endpoint_detail: 1
- no_clear_evidence_extractable_from_supplied_text: 1
- no_clear_extractable_evidence_found_in_the_provided_text: 1
- no_direct_extraction_evidence_related_to_ibuprofen_or_diffusion_cells: 1
- no_explicit_evidence_extraction_found_in_provided_text: 1
- no_extractable_evidence_could_be_identified_from_the_provided_document_text: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_in_provided_text: 3
- no_extractable_evidence_found_in_the_pages_provided: 1
- no_extractable_evidence_found_in_the_provided_document: 2
- no_extractable_evidence_found_in_the_provided_document_snippet: 1
- no_extractable_evidence_found_in_the_provided_pages: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_found_in_the_provided_text_from_the_document: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cell: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cell_found_in_the_prov: 1
- no_relevant_content_extractable_from_provided_document: 1
- no_relevant_content_for_extraction_found: 1
- no_relevant_content_identified_pertaining_to_ibuprofen_dermal_formulations: 1
- no_relevant_evidence_found_in_provided_text: 1
- no_relevant_evidence_found_in_the_extracted_text: 1
- no_relevant_evidence_found_related_to_the_specified_parameters: 1
- no_relevant_evidence_pertaining_to_ibuprofen_dermal_formulation_found: 1
- no_relevant_evidence_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_extractable_evidence_related_to_ibuprofen_dermal_formulation_found: 1
- no_relevant_extraction_evidence_found_related_to_ibuprofen_or_dermal_formulation: 1
- no_relevant_extraction_evidence_is_available_based_on_the_given_text: 1
- no_relevant_information_about_ibuprofen_or_diffusion_cells_extracted_from_the_do: 1
- no_relevant_information_about_ibuprofen_or_diffusion_cells_found_in_the_provided: 1
- no_relevant_information_about_ibuprofen_or_diffusion_studies_identified: 1
- no_relevant_information_about_ibuprofen_or_related_formulations: 1
- no_relevant_information_extracted_from_the_document: 1
- no_relevant_information_extracted_related_to_ibuprofen_or_dermal_formulation: 1
- no_relevant_information_found_in_the_provided_document_blocks: 1
- no_relevant_information_found_in_the_provided_text: 2
- no_relevant_information_found_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_found_regarding_ibuprofen_or_formulation_details_in_the_: 1
- no_relevant_information_found_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_on_ibuprofen_formulations_or_diffusion_cells: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cell_found: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_is_present_in_the: 1
- no_specific_data_on_ibuprofen_or_related_drug_formulations_found_in_the_text: 1
- no_specific_details_extracted_due_to_incomplete_content: 1
- no_specific_evidence_details_provided_in_the_available_text: 1
- only_mentions_ibuprofen_additional_details_not_available: 1
- only_page_1_is_available_no_extractable_evidence_present: 1
- the_content_does_not_provide_specific_details_about_diffusion_cells_or_endpoints: 1
- the_content_from_the_document_is_insufficient_for_extraction: 1
- the_content_provided_does_not_offer_extractable_evidence_related_to_the_specific: 1
- the_content_provided_is_primarily_administrative_and_does_not_include_relevant_s: 1
- the_document_appears_to_be_a_review_and_does_not_mention_ibuprofen_or_diffusion_: 1
- the_document_appears_to_be_about_ibuprofen_s_effects_but_lacks_specific_data_reg: 1
- the_document_appears_to_focus_on_a_protocol_for_a_trial_and_may_not_contain_deta: 1
- the_document_appears_unrelated_to_ibuprofen_or_dermal_formulations: 1
- the_document_contains_no_specific_evidence_related_to_the_formulation_or_study_m: 1
- the_document_content_does_not_provide_extractable_evidence_related_to_ibuprofen_: 1
- the_document_content_is_not_accessible_it_appears_to_be_a_navigation_or_error_pa: 1
- the_document_content_provided_does_not_contain_relevant_information_for_extracti: 1
- the_document_does_not_appear_to_contain_relevant_evidence_regarding_ibuprofen_or: 1
- the_document_does_not_appear_to_contain_relevant_information_on_ibuprofen_or_der: 1
- the_document_does_not_contain_extractable_evidence_related_to_the_specified_crit: 1
- the_document_does_not_contain_identifiable_evidence_related_to_ibuprofen_or_diff: 1
- the_document_does_not_contain_relevant_information_for_ibuprofen_dermal_formulat: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_diffus: 1
- the_document_does_not_contain_relevant_information_related_to_ibuprofen_or_derma: 2
- the_document_does_not_contain_relevant_information_related_to_ibuprofen_or_diffu: 1
- the_document_does_not_contain_specific_evidence_regarding_ibuprofen_or_diffusion: 1
- the_document_does_not_provide_direct_evidence_extraction_opportunities_further_e: 1
- the_document_does_not_provide_relevant_evidence_regarding_ibuprofen_dermal_formu: 1
- the_document_does_not_provide_relevant_evidence_related_to_ibuprofen_or_dermal_f: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_or_diffus: 2
- the_document_does_not_provide_specific_extraction_routes_or_content_beyond_the_i: 1
- the_document_does_not_provide_sufficient_structured_data_to_extract_detailed_evi: 1
- the_document_does_not_provide_the_necessary_content_for_targeted_extraction_rega: 1
- the_document_does_not_provide_the_relevant_extraction_information_directly: 1
- the_document_focuses_on_the_permeation_of_ibuprofen_using_strat_m_membranes_and_: 1
- the_document_is_primarily_introductory_content_related_to_europe_pmc_and_does_no: 1
- the_document_primarily_discusses_a_hydrogel_formulation_containing_ibuprofen_for: 1
- the_document_primarily_discusses_methods_and_does_not_appear_to_focus_specifical: 1
- the_document_primarily_discusses_pharmaceuticals_in_wastewater_and_their_removal: 1
- the_document_primarily_mentions_tcm_plasters_and_does_not_discuss_ibuprofen_or_r: 1
- the_document_primarily_provides_general_information_without_specific_extractable: 1
- the_document_provided_does_not_contain_extractable_evidence_related_to_ibuprofen: 1
- the_document_text_does_not_provide_relevant_information_for_extraction: 1
- the_full_contents_of_the_paper_need_to_be_reviewed_to_accurately_determine_the_e: 1
- the_paper_appears_to_be_focused_on_the_action_of_ibuprofen_and_does_not_provide_: 1
- the_paper_discusses_mitochondrial_stress_and_inflammatory_signaling_but_does_not: 1
- the_paper_discusses_naproxen_and_famotidine_rather_than_ibuprofen: 1
- the_paper_explores_ibuprofen_functionalized_biomembranes_but_does_not_provide_cl: 1
- the_paper_focuses_on_nanoemulsions_for_intravenous_delivery_not_dermal_formulati: 1
- the_provided_document_pages_do_not_contain_relevant_evidence: 1
- this_paper_discusses_nsaids_and_their_effects_but_does_not_specifically_mention_: 1
- this_paper_reviews_the_biodegradation_of_nsaids_including_ibuprofen_but_does_not: 1
- this_study_validates_a_franz_diffusion_cell_system_for_in_vitro_studies_but_does: 1
- unable_to_extract_relevant_information_regarding_ibuprofen_dermal_formulation: 1
- unable_to_extract_specific_evidence_from_the_document_due_to_the_nature_of_the_t: 1
- unable_to_extract_specific_evidence_or_carriers_from_the_provided_text: 1
- unspecified: 28
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
- skipped: 68
#### patch_area
- applied: 7
- skipped: 34
#### patch_endpoint_time
- applied: 11
- skipped: 6
#### patch_endpoint_value
- applied: 25
- skipped: 49

## Patch Success Counts
- patch_area: 7
- patch_endpoint_time: 11
- patch_endpoint_value: 25