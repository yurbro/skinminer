# Reproducibility Analysis: 5 Runs (full_run_16 + 16a + 16b + 16c + 16d)

Code note: these reruns were executed on the current code tree after later provider/policy abstraction changes were already present. Under `--llm-provider openai --policy v1`, the user approved treating those later changes as no-op relative to the functional behavior targeted by `full_run_16_post_all_fixes`. Prompt asset versions and stage model selections recorded in manifests remain aligned across all five runs.

## 1. Aggregate Metrics

| Metric | Run 16 | Run 16a | Run 16b | Run 16c | Run 16d | Mean | SD | CV% |
|---|---|---|---|---|---|---|---|---|
| assembled | 239 | 248 | 238 | 277 | 279 | 256.20 | 20.29 | 7.92 |
| verified (v1) | 1 | 1 | 1 | 4 | 9 | 3.20 | 3.49 | 109.15 |
| unresolved (v1) | 179 | 199 | 178 | 201 | 171 | 185.60 | 13.52 | 7.28 |
| rejected (v1) | 59 | 48 | 59 | 72 | 99 | 67.40 | 19.60 | 29.09 |
| verified (v2) | 25 | 25 | 25 | 28 | 33 | 27.20 | 3.49 | 12.84 |
| table records | 252 | 243 | 247 | 275 | 279 | 259.20 | 16.62 | 6.41 |
| figure records | 10 | 16 | 14 | 13 | 14 | 13.40 | 2.19 | 16.35 |

## 2. Route-Level Stability

| Route | verified mean +/- SD | unresolved mean +/- SD |
|---|---|---|
| table | 0.20 +/- 0.45 | 69.00 +/- 12.92 |
| figure | 1.40 +/- 0.89 | 69.40 +/- 12.30 |
| text | 0.00 +/- 0.00 | 5.40 +/- 2.70 |
| mixed | 1.60 +/- 3.58 | 41.80 +/- 14.13 |

## 3. Record-Level Agreement

Pairwise comparison uses the set of `record_id` values with `verification_status=verified` in each run.

| Run pair | Both verified | A-only verified | B-only verified | Agreement rate |
|---|---|---|---|---|
| Run 16 vs Run 16a | 0 | 1 | 1 | 0.0000 |
| Run 16 vs Run 16b | 0 | 1 | 1 | 0.0000 |
| Run 16 vs Run 16c | 0 | 1 | 4 | 0.0000 |
| Run 16 vs Run 16d | 0 | 1 | 9 | 0.0000 |
| Run 16a vs Run 16b | 0 | 1 | 1 | 0.0000 |
| Run 16a vs Run 16c | 0 | 1 | 4 | 0.0000 |
| Run 16a vs Run 16d | 0 | 1 | 9 | 0.0000 |
| Run 16b vs Run 16c | 0 | 1 | 4 | 0.0000 |
| Run 16b vs Run 16d | 0 | 1 | 9 | 0.0000 |
| Run 16c vs Run 16d | 0 | 4 | 9 | 0.0000 |

V2 rescore pairwise agreement:

| Run pair | Both verified | A-only verified | B-only verified | Agreement rate |
|---|---|---|---|---|
| Run 16 vs Run 16a | 24 | 1 | 1 | 0.9231 |
| Run 16 vs Run 16b | 24 | 1 | 1 | 0.9231 |
| Run 16 vs Run 16c | 24 | 1 | 4 | 0.8276 |
| Run 16 vs Run 16d | 24 | 1 | 9 | 0.7059 |
| Run 16a vs Run 16b | 24 | 1 | 1 | 0.9231 |
| Run 16a vs Run 16c | 24 | 1 | 4 | 0.8276 |
| Run 16a vs Run 16d | 24 | 1 | 9 | 0.7059 |
| Run 16b vs Run 16c | 24 | 1 | 4 | 0.8276 |
| Run 16b vs Run 16d | 24 | 1 | 9 | 0.7059 |
| Run 16c vs Run 16d | 24 | 4 | 9 | 0.6486 |

## 4. V2 Rescore Stability

| Metric | Run 16 v2 | Run 16a v2 | Run 16b v2 | Run 16c v2 | Run 16d v2 | Mean | SD |
|---|---|---|---|---|---|---|---|
| verified | 25 | 25 | 25 | 28 | 33 | 27.20 | 3.49 |
| table verified | 24 | 24 | 24 | 25 | 24 | 24.20 | 0.45 |

Across all five runs, the intersection of v2-verified records is `24` records.
Common-core route distribution: table=24.
Common-core DOI distribution: 10.1208/s12249-013-9995-4 (24).

