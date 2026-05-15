# Verification Ceiling: Recommendations

## 1. What is the main cause of the ceiling?

The ceiling is primarily a strict-field grounding ceiling, not a general verifier-overreach problem. E2 improves extraction volume and patch success, but the rows still fail on three strict requirements that must be both present and explicitly supported: (1) a strict `5% w/w` concentration basis, (2) a normalized amount endpoint, and (3) route-consistent evidence support. In the reviewed rows, verification is usually exposing those unresolved grounding gaps rather than falsely blocking otherwise-complete strict records.

## 2. Which failure-reason gates should be reviewed first?

### Gate 1: `missing_api_concentration`
- E2 unresolved rows blocked by this gate: 9
- Rows judged clearly over-conservative: 0
- High-value recoverable pocket: 8 table rows from `10.1208/s12249-013-9995-4`, each as the only remaining failure code
- Estimated new verified if the gate itself is relaxed: 0 defensible
- Estimated new verified if upstream concentration recovery is fixed instead: up to 8 rows, but this needs paper-level confirmation
- Precision risk if relaxed: high, because `5% w/w` is scope-defining rather than optional metadata

### Gate 2: `insufficient_evidence`
- E2 unresolved rows blocked by this gate: 24
- Rows judged clearly over-conservative: 0; borderline/uncertain: 1 (`record_b357c03adc16`)
- Estimated new verified if relaxed globally: at most 1 to 2, and even that is uncertain
- Precision risk if relaxed: very high, because this code currently absorbs several real problems: endpoint-kind ambiguity, weak device grounding, and mixed-route single-modality support
- Recommendation: do not relax it globally. Split it into narrower diagnostics before changing behavior.

### Gate 3: `unit_normalization_failed`
- E2 unresolved rows blocked by this gate: 9
- Rows judged clearly over-conservative: 0
- Estimated new verified if the gate itself is relaxed: 0 defensible
- Estimated new verified if unit extraction / normalization is fixed upstream: small but non-zero; likely concentrated in the `10.1039/d0ra00100g` table rows
- Precision risk if relaxed: medium-high, because several reviewed rows still have unresolved concentration or evidence-support issues even after the unit problem is fixed

`ambiguous_api_concentration` is a large bucket (23 unresolved rows), but the reviewed samples look like correct strict blocks rather than obvious false rejections: 8 mM ion-pairs, mg/cm2 dose rows, and mg dm-3 adsorption rows are not clean 5% w/w records. It should be reviewed diagnostically, but it is not a good relaxation target.

## 3. How should the adjudication layer change?

Keep adjudication audit-only for now. If adjudication were allowed to override the pipeline today, 8 rows would flip from `unresolved` to `verified`. After manual review, 0/8 look like clearly correct overrides. In every case the adjudication rationale waived a strict missing field: non-5%-w/w concentration, missing numeric endpoint value, or unresolved unit normalization.

If adjudication is revisited later, it first needs a consistency check: a row should not be allowed to end with `recommended_status=verified` when its own sub-findings say `concentration_5pct_ww_ok=no` or when the rationale explicitly says the exact endpoint value is absent.

## 4. Recommended next step

Do not relax verification rules yet, and do not give adjudication override power yet. The next step should be a targeted fix package on the three concrete grounding bottlenecks revealed by this diagnosis:

1. Improve non-figure concentration propagation/recovery, especially table-to-record carry-over for papers like `10.1208/s12249-013-9995-4`.
2. Fix endpoint unit parsing and normalization for mixed/table rows like the `10.1039/d0ra00100g` cluster.
3. Split `insufficient_evidence` into narrower observable causes so that endpoint-kind ambiguity, weak device support, and mixed-route support deficits are not all hidden behind one umbrella code.

After those targeted fixes, rerun only the affected E2 paper subset first. If the non-figure verified count still stays at zero after those fixes, then the next move should be gold-set expansion before any policy relaxation. But current evidence does not justify weakening the strict verifier itself.