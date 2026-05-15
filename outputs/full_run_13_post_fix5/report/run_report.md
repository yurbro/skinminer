# Run Report: run_4465774f3425

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `79`
- Final records evaluated: `79`
- Actually verified: `4`
- Final unresolved: `48`
- Final rejected: `27`

## Route Distribution
- figure: 24
- mixed: 6
- table: 13
- text: 9
- unresolved: 477

## Extractor Outputs
- figure: 9
- table: 64
- text: 11

## Verification Outcomes
- rejected: 27
- unresolved: 48
- verified: 4

## Scope Buckets
- out_of_scope: 16
- recoverable_unresolved: 44
- strict_in_scope: 4
- useful_but_out_of_scope: 15

## Scope Tags
- non_target_api: 16
- recoverable_api_basis: 26
- recoverable_area: 6
- recoverable_endpoint: 6
- recoverable_endpoint_time: 2
- recoverable_figure_digitization: 3
- recoverable_support_gap: 30
- recoverable_unit_normalization: 2
- recoverable_unresolved: 44
- useful_api_concentration_out_of_scope: 7
- useful_but_out_of_scope: 15
- useful_device_out_of_scope: 2
- useful_endpoint_out_of_scope: 3
- useful_study_type_out_of_scope: 9

## Failure Taxonomy
- ambiguous_api_concentration: 42
- figure_digitization_failed: 8
- insufficient_evidence: 54
- missing_api_concentration: 1
- missing_area: 14
- missing_endpoint: 11
- missing_endpoint_time: 2
- not_target_api: 16
- not_target_api_concentration: 10
- not_target_device: 3
- not_target_study_type: 12
- percent_only: 6
- unit_normalization_failed: 3

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 29
- figure_digitization_failed: 6
- insufficient_evidence: 27
- missing_api_concentration: 1
- missing_area: 10
- missing_endpoint: 6
- not_target_api: 13
- not_target_api_concentration: 8
- not_target_device: 2
- not_target_study_type: 10
- percent_only: 4
- unit_normalization_failed: 2
### mixed
- figure_digitization_failed: 2
- insufficient_evidence: 6
- missing_endpoint: 3
- not_target_api: 1
- not_target_api_concentration: 1
- not_target_study_type: 1
- unit_normalization_failed: 1
### table
- ambiguous_api_concentration: 13
- insufficient_evidence: 12
- missing_area: 4
- not_target_api: 2
- not_target_api_concentration: 1
- not_target_device: 1
- not_target_study_type: 1
- percent_only: 2
### text
- insufficient_evidence: 9
- missing_endpoint: 2
- missing_endpoint_time: 2

## Figure Stage Counts
- digitization_no_output: 6
- digitized_curves: 25
- digitized_endpoints_failed: 9
- digitized_endpoints_ok: 25
- mapped_curves: 12
- triage_artifacts: 22
- triage_digitize_candidates: 19
- triage_has_permeation_plot_true: 19
- unmapped_curves: 13
- vlm_readings_readable: 21
- vlm_readings_total: 26
- vlm_used_as_final: 8

## Figure Gate Counts
- routed_candidates: 29
- after_gate: 25
- skipped:missing_explicit_figure_signal: 4

## Figure Triage Routes
- digitize: 19
- skip: 3

## Figure Plot Presence
- false: 3
- true: 19

## Figure Triage Signals
- digitizable:no: 3
- endpoint_curve_present:no: 5
- recommended_route:skip: 3
- ticks_readable:no: 1
- ticks_readable:uncertain: 4
- why_not_digitizable:calibration_curve_not_target: 1
- why_not_digitizable:no_endpoint_curve_is_present_in_this_subplot: 1
- why_not_digitizable:no_ibuprofen_endpoint_curves_are_visible_in_the_image: 1

## Figure Digitization Statuses
- digitization_no_output: 6
- fail_missing_axis_range: 3
- ok: 25

## Figure Mapping Statuses
- underconstrained_labels: 13
- vision_mapped: 12

## Figure VLM Grounding Statuses
- figure_label_space: 3
- figure_label_space_only: 7
- none: 6
- source_label_space: 3
- ungrounded: 7

