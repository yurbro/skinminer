# Supplementary Tables Generation

## Table S1: Extraction audit

- Input file path: `outputs/phase07_audit/master_table_v15_normalized.csv` + `outputs/phase07_audit/per_record_audit.json`
- Output file path: `outputs/supplementary/table_S1_extraction_audit.csv`
- Row count: 47
- Sanity checks: composition parsed 47/47; J within 2% 47/47; SD within 5% 46/47; unmapped 0
- SHA-256: `6569bc6862c07b00f415e5d87b25b857fbdb7e4a724e87a329dfd0cf7e1240b6`

## Table S2: Section 3.5.1 modelling dataset

- Input file path: `outputs/phase1_step2_redo/dataset.csv` + `outputs/phase1_step2_F2/solubility_table.csv`
- Output file path: `outputs/supplementary/table_S2_section_3_5_1_dataset.csv`
- Row count: 17
- Sanity checks: train=5, test=12; all log10_solubility non-null=true; unmapped vehicles=0
- SHA-256: `f50448b0a113b3f1447017b1a4f02db6c15806b4e9304008d65eeeb4c49be825`

## Table S3: Silicone-skin pairs

- Input file path: `outputs/phase1_step3/silicone_skin_paired_dataset.csv` + `outputs/phase07_audit/master_table_v15_normalized.csv`
- Output file path: `outputs/supplementary/table_S3_silicone_skin_pairs.csv`
- Row count: 12
- Sanity checks: Part I=5, Part II=4, Part III=3; pure ethanol pairs=1; include_in_V3=11; incomplete pairs=0
- SHA-256: `c576eeff5e32569008536de02b61c9feccae90c1c10bf5fb6d39f80d1c133889`

## Table S4: Section 3.5.3 binary-to-ternary dataset

- Input file path: `outputs/phase1_step3/binary_to_ternary_dataset.csv` + `outputs/phase1_step2_F2/solubility_table.csv` + `outputs/phase07_audit/master_table_v15_normalized.csv`
- Output file path: `outputs/supplementary/table_S4_section_3_5_3_dataset.csv`
- Row count: 17
- Sanity checks: train=15, test=2; all log10_solubility non-null=true; unmapped vehicles=0
- SHA-256: `c32ab430b1d5aff43b1649136cdadaf9d3db811a2b1fcfa0297d0b3c6cb0676b`

## Detailed sanity checks

- S1 endpoint_unit distribution: `{μg/cm2/h: 47}`
- S1 endpoint_kind distribution: `{flux: 47}`
- S1 used_in_section unique values: `['excluded (variant: non_occluded)', 'excluded (variant: pretreated)', '§3.5.1 test, §3.5.2, §3.5.3 test', '§3.5.1 test, §3.5.2, §3.5.3 train', '§3.5.1 train, §3.5.2, §3.5.3 train', '§3.5.2']`
- S2 solubility_source distribution: `{PartII_PG_water_Manrique: 10, PartII_Table1: 2, PartI_Table1: 5}`
- S3 silicone_skin_ratio range: all 12 = 0.040134 to 0.450501; exclude pure EtOH = 0.114286 to 0.450501
- S4 solubility_source distribution: `{PartII_PG_water_Manrique: 10, PartII_Table1: 2, PartI_Table1: 5}`

## Cross-table consistency

- S1 record_id uniqueness: PASS
- S2/S4 overlap on common records: PASS
- S3 silicone_record_id membership in master_table and include_in_F3_silicone=True: PASS
- S3 skin_record_id membership in master_table and include_in_F3_skin=True: PASS

## Determinism

- Hash compare on four CSV files after two generation passes: PASS

Overall status: **PASS**
