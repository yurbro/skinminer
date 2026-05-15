# Run Report: run_b96cfc745c17

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `88`
- Final records evaluated: `88`
- Actually verified: `5`
- Final unresolved: `51`
- Final rejected: `32`

## Route Distribution
- figure: 20
- mixed: 8
- table: 16
- text: 16
- unresolved: 488

## Extractor Outputs
- figure: 20
- table: 62
- text: 13

## Verification Outcomes
- rejected: 32
- unresolved: 51
- verified: 5

## Scope Buckets
- out_of_scope: 13
- recoverable_unresolved: 43
- strict_in_scope: 5
- useful_but_out_of_scope: 27

## Scope Tags
- non_target_api: 13
- recoverable_api_basis: 28
- recoverable_area: 12
- recoverable_endpoint: 4
- recoverable_endpoint_time: 1
- recoverable_figure_digitization: 1
- recoverable_support_gap: 30
- recoverable_unit_normalization: 1
- recoverable_unresolved: 43
- useful_api_concentration_out_of_scope: 9
- useful_but_out_of_scope: 27
- useful_device_out_of_scope: 11
- useful_endpoint_out_of_scope: 2
- useful_study_type_out_of_scope: 13

## Failure Taxonomy
- ambiguous_api_concentration: 45
- figure_digitization_failed: 2
- insufficient_evidence: 56
- missing_api_concentration: 7
- missing_area: 31
- missing_endpoint: 6
- missing_endpoint_time: 1
- not_target_api: 13
- not_target_api_concentration: 12
- not_target_device: 17
- not_target_study_type: 17
- percent_only: 6
- unit_normalization_failed: 3

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 21
- figure_digitization_failed: 2
- insufficient_evidence: 28
- missing_api_concentration: 4
- missing_area: 14
- missing_endpoint: 2
- not_target_api: 8
- not_target_api_concentration: 7
- not_target_device: 6
- not_target_study_type: 12
- percent_only: 5
- unit_normalization_failed: 2
### mixed
- ambiguous_api_concentration: 6
- insufficient_evidence: 13
- missing_api_concentration: 3
- missing_area: 8
- missing_endpoint: 3
- not_target_api: 5
- not_target_api_concentration: 4
- not_target_device: 6
- percent_only: 1
### table
- ambiguous_api_concentration: 14
- insufficient_evidence: 8
- missing_area: 8
- not_target_api_concentration: 1
- not_target_device: 5
- not_target_study_type: 5
- unit_normalization_failed: 1
### text
- ambiguous_api_concentration: 4
- insufficient_evidence: 7
- missing_area: 1
- missing_endpoint: 1
- missing_endpoint_time: 1

## Figure Stage Counts
- digitized_curves: 20
- digitized_endpoints_failed: 2
- digitized_endpoints_ok: 20
- mapped_curves: 20
- triage_artifacts: 18
- triage_digitize_candidates: 17
- unmapped_curves: 0

## Figure Gate Counts
- routed_candidates: 27
- after_gate: 20
- skipped:missing_explicit_figure_signal: 7

## Figure Triage Routes
- digitize: 17
- skip: 1

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 1
- endpoint_curve_present:uncertain: 1
- recommended_route:skip: 1
- ticks_readable:no: 1
- ticks_readable:uncertain: 2
- why_not_digitizable:none: 1
- why_not_digitizable:the_figure_includes_complexity_without_clearly_defined_curves_suitable_for_digit: 1

## Figure Digitization Statuses
- fail_missing_axis_range: 2
- ok: 20

