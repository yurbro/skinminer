# Run Report: run_82febe8626d9

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `238`
- Final records evaluated: `238`
- Actually verified: `1`
- Final unresolved: `178`
- Final rejected: `59`

## Route Distribution
- figure: 19
- mixed: 7
- table: 14
- text: 10
- unresolved: 479

## Extractor Outputs
- figure: 14
- table: 247
- text: 11

## Verification Outcomes
- rejected: 59
- unresolved: 178
- verified: 1

## Scope Buckets
- out_of_scope: 23
- recoverable_unresolved: 159
- strict_in_scope: 1
- useful_but_out_of_scope: 55

## Scope Tags
- non_target_api: 23
- recoverable_api_basis: 121
- recoverable_area: 20
- recoverable_endpoint: 20
- recoverable_figure_digitization: 13
- recoverable_source_context: 54
- recoverable_support_gap: 85
- recoverable_unit_normalization: 20
- recoverable_unresolved: 159
- useful_api_concentration_out_of_scope: 27
- useful_but_out_of_scope: 55
- useful_device_out_of_scope: 25
- useful_endpoint_out_of_scope: 1
- useful_study_type_out_of_scope: 16

## Failure Taxonomy
- ambiguous_api_concentration: 97
- figure_digitization_failed: 20
- insufficient_evidence: 126
- missing_api_concentration: 67
- missing_area: 54
- missing_endpoint: 32
- missing_endpoint_time: 5
- not_target_api: 23
- not_target_api_concentration: 31
- not_target_device: 25
- not_target_study_type: 16
- percent_only: 22
- source_context_inconsistent: 75
- unit_normalization_failed: 20

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 36
- figure_digitization_failed: 20
- insufficient_evidence: 52
- missing_api_concentration: 48
- missing_area: 34
- missing_endpoint: 23
- not_target_api: 8
- not_target_api_concentration: 7
- not_target_device: 15
- not_target_study_type: 3
- source_context_inconsistent: 75
- unit_normalization_failed: 12
### mixed
- ambiguous_api_concentration: 4
- insufficient_evidence: 31
- missing_api_concentration: 11
- missing_area: 4
- missing_endpoint: 5
- missing_endpoint_time: 4
- not_target_api: 6
- not_target_api_concentration: 10
- not_target_device: 4
- percent_only: 19
### table
- ambiguous_api_concentration: 56
- insufficient_evidence: 36
- missing_api_concentration: 8
- missing_area: 16
- not_target_api: 9
- not_target_api_concentration: 14
- not_target_device: 5
- not_target_study_type: 13
- percent_only: 3
- unit_normalization_failed: 8
### text
- ambiguous_api_concentration: 1
- insufficient_evidence: 7
- missing_endpoint: 4
- missing_endpoint_time: 1
- not_target_device: 1

## Figure Stage Counts
- digitization_no_output: 8
- digitized_curves: 30
- digitized_endpoints_failed: 8
- digitized_endpoints_ok: 30
- mapped_curves: 14
- triage_artifacts: 19
- triage_digitize_candidates: 19
- triage_has_permeation_plot_true: 19
- unmapped_curves: 16
- vlm_readings_readable: 31
- vlm_readings_total: 35
- vlm_used_as_final: 8

## Figure Gate Counts
- routed_candidates: 25
- after_gate: 20
- skipped:missing_explicit_figure_signal: 5

## Figure Triage Routes
- digitize: 19

## Figure Plot Presence
- true: 19

## Figure Triage Signals
- endpoint_curve_present:no: 1
- ticks_readable:no: 1
- ticks_readable:uncertain: 1

## Figure Digitization Statuses
- digitization_no_output: 8
- ok: 30

## Figure Mapping Statuses
- underconstrained_labels: 16
- vision_mapped: 14

## Figure VLM Grounding Statuses
- figure_label_space: 10
- figure_label_space_only: 4
- none: 4
- source_label_space: 7
- ungrounded: 10

