# Run Report: run_8c7c590695db

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `102`
- Final records evaluated: `102`
- Actually verified: `2`
- Final unresolved: `71`
- Final rejected: `29`

## Route Distribution
- figure: 20
- mixed: 8
- table: 18
- text: 7
- unresolved: 487

## Extractor Outputs
- figure: 21
- table: 78
- text: 12

## Verification Outcomes
- rejected: 29
- unresolved: 71
- verified: 2

## Scope Buckets
- out_of_scope: 4
- recoverable_unresolved: 68
- strict_in_scope: 2
- useful_but_out_of_scope: 28

## Scope Tags
- non_target_api: 4
- recoverable_unresolved: 68
- useful_but_out_of_scope: 28

## Failure Taxonomy
- ambiguous_api_concentration: 13
- ambiguous_mapping: 3
- figure_digitization_failed: 3
- insufficient_evidence: 87
- missing_api_concentration: 8
- missing_area: 16
- missing_endpoint: 7
- missing_endpoint_time: 4
- not_target_api: 4
- not_target_api_concentration: 8
- not_target_device: 23
- not_target_study_type: 7
- percent_only: 3
- unit_normalization_failed: 4

## Failure Taxonomy By Route
### figure
- ambiguous_mapping: 3
- figure_digitization_failed: 3
- insufficient_evidence: 54
- missing_api_concentration: 4
- missing_area: 8
- missing_endpoint: 3
- not_target_api: 3
- not_target_api_concentration: 1
- not_target_device: 11
- percent_only: 3
- unit_normalization_failed: 4
### mixed
- insufficient_evidence: 20
- missing_api_concentration: 3
- missing_area: 3
- missing_endpoint: 4
- missing_endpoint_time: 4
- not_target_api_concentration: 4
- not_target_device: 6
- not_target_study_type: 3
### table
- ambiguous_api_concentration: 13
- insufficient_evidence: 8
- missing_api_concentration: 1
- missing_area: 5
- not_target_api: 1
- not_target_api_concentration: 3
- not_target_device: 6
- not_target_study_type: 4
### text
- insufficient_evidence: 5

## Figure Stage Counts
- digitized_curves: 22
- digitized_endpoints_failed: 0
- digitized_endpoints_ok: 22
- mapped_curves: 21
- triage_artifacts: 18
- triage_digitize_candidates: 15
- unmapped_curves: 1

## Figure Gate Counts
- routed_candidates: 28
- after_gate: 20
- skipped:missing_explicit_figure_signal: 8

## Figure Triage Routes
- digitize: 15
- skip: 3

## Figure Triage Signals
- digitizable:no: 3
- endpoint_curve_present:no: 3
- recommended_route:skip: 3
- ticks_readable:no: 2
- ticks_readable:uncertain: 3
- why_not_digitizable:insufficient_data_for_digitization: 1
- why_not_digitizable:no_curves_detected_based_on_the_provided_figure: 1
- why_not_digitizable:no_endpoint_curves_are_present_in_the_image: 1

## Figure Digitization Statuses
- ok: 22

## Figure Mapping Statuses
- unmapped: 1
- vision_mapped: 21

## LLM Reliability
### detection.router
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 230
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.figure.map_curves
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 10
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.figure.triage
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 18
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.table
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 46
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.text
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 14
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### triage.llm_triage
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 749
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### verification.llm_adjudicate
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 14
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0

## LLM Adjudication Audit
- rows: 14
- priority_bucket:high: 11
- priority_bucket:medium: 3
- review_focus:api_concentration_basis: 8
- review_focus:diffusion_area: 3
- review_focus:endpoint_value: 2
- review_focus:unit_normalization: 1
- recommended_status:rejected: 3
- recommended_status:unresolved: 11
- disagreement:scope_bucket_disagreement: 3
- disagreement:status_disagreement: 3

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-03-28.v1
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1

