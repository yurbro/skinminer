# Run Report: run_a19b32f00b06

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `239`
- Final records evaluated: `239`
- Actually verified: `1`
- Final unresolved: `179`
- Final rejected: `59`

## Route Distribution
- figure: 15
- mixed: 9
- table: 18
- text: 14
- unresolved: 480

## Extractor Outputs
- figure: 10
- table: 252
- text: 10

## Verification Outcomes
- rejected: 59
- unresolved: 179
- verified: 1

## Scope Buckets
- out_of_scope: 37
- recoverable_unresolved: 156
- strict_in_scope: 1
- useful_but_out_of_scope: 45

## Scope Tags
- non_target_api: 37
- recoverable_api_basis: 128
- recoverable_area: 18
- recoverable_endpoint: 3
- recoverable_endpoint_time: 1
- recoverable_figure_digitization: 2
- recoverable_source_context: 35
- recoverable_support_gap: 90
- recoverable_unit_normalization: 8
- recoverable_unresolved: 156
- useful_api_concentration_out_of_scope: 27
- useful_but_out_of_scope: 45
- useful_device_out_of_scope: 18
- useful_study_type_out_of_scope: 4

## Failure Taxonomy
- ambiguous_api_concentration: 100
- figure_digitization_failed: 2
- insufficient_evidence: 122
- missing_api_concentration: 73
- missing_area: 37
- missing_endpoint: 12
- missing_endpoint_time: 10
- not_target_api: 37
- not_target_api_concentration: 37
- not_target_device: 27
- not_target_study_type: 4
- percent_only: 19
- source_context_inconsistent: 65
- unit_normalization_failed: 8

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 26
- figure_digitization_failed: 2
- insufficient_evidence: 28
- missing_api_concentration: 5
- missing_area: 25
- missing_endpoint: 2
- not_target_api: 16
- not_target_api_concentration: 22
- not_target_device: 12
- not_target_study_type: 4
- source_context_inconsistent: 65
### mixed
- ambiguous_api_concentration: 18
- insufficient_evidence: 58
- missing_api_concentration: 53
- missing_area: 2
- missing_endpoint: 9
- missing_endpoint_time: 9
- not_target_api: 11
- not_target_api_concentration: 12
- not_target_device: 9
- percent_only: 19
- unit_normalization_failed: 8
### table
- ambiguous_api_concentration: 56
- insufficient_evidence: 29
- missing_api_concentration: 15
- missing_area: 10
- not_target_api: 10
- not_target_api_concentration: 3
- not_target_device: 6
### text
- insufficient_evidence: 7
- missing_endpoint: 1
- missing_endpoint_time: 1

## Figure Stage Counts
- digitization_no_output: 4
- digitized_curves: 17
- digitized_endpoints_failed: 5
- digitized_endpoints_ok: 17
- mapped_curves: 10
- triage_artifacts: 14
- triage_digitize_candidates: 14
- triage_has_permeation_plot_true: 14
- unmapped_curves: 7
- vlm_readings_readable: 13
- vlm_readings_total: 20
- vlm_used_as_final: 6

## Figure Gate Counts
- routed_candidates: 23
- after_gate: 16
- skipped:missing_explicit_figure_signal: 7

## Figure Triage Routes
- digitize: 14

## Figure Plot Presence
- true: 14

## Figure Triage Signals
- endpoint_curve_present:no: 1
- ticks_readable:uncertain: 2

## Figure Digitization Statuses
- digitization_no_output: 4
- fail_missing_axis_range: 1
- ok: 17

## Figure Mapping Statuses
- underconstrained_labels: 7
- vision_mapped: 10

## Figure VLM Grounding Statuses
- figure_label_space: 3
- figure_label_space_only: 7
- none: 3
- source_label_space: 7

