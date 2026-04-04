# Run Report: run_b3f7e753ce61

- Model: `gpt-4o-mini`
- Policy: `v1_strict_ibuprofen_5pct`
- Query profile: ``
- Query profile version: ``
- Query source: ``
- Assembled records: `42`
- Final records evaluated: `42`
- Actually verified: `13`
- Final unresolved: `14`
- Final rejected: `15`

## Route Distribution
- figure: 6
- mixed: 3
- table: 5
- text: 4
- unresolved: 513

## Extractor Outputs
- figure: 0
- table: 22
- text: 21

## Verification Outcomes
- rejected: 15
- unresolved: 14
- verified: 13

## Failure Taxonomy
- insufficient_evidence: 2
- missing_api_concentration: 10
- missing_area: 3
- missing_endpoint: 5
- not_target_api: 2
- not_target_device: 14
- not_target_study_type: 2
- percent_only: 4

## Failure Taxonomy By Route
### figure
- missing_area: 3
- missing_endpoint: 2
- not_target_device: 2
- percent_only: 4
### mixed
- missing_api_concentration: 5
- missing_endpoint: 3
- not_target_api: 2
- not_target_device: 4
### table
- missing_api_concentration: 1
- not_target_device: 6
- not_target_study_type: 2
### text
- insufficient_evidence: 2
- missing_api_concentration: 4
- not_target_device: 2

## Figure Stage Counts
- digitized_curves: 0
- digitized_endpoints_failed: 5
- digitized_endpoints_ok: 0
- mapped_curves: 0
- triage_artifacts: 8
- triage_digitize_candidates: 6
- unmapped_curves: 0

## Figure Triage Routes
- digitize: 6
- skip: 2

## Figure Triage Signals
- digitizable:no: 2
- endpoint_curve_present:no: 2
- recommended_route:skip: 2
- ticks_readable:uncertain: 1
- why_not_digitizable:figures_do_not_display_endpoint_curves_relevant_to_ibuprofen: 1
- why_not_digitizable:n_a: 1
- why_not_digitizable:no_endpoint_curves_identified_for_digitization_related_to_ibuprofen: 1

## Figure Digitization Statuses
- fail_few_edges: 4
- fail_missing_plot_context: 1

## Figure Mapping Statuses

## LLM Reliability
- none

## Prompt Assets
- none

