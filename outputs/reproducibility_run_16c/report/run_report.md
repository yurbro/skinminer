# Run Report: run_f11f154710c9

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `277`
- Final records evaluated: `277`
- Actually verified: `4`
- Final unresolved: `201`
- Final rejected: `72`

## Route Distribution
- figure: 19
- mixed: 10
- table: 17
- text: 16
- unresolved: 477

## Extractor Outputs
- figure: 13
- table: 275
- text: 6

## Verification Outcomes
- rejected: 72
- unresolved: 201
- verified: 4

## Scope Buckets
- out_of_scope: 36
- recoverable_unresolved: 153
- strict_in_scope: 4
- useful_but_out_of_scope: 84

## Scope Tags
- non_target_api: 36
- recoverable_api_basis: 97
- recoverable_area: 30
- recoverable_endpoint: 4
- recoverable_endpoint_time: 2
- recoverable_source_context: 49
- recoverable_support_gap: 93
- recoverable_unit_normalization: 14
- recoverable_unresolved: 153
- useful_api_concentration_out_of_scope: 51
- useful_but_out_of_scope: 84
- useful_device_out_of_scope: 17
- useful_endpoint_out_of_scope: 2
- useful_study_type_out_of_scope: 19

## Failure Taxonomy
- ambiguous_api_concentration: 135
- figure_digitization_failed: 3
- insufficient_evidence: 175
- missing_api_concentration: 26
- missing_area: 63
- missing_endpoint: 8
- missing_endpoint_time: 3
- not_target_api: 36
- not_target_api_concentration: 56
- not_target_device: 19
- not_target_study_type: 38
- percent_only: 25
- source_context_inconsistent: 94
- unit_normalization_failed: 14

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 43
- figure_digitization_failed: 3
- insufficient_evidence: 59
- missing_api_concentration: 5
- missing_area: 34
- missing_endpoint: 5
- missing_endpoint_time: 1
- not_target_api: 13
- not_target_api_concentration: 22
- not_target_device: 6
- not_target_study_type: 22
- percent_only: 2
- source_context_inconsistent: 94
- unit_normalization_failed: 12
### mixed
- ambiguous_api_concentration: 11
- insufficient_evidence: 59
- missing_api_concentration: 14
- missing_area: 18
- missing_endpoint: 1
- not_target_api: 21
- not_target_api_concentration: 20
- not_target_study_type: 16
- percent_only: 4
### table
- ambiguous_api_concentration: 80
- insufficient_evidence: 54
- missing_api_concentration: 7
- missing_area: 11
- not_target_api: 2
- not_target_api_concentration: 14
- not_target_device: 13
- percent_only: 19
- unit_normalization_failed: 2
### text
- ambiguous_api_concentration: 1
- insufficient_evidence: 3
- missing_endpoint: 2
- missing_endpoint_time: 2

## Figure Stage Counts
- digitization_no_output: 5
- digitized_curves: 19
- digitized_endpoints_failed: 9
- digitized_endpoints_ok: 19
- mapped_curves: 10
- triage_artifacts: 18
- triage_digitize_candidates: 18
- triage_has_permeation_plot_true: 18
- unmapped_curves: 9
- vlm_readings_readable: 19
- vlm_readings_total: 21
- vlm_used_as_final: 16

## Figure Gate Counts
- routed_candidates: 29
- after_gate: 19
- skipped:low_route_confidence: 1
- skipped:missing_explicit_figure_signal: 9

## Figure Triage Routes
- digitize: 18

## Figure Plot Presence
- true: 18

## Figure Triage Signals
- endpoint_curve_present:no: 2
- ticks_readable:uncertain: 7

## Figure Digitization Statuses
- digitization_no_output: 5
- fail_missing_axis_range: 4
- ok: 19

## Figure Mapping Statuses
- underconstrained_labels: 9
- vision_mapped: 10

## Figure VLM Grounding Statuses
- figure_label_space: 5
- figure_label_space_only: 15
- ungrounded: 1

