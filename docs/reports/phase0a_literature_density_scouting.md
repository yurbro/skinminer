# Phase 0a Literature Density Scouting

Metadata-only scout using PubMed E-utilities, Europe PMC OA search, Crossref metadata, and deterministic regex audit. No full-text PDFs were downloaded and no LLM scoring was used.

## 1. OA modelling-ready counts

| Track | PubMed hits | Europe PMC OA hits | Unique papers | OA papers | OA + PDF URL | OA modelling-ready | Franz | Non-Franz | With % composition | Without % composition |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A_caffeine | 113 | 94 | 187 | 101 | 100 | 4 | 2 | 2 | 1 | 3 |
| B_ibuprofen_gel | 83 | 76 | 140 | 78 | 76 | 2 | 1 | 1 | 0 | 2 |

### Track A - caffeine/nicotinamide/lidocaine vehicles: publication-year histogram
| Year | Count | Histogram |
|---:|---:|---|
| 2013 | 1 | `#` |
| 2014 | 1 | `#` |
| 2023 | 1 | `#` |
| 2025 | 1 | `#` |

### Track B - ibuprofen gel matrices: publication-year histogram
| Year | Count | Histogram |
|---:|---:|---|
| 2011 | 1 | `#` |
| 2020 | 1 | `#` |

## 2. Formulation-factor coverage

### Track A - caffeine/nicotinamide/lidocaine vehicles
Coverage below is counted within 4 OA modelling-ready papers.
PG with numeric %: 1; EtOH with numeric %: 1; water with numeric %: 0; mineral oil with numeric %: 0; IPM with numeric %: 0.
Multi-ratio proxy: 1 papers have explicit % ranges and 1 papers have at least two percentage values in title/abstract.

### Track B - ibuprofen gel matrices
Coverage below is counted within 2 OA modelling-ready papers.
Carbopol with numeric %: 0; HPMC with numeric %: 0; Poloxamer/Pluronic with numeric %: 0; gel word in title: 0.
Multi-ratio proxy: 0 papers have explicit % ranges and 2 papers have at least two percentage values in title/abstract.

## 3. Source/target paper candidates

### Track A - caffeine/nicotinamide/lidocaine vehicles: top candidates
| Rank | Year | API | Identifier | Journal | Title | Signals |
|---:|---:|---|---|---|---|---|
| 1 | 2025 | nicotinamide | doi:10.1186/s13065-025-01555-6 | BMC chemistry | Eco-friendly QbD-optimized chromatographic method for simultaneous analysis of metronidazole and nicotinamide with applications... | multi_terms=6; Franz; endpoints=flux/kp |
| 2 | 2013 | caffeine, lidocaine | doi:10.1208/s12248-013-9518-y | The AAPS journal | Structure activity relationships in alkylammonium C12-gemini surfactants used as dermal permeation enhancers. | multi_terms=4; endpoints=cumulative |
| 3 | 2014 | lidocaine | doi:10.1186/1746-6148-10-138 | BMC veterinary research | The effects of chemical and physical penetration enhancers on the percutaneous permeation of lidocaine through equine skin. | multi_terms=3; range_pct; pct_values=7; Franz; endpoints=flux; ionto/microneedle |
| 4 | 2023 | lidocaine | doi:10.3390/pharmaceutics15020318 | Pharmaceutics | Physicochemical Properties and Transdermal Absorption of a Flurbiprofen and Lidocaine Complex in the Non-Crystalline Form. | multi_terms=2; endpoints=flux |

#### Track A per-API top candidates: caffeine
| Rank | Year | API | Identifier | Journal | Title | Signals |
|---:|---:|---|---|---|---|---|
| 1 | 2013 | caffeine, lidocaine | doi:10.1208/s12248-013-9518-y | The AAPS journal | Structure activity relationships in alkylammonium C12-gemini surfactants used as dermal permeation enhancers. | multi_terms=4; endpoints=cumulative |

