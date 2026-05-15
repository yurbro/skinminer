# Fix 2 Figure Identity Diagnosis

Date: 2026-04-06

## Scope

This note diagnoses the 7 target records that remained value-wrong after Fix 1 even though their surviving figure source was `candidate_tier = triage_primary` or their paper-level route anchor still pointed to the triage-primary figure. The goal is to answer, for each record:

1. Which page/figure triage selected.
2. What is actually on that page/figure.
3. Where the paper's true target permeation figure lives.

This note does not change code. It is preparation for Fix 2 only.

---

## Per-record diagnosis

| Record | Triage selected page/figure | What is actually on that page/figure | True target permeation figure page | Diagnosis |
|---|---|---|---|---|
| `record_47710103a12d` | PDF p14, Figure 10(a) | Not a permeation plot. It is a calibration curve: `Absorbance (mAu)` vs `Concentration (µg/mL)` with UV images below. | PDF p16, Figure 11(a) | Direct triage semantic error. The wrong figure was selected at triage time, not later in fallback ordering. |
| `record_cc84e1bf6e4e` | Inherited from the same EJPB paper-level triage anchor: PDF p14, Figure 10(a) | Same calibration figure as above. | PDF p16, Figure 11(a) | Cross-modal contamination from the misidentified direct figure source. Not an independent table value. |
| `record_e04ec91b3e26` | Inherited from the same EJPB paper-level triage anchor: PDF p14, Figure 10(a) | Same calibration figure as above. | PDF p16, Figure 11(a) | Same as `record_cc84e1bf6e4e`: cross-modal contamination from the wrong direct figure source. |
| `record_982332825448` | PDF p7, Figure 1(A) | This is a real permeation figure page. However, the digitize crop covers the full multi-panel Figure 1 (`A-D`), not subplot `A` only. | PDF p7, Figure 1(A) | Triage page identity is correct, but subplot identity is not preserved. This is a triage-to-digitize binding problem, not a triage-VLM page-selection problem. |
| `record_437e38b169f5` | No record-level figure trace. The paper-level figure route anchor still points to PDF p7, Figure 1(A). | PDF p7 is a real multi-panel permeation figure page (`Figure 1`, panels `A-D`). The record value is not actually bound to any one subplot. | The paper's relevant permeation figures are PDF p7 (`Figure 1`) and PDF p10 (`Figure 3`). This record has no trustworthy single-figure binding. | Cross-modal contamination. This row is table/text-backed and should not be treated as a clean triage-primary figure miss. |
| `record_a28c8f99f0f6` | No record-level figure trace. The paper-level figure route anchor still points to PDF p7, Figure 1(A). | Same as above: a real multi-panel permeation figure page, but the record is not trace-bound to a single subplot. | Same paper-level answer: relevant permeation figures are on PDF p7 and PDF p10. The current record has no reliable single-figure identity. | Cross-modal contamination, not direct triage page error. |
| `record_e5a5cd848fa6` | No record-level figure trace. The paper-level figure route anchor still points to PDF p7, Figure 1(A). | Same as above: real permeation figure page, but no preserved subplot binding for this table-backed row. | Same paper-level answer: relevant permeation figures are on PDF p7 and PDF p10. The current record has no reliable single-figure identity. | Cross-modal contamination, not direct triage page error. |

---

## Record-by-record detail

### EJPB: `10.1016/j.ejpb.2020.05.013`

#### `record_47710103a12d`

- Triage selected: `figure_trace_paper_b451e1b601ac_10_14_a_70082c9c7d8a`
- Selected image: `...10.1016_j.ejpb.2020.05.013__p14.jpg`
- Selected figure identity: `Figure 10(a)` on PDF page 14
- Actual content on selected page:
  - x-axis: `Concentration (µg/mL)`
  - y-axis: `Absorbance (mAu)`
  - caption: calibration curve with UV images
  - this is not a permeation endpoint figure
- True target figure:
  - PDF page 16
  - `Figure 11(a)`
  - amount permeated vs time, with UV images in panel `b`
- Conclusion:
  - this is a triage semantic false positive
  - the failure is upstream of digitization fallback

#### `record_cc84e1bf6e4e` and `record_e04ec91b3e26`

- These are table-backed rows, but both inherited endpoint value `261.17` from the same wrong figure trace as `record_47710103a12d`.
- There is no independent correct figure binding for either row.
- Conclusion:
  - they are downstream contamination rows caused by the EJPB calibration-figure misidentification

### IJPharm: `10.1016/j.ijpharm.2016.03.043`

#### `record_982332825448`