| Run | v2-only non-common verified record(s) |
|---|---|
| Run 16 | record_e3375489a6c9 | 10.1016/j.ejpb.2020.05.013 | figure | 5% w/w Ibuprofen gel | 250.0 µg/mL @ 720.0 min |
| Run 16a | record_85ba246d16a3 | 10.1016/j.ijpharm.2016.03.043 | figure | 5% w/w Ibuprofen in PEG 300 | 15.707099914550781 μg/cm² @ 48.0 h |
| Run 16b | record_3e03f1e9c7b9 | 10.1208/s12249-019-1584-8 | figure | Ibuprofen Loaded Hydrogel (Gel) | 200.0 µg/cm² @ 24.0 hours |
| Run 16c | record_4fcf67b3f8a8 | 10.1016/j.ejpb.2020.05.013 | figure | 5% w/w Ibuprofen gel | 150.7633514404297 µg/mL @ 720.0 min; record_81abc98954c3 | 10.1208/s12249-010-9522-9 | table | Ibuprofen 5% | 500.0 mg/cm2 @ 24.0 h; record_8ad9e33e54f0 | 10.1016/j.ijpharm.2016.03.043 | figure | IBULEVE™ Speed Relief 5% Spray | 34.0 μg/cm² @ 48.0 h; record_9c767c2806d6 | 10.1016/j.ijpharm.2016.03.043 | figure | IBUGEL™ (Ibuprofen 5% w/w) | 42.0 μg/cm² @ 48.0 h |
| Run 16d | record_1c25b3976688 | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in Isopropyl Alcohol Solution | 38.0 ug/cm2 @ 48.0 h; record_1c8653da686a | 10.1016/j.ijpharm.2016.03.043 | mixed | IBUGEL™ (Ibuprofen 5% w/w) | 38.0 ug/cm2 @ 6.0 h; record_4b76750618ca | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in Isopropyl Alcohol Solution | 38.0 ug/cm2 @ 6.0 h; record_5a9d0b11fd96 | 10.1016/j.ijpharm.2016.03.043 | mixed | IBUGEL™ (Ibuprofen 5% w/w) | 38.0 µg/cm2 @ 48.0 h; record_8ae64d3d7e7d | 10.1016/j.ijpharm.2016.03.043 | mixed | IBULEVE™ Speed Relief 5% Spray | 38.0 ug/cm2 @ 6.0 h; record_96227d3c56dd | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in PEG 300 Solution | 38.0 ug/cm2 @ 48.0 h; record_ba6bb4465891 | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in PEG 300 Solution | 38.0 ug/cm2 @ 6.0 h; record_d9d91800b070 | 10.1016/j.ijpharm.2016.03.043 | mixed | IBULEVE™ Speed Relief 5% Spray | 38.0 ug/cm2 @ 48.0 h; record_dd0ac19530e8 | 10.1016/j.ejpb.2020.05.013 | figure | Ibuprofen gel 5% w/w | 150.7633514404297 µg/mL @ 720.0 minutes |

## 5. Failure Taxonomy Stability

Failure reasons whose unresolved count changes by more than 20% across the five runs:

| failure_reason | Run 16 | Run 16a | Run 16b | Run 16c | Run 16d | max/min ratio delta |
|---|---|---|---|---|---|---|
| ambiguous_api_concentration | 38 | 39 | 32 | 39 | 40 | 0.25 |
| insufficient_evidence | 75 | 74 | 63 | 80 | 68 | 0.27 |
| missing_api_concentration | 21 | 19 | 13 | 0 | 8 | inf |
| missing_endpoint | 0 | 2 | 2 | 0 | 0 | inf |
| not_target_api_concentration | 0 | 0 | 12 | 15 | 12 | inf |
| source_context_inconsistent | 45 | 65 | 56 | 67 | 43 | 0.56 |

## 6. Key Target Paper Stability

For `10.1208/s12249-013-9995-4`:

| Run | table records | v2 verified |
|---|---|---|
| Run 16 | 24 | 24 |
| Run 16a | 30 | 24 |
| Run 16b | 24 | 24 |
| Run 16c | 24 | 24 |
| Run 16d | 24 | 24 |

For `10.1016/j.ejpb.2020.05.013`:

| Run | Fix 3b retry triggered? | retry candidate page | retry result | figure verified? | endpoint value |
|---|---|---|---|---|---|
| Run 16 | yes | 16 | recovered_digitizable | yes | 250.0 µg/mL @ 720.0 min |
| Run 16a | no |  |  | no |  |
| Run 16b | no |  |  | no |  |
| Run 16c | yes | 16 | recovered_digitizable | yes | 150.7633514404297 µg/mL @ 720.0 min |
| Run 16d | yes | 16 | recovered_digitizable | yes | 150.7633514404297 µg/mL @ 720.0 minutes |

