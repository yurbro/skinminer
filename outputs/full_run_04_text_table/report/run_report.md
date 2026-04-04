# Run Report: run_7732b12587cb

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Run profile: `text_table_baseline`
- Query profile: `ibuprofen_dermal_oa_v1`
- Query profile version: `2026-03-28.v1`
- Query source: `profile:ibuprofen_dermal_oa_v1`
- Assembled records: `24`
- Final records evaluated: `24`
- Actually verified: `7`
- Final unresolved: `9`
- Final rejected: `8`

## Route Distribution
- figure: 8
- table: 5
- text: 2
- unresolved: 515

## Extractor Outputs
- figure: 0
- table: 21
- text: 5

## Verification Outcomes
- rejected: 8
- unresolved: 9
- verified: 7

## Failure Taxonomy
- insufficient_evidence: 5
- missing_api_concentration: 5
- missing_area: 5
- missing_endpoint: 2
- not_target_api: 1
- not_target_device: 7
- not_target_study_type: 2
- percent_only: 1

## Failure Taxonomy By Route
### figure
- missing_area: 5
- missing_endpoint: 2
- not_target_api: 1
- not_target_device: 3
- not_target_study_type: 2
- percent_only: 1
### table
- not_target_device: 4
### text
- insufficient_evidence: 5
- missing_api_concentration: 5

## Figure Stage Counts
- digitized_curves: 0
- digitized_endpoints_failed: 0
- digitized_endpoints_ok: 0
- mapped_curves: 0
- triage_artifacts: 0
- triage_digitize_candidates: 0
- unmapped_curves: 0

## Figure Triage Routes

## Figure Triage Signals

## Figure Digitization Statuses

