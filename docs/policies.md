# Acceptance policies

SkinMiner evaluates extracted records against four cumulative acceptance levels. The `policy_level` field stores the first level that accepts a record. A manuscript result at level v3 includes records first accepted at v1, v2, or v3.

## Policy ladder

| Code policy | Manuscript label | Added acceptance rule |
|---|---|---|
| `v1_strict_ibuprofen_5pct` | Strict | Ibuprofen at 5% w/w or 50 mg/g, Franz device, IVPT/IVRT/both, cumulative-amount endpoint, and a recorded endpoint time |
| `v2_accept_wv` | Extended | Adds 5% w/v or 50 mg/mL while retaining the Strict device, study, endpoint, and time gates |
| `v3_any_ibuprofen_concentration` | Any-concentration | Accepts any ibuprofen concentration while retaining the device, study, endpoint, and time gates |
| `v4_accept_flux` | Flux-augmented | Adds flux, Jss, and permeability-coefficient endpoints, including unit-driven endpoint correction |

## Strict

Strict requires all of the following:

- The active ingredient normalizes to ibuprofen.
- The device string contains `franz`.
- The study type is IVPT, IVRT, or both.
- A cumulative-amount endpoint has a numeric mean.
- The endpoint time is present.
- The concentration is exactly 5% w/w or 50 mg/g.

Oral, intravenous, subcutaneous, intraperitoneal, and other dose expressions are outside this concentration scope. Ambiguous concentration bases remain unresolved or rejected according to the verification path.

## Extended

Extended inherits Strict and additionally recognizes 5% w/v and 50 mg/mL as eligible ibuprofen concentrations. It does not relax the Franz, study-type, cumulative-amount, or endpoint-time requirements.

The manuscript Extended result uses `{v1, v2}`. It is not an equality filter on `policy_level == v2`.

## Any-concentration

Any-concentration inherits the structural scope gates and accepts any concentration when the active ingredient is ibuprofen. A missing active-ingredient name remains missing, and a different active ingredient remains out of scope.

The manuscript result uses `{v1, v2, v3}`.

## Flux-augmented

Flux-augmented inherits Any-concentration and accepts flux or permeability endpoints. It maintains a closed family of recognized flux units and can correct an endpoint kind when a unit unambiguously indicates flux. It can also recognize permeability coefficients from units such as length per time when the evidence context explicitly identifies permeability.

The manuscript result uses `{v1, v2, v3, v4}`.

## Cumulative scoring

For requested level `vk`, the evaluation adapter includes all records whose first accepted level is in the prefix through `vk`.

```text
v1 → {v1}
v2 → {v1, v2}
v3 → {v1, v2, v3}
v4 → {v1, v2, v3, v4}
```

The released loader reports:

- `first_level_filter`, the concrete membership predicate
- `cumulative_levels`, the included level list
- verified, unresolved, and rejected counts
- scope true positives and false positives
- scope precision
- scope and value true positives
- end-to-end precision

## Reference values

| Provider | Level | Verified | Scope TP | Scope FP | Scope precision |
|---|---|---:|---:|---:|---:|
| GPT | Strict | 1 | 1 | 0 | 100% |
| GPT | Extended | 25 | 25 | 0 | 100% |
| GPT | Any-concentration | 47 | 25 | 22 | 53.1915% |
| GPT | Flux-augmented | 51 | 25 | 26 | 49.0196% |
| Claude | Strict | 0 | 0 | 0 | N.A. |
| Claude | Extended | 24 | 24 | 0 | 100% |
| Claude | Any-concentration | 38 | 24 | 14 | 63.1579% |
| Claude | Flux-augmented | 47 | 28 | 19 | 59.5745% |

The Claude Strict precision is undefined because the denominator is zero. The published figure leaves that precision point empty.

## Recompute a policy level

```bash
python -m evaluation.score_run \
  --gold-format round2 \
  --provider gpt \
  --policy-level v2 \
  --gold-csv evaluation/gold/gold_set_round2_annotation.csv
```

See [paper_mapping.md](paper_mapping.md) for the Claude command and figure inputs.

