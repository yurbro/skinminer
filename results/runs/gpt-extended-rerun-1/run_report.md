# Run Report: run_79762448094a

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `248`
- Final records evaluated: `248`
- Actually verified: `1`
- Final unresolved: `199`
- Final rejected: `48`

## Route Distribution
- figure: 19
- mixed: 4
- table: 19
- text: 13
- unresolved: 478

## Extractor Outputs
- figure: 16
- table: 243
- text: 13

## Verification Outcomes
- rejected: 48
- unresolved: 199
- verified: 1

## Scope Buckets
- out_of_scope: 19
- recoverable_unresolved: 177
- strict_in_scope: 1
- useful_but_out_of_scope: 51

## Scope Tags
- non_target_api: 19
- recoverable_api_basis: 156
- recoverable_area: 34
- recoverable_endpoint: 8
- recoverable_endpoint_time: 1
- recoverable_figure_digitization: 5
- recoverable_source_context: 61
- recoverable_support_gap: 105
- recoverable_unresolved: 177
- useful_api_concentration_out_of_scope: 35
- useful_but_out_of_scope: 51
- useful_device_out_of_scope: 14
- useful_study_type_out_of_scope: 16

## Failure Taxonomy
- ambiguous_api_concentration: 105
- figure_digitization_failed: 7
- insufficient_evidence: 163
- missing_api_concentration: 82
- missing_area: 53
- missing_endpoint: 11
- missing_endpoint_time: 2
- not_target_api: 19
- not_target_api_concentration: 36
- not_target_device: 14
- not_target_study_type: 19
- percent_only: 19
- source_context_inconsistent: 83

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 54
- figure_digitization_failed: 7
- insufficient_evidence: 66
- missing_api_concentration: 24
- missing_area: 26
- missing_endpoint: 7
- not_target_api: 4
- not_target_api_concentration: 12
- not_target_device: 8
- not_target_study_type: 11
- source_context_inconsistent: 83
### mixed
- insufficient_evidence: 45
- missing_api_concentration: 23
- missing_area: 8
- not_target_api: 1
- not_target_api_concentration: 20
- not_target_device: 3
- not_target_study_type: 3
- percent_only: 19
### table
- ambiguous_api_concentration: 51
- insufficient_evidence: 46
- missing_api_concentration: 35
- missing_area: 19
- not_target_api: 14
- not_target_api_concentration: 4
- not_target_device: 2
- not_target_study_type: 4
### text
- insufficient_evidence: 6
- missing_endpoint: 4
- missing_endpoint_time: 2
- not_target_device: 1
- not_target_study_type: 1

## Figure Stage Counts
- digitization_no_output: 6
- digitized_curves: 17
- digitized_endpoints_failed: 9
- digitized_endpoints_ok: 17
- mapped_curves: 12
- triage_artifacts: 18
- triage_digitize_candidates: 17
- triage_has_permeation_plot_true: 17
- unmapped_curves: 5
- vlm_readings_readable: 29
- vlm_readings_total: 33
- vlm_used_as_final: 13

## Figure Gate Counts
- routed_candidates: 22
- after_gate: 19
- skipped:missing_explicit_figure_signal: 3

## Figure Triage Routes
- digitize: 17
- skip: 1

## Figure Plot Presence
- false: 1
- true: 17

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 2
- recommended_route:skip: 1
- ticks_readable:uncertain: 4
- why_not_digitizable:figure_is_a_table_with_text_data_not_curves: 1

## Figure Digitization Statuses
- digitization_no_output: 6
- fail_missing_axis_range: 3
- ok: 17

## Figure Mapping Statuses
- underconstrained_labels: 5
- vision_mapped: 12

## Figure VLM Grounding Statuses
- figure_label_space: 3
- figure_label_space_only: 4
- none: 4
- source_label_space: 14
- ungrounded: 8

