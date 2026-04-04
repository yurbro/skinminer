# Run Report: run_41666c88a344

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Assembled records: `88`
- Final records evaluated: `88`
- Actually verified: `2`
- Final unresolved: `60`
- Final rejected: `26`

## Route Distribution
- figure: 15
- mixed: 4
- table: 14
- text: 18
- unresolved: 492

## Extractor Outputs
- figure: 27
- table: 52
- text: 15

## Verification Outcomes
- rejected: 26
- unresolved: 60
- verified: 2

## Scope Buckets
- out_of_scope: 12
- recoverable_unresolved: 55
- strict_in_scope: 2
- useful_but_out_of_scope: 19

## Failure Taxonomy
- ambiguous_api_concentration: 39
- figure_digitization_failed: 2
- insufficient_evidence: 55
- missing_api_concentration: 2
- missing_area: 9
- missing_endpoint: 3
- missing_endpoint_time: 3
- not_target_api: 12
- not_target_api_concentration: 15
- not_target_device: 19
- not_target_study_type: 4
- percent_only: 6
- unit_normalization_failed: 7

## Failure Taxonomy By Route
### figure
- ambiguous_api_concentration: 27
- figure_digitization_failed: 2
- insufficient_evidence: 24
- missing_api_concentration: 1
- missing_area: 7
- missing_endpoint: 2
- missing_endpoint_time: 1
- not_target_api: 7
- not_target_api_concentration: 9
- not_target_device: 12
- percent_only: 5
- unit_normalization_failed: 7
### mixed
- ambiguous_api_concentration: 2
- insufficient_evidence: 10
- missing_api_concentration: 1
- missing_area: 2
- not_target_api: 2
- not_target_device: 2
- not_target_study_type: 3
- percent_only: 1
### table
- ambiguous_api_concentration: 10
- insufficient_evidence: 10
- not_target_api: 3
- not_target_api_concentration: 6
- not_target_device: 5
- not_target_study_type: 1
### text
- insufficient_evidence: 11
- missing_endpoint: 1
- missing_endpoint_time: 2

## Figure Stage Counts
- digitized_curves: 29
- digitized_endpoints_failed: 0
- digitized_endpoints_ok: 29
- mapped_curves: 28
- triage_artifacts: 14
- triage_digitize_candidates: 13
- unmapped_curves: 1

## Figure Gate Counts
- routed_candidates: 18
- after_gate: 15
- skipped:missing_explicit_figure_signal: 3

## Figure Triage Routes
- digitize: 13
- skip: 1

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 1
- recommended_route:skip: 1
- ticks_readable:no: 1
- ticks_readable:uncertain: 1
- why_not_digitizable:the_axes_and_curves_cannot_be_accurately_interpreted_for_digitization: 1

## Figure Digitization Statuses
- ok: 29

## Figure Mapping Statuses
- unmapped: 1
- vision_mapped: 28

## LLM Reliability
### detection.router
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 223
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.figure.map_curves
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 10
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.figure.triage
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 14
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.table
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 33
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### extractors.text
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 21
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0
### triage.llm_triage
- api_failures: 0
- attempt_failures: 0
- auth_failures: 0
- final_failures: 0
- malformed_output_failures: 0
- other_failures: 0
- rate_limit_failures: 0
- requests: 749
- retried_requests: 0
- retries_attempted: 0
- retry_successes: 0
- schema_validation_failures: 0
- timeout_failures: 0
- transport_failures: 0

## LLM Adjudication Audit
- rows: 76
- recommended_status:rejected: 15
- recommended_status:unresolved: 58
- recommended_status:verified: 3
- disagreement:scope_bucket_disagreement: 30
- disagreement:status_disagreement: 2

## Prompt Assets
- extractors.figure.curve_map: 2026-03-28.v1
- extractors.figure.triage: 2026-03-28.v1
- extractors.table.structured_tables: 2026-03-28.v1
- extractors.text.structured_fields: 2026-03-28.v1
- routing.structured_first: 2026-03-28.v1
- triage.abstract_relevance: 2026-03-28.v1

