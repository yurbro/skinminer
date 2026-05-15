# Run Report: run_d232c729331e

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `95`
- Final records evaluated: `95`
- Actually verified: `8`
- Final unresolved: `66`
- Final rejected: `21`

## Route Distribution
- figure: 19
- mixed: 4
- table: 18
- text: 11
- unresolved: 487

## Extractor Outputs
- figure: 28
- table: 67
- text: 14

## Verification Outcomes
- rejected: 21
- unresolved: 66
- verified: 8

## Scope Buckets
- out_of_scope: 9
- recoverable_unresolved: 52
- strict_in_scope: 8
- useful_but_out_of_scope: 26

## Scope Tags
- non_target_api: 9
- recoverable_api_basis: 23
- recoverable_area: 10
- recoverable_endpoint: 7
- recoverable_endpoint_time: 2
- recoverable_figure_digitization: 1
- recoverable_support_gap: 39
- recoverable_unit_normalization: 6
- recoverable_unresolved: 52
- useful_api_concentration_out_of_scope: 15
- useful_but_out_of_scope: 26
- useful_device_out_of_scope: 5
- useful_endpoint_out_of_scope: 5
- useful_study_type_out_of_scope: 7

## Failure Taxonomy
- ambiguous_api_concentration: 33
- figure_digitization_failed: 2
- insufficient_evidence: 64
- missing_api_concentration: 7
- missing_area: 19
- missing_endpoint: 8
- missing_endpoint_time: 2
- not_target_api: 9
- not_target_api_concentration: 16
- not_target_device: 5
- not_target_study_type: 11
- percent_only: 9
- unit_normalization_failed: 6

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 18
- figure_digitization_failed: 2
- insufficient_evidence: 31
- missing_api_concentration: 4
- missing_area: 11
- missing_endpoint: 2
- not_target_api: 9
- not_target_api_concentration: 11
- not_target_device: 1
- not_target_study_type: 10
- percent_only: 9
- unit_normalization_failed: 4
### mixed
- ambiguous_api_concentration: 3
- insufficient_evidence: 18
- missing_api_concentration: 1
- missing_area: 1
- missing_endpoint: 4
- not_target_api_concentration: 2
- unit_normalization_failed: 1
### table
- ambiguous_api_concentration: 12
- insufficient_evidence: 11
- missing_api_concentration: 2
- missing_area: 7
- not_target_api_concentration: 3
- not_target_device: 4
- not_target_study_type: 1
- unit_normalization_failed: 1
### text
- insufficient_evidence: 4
- missing_endpoint: 2
- missing_endpoint_time: 2

## Figure Stage Counts
- digitized_curves: 31
- digitized_endpoints_failed: 0
- digitized_endpoints_ok: 31
- mapped_curves: 31
- triage_artifacts: 20
- triage_digitize_candidates: 17
- unmapped_curves: 0

## Figure Gate Counts
- routed_candidates: 22
- after_gate: 21
- skipped:missing_explicit_figure_signal: 1

## Figure Triage Routes
- digitize: 17
- skip: 3

## Figure Triage Signals
- digitizable:no: 2
- digitizable:uncertain: 1
- endpoint_curve_present:no: 2
- endpoint_curve_present:uncertain: 1
- recommended_route:skip: 3
- ticks_readable:no: 2
- ticks_readable:uncertain: 2
- why_not_digitizable:curves_and_data_are_not_provided_in_a_format_suitable_for_digitization: 1
- why_not_digitizable:curves_not_identifiable_no_clear_endpoints_to_digitize: 1
- why_not_digitizable:insufficient_visible_data_on_curves_or_y_axis_values: 1

## Figure Digitization Statuses
- ok: 31