## Figure VLM Reconciliation Statuses
- cv_only: 8
- cv_vlm_agree: 1
- cv_vlm_disagreement: 6
- no_source_record: 1
- unreadable: 4
- vlm_only: 13

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 113
- priority_bucket:high: 97
- priority_bucket:medium: 16
- review_focus:api_concentration_basis: 93
- review_focus:diffusion_area: 16
- review_focus:endpoint_value: 4
- recommended_status:rejected: 13
- recommended_status:unresolved: 100
- disagreement:scope_bucket_disagreement: 13
- disagreement:status_disagreement: 13

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
- downloaded: 290
- error: 13
- unresolved: 230
### Access Reasons
- failed_download_html: 2
- failed_download_pdf: 21
- resolve_error_connectionerror: 1
- seed_pdf_url_from_metadata: 8
### Unresolved Route Reasons
- additional_information_from_the_paper_is_required_to_provide_complete_extraction: 1
- contains_relevant_information_on_ibuprofen_composites: 1
- content_does_not_provide_specific_evidence_related_to_ibuprofen_or_diffusion_stu: 1
- content_extracted_from_the_source_could_not_be_determined_due_to_lack_of_identif: 1
- content_primarily_about_synthetic_evaluation_relevance_to_ibuprofen_formulation_: 1
- content_primarily_consists_of_web_navigation_elements_no_extractable_content_rel: 1
- document_consists_mainly_of_navigation_details_and_does_not_provide_relevant_stu: 1
- document_contains_no_extractable_evidence_regarding_specific_formulations_or_end: 1
- document_content_unavailable_for_extraction: 1
- document_does_not_contain_evidence_beyond_preliminary_information: 1
- document_does_not_contain_explicit_references_to_ibuprofen_or_diffusion_cells: 1
- document_does_not_contain_relevant_information_related_to_ibuprofen_or_dermal_fo: 1
- document_does_not_provide_relevant_extractable_evidence_regarding_dermal_formula: 1
- document_doesn_t_appear_to_contain_relevant_data_on_ibuprofen_dermal_formulation: 1
- document_lacks_relevant_information_for_extraction: 1
- document_text_does_not_provide_explicit_evidence_related_to_ibuprofen_or_diffusi: 1
- evidence_extraction_is_limited_due_to_the_document_not_containing_clear_indicati: 1
- evidence_extraction_is_limited_due_to_the_lack_of_specific_details_in_the_provid: 1
- evidence_extraction_is_unclear_lacks_explicit_details_on_formulations_and_endpoi: 1
- evidence_extraction_needs_further_details: 1
- evidence_extraction_not_applicable_as_no_relevant_content_found_in_the_provided_: 1
- extraction_route_is_uncertain_due_to_lack_of_specific_details_in_the_text: 1
- extraction_route_not_possible_due_to_insufficient_references_to_ibuprofen_or_rel: 1
- further_details_required_to_clarify_the_specific_extraction_points_regarding_ibu: 1
- information_extraction_is_limited_due_to_the_lack_of_structured_content_in_the_p: 1
- information_from_the_document_is_insufficient_to_determine_specific_extraction_r: 1
- information_limited_further_detail_extraction_needed_from_the_full_document: 1
- initial_analysis_suggests_a_focus_on_ibuprofen_in_a_synoviocyte_model_but_lacks_: 1
- initial_findings_from_a_randomized_controlled_clinical_investigation_involving_b: 1
- initial_page_contains_no_relevant_extractable_information: 1
- insufficient_content_available_to_extract_relevant_evidence: 1
- insufficient_content_for_specific_evidence_extraction_document_lacks_detailed_me: 1
- insufficient_content_provided_to_determine_evidence_extraction: 1
- insufficient_data_available_in_the_document_for_further_categorization: 1
- insufficient_detail_to_extract_specific_evidence_regarding_ibuprofen_or_formulat: 1
- insufficient_evidence_and_specific_references_to_ibuprofen_or_relevant_data: 1
- insufficient_evidence_from_the_provided_text_to_determine_specific_details: 1
- insufficient_evidence_related_to_ibuprofen_or_dermal_formulations: 1
- insufficient_evidence_related_to_ibuprofen_or_diffusion_cell_in_the_document: 1
- insufficient_extractable_evidence_in_provided_text: 1
- insufficient_information_extracted_from_the_document: 1
- insufficient_information_for_data_extraction: 1
- insufficient_information_for_extraction: 1
- insufficient_information_in_the_document_for_extraction: 1
- insufficient_information_provided_to_extract_specific_details_about_study_or_fin: 1
- insufficient_information_to_determine_specific_evidence_details: 1
- insufficient_information_to_extract_relevant_evidence: 1
- investigates_permeation_promoters_for_ibuprofen_delivery: 1
- metadata_indicates_study_on_transdermal_delivery_of_ibuprofen_with_novel_adhesiv: 1
- missing_structured_and_pdf_router_source: 241
- missing_structured_and_pdf_router_source_blocked_html_local_captcha_blocked_html: 65
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- no_clear_evidence_extraction_points_identified_due_to_initial_page_content_limit: 1
- no_explicit_evidence_on_ibuprofen_or_specific_formulations_found: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_found_on_ibuprofen_dermal_formulation: 1
- no_extractable_evidence_regarding_ibuprofen_or_diffusion_cell_further_details_ne: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cell: 1
- no_information_available_on_specific_barriers_or_formulations: 1
- no_relevant_content_extracted_pertaining_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_content_found_in_the_provided_pages: 1
- no_relevant_content_visible_in_the_provided_text: 1
- no_relevant_data_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_data_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_details_provided_in_the_excerpt: 1
- no_relevant_evidence_extracted_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_for_ibuprofen_or_diffusion_cell_found_in_provided_text: 1
- no_relevant_evidence_for_ibuprofen_or_diffusion_cell_found_in_the_document: 1
- no_relevant_evidence_found_in_the_provided_document: 2
- no_relevant_evidence_found_in_the_provided_text: 1
- no_relevant_evidence_found_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_diffusion_cells_in_the_provid: 1
- no_relevant_evidence_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_found_in_the_in: 1
- no_relevant_extractable_evidence_found_in_the_provided_text: 1
- no_relevant_extractable_evidence_related_to_oa_or_ibuprofen_detected_in_the_prov: 1
- no_relevant_extraction_routes_found_from_the_provided_document: 1
- no_relevant_extracts_regarding_ibuprofen_or_diffusion_cells_found: 1
- no_relevant_information_about_diffusion_formulations_or_endpoints_found_in_the_p: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_found_in_the_provided_document: 1
- no_relevant_information_found_in_the_provided_text: 1
- no_relevant_information_found_regarding_ibuprofen_or_related_dermal_formulations: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cell_in_the_provided_pa: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_is_found_within_t: 1
- no_relevant_information_regarding_ibuprofen_or_drug_formulation_found_in_the_giv: 1
- no_relevant_information_regarding_ibuprofen_or_related_dermal_formulations_found: 1
- no_relevant_information_regarding_nsaids_or_ibuprofen_formulations_found: 1
- no_relevant_information_related_to_ibuprofen_or_diffusion_cells_found_in_the_pro: 1
- no_relevant_information_to_extract_from_provided_text: 1
- no_specific_endpoints_or_formulations_mentioned: 1
- no_specific_evidence_extractable_from_the_provided_text: 2
- no_specific_evidence_extraction_could_be_made_from_the_provided_text: 1
- no_specific_extraction_points_available: 1
- no_specific_information_on_ibuprofen_application_formulation_or_endpoints_found_: 1
- not_enough_information_in_provided_text_to_determine_specific_extraction_routes: 1
- potential_relevance_due_to_ibuprofen_formulation_focus: 1
- the_content_does_not_provide_specific_locations_for_extraction: 1
- the_content_primarily_refers_to_the_synthesis_and_use_of_new_ibuprofen_formulati: 1
- the_document_appears_primarily_focused_on_allergic_reactions_rather_than_specifi: 1
- the_document_appears_to_be_locked_or_incompletely_rendered_limiting_the_extracti: 1
- the_document_appears_to_be_unavailable_for_extraction_as_it_contains_only_naviga: 1
- the_document_appears_to_focus_on_the_design_and_synthesis_of_coumarin_schiff_bas: 1
- the_document_content_appears_to_pertain_to_the_assembly_of_lignin_based_colloids: 1
- the_document_does_not_appear_to_contain_relevant_evidence_based_on_the_provided_: 1
- the_document_does_not_appear_to_discuss_ibuprofen_or_related_dermal_formulations: 1
- the_document_does_not_contain_extractable_evidence_due_to_missing_structured_con: 1
- the_document_does_not_contain_relevant_evidence_related_to_ibuprofen_dermal_form: 1
- the_document_does_not_contain_relevant_information_about_ibuprofen_or_formulatio: 1
- the_document_does_not_contain_relevant_information_based_on_the_provided_content: 1
- the_document_does_not_contain_relevant_information_for_extraction_concerning_ibu: 1
- the_document_does_not_contain_relevant_information_on_ibuprofen_further_explorat: 1
- the_document_does_not_provide_clear_evidence_for_structured_extraction_specific_: 1
- the_document_does_not_provide_detailed_evidence_extraction_options: 1
- the_document_does_not_provide_enough_details_on_specific_methodologies_or_findin: 1
- the_document_does_not_provide_relevant_content_for_extraction_related_to_ibuprof: 1
- the_document_does_not_provide_specific_details_relevant_to_the_oa_only_ibuprofen: 1
- the_document_does_not_provide_sufficient_information_for_a_clear_extraction_rout: 1
- the_document_doesn_t_provide_clear_evidence_to_identify_relevant_endpoints_or_fo: 1
- the_document_primarily_comprises_web_and_institutional_navigation_information_no: 1
- the_document_primarily_consists_of_europe_pmc_interface_details_rather_than_subs: 1
- the_document_primarily_consists_of_navigation_and_metadata_lacking_core_content_: 1
- the_document_primarily_contains_metadata_about_the_journal_and_does_not_provide_: 1
- the_document_primarily_contains_navigation_and_access_information_for_the_europe: 2
- the_document_primarily_contains_navigation_details_and_does_not_provide_content_: 1
- the_document_primarily_discusses_naproxen_and_famotidine_with_no_mention_of_ibup: 1
- the_document_source_does_not_provide_clear_evidence_or_sections_to_extract_from: 1
- the_document_starts_with_a_europe_pmc_notice_and_does_not_contain_specific_infor: 1
- the_document_structure_is_unclear_and_specific_details_about_endpoints_or_formul: 1
- the_document_text_provided_does_not_contain_extractable_evidence_related_to_ibup: 1
- the_paper_discusses_maisine_based_microemulsions_for_drug_delivery_and_does_not_: 1
- the_paper_discusses_various_organic_contaminants_including_ibuprofen_but_additio: 1
- the_paper_explores_interactions_of_ibuprofen_with_a_metal_organic_framework_for_: 1
- the_provided_text_does_not_contain_relevant_information_regarding_ibuprofen_diff: 1
- the_provided_text_does_not_contain_relevant_information_to_extract_for_the_speci: 1
- the_relevant_data_and_evidence_are_not_visible_in_the_provided_text: 1
- this_document_contains_limited_key_extracts_due_to_the_presence_of_only_introduc: 1
- unable_to_determine_relevant_extraction_details_from_the_provided_document_text: 1
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
#### patch_api_concentration
- applied: 4
- skipped: 232
#### patch_area
- applied: 12
- skipped: 114
#### patch_endpoint_time
- applied: 54
- skipped: 2
#### patch_endpoint_value
- applied: 54
- skipped: 108

## Patch Success Counts
- patch_api_concentration: 4
- patch_area: 12
- patch_endpoint_time: 54
- patch_endpoint_value: 54