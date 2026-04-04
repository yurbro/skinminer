# Manual Review Priority Checklist: `full_run_07_full`

## Why Review Now

Manual review is necessary for this run.

Reasons:

- `Actually verified = 32`, which is the best result so far, but some verified records still look suspicious.
- Several verified records appear to carry non-target endpoint types such as `flux`, `jss`, `Papp`, or other non-amount outputs.
- Some verified records also carry API expressions such as `mg/ml`, `mg/kg`, `mg/L`, or plain `5%`, which may not satisfy the intended strict `5% w/w` scope.
- The current verification output is therefore good enough for targeted human checking, but not yet safe to trust without review.

Primary review sources:

- [verified_records.jsonl](c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/outputs/full_run_07_full/verified_records.jsonl)
- [verified_records.csv](c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/outputs/full_run_07_full/verified_records.csv)
- [run_report.md](c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/outputs/full_run_07_full/report/run_report.md)
- [figure_failure_summary.csv](c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/outputs/full_run_07_full/report/figure_failure_summary.csv)
- [blockage_summary.csv](c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/outputs/full_run_07_full/report/blockage_summary.csv)

## Review Questions

For each reviewed record, check these in order:

1. Is the study actually about `ibuprofen` as the target API?
2. Is the concentration truly `5% w/w` rather than `5%`, `mg/ml`, `mg/kg`, `mg/L`, or another basis?
3. Is the device explicitly a `Franz diffusion cell`, not only a generic `diffusion cell`?
4. Is the study really `IVPT` / `IVRT`, rather than a clinical, enzymatic, environmental, permeability, or unrelated assay?
5. Is the endpoint an `amount` endpoint, rather than `flux`, `Jss`, `Papp`, `% release`, `risk ratio`, or another non-target metric?
6. If the endpoint is total amount, is the diffusion area explicit enough to normalize or validate it?

## Priority 1: Suspicious Verified Records

Review all `32` verified records.

Start with these `24` suspicious verified records from `8` papers. These are the highest-risk false positives.

### 1.1 Highest-Priority Papers

- `paper_13eefc545725` | DOI `10.1016/j.jhazmat.2021.125554`
  Reason: 5 verified text records with `mg/L`-style API expressions and `flux/Jss`-like endpoints. Very likely out of strict dermal-formulation scope.

- `paper_c6791af323cf` | DOI `10.1523/jneurosci.5741-07.2008`
  Reason: 5 verified mixed records with `40 mg/kg` API expression. Very likely non-target biology/neuroscience context.

- `paper_85f231cdccef` | DOI `10.1208/s12249-019-1584-8`
  Reason: 4 verified figure/mixed records with plain `5%` and `Jss`-type endpoints. Likely useful paper, but strict-scope compliance needs confirmation.

- `paper_b257621dff97` | DOI `10.1007/s11095-008-9785-y`
  Reason: 3 verified mixed records with `~10 mg/ml` API expression and low-to-moderate support rate.

- `paper_bfb4f8a16de3` | DOI `10.4103/jomfp.jomfp_253_19`
  Reason: 3 verified mixed records with plain `5%` and non-target endpoint styles.

- `paper_eabb128fb839` | DOI `10.1186/2050-6511-13-5`
  Reason: 2 verified table records include `flux` / `Papp`. These should be checked carefully against the strict amount-endpoint policy.

- `paper_567266ad0643` | DOI `10.1248/cpb.c21-00033`
  Reason: verified figure record uses molar-fraction style formulation description and `flux` endpoint.

- `paper_6e6aaf875560` | DOI `10.1248/bpb.b19-00221`
  Reason: verified table record label is `Caco-2 Permeability Assay`; likely outside intended dermal IVPT/IVRT scope.

### 1.2 Immediate Spot-Check Targets

These should be checked first before trusting the verified set:

- `record_38856e1ffe65` | DOI `10.1186/2050-6511-13-5`
  Reason: verified with endpoint kinds `flux` and `unknown` / `Papp`.

- `record_9e37bfbbdb75` | DOI `10.1248/bpb.b19-00221`
  Reason: verified despite `Caco-2 Permeability Assay` label.

- `record_4b26f53f8d92` | DOI `10.1248/cpb.c21-00033`
  Reason: verified figure record with `flux` endpoint and molar-fraction API description.

- `record_0c86a8a8bb55` and related records under DOI `10.1523/jneurosci.5741-07.2008`
  Reason: likely false positives despite high support rate.

## Priority 2: Recoverable Unresolved Records

These are the best candidates for salvage in the next refinement round or manual rescue.

Current bucket:

- `29` unresolved records
- `10` papers
- mostly missing `area`, `endpoint`, or unit normalization

### 2.1 Most Recoverable Papers

- `paper_48cbfe0b170b` | DOI `10.1208/s12249-013-9995-4` | `8` table records
  Dominant issue: `missing_area`
  Why review: this is a concentrated, table-driven paper where one manual area confirmation could recover many records.

- `paper_d3e3b20e276b` | DOI `10.3389/fphar.2024.1355283` | `6` figure records
  Dominant issue: `missing_area`
  Why review: high support, Franz-confirmed, likely recoverable if area is stated elsewhere in the paper.

- `paper_85f231cdccef` | DOI `10.1208/s12249-019-1584-8` | `3` mixed records
  Dominant issue: `missing_endpoint`
  Why review: likely a real target paper; unresolved records may be recoverable from tables/figures.

- `paper_4cd65bde6fb4` | DOI `10.1021/acs.molpharmaceut.0c00720` | `2` figure records
  Dominant issue: `missing_area`
  Why review: high-confidence figure route, endpoint present, only area missing.

- `paper_567266ad0643` | DOI `10.1248/cpb.c21-00033` | `2` figure records
  Dominant issue: `unit_normalization_failed`
  Why review: endpoint appears real; normalization rule may be the only blocker.

- `paper_b451e1b601ac` | DOI `10.1016/j.ejpb.2020.05.013` | `2` figure records
  Dominant issue: likely recoverable figure-side normalization / area issue.

- `paper_cceb8131dfed` | DOI `10.1016/j.ijpharm.2019.118975` | `2` mixed records
  Dominant issue: likely endpoint/area recovery.

### 2.2 First Recoverable Records to Inspect

- `record_32f3510accd1` | DOI `10.1039/d0ra00100g`
  Failure: `missing_area`

- `record_bed30cc4c744` | DOI `10.1021/acs.molpharmaceut.0c00720`
  Failure: `missing_area`

- `record_e0f692cb7519` | DOI `10.3389/fphar.2024.1355283`
  Failure: `missing_area`

- `record_cb97635fc722` and `record_a17e21ef4279` | DOI `10.1248/cpb.c21-00033`
  Failure: `unit_normalization_failed`

- `record_c3fdc7aafe21`, `record_c846ed69a806`, `record_423fd58bcb1f` | DOI `10.1208/s12249-019-1584-8`
  Failure: `missing_endpoint`

## Priority 3: Borderline Rejected Records

These are useful for calibration. Some are probably true negatives, but some may reveal over-strict or misdirected normalization.

Current bucket:

- `18` rejected records
- `10` papers

### 3.1 Best Borderline Papers to Audit

- `paper_75f801f960c1` | DOI `10.21203/rs.3.rs-3773667/v1`
  Reason: table records rejected only for `not_target_device`; may be a real diffusion setup with weak device phrasing.

- `paper_112cba50495d` | DOI `10.1038/s41598-024-57883-5`
  Reason: mixed records have good support but are still `uncertain` + `diffusion cell`; useful for device/study-type calibration.

- `paper_4431fa44bca9` | DOI `10.1186/s13065-022-00901-2`
  Reason: table record rejected for `not_target_device`; should be checked once to see whether the device rule is too strict.

### 3.2 Likely True Negatives But Worth One Look

- `paper_6d7ce6948405` | DOI `10.1002/14651858.cd001177.pub2`
  Reason: ibuprofen foam dressing / clinical context. Likely correct rejection, but useful as a sanity-check example.

- `paper_7fb33aad5434` | DOI `10.1172/jci2614`
  Reason: likely non-target physiology figure route. Good negative-control example.

- `paper_4d9539f88d46` | DOI `10.1016/j.clinthera.2010.03.002`
  Reason: multiple text rejections with `not_target_device + missing_area`; likely out of scope.

## Recommended Human Review Order

1. Review all suspicious verified records first.
2. Review all figure-route verified records next, even if they do not look suspicious.
3. Review recoverable unresolved papers with concentrated missing-area failures.
4. Review a small calibration sample from borderline rejected records.

## Suggested Review Batch Sizes

- Batch A: `32` verified records
- Batch B: `29` recoverable unresolved records
- Batch C: `10-15` borderline rejected records

If time is limited, start with:

1. `paper_13eefc545725`
2. `paper_c6791af323cf`
3. `paper_85f231cdccef`
4. `paper_48cbfe0b170b`
5. `paper_d3e3b20e276b`