## Figure VLM Reconciliation Statuses
- cv_only: 16
- cv_vlm_agree: 1
- cv_vlm_disagreement: 6
- unreadable: 4
- vlm_only: 8

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 106
- priority_bucket:high: 82
- priority_bucket:medium: 24
- review_focus:api_concentration_basis: 72
- review_focus:diffusion_area: 13
- review_focus:endpoint_value: 17
- review_focus:unit_normalization: 4
- recommended_status:rejected: 11
- recommended_status:unresolved: 95
- disagreement:scope_bucket_disagreement: 9
- disagreement:status_disagreement: 11

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
- error: 15
- unresolved: 224
### Access Reasons
- failed_download_html: 3
- failed_download_pdf: 22
- resolve_error_connectionerror: 2
- seed_pdf_url_from_metadata: 7
### Unresolved Route Reasons
- content_does_not_provide_extractable_evidence_or_specific_data: 1
- content_does_not_seem_to_contain_relevant_information_regarding_ibuprofen_or_its: 1
- content_from_the_provided_document_is_insufficient_for_detailed_extraction: 1
- content_is_incomplete_and_does_not_provide_clear_evidence_for_extraction: 1
- document_appears_to_be_an_oa_paper_unrelated_to_ibuprofen_or_dermal_formulations: 1
- document_appears_to_be_mostly_navigational_content_from_europe_pmc_without_extra: 1
- document_content_does_not_provide_extractable_evidence: 1
- document_content_does_not_provide_specific_evidence_related_to_ibuprofen_or_diff: 1
- document_does_not_contain_any_relevant_information_on_ibuprofen_or_dermal_formul: 1
- document_does_not_contain_relevant_evidence_related_to_ibuprofen: 1
- document_does_not_provide_specific_content_except_for_metadata: 1
- document_does_not_provide_sufficient_evidence_for_structured_extraction: 1
- document_text_does_not_contain_evidence_relevant_for_structured_extraction: 1
- evidence_extraction_is_not_applicable_as_the_document_appears_to_primarily_discu: 1
- evidence_extraction_requires_further_detailed_examination_of_the_document_for_sp: 1
- extractable_evidence_is_uncertain_as_the_document_does_not_provide_sufficient_de: 1
- extractable_evidence_not_clear_from_the_document: 1
- extractable_evidence_regarding_ibuprofen_can_be_linked_to_the_synthesis_of_deriv: 1
- extractable_evidence_status_is_currently_unresolved: 1
- extraction_details_not_present_in_the_provided_text: 1
- extraction_route_remains_unclear_due_to_lack_of_information_provided_in_the_docu: 1
- information_from_the_pages_is_insufficient_to_determine_specific_extraction_path: 1
- initial_findings_details_on_endpoints_and_formulations_not_clearly_provided: 1
- initial_page_does_not_contain_relevant_content: 1
- initial_pages_have_no_relevant_evidence_further_extraction_needed: 1
- insufficient_data_in_the_provided_text: 1
- insufficient_data_provided_from_the_document: 1
- insufficient_evidence_detail_available: 1
- insufficient_evidence_found_in_the_provided_document_text: 1
- insufficient_extractable_evidence_in_the_supplied_document: 1
- insufficient_extracted_information_from_the_provided_document_text: 1
- insufficient_information_available_for_detailed_extraction: 1
- insufficient_information_available_in_the_provided_text_to_determine_relevant_de: 1
- insufficient_information_in_the_document_for_comprehensive_extraction: 1
- insufficient_information_provided_to_determine_extraction_route: 1
- insufficient_information_to_determine_carrier_details_and_extraction_route: 1
- insufficient_information_to_determine_specifics_about_formulation_or_endpoints: 1
- insufficient_information_to_extract_specific_details_about_methods_or_results: 1
- limited_information_available_for_extraction_from_the_provided_text: 1
- missing_structured_and_pdf_router_source: 236
- missing_structured_and_pdf_router_source_blocked_html_local_captcha_blocked_html: 60
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- no_clear_evidence_extractable_from_provided_page: 1
- no_direct_evidence_of_ibuprofen_or_specific_endpoints_found_in_the_provided_text: 1
- no_evidence_related_to_ibuprofen_or_diffusion_cells: 1
- no_evidence_related_to_ibuprofen_or_diffusion_cells_was_found_in_the_provided_do: 1
- no_evidence_related_to_ibuprofen_or_specific_diffusion_methodology_is_identified: 1
- no_explicit_evidence_extractable_from_provided_text: 1
- no_extractable_content_found_in_the_provided_text: 1
- no_extractable_evidence_available_from_the_provided_text: 1
- no_extractable_evidence_found_document_appears_to_focus_on_the_usage_of_hot_melt: 1
- no_extractable_evidence_found_due_to_lack_of_content: 1
- no_extractable_evidence_found_from_the_supplied_document_text: 1
- no_extractable_evidence_found_in_the_provided_document: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_identified: 1
- no_extractable_evidence_identified_in_the_provided_text: 1
- no_extractable_evidence_on_diffusion_cell_endpoint_or_formulation_provided_in_th: 1
- no_extractable_evidence_present_in_provided_text: 1
- no_extractable_evidence_related_to_ibuprofen_or_dermal_formulations_found_in_the: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_methodology_identified: 1
- no_pertinent_evidence_found_in_the_provided_text: 1
- no_relevant_content_available_for_extraction_regarding_ibuprofen_formulations: 1
- no_relevant_content_extracted_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_content_found_related_to_ibuprofen_or_its_dermal_formulation: 1
- no_relevant_data_related_to_ibuprofen_or_dermal_formulations_detected_in_the_tex: 1
- no_relevant_details_on_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_evidence_extractable_from_provided_document_text: 1
- no_relevant_evidence_extractable_from_the_document: 1
- no_relevant_evidence_for_ibuprofen_formulation_found_in_the_document: 1
- no_relevant_evidence_found_in_the_provided_text: 1
- no_relevant_evidence_on_ibuprofen_or_diffusion_cells_found_in_the_provided_text: 1
- no_relevant_evidence_regarding_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_evidence_regarding_ibuprofen_or_diffusion_cells_found_in_the_provide: 1
- no_relevant_extractable_evidence_regarding_ibuprofen_or_dermal_formulation_found: 1
- no_relevant_extractable_information_found_in_the_visible_pages: 1
- no_relevant_extraction_content_found_in_the_provided_document: 1
- no_relevant_extraction_evidence_found_in_the_provided_text: 1
- no_relevant_extraction_evidence_located: 1
- no_relevant_extraction_points_identified_in_the_provided_document: 1
- no_relevant_information_appears_to_be_extractable_regarding_ibuprofen_or_its_der: 1
- no_relevant_information_available_from_the_provided_text: 1
- no_relevant_information_extracted_from_the_provided_pages: 1
- no_relevant_information_found_for_extraction: 1
- no_relevant_information_found_in_the_provided_content: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulation_found: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulation_in_provided_text: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_found_in_the_provided_do: 1
- no_relevant_information_pertaining_to_ibuprofen_in_this_document: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_is_available_: 1
- no_specific_details_about_ibuprofen_or_diffusion_cells_were_found_in_the_provide: 1
- no_specific_evidence_about_ibuprofen_or_diffusion_cells_was_found_in_the_excerpt: 1
- no_specific_evidence_extractable_from_provided_text: 1
- no_specific_evidence_extraction_sections_noted: 1
- no_specific_evidence_on_ibuprofen_or_formulation_details_found_in_the_provided_c: 1
- no_specific_evidence_regarding_ibuprofen_or_diffusion_cells_is_mentioned_in_the_: 1
- no_specific_evidence_related_to_ibuprofen_or_diffusion_cells_is_identified_in_th: 1
- not_enough_extractable_evidence_apparent_from_the_provided_document: 1
- not_enough_information_to_determine_specifics_from_the_provided_text: 1
- not_relevant_to_ibuprofen_dermal_formulations: 1
- paper_discusses_the_impact_of_permeation_promoters_on_ibuprofen_release_indicati: 1
- potential_relevance_due_to_sulfonimide_derivative_lacks_specific_mention_of_ibup: 1
- text_from_the_document_is_primarily_a_navigation_interface_and_does_not_provide_: 1
- the_content_extraction_cannot_be_determined_from_the_text_provided: 1
- the_document_appears_to_be_a_review_based_on_the_title_actual_details_regarding_: 1
- the_document_appears_to_be_inaccessible_or_lacks_significant_content_to_assess_e: 1
- the_document_appears_to_be_primarily_about_a_novel_ibuprofen_derivative_rather_t: 1
- the_document_appears_to_be_primarily_focused_on_cancer_research_and_does_not_pro: 1
- the_document_appears_to_be_providing_an_overview_rather_than_extractable_evidenc: 1
- the_document_appears_to_focus_on_skin_cancers_rather_than_dermal_formulations_or: 1
- the_document_appears_to_lack_clear_structured_evidence_on_formulation_endpoints_: 1
- the_document_content_available_is_limited_and_does_not_specify_relevant_evidence: 1
- the_document_content_primarily_appears_to_be_navigation_and_operational_informat: 1
- the_document_discusses_ibuprofen_in_the_context_of_covid_19_including_its_pharma: 1
- the_document_does_not_appear_to_directly_address_topics_relevant_to_oa_or_ibupro: 1
- the_document_does_not_contain_clear_evidence_related_to_ibuprofen_or_the_require: 1
- the_document_does_not_contain_extractable_evidence_regarding_diffusion_cells_or_: 1
- the_document_does_not_contain_extractable_evidence_related_to_ibuprofen_dermal_f: 1
- the_document_does_not_contain_relevant_evidence_related_to_ibuprofen_or_dermal_f: 1
- the_document_does_not_contain_relevant_extractable_evidence_or_mentions_of_ibupr: 1
- the_document_does_not_contain_relevant_extraction_evidence_related_to_ibuprofen_: 1
- the_document_does_not_contain_relevant_information_on_ibuprofen_dermal_formulati: 1
- the_document_does_not_contain_relevant_information_on_ibuprofen_formulations: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_dermal: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_diffus: 1
- the_document_does_not_include_specific_evidence_extractable_details_related_to_i: 1
- the_document_does_not_mention_ibuprofen_or_related_dermal_formulations: 1
- the_document_does_not_provide_relevant_information_on_ibuprofen_or_any_related_d: 1
- the_document_does_not_provide_relevant_structured_information_for_extraction: 1
- the_document_does_not_provide_sufficient_details_or_clear_evidence_for_extractio: 1
- the_document_is_primarily_about_a_protocol_for_a_trial_and_does_not_seem_to_cont: 1
- the_document_is_primarily_structured_as_a_webpage_for_europe_pmc_with_no_accessi: 1
- the_document_lacks_extractable_evidence_relevant_to_the_formulation_or_study_of_: 1
- the_document_lacks_relevant_data_related_to_ibuprofen_and_its_dermal_formulation: 1
- the_document_only_contains_meta_information_about_the_europe_pmc_platform_and_do: 1
- the_document_primarily_consists_of_navigation_and_does_not_contain_relevant_cont: 1
- the_document_primarily_consists_of_navigational_content_and_does_not_contain_rel: 1
- the_document_primarily_contains_navigational_content_for_europe_pmc_and_does_not: 1
- the_document_primarily_discusses_a_novel_nsaid_derivative_and_its_effects_on_col: 1
- the_document_primarily_discusses_diffusivity_in_aqueous_solutions_without_clear_: 1
- the_document_provided_does_not_contain_pertinent_extractable_evidence_regarding_: 1
- the_document_seems_to_focus_on_synthesis_and_characterization_without_explicit_i: 1
- the_document_snippets_do_not_provide_clear_information_regarding_ibuprofen_diffu: 1
- the_evidence_extraction_routes_are_unclear_due_to_insufficient_data_presented_in: 1
- the_extracted_document_does_not_provide_clear_evidence_of_specific_endpoints_or_: 1
- the_paper_appears_focused_on_zn_based_mof_synthesis_and_characterization_with_no: 1
- the_paper_discusses_a_dressing_for_wound_healing_but_does_not_focus_on_ibuprofen: 1
- the_paper_discusses_ibuprofen_but_does_not_provide_clear_experimental_details_or: 1
- the_paper_discusses_lumbar_spinal_surgery_and_the_effects_of_naproxen_and_famoti: 1
- the_paper_does_not_provide_clear_evidence_relevant_to_ibuprofen_or_diffusion_cel: 1
- the_paper_explores_a_gelling_system_with_ibuprofen_but_lacks_detailed_informatio: 1
- the_paper_focuses_on_a_biodegradable_implant_for_drug_delivery_but_does_not_ment: 1
- the_provided_document_appears_to_be_focused_on_the_role_of_nsaids_in_viral_infec: 1
- the_source_document_does_not_provide_any_extractable_evidence_related_to_oa_or_i: 1
- the_study_mentions_ibuprofen_but_does_not_provide_specific_details_on_formulatio: 1
- this_paper_does_not_appear_to_discuss_ibuprofen_or_diffusion_cells_making_it_uns: 1
- this_paper_does_not_appear_to_focus_on_ibuprofen_or_related_dermal_formulations: 1
- unspecified: 26
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
- skipped: 222
#### patch_area
- applied: 17
- skipped: 105
#### patch_endpoint_time
- applied: 53
- skipped: 5
#### patch_endpoint_value
- applied: 75
- skipped: 169

## Patch Success Counts
- patch_area: 17
- patch_endpoint_time: 53
- patch_endpoint_value: 75