# Run Report: run_e27a1d3825da

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Assembled records: `126`
- Final records evaluated: `126`
- Actually verified: `29`
- Final unresolved: `27`
- Final rejected: `70`

## Route Distribution
- figure: 13
- mixed: 8
- table: 19
- text: 9
- unresolved: 492

## Extractor Outputs
- figure: 30
- table: 86
- text: 21

## Verification Outcomes
- rejected: 70
- unresolved: 27
- verified: 29

## Failure Taxonomy
- figure_digitization_failed: 11
- insufficient_evidence: 2
- missing_api_concentration: 9
- missing_area: 24
- missing_endpoint: 10
- missing_endpoint_time: 3
- not_target_api: 12
- not_target_device: 66
- not_target_study_type: 24
- percent_only: 29
- unit_normalization_failed: 10

## Failure Taxonomy By Route
### figure
- figure_digitization_failed: 11
- missing_area: 19
- missing_endpoint: 6
- not_target_api: 1
- not_target_device: 25
- not_target_study_type: 6
- percent_only: 8
- unit_normalization_failed: 8
### mixed
- missing_area: 1
- missing_endpoint: 3
- missing_endpoint_time: 2
- not_target_api: 4
- not_target_device: 4
- unit_normalization_failed: 1
### table
- missing_api_concentration: 1
- missing_area: 4
- not_target_api: 7
- not_target_device: 36
- not_target_study_type: 18
- percent_only: 21
- unit_normalization_failed: 1
### text
- insufficient_evidence: 2
- missing_api_concentration: 8
- missing_endpoint: 1
- missing_endpoint_time: 1
- not_target_device: 1

## Figure Stage Counts
- digitized_curves: 32
- digitized_endpoints_failed: 1
- digitized_endpoints_ok: 32
- mapped_curves: 30
- triage_artifacts: 15
- triage_digitize_candidates: 14
- unmapped_curves: 2

## Figure Gate Counts
- routed_candidates: 21
- after_gate: 15
- skipped:missing_explicit_figure_signal: 6

## Figure Triage Routes
- digitize: 14
- skip: 1

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 2
- recommended_route:skip: 1
- ticks_readable:uncertain: 1
- why_not_digitizable:lacks_clear_endpoint_curves_and_data_representation: 1

## Figure Digitization Statuses
- fail_missing_axis_range: 1
- ok: 32

## Figure Mapping Statuses
- unmapped: 2
- vision_mapped: 30

## LLM Reliability
- none

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-03-28.v1
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1

