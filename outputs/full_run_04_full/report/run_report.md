# Run Report: run_d2b27259519f

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `balanced_full`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Assembled records: `42`
- Final records evaluated: `42`
- Actually verified: `0`
- Final unresolved: `28`
- Final rejected: `14`

## Route Distribution
- figure: 8
- mixed: 3
- table: 6
- text: 3
- unresolved: 508

## Extractor Outputs
- figure: 2
- table: 25
- text: 16

## Verification Outcomes
- rejected: 14
- unresolved: 28

## Failure Taxonomy
- figure_digitization_failed: 25
- insufficient_evidence: 14
- missing_api_concentration: 15
- missing_area: 4
- missing_endpoint: 4
- not_target_api: 1
- not_target_device: 13
- not_target_study_type: 1
- percent_only: 2

## Failure Taxonomy By Route
### figure
- figure_digitization_failed: 16
- missing_area: 3
- missing_endpoint: 3
- not_target_device: 5
- percent_only: 1
### mixed
- figure_digitization_failed: 9
- insufficient_evidence: 4
- missing_api_concentration: 5
- missing_endpoint: 1
- not_target_device: 3
- percent_only: 1
### table
- missing_area: 1
- not_target_api: 1
- not_target_device: 3
- not_target_study_type: 1
### text
- insufficient_evidence: 10
- missing_api_concentration: 10
- not_target_device: 2

## Figure Stage Counts
- digitized_curves: 2
- digitized_endpoints_failed: 7
- digitized_endpoints_ok: 2
- mapped_curves: 2
- triage_artifacts: 11
- triage_digitize_candidates: 10
- unmapped_curves: 0

## Figure Triage Routes
- digitize: 10
- skip: 1

## Figure Triage Signals
- digitizable:no: 1
- endpoint_curve_present:no: 1
- recommended_route:skip: 1
- ticks_readable:no: 1
- why_not_digitizable:no_relevant_figures_available_on_page: 1

## Figure Digitization Statuses
- fail_few_edges: 7
- ok: 2

