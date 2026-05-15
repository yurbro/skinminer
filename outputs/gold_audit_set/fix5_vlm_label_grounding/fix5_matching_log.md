# Fix5 Matching Log

## Matching Policy

Fix 5 introduced figure-local VLM series grounding and produced new structured artifacts in the validation run, including one new grounded `vlm_only` IJPharm row.

For the **gold overlay**, this round uses a **conservative no-remap policy**:

- rows outside the Fix 5 validation scope are inherited unchanged from the previous VLM overlay
- `CPB` (`10.1248/cpb.c21-00033`) and `EJPB` (`10.1016/j.ejpb.2020.05.013`) rows are inherited unchanged because Fix 5 changed observability/grounding, but did not create a clean one-to-one direct-gold replacement row
- `IJPharm` (`10.1016/j.ijpharm.2016.03.043`) produced new direct figure rows, but no conservative one-to-one remap was applied at scoring time because the current round-1 gold rows mix legacy CV rows, cross-modal rows, and duplicated 6 h / 48 h concepts; forcing a remap would risk overstating improvement

## Rows In Scope

| gold_record_id | mode | mapped_record_id | note |
|---|---|---|---|
| `record_1d882e0e9090` | conservative_keep | `` | IJPharm: new direct rows exist (`record_9c767c2806d6`, `record_f87d1fa55aa9`), but no one-to-one remap accepted for round-1 gold scoring. |
| `record_339f642dd0cd` | conservative_keep | `` | IJPharm: retained prior overlay to avoid speculative remap from legacy direct row to new grounded VLM-only row. |
| `record_437e38b169f5` | conservative_keep | `` | IJPharm: retained prior overlay; current validation run also contains non-VLM 6 h rows, but attribution to Fix 5 would be ambiguous. |
| `record_982332825448` | conservative_keep | `` | IJPharm: retained prior overlay; direct current rows are structurally improved but not remapped conservatively. |
| `record_a28c8f99f0f6` | conservative_keep | `` | IJPharm: exact record id survives in validation run, but semantic drift across earlier fixes makes direct gold remap non-conservative. |
| `record_ca0291b430fe` | conservative_keep | `` | IJPharm: retained prior overlay; no one-to-one remap accepted. |
| `record_e5a5cd848fa6` | conservative_keep | `` | IJPharm: retained prior overlay; 6 h direct/value path remains mixed with older cross-modal rows. |
| `record_3756495eb520` | conservative_keep | `` | CPB: Fix 5 improved VLM series diagnostics only; no clean gold-comparable final direct row. |
| `record_3d0adefd8d76` | conservative_keep | `` | CPB inherited unchanged. |
| `record_3f010c7e63c3` | conservative_keep | `` | CPB inherited unchanged. |
| `record_46eb58696d42` | conservative_keep | `` | CPB inherited unchanged. |
| `record_5f7a6dc5d170` | conservative_keep | `` | CPB inherited unchanged. |
| `record_66c595f609f5` | conservative_keep | `` | CPB inherited unchanged. |
| `record_7d4b4c3f9112` | conservative_keep | `` | CPB inherited unchanged. |
| `record_80dc0c1bef05` | conservative_keep | `` | CPB inherited unchanged. |
| `record_8263508e53c5` | conservative_keep | `` | CPB inherited unchanged. |
| `record_a15daa52e1ef` | conservative_keep | `` | CPB inherited unchanged. |
| `record_b808765948d6` | conservative_keep | `` | CPB inherited unchanged. |
| `record_d4f5bca2e39d` | conservative_keep | `` | CPB inherited unchanged. |
| `record_d646fe3f3b40` | conservative_keep | `` | CPB inherited unchanged. |
| `record_47710103a12d` | conservative_keep | `` | EJPB: validation run now exposes text-route unresolved rows, but Fix 5 did not solve the figure-recovery gap; retained prior overlay. |
| `record_cc84e1bf6e4e` | conservative_keep | `` | EJPB inherited unchanged. |
| `record_e04ec91b3e26` | conservative_keep | `` | EJPB inherited unchanged. |

## Structural Evidence Not Counted In Gold Overlay

The following validation-run rows are real Fix 5 outputs but were **not** force-mapped into round-1 gold scoring:

- `record_9c767c2806d6`
  - `doi=10.1016/j.ijpharm.2016.03.043`
  - `figure_extraction_method=vlm_only`
  - `vlm_grounding_status=figure_label_space`
  - `endpoint=15.0 ?g/cm? @ 48 h`
- `record_f87d1fa55aa9`
  - `doi=10.1016/j.ijpharm.2016.03.043`
  - direct CV figure row retained alongside the new VLM path
  - `endpoint=16.1832 ?g/cm? @ 48 h`

These rows matter for structural diagnosis, but this round's gold overlay does not count them as audited improvements without a cleaner row-identity contract.