## Blockage Summary
### Access Statuses
- downloaded: 40
- error: 185
- resolved: 84
- unresolved: 222
### Access Reasons
- resolve_error_connectionerror: 185
### Unresolved Route Reasons
- access_issues_no_extractable_evidence_available: 1
- access_to_content_is_blocked_unable_to_extract_details: 1
- access_to_content_is_restricted_no_extractable_evidence_available: 1
- access_to_content_not_available_due_to_website_restrictions: 1
- access_to_document_requires_javascript_which_is_currently_unsupported_unable_to_: 1
- access_to_full_document_requires_javascript_support_so_content_not_fully_extract: 1
- access_to_the_document_is_currently_restricted_due_to_javascript_issues: 1
- access_to_the_document_is_restricted_due_to_javascript_requirements: 1
- access_to_the_document_is_restricted_evidence_extraction_not_possible: 1
- access_to_the_document_requires_javascript_content_not_available_for_extraction: 1
- access_to_the_full_text_is_necessary_to_provide_relevant_extraction_details: 1
- cannot_access_content_due_to_javascript_requirements: 1
- content_inaccessible_no_relevant_information_available: 1
- content_is_inaccessible_due_to_javascript_requirement: 1
- content_is_not_accessible_due_to_javascript_requirement: 2
- content_is_not_accessible_due_to_javascript_restrictions: 1
- content_not_accessible_due_to_javascript_issue: 1
- content_not_accessible_due_to_javascript_requirement: 1
- content_not_accessible_due_to_website_restrictions: 2
- content_not_available_for_extraction: 1
- content_unavailable_due_to_javascript_requirement: 1
- document_content_is_inaccessible_due_to_javascript_requirements: 1
- document_content_not_accessible_requires_javascript_support: 1
- document_is_inaccessible_requires_javascript: 1
- document_not_accessible_due_to_javascript_requirement: 1
- html_page_requires_javascript_and_cannot_be_accessed: 1
- insufficient_evidence_extractable_from_the_provided_text: 1
- insufficient_information_available_in_the_document: 1
- javascript_required_to_view_content: 1
- missing_structured_and_pdf_router_source: 418
- missing_structured_and_pdf_router_source_html_remote_httperror: 2
- no_accessible_content_available_for_extraction: 1
- no_accessible_content_due_to_javascript_requirements: 1
- no_accessible_content_javascript_required_to_view: 1
- no_detailed_evidence_available_due_to_website_access_issues: 1
- no_extractable_evidence_available_document_content_cannot_be_accessed: 1
- no_extractable_evidence_available_due_to_inability_to_access_document_content: 1
- no_extractable_evidence_available_due_to_inaccessible_document_content: 1
- no_extractable_evidence_available_due_to_page_content_restrictions: 1
- no_extractable_evidence_available_due_to_restricted_access_on_europe_pmc: 1
- no_extractable_evidence_available_due_to_website_access_limitations: 1
- no_extractable_evidence_due_to_lack_of_accessible_content: 1
- no_extractable_evidence_found_due_to_inaccessible_content: 4
- no_extractable_evidence_found_due_to_webpage_restrictions: 1
- no_extractable_evidence_found_due_to_website_access_issues: 1
- no_extractable_evidence_found_in_the_provided_document: 1
- no_extractable_evidence_from_the_provided_document: 1
- no_extractable_information_available_due_to_webpage_access_issues: 1
- no_relevant_content_available_from_the_document: 1
- no_relevant_extractable_evidence_found_in_the_provided_text: 1
- no_relevant_extraction_data_available_from_provided_document: 1
- the_content_could_not_be_accessed_due_to_the_requirement_of_javascript: 1
- the_document_cannot_be_accessed_contains_only_messages_about_javascript_support: 1
- the_document_contains_no_useful_content_due_to_javascript_restrictions: 1
- the_document_content_is_inaccessible_due_to_javascript_requirements: 2
- the_document_content_is_inaccessible_it_may_require_javascript_to_view_properly: 1
- the_document_content_is_not_accessible_unable_to_extract_relevant_information: 1
- the_document_could_not_be_accessed_due_to_a_javascript_requirement: 1
- the_document_did_not_load_no_extractable_evidence_could_be_found: 1
- the_document_does_not_provide_any_accessible_content_due_to_javascript_restricti: 1
- the_document_does_not_provide_extractable_content_regarding_ibuprofen_or_diffusi: 1
- the_document_does_not_provide_extractable_evidence: 1
- the_document_is_inaccessible_as_it_requires_javascript: 1
- the_document_is_inaccessible_due_to_javascript_issues: 1
- the_document_is_inaccessible_due_to_javascript_requirements: 3
- the_document_is_inaccessible_due_to_javascript_requirements_thus_no_relevant_inf: 1
- the_document_is_inaccessible_due_to_javascript_restrictions: 1
- the_document_is_inaccessible_no_extractable_evidence_can_be_determined: 1
- the_document_is_inaccessible_no_extractable_information_available: 1
- the_document_is_not_accessible_due_to_issues_with_javascript: 1
- the_document_is_not_accessible_without_javascript: 1
- the_document_requires_javascript_no_extractable_data_available: 1
- the_extraction_route_cannot_be_determined_due_to_lack_of_accessible_content: 1
- the_source_content_does_not_provide_any_usable_information_for_extraction: 1
- the_source_document_could_not_be_accessed_due_to_javascript_restrictions: 1
- the_source_link_is_inaccessible_limiting_the_extraction_of_evidence: 1
- the_webpage_content_is_not_accessible_requires_javascript: 1
- unable_to_access_content_due_to_javascript_requirement: 1
- unable_to_extract_content_due_to_javascript_requirement_on_the_source_page: 1
- unable_to_extract_evidence_due_to_access_limitations: 1
- unable_to_extract_evidence_due_to_javascript_requirement_for_the_webpage: 1
- unable_to_extract_evidence_due_to_website_restrictions_and_lack_of_accessible_co: 1
- unable_to_extract_information_from_the_paper_due_to_javascript_requirement: 1
- unable_to_extract_meaningful_information_due_to_html_content_limitations: 1
- unable_to_extract_relevant_content_due_to_blockage_from_javascript_support: 1
- unable_to_extract_relevant_evidence_due_to_javascript_restrictions_on_the_webpag: 1
- unable_to_extract_specific_information_due_to_document_access_restrictions: 1
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
- applied: 6
- skipped: 10
#### patch_area
- skipped: 16
#### patch_endpoint_time
- applied: 7
#### patch_endpoint_value
- applied: 1
- skipped: 5

## Patch Success Counts
- patch_api_concentration: 6
- patch_endpoint_time: 7
- patch_endpoint_value: 1