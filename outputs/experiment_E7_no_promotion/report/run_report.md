# Run Report: run_dd4795e7bee9

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `73`
- Final records evaluated: `73`
- Actually verified: `4`
- Final unresolved: `47`
- Final rejected: `22`

## Route Distribution
- figure: 17
- mixed: 7
- table: 20
- text: 14
- unresolved: 478

## Extractor Outputs
- figure: 7
- table: 68
- text: 7

## Verification Outcomes
- rejected: 22
- unresolved: 47
- verified: 4

## Scope Buckets
- out_of_scope: 6
- recoverable_unresolved: 37
- strict_in_scope: 4
- useful_but_out_of_scope: 26

## Scope Tags
- non_target_api: 6
- recoverable_api_basis: 21
- recoverable_area: 3
- recoverable_endpoint: 7
- recoverable_endpoint_time: 1
- recoverable_figure_digitization: 2
- recoverable_support_gap: 28
- recoverable_unit_normalization: 2
- recoverable_unresolved: 37
- useful_api_concentration_out_of_scope: 13
- useful_but_out_of_scope: 26
- useful_device_out_of_scope: 5
- useful_endpoint_out_of_scope: 1
- useful_study_type_out_of_scope: 11

## Failure Taxonomy
- ambiguous_api_concentration: 38
- figure_digitization_failed: 2
- insufficient_evidence: 51
- missing_api_concentration: 2
- missing_area: 18
- missing_endpoint: 7
- missing_endpoint_time: 1
- not_target_api: 6
- not_target_api_concentration: 13
- not_target_device: 5
- not_target_study_type: 12
- percent_only: 4
- unit_normalization_failed: 3

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 18
- figure_digitization_failed: 2
- insufficient_evidence: 18
- missing_area: 8
- missing_endpoint: 2
- not_target_api: 1
- not_target_api_concentration: 5
- not_target_device: 4
- not_target_study_type: 8
- percent_only: 3
- unit_normalization_failed: 3
### mixed
- ambiguous_api_concentration: 1
- insufficient_evidence: 13
- missing_api_concentration: 2
- missing_area: 1
- missing_endpoint: 4
- percent_only: 1
### table
- ambiguous_api_concentration: 19
- insufficient_evidence: 17
- missing_area: 9
- not_target_api: 5
- not_target_api_concentration: 8
- not_target_device: 1
- not_target_study_type: 4
### text
- insufficient_evidence: 3
- missing_endpoint: 1
- missing_endpoint_time: 1

## Figure Stage Counts
- digitization_no_output: 4
- digitized_curves: 23
- digitized_endpoints_failed: 6
- digitized_endpoints_ok: 23
- mapped_curves: 3
- triage_artifacts: 17
- triage_digitize_candidates: 15
- triage_has_permeation_plot_true: 15
- unmapped_curves: 20
- vlm_readings_readable: 24
- vlm_readings_total: 28
- vlm_used_as_final: 14

## Figure Gate Counts
- routed_candidates: 23
- after_gate: 18
- skipped:missing_explicit_figure_signal: 5

## Figure Triage Routes
- digitize: 15
- skip: 1
- supp_needed: 1

## Figure Plot Presence
- false: 2
- true: 15

## Figure Triage Signals
- digitizable:no: 1
- digitizable:uncertain: 1
- endpoint_curve_present:no: 3
- endpoint_curve_present:uncertain: 2
- recommended_route:skip: 1
- recommended_route:supp_needed: 1
- ticks_readable:uncertain: 5
- why_not_digitizable:calibration_curve_not_target: 1
- why_not_digitizable:low_clarity_and_complexity_of_data_representation_hinder_definitive_digitization: 1

## Figure Digitization Statuses
- digitization_no_output: 4
- fail_missing_axis_range: 2
- ok: 23

## Figure Mapping Statuses
- underconstrained_labels: 20
- vision_mapped: 3