## Figure Mapping Statuses
- vision_mapped: 2

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
- downloaded: 40
- error: 191
- resolved: 78
- unresolved: 219
### Access Reasons
- resolve_error_connectionerror: 191
### Unresolved Route Reasons
- access_issues_content_not_retrievable_due_to_website_restrictions: 1
- access_to_content_is_blocked_javascript_is_required: 1
- access_to_content_is_restricted_due_to_javascript_issues_preventing_evidence_ext: 1
- access_to_document_not_available_due_to_javascript_requirement: 1
- access_to_the_article_content_requires_javascript_preventing_extraction_of_speci: 1
- access_to_the_article_is_restricted_due_to_javascript_requirements_details_regar: 1
- access_to_the_content_is_restricted_due_to_javascript_requirements_limiting_the_: 1
- access_to_the_content_is_restricted_unable_to_extract_relevant_information: 1
- access_to_the_document_is_restricted_due_to_javascript_requirements: 4
- access_to_the_paper_is_limited_due_to_javascript_requirements: 1
- accessing_content_not_possible_due_to_javascript_requirement: 1
- accessing_the_content_requires_javascript_and_currently_there_is_no_extractable_: 1
- accessing_the_document_requires_javascript_which_is_not_supported_in_the_current: 1
- accessing_the_full_content_requires_javascript_support: 1
- cannot_extract_specific_evidence_due_to_page_loading_issues: 1
- cannot_extract_specific_information_due_to_limited_text_access: 1
- content_inaccessible_due_to_javascript_requirement: 3
- content_is_behind_javascript_specific_extraction_cannot_be_performed: 1
- content_is_inaccessible_due_to_javascript_requirement: 1
- content_is_not_accessible_due_to_javascript_requirement: 1
- content_is_not_accessible_due_to_javascript_restrictions: 1
- content_not_accessible_due_to_javascript_requirement: 1
- content_not_accessible_due_to_javascript_restrictions: 1
- content_not_accessible_only_webpage_loading_issues_present: 1
- content_not_extractable_due_to_javascript_requirement: 1
- content_unavailable_due_to_javascript_requirement: 1
- document_lacks_accessible_information_due_to_requiring_javascript: 1
- document_not_accessible_due_to_javascript_requirement: 1
- insufficient_information_for_extraction_content_is_inaccessible_due_to_javascrip: 1
- missing_structured_and_pdf_router_source: 420
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- no_accessible_content_from_the_article_to_extract_evidence: 1
- no_evidence_extracted_due_to_lack_of_content_accessible_from_the_provided_source: 1
- no_extractable_content_available_due_to_browser_issues: 1
- no_extractable_content_available_due_to_javascript_issues: 1
- no_extractable_content_could_be_determined_due_to_restricted_access: 1
- no_extractable_content_found_in_the_document: 1
- no_extractable_evidence_due_to_content_being_inaccessible: 1
- no_extractable_evidence_due_to_javascript_requirement: 1
- no_extractable_evidence_due_to_javascript_requirement_for_document_access: 1
- no_extractable_evidence_found_due_to_inaccessible_content: 2
- no_extractable_evidence_found_due_to_webpage_access_issues: 1
- no_extractable_evidence_found_the_content_is_not_accessible: 1
- no_extractable_evidence_is_available_from_the_document: 1
- the_content_cannot_be_accessed_as_the_page_requires_javascript: 1
- the_content_was_inaccessible_due_to_javascript_restrictions_on_the_webpage: 1
- the_document_cannot_be_accessed_properly_due_to_javascript_issues: 1
- the_document_could_not_be_accessed_due_to_javascript_requirements: 1
- the_document_could_not_be_accessed_to_extract_specific_information: 1
- the_document_did_not_provide_accessible_content_due_to_javascript_requirement: 1
- the_document_did_not_provide_any_extractable_information_due_to_restrictions_on_: 1
- the_document_does_not_provide_any_accessible_content_for_extraction: 1
- the_document_does_not_provide_content_for_extraction: 1
- the_document_does_not_provide_extractable_evidence_due_to_lack_of_content: 1
- the_document_does_not_provide_relevant_evidence_regarding_ibuprofen_or_diffusion: 1
- the_document_is_currently_inaccessible_due_to_javascript_requirements: 1
- the_document_is_inaccessible_due_to_javascript_requirements: 4
- the_document_is_inaccessible_due_to_javascript_requirements_no_extractable_evide: 1
- the_document_is_inaccessible_due_to_javascript_requirements_therefore_no_evidenc: 1
- the_document_is_not_accessible_and_contains_no_extractable_evidence: 1
- the_document_is_not_accessible_due_to_javascript_issues: 1
- the_document_is_not_accessible_due_to_javascript_requirements_and_therefore_no_e: 1
- the_document_is_not_accessible_due_to_javascript_requirements_and_thus_evidence_: 1
- the_document_is_not_accessible_due_to_restrictions: 1
- the_provided_text_does_not_contain_relevant_information_regarding_the_study_and_: 1
- the_source_document_requires_javascript_to_display_content_preventing_access_to_: 1
- the_source_is_currently_inaccessible_as_it_is_a_remote_html_page_that_requires_j: 1
- the_study_involves_synthetic_membranes_and_franz_cells_but_specific_data_on_ibup: 1
- unable_to_access_content_due_to_javascript_requirements: 1
- unable_to_access_content_for_further_extraction: 1
- unable_to_access_content_javascript_requirement_not_met: 1
- unable_to_extract_any_relevant_information_due_to_javascript_issues: 1
- unable_to_extract_detailed_information_due_to_site_restrictions: 1
- unable_to_extract_evidence_due_to_lack_of_accessible_content: 1
- unable_to_extract_evidence_due_to_loading_issues_with_the_document: 1
- unable_to_extract_evidence_from_the_document_due_to_javascript_requirement: 1
- unable_to_extract_relevant_evidence_due_to_inaccessible_document_content: 1
- unable_to_extract_relevant_information_due_to_lack_of_accessible_content: 1
- unable_to_extract_relevant_information_due_to_webpage_limitations: 1
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
- skipped: 15
#### patch_area
- skipped: 16
#### patch_endpoint_time
- applied: 10
#### patch_endpoint_value
- applied: 2
- skipped: 4

## Patch Success Counts
- patch_endpoint_time: 10
- patch_endpoint_value: 2