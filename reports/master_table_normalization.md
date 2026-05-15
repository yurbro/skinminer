# Master Table Normalization

Date: 2026-05-10

## Inputs

- Source: `outputs/phase07_audit/master_table_v15.csv` (47 rows)
- Mapping: frozen Phase 1 Step 1 `(doi, source_table)` table

## Sanity Checks

```
Total records: 47

Per-paper:
  Part I (10.1159/000183922): expected 13 / actual 13
  Part II (10.1159/000231528): expected 20 / actual 20
  Part III (10.1159/000315139): expected 14 / actual 14

occlusion_inferred distribution:
  occluded:     expected 42 / actual 42
  pretreated:   expected 3  / actual 3
  non_occluded: expected 2  / actual 2

barrier_normalized distribution:
  silicone:        expected 33 / actual 33
  human_epidermis: expected 14 / actual 14
  unknown:         expected 0  / actual 0

Membership flag counts:
  include_in_F2_train: expected 17 / actual 17
  include_in_F2_test:  expected 11 / actual 11
  include_in_F3_silicone: expected 28 / actual 28
  include_in_F3_skin:     expected 14 / actual 14

F3 pair coverage:
  silicone records:      28
  skin records:          14
  unique pair_ids in silicone: 28
  unique pair_ids in skin:     14
  pair_ids common to both:     12
  silicone-only pair_ids:      16
  skin-only pair_ids:          2

Unmapped records (no source_table match): 0
Unpaired skin records:                    2
```

## Observations

- All 47 rows mapped to the frozen `(doi, source_table)` rules.
- F3 pair coverage is 12/14, not 14/14. The unpaired skin rows are written to `outputs/phase07_audit/unpaired_skin_records.csv`.
- The mismatch is not repaired here because pair matching is based strictly on numeric vehicle composition and the frozen criteria.

## Unpaired Skin Records

| record_id | doi | source_table | vehicle_raw_string | vehicle_signature | pair_id | reason |
| --- | --- | --- | --- | --- | --- | --- |
| record_d56177853e9b | 10.1159/000231528 | Table 5 | 25:75 PG:water | 0:25:75:0:0 | 231528_0:25:75:0:0 | no matching F3 silicone record with same doi and vehicle composition |
| record_0917c25edbf8 | 10.1159/000231528 | Table 5 | 50:50 PG:water | 0:50:50:0:0 | 231528_0:50:50:0:0 | no matching F3 silicone record with same doi and vehicle composition |

## Output Files

- `outputs/phase07_audit/master_table_v15_normalized.csv`
- `outputs/phase07_audit/unmapped_records.csv`
- `outputs/phase07_audit/unpaired_skin_records.csv`
- `reports/master_table_normalization.md`

Overall status: **FAIL**

Determinism check (run twice, hash compare): **PASS**

## Step 1.1 patch

```
[STEP 1.1 PATCH] Done.

Backup: _v1_backup_phase1_step1_1_20260510_181428/master_table_v15_normalized.csv

include_in_F3_paired:
  True count: 24/24  [PASS]
  paired silicone (F3_silicone & F3_paired): 12/12
  paired skin     (F3_skin & F3_paired):     12/12

is_pure_ethanol_system:
  True count: 2/2  [PASS]
  Where: Part I Table 3 (silicone 100:0)? yes
         Part I Table 5 (skin 100:0)?     yes

Excluded skin records (F3_skin & ~F3_paired):
  expected: 25:75 + 50:50 PG:water (Part II Table 5)
  actual:
  - 10.1159/000231528 Table 5 25:75 PG:water
  - 10.1159/000231528 Table 5 50:50 PG:water

Determinism check (run twice, hash compare): PASS
```

Notes:

- `include_in_F3_paired` is true only for pair IDs present on both F3 silicone and F3 skin ends.
- `is_pure_ethanol_system` is applied to F3-standard silicone/skin records to match the Step 1.1 expected count; the Part I Table 4 pretreated 100:0 row remains false.

Status: **PASS**