## Figure VLM Reconciliation Statuses
- cv_only: 3
- cv_vlm_agree: 1
- cv_vlm_disagreement: 4
- unreadable: 7
- vlm_only: 5

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 90
- priority_bucket:high: 77
- priority_bucket:medium: 13
- review_focus:api_concentration_basis: 75
- review_focus:diffusion_area: 7
- review_focus:endpoint_value: 3
- review_focus:unit_normalization: 5
- recommended_status:rejected: 9
- recommended_status:unresolved: 81
- disagreement:scope_bucket_disagreement: 10
- disagreement:status_disagreement: 9

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
- downloaded: 302
- error: 13
- unresolved: 221
### Access Reasons
- failed_download_html: 3
- failed_download_pdf: 22
- seed_pdf_url_from_metadata: 8
### Unresolved Route Reasons
- content_does_not_contain_specific_information_related_to_ibuprofen: 1
- content_from_pages_1_and_2_seems_to_focus_on_navigation_and_functionality_of_eur: 1
- content_is_not_directly_extractable_the_document_appears_to_be_more_informative_: 1
- content_primarily_consists_of_procedural_information_with_unclear_extractable_ev: 1
- content_primarily_consists_of_web_navigation_and_does_not_provide_relevant_extra: 1
- content_primarily_related_to_decellularized_macroalgae_for_skin_tissue_engineeri: 1
- content_provided_does_not_include_extractable_evidence_about_ibuprofen_formulati: 1
- detailed_specifics_regarding_diffusion_cell_and_endpoints_are_not_provided: 1
- document_content_appears_to_be_inaccessible_or_missing_relevant_information: 1
- document_does_not_provide_clear_evidence_extraction_routes: 1
- document_does_not_provide_evidence_for_ibuprofen_or_related_experiments: 1
- document_does_not_provide_relevant_evidence_for_ibuprofen_dermal_formulation: 1
- document_excerpts_do_not_contain_sufficient_evidence_related_to_ibuprofen_or_rel: 1
- document_primarily_contains_procedural_information_regarding_the_vapour_phase_me: 1
- document_primarily_discusses_degradation_of_ibuprofen_in_an_integrated_wetland_s: 1
- evidence_extractability_is_uncertain_from_the_provided_pages: 1
- evidence_extractable_information_is_insufficiently_provided_in_the_text: 1
- evidence_extraction_is_limited_due_to_lack_of_detailed_structured_data_in_the_pr: 1
- evidence_extraction_is_unclear_due_to_limited_document_text_provided: 1
- evidence_extraction_may_need_more_context_due_to_incomplete_document_preview: 1
- evidence_extraction_route_uncertain_based_on_the_provided_text: 1
- evidence_of_ibuprofen_interactions_and_loading_capacity_in_a_drug_delivery_syste: 1
- extraction_details_cannot_be_determined_from_the_provided_text: 1
- extraction_from_the_provided_content_is_limited_more_specific_sections_on_method: 1
- extraction_of_relevant_evidence_is_limited_due_to_incomplete_document_informatio: 1
- incomplete_document_extraction_cannot_be_effectively_determined: 1
- information_is_limited_carriers_and_specific_study_parameters_are_not_mentioned_: 1
- initial_findings_on_a_clinical_investigation: 1
- initial_page_contains_informational_content_further_extraction_needed_from_subse: 1
- initial_pages_do_not_contain_relevant_evidence_extraction_information: 1
- insufficient_content_from_document_to_determine_extractable_evidence: 1
- insufficient_content_provided_to_extract_specific_evidence: 1
- insufficient_evidence_available_in_the_provided_document: 1
- insufficient_evidence_for_extraction_routes_from_the_provided_text: 1
- insufficient_evidence_in_the_document_to_extract_relevant_information_related_to: 1
- insufficient_evidence_in_the_provided_text_for_detailed_extraction: 1
- insufficient_information_available_in_the_provided_text: 1
- insufficient_information_from_the_document: 1
- insufficient_information_in_the_provided_text_to_determine_extraction_routes: 1
- insufficient_information_on_the_pages_provided_to_determine_specific_extraction_: 1
- insufficient_information_provided_in_the_document: 1
- insufficient_information_provided_to_extract_specific_evidence_related_to_ibupro: 1
- insufficient_information_to_extract_meaningful_evidence: 1
- insufficient_relevant_information_found_in_the_provided_text_for_extraction: 1
- insufficient_text_provided_to_extract_specific_evidence: 1
- missing_structured_and_pdf_router_source: 231
- missing_structured_and_pdf_router_source_blocked_html_local_captcha_blocked_html: 67
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- no_clear_evidence_extraction_route_identified_in_the_provided_document_text: 1
- no_clear_evidence_related_to_ibuprofen_or_diffusion_cells_present_in_the_documen: 1
- no_clear_structured_evidence_could_be_extracted_from_the_text: 1
- no_extractable_content_available: 1
- no_extractable_content_provided_in_the_initial_pages: 1
- no_extractable_evidence_available_from_the_provided_text: 1
- no_extractable_evidence_could_be_inferred: 1
- no_extractable_evidence_directly_related_to_ibuprofen_or_formulation_could_be_id: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_found_in_the_supplied_document_text: 1
- no_extractable_evidence_on_methods_or_results_available_from_the_provided_text: 1
- no_mention_of_ibuprofen_or_diffusion_studies: 1
- no_mention_of_ibuprofen_or_related_formulation_evidence_in_provided_pages: 1
- no_relevant_content_related_to_ibuprofen_dermal_formulations_found_in_the_extrac: 1
- no_relevant_evidence_extracted: 1
- no_relevant_evidence_extracted_due_to_lack_of_details_in_the_document: 1
- no_relevant_evidence_extracted_related_to_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_found_in_the_provided_document: 1
- no_relevant_extractable_evidence_detected: 1
- no_relevant_extractable_evidence_related_to_ibuprofen_was_found_in_the_sourced_d: 1
- no_relevant_extraction_could_be_made_based_on_provided_document: 1
- no_relevant_extraction_points_identified_from_the_provided_text: 1
- no_relevant_information_accessible_in_the_extracted_text: 1
- no_relevant_information_available_related_to_ibuprofen_or_diffusion_cells_in_the: 1
- no_relevant_information_extracted_about_ibuprofen_or_diffusion_cells_from_the_pr: 1
- no_relevant_information_extracted_from_the_document: 1
- no_relevant_information_for_ibuprofen_dermal_formulation_mining_found: 1
- no_relevant_information_found_for_ibuprofen_or_diffusion_cell: 1
- no_relevant_information_found_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_found_in_the_provided_te: 1
- no_relevant_information_on_ibuprofen_or_diffusion_methods_found: 1
- no_relevant_information_regarding_ibuprofen_or_any_dermal_formulation: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulations_was_found: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_methods_found_in_the_pr: 1
- no_specific_details_on_ibuprofen_or_formulations_available: 1
- no_specific_evidence_extractable_content_mainly_refers_to_navigation_and_feature: 1
- no_specific_evidence_extractable_regarding_ibuprofen_or_diffusion_cell_focus_on_: 1
- no_specific_evidence_related_to_ibuprofen_or_diffusion_cells_found_in_the_provid: 1
- no_specific_experimental_data_on_ibuprofen_found: 1
- no_specific_extractable_evidence_is_present_in_the_provided_text: 1
- some_information_about_the_ibuprofen_formulation_is_likely_present_but_the_speci: 1
- study_focuses_on_the_diffusion_and_permeation_of_ibuprofen_using_franz_diffusion: 1
- the_content_provided_does_not_contain_specific_details_regarding_diffusion_cells: 1
- the_document_appears_to_be_a_review_with_no_specific_mention_of_ibuprofen_or_rel: 1
- the_document_appears_to_be_a_study_focusing_on_ibuprofen_permeation_through_a_sy: 1
- the_document_appears_to_be_about_pediatric_procedural_sedation_and_analgesia_in_: 1
- the_document_appears_to_be_mostly_about_hypothalamic_prostaglandins_and_does_not: 1
- the_document_appears_to_be_primarily_a_web_interface_for_europe_pmc_with_no_rele: 1
- the_document_appears_to_focus_more_on_microbicidal_activity_rather_than_dermal_f: 1
- the_document_appears_to_focus_on_coumarin_schiff_base_derivatives_rather_than_ib: 1
- the_document_appears_to_focus_on_lignin_based_hydrogels_for_drug_delivery_and_do: 1
- the_document_appears_to_lack_relevant_content_for_the_specified_criteria_regardi: 1
- the_document_appears_to_lack_relevant_information_regarding_ibuprofen_and_relate: 1
- the_document_content_did_not_provide_specific_information_for_detailed_extractio: 1
- the_document_does_not_contain_clear_evidence_for_dermal_formulation_details_rele: 1
- the_document_does_not_contain_extractable_evidence_relevant_to_ibuprofen_or_a_di: 1
- the_document_does_not_contain_relevant_extraction_evidence_related_to_ibuprofen_: 1
- the_document_does_not_contain_relevant_information_for_ibuprofen_dermal_formulat: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_diffus: 1
- the_document_does_not_contain_structured_experimental_data_or_discussion_about_i: 1
- the_document_does_not_provide_clear_relevant_data_for_extraction: 1
- the_document_does_not_provide_clear_structured_evidence_further_content_review_n: 1
- the_document_does_not_provide_explicit_evidence_related_to_ibuprofen_or_specific: 1
- the_document_does_not_provide_relevant_information_pertaining_specifically_to_ib: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_or_diffus: 1
- the_document_does_not_seem_relevant_to_ibuprofen_dermal_formulations: 1
- the_document_is_not_applicable_for_ibuprofen_dermal_formulation: 1
- the_document_mainly_discusses_the_impact_of_permeation_promoters_on_ibuprofen_de: 1
- the_document_primarily_contains_administrative_and_navigation_content_no_extract: 1
- the_document_primarily_contains_navigation_and_header_information_without_specif: 1
- the_document_primarily_discusses_molecular_dynamics_simulation_and_does_not_prov: 1
- the_document_primarily_discusses_the_development_of_a_biodegradable_implant_and_: 1
- the_document_primarily_focuses_on_nsaids_and_their_implications_in_viral_infecti: 1
- the_document_primarily_focuses_on_skin_cancer_and_therapeutic_targets_with_no_me: 1
- the_document_primarily_focuses_on_the_applicability_of_a_3d_printed_inert_minita: 1
- the_document_primarily_serves_as_a_preliminary_outline_and_lacks_detailed_result: 1
- the_document_provided_is_primarily_introductory_and_does_not_contain_relevant_ex: 1
- the_document_requires_more_specific_content_to_ascertain_any_relevant_evidence: 1
- the_document_seems_incomplete_no_specific_evidence_about_formulation_or_endpoint: 1
- the_document_text_provided_does_not_contain_relevant_information_regarding_ibupr: 1
- the_document_text_provided_does_not_contain_specific_extractable_evidence: 1
- the_paper_discusses_a_new_ibuprofen_formulation_but_lacks_clear_experimental_dat: 1
- the_paper_discusses_slc5a8_and_its_role_in_drug_transport_with_a_mention_of_ibup: 1
- the_paper_discusses_synergy_involving_ibuprofen_but_lacks_evidence_on_dermal_for: 1
- the_paper_discusses_the_pharmacological_potential_of_kyotorphin_and_its_derivati: 1
- the_paper_discusses_zn_based_mofs_and_their_potential_applications_but_does_not_: 1
- the_paper_emphasizes_biodegradation_processes_for_ibuprofen_but_does_not_specifi: 1
- the_paper_focuses_on_the_acute_phase_response_in_patients_undergoing_surgery_and: 1
- the_paper_focuses_on_transdermal_fentanyl_not_ibuprofen: 1
- the_paper_response_includes_ibuprofen_and_discusses_an_experimental_model_but_la: 1
- the_provided_text_does_not_contain_any_extractable_content_relevant_to_oa_ibupro: 1
- the_provided_text_does_not_contain_relevant_information_on_ibuprofen_or_a_diffus: 1
- the_source_document_does_not_contain_relevant_evidence_for_ibuprofen_or_dermal_f: 1
- the_text_provided_does_not_contain_extractable_evidence_related_to_ibuprofen_or_: 1
- this_paper_discusses_biofabricated_3d_intestinal_models_and_does_not_appear_to_c: 1
- this_paper_does_not_appear_to_focus_on_ibuprofen_or_diffusion_cells_with_no_clea: 1
- unable_to_extract_extractable_evidence_due_to_lack_of_content_details: 1
- unable_to_extract_relevant_evidence_from_the_provided_text: 1
- unable_to_extract_specific_evidence_from_the_current_page_due_to_missing_relevan: 1
- unspecified: 34
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
- skipped: 219
#### patch_area
- applied: 20
- skipped: 96
#### patch_endpoint_time
- applied: 53
- skipped: 10
#### patch_endpoint_value
- applied: 69
- skipped: 105

## Patch Success Counts
- patch_area: 20
- patch_endpoint_time: 53
- patch_endpoint_value: 69