## Blockage Summary
### Access Statuses
- downloaded: 219
- error: 1
- resolved: 92
- unresolved: 231
### Access Reasons
- resolve_error_connectionerror: 1
### Unresolved Route Reasons
- content_does_not_provide_evidence_related_to_ibuprofen_diffusion_cells_or_any_re: 1
- content_does_not_provide_extractable_evidence_about_the_study: 1
- content_does_not_provide_extractable_evidence_related_to_ibuprofen_or_diffusion_: 1
- content_from_the_document_is_limited_and_does_not_provide_explicit_evidence_for_: 1
- content_primarily_about_conjugated_drugs_and_cytotoxicity_no_mention_of_ibuprofe: 1
- content_provided_does_not_include_extractable_evidence: 1
- document_appears_incomplete_or_without_relevant_content: 1
- document_content_is_insufficient_for_detailed_extraction: 1
- document_content_is_insufficient_to_extract_detailed_evidence: 1
- document_content_provided_does_not_contain_extractable_evidence_related_to_ibupr: 1
- document_contents_suggest_potential_but_lack_clear_extractable_structured_eviden: 1
- document_does_not_appear_to_contain_relevant_information_related_to_ibuprofen_or: 1
- document_only_contains_front_matter_and_no_relevant_information: 1
- document_only_has_metadata_and_no_content_relevant_to_extraction: 1
- document_structure_primarily_consists_of_navigation_elements_and_does_not_provid: 1
- evidence_cannot_be_extracted_based_on_the_provided_text: 1
- evidence_extraction_from_this_document_is_limited_due_to_the_lack_of_accessible_: 1
- evidence_extraction_is_limited_due_to_insufficient_specific_information_regardin: 1
- evidence_extraction_not_clear_due_to_lack_of_accessible_content: 1
- extractable_evidence_is_likely_to_be_found_in_the_clinical_study_outcomes_or_fin: 1
- extractable_evidence_is_unclear_from_the_document: 1
- extraction_evidence_is_limited_due_to_the_provided_document_not_containing_subst: 1
- focus_on_sections_discussing_interactions_between_mil_88b_fe_and_ibuprofen_espec: 1
- further_details_are_needed_for_precise_extraction: 1
- further_extraction_information_not_available_in_the_text: 1
- initial_pages_do_not_contain_relevant_extraction_points: 1
- insufficient_detail_to_determine_extraction_routes: 1
- insufficient_evidence_available_in_the_document_to_determine_key_details: 1
- insufficient_information_available: 1
- insufficient_information_from_the_provided_document: 1
- insufficient_information_in_provided_text_to_determine_extraction_details: 1
- insufficient_information_in_the_provided_document: 1
- insufficient_information_to_extract_relevant_evidence_regarding_ibuprofen_dermal: 1
- insufficient_information_to_identify_specific_data_extraction_points: 1
- missing_structured_and_pdf_router_source: 244
- missing_structured_and_pdf_router_source_blocked_html_remote_captcha: 72
- missing_structured_and_pdf_router_source_html_remote_connectionerror: 1
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- need_more_details_for_specific_extraction: 1
- no_actionable_evidence_found_in_provided_text: 1
- no_clear_endpoints_or_formulations_found_in_the_provided_pages: 1
- no_detailed_data_available_in_the_provided_text: 1
- no_detailed_information_provided_about_formulations_or_endpoints: 1
- no_evidence_related_to_ibuprofen_or_dermal_formulation_present_in_the_extracted_: 1
- no_explicit_evidence_extraction_routes_available_in_the_supplied_text: 1
- no_extractable_content_was_found_in_the_provided_document_segments: 1
- no_extractable_evidence_appearing_in_the_provided_pages: 1
- no_extractable_evidence_found: 1
- no_extractable_evidence_found_in_provided_text: 1
- no_extractable_evidence_found_in_the_provided_content: 1
- no_extractable_evidence_found_in_the_provided_document: 2
- no_extractable_evidence_found_in_the_provided_pages: 1
- no_extractable_evidence_found_in_the_provided_text: 2
- no_extractable_evidence_found_on_this_page: 1
- no_extractable_evidence_located_in_the_provided_content: 1
- no_mention_of_ibuprofen_or_diffusion_testing: 1
- no_relevant_content_found_in_the_provided_document: 1
- no_relevant_content_regarding_ibuprofen_or_dermal_formulations_was_found: 1
- no_relevant_content_related_to_ibuprofen_or_diffusion_cells_detected: 1
- no_relevant_evidence_extracted_related_to_ibuprofen_dermal_formulations: 1
- no_relevant_evidence_found_related_to_ibuprofen_or_dermal_formulation: 1
- no_relevant_evidence_was_found_in_the_provided_document: 1
- no_relevant_extractable_evidence_available_in_the_provided_text: 1
- no_relevant_extractable_evidence_concerning_ibuprofen_or_diffusion_cells_found_i: 1
- no_relevant_extraction_data_found_in_provided_text: 1
- no_relevant_extraction_data_found_in_the_provided_text: 1
- no_relevant_extraction_data_present: 1
- no_relevant_extraction_evidence_found_in_the_provided_document: 1
- no_relevant_extraction_information_available: 1
- no_relevant_extraction_routes_identified_related_to_ibuprofen_or_diffusion_cells: 1
- no_relevant_information_about_ibuprofen_or_related_dermal_formulations_extracted: 1
- no_relevant_information_available_regarding_ibuprofen_or_related_dermal_formulat: 1
- no_relevant_information_extractable_regarding_ibuprofen_or_dermal_formulations: 1
- no_relevant_information_for_extraction_related_to_ibuprofen_or_relevant_dermal_f: 1
- no_relevant_information_found_in_the_provided_document_text: 1
- no_relevant_information_found_in_the_provided_pages: 1
- no_relevant_information_found_in_the_provided_text: 1
- no_relevant_information_found_regarding_ibuprofen_or_related_formulations: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_found: 1
- no_relevant_information_on_ibuprofen_or_dermal_formulations_identified: 1
- no_relevant_information_pertaining_to_ibuprofen_was_found_in_the_document: 1
- no_relevant_information_regarding_ibuprofen_or_diffusion_cells_in_the_provided_t: 1
- no_relevant_information_regarding_ibuprofen_or_specific_diffusion_methods: 1
- no_relevant_sections_identified_for_extraction: 1
- no_relevant_text_or_data_provided_for_extraction: 1
- no_specific_details_available_from_the_provided_text: 1
- no_specific_details_on_ibuprofen_or_diffusion_cells_in_the_provided_text: 1
- no_specific_details_regarding_ibuprofen_or_dermal_formulations_are_mentioned_in_: 1
- no_specific_extractable_evidence_provided_in_context: 1
- no_specific_extraction_route_determined_due_to_lack_of_relevant_information_in_t: 1
- no_structured_data_found_to_support_evidence_extraction: 1
- not_enough_information_available_to_extract_relevant_evidence: 1
- only_the_first_two_pages_were_accessible_further_document_details_needed: 1
- paper_discusses_the_development_of_a_biodegradable_hydrogel_for_drug_delivery_sp: 1
- paper_discusses_transporters_in_skin_related_to_drug_induced_skin_disorders_but_: 1
- study_involves_a_comparative_analysis_specifics_on_endpoints_and_formulations_no: 1
- the_content_does_not_provide_clear_evidence_regarding_diffusion_cell_or_endpoint: 1
- the_content_does_not_seem_relevant_for_ibuprofen_dermal_formulations: 1
- the_content_indicates_the_study_is_related_to_ibuprofen_in_biomaterials_for_woun: 1
- the_content_is_related_to_wound_healing_and_nanoparticles_but_does_not_mention_i: 1
- the_document_appears_to_be_primarily_a_review_focusing_on_compounds_from_gynura_: 1
- the_document_appears_to_be_primarily_about_dna_damage_and_does_not_specifically_: 1
- the_document_appears_to_contain_a_title_and_minimal_introductory_information_but: 1
- the_document_appears_to_focus_on_chiral_membranes_for_drug_separation_with_no_sp: 1
- the_document_appears_to_focus_on_drug_release_mechanisms_but_does_not_mention_ib: 1
- the_document_contains_metadata_regarding_the_publication_and_website_features_bu: 1
- the_document_contains_several_placeholder_pages_and_does_not_provide_accessible_: 1
- the_document_content_appears_to_be_an_interface_for_europe_pmc_and_does_not_cont: 1
- the_document_did_not_contain_usable_extraction_information: 1
- the_document_does_not_appear_to_cover_relevant_details_regarding_ibuprofen_or_di: 1
- the_document_does_not_clearly_mention_ibuprofen_or_diffusion_cells_and_specific_: 1
- the_document_does_not_contain_relevant_data_for_the_extraction_framework_focusin: 1
- the_document_does_not_contain_relevant_evidence_regarding_ibuprofen_or_dermal_fo: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_diffusion: 1
- the_document_does_not_contain_relevant_information_regarding_ibuprofen_or_diffus: 1
- the_document_does_not_provide_any_relevant_information_for_the_extraction_regard: 1
- the_document_does_not_provide_explicit_extractable_evidence_related_to_ibuprofen: 1
- the_document_does_not_provide_extractable_evidence: 1
- the_document_does_not_provide_relevant_information_about_ibuprofen_or_dermal_for: 1
- the_document_does_not_provide_specific_details_on_endpoints_or_formulations: 1
- the_document_does_not_provide_specific_details_regarding_the_extraction_of_evide: 1
- the_document_does_not_provide_sufficient_information_for_detailed_extraction_it_: 1
- the_document_does_not_seem_to_contain_relevant_evidence_for_ibuprofen_dermal_for: 1
- the_document_lacks_relevant_content_regarding_ibuprofen_or_other_extraction_endp: 1
- the_document_primarily_contains_information_about_the_ethos_service_rather_than_: 1
- the_document_primarily_discusses_a_pain_model_study_without_specific_reference_t: 1
- the_document_primarily_discusses_a_zn_based_mof_s_antimicrobial_anti_inflammator: 1
- the_document_primarily_discusses_ecotoxicological_impacts_and_does_not_focus_on_: 1
- the_document_provided_does_not_contain_extractable_evidence_related_to_ibuprofen: 1
- the_document_provides_insufficient_detail_to_extract_definitive_evidence_regardi: 1
- the_document_seems_to_focus_on_molecular_dynamics_without_clear_extractable_data: 1
- the_document_seems_to_not_contain_extractable_evidence_related_to_ibuprofen_or_d: 1
- the_document_text_does_not_provide_explicit_structured_information_for_extractio: 1
- the_document_text_provided_does_not_contain_relevant_information_for_extraction_: 1
- the_extraction_route_is_unclear_as_the_document_content_hints_at_relevance_to_ib: 1
- the_paper_discusses_decellularized_macroalgae_but_does_not_focus_on_ibuprofen_or: 1
- the_paper_focuses_on_naproxen_and_famotidine_not_ibuprofen: 1
- the_paper_focuses_on_validating_a_static_franz_diffusion_cell_system_without_exp: 1
- the_paper_s_content_regarding_ibuprofen_and_potential_relevance_to_dermal_formul: 1
- this_document_consists_of_only_the_frontend_and_introductory_content_without_sub: 1
- this_document_primarily_appears_to_discuss_antibacterial_properties_rather_than_: 1
- this_paper_does_not_appear_relevant_to_ibuprofen_or_dermal_formulations: 1
- this_paper_focuses_on_supercritical_co_assisted_spray_drying_for_inhalation_and_: 1
- unable_to_extract_further_information_due_to_incomplete_document_text: 1
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
- applied: 5
- skipped: 64
#### patch_area
- applied: 12
- skipped: 30
#### patch_endpoint_time
- applied: 24
- skipped: 3
#### patch_endpoint_value
- applied: 37
- skipped: 49

## Patch Success Counts
- patch_api_concentration: 5
- patch_area: 12
- patch_endpoint_time: 24
- patch_endpoint_value: 37