## Figure VLM Reconciliation Statuses
- cv_only: 9
- cv_vlm_disagreement: 4
- unreadable: 5
- vlm_only: 8

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 33
- priority_bucket:high: 28
- priority_bucket:medium: 5
- review_focus:api_concentration_basis: 26
- review_focus:endpoint_value: 6
- review_focus:unit_normalization: 1
- recommended_status:rejected: 6
- recommended_status:unresolved: 27
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
- downloaded: 219
- error: 1
- resolved: 86
- unresolved: 223
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- additional_document_content_needed_for_specific_extraction_details: 1
- content_appears_limited_to_metadata_and_navigation_links_no_evidence_directly_re: 1
- content_appears_to_be_about_a_different_topic_not_related_to_ibuprofen: 1
- content_does_not_provide_extractable_evidence: 1
- content_primarily_discusses_ibuprofen_induced_effects_on_red_blood_cells_further: 1
- content_primarily_focused_on_hydrogel_system_details_of_extraction_are_not_clear: 1
- detailed_content_extraction_cannot_be_performed_without_accessing_specific_evide: 1
- document_appears_to_be_invalid_or_does_not_contain_relevant_content: 1
- document_appears_to_be_primarily_an_introduction_with_no_clear_evidence_extracti: 1
- document_does_not_contain_relevant_information_about_ibuprofen_or_dermal_formula: 1
- document_does_not_contain_relevant_information_regarding_ibuprofen_formulations_: 1
- document_does_not_provide_evidence_related_to_ibuprofen_or_diffusion_cells: 1
- document_lacks_detailed_descriptions_relevant_to_ibuprofen_formulation_extractio: 1
- document_mainly_consists_of_navigation_and_access_information_for_europe_pmc_no_: 1
- document_primarily_consists_of_metadata_no_extractable_evidence_identified: 1
- document_primarily_discusses_synthesis_and_characterization_needs_detailed_analy: 1
- document_text_provided_is_not_sufficient_for_further_extraction: 1
- evidence_extraction_needs_to_be_confirmed_details_on_barriers_and_endpoint_speci: 1
- evidence_extraction_not_possible_document_primarily_consists_of_navigation_and_h: 1
- evidence_extraction_route_cannot_be_determined_from_the_provided_text: 1
- evidence_related_to_ibuprofen_exists_but_further_details_on_study_type_and_formu: 1
- extract_valuable_evidence_from_the_text_related_to_ibuprofen_and_its_application: 1
- extractable_evidence_details_are_not_available_in_the_provided_text_further_revi: 1
- extractable_information_about_ibuprofen_and_testing_method_is_unclear: 1
- extraction_details_are_minimal_further_information_may_be_extracted_from_subsequ: 1
- extraction_information_is_limited_and_further_details_are_needed_to_specify_endp: 1
- initial_findings_on_a_clinical_study_related_to_ibuprofen: 1
- insufficient_content_to_determine_detailed_extraction_information: 1
- insufficient_data_for_extraction_consider_reviewing_further_pages_for_specific_d: 1
- insufficient_evidence_present_in_the_provided_text_for_detailed_extraction: 1
- insufficient_extractable_evidence_from_the_provided_document_text: 1
- insufficient_information_available_in_provided_document_text: 1
- insufficient_information_extracted_for_a_specific_conclusion: 1
- insufficient_information_in_the_document_to_determine_extraction_details: 1
- insufficient_information_in_the_provided_snippet_to_determine_specific_extractio: 1
- insufficient_information_provided_to_determine_specific_evidence_extraction_rout: 1
- insufficient_information_to_determine_relevant_extraction_details: 1
- insufficient_information_to_determine_specific_details_from_the_provided_text: 1
- limited_extractable_evidence_due_to_the_document_being_a_description_of_journal_: 1
- missing_structured_and_pdf_router_source: 236
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 68
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- no_clear_carrier_information_visible_from_the_supplied_text: 1
- no_clear_extractable_evidence_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_concrete_evidence_related_to_formulations_or_endpoints_found_in_the_provided_: 1
- no_details_provided_in_the_text_related_to_ibuprofen_or_dermal_formulations: 1
- no_evidence_related_to_ibuprofen_or_dermal_formulations_found_in_the_document: 1
- no_extractable_data_found_in_the_provided_document_content: 1
- no_extractable_evidence_for_analysis_related_to_ibuprofen: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_found_in_the_text_provided: 1
- no_extractable_evidence_identified_in_the_provided_text: 1
- no_extractable_evidence_regarding_ibuprofen_dermal_formulation: 1
- no_extractable_evidence_regarding_ibuprofen_document_lacks_relevant_data: 1
- no_information_relevant_to_ibuprofen_dermal_formulation_extraction: 1
- no_relevant_content_found_related_to_ibuprofen_or_diffusion_cell: 1
- no_relevant_content_identified_in_the_extracted_data: 1
- no_relevant_data_for_extraction_related_to_ibuprofen_or_diffusion_studies: 1
- no_relevant_data_found_in_the_provided_text: 1
- no_relevant_data_on_ibuprofen_or_diffusion_cells_found_in_the_provided_text: 1
- no_relevant_data_related_to_ibuprofen_or_diffusion_cells_found_in_the_provided_d: 1
- no_relevant_details_on_ibuprofen_or_diffusion_cells: 1
- no_relevant_evidence_extractable_from_the_document: 1
- no_relevant_evidence_extracted_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_extraction_found: 1
- no_relevant_evidence_for_ibuprofen_or_diffusion_cell_content_seems_to_focus_on_a: 1
- no_relevant_evidence_found_in_provided_text: 1
- no_relevant_evidence_found_in_the_provided_document: 1
- no_relevant_evidence_identified_in_accessible_text: 1
- no_relevant_evidence_regarding_ibuprofen_or_diffusion_cells_identified_in_the_ex: 1
- no_relevant_extractable_evidence_found_in_the_document: 1
- no_relevant_extractable_evidence_found_related_to_ibuprofen_dermal_formulation: 1
- no_relevant_extractable_evidence_identified_in_the_provided_text: 1
- no_relevant_extraction_evidence_could_be_determined_from_the_provided_text: 1
- no_relevant_information_about_ibuprofen_dermal_formulation: 1
- no_relevant_information_about_ibuprofen_or_diffusion_cells_found_in_the_availabl: 1
- no_relevant_information_about_ibuprofen_or_diffusion_cells_is_found_in_the_provi: 1
- no_relevant_information_extracted_due_to_lack_of_content_visibility: 1
- no_relevant_information_extracted_from_the_document: 1
- no_relevant_information_extracted_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_found_in_the_document_text: 1
- no_relevant_information_on_ibuprofen_formulation_or_diffusion_cell: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulation_found_in_provided_con: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulation_found: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_found_in_the_: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_was_found_in_: 1
- no_relevant_information_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_sections_extracted: 1
- no_specific_evidence_extraction_is_possible_from_the_provided_text: 1
- no_specific_evidence_extraction_possible_from_the_provided_text: 1
- no_specific_evidence_on_ibuprofen_or_diffusion_cell_is_mentioned_in_the_document: 1
- no_specific_extractable_evidence_found_in_the_provided_document_excerpt: 1
- no_specific_extractable_evidence_related_to_ibuprofen_or_diffusion_cell: 1
- no_specific_information_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_substantive_content_found_in_the_provided_text: 1
- paper_focuses_on_nsaid_effects_not_specifically_on_ibuprofen_formulations: 1
- the_content_was_not_provided_to_extract_specific_evidence: 1
- the_document_appears_to_be_an_introduction_and_not_contain_specific_extractable_: 1
- the_document_appears_to_be_an_overview_page_without_the_relevant_content: 1
- the_document_appears_to_discuss_procedural_sedation_and_analgesia_without_specif: 1
- the_document_appears_to_focus_on_a_topic_unrelated_to_ibuprofen_or_dermal_formul: 1
- the_document_appears_to_focus_on_lignin_based_hydrogels_for_drug_delivery_rather: 1
- the_document_appears_to_lack_substantive_information_regarding_ibuprofen_diffusi: 1
- the_document_content_does_not_provide_sufficient_details_on_formulations_related: 1
- the_document_content_is_primarily_navigation_and_does_not_provide_relevant_scien: 1
- the_document_content_provided_does_not_contain_specific_evidence_on_ibuprofen_di: 1
- the_document_does_not_appear_to_provide_relevant_data_for_ibuprofen_dermal_formu: 1
- the_document_does_not_contain_relevant_evidence_related_to_ibuprofen_or_dermal_f: 1
- the_document_does_not_contain_relevant_information_for_extraction_related_to_ibu: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_dermal: 1
- the_document_does_not_contain_relevant_information_related_to_ibuprofen_dermal_f: 1
- the_document_does_not_contain_specific_details_regarding_ibuprofen_or_diffusion_: 1
- the_document_does_not_contain_specific_evidence_relevant_to_ibuprofen_or_diffusi: 1
- the_document_does_not_contain_specific_information_about_ibuprofen_or_diffusion_: 1
- the_document_does_not_contain_sufficient_information_about_ibuprofen_or_relevant: 1
- the_document_does_not_include_any_content_directly_related_to_iv_formulation_or_: 1
- the_document_does_not_provide_any_extractable_evidence_related_to_ibuprofen_or_i: 1
- the_document_does_not_provide_any_extractable_evidence_relevant_to_ibuprofen_for: 1
- the_document_does_not_provide_enough_content_related_to_ibuprofen_or_diffusion_m: 1
- the_document_does_not_provide_relevant_details_for_a_specific_extraction_related: 1
- the_document_does_not_provide_relevant_information_for_extraction_related_to_ibu: 1
- the_document_does_not_provide_relevant_information_related_to_ibuprofen_dermal_f: 1
- the_document_does_not_provide_specific_details_about_ibuprofen_drug_diffusion_or: 1
- the_document_does_not_seem_to_discuss_ibuprofen_or_diffusion_cells_based_on_the_: 1
- the_document_primarily_consists_of_navigation_instructions_and_does_not_contain_: 1
- the_document_primarily_contains_navigation_content_and_does_not_provide_specific: 1
- the_document_primarily_discusses_a_metal_organic_framework_membrane_and_does_not: 1
- the_document_provided_has_no_relevant_details_regarding_ibuprofen_or_any_related: 1
- the_document_provided_primarily_contains_metadata_and_navigational_information_r: 1
- the_document_provides_minimal_context_and_content_for_extraction: 1
- the_document_seems_to_be_introductory_content_not_directly_containing_the_core_r: 1
- the_document_text_primarily_discusses_multifunctional_materials_for_bone_cancer_: 1
- the_paper_discusses_nonsteroidal_anti_inflammatory_drugs_specifically_ibuprofen_: 1
- the_paper_focuses_on_the_anticancer_activity_of_ibuprofen_but_does_not_provide_r: 1
- the_paper_is_about_the_synthesis_and_characterization_of_ibuprofen_nanohybrid_bu: 1
- the_provided_document_mainly_contains_navigation_and_functional_information_for_: 1
- the_provided_text_does_not_contain_structured_data_or_extractable_evidence_relat: 1
- the_study_mentions_ibuprofen_but_lacks_specific_details_on_diffusion_cells_endpo: 1
- the_text_does_not_contain_specific_information_regarding_ibuprofen_or_diffusion_: 1
- this_document_does_not_provide_clear_carriers_for_endpoints_or_formulations: 1
- this_paper_focuses_on_a_mixed_micellar_gel_formulation_for_ibuprofen_but_lacks_s: 1
- unable_to_extract_detailed_information_due_to_limited_available_text: 1
- unspecified: 30
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
- skipped: 72
#### patch_area
- applied: 12
- skipped: 32
#### patch_endpoint_time
- applied: 18
- skipped: 2
#### patch_endpoint_value
- applied: 28
- skipped: 56

## Patch Success Counts
- patch_area: 12
- patch_endpoint_time: 18
- patch_endpoint_value: 28