## Blockage Summary
### Access Statuses
- downloaded: 226
- error: 1
- resolved: 87
- unresolved: 226
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- content_appears_to_be_from_title_and_initial_pages_without_detailed_extraction_e: 1
- content_does_not_provide_specific_details_on_formulations_or_endpoints: 1
- content_extraction_not_available_focuses_on_fluorescence_and_drug_delivery_mecha: 1
- content_from_the_document_is_not_extractable: 1
- content_mainly_focused_on_membrane_interaction_specifics_about_formulations_or_e: 1
- content_not_extractable_from_the_provided_text: 1
- content_not_provided_details_missing: 1
- document_appears_to_be_a_web_interface_or_platform_for_accessing_abstracts_or_ar: 1
- document_contains_elements_not_directly_usable_for_extraction: 1
- document_content_does_not_provide_relevant_data_for_extraction: 1
- document_content_does_not_provide_specific_information_regarding_ivpt_ivrt_barri: 1
- document_content_is_not_extractable_relevant_information_not_found: 1
- document_contents_do_not_provide_relevant_evidence_related_to_ibuprofen_or_formu: 1
- document_does_not_appear_to_contain_relevant_evidence_for_oa_ibuprofen_dermal_fo: 1
- document_does_not_provide_data_about_ibuprofen_or_diffusion_studies: 1
- document_does_not_provide_relevant_content_for_extraction: 1
- document_does_not_provide_specific_evidence_related_to_ibuprofen_or_the_methodol: 1
- document_text_does_not_contain_relevant_extraction_information: 1
- evidence_extractable_details_are_not_clear_from_the_provided_content: 1
- evidence_extraction_details_cannot_be_determined_from_the_provided_content: 1
- evidence_extraction_is_unclear_further_details_needed_from_the_document: 1
- evidence_extraction_route_unclear_due_to_lack_of_detailed_content: 1
- extractable_evidence_is_unclear_due_to_limited_available_content_and_lack_of_spe: 1
- extractable_evidence_is_unclear_from_provided_text: 1
- extractable_evidence_not_identifiable_from_the_provided_text: 1
- extraction_route_based_on_observation_of_ibuprofen_mention_and_primary_experimen: 1
- extraction_route_needs_further_information_from_the_document: 1
- focus_on_functionalized_biomembranes_for_wound_dressing_applications: 1
- further_context_required_from_document_for_detailed_extraction: 1
- initial_findings_suggest_the_formulation_s_effectiveness_but_details_are_limited: 1
- initial_pages_contain_europe_pmc_interface_information_no_relevant_content_extra: 1
- initial_pages_do_not_contain_relevant_information: 1
- initial_pages_do_not_contain_the_main_evidence_extraction_information: 1
- initial_pages_do_not_provide_content_related_to_extraction_further_analysis_of_t: 1
- insufficient_content_available_from_the_document_to_determine_extraction_routes: 1
- insufficient_content_extracted_to_determine_specific_evidence_regarding_ibuprofe: 1
- insufficient_content_provided_to_determine_detailed_extraction_routes: 1
- insufficient_content_to_extract_relevant_evidence: 1
- insufficient_data_available_to_determine_specific_extractable_evidence: 1
- insufficient_evidence_extractable_from_current_text: 1
- insufficient_evidence_in_the_provided_content_to_determine_specific_details: 1
- insufficient_extractable_evidence_in_the_provided_document: 1
- insufficient_information_available: 1
- insufficient_information_available_from_the_provided_text: 1
- insufficient_information_available_in_the_extracted_document: 1
- insufficient_information_available_to_determine_relevant_extraction_routes: 1
- insufficient_information_in_the_provided_text: 1
- insufficient_information_in_the_provided_text_to_determine_relevant_details_abou: 1
- insufficient_information_to_extract_specific_evidence_related_to_ibuprofen_or_de: 1
- limited_information_available_in_provided_text: 1
- missing_structured_and_pdf_router_source: 237
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 71
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- no_content_provided_in_the_document_for_extraction: 1
- no_evidence_extraction_routes_found_based_on_the_supplied_document: 1
- no_evidence_related_to_ibuprofen_or_diffusion_cells_was_found_in_the_provided_do: 1
- no_explicit_details_about_formulations_or_endpoints_are_provided_in_the_document: 1
- no_explicit_evidence_appears_to_be_extractable_from_the_provided_text: 1
- no_extractable_evidence_detected_in_the_provided_text: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_document_content_does_not_contain_structured_data: 1
- no_extractable_evidence_found_in_provided_document_text: 1
- no_extractable_evidence_found_in_the_document: 1
- no_extractable_evidence_found_in_the_provided_document_text: 2
- no_extractable_evidence_found_in_the_provided_text: 2
- no_extractable_evidence_from_the_provided_text: 1
- no_extractable_evidence_provided_in_the_text: 1
- no_information_found_relevant_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_content_found_about_ibuprofen_or_diffusion_cells: 1
- no_relevant_content_related_to_ibuprofen_formulation_or_diffusion_cell_found_in_: 1
- no_relevant_data_found_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_details_found_in_the_text_provided: 1
- no_relevant_evidence_extractable_from_the_provided_text: 1
- no_relevant_evidence_extraction_found_in_the_provided_text: 1
- no_relevant_evidence_for_oa_formulations_is_present_in_the_document: 1
- no_relevant_evidence_found_regarding_ibuprofen_or_related_formulations: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_evidence_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_regarding_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_evidential_content_related_to_ibuprofen_or_diffusion_cells_found_in_: 1
- no_relevant_extraction_details_are_available: 1
- no_relevant_extraction_evidence_found: 1
- no_relevant_extraction_points_identified_pertaining_to_ibuprofen_dermal_formulat: 1
- no_relevant_information_about_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_extracted_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_found_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_identified_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_found: 1
- no_relevant_information_on_ibuprofen_or_related_diffusion_studies_found: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_found_in_the_: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_identified: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_found_in_the_prov: 1
- no_relevant_information_related_to_ibuprofen_or_diffusion_cells_identified: 1
- no_relevant_information_related_to_the_extraction_criteria: 1
- no_specific_evidence_extractable_from_provided_pages: 1
- no_specific_evidence_extraction_pertinent_to_ibuprofen_or_diffusion_cells: 1
- no_specific_extractable_evidence_found_due_to_limited_available_document_context: 1
- no_specific_extractable_evidence_found_in_the_provided_document_text: 1
- no_specific_information_about_ibuprofen_or_diffusion_cell_is_provided_in_the_tex: 1
- no_substantive_content_extractable_document_consists_mainly_of_navigation_tools_: 1
- no_visible_extractable_evidence_due_to_content_restrictions: 1
- not_enough_content_provided_to_extract_specific_evidence: 1
- paper_focuses_on_naproxen_and_famotidine_not_ibuprofen: 1
- technical_note_discussing_techniques_for_monitoring_ibuprofen_release: 1
- the_content_does_not_provide_clear_extractable_data_regarding_diffusion_cells_or: 1
- the_details_for_diffusion_cell_and_endpoint_specifics_are_not_discernible_from_t: 1
- the_document_appears_to_be_oriented_towards_antidepressants_and_anti_inflammator: 1
- the_document_appears_to_focus_on_ibuprofen_loaded_alginate_based_biocomposite_hy: 1
- the_document_content_appears_to_be_partial_and_lacks_specific_details_needed_for: 1
- the_document_content_provided_does_not_contain_relevant_details_regarding_ibupro: 1
- the_document_does_not_contain_clear_extractable_evidence: 1
- the_document_does_not_contain_explicit_extractable_evidence_related_to_ibuprofen: 1
- the_document_does_not_contain_relevant_evidence_for_ibuprofen_or_diffusion_cell_: 1
- the_document_does_not_contain_relevant_evidence_for_ibuprofen_or_its_dermal_form: 1
- the_document_does_not_contain_relevant_evidence_related_to_ibuprofen_or_diffusio: 1
- the_document_does_not_contain_relevant_information_on_ibuprofen_or_related_formu: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_diffus: 1
- the_document_does_not_provide_any_visible_extraction_opportunities_based_on_the_: 1
- the_document_does_not_provide_explicit_evidence_related_to_ibuprofen_or_diffusio: 1
- the_document_does_not_provide_extractable_evidence_related_to_ibuprofen_dermal_f: 1
- the_document_does_not_provide_extractable_evidence_related_to_ibuprofen_or_derma: 1
- the_document_does_not_provide_extractable_information_regarding_ibuprofen_or_dif: 1
- the_document_does_not_provide_relevant_extractable_evidence_on_the_specified_top: 1
- the_document_does_not_provide_relevant_information_on_ibuprofen_or_its_dermal_fo: 1
- the_document_does_not_specifically_mention_ibuprofen_or_diffusion_cells_further_: 1
- the_document_is_not_providing_clear_evidence_related_to_ibuprofen_or_diffusion_c: 1
- the_document_lacks_sufficient_evidence_and_details_related_to_formulation_and_di: 1
- the_document_primarily_consists_of_navigational_elements_for_europe_pmc_and_does: 1
- the_document_primarily_contains_navigation_and_service_information_about_europe_: 1
- the_document_primarily_provides_a_general_overview_and_requires_further_investig: 1
- the_document_provided_appears_to_be_an_index_or_table_of_contents_giving_no_dire: 1
- the_document_provided_does_not_contain_relevant_data_for_extractable_evidence: 1
- the_document_provided_does_not_contain_relevant_evidence_for_extraction: 1
- the_document_provides_a_variety_of_studies_related_to_ibuprofen_but_specific_ext: 1
- the_document_seems_to_lack_specific_details_about_the_formulation_and_endpoint: 1
- the_document_text_does_not_provide_relevant_information_regarding_ibuprofen_or_r: 1
- the_extracted_content_does_not_provide_sufficient_relevant_data_pertaining_to_ib: 1
- the_paper_discusses_ibuprofen_but_does_not_specify_diffusion_methodology_clearly: 1
- the_paper_does_not_appear_relevant_to_ibuprofen_or_dermal_formulations: 1
- the_paper_does_not_mention_ibuprofen_or_diffusion_cells_and_there_is_no_relevant: 1
- the_paper_does_not_provide_information_about_ibuprofen_or_diffusion_cells_the_co: 1
- the_provided_text_does_not_contain_any_relevant_extractable_evidence_regarding_i: 1
- the_source_does_not_mention_ibuprofen_or_any_relevant_evidence_regarding_dermal_: 1
- this_is_a_review_paper_on_therapeutic_options_for_chronic_rhinosinusitis_in_cyst: 1
- this_paper_discusses_a_metal_organic_framework_zif_8_and_its_applications_rather: 1
- this_paper_discusses_ibuprofen_delivery_but_lacks_specific_details_about_methodo: 1
- this_paper_does_not_pertain_to_ibuprofen_or_dermal_formulations: 1
- this_paper_does_not_seem_relevant_to_oa_ibuprofen_dermal_formulation: 1
- unable_to_extract_relevant_evidence_due_to_lack_of_access_to_meaningful_content_: 1
- unspecified: 27
- validation_of_a_static_franz_diffusion_cell_system: 1
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
- skipped: 46
#### patch_area
- applied: 7
- skipped: 31
#### patch_endpoint_time
- applied: 27
- skipped: 4
#### patch_endpoint_value
- applied: 46
- skipped: 60

## Patch Success Counts
- patch_area: 7
- patch_endpoint_time: 27
- patch_endpoint_value: 46