Verified records per run under v1:

| Run | v1 verified records |
|---|---|
| Run 16 | record_e3375489a6c9 | 10.1016/j.ejpb.2020.05.013 | figure | 5% w/w Ibuprofen gel | 250.0 µg/mL @ 720.0 min |
| Run 16a | record_85ba246d16a3 | 10.1016/j.ijpharm.2016.03.043 | figure | 5% w/w Ibuprofen in PEG 300 | 15.707099914550781 μg/cm² @ 48.0 h |
| Run 16b | record_3e03f1e9c7b9 | 10.1208/s12249-019-1584-8 | figure | Ibuprofen Loaded Hydrogel (Gel) | 200.0 µg/cm² @ 24.0 hours |
| Run 16c | record_4fcf67b3f8a8 | 10.1016/j.ejpb.2020.05.013 | figure | 5% w/w Ibuprofen gel | 150.7633514404297 µg/mL @ 720.0 min; record_81abc98954c3 | 10.1208/s12249-010-9522-9 | table | Ibuprofen 5% | 500.0 mg/cm2 @ 24.0 h; record_8ad9e33e54f0 | 10.1016/j.ijpharm.2016.03.043 | figure | IBULEVE™ Speed Relief 5% Spray | 34.0 μg/cm² @ 48.0 h; record_9c767c2806d6 | 10.1016/j.ijpharm.2016.03.043 | figure | IBUGEL™ (Ibuprofen 5% w/w) | 42.0 μg/cm² @ 48.0 h |
| Run 16d | record_1c25b3976688 | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in Isopropyl Alcohol Solution | 38.0 ug/cm2 @ 48.0 h; record_1c8653da686a | 10.1016/j.ijpharm.2016.03.043 | mixed | IBUGEL™ (Ibuprofen 5% w/w) | 38.0 ug/cm2 @ 6.0 h; record_4b76750618ca | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in Isopropyl Alcohol Solution | 38.0 ug/cm2 @ 6.0 h; record_5a9d0b11fd96 | 10.1016/j.ijpharm.2016.03.043 | mixed | IBUGEL™ (Ibuprofen 5% w/w) | 38.0 µg/cm2 @ 48.0 h; record_8ae64d3d7e7d | 10.1016/j.ijpharm.2016.03.043 | mixed | IBULEVE™ Speed Relief 5% Spray | 38.0 ug/cm2 @ 6.0 h; record_96227d3c56dd | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in PEG 300 Solution | 38.0 ug/cm2 @ 48.0 h; record_ba6bb4465891 | 10.1016/j.ijpharm.2016.03.043 | mixed | Ibuprofen in PEG 300 Solution | 38.0 ug/cm2 @ 6.0 h; record_d9d91800b070 | 10.1016/j.ijpharm.2016.03.043 | mixed | IBULEVE™ Speed Relief 5% Spray | 38.0 ug/cm2 @ 48.0 h; record_dd0ac19530e8 | 10.1016/j.ejpb.2020.05.013 | figure | Ibuprofen gel 5% w/w | 150.7633514404297 µg/mL @ 720.0 minutes |

## 7. Conclusion

Aggregate-level stability is mixed. `verified (v1)` has mean `3.20` and SD `3.49`; pairwise v1 agreement ranges from `0.0000` to `0.0000`.
`Run 16d` is the new high-yield outlier with `9` v1-verified records, `279` assembled records, and `279` table records.

V2 rescoring remains more stable than v1 but shows wider spread after adding `Run 16d`. `verified (v2)` has mean `27.20` and SD `3.49`; pairwise v2 agreement ranges from `0.6486` to `0.9231`.
The stable common core across all five runs is `24` records, distributed as table=24.

The key table paper `10.1208/s12249-013-9995-4` remains outcome-stable under v2 if its verified count is unchanged across runs; the updated table above shows whether the raw table-row variance now propagates into v2 outcomes. The Fix 3b figure paper `10.1016/j.ejpb.2020.05.013` should be interpreted as unstable unless retry fires consistently and yields the same endpoint across runs.

Recommendation: for the paper, base the reproducibility claim on the full five-run statistics and on the common v2 core, not on any single v1 figure-derived endpoint. `Run 16d` materially widens the variance envelope, so the five-run summary is a stricter and more credible bound than the earlier four-run report.
