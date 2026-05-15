# Excipient-Matched Literature Search

## Search Scope

- Source file: `C:\Users\yz02380\OneDrive - University of Surrey\Science Research\Codes\SkinMiner\outputs\full_run_16_post_all_fixes\patched_area.jsonl`
- Total assembled records scanned: `239`
- Records passing the topical/transdermal plausibility guard: `133`
- Search fields inspected: formulation label/name, API concentration raw text, structured component list, condition notes, and evidence snippets.

## Funnel Counts

| Level | Criteria | Matching records |
|---|---|---:|
| Level 1 | Ibuprofen + Franz/diffusion cell + Strat-M/synthetic membrane + poloxamer + ethanol + PG | 0 |
| Level 2 | Ibuprofen + Franz/diffusion cell + poloxamer + ethanol + PG | 0 |
| Level 3 | Ibuprofen + Franz/diffusion cell + at least one of poloxamer / ethanol / PG | 26 |
| Level 4 | Ibuprofen + Franz/diffusion cell | 80 |

## Interpretation

- Level 1 exact matches found: `0`.
- Level 2 same-excipient-system matches found: `0`.
- Level 3 partial-overlap matches found: `26` across `5` papers.
- The absence of Level 1 and Level 2 hits means the current SkinMiner corpus does not contain a directly comparable ibuprofen Franz-cell record with the full Poloxamer 407 / ethanol / propylene glycol system.
- That is the core novelty argument for Paper 1: SkinMiner can search the corpus automatically and still show that your exact experimental system is not already represented in the extracted literature set.

## Level 3 Partial Overlap Breakdown

| Excipient token | Records |
|---|---:|
| `ethanol` | 8 |
| `poloxamer` | 3 |
| `propylene glycol` | 15 |

| DOI | Example matched formulation labels |
|---|---|
| `10.1007/s11095-008-9785-y` | Ibuprofen 750 μg/cm², text_1 |
| `10.1007/s11095-024-03747-6` | Ibuprofen 10% (With Poloxamer 188), Ibuprofen 15% (With Poloxamer 188), Ibuprofen 5% (With Poloxamer 188) |
| `10.1016/j.ijpharm.2016.03.043` | IBUGEL™ (Ibuprofen 5% w/w), IBULEVE™ Speed Relief 5% Spray, Isopropyl alcohol solution (5% w/w), Propylene glycol solution (5% w/w) |
| `10.1016/j.ijpharm.2019.118975` | F1, F2, F3 |
| `10.3389/fchem.2021.767923` | CI1 |

## Notes

- Level 3 hits are partial textual overlaps only. They are useful as reconnaissance signals, not as evidence of direct comparability.
- The funnel intentionally uses assembled records rather than verified-only records because the task here is literature reconnaissance, not benchmark-grade endpoint confirmation.
