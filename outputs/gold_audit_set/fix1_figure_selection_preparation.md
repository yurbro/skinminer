# Fix 1 Preparation: Figure/Page Selection

## 1. Common pattern in the 7 `figure_misidentified` records

The 7 target records are:

- `record_47710103a12d`
- `record_cc84e1bf6e4e`
- `record_e04ec91b3e26`
- `record_437e38b169f5`
- `record_982332825448`
- `record_a28c8f99f0f6`
- `record_e5a5cd848fa6`

They share one primary pattern: triage identifies a plausible permeation figure trace, but digitization or downstream reuse does not stay bound to that same page/figure context.

### 1.1 Shared page-selection pattern

- In `10.1016/j.ejpb.2020.05.013`, triage emits `page_number=14`, `figure_id=10`, `subplot=a`, but also passes alternative pages `[9, 11, 14]`. The true target under human review is Figure 11(a) on p.16, while digitization actually locks onto p.14 calibration content.
- In `10.1016/j.ijpharm.2016.03.043`, triage emits `page_number=7`, `figure_id=1`, `subplot=A`, but also passes alternative pages `[7, 10, 11]`. Digitization then uses p.11 as `source_path` because `_iter_image_candidates()` feeds all candidates into a global “max edge count wins” search.
- The current implementation therefore does **not** preserve “triage chose page X / figure Y / subplot Z” as a hard binding. It treats triage output as a loose candidate set.

### 1.2 Current selection logic in `_iter_image_candidates`

`_iter_image_candidates()` simply returns:

1. `selected_image_path` as `triage_primary`
2. every path in `selected_image_paths`
3. no confidence tiering beyond this order

`digitize_figure_curves()` then evaluates every returned page/bbox combination and chooses the candidate with the largest `edge_points`. This means a denser non-target page can override the intended triage page even when triage itself was directionally correct.

### 1.3 Was triage identity correctly consumed downstream?

No. Triage identity is only weakly consumed. `page_number`, `figure_id`, and `subplot` are retained in the artifact, but the actual image used by digitization can drift to another page because candidate ranking is driven by edge density, not by page/figure consistency. That drift is visible in the IJPharm records: triage points to p.7 Fig.1(A), but digitization artifacts and overlays point to p.11.

## 2. Source tracing for the 6 cross-modal contamination records

The 6 contamination records are:

- `record_cc84e1bf6e4e`
- `record_e04ec91b3e26`
- `record_437e38b169f5`
- `record_a28c8f99f0f6`
- `record_e5a5cd848fa6`
- `record_c846ed69a806`

### 2.1 `record_cc84e1bf6e4e` and `record_e04ec91b3e26`

- Both are `extractor_name = table`
- Both end up with the exact same endpoint value as the direct misidentified figure record: `261.17059326171875 ug`
- Neither has patch history

Interpretation: these are not patched values; they are table-backed records whose endpoint was contaminated by cross-modal promotion / shared source binding on a figure-route paper. Evidence items do not clearly record the true injected source, so the source binding is not auditable enough.

### 2.2 `record_437e38b169f5`, `record_a28c8f99f0f6`, `record_e5a5cd848fa6`

- All three are `extractor_name = table`
- None has patch history
- Their evidence items include narrative snippets such as “At 6 h approximately 280 µg/cm²...” and “For the 1 µL application, the cumulative amounts permeated were 90–100 µg/cm²...”

Interpretation: these values were injected during extraction on a figure-route paper, not by patchers. The contamination mechanism is table/text extraction over route-selected pages on a paper whose endpoint evidence is primarily figure-based. In practice, page-level narrative summaries for one dose or experiment variant were lifted into unrelated formulation records.

### 2.3 `record_c846ed69a806`

- `extractor_name = table`
- `table_id = Table I`
- `row_source_pages = [6]`
- No patch history

Interpretation: this is not a digitization error. It is a table-origin record on a figure-route paper where formulation-table content was allowed to stand in for endpoint content. The route anchor references Figure 3, but the record-level endpoint binding comes from the wrong modality.

### 2.4 Were these injections properly recorded in `EvidenceItem`?

Not adequately. The contaminated records retain route-level figure anchors and generic snippets, but the actual value-bearing source is not always recorded as a tight record-level binding with traceable figure/page provenance. This is why the problem appears as a value error rather than a clear patch/promotion audit trail.

## 3. Fix proposal

**Fix proposal:** constrain `extractors/figure/digitize.py::_iter_image_candidates` and `extractors/figure/digitize.py::digitize_figure_curves` so that digitization honors the triage-selected page/figure first, and only falls back to alternative pages if the primary page fails explicit plot-context checks. Do not let a non-primary page win solely because it has more edges.

Concretely:

1. In `_iter_image_candidates()`, return candidates grouped by confidence tier:
   - tier 1: `triage_primary` on `triage.page_number`
   - tier 2: same-page alternatives only
   - tier 3: cross-page alternatives
2. In `digitize_figure_curves()`, search tier-by-tier rather than globally. Accept the first candidate in the highest available tier that passes basic plot-context checks.
3. Keep alternative pages as fallback only when the primary page has no usable crop / no usable mask / no axis range support.
4. Do **not** touch prompt text, mapping logic, or assembly logic in this first fix.

### Expected impacted record IDs

Primary target set:

- `record_47710103a12d`
- `record_cc84e1bf6e4e`
- `record_e04ec91b3e26`
- `record_437e38b169f5`
- `record_982332825448`
- `record_a28c8f99f0f6`
- `record_e5a5cd848fa6`

Expected direct repair is strongest for:

- `record_47710103a12d`
- `record_cc84e1bf6e4e`
- `record_e04ec91b3e26`
- `record_982332825448`

The remaining three are likely only partially affected, because they also involve table/text contamination and may require a later source-binding audit outside digitization.

### Expected end-to-end precision change

Conservative expectation: from `0/10` to about `4/10`.

Reason:

- `record_47710103a12d` should improve if p.14 calibration content is no longer allowed to override the intended permeation figure
- `record_cc84e1bf6e4e` and `record_e04ec91b3e26` are exact-value dependents of that same wrong source and may improve with it
- `record_982332825448` is the clearest direct IJPharm candidate likely to improve from page-binding alone

The mapping-error rows (`record_1d882e0e9090`, `record_339f642dd0cd`, `record_ca0291b430fe`) are not expected to improve in this fix, and the table-contaminated IJPharm records may persist until the later cross-modal source-binding audit.

### Possible side effects

- Some previously accepted digitizations may now fall back less aggressively and become `unresolved` if the triage primary page is weak
- Figure recall may dip slightly on papers where the true plot is genuinely only captured by an alternative page image
- This is acceptable for Fix 1 because the audit-set problem is false value precision, not figure recall

### Files and functions involved

- `extractors/figure/digitize.py::_iter_image_candidates`
- `extractors/figure/digitize.py::digitize_figure_curves`

No code changes are proposed yet for:

- `extractors/figure/map_curves.py::map_curves_to_formulations`
- `assembly/assemble_records.py`
- `patchers/patch_endpoint.py`

Those should be considered only after measuring the delta from this first, narrower fix.
