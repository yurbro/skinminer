# Run Report: run_e539b56a6759

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Stage models: `{'llm_triage': 'gpt-4o-mini', 'routing': 'gpt-4o-mini', 'text_extract': 'gpt-4o-mini', 'table_extract': 'gpt-4o-mini', 'figure_triage': 'gpt-4o-mini', 'figure_vlm': 'gpt-4o-mini', 'figure_map': 'gpt-4o-mini', 'llm_adjudicate': 'gpt-4o-mini'}`
- Assembled records: `90`
- Final records evaluated: `90`
- Actually verified: `2`
- Final unresolved: `65`
- Final rejected: `23`

## Route Distribution
- figure: 20
- mixed: 9
- table: 15
- text: 14
- unresolved: 476

## Extractor Outputs
- figure: 8
- table: 65
- text: 22

## Verification Outcomes
- rejected: 23
- unresolved: 65
- verified: 2

## Scope Buckets
- out_of_scope: 13
- recoverable_unresolved: 55
- strict_in_scope: 2
- useful_but_out_of_scope: 20

## Scope Tags
- non_target_api: 13
- recoverable_api_basis: 29
- recoverable_area: 12
- recoverable_endpoint: 5
- recoverable_figure_digitization: 2
- recoverable_support_gap: 43
- recoverable_unresolved: 55
- useful_api_concentration_out_of_scope: 11
- useful_but_out_of_scope: 20
- useful_device_out_of_scope: 3
- useful_endpoint_out_of_scope: 4
- useful_study_type_out_of_scope: 7

## Failure Taxonomy
- ambiguous_api_concentration: 42
- figure_digitization_failed: 3
- insufficient_evidence: 73
- missing_api_concentration: 6
- missing_area: 19
- missing_endpoint: 7
- not_target_api: 13
- not_target_api_concentration: 11
- not_target_device: 3
- not_target_study_type: 11
- percent_only: 7
- unit_normalization_failed: 2

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 23
- figure_digitization_failed: 2
- insufficient_evidence: 28
- missing_api_concentration: 1
- missing_area: 15
- missing_endpoint: 4
- not_target_api: 8
- not_target_api_concentration: 6
- not_target_device: 1
- not_target_study_type: 9
- percent_only: 7
- unit_normalization_failed: 2
### mixed
- ambiguous_api_concentration: 5
- figure_digitization_failed: 1
- insufficient_evidence: 22
- missing_api_concentration: 1
- missing_area: 3
- missing_endpoint: 3
- not_target_api_concentration: 1
### table
- ambiguous_api_concentration: 14
- insufficient_evidence: 13
- missing_api_concentration: 4
- missing_area: 1
- not_target_api: 5
- not_target_api_concentration: 4
- not_target_study_type: 2
### text
- insufficient_evidence: 10
- not_target_device: 2

## Figure Stage Counts
- digitization_no_output: 3
- digitized_curves: 20
- digitized_endpoints_failed: 7
- digitized_endpoints_ok: 20
- mapped_curves: 7
- triage_artifacts: 19
- triage_digitize_candidates: 18
- triage_has_permeation_plot_true: 18
- unmapped_curves: 13
- vlm_readings_readable: 31
- vlm_readings_total: 31
- vlm_used_as_final: 14

## Figure Gate Counts
- routed_candidates: 28
- after_gate: 21
- skipped:missing_explicit_figure_signal: 7

## Figure Triage Routes
- digitize: 18
- skip: 1

## Figure Plot Presence
- false: 1
- true: 18

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 3
- recommended_route:skip: 1
- ticks_readable:uncertain: 7
- why_not_digitizable:data_is_not_presented_as_a_continuous_curve_suitable_for_digitization_it_consist: 1

## Figure Digitization Statuses
- digitization_no_output: 3
- fail_missing_axis_range: 4
- ok: 20

## Figure Mapping Statuses
- underconstrained_labels: 13
- vision_mapped: 7

## Figure VLM Grounding Statuses
- figure_label_space: 2
- figure_label_space_only: 11
- source_label_space: 5
- ungrounded: 13

## Figure VLM Reconciliation Statuses
- cv_only: 14
- cv_vlm_agree: 1
- cv_vlm_disagreement: 2
- vlm_only: 14