## Figure VLM Reconciliation Statuses
- cv_only: 1
- cv_vlm_disagreement: 1
- no_source_record: 1
- unreadable: 2
- vlm_only: 16

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 112
- priority_bucket:high: 94
- priority_bucket:medium: 18
- review_focus:api_concentration_basis: 86
- review_focus:diffusion_area: 13
- review_focus:endpoint_value: 4
- review_focus:unit_normalization: 9
- recommended_status:rejected: 17
- recommended_status:unresolved: 95
- disagreement:scope_bucket_disagreement: 17
- disagreement:status_disagreement: 17

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
- downloaded: 306
- error: 16
- unresolved: 217
### Access Reasons
- failed_download_html: 3
- failed_download_pdf: 24
- resolve_error_connectionerror: 2
- seed_pdf_url_from_metadata: 7
### Unresolved Route Reasons
- abstract_does_not_provide_specific_methodologies_further_sections_are_required_f: 1
- content_does_not_provide_relevant_evidence_for_ibuprofen_dermal_formulation: 1
- content_not_accessible_further_examination_needed: 1
- content_not_fully_provided_for_structured_extraction: 1
- document_appears_to_be_a_general_article_without_specific_information_on_ibuprof: 1
- document_appears_to_be_a_study_protocol_for_a_clinical_trial_lacking_specific_re: 1
- document_appears_to_have_no_relevant_extraction_content: 1
- document_content_mostly_contains_navigation_and_metadata_information_without_any: 1
- document_content_not_provided_limited_information_available: 1
- document_does_not_contain_relevant_evidence_extracts: 1
- document_does_not_contain_relevant_information_regarding_ibuprofen_or_related_fo: 1
- document_does_not_provide_sufficient_content_for_extraction: 1
- document_primarily_contains_catalog_information_rather_than_content_related_to_d: 1
- document_primarily_contains_navigation_links_rather_than_substantive_content: 1
- document_text_extracted_does_not_contain_relevant_information_about_ibuprofen_or: 1
- evidence_extraction_from_the_provided_source_is_limited_as_specific_experimental: 1
- evidence_extraction_is_limited_due_to_lack_of_details_and_structured_data_in_the: 1
- exploration_of_ph_sensitive_sustained_delivery_mechanisms_for_ibuprofen: 1
- extractable_evidence_appears_to_be_present_but_specific_details_regarding_experi: 1
- extractable_evidence_is_unclear_further_context_is_needed: 1
- extractable_evidence_related_to_nanoemulsions_and_ibuprofen_interactions: 1
- full_content_extraction_not_available_details_required_to_assess_study: 1
- initial_pages_contain_administrative_content_research_content_likely_starts_late: 1
- initial_part_of_the_document_does_not_provide_specific_information_further_conte: 1
- insufficient_content_available_for_extraction: 1
- insufficient_data_to_extract_specific_evidence_related_to_ibuprofen_or_diffusion: 1
- insufficient_details_provided_in_the_document_for_extraction: 1
- insufficient_evidence_available_from_provided_text_to_determine_key_study_detail: 1
- insufficient_evidence_for_extraction: 1
- insufficient_extractable_evidence_in_the_provided_text: 1
- insufficient_information_available_to_determine_specific_evidence_extraction_rou: 1
- insufficient_information_for_extracting_relevant_evidence: 1
- insufficient_information_for_extraction: 1
- insufficient_information_in_the_provided_text_to_extract_specific_evidence_relat: 1
- insufficient_information_is_available_in_the_provided_text_for_concrete_extracti: 1
- insufficient_information_to_determine_specific_extractable_evidence: 1
- insufficient_information_to_identify_relevant_extraction_routes: 1
- limited_extractable_evidence_in_the_text_based_on_provided_content: 1
- missing_structured_and_pdf_router_source: 230
- missing_structured_and_pdf_router_source_blocked_html_local_captcha_blocked_html: 68
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- no_clear_evidence_extractable_from_the_provided_document_text: 1
- no_clear_extractable_evidence_or_structured_data_present_in_the_provided_text: 1
- no_detailed_extractable_evidence_found_yet_content_presents_a_summary_without_sp: 1
- no_evidence_about_ibuprofen_or_diffusion_cells_found_in_the_provided_text: 1
- no_evidence_found_in_provided_text: 1
- no_evidence_related_to_ibuprofen_or_dermal_formulation_found: 1
- no_evidence_related_to_ibuprofen_or_diffusion_cells_found_uncertainty_in_extract: 1
- no_explicit_evidence_of_ibuprofen_or_diffusion_cells_identified_in_the_provided_: 1
- no_extractable_content_found_in_the_provided_text_the_document_seems_to_consist_: 1
- no_extractable_evidence_detailed_on_pages: 1
- no_extractable_evidence_found_in_the_provided_document: 2
- no_extractable_evidence_found_in_the_provided_document_text: 2
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_found_in_the_supplied_text: 1
- no_extractable_evidence_from_the_provided_document: 1
- no_extractable_evidence_identified_in_the_provided_content: 1
- no_extractable_evidence_regarding_ibuprofen_dermal_formulation: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cell: 1
- no_extractable_evidence_visible_in_the_provided_document_snippet: 1
- no_relevant_content_for_extraction_related_to_ibuprofen_or_dermal_formulation: 1
- no_relevant_content_for_ibuprofen_dermal_formulations: 1
- no_relevant_content_regarding_ibuprofen_or_diffusion_cell_is_present_in_the_init: 1
- no_relevant_data_related_to_ibuprofen_or_dermal_formulation_was_found_in_the_doc: 1
- no_relevant_details_related_to_ibuprofen_or_specific_formulations_found_in_the_p: 1
- no_relevant_evidence_extractable_from_the_provided_document_section: 1
- no_relevant_evidence_extracted_regarding_ibuprofen_or_dermal_formulation: 1
- no_relevant_evidence_found_in_the_document: 1
- no_relevant_evidence_found_in_the_extracted_content: 1
- no_relevant_evidence_found_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_regarding_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_evidence_related_to_ibuprofen_dermal_formulation_found_in_the_paper: 1
- no_relevant_extractable_evidence_found_in_the_provided_document: 1
- no_relevant_extractable_evidence_found_in_the_provided_text: 1
- no_relevant_extraction_evidence_found: 1
- no_relevant_extraction_evidence_found_in_the_provided_document_text: 1
- no_relevant_extraction_routes_identified_in_the_provided_text: 1
- no_relevant_information_about_ibuprofen_or_diffusion_cells_found_in_the_provided: 1
- no_relevant_information_extracted_concerning_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_found_in_the_pages_provided: 1
- no_relevant_information_found_in_the_provided_document_text: 1
- no_relevant_information_found_in_the_provided_text: 1
- no_relevant_information_on_ibuprofen_or_its_dermal_formulation: 1
- no_relevant_information_pertaining_to_ibuprofen_or_dermal_formulation_is_present: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_was_found_in_the_: 1
- no_relevant_information_regarding_ibuprofen_or_related_formulations_was_found_in: 1
- no_relevant_information_related_to_ibuprofen_or_dermal_formulations_found_in_the: 2
- no_relevant_information_related_to_ibuprofen_or_diffusion: 1
- no_relevant_information_related_to_ibuprofen_or_diffusion_cell_evidence_extracti: 1
- no_specific_evidence_extraction_possible_from_the_given_excerpt: 1
- not_enough_information_available_to_extract_specific_evidence_regarding_ibuprofe: 1
- only_general_information_about_the_source_and_navigation_of_the_document_is_avai: 1
- only_metadata_available_no_extractable_content: 1
- only_partial_document_info_available: 1
- the_content_does_not_directly_mention_ibuprofen_or_related_diffusion_studies: 1
- the_content_refers_to_phytochemical_studies_and_anti_inflammatory_properties_but: 1
- the_document_appears_to_be_an_article_with_limited_initial_accessibility_to_cont: 1
- the_document_appears_to_be_unavailable_as_it_contains_only_navigation_and_suppor: 1
- the_document_appears_to_discuss_transporters_in_skin_but_does_not_specifically_m: 1
- the_document_appears_to_focus_on_microneedle_spacing_and_materials_optimization_: 1
- the_document_appears_to_primarily_provide_an_overview_and_discussion_rather_than: 1
- the_document_contains_limited_extractable_evidence_and_does_not_explicitly_menti: 1
- the_document_contains_minimal_extractable_evidence_further_information_is_likely: 1
- the_document_content_from_the_source_does_not_provide_sufficient_information_reg: 1
- the_document_does_not_contain_relevant_extractable_information: 1
- the_document_does_not_contain_relevant_information_about_ibuprofen_or_diffusion_: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_formulati: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_its_de: 1
- the_document_does_not_contain_specific_evidence_related_to_ibuprofen_or_diffusio: 1
- the_document_does_not_provide_clear_evidence_regarding_formulation_or_specific_e: 1
- the_document_does_not_provide_clear_extractable_evidence_regarding_ibuprofen_or_: 1
- the_document_does_not_provide_direct_evidence_on_study_methodology_or_results_re: 1
- the_document_does_not_provide_direct_references_to_ibuprofen_or_specific_diffusi: 1
- the_document_does_not_provide_explicit_information_relevant_to_the_specified_ext: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_dermal_fo: 1
- the_document_does_not_provide_specific_details_necessary_for_extraction_more_inf: 1
- the_document_does_not_provide_specific_evidence_extract_it_seems_to_only_contain: 1
- the_document_does_not_provide_sufficient_information_to_identify_detailed_extrac: 1
- the_document_is_mostly_non_technical_and_contains_more_information_about_accessi: 1
- the_document_mainly_provides_an_overview_of_the_ethos_service_without_specific_d: 1
- the_document_primarily_contains_metadata_and_navigation_elements_without_substan: 1
- the_document_primarily_contains_non_research_content_and_lacks_extractable_scien: 1
- the_document_primarily_discusses_celecoxib_and_does_not_appear_to_provide_releva: 1
- the_document_primarily_focuses_on_a_clinical_response_to_transdermal_ibuprofen_b: 1
- the_document_primarily_focuses_on_nonsteroidal_anti_inflammatory_drugs_and_antib: 1
- the_document_primarily_includes_navigation_details_and_not_the_core_scientific_c: 1
- the_document_provided_does_not_contain_relevant_data_on_ibuprofen_or_diffusion_c: 1
- the_document_provided_does_not_contain_relevant_information_regarding_ibuprofen_: 1
- the_document_provided_does_not_contain_sufficient_content_to_identify_specific_e: 1
- the_document_s_contents_are_not_available_making_comprehensive_analysis_impossib: 1
- the_paper_discusses_ibuprofen_delivery_but_lacks_specific_data_extraction_points: 1
- the_paper_discusses_novel_nsaids_but_does_not_specifically_mention_ibuprofen_or_: 1
- the_paper_focuses_on_biodegradable_implants_and_does_not_mention_ibuprofen_or_an: 1
- the_paper_focuses_on_ibuprofen_removal_using_a_hybrid_system_not_on_dermal_formu: 1
- the_paper_focuses_on_naproxen_and_famotidine_with_no_mention_of_ibuprofen: 1
- the_paper_primarily_reviews_sodium_coupled_monocarboxylate_transporters_includin: 1
- the_source_document_does_not_provide_clear_details_on_content_for_extraction: 1
- the_source_document_does_not_provide_sufficient_structured_data_for_endpoint_or_: 1
- this_narrative_review_addresses_the_safety_and_efficacy_of_ibuprofen_in_the_cont: 1
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
- applied: 20
- skipped: 223
#### patch_area
- applied: 7
- skipped: 140
#### patch_endpoint_time
- applied: 60
- skipped: 3
#### patch_endpoint_value
- applied: 80
- skipped: 124

## Patch Success Counts
- patch_api_concentration: 20
- patch_area: 7
- patch_endpoint_time: 60
- patch_endpoint_value: 80