## Blockage Summary
### Access Statuses
- downloaded: 233
- error: 1
- resolved: 79
- unresolved: 228
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- additional_details_required_for_thorough_extraction: 1
- clinical_study_investigating_nsaid_effects_on_aldosterone_glucuronidation: 1
- content_appears_to_be_inaccessible_no_relevant_information_available_from_the_pr: 1
- content_does_not_provide_sufficient_information_for_detailed_extraction: 1
- content_from_pages_is_unavailable_needs_further_exploration_for_detailed_study_a: 1
- content_from_the_document_is_insufficient_to_extract_evidence_based_on_the_crite: 1
- content_mainly_includes_navigational_instructions_and_lacks_specific_scientific_: 1
- content_primarily_focused_on_the_database_and_updates_lacks_specific_details_on_: 1
- content_primarily_relates_to_ibuprofen_s_role_as_a_plasticizer_no_explicit_menti: 1
- content_useful_but_lacks_detailed_endpoints_or_formulations: 1
- document_appears_to_be_about_a_novel_nanocarrier_for_drug_release_with_no_mentio: 1
- document_appears_to_focus_on_chiral_membranes_no_relevant_evidence_related_to_ib: 1
- document_begins_with_navigational_elements_and_lacks_substantive_content_for_ext: 1
- document_content_is_largely_inaccessible_appears_to_be_a_navigation_or_landing_p: 1
- document_primarily_about_microneedle_design_and_optimization_contains_no_relevan: 1
- document_primarily_contains_metadata_and_no_relevant_extractable_evidence: 1
- evidence_details_are_not_provided_within_the_text: 1
- evidence_extraction_is_limited_due_to_lack_of_specific_details_in_the_provided_d: 1
- evidence_extraction_is_not_feasible_from_the_provided_text: 1
- evidence_extraction_not_feasible_from_provided_content: 1
- evidence_extraction_route_uncertain_due_to_lack_of_detailed_content: 1
- evidence_not_extractable_from_the_provided_document_sections: 1
- extraction_information_is_insufficient_and_unclear_from_the_provided_document_te: 1
- full_text_is_inaccessible_only_front_pages_of_the_document_are_provided: 1
- information_on_diffusion_cell_or_franz_confirmation_is_not_provided: 1
- initial_content_did_not_provide_extractable_evidence_details: 1
- initial_findings_from_a_clinical_investigation_on_biatain_ibu_for_venous_leg_ulc: 1
- initial_pages_do_not_contain_relevant_evidence_further_extraction_needed_from_re: 1
- initial_pages_do_not_contain_relevant_extractable_evidence: 1
- insufficient_content_to_provide_structured_extraction: 1
- insufficient_information_for_structured_extraction: 1
- insufficient_information_in_the_provided_text_to_determine_specific_details_abou: 1
- insufficient_information_to_extract_relevant_evidence: 1
- lacks_sufficient_evidence_on_any_specific_formulations_or_endpoints: 1
- missing_structured_and_pdf_router_source: 240
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 60
- missing_structured_and_pdf_router_source_html_remote_connectionerror: 1
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- no_content_related_to_ibuprofen_or_diffusion_cells_detected_in_the_provided_page: 1
- no_detailed_evidence_extractable_from_the_content_provided: 1
- no_direct_evidence_extraction_possible_from_provided_text: 1
- no_extractable_evidence_found_in_the_provided_document: 1
- no_extractable_evidence_found_in_the_provided_document_sections: 1
- no_extractable_evidence_found_in_the_provided_text: 1
- no_extractable_evidence_found_in_the_text_provided: 1
- no_extractable_evidence_found_in_the_visible_document_text: 1
- no_extractable_evidence_found_related_to_ibuprofen_or_relevant_formulation: 1
- no_extractable_evidence_found_related_to_ibuprofen_or_specific_diffusion_methods: 1
- no_extractable_evidence_identified_related_to_ibuprofen_or_diffusion_testing: 1
- no_extractable_evidence_provided: 1
- no_extractable_evidence_related_to_ibuprofen_found: 1
- no_extractable_evidence_related_to_ibuprofen_or_dermal_formulations: 1
- no_extractable_evidence_related_to_ibuprofen_or_diffusion_cells_found_in_the_doc: 1
- no_extractable_evidence_seen_in_the_available_pages: 1
- no_identifying_information_on_ibuprofen_or_diffusion_cells_present_in_the_provid: 1
- no_pertinent_information_extracted_from_the_provided_text: 1
- no_relevant_content_found_in_the_provided_document_text: 1
- no_relevant_content_found_in_the_provided_pages: 1
- no_relevant_content_found_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_data_concerning_ibuprofen_or_diffusion_cell_methods_is_present_in_th: 1
- no_relevant_data_extracted_regarding_ibuprofen_or_its_dermal_formulation: 1
- no_relevant_details_extracted_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_evidence_for_ibuprofen_dermal_formulation_was_identified_in_the_prov: 1
- no_relevant_evidence_found_in_the_provided_pages: 1
- no_relevant_evidence_found_in_the_provided_text: 1
- no_relevant_evidence_identified: 1
- no_relevant_evidence_provided_in_the_visible_text: 1
- no_relevant_evidence_related_to_ibuprofen_or_its_dermal_formulation_found_in_the: 1
- no_relevant_extraction_evidence_found_in_provided_document_section: 1
- no_relevant_extraction_evidence_found_in_the_provided_document: 1
- no_relevant_extraction_points_identified_in_the_provided_document: 1
- no_relevant_ibuprofen_related_evidence_found: 1
- no_relevant_information_about_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_about_ibuprofen_or_diffusion_cell_found: 1
- no_relevant_information_extracted_regarding_ibuprofen_formulation_and_diffusion_: 1
- no_relevant_information_extracted_related_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_found_in_the_provided_text: 2
- no_relevant_information_found_regarding_ibuprofen: 1
- no_relevant_information_found_regarding_ibuprofen_diffusion_cell_or_endpoints_re: 1
- no_relevant_information_found_regarding_ibuprofen_or_dermal_formulation: 2
- no_relevant_information_found_regarding_ibuprofen_or_relevant_extraction: 1
- no_relevant_information_found_specific_to_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_on_ibuprofen_or_diffusion_methods_found: 1
- no_relevant_information_related_to_ibuprofen_dermal_formulation_found: 1
- no_specific_endpoint_or_diffusion_cell_information_provided_in_the_text: 1
- no_specific_endpoints_or_formulations_are_directly_extractable_from_the_provided: 1
- no_specific_evidence_about_ibuprofen_or_diffusion_cells_is_mentioned: 1
- no_specific_evidence_found_in_extractable_formats: 1
- no_specific_extractable_evidence_has_been_identified_due_to_the_lack_of_relevant: 1
- no_specific_information_on_endpoint_or_formulation_details_available_in_provided: 1
- no_specific_information_related_to_ibuprofen_or_dermal_formulations_found: 1
- not_enough_information_for_detailed_extraction: 1
- only_general_information_available_due_to_non_accessible_detailed_content: 1
- only_title_and_references_to_ibuprofen_in_current_text: 1
- paper_discusses_mastocytosis_related_to_cox_inhibitors_including_ibuprofen: 1
- paper_discusses_separation_of_ibuprofen_using_polymeric_membranes_but_does_not_d: 1
- paper_focuses_on_an_injectable_ibuprofen_formulation_but_lacks_clear_evidence_ex: 1
- source_content_does_not_provide_sufficient_detail_for_extraction: 1
- the_content_does_not_provide_specific_information_related_to_ibuprofen_or_diffus: 1
- the_document_appears_to_be_about_the_synthesis_method_and_does_not_provide_extra: 1
- the_document_appears_to_be_focused_on_pharmaceuticals_removal_using_clay_materia: 1
- the_document_appears_to_be_non_extractive_and_contains_promotional_content_witho: 1
- the_document_appears_to_be_primarily_informational_and_does_not_provide_specific: 1
- the_document_appears_to_be_related_to_ibuprofen_and_transdermal_delivery_but_spe: 1
- the_document_appears_to_contain_introductory_information_and_website_navigation_: 1
- the_document_appears_to_focus_on_drug_delivery_mechanisms_but_does_not_specifica: 1
- the_document_appears_to_not_contain_relevant_information_about_ibuprofen_or_any_: 1
- the_document_content_does_not_appear_to_include_relevant_extractable_evidence: 1
- the_document_content_does_not_contain_relevant_information_regarding_ibuprofen_o: 1
- the_document_content_does_not_pertain_to_ibuprofen_or_relevant_dermal_studies: 1
- the_document_content_is_mostly_related_to_javascript_issues_and_does_not_provide: 1
- the_document_content_is_not_fully_accessible_further_review_needed_for_more_deta: 1
- the_document_content_provided_does_not_contain_relevant_information_for_extracti: 1
- the_document_does_not_contain_explicit_evidence_related_to_ibuprofen_or_diffusio: 1
- the_document_does_not_contain_relevant_data_for_extraction_related_to_ibuprofen_: 1
- the_document_does_not_contain_relevant_evidence_related_to_ibuprofen_or_any_derm: 1
- the_document_does_not_contain_relevant_information_about_ibuprofen_or_formulatio: 1
- the_document_does_not_contain_relevant_information_for_the_extraction_route: 1
- the_document_does_not_contain_specific_information_regarding_ibuprofen_or_any_re: 1
- the_document_does_not_directly_relate_to_ibuprofen_or_dermal_formulations: 1
- the_document_does_not_discuss_ibuprofen_or_related_dermal_formulations: 1
- the_document_does_not_provide_enough_information_to_confirm_extraction_routes_re: 1
- the_document_does_not_provide_extractable_evidence_relevant_to_ibuprofen_or_diff: 1
- the_document_does_not_provide_relevant_content_related_to_ibuprofen_or_diffusion: 1
- the_document_does_not_provide_relevant_evidence_for_ibuprofen_or_specific_drug_d: 1
- the_document_does_not_provide_relevant_information_regarding_ibuprofen_or_relate: 1
- the_document_does_not_provide_specific_details_on_studies_or_formulations: 1
- the_document_does_not_provide_specific_extractable_evidence_from_the_first_two_p: 1
- the_document_does_not_provide_specific_extractable_evidence_related_to_ibuprofen: 1
- the_document_does_not_provide_sufficient_information_to_extract_detailed_evidenc: 1
- the_document_does_not_relate_to_ibuprofen_or_dermal_formulations: 1
- the_document_extracted_does_not_provide_relevant_information_on_ibuprofen_or_dif: 1
- the_document_is_a_review_of_therapeutic_options_in_chronic_rhinosinusitis_relate: 1
- the_document_is_incomplete_and_mostly_consists_of_website_navigation_without_con: 1
- the_document_mainly_contains_navigation_and_technical_information_related_to_eur: 1
- the_document_primarily_consists_of_introductory_content_with_no_relevant_text_ab: 1
- the_document_primarily_consists_of_metadata_and_does_not_contain_detailed_eviden: 1
- the_document_primarily_deals_with_a_gelatin_methacryloyl_scaffold_for_dental_app: 1
- the_document_primarily_discusses_nitric_oxide_and_prostaglandin_effects_no_relev: 1
- the_document_primarily_discusses_the_validation_of_a_franz_diffusion_cell_system: 1
- the_document_primarily_focuses_on_dexamethasone_and_amyloid_beta_and_does_not_co: 1
- the_document_primarily_relates_to_traumatic_brain_injury_no_direct_evidence_rega: 1
- the_document_seems_to_be_an_introductory_text_with_no_extractable_evidence_provi: 1
- the_document_seems_to_contain_web_navigation_content_and_lacks_the_main_scientif: 1
- the_document_seems_to_focus_on_a_systematic_review_of_interventions_for_chronic_: 1
- the_document_seems_unrelated_to_ibuprofen_and_does_not_provide_extractable_evide: 1
- the_document_text_does_not_provide_detailed_insight_regarding_endpoints_study_ty: 1
- the_full_detailed_content_and_specific_findings_regarding_ibuprofen_or_diffusion: 1
- the_paper_discusses_controlled_release_of_therapeutics_from_contact_lenses_but_d: 1
- the_paper_discusses_the_effects_of_nonsteroidal_anti_inflammatory_drugs_but_lack: 1
- the_paper_does_not_appear_to_mention_ibuprofen_or_relevant_dermal_formulation_de: 1
- the_paper_does_not_provide_identifiable_extractable_information_related_to_ibupr: 1
- the_paper_focuses_on_poly_l_lactic_acid_nanofiber_membranes_which_are_not_relate: 1
- the_provided_content_does_not_contain_relevant_information_for_extraction_regard: 1
- the_provided_text_does_not_contain_extractable_evidence_due_to_its_limitation_to: 1
- the_provided_text_does_not_contain_sufficient_information_regarding_studies_or_f: 1
- the_text_indicates_ibuprofen_is_discussed_but_further_details_on_study_type_and_: 1
- this_paper_does_not_relate_to_ibuprofen_or_dermal_formulations: 1
- unable_to_extract_evidence_due_to_incomplete_document_additional_pages_not_provi: 1
- unable_to_extract_relevant_evidence_due_to_lack_of_specified_content: 1
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
- applied: 20
- skipped: 9
#### patch_area
- applied: 7
- skipped: 64
#### patch_endpoint_time
- applied: 15
- skipped: 3
#### patch_endpoint_value
- applied: 13
- skipped: 10

## Patch Success Counts
- patch_api_concentration: 20
- patch_area: 7
- patch_endpoint_time: 15
- patch_endpoint_value: 13