## LLM Reliability
- none

## LLM Adjudication Audit
- rows: 33
- priority_bucket:high: 29
- priority_bucket:medium: 4
- review_focus:api_concentration_basis: 28
- review_focus:diffusion_area: 3
- review_focus:endpoint_value: 2
- recommended_status:rejected: 7
- recommended_status:unresolved: 26
- disagreement:scope_bucket_disagreement: 7
- disagreement:status_disagreement: 7

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
- downloaded: 228
- error: 1
- resolved: 85
- unresolved: 220
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- cannot_determine_specific_extractable_evidence_from_the_provided_document_text: 1
- cannot_extract_evidence_due_to_insufficient_information_in_the_document: 1
- content_appears_largely_unstructured_and_unreachable_for_specific_extraction: 1
- content_does_not_provide_sufficient_extractable_evidence: 1
- content_extraction_may_need_further_context_from_the_full_document: 1
- content_from_page_1_primarily_relates_to_website_navigation_and_does_not_include: 1
- content_in_the_extract_does_not_provide_clear_evidence_regarding_endpoints_or_fo: 1
- content_not_accessible_seems_like_an_interface_issue: 1
- document_appears_to_be_an_early_page_or_introductory_material_lacking_specific_d: 1
- document_content_does_not_provide_extractable_evidence_related_to_ibuprofen_or_d: 1
- document_content_primarily_pertains_to_permeation_enhancers_and_does_not_explici: 1
- document_content_unavailable_check_pdf_for_details: 1
- document_does_not_provide_extractable_evidence_regarding_ibuprofen_or_relevant_f: 1
- document_does_not_provide_relevant_evidence_for_ibuprofen_formulation: 1
- document_text_is_not_accessible: 1
- evidence_extraction_details_are_limited_specific_endpoint_and_formulation_detail: 1
- evidence_extraction_details_are_not_available_from_the_provided_document_excerpt: 1
- evidence_extraction_route_remains_unclear_due_to_lacking_defined_sections: 1
- extractable_evidence_is_limited_based_on_the_provided_document_excerpt: 1
- extractable_evidence_regarding_ibuprofen_is_present_but_specifics_on_methodologi: 1
- extraction_carrier_and_details_unclear_due_to_insufficient_text: 1
- extraction_details_are_vague_and_not_enough_structured_evidence_is_available: 1
- extraction_of_information_is_limited_based_on_available_context: 1
- first_page_contains_no_relevant_information: 1
- further_details_about_the_formulations_and_study_setup_may_be_missing_making_ext: 1
- further_details_on_extraction_routes_need_to_be_clarified_as_document_content_is: 1
- initial_evidence_extraction_route_unclear_due_to_insufficient_information_in_pro: 1
- initial_findings_from_a_randomized_controlled_trial_on_a_dermal_formulation: 1
- initial_pages_do_not_contain_relevant_data_for_evidence_extraction: 1
- initial_pages_mostly_contain_menu_and_disclaimers_no_extractable_evidence_found: 1
- insufficient_content_available_for_detailed_extraction: 1
- insufficient_data_retrieved_from_the_provided_source: 1
- insufficient_details_available_for_concrete_extraction: 1
- insufficient_evidence_available_page_content_is_related_to_europe_pmc_interface_: 1
- insufficient_evidence_for_extraction: 1
- insufficient_information_available_from_the_document_text: 1
- insufficient_information_available_to_extract_evidence_related_to_ibuprofen_and_: 1
- insufficient_information_available_to_extract_relevant_evidence: 1
- insufficient_information_for_extraction: 1
- insufficient_information_in_the_document_to_determine_extraction_details: 1
- insufficient_information_in_the_provided_text_to_extract_relevant_evidence: 1
- insufficient_information_to_determine_relevant_extraction_routes: 1
- missing_structured_and_pdf_router_source: 229
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 69
- missing_structured_and_pdf_router_source_html_remote_httperror: 4
- no_additional_context_or_specifics_captured_from_the_pages_provided: 1
- no_clear_evidence_extraction_possible_from_the_provided_page_further_information: 1
- no_clear_extractable_evidence_found_from_the_provided_text: 1
- no_evidence_of_ibuprofen_or_diffusion_cell_mentioned_in_the_document: 1
- no_evidence_related_to_ibuprofen_diffusion_cells_or_formulations_found_in_the_pr: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_from_the_document: 1
- no_extractable_evidence_found_in_provided_text: 1
- no_extractable_evidence_found_in_the_provided_document_text: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_found_related_to_ibuprofen_or_relevant_diffusion_cell_me: 1
- no_extractable_evidence_identified_from_the_provided_text: 1
- no_extractable_evidence_regarding_ibuprofen_or_specific_analytical_methods: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cell: 1
- no_extractable_evidence_related_to_ibuprofen_was_found_in_the_document: 1
- no_information_regarding_ibuprofen_or_diffusion_cells_is_present_in_the_document: 1
- no_mention_of_ibuprofen_or_relevant_extraction_evidence_found: 1
- no_relevant_content_extracted_from_the_provided_text: 1
- no_relevant_content_found_related_to_ibuprofen_or_diffusion_studies: 1
- no_relevant_data_extracted_from_the_provided_document: 1
- no_relevant_data_found_in_the_provided_content: 1
- no_relevant_evidence_extractable_from_the_text_provided_unclear_details_about_th: 1
- no_relevant_evidence_found_in_the_provided_document: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_dermal_formulation: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_on_ibuprofen_or_dermal_application_found_in_the_provided_ex: 1
- no_relevant_evidence_on_ibuprofen_or_diffusion_cell: 1
- no_relevant_evidence_pertaining_to_ibuprofen_dermal_formulation_found_in_the_pro: 1
- no_relevant_evidence_related_to_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_extractable_evidence_related_to_ibuprofen_or_its_dermal_formulations: 1
- no_relevant_extraction_evidence_found_document_content_primarily_consists_of_nav: 1
- no_relevant_extraction_evidence_found_in_the_provided_document_text: 1
- no_relevant_extraction_sources_in_the_provided_document_sections: 1
- no_relevant_information_extracted_from_the_provided_text: 1
- no_relevant_information_for_ibuprofen_dermal_formulations: 1
- no_relevant_information_found_in_the_provided_document: 1
- no_relevant_information_identified_regarding_ibuprofen_or_diffusion_cell: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_on_ibuprofen_or_diffusion_cells_found: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cell_extraction_found_o: 1
- no_specific_evidence_extractable_from_provided_content: 1
- no_specific_evidence_found_regarding_ibuprofen_or_diffusion_cells: 1
- no_specific_evidence_related_to_ibuprofen_or_diffusion_cells_found_in_the_excerp: 1
- no_specific_extractable_evidence_found_in_the_provided_text: 1
- no_specific_extraction_points_identified_in_the_provided_text: 1
- not_related_to_ibuprofen_or_dermal_formulations: 1
- only_contains_introductory_and_navigation_information: 1
- paper_discusses_a_zn_based_mof_no_relevant_details_related_to_ibuprofen_or_skin_: 1
- paper_discusses_emerging_contaminants_and_pharmaceuticals_but_does_not_focus_on_: 1
- paper_discusses_nonsteroidal_anti_inflammatory_drugs_but_does_not_provide_specif: 1
- source_document_provides_limited_information: 1
- the_content_does_not_provide_enough_details_to_extract_relevant_evidence: 1
- the_content_from_the_provided_document_does_not_indicate_the_presence_of_ibuprof: 1
- the_content_from_the_provided_source_does_not_contain_relevant_information_regar: 1
- the_content_is_not_related_to_dermal_formulations_or_ibuprofen: 1
- the_content_provided_does_not_contain_relevant_information_regarding_ibuprofen_o: 1
- the_document_appears_to_be_an_article_discussing_the_effects_of_cyclooxygenase_i: 1
- the_document_appears_to_be_unrelated_to_oa_ibuprofen_or_dermal_formulations: 1
- the_document_appears_to_focus_on_skin_cancers_and_molecular_mechanisms_not_ibupr: 1
- the_document_contains_no_relevant_extractable_evidence_related_to_ibuprofen_or_d: 1
- the_document_content_does_not_provide_extractable_evidence_relevant_to_the_speci: 1
- the_document_does_not_appear_to_be_related_to_oa_or_ibuprofen_formulations: 1
- the_document_does_not_appear_to_contain_relevant_information_on_ibuprofen_or_dif: 1
- the_document_does_not_contain_clear_evidence_related_to_ibuprofen_or_diffusion_c: 1
- the_document_does_not_contain_detectable_evidence_related_to_ibuprofen_or_diffus: 1
- the_document_does_not_contain_extractable_clinical_data_related_to_ibuprofen_or_: 1
- the_document_does_not_contain_extractable_evidence_related_to_ibuprofen_dermal_f: 1
- the_document_does_not_mention_ibuprofen_or_diffusion_cells_and_no_endpoints_are_: 1
- the_document_does_not_mention_ibuprofen_or_relevant_diffusion_studies: 1
- the_document_does_not_provide_adequate_information_for_specific_extraction_route: 1
- the_document_does_not_provide_clear_evidence_related_to_the_extraction_requireme: 1
- the_document_does_not_provide_extractable_evidence_related_to_ibuprofen_or_diffu: 1
- the_document_does_not_provide_relevant_extraction_details: 1
- the_document_does_not_provide_relevant_information_for_the_extraction_process_re: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_or_its_de: 1
- the_document_does_not_provide_relevant_information_related_to_ibuprofen_or_derma: 1
- the_document_does_not_provide_specific_extractable_evidence_related_to_ibuprofen: 1
- the_document_is_mostly_metadata_and_does_not_provide_the_relevant_experimental_o: 1
- the_document_lacks_specific_data_related_to_ibuprofen_or_relevant_diffusion_cell: 1
- the_document_primarily_consists_of_metadata_and_navigational_content_with_no_ext: 1
- the_document_primarily_contains_metadata_and_does_not_provide_relevant_evidence_: 1
- the_document_primarily_contains_navigation_information_for_europe_pmc_and_does_n: 1
- the_document_primarily_deals_with_drug_delivery_modeling_and_does_not_mention_ib: 1
- the_document_primarily_discusses_neutrophil_migration_and_nsaid_effects_without_: 1
- the_document_primarily_discusses_the_biological_activity_of_polyphenolic_compone: 1
- the_document_primarily_discusses_the_impact_of_emerging_contaminants_on_wastewat: 1
- the_document_primarily_discusses_the_response_of_synoviocyte_models_to_ibuprofen: 1
- the_document_primarily_focuses_on_molecular_dynamics_and_diffusivity_with_a_ment: 1
- the_document_primarily_pertains_to_non_haemolytic_nanoemulsions_for_intravenous_: 1
- the_document_provided_appears_to_be_an_administrative_interface_for_a_research_r: 1
- the_document_provided_does_not_contain_specific_information_related_to_diffusion: 1
- the_document_provided_does_not_contain_specific_relevant_information_regarding_i: 1
- the_document_provided_does_not_contain_sufficient_information_to_extract_specifi: 1
- the_document_provided_is_primarily_navigation_related_and_does_not_contain_relev: 1
- the_document_provides_no_relevant_information_regarding_ibuprofen_or_a_diffusion: 1
- the_document_text_provided_lacks_specific_experimental_details_endpoints_and_fin: 1
- the_paper_discusses_derivatives_of_2_4_isobutylphenyl_propionic_acid_which_is_kn: 1
- the_paper_discusses_enhancement_of_drug_penetration_but_does_not_specify_formula: 1
- the_paper_focuses_on_mucilage_from_lepidium_sativum_and_does_not_mention_ibuprof: 1
- the_summary_does_not_provide_enough_evidence_regarding_ibuprofen_or_detailed_fin: 1
- this_document_appears_to_be_primarily_focused_on_biomof_cellulose_glycerogel_sca: 1
- this_document_does_not_seem_relevant_to_ibuprofen_or_its_dermal_formulation: 1
- unspecified: 29
- validates_a_static_franz_diffusion_cell_system_for_in_vitro_studies: 1
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
- skipped: 84
#### patch_area
- applied: 5
- skipped: 40
#### patch_endpoint_time
- applied: 21
#### patch_endpoint_value
- applied: 23
- skipped: 37

## Patch Success Counts
- patch_area: 5
- patch_endpoint_time: 21
- patch_endpoint_value: 23