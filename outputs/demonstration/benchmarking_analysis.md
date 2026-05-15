# Benchmarking Demonstration Analysis

## 1. Why The Earlier Ranking Was Removed

The previous benchmarking version ranked Paper 1 and literature permeation values together even when membrane type, excipient system, and dose mode were materially different. That ranking was not scientifically defensible.

This revised version changes the closure narrative: SkinMiner is used first as an automated literature reconnaissance engine, then as a structured comparability-assessment tool. The literature distribution is still shown, but only as context, not as a direct cross-condition leaderboard.

## 2. Updated Paper 1 Dataset

- Updated Excel rows: `150`
- Unique formulations: `30`
- Replicates per formulation: `5`
- Design groups: `BBD=15`, `LHS=10`, `BO=4`, `OPT=1`
- Paper 1 24 h mean range: `168.3-283.9 ug/cm2`

## 3. Excipient-Matched Literature Search

SkinMiner searched all `239` assembled records from the frozen GPT baseline (`full_run_16_post_all_fixes/patched_area.jsonl`). To suppress obvious non-topical contamination, the funnel only counts records that pass a topical/transdermal plausibility guard (`study_type` IVPT/IVRT plus skin/membrane context, excluding injection-like contexts).

| Funnel level | Matching records |
|---|---:|
| Level 1 exact match | 0 |
| Level 2 same excipient system | 0 |
| Level 3 partial excipient overlap | 26 |
| Level 4 same API + device only | 80 |

Level 2 is the critical result and it is `0`: no extracted record in the current corpus matches ibuprofen + Franz/diffusion cell + the full Poloxamer / ethanol / propylene glycol system. Level 1 is also `0`, so there is no exact match once Strat-M/synthetic membrane is required.

Level 3 returns `26` records across `5` papers. The partial overlaps are only reconnaissance signals: `poloxamer=3`, `ethanol=8`, `propylene glycol=15`.

## 4. Automated Comparability Assessment

SkinMiner can still structure a literature condition block automatically. The F1-F8 ibuprofen nanosuspension records provide a good demonstration case because the extraction captures API concentration, membrane, receptor, dose mode, diffusion area, and excipient composition.

However, the structured comparison shows why those values must not be ranked directly against Paper 1:

- API is only partially aligned (`5% w/w` vs `5% w/v`).
- Device is aligned (Franz diffusion cell).
- Membrane is not aligned (`Strat-M` vs `porcine skin`).
- Excipient system is not aligned (`Poloxamer 407 / EtOH / PG` vs `Vit. E TPGS / HPMC`).
- Dose mode is not aligned (`finite 300 mg` vs `infinite dose`).
- Receptor is aligned closely enough for qualitative comparison (`PBS` vs `PBS pH 7.4`).

That is why Figure 4 is now a split distribution figure with an explicit 'not directly comparable' separator instead of a combined ranking plot.

## 5. What SkinMiner Contributes To The PhD Story

Paper 1-3 solve how to optimize formulations efficiently inside a chosen experimental system. Paper 4 adds the missing literature-intelligence layer: it can automatically search whether that system already exists in the literature, expose when it does not, and make comparability judgments explicit when only partially related systems are available.

## 6. Updated Closure Statement

SkinMiner closes the loop not by naively merging heterogeneous literature responses into model training, but by turning the literature into a structured reconnaissance layer for formulation science. It answers three practical questions after optimization: Is there prior literature in the same excipient system? If not, how novel is the current setup? And if related papers exist, which condition mismatches prevent direct comparison?