## Figure Mapping Statuses
- vision_mapped: 31

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
- downloaded: 220
- error: 1
- resolved: 95
- unresolved: 223
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- cannot_extract_definitive_evidence_related_to_the_framework_based_on_the_provide: 1
- cannot_extract_specific_evidence_related_to_ibuprofen_or_diffusion_cells_from_th: 1
- content_does_not_appear_to_contain_relevant_evidence_related_to_ibuprofen_or_der: 1
- content_does_not_provide_specific_evidence_related_to_ibuprofen_or_dermal_formul: 1
- content_focused_on_ibuprofen_release_monitoring_methods: 1
- content_from_pdf_extraction_indicates_experiments_related_to_ibuprofen_permeatio: 1
- content_is_mostly_about_the_web_interface_and_does_not_provide_direct_data_or_fi: 1
- content_not_extractable_from_provided_text: 1
- content_not_relevant_to_ibuprofen_dermal_formulation: 1
- document_appears_to_be_a_general_reference_page_with_no_relevant_data_on_ibuprof: 1
- document_appears_to_focus_on_naproxen_and_famotidine_no_relevant_details_on_ibup: 1
- document_appears_to_focus_on_ocular_drug_discovery_and_development_no_specific_m: 1
- document_contains_navigation_and_access_information_no_relevant_data_appears_to_: 1
- document_content_is_not_extractable_from_the_provided_text: 1
- document_content_not_accessible_for_extraction: 1
- document_content_not_fully_accessible_unable_to_extract_specific_details: 1
- document_content_primarily_consists_of_navigational_elements_and_does_not_provid: 1
- document_does_not_contain_specific_extractable_evidence_regarding_diffusion_cell: 1
- document_does_not_provide_relevant_evidence_appears_to_be_unrelated_to_ibuprofen: 1
- document_does_not_provide_specific_extractable_evidence_related_to_ibuprofen_or_: 1
- evidence_extraction_details_are_currently_unavailable_from_the_provided_text: 1
- evidence_extraction_details_require_more_text_from_the_document: 1
- evidence_extraction_is_currently_impeded_by_incomplete_document_text: 1
- evidence_extraction_is_uncertain_based_on_the_provided_text_mainly_due_to_lack_o: 1
- evidence_extraction_route_is_unclear_based_on_provided_text: 1
- evidence_extraction_route_unclear_due_to_lack_of_detailed_content_provided: 1
- evidence_not_extractable_from_provided_text_mainly_metadata_and_header: 1
- evidence_regarding_ibuprofen_is_present_but_specifics_like_diffusion_cells_or_fr: 1
- evidence_routing_is_not_possible_due_to_lack_of_extractable_data_in_provided_pag: 1
- extraction_details_not_found_in_the_provided_text: 1
- further_details_needed_to_clarify_extraction_routes: 1
- information_regarding_ibuprofen_and_diffusion_methods_not_explicitly_mentioned: 1
- initial_pages_do_not_contain_relevant_extraction_evidence: 1
- initial_pages_do_not_provide_detailed_content_or_structure_relevant_for_more_spe: 1
- initial_pages_do_not_provide_substantive_content_related_to_ibuprofen_or_diffusi: 1
- insufficient_evidence_for_detailed_extraction: 1
- insufficient_evidence_in_the_provided_document_section_for_specific_extraction: 1
- insufficient_evidence_provided_in_the_document_to_determine_extraction_details: 1
- insufficient_information_available_in_provided_text: 1
- insufficient_information_available_to_identify_extraction_route: 1
- insufficient_information_in_the_document_for_extraction: 1
- insufficient_information_in_the_document_to_determine_extraction_routes: 1
- insufficient_information_to_determine_specific_details_regarding_diffusion_cell_: 1
- insufficient_information_to_extract_relevant_evidence_regarding_ibuprofen_dermal: 1
- limited_information_available_from_the_provided_document_context: 1
- missing_structured_and_pdf_router_source: 234
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 80
- missing_structured_and_pdf_router_source_html_remote_httperror: 1
- no_clear_extractable_evidence_regarding_ibuprofen_or_diffusion_cells: 1
- no_clear_extractable_evidence_was_identified_in_the_provided_content: 1
- no_evidence_related_to_ibuprofen_or_diffusion_cells_found_in_the_provided_text: 1
- no_explicit_extractable_evidence_found_in_the_provided_document_text: 1
- no_extractable_evidence_found: 2
- no_extractable_evidence_found_in_available_content: 1
- no_extractable_evidence_found_in_the_provided_document_text: 1
- no_extractable_evidence_found_in_the_provided_pages: 1
- no_extractable_evidence_found_in_the_text_provided: 1
- no_extractable_evidence_found_within_the_text_provided: 1
- no_extractable_evidence_or_specific_data_found_within_the_provided_text: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cells: 1
- no_extractable_structured_information_found: 1
- no_relevant_content_extracted_regarding_ibuprofen_formulations: 1
- no_relevant_content_for_ibuprofen_dermal_formulation_extraction: 1
- no_relevant_content_identified_from_the_pdf: 1
- no_relevant_content_relating_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_data_on_ibuprofen_or_diffusion_cell_found_in_the_provided_text: 1
- no_relevant_evidence_for_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_evidence_found_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulation_is_present: 1
- no_relevant_extractable_evidence_available_from_the_supplied_document_text: 1
- no_relevant_extractable_evidence_related_to_ibuprofen_or_diffusion_cells_found_i: 1
- no_relevant_extraction_could_be_performed_from_the_provided_document_content: 1
- no_relevant_information_about_ibuprofen_or_dermal_formulation_found_in_the_docum: 1
- no_relevant_information_concerning_ibuprofen_or_its_dermal_formulation_is_availa: 1
- no_relevant_information_currently_available_in_the_provided_document: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_diffusion_cells: 2
- no_relevant_information_for_extraction_found_in_the_provided_document: 1
- no_relevant_information_for_ibuprofen_dermal_formulations_found_in_the_provided_: 1
- no_relevant_information_found_in_the_provided_document: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_found_in_the_provided_te: 1
- no_relevant_information_provided_from_the_document: 1
- no_specific_extractable_evidence_found_in_the_provided_text: 1
- not_enough_extractable_evidence_available_from_the_provided_document_pages: 1
- not_enough_extractable_evidence_available_from_the_supplied_document: 1
- not_enough_information_provided: 1
- not_enough_information_provided_in_the_text_for_detailed_extraction: 1
- summary_indicates_it_s_about_a_fibrous_membrane_with_ibuprofen_specifics_on_meth: 1
- the_content_provided_does_not_include_specific_information_related_to_ibuprofen_: 1
- the_content_was_unextractable_the_document_appears_to_be_a_web_portal_without_sp: 1
- the_document_cannot_be_extracted_as_it_appears_to_be_an_introductory_page_with_n: 1
- the_document_content_does_not_provide_relevant_extraction_points: 1
- the_document_content_does_not_provide_sufficient_data_for_detailed_extraction: 1
- the_document_content_is_incomplete_for_further_extraction: 1
- the_document_did_not_provide_explicit_data_or_references_related_to_ibuprofen_or: 1
- the_document_discusses_microneedles_in_the_context_of_enhanced_drug_delivery_imp: 1
- the_document_does_not_contain_clear_information_about_diffusion_cell_or_franz_ce: 1
- the_document_does_not_contain_extractable_evidence_about_ibuprofen_or_diffusion_: 1
- the_document_does_not_provide_clear_extractable_evidence_related_to_ibuprofen_or: 1
- the_document_does_not_provide_clear_sections_relevant_to_extraction: 1
- the_document_does_not_provide_detailed_evidence_relevant_to_dermal_formulation_o: 1
- the_document_does_not_provide_detailed_information_relevant_to_the_extraction_qu: 1
- the_document_does_not_provide_extractable_evidence_related_to_ibuprofen_or_diffu: 1
- the_document_does_not_provide_relevant_evidence_for_ibuprofen_dermal_formulation: 1
- the_document_does_not_provide_relevant_extractable_evidence_for_ibuprofen_dermal: 1
- the_document_does_not_provide_relevant_information_on_ibuprofen_or_dermal_formul: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_or_its_fo: 1
- the_document_does_not_provide_specific_details_on_ibuprofen_or_related_diffusion: 1
- the_document_does_not_provide_specific_extractable_evidence_regarding_ibuprofen_: 1
- the_document_does_not_provide_sufficient_data_for_detailed_extraction: 1
- the_document_does_not_provide_sufficient_information_regarding_ibuprofen_or_a_di: 1
- the_document_does_not_provide_sufficient_information_regarding_ibuprofen_or_rele: 1
- the_document_does_not_seem_to_relate_to_ibuprofen_or_dermal_formulations: 1
- the_document_has_not_provided_content_related_to_extraction: 1
- the_document_mainly_consists_of_metadata_and_lacks_specific_experimental_details: 1
- the_document_preview_does_not_provide_enough_relevant_content_for_extraction: 1
- the_document_primarily_consists_of_navigation_and_help_information_for_europe_pm: 1
- the_document_primarily_contains_structured_information_about_europe_pmc_and_does: 1
- the_document_primarily_discusses_a_hybrid_system_for_ibuprofen_removal_specific_: 1
- the_document_primarily_includes_non_research_related_content_further_details_are: 1
- the_document_provided_does_not_contain_relevant_extractable_evidence_related_to_: 1
- the_document_s_content_was_not_fully_retrieved_making_it_difficult_to_determine_: 1
- the_document_seems_to_be_more_focused_on_acetylcholinesterase_modulation_rather_: 1
- the_document_text_did_not_provide_enough_information_to_determine_specific_evide: 1
- the_emphasis_is_on_the_validation_of_the_franz_diffusion_cell_system_rather_than: 1
- the_paper_appears_to_focus_on_ibuprofen_derived_nitric_oxide_donors_in_the_conte: 1
- the_paper_discusses_ibuprofen_loaded_formulations_but_does_not_contain_clear_str: 1
- the_paper_focuses_on_supercritical_co_assisted_spray_drying_and_does_not_seem_to: 1
- the_provided_document_text_does_not_contain_any_extractable_evidence_related_to_: 1
- the_provided_text_does_not_contain_relevant_details_for_extraction: 1
- the_provided_text_does_not_contain_relevant_evidence_related_to_ibuprofen_or_the: 1
- the_provided_text_does_not_contain_relevant_information_related_to_ibuprofen: 1
- the_source_document_appears_to_contain_navigation_and_access_instructions_rather: 1
- the_title_mentions_ibuprofen_but_specific_evidence_extraction_details_are_unclea: 1
- unable_to_extract_clear_evidence_due_to_limited_content_provided: 1
- unspecified: 37
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
- applied: 8
- skipped: 78
#### patch_area
- applied: 7
- skipped: 49
#### patch_endpoint_time
- applied: 19
- skipped: 2
#### patch_endpoint_value
- applied: 35
- skipped: 53

## Patch Success Counts
- patch_api_concentration: 8
- patch_area: 7
- patch_endpoint_time: 19
- patch_endpoint_value: 35