- Triage selected:
  - `figure_trace_paper_7008480bdcae_ibuprofen_permeation_7_A_48f0a81345dd`
  - PDF page 7
  - `Figure 1(A)`
- Actual content on selected page:
  - this page is a genuine permeation figure page
  - `Figure 1` has four panels: `A` human skin, `B` porcine skin, `C` silicone membrane, `D` skin PAMPA
  - the bbox/crop used by digitization spans the whole `Figure 1` block, not subplot `A` alone
- True target figure for this row:
  - still PDF page 7, `Figure 1(A)`
- Conclusion:
  - page identity is correct
  - subplot identity is lost between triage and digitization

#### `record_437e38b169f5`, `record_a28c8f99f0f6`, `record_e5a5cd848fa6`

- These rows do not carry a record-level figure trace after Fix 1.
- Their paper-level route anchor still comes from the same IJPharm figure route that selected PDF page 7.
- Actual content on the anchored page:
  - a real permeation figure page (`Figure 1`, panels `A-D`)
- However:
  - the rows themselves are table/text-backed
  - the numeric values are not trace-bound to one curve or one subplot
  - because of that, they cannot be diagnosed as direct triage-primary figure errors in the same way as `record_982332825448`
- Conclusion:
  - these are source-binding / cross-modal contamination rows
  - they should not drive the first direct figure-selection fix

---

## Synthesis

The 7 "still wrong" rows actually split into three distinct groups:

1. **Direct triage semantic error**
   - `record_47710103a12d`
   - plus two downstream contaminated rows:
     - `record_cc84e1bf6e4e`
     - `record_e04ec91b3e26`
   - Root problem: triage chose a calibration figure and labeled it as a permeation plot.

2. **Correct page, wrong subplot binding**
   - `record_982332825448`
   - Root problem: triage selected the right page and intended subplot `A`, but digitization consumed a crop covering all four subplots.

3. **Cross-modal contamination**
   - `record_437e38b169f5`
   - `record_a28c8f99f0f6`
   - `record_e5a5cd848fa6`
   - Root problem: the record is no longer figure-trace-bound, so the value cannot be attributed to one selected subplot at all.

This means the remaining problem is not one thing. It is:

- first, an EJPB-style **triage semantic misclassification**
- second, an IJPharm-style **subplot identity handoff failure**
- and only after that, a separate **cross-modal contamination** issue

---

## Fix 2 proposal

### Proposed scope

Fix only the first direct root cause class in this round:

- **tighten triage-to-digitization figure identity for direct figure rows**

and explicitly do **not** attempt to repair cross-modal contamination yet.

### Proposed code scope

Primary targets:

- `extractors/figure/triage.py`
- `extractors/figure/models.py`
- `extractors/figure/digitize.py`

### Proposed behavior

1. **Add figure semantic type to triage output**
   - Emit a low-cardinality field such as:
     - `permeation_curve`
     - `calibration_curve`
     - `uv_image_panel`
     - `schematic_or_device`
     - `other`
   - This should be derived from the same existing VLM read, not by adding a second independent model call unless necessary.

2. **Hard gate digitization for obviously non-permeation figures**
   - If x/y semantics look like calibration (`Concentration` on x, `Absorbance` on y), do not let the figure proceed as a permeation digitization candidate.
   - This directly targets the EJPB error.

3. **Carry a subplot-aware crop contract from triage into digitization**
   - When triage says subplot `A`, digitization should first crop to the inferred `A` region, not the full multi-panel page.
   - Same-page fallback can still exist, but only after the subplot-specific candidate fails.
   - This directly targets the IJPharm direct-figure error.

### Why this is the right next fix

- It addresses the two direct figure-source failures revealed by the 7-row diagnosis:
  - wrong figure semantics at triage
  - lost subplot identity at digitization
- It stays narrower than a full cross-modal cleanup.
- It preserves the staged unfreeze strategy:
  - fix direct figure source binding first
  - fix shared-hint / table contamination later

### What Fix 2 should not do

- Do not yet change `assembly`, `patch_endpoint`, or table support promotion.
- Do not yet broaden verification or relax scope gates.
- Do not yet try to solve the 3 cross-modal contamination rows in the same patch.

### Expected effect

Conservative expectation:

- EJPB direct figure misselection should be blocked or redirected away from the calibration page.
- IJPharm direct figure extraction should become subplot-aware.
- The 3 contamination rows may remain unresolved, and that is acceptable for this round.

---

## Recommendation

Proceed with Fix 2 only if you agree with this narrower scope:

- **fix direct figure semantic identity and subplot handoff**
- **defer cross-modal contamination to a later fix**