## Figure Mapping Statuses

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
- downloaded: 44
- error: 183
- resolved: 80
- unresolved: 223
### Access Reasons
- resolve_error_connectionerror: 183
### Unresolved Route Reasons
- access_issues_content_not_viewable: 1
- access_issues_encountered_no_relevant_content_obtained: 1
- access_to_basic_content_is_restricted_unable_to_extract_specific_details: 1
- access_to_content_is_not_provided_due_to_javascript_issues: 1
- access_to_content_is_restricted_due_to_javascript_requirements: 1
- access_to_the_article_is_required_to_extract_specific_information: 1
- access_to_the_content_is_blocked_due_to_javascript_requirement: 1
- access_to_the_content_is_limited_page_requires_javascript: 1
- access_to_the_content_is_restricted_due_to_javascript_requirement: 1
- access_to_the_document_is_not_possible_due_to_javascript_restrictions: 1
- access_to_the_document_is_restricted_due_to_javascript_requirements: 1
- access_to_the_full_article_is_required_to_extract_detailed_information: 1
- accessing_the_document_is_not_possible_due_to_javascript_restriction: 1
- article_content_not_accessible_due_to_javascript_restrictions: 1
- cannot_extract_relevant_evidence_due_to_page_access_restrictions: 1
- content_cannot_be_accessed_due_to_javascript_restrictions: 1
- content_inaccessible_due_to_inability_to_access_the_webpage: 1
- content_inaccessible_unable_to_extract_any_relevant_data: 1
- content_not_accessible_cannot_determine_relevant_extraction_routes: 1
- content_not_accessible_due_to_javascript_requirement: 1
- content_not_accessible_evidence_extraction_not_possible: 1
- content_not_extractable_unable_to_access_relevant_information: 1
- content_unavailable_requires_javascript: 1
- document_blocks_contain_no_relevant_extractable_evidence_due_to_javascript_limit: 1
- document_inaccessible_due_to_javascript_requirement: 1
- document_is_inaccessible_due_to_javascript_requirement: 1
- document_is_not_fully_accessible_due_to_javascript_requirements: 1
- document_not_accessible_due_to_javascript_restrictions: 1
- evidence_extraction_not_possible_due_to_inaccessible_content: 1
- extractable_evidence_appears_to_be_limited_due_to_javascript_requirement: 1
- full_content_is_not_accessible_only_html_for_a_non_functional_page_is_available: 1
- information_needed_from_the_article_is_not_accessible_due_to_javascript_restrict: 1
- insufficient_content_available_for_detailed_extraction: 1
- insufficient_content_available_for_evidence_extraction: 1
- limited_extractable_evidence_in_provided_text: 1
- missing_structured_and_pdf_router_source: 417
- missing_structured_and_pdf_router_source_html_remote_httperror: 3
- no_accessible_content_available_javascript_is_required_to_view_the_document: 1
- no_content_available_for_extraction: 2
- no_content_extracted_due_to_access_restrictions: 1
- no_detailed_evidence_can_be_extracted_as_the_document_content_is_not_accessible: 1
- no_evidence_extractable_due_to_functional_limitations_of_the_source: 1
- no_extractable_evidence_available_due_to_inaccessible_content: 1
- no_extractable_evidence_available_due_to_javascript_restrictions_on_the_page: 1
- no_extractable_evidence_available_due_to_lack_of_content: 1
- no_extractable_evidence_available_from_the_provided_document: 1
- no_extractable_evidence_available_the_document_does_not_provide_any_content_as_i: 1
- no_extractable_evidence_detected_due_to_lack_of_content: 1
- no_extractable_evidence_due_to_lack_of_content: 1
- no_extractable_evidence_found_due_to_content_being_blocked_by_javascript: 1
- no_extractable_evidence_found_due_to_inaccessible_content: 1
- no_extractable_evidence_found_due_to_lack_of_accessible_content: 1
- no_extractable_evidence_is_present_due_to_webpage_loading_issues: 1
- no_extractable_information_from_the_document_as_it_requires_javascript_to_displa: 1
- no_relevant_content_or_evidence_found: 1
- no_relevant_extraction_possible_due_to_lack_of_content: 1
- no_specific_evidence_related_to_ibuprofen_or_diffusion_cell_provided_in_the_visi: 1
- no_specific_extractable_evidence_found_in_the_provided_document: 1
- no_specific_mention_of_ibuprofen_or_relevant_diffusion_cells: 1
- source_access_issue_unable_to_extract_detailed_information: 1
- the_content_is_inaccessible_as_the_page_requires_javascript_to_view: 1
- the_content_is_not_accessible_due_to_javascript_restrictions: 1
- the_document_appears_to_be_inaccessible_unable_to_extract_substantial_evidence: 1
- the_document_cannot_be_accessed_due_to_javascript_issues: 1
- the_document_cannot_be_accessed_due_to_javascript_restrictions: 1
- the_document_content_could_not_be_accessed_due_to_javascript_requirements: 1
- the_document_content_is_inaccessible_due_to_javascript_requirement: 1
- the_document_does_not_provide_any_extractable_evidence: 1
- the_document_does_not_provide_extractable_evidence_due_to_technical_issues_with_: 1
- the_document_is_inaccessible_and_contains_no_extractable_evidence: 1
- the_document_is_inaccessible_due_to_javascript_requirements: 5
- the_document_is_inaccessible_due_to_javascript_requirements_limiting_the_ability: 1
- the_document_is_inaccessible_no_relevant_evidence_can_be_extracted: 1
- the_document_is_not_accessible_content_cannot_be_reviewed: 1
- the_document_is_not_accessible_due_to_javascript_requirements: 2
- the_document_is_not_accessible_due_to_javascript_requirements_cannot_extract_spe: 1
- the_document_is_not_accessible_without_javascript: 1
- the_document_was_not_accessible_due_to_technical_issues: 1
- the_source_document_only_contains_messages_regarding_javascript_functionality_an: 1
- the_source_does_not_contain_relevant_content_related_to_ibuprofen_or_diffusion_c: 1
- the_source_does_not_provide_usable_content_due_to_browser_restrictions: 1
- the_source_page_does_not_contain_relevant_content_due_to_javascript_issues: 1
- unable_to_access_content_due_to_javascript_requirement: 1
- unable_to_access_content_page_requires_javascript: 1
- unable_to_extract_content_due_to_javascript_issues: 1
- unable_to_extract_content_due_to_lack_of_accessible_text: 1
- unable_to_extract_evidence_due_to_the_content_being_javascript_dependent: 1
- unable_to_extract_evidence_from_the_html_due_to_javascript_issues: 1
- unable_to_extract_relevant_content_webpage_requires_javascript: 1
- unable_to_extract_relevant_information_due_to_document_being_inaccessible: 1
- unable_to_extract_relevant_information_due_to_inaccessible_content: 1
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
- skipped: 5
#### patch_area
- skipped: 12
#### patch_endpoint_time
- applied: 5
#### patch_endpoint_value
- applied: 3
- skipped: 2

## Patch Success Counts
- patch_endpoint_time: 5
- patch_endpoint_value: 3