#### Track A per-API top candidates: nicotinamide/niacinamide
| Rank | Year | API | Identifier | Journal | Title | Signals |
|---:|---:|---|---|---|---|---|
| 1 | 2025 | nicotinamide | doi:10.1186/s13065-025-01555-6 | BMC chemistry | Eco-friendly QbD-optimized chromatographic method for simultaneous analysis of metronidazole and nicotinamide with applications... | multi_terms=6; Franz; endpoints=flux/kp |

#### Track A per-API top candidates: lidocaine/lignocaine
| Rank | Year | API | Identifier | Journal | Title | Signals |
|---:|---:|---|---|---|---|---|
| 1 | 2013 | caffeine, lidocaine | doi:10.1208/s12248-013-9518-y | The AAPS journal | Structure activity relationships in alkylammonium C12-gemini surfactants used as dermal permeation enhancers. | multi_terms=4; endpoints=cumulative |
| 2 | 2014 | lidocaine | doi:10.1186/1746-6148-10-138 | BMC veterinary research | The effects of chemical and physical penetration enhancers on the percutaneous permeation of lidocaine through equine skin. | multi_terms=3; range_pct; pct_values=7; Franz; endpoints=flux; ionto/microneedle |
| 3 | 2023 | lidocaine | doi:10.3390/pharmaceutics15020318 | Pharmaceutics | Physicochemical Properties and Transdermal Absorption of a Flurbiprofen and Lidocaine Complex in the Non-Crystalline Form. | multi_terms=2; endpoints=flux |

### Track B - ibuprofen gel matrices: top candidates
| Rank | Year | Identifier | Journal | Title | Signals |
|---:|---:|---|---|---|---|
| 1 | 2020 | doi:10.3390/pharmaceutics12020151 | Pharmaceutics | Evaluation of Formulation Parameters on Permeation of Ibuprofen from Topical Formulations Using Strat-M® Membrane. | multi_terms=17; pct_values=6; endpoints=flux/cumulative |
| 2 | 2011 | doi:10.1186/1471-2210-11-12 | BMC pharmacology | The effect of formulation vehicles on the in vitro percutaneous permeation of ibuprofen. | multi_terms=12; pct_values=4; Franz; endpoints=flux/cumulative/kp/lag |

## 4. Recommendation

| Track | Signal class | OA modelling-ready | Ranked multi-formulation candidates | Formulation diversity count |
|---|---|---:|---:|---:|
| A_caffeine | Weak | 4 | 4 | 2 |
| B_ibuprofen_gel | Weak | 2 | 2 | 0 |

Decision: NEITHER. Both tracks are weak under the regex-only OA modelling-ready screen.

## 5. Risks / caveats

### Track A - caffeine/nicotinamide/lidocaine vehicles
Ionto/microneedle/electroporation dilution risk: 1/4 OA modelling-ready papers flagged.
Journal concentration among OA modelling-ready papers: The AAPS journal=1 (25.0%), BMC veterinary research=1 (25.0%), Pharmaceutics=1 (25.0%), BMC chemistry=1 (25.0%).
First/senior author concentration proxy: Silva=1 (25.0%), Michniak-Kohn=1 (25.0%), Stahl=1 (25.0%), Kietzmann=1 (25.0%), Xu=1 (25.0%).
Language metadata across unique papers: eng=187.
PubMed hits are well below the rough prior of 500-1500, so the prior was optimistic for the exact vehicle-constrained query.

### Track B - ibuprofen gel matrices
Ionto/microneedle/electroporation dilution risk: 0/2 OA modelling-ready papers flagged.
Journal concentration among OA modelling-ready papers: BMC pharmacology=1 (50.0%), Pharmaceutics=1 (50.0%).
First/senior author concentration proxy: Stahl=1 (50.0%), Kietzmann=1 (50.0%), Bolla=1 (50.0%), Renukuntla=1 (50.0%).
Language metadata across unique papers: eng=136, ita=1, ger=1, chi=1, unknown=1.
PubMed hits are below the rough prior of 150-500, so the prior was optimistic for the exact gel query.

RECOMMENDED TRACK: NEITHER | Both tracks are weak under the regex-only OA modelling-ready screen.
