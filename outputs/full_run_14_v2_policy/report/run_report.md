# Run Report: run_9dfb0936f0c4

- Model: `gpt-4o-mini`
- Policy: `v2_accept_wv`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `75`
- Final records evaluated: `75`
- Actually verified: `10`
- Final unresolved: `43`
- Final rejected: `22`

## Route Distribution
- figure: 18
- mixed: 13
- table: 14
- text: 12
- unresolved: 481

## Extractor Outputs
- figure: 7
- table: 60
- text: 13

## Verification Outcomes
- rejected: 22
- unresolved: 43
- verified: 10

## Scope Buckets
- out_of_scope: 11
- recoverable_unresolved: 37
- strict_in_scope: 10
- useful_but_out_of_scope: 17

## Scope Tags
- non_target_api: 11
- recoverable_api_basis: 15
- recoverable_area: 6
- recoverable_endpoint: 5
- recoverable_figure_digitization: 2
- recoverable_support_gap: 32
- recoverable_unit_normalization: 1
- recoverable_unresolved: 37
- useful_api_concentration_out_of_scope: 7
- useful_but_out_of_scope: 17
- useful_device_out_of_scope: 3
- useful_endpoint_out_of_scope: 1
- useful_study_type_out_of_scope: 9

## Failure Taxonomy
- ambiguous_api_concentration: 26
- figure_digitization_failed: 5
- insufficient_evidence: 54
- missing_api_concentration: 1
- missing_area: 17
- missing_endpoint: 9
- not_target_api: 11
- not_target_api_concentration: 10
- not_target_device: 5
- not_target_study_type: 9
- percent_only: 2
- unit_normalization_failed: 1

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 9
- figure_digitization_failed: 5
- insufficient_evidence: 18
- missing_area: 10
- missing_endpoint: 5
- not_target_api: 5
- not_target_api_concentration: 5
- not_target_device: 5
- not_target_study_type: 6
- percent_only: 2
### mixed
- ambiguous_api_concentration: 7
- insufficient_evidence: 25
- missing_api_concentration: 1
- missing_area: 4
- missing_endpoint: 3
- not_target_api: 4
- not_target_api_concentration: 3
- not_target_study_type: 1
- unit_normalization_failed: 1
### table
- ambiguous_api_concentration: 10
- insufficient_evidence: 10
- missing_area: 3
- not_target_api: 2
- not_target_api_concentration: 2
- not_target_study_type: 2
### text
- insufficient_evidence: 1
- missing_endpoint: 1

## Figure Stage Counts
- digitization_no_output: 6
- digitized_curves: 14
- digitized_endpoints_failed: 7
- digitized_endpoints_ok: 14
- mapped_curves: 5
- triage_artifacts: 17
- triage_digitize_candidates: 15
- triage_has_permeation_plot_true: 15
- unmapped_curves: 9
- vlm_readings_readable: 16
- vlm_readings_total: 21
- vlm_used_as_final: 7

## Figure Gate Counts
- routed_candidates: 30
- after_gate: 18
- skipped:missing_explicit_figure_signal: 12

## Figure Triage Routes
- digitize: 15
- skip: 2

## Figure Plot Presence
- false: 2
- true: 15

## Figure Triage Signals
- digitizable:no: 2
- endpoint_curve_present:no: 2
- recommended_route:skip: 2
- ticks_readable:uncertain: 2
- why_not_digitizable:calibration_curve_not_target: 1
- why_not_digitizable:figure_does_not_contain_endpoint_curves_related_to_ibuprofen: 1

## Figure Digitization Statuses
- digitization_no_output: 6
- fail_missing_axis_range: 1
- ok: 14

## Figure Mapping Statuses
- underconstrained_labels: 9
- vision_mapped: 5

## Figure VLM Grounding Statuses
- figure_label_space: 2
- figure_label_space_only: 4
- none: 1
- source_label_space: 13
- ungrounded: 1