## Figure Mapping Statuses
- vision_mapped: 20

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
- downloaded: 228
- error: 1
- resolved: 96
- unresolved: 223
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- content_indicates_no_extraction_relevance_for_ibuprofen: 1
- document_content_not_fully_provided_limited_extraction_possible: 1
- document_does_not_appear_to_contain_relevant_information_regarding_ibuprofen_for: 1
- document_does_not_contain_relevant_information_regarding_ibuprofen_or_diffusion_: 1
- document_does_not_provide_specific_evidence_regarding_ibuprofen_formulations_or_: 1
- document_does_not_provide_sufficient_extractable_evidence_relevant_to_ibuprofen_: 1
- document_is_mostly_navigational_and_lacks_extractable_evidence: 1
- document_primarily_contains_navigation_and_site_information_no_relevant_content_: 1
- evidence_extraction_is_unclear_due_to_incomplete_information_from_the_provided_d: 1
- evidence_extraction_requires_further_investigation_into_the_paper_content: 1
- first_page_shows_web_related_information_without_relevant_content: 1
- further_details_on_experimentation_and_results_may_be_within_the_full_document_t: 1
- further_evidence_needed_to_determine_specific_extraction_routes: 1
- initial_findings_on_ibuprofen_formulation_for_painful_venous_leg_ulcers: 1
- initial_pages_contain_header_and_menu_information_no_relevant_content: 1
- initial_pages_do_not_contain_extractable_evidence_further_pages_likely_needed: 1
- insufficient_content_to_determine_detailed_extraction_routes: 1
- insufficient_data_available_for_extraction: 1
- insufficient_data_to_assess_extraction_route: 1
- insufficient_evidence_regarding_ibuprofen_or_related_diffusion_methods: 1
- insufficient_extractable_evidence_found_in_the_document_text: 1
- insufficient_information_available_for_specific_extraction_details: 1
- insufficient_information_provided_to_extract_relevant_evidence: 1
- insufficient_information_to_determine_specific_extraction_routes: 1
- insufficient_relevant_content_regarding_ibuprofen_or_dermal_formulations: 1
- insufficient_structured_data_available_for_evidence_extraction: 1
- missing_structured_and_pdf_router_source: 234
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 80
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- no_clear_sections_identified_entire_document_may_need_review: 1
- no_detailed_info_available_in_the_provided_text: 1
- no_extractable_evidence_available: 1
- no_extractable_evidence_detected_from_current_page_content: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_in_provided_text: 1
- no_extractable_evidence_found_in_the_provided_document: 1
- no_extractable_evidence_found_in_the_provided_text: 3
- no_extractable_evidence_found_in_the_visible_sections: 1
- no_extractable_evidence_found_on_the_pages_provided: 1
- no_extractable_evidence_found_regarding_ibuprofen_or_diffusion_cells_content_app: 1
- no_extractable_evidence_located_regarding_ibuprofen_or_diffusion_cells: 1
- no_extractable_evidence_provided_due_to_the_lack_of_content_in_the_document: 1
- no_extractable_evidence_regarding_ibuprofen_or_relevant_diffusion_studies_appear: 1
- no_extractable_evidence_related_to_oa_or_ibuprofen_is_found_in_the_provided_docu: 1
- no_relevant_content_found: 1
- no_relevant_content_found_in_provided_document_excerpt: 1
- no_relevant_content_found_in_the_provided_document_sections: 1
- no_relevant_content_found_regarding_ibuprofen_or_dermal_formulation: 1
- no_relevant_content_regarding_ibuprofen_or_diffusion_cells_found_in_the_document: 1
- no_relevant_data_for_ibuprofen_or_diffusion_cell_extraction_found: 1
- no_relevant_evidence_for_ibuprofen_dermal_formulation_found_in_the_document: 1
- no_relevant_evidence_found_in_the_provided_document: 1
- no_relevant_evidence_found_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_on_ibuprofen_or_diffusion_cells_found_in_the_provided_text: 1
- no_relevant_evidence_regarding_ibuprofen_or_dermal_formulations_found_in_the_ext: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_could_be_extrac: 1
- no_relevant_extractable_evidence_found_in_the_provided_document: 1
- no_relevant_extraction_content_found_in_the_provided_text: 1
- no_relevant_information_available_from_the_provided_text: 1
- no_relevant_information_available_in_the_provided_text: 2
- no_relevant_information_for_ibuprofen_found_in_the_extracted_document: 1
- no_relevant_information_found_in_the_provided_document: 1
- no_relevant_information_found_regarding_ibuprofen_or_any_specific_drug_release_e: 1
- no_relevant_information_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_on_ibuprofen_formulations_found: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulation_found_in_the_document: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_is_evident_in_the_pr: 1
- no_relevant_information_pertaining_to_ibuprofen_or_diffusion_cells_found_in_the_: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_could_be_extr: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_identified: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_appears_to_be_pre: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_was_found_in_the_: 1
- no_relevant_information_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_relevant_passages_available_for_detailed_extraction: 1
- no_specific_evidence_extraction_points_identified_from_the_provided_text: 1
- no_specific_evidence_related_to_ibuprofen_or_diffusion_cells_was_found_in_the_te: 1
- no_specific_extractable_evidence_found_in_the_provided_text: 1
- no_specific_mention_of_ibuprofen_or_diffusion_cell_methods: 1
- not_enough_extractable_evidence_available_in_the_document: 1
- not_specific_to_dermal_formulations_or_ivpt_ivrt: 1
- paper_focuses_on_supercritical_co_assisted_spray_drying_and_does_not_involve_ibu: 1
- pdf_does_not_provide_sufficient_content_for_analysis: 1
- the_abstract_and_sections_related_to_ibuprofen_and_diffusion_methods_are_not_fou: 1
- the_content_does_not_provide_enough_information_to_determine_specific_extractabl: 1
- the_content_primarily_relates_to_moxibustion_therapy_rather_than_ibuprofen_or_de: 1
- the_document_appears_to_be_a_journal_landing_page_without_relevant_extraction_in: 1
- the_document_appears_to_be_an_entry_from_europe_pmc_but_contains_no_relevant_con: 1
- the_document_appears_to_be_an_irrelevant_webpage_with_no_extractable_data_regard: 1
- the_document_appears_to_be_focused_on_bradykinin_b2_receptors_rather_than_ibupro: 1
- the_document_appears_to_be_related_to_pharmaceuticals_and_natural_clay_but_does_: 1
- the_document_appears_to_be_unrelated_to_ibuprofen_or_relevant_dermal_formulation: 1
- the_document_appears_to_focus_on_synthesis_rather_than_a_specific_study_of_formu: 1
- the_document_appears_to_have_missing_or_insufficient_information_to_extract_the_: 1
- the_document_appears_to_not_contain_extractable_evidence_pertaining_to_ibuprofen: 1
- the_document_contains_limited_extractable_evidence_regarding_the_study_s_specifi: 1
- the_document_content_does_not_provide_relevant_details_for_extraction_related_to: 1
- the_document_content_does_not_provide_structured_evidence_for_extraction_regardi: 1
- the_document_content_does_not_provide_sufficient_information_for_detailed_extrac: 1
- the_document_content_does_not_provide_sufficient_information_related_to_dermal_f: 1
- the_document_content_mostly_consists_of_navigational_and_interface_elements_and_: 1
- the_document_content_provided_does_not_contain_extractable_evidence_relevant_to_: 1
- the_document_does_not_appear_to_focus_on_ibuprofen_or_dermal_formulation: 1
- the_document_does_not_appear_to_relate_to_ibuprofen_diffusion_cells_or_associate: 1
- the_document_does_not_contain_any_relevant_extractable_information_associated_wi: 1
- the_document_does_not_contain_clear_structured_data_or_endpoints_that_can_be_ext: 1
- the_document_does_not_contain_extractable_evidence_regarding_ibuprofen_or_specif: 1
- the_document_does_not_contain_extractable_evidence_relevant_to_ibuprofen_or_rela: 1
- the_document_does_not_contain_relevant_evidence_related_to_ibuprofen_or_diffusio: 1
- the_document_does_not_have_enough_contextual_information_to_determine_specifics_: 1
- the_document_does_not_pertain_to_ibuprofen_or_relevant_dermal_formulation_eviden: 1
- the_document_does_not_provide_clear_information_relevant_to_the_extraction: 1
- the_document_does_not_provide_explicit_information_relevant_for_thorough_extract: 1
- the_document_does_not_provide_substantial_details_for_extraction_based_on_the_cu: 1
- the_document_does_not_seem_to_relate_to_ibuprofen_or_dermal_formulations: 1
- the_document_is_primarily_a_description_of_the_study_involving_ibuprofen_but_lac: 1
- the_document_lacks_sufficient_information_relevant_to_ibuprofen_dermal_formulati: 1
- the_document_mainly_consists_of_a_homepage_and_does_not_provide_the_necessary_de: 1
- the_document_primarily_contains_navigation_elements_for_europe_pmc_with_no_extra: 1
- the_document_primarily_discusses_a_biodegradable_subcutaneous_implant_and_does_n: 1
- the_document_primarily_discusses_microglia_activation_and_does_not_contain_relev: 1
- the_document_primarily_discusses_synthetic_membranes_for_drug_diffusion_in_franz: 1
- the_document_primarily_includes_navigation_and_metadata_information_without_spec: 1
- the_document_primarily_provides_initial_data_without_clear_evidence_for_extracti: 1
- the_document_provided_does_not_contain_detailed_information_regarding_the_formul: 1
- the_document_provides_general_information_but_lacks_specific_details_regarding_t: 1
- the_pages_provided_do_not_contain_relevant_content_for_extraction_the_document_m: 1
- the_paper_discusses_the_role_of_sodium_coupled_monocarboxylate_transporters_in_d: 1
- the_paper_focuses_on_an_injectable_thermosensitive_hydrogel_formulation_containi: 1
- the_paper_primarily_discusses_novel_nsaids_with_potential_anticancer_properties_: 1
- the_provided_text_does_not_contain_relevant_information_for_extraction_regarding: 1
- this_document_contains_minimal_information_regarding_the_specifics_of_diffusion_: 1
- this_document_lacks_specific_extractable_evidence_further_examination_is_require: 1
- this_paper_does_not_mention_ibuprofen_or_related_methodologies: 1
- unspecified: 39
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
- applied: 5
- skipped: 73
#### patch_area
- applied: 6
- skipped: 41
#### patch_endpoint_time
- applied: 18
- skipped: 1
#### patch_endpoint_value
- applied: 33
- skipped: 51

## Patch Success Counts
- patch_api_concentration: 5
- patch_area: 6
- patch_endpoint_time: 18
- patch_endpoint_value: 33