## Figure VLM Grounding Statuses
- figure_label_space: 5
- figure_label_space_only: 13
- none: 3
- ungrounded: 7

## Figure VLM Reconciliation Statuses
- cv_only: 10
- unreadable: 4
- vlm_only: 14

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 27
- priority_bucket:high: 20
- priority_bucket:medium: 7
- review_focus:api_concentration_basis: 19
- review_focus:diffusion_area: 1
- review_focus:endpoint_value: 7
- recommended_status:rejected: 8
- recommended_status:unresolved: 19
- disagreement:scope_bucket_disagreement: 8
- disagreement:status_disagreement: 8

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
- downloaded: 227
- error: 1
- resolved: 89
- unresolved: 219
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- best_extraction_route_cannot_be_determined_from_the_provided_content: 1
- cannot_extract_definitive_evidence_due_to_lack_of_specific_content_in_the_provid: 1
- content_does_not_provide_any_concrete_evidence_extractable_regarding_ibuprofen_o: 1
- content_from_the_document_is_not_fully_extractable_due_to_the_lack_of_specific_s: 1
- content_is_inaccessible_only_meta_information_is_available: 1
- content_is_primarily_about_synthesis_and_delivery_mechanisms_rather_than_specifi: 1
- content_not_extractable_possibly_due_to_lack_of_information: 1
- content_only_shows_a_web_interface_with_no_extractable_evidence: 1
- content_primarily_provides_insights_into_nsaids_and_does_not_specifically_focus_: 1
- could_not_extract_detailed_evidence_from_the_provided_document: 1
- detailed_information_on_the_endpoints_and_formulations_was_not_found_in_the_extr: 1
- document_appears_to_be_an_article_discussing_a_thermosensitive_hydrogel_for_trea: 1
- document_contains_references_to_ibuprofen_but_lacks_specific_experimental_detail: 1
- document_content_does_not_appear_to_provide_relevant_extraction_information: 1
- document_did_not_provide_extractable_content_relevant_to_ibuprofen_or_diffusion_: 1
- document_does_not_contain_relevant_information_specific_to_ibuprofen_or_its_derm: 1
- document_does_not_provide_extractable_structured_evidence: 1
- document_does_not_provide_relevant_extractable_evidence_regarding_ibuprofen_or_d: 1
- document_does_not_provide_specific_findings: 1
- document_text_does_not_provide_extractable_evidence: 1
- evidence_extraction_details_are_vague_from_the_provided_excerpt: 1
- evidence_extraction_may_not_be_possible_as_no_relevant_data_is_visible_in_the_pr: 1
- evidence_might_exist_but_is_not_extractable_from_the_available_content: 1
- evidence_related_to_ibuprofen_presence_but_lacks_clarity_on_endpoint_or_formulat: 1
- extractable_details_about_ibuprofen_and_formulations_are_not_evident_from_the_in: 1
- focus_on_ibuprofen_permeability_using_a_synthetic_membrane: 1
- focus_on_ibuprofen_permeation_across_synthetic_membranes_using_established_diffu: 1
- insufficient_content_provided_for_detailed_extraction: 1
- insufficient_detail_to_determine_evidence: 1
- insufficient_extraction_route_due_to_lack_of_specific_evidence_location_details: 1
- insufficient_information_available_to_determine_specific_evidence_extraction_rou: 1
- insufficient_information_to_determine_extraction_route: 1
- insufficient_text_provided_to_extract_concrete_evidence: 1
- missing_structured_and_pdf_router_source: 233
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 70
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- need_more_content_to_determine_extractable_evidence: 1
- no_detailed_information_extractable_from_the_provided_text: 1
- no_evidence_extraction_possible_from_provided_text: 1
- no_extractable_evidence_currently_available_from_the_provided_text: 1
- no_extractable_evidence_found_in_the_provided_document: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_from_the_provided_text: 1
- no_extractable_information_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_content_extractable_regarding_ibuprofen_or_diffusion_methods: 1
- no_relevant_content_extracted_from_the_pages_provided: 1
- no_relevant_content_extracted_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_content_related_to_ibuprofen_or_diffusion_cell_was_found_in_the_prov: 1
- no_relevant_data_available_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_data_on_ibuprofen_or_dermal_formulations_found_in_the_provided_docum: 1
- no_relevant_details_about_ibuprofen_or_diffusion_cells_found_in_the_provided_doc: 1
- no_relevant_details_extracted_from_the_content_provided: 1
- no_relevant_evidence_extraction_found_in_the_provided_text: 1
- no_relevant_evidence_for_ibuprofen_dermal_formulation_found: 1
- no_relevant_evidence_for_ibuprofen_found_in_the_text_provided: 1
- no_relevant_evidence_found_in_the_document: 1
- no_relevant_evidence_found_in_the_provided_text: 2
- no_relevant_evidence_found_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_on_ibuprofen_extraction: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_found_in_the_do: 1
- no_relevant_extractable_evidence_detected_in_the_provided_document_text: 1
- no_relevant_extractable_evidence_found_in_the_provided_text: 2
- no_relevant_extractable_evidence_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_extraction_found_related_to_ibuprofen_or_diffusion_study: 1
- no_relevant_information_extracted_from_the_document: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_dermal_formulations: 2
- no_relevant_information_found_on_the_specific_study_or_contents: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_found_in_the_documen: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_is_found_in_this_excerpt: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_noted_in_the_prov: 1
- no_relevant_information_related_to_ibuprofen_or_dermal_formulations_is_found_in_: 1
- no_specific_details_or_extractable_information_about_endpoints_formulations_or_s: 1
- no_specific_evidence_extractable_related_to_ibuprofen_or_dermal_formulations: 1
- no_specific_evidence_extracted_content_appears_non_relevant: 1
- no_specific_evidence_extracted_related_to_ibuprofen_or_diffusion_cells: 1
- no_specific_evidence_extraction_can_be_made_from_the_provided_content: 1
- no_specific_evidence_regarding_ibuprofen_or_diffusion_cells_found_in_the_provide: 1
- no_specific_evidence_regarding_ibuprofen_or_diffusion_cells_is_mentioned_in_the_: 1
- no_specific_extractable_evidence_found_regarding_ibuprofen_formulation: 1
- no_specific_extraction_points_identified_due_to_lack_of_detailed_content: 1
- no_structured_evidence_present_in_provided_text: 1
- no_useful_evidence_extractable_from_the_pages_provided: 1
- not_enough_extractable_evidence_available_in_the_provided_text: 1
- paper_discusses_ibuprofen_in_a_formulation_context_but_does_not_provide_clear_en: 1
- paper_does_not_seem_to_contain_relevant_information_regarding_ibuprofen_or_derma: 1
- the_document_appears_to_be_incomplete_or_does_not_provide_sufficient_structured_: 1
- the_document_appears_to_be_primarily_about_ocular_drug_discovery_and_development: 1
- the_document_appears_to_be_unavailable_or_incomplete_in_the_provided_text: 1
- the_document_appears_to_discuss_drug_delivery_systems_but_does_not_specifically_: 1
- the_document_appears_to_relate_to_catalytic_ozonation_of_pharmaceuticals_not_dir: 1
- the_document_contains_limited_content_unable_to_extract_specific_evidence: 1
- the_document_contains_no_clear_extractable_evidence_locations_from_the_provided_: 1
- the_document_contains_no_relevant_extractable_evidence: 1
- the_document_content_does_not_provide_relevant_data_on_ibuprofen_or_direct_evide: 1
- the_document_content_primarily_contains_metadata_and_requires_further_analysis_f: 1
- the_document_content_refers_to_effects_of_diclofenac_and_ibuprofen_but_no_extrac: 1
- the_document_did_not_provide_sufficient_detail_for_specific_extraction_routes: 1
- the_document_does_not_appear_to_relate_directly_to_ibuprofen_or_dermal_formulati: 1
- the_document_does_not_contain_relevant_information_on_ibuprofen_or_relevant_diff: 1
- the_document_does_not_mention_ibuprofen_or_provide_relevant_evidence_for_extract: 1
- the_document_does_not_provide_enough_structured_content_to_extract_specific_evid: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_formulati: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_or_its_de: 1
- the_document_does_not_provide_specific_information_related_to_ibuprofen_or_any_r: 1
- the_document_does_not_provide_sufficient_evidence_related_to_ibuprofen_or_diffus: 1
- the_document_is_about_supercritical_co_assisted_spray_drying_of_nanocomposites_n: 1
- the_document_is_incomplete_and_does_not_provide_specific_sections_or_counts_rega: 1
- the_document_is_largely_inaccessible_with_the_first_two_pages_containing_no_rele: 1
- the_document_lacked_explicit_information_on_the_extraction_parameters: 1
- the_document_lacks_clear_structured_data_on_endpoints_or_formulations: 1
- the_document_pages_consist_of_navigation_and_help_information_without_relevant_c: 1
- the_document_primarily_consists_of_navigation_and_support_content_without_clear_: 1
- the_document_primarily_discusses_green_light_exposure_and_its_effects_on_inflamm: 1
- the_document_primarily_discusses_lignin_based_colloidal_particles_and_does_not_m: 1
- the_document_primarily_discusses_molecular_dynamics_simulations_rather_than_empi: 1
- the_document_primarily_features_metadata_and_navigation_information_but_does_men: 1
- the_document_primarily_includes_navigation_and_links_related_to_europe_pmc_no_re: 1
- the_document_provides_limited_information_to_determine_specific_details_regardin: 1
- the_document_starts_with_no_relevant_information_regarding_ibuprofen_or_a_dermal: 1
- the_document_text_does_not_contain_relevant_information_regarding_ibuprofen_or_d: 1
- the_document_text_does_not_provide_sufficient_evidence_related_to_ibuprofen_or_d: 1
- the_paper_appears_to_focus_on_the_extraction_and_characterization_of_a_specific_: 1
- the_paper_discusses_characteristics_of_ibuprofen_films_but_does_not_provide_extr: 1
- the_paper_discusses_initial_findings_from_a_clinical_investigation_involving_the: 1
- the_paper_discusses_interactions_between_mil_88b_fe_and_ibuprofen_including_load: 1
- the_paper_does_not_directly_mention_ibuprofen_or_any_related_formulations: 1
- the_pdf_provided_does_not_contain_sufficient_information_for_a_proper_evaluation: 1
- the_provided_text_does_not_contain_relevant_information_regarding_ibuprofen_or_d: 1
- the_source_document_does_not_provide_relevant_details_for_extraction_regarding_i: 1
- the_source_document_does_not_provide_sufficient_information_for_analysis: 1
- the_text_does_not_provide_specific_locations_or_structured_evidence: 1
- the_title_mentions_ibuprofen_but_details_on_its_formulation_and_diffusion_studie: 1
- this_document_does_not_provide_explicit_details_about_ibuprofen_or_a_diffusion_c: 1
- this_paper_primarily_discusses_the_acute_phase_response_in_lumbar_spinal_surgery: 1
- this_review_discusses_the_safety_and_efficacy_of_ibuprofen_in_the_context_of_cov: 1
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
- applied: 4
- skipped: 60
#### patch_area
- applied: 3
- skipped: 34
#### patch_endpoint_time
- applied: 14
- skipped: 1
#### patch_endpoint_value
- applied: 17
- skipped: 31

## Patch Success Counts
- patch_api_concentration: 4
- patch_area: 3
- patch_endpoint_time: 14
- patch_endpoint_value: 17