## Figure VLM Reconciliation Statuses
- cv_only: 8
- cv_vlm_disagreement: 1
- unreadable: 5
- vlm_only: 7

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 20
- priority_bucket:high: 17
- priority_bucket:medium: 3
- review_focus:api_concentration_basis: 15
- review_focus:diffusion_area: 1
- review_focus:endpoint_value: 4
- recommended_status:rejected: 4
- recommended_status:unresolved: 16
- disagreement:scope_bucket_disagreement: 3
- disagreement:status_disagreement: 4

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
- downloaded: 230
- error: 1
- resolved: 83
- unresolved: 224
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- content_appears_to_be_non_extractable_due_to_lack_of_relevant_structured_informa: 1
- content_does_not_provide_enough_specific_information_relevant_to_ibuprofen_or_di: 1
- content_extraction_was_not_available_due_to_a_lack_of_detailed_sections_or_evide: 1
- content_from_initial_pages_is_unextractable_related_to_the_topic: 1
- content_on_first_two_pages_is_not_relevant_for_extraction: 1
- content_primarily_consists_of_navigational_elements_and_no_substantial_evidence_: 1
- document_appears_to_be_a_general_overview_without_specific_extractable_evidence_: 1
- document_appears_to_be_highly_technical_and_relevant_to_nsaids_but_lacks_the_spe: 1
- document_content_does_not_provide_enough_information_for_extraction: 1
- document_content_not_accessible_for_specific_extraction: 1
- document_did_not_provide_any_relevant_evidence_regarding_the_extraction_inquirie: 1
- document_does_not_contain_concrete_details_about_diffusion_studies_related_to_ib: 1
- document_is_primarily_procedural_specific_extraction_details_on_formulations_or_: 1
- evidence_extraction_is_limited_due_to_lack_of_specific_sections_or_details_in_th: 1
- evidence_extraction_not_explicit_keywords_indicate_focus_on_ibuprofen_response_b: 1
- extract_evidence_regarding_ibuprofen_delivery_method_and_formulation_from_the_pa: 1
- extractable_evidence_not_available_in_provided_text: 1
- extraction_not_feasible_due_to_insufficient_information_in_the_provided_text: 1
- further_details_unavailable_from_the_provided_text: 1
- information_extracted_does_not_mention_ibuprofen_or_any_relevant_diffusion_cell_: 1
- information_regarding_diffusion_cell_franz_type_studies_and_specific_endpoints_i: 1
- initial_extraction_reveals_potential_relevance_to_ibuprofen_formulation_but_lack: 1
- insufficient_content_in_provided_text_to_determine_evidence: 1
- insufficient_content_provided_to_determine_details: 1
- insufficient_content_to_determine_extraction_details: 1
- insufficient_content_to_extract_specific_details_regarding_the_formulation_endpo: 1
- insufficient_evidence_related_to_ibuprofen_or_diffusion_cells_focus_on_traumatic: 1
- insufficient_extractable_data_in_the_provided_text: 1
- insufficient_extractable_evidence_details_available_from_the_document_text: 1
- insufficient_extractable_evidence_in_provided_text: 1
- insufficient_information_available_content_consists_mainly_of_navigation_and_sup: 1
- insufficient_information_available_from_the_provided_text: 1
- insufficient_information_available_in_the_excerpt: 1
- insufficient_information_available_in_the_provided_document: 1
- insufficient_information_available_to_assess_content: 1
- insufficient_information_available_to_determine_extraction_route: 2
- insufficient_information_for_specific_extraction: 1
- insufficient_information_in_the_provided_text: 1
- insufficient_information_to_determine_evidence_related_to_ibuprofen_or_dermal_fo: 1
- lacks_sufficient_extractable_evidence_regarding_ibuprofen: 1
- missing_structured_and_pdf_router_source: 236
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 63
- missing_structured_and_pdf_router_source_html_remote_httperror: 5
- no_clear_evidence_extraction_points_identified_from_the_provided_document_text: 1
- no_clear_evidence_extraction_routes_identified_from_the_provided_text: 1
- no_clear_extractable_evidence_found_in_provided_text: 1
- no_clear_extractable_evidence_found_in_the_provided_document: 1
- no_clear_extractable_evidence_related_to_ibuprofen_or_diffusion_cells_in_the_pro: 1
- no_clear_mention_of_ibuprofen_or_relevant_diffusion_methods: 1
- no_detailed_evidence_extraction_available_from_the_provided_document: 1
- no_evidence_related_to_ibuprofen_or_dermal_formulations_found: 1
- no_extractable_content_identified_in_the_provided_pages: 1
- no_extractable_evidence_available: 1
- no_extractable_evidence_available_from_provided_document: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_in_provided_pages: 1
- no_extractable_evidence_identified_in_the_text_provided: 1
- no_extractable_evidence_present: 1
- no_extractable_evidence_provided_in_the_document_text: 1
- no_extractable_evidence_regarding_ibuprofen_or_diffusion_cell_found: 1
- no_extractable_evidence_regarding_ibuprofen_or_related_formulations_found_in_the: 1
- no_extractable_evidence_related_to_ibuprofen_found_in_the_provided_document: 1
- no_extractable_evidence_was_found_in_the_displayed_document: 1
- no_relevant_content_found_regarding_ibuprofen_or_diffusion_cells: 1
- no_relevant_content_from_the_provided_text: 1
- no_relevant_data_appears_to_be_extractable_from_the_provided_text: 1
- no_relevant_data_extraction_possible: 1
- no_relevant_data_related_to_ibuprofen_dermal_formulation_extraction_found_in_pro: 1
- no_relevant_data_related_to_ibuprofen_or_diffusion_cells_found: 1
- no_relevant_evidence_extracted_regarding_ibuprofen_or_diffusion_studies: 1
- no_relevant_evidence_found_in_the_document: 2
- no_relevant_evidence_on_ibuprofen_or_diffusion_cells_found_in_the_available_text: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_found_in_the_do: 1
- no_relevant_evidence_related_to_ibuprofen_or_diffusion_cells_content_appears_to_: 1
- no_relevant_extractable_evidence_found: 1
- no_relevant_extractable_evidence_found_in_the_provided_document_section: 2
- no_relevant_extractable_evidence_identified: 1
- no_relevant_information_about_ibuprofen_or_dermal_formulations_found_in_the_prov: 1
- no_relevant_information_extracted_regarding_ibuprofen_or_the_use_of_diffusion_ce: 1
- no_relevant_information_found_in_the_provided_document_text: 1
- no_relevant_information_found_in_the_provided_text: 1
- no_relevant_information_found_regarding_ibuprofen_or_dermal_formulations: 2
- no_relevant_information_on_ibuprofen_or_dermal_formulations_found_in_the_provide: 1
- no_relevant_information_regarding_ibuprofen_or_dermal_formulation_extraction: 1
- no_relevant_information_regarding_ibuprofen_or_related_dermal_formulations: 1
- no_relevant_information_related_to_ibuprofen_or_diffusion_studies_was_found: 1
- no_specific_evidence_extraction_routes_identified_from_the_provided_text: 1
- no_specific_evidence_related_to_ibuprofen_extraction_identified: 1
- no_specific_experimental_details_or_results_are_provided_in_the_pages_shown: 1
- no_specific_extractable_evidence_on_ibuprofen_or_diffusion_methodologies_availab: 1
- only_basic_information_available_from_the_document_headers: 1
- only_structural_webpage_content_found_no_relevant_extractable_evidence_regarding: 1
- potential_for_extracting_data_on_a_mixed_micellar_gel_formulation_for_ibuprofen_: 1
- some_details_about_barriers_and_endpoints_are_not_specified: 1
- the_content_does_not_mention_ibuprofen_or_relevant_diffusion_cells_lacking_extra: 1
- the_content_does_not_provide_explicit_data_related_to_ibuprofen_or_diffusion_cel: 1
- the_content_does_not_provide_sufficient_data_to_identify_specific_extraction_poi: 1
- the_content_mainly_discusses_molecular_interactions_and_structural_preservation_: 1
- the_content_primarily_contains_navigation_and_technical_information_about_europe: 1
- the_document_appears_to_be_a_molecular_dynamics_simulation_study_discussing_ibup: 1
- the_document_appears_to_be_focused_on_drug_release_coatings_and_does_not_mention: 1
- the_document_appears_to_be_focused_on_polyphenolic_components_and_does_not_menti: 1
- the_document_appears_to_be_incomplete_and_not_directly_related_to_ibuprofen_or_d: 1
- the_document_appears_to_focus_on_the_biological_effects_of_certain_compounds_rat: 1
- the_document_appears_to_focus_on_the_effects_of_ibuprofen_in_combination_with_ot: 1
- the_document_contains_no_extractable_evidence_related_to_ibuprofen_or_specific_d: 1
- the_document_contains_no_structured_evidence_related_to_ibuprofen_or_formulation: 1
- the_document_content_does_not_provide_relevant_information_for_extraction: 1
- the_document_content_does_not_provide_sufficient_information_to_determine_extrac: 1
- the_document_content_does_not_provide_sufficient_information_to_determine_specif: 1
- the_document_does_not_contain_extractable_evidence_relevant_to_ibuprofen_formula: 1
- the_document_does_not_contain_relevant_extractable_evidence_related_to_ibuprofen: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_its_fo: 1
- the_document_does_not_mention_ibuprofen_or_diffusion_cells_evidence_extraction_i: 1
- the_document_does_not_pertain_to_ibuprofen_or_relevant_dermal_formulations: 1
- the_document_does_not_provide_any_extractable_evidence_related_to_ibuprofen_diff: 1
- the_document_does_not_provide_clear_evidence_or_structured_data_that_can_be_extr: 1
- the_document_does_not_provide_concrete_evidence_regarding_endpoints_or_formulati: 1
- the_document_does_not_provide_relevant_information_on_ibuprofen_or_related_derma: 1
- the_document_does_not_provide_sufficient_information_regarding_ibuprofen_or_diff: 1
- the_document_doesn_t_provide_specific_content_related_to_ibuprofen_or_details_on: 1
- the_document_mainly_discusses_drug_induced_toxic_epidermal_necrolysis_and_does_n: 1
- the_document_only_includes_the_first_two_pages_which_are_not_informative_regardi: 1
- the_document_predominantly_includes_navigation_and_setup_content_from_europe_pmc: 1
- the_document_preview_does_not_provide_sufficient_detail_to_identify_extractable_: 1
- the_document_primarily_contains_navigation_information_related_to_europe_pmc_and: 1
- the_document_primarily_contains_navigational_and_administrative_text_from_europe: 1
- the_document_primarily_discusses_naproxen_and_famotidine_in_the_context_of_acute: 1
- the_document_primarily_discusses_skin_cancers_and_their_molecular_mechanisms_wit: 1
- the_document_provided_does_not_contain_the_necessary_evidence_related_to_ibuprof: 1
- the_document_provided_is_information_about_the_e_theses_online_service_and_does_: 1
- the_document_seems_to_focus_on_drug_toxicity_assays_using_biofabricated_models_a: 1
- the_paper_discusses_plga_implants_and_fluid_renewal_effects_but_does_not_mention: 1
- the_paper_discusses_sodium_coupled_monocarboxylate_transporters_particularly_slc: 1
- the_paper_discusses_the_role_of_nsaids_ibuprofen_included_in_ad_but_does_not_foc: 1
- the_paper_discusses_the_synthesis_and_characterization_of_ibuprofen_functionaliz: 1
- the_paper_does_not_discuss_ibuprofen_or_its_dermal_formulations: 1
- the_provided_text_does_not_contain_relevant_evidence_related_to_ibuprofen_or_spe: 1
- the_study_focuses_on_the_interactions_and_loading_capacity_of_ibuprofen_with_mil: 1
- this_paper_discusses_a_hydrogel_designed_for_nsaid_delivery_but_lacks_sufficient: 1
- this_paper_evaluates_new_ibuprofen_polymeric_prodrugs_and_includes_in_vitro_eval: 1
- unspecified: 35
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
- skipped: 63
#### patch_area
- applied: 2
- skipped: 36
#### patch_endpoint_time
- applied: 13
#### patch_endpoint_value
- applied: 16
- skipped: 34

## Patch Success Counts
- patch_area: 2
- patch_endpoint_time: 13
- patch_endpoint_value: 16