# Literature Permeation Data Summary

## Source

- GPT baseline: `full_run_16_post_all_fixes` from `v2`, `v3`, `v4` rescore verified records
- Claude baseline: `experiment_E3_claude_v2` from `v2`, `v3`, `v4` rescore verified records

## Filtering

- `verification_status = verified`
- `api_name` contains `ibuprofen`
- `endpoint.kind in {amount_total, amount_per_area, amount}`
- `endpoint.value > 0` and `endpoint.time > 0`
- `device` contains `Franz` or `diffusion cell`
- `literature_permeation_data_gpr.csv` additionally canonical-deduplicates repeated GPT/Claude/policy observations

- Verified rows before task filtering: `232`
- Rows after task filtering: `217`
- Canonical literature observations after GPT/Claude/policy dedupe: `60`
- GPR rows written: `60` (`api_concentration_pct` parseable in `26` rows)

## Statistics

| Metric | Value |
|---|---|
| Total records after filtering | 217 provenance rows; 60 canonical rows |
| Unique DOI | 9 |
| Unique formulations | 40 |
| API concentration range | 0.383 to 5.0 % among parseable rows; many other rows use non-percent concentration descriptions |
| Endpoint time range | 0.5 to 72.0 h |
| Cumulative amount range (ug/cm2) | 0.720 to 302840.000 |
| Membrane types | `porcine skin` (25), `silicone membrane` (11), `Porcine skin` (6), `stratum corneum` (5), `skin` (5), `bovine split skin` (4), `(missing)` (1), `Caco-2` (1) |
| DOI distribution | `10.1208/s12249-013-9995-4` (24), `10.1248/cpb.c21-00033` (11), `10.1186/2050-6511-13-5` (6), `10.1208/s12249-019-1481-1` (6), `10.1007/s11095-008-9785-y` (5), `10.1523/jneurosci.5741-07.2008` (5), `10.1016/j.ejpb.2020.05.013` (1), `10.1039/d0ra00100g` (1), `10.1248/bpb.b19-00221` (1) |

## Comparison With Paper 1 Self-Generated Data

| Dimension | Paper 1 Data | Literature Data | Overlap |
|---|---|---|---|
| API | 5% w/w ibuprofen | ibuprofen only; parseable `%` rows are dominated by 5.0% plus one 0.383% w/v row | partial |
| Membrane | Strat-M | mostly porcine skin / dermatomed porcine skin; no stable verified Strat-M block | low |
| Device | Franz cell | all selected rows are Franz diffusion cell records | high |
| Excipients | Poloxamer 407 / Ethanol / PG | mostly TPGS/HPMC nanosuspension systems, ionic-liquid systems, and other non-matching vehicles | low |
| Endpoint time | 28 h | 0.5 to 72 h; no exact 28 h anchor in the current verified set | low |
| Response range (ug/cm2) | ~150-350 | 0.720 to 302840.000 | partial |

## Heterogeneity Assessment

The literature set is heterogeneous in exactly the dimensions that matter for direct formulation-space transfer. Membrane type is mostly porcine rather than Strat-M, endpoint times are much longer than the Paper 1 28 h target, and the excipient systems are usually unrelated to the Poloxamer 407 / ethanol / PG design space.

The duplication analysis also shows that the apparent volume of evidence is inflated by policy and provider overlap. After removing repeated GPT/Claude/policy views of the same observation, only the canonical rows remain. The data are therefore useful as a noisy response prior, but not as a clean matched covariate dataset.

## Usability Judgment

This literature set is usable for a demonstration-grade GPR augmentation experiment only under a weak-prior interpretation. It is not strong enough for direct supervised transfer in the original Paper 1 excipient space.

Recommended use:

- Use response-only augmentation as the default (`scheme A`) with high literature noise weighting.
- Start with `alpha_factor` around `10` to `20` because domain mismatch is large.
- Treat any improvement as proof-of-concept evidence that literature responses can regularize early sparse-data GPR, not as evidence of exact formulation transfer.

If a stronger augmentation claim is needed later, the next step is not to reuse unresolved rows under the current task constraints; it is to expand the verified pool with more matched Franz / 5% ibuprofen / membrane-compatible literature.
