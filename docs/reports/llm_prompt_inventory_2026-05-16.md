# SkinMiner LLM Prompt Inventory — 2026-05-16

This inventory describes the live source tree as inspected on 2026-06-24. Prompt text is reproduced verbatim from the code, except that runtime-interpolated values are replaced by `{{variable_name}}` slots. No separate developer-role messages were found in these calls.

The frozen baseline models are OpenAI `gpt-4o-mini` and Anthropic `claude-sonnet-4-6`, each used for all stages in its respective frozen run (`reports/baseline_definition.md:7-16`, `reports/baseline_definition.md:28-38`). Document-metadata recovery was added after that April freeze; its provider defaults are the same two model names (`utils/llm_client.py:12-14`, `utils/llm_client.py:58-64`).

## Summary table (draft of Supplementary Table S7)

| Stage | Role | Prompt version ID | Model (frozen baseline) | Output schema |
|---|---|---|---|---|
| Relevance triage | Abstract-level OA processing priority | `triage.abstract_relevance` / `2026-03-28.v1` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `LLMTriageResult` |
| Route detection | Locate evidence carrier and select extraction modality | `routing.structured_first` / `2026-03-28.v1` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `RouterLLMResponse` |
| Text extraction | Extract structured IVPT/IVRT records from selected text | `extractors.text.structured_fields` / `2026-04-11.v1` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `PaperExtraction` |
| Table extraction | Extract every relevant formulation × endpoint row | `extractors.table.structured_tables` / `2026-05-10.change-set-c` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `TableExtractionResult` |
| Figure triage | Select one digitizable endpoint subplot; conditional calibration retry | `extractors.figure.triage` / `2026-04-06.v1` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `FigureTriageResult` |
| Figure VLM digitisation | Read endpoint values from one locked subplot crop | `extractors.figure.vlm_digitize` / `2026-04-11.v1` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `VLMFigureResult` |
| Figure curve-label mapping | Constrain digitized curves to extracted formulation labels | `extractors.figure.curve_map` / `2026-03-28.v1` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `MapResult` |
| Verification adjudication | Second opinion on recoverable unresolved records | `verification.llm_adjudication` / `2026-04-03.v1` | GPT: `gpt-4o-mini`; Claude: `claude-sonnet-4-6` | `AdjudicationVerdict` |
| Document-metadata recovery | Recover bibliographic metadata from uploaded PDF text | `corpus.pdf_metadata` / `2026-05-10.v1` | Not in April frozen runs; defaults: `gpt-4o-mini` / `claude-sonnet-4-6` | `PdfMetadataLLMResponse` |

Prompt assets are registered centrally in `run_pipeline.py:91-100`. The live table prompt version is `2026-05-10.change-set-c` (`extractors/table/extractor.py:53-54`), while the older April frozen-baseline record lists `2026-04-11.v1` (`reports/baseline_definition.md:18-26`, `reports/baseline_definition.md:39-47`). Table S7 should state explicitly whether it documents the live pipeline or the historical frozen run.

## 1. Relevance triage

### 1.1 Stage identity

- **Prompt definition:** `triage/prompts.py:1-12`
- **Call site:** `triage/llm_triage.py:99-110`
- **Prompt asset/version:** `triage.abstract_relevance` / `2026-03-28.v1`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `LLMTriageResult`
- **Top-level fields:** `queue`, `relevance_label`, `mentions_franz_in_abstract`, `likely_study_type`, `likely_has_measurable_endpoint`, `likely_has_formulation_info`, `likely_barrier_category`, `what_to_check_in_fulltext`, `rationale`, `confidence` (`triage/llm_triage.py:20-30`)

The preceding deterministic prefilter is not an LLM call. It searches title plus abstract for the word `ibuprofen`, requires at least one topical/permeation/diffusion-related pass pattern, and rejects records matching oral/tablet/capsule/plasma/pharmacokinetic/in-vivo patterns (`triage/rule_filter.py:8-28`, `triage/rule_filter.py:43-71`).

### 1.2 Full prompt text

**System prompt** (`triage/prompts.py:4-8`):

```text
You are a strict scientific literature triage assistant for an ibuprofen dermal formulation mining framework. Use ONLY the provided title and abstract. If the abstract does not support a claim, mark it uncertain. Prioritize whether the paper should advance to OA full-text processing for diffusion-cell IVPT/IVRT evidence.
```

**User prompt** (`triage/prompts.py:11-12`):

```text
TITLE:
{{title}}

ABSTRACT:
{{abstract}}
```

### 1.3 Example input

**Real example.** The title and abstract below are from `outputs/gpt-extended-baseline/corpus.jsonl:2`.

```text
TITLE:
Topical administration of racemic ibuprofen.

ABSTRACT:
In vitro experiments to investigate possible stereoselective aspects of the topical administration of ibuprofen have been conducted. Incubation of ibuprofen with rat skin homogenates in the presence of coenzyme A, ATP, and magnesium provided no evidence for the formation of ibuprofenyl coenzyme A (the initial intermediate in the metabolic inversion of [R]- to [S]-ibuprofen). Similar incubation studies gave no indication of a change in the enantiomeric ratios of ibuprofen over the time course of the experiments. Percutaneous penetration studies of ibuprofen gel through porcine skin indicated that the ibuprofen enantiomer levels in the reservoir solutions were consistent with racemic ibuprofen having traversed the skin with no metabolic inversion. These results suggest that, in the models studied, skin metabolism does not result in the chiral inversion of (R)- to (S)-ibuprofen and that the topical administration of ibuprofen will result in the delivery of 50% "isomeric ballast."
```

### 1.4 Example output

**Real output**, shortened only by omitting corpus fields that are carried through outside the schema, from `outputs/gpt-extended-baseline/llm_triage.jsonl:2`.

```json
{
  "queue": "now",
  "relevance_label": "relevant",
  "mentions_franz_in_abstract": "no",
  "likely_study_type": "IVPT",
  "likely_has_measurable_endpoint": "yes",
  "likely_has_formulation_info": "yes",
  "likely_barrier_category": "skin",
  "what_to_check_in_fulltext": [
    "Details on formulation specifics",
    "Methodology of percutaneous penetration studies",
    "Quantitative results of enantiomeric ratios",
    "Discussion on implications of findings"
  ],
  "rationale": "The abstract discusses percutaneous penetration of ibuprofen through skin and suggests measurable outcomes regarding enantiomeric ratios, indicating relevance to IVPT study for dermal formulation of ibuprofen.",
  "confidence": 0.9
}
```

### 1.5 Caption suggestion

The prompt, example input, and example output of abstract relevance assessment in the relevance-triage stage.

## 2. Route detection

### 2.1 Stage identity

- **Prompt definition:** `detection/router.py:25-26`, `detection/router.py:98-104`, `detection/router.py:515-522`
- **Call site:** `detection/router.py:523-532`
- **Prompt asset/version:** `routing.structured_first` / `2026-03-28.v1`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `RouterLLMResponse`
- **Top-level fields:** `paper_type`, `mentions_ibuprofen`, `mentions_diffusion_cell`, `franz_confirmed`, `where_diffusion_cell`, `where_franz`, `study_type`, `barrier_category`, `barrier_name_raw`, `endpoint_found`, `endpoint_time_found`, `where_endpoint`, `endpoint_carrier`, `endpoint_carrier_snippet`, `formulation_carrier`, `formulation_carrier_snippet`, `endpoint_likely_in_supp`, `formulation_table_missing`, `notes` (`detection/router.py:69-88`)

### 2.2 Full prompt text

**System prompt** (`detection/router.py:98-104`):

```text
You are an evidence routing assistant for an OA-only ibuprofen dermal formulation mining framework. Use ONLY the supplied document text. Identify where extractable evidence appears, but do not apply the strict v1 policy here. When the content comes from structured XML or HTML, locators may refer to blocks, sections, captions, or headings rather than page numbers. Prefer assigning text, table, figure, or mixed whenever the carrier is explicit enough. Use unresolved only when the carrier really cannot be determined from the supplied text.
```

**User prompt** (`detection/router.py:515-522`):

```text
Determine the best extraction route for this OA paper.

SOURCE_BACKEND: {{router_document.source_backend}}
SOURCE_REF: {{router_document.source_ref}}
DOI: {{doi}}
TITLE: {{title}}

DOCUMENT:
{{router_document.content}}
```

### 2.3 Example input

**Constructed shortening based on a real routed paper.** The DOI, title, and evidence phrases are drawn from the real route result at `outputs/gpt-extended-baseline/route_decisions.jsonl:46`; the full document supplied at runtime was longer.

```text
Determine the best extraction route for this OA paper.

SOURCE_BACKEND: pdf_local
SOURCE_REF: papers\pdf\10.1007_s11095-008-9785-y__4a59bd2375.pdf
DOI: 10.1007/s11095-008-9785-y
TITLE: Dermatopharmacokinetics: factors influencing drug clearance from the stratum corneum.

DOCUMENT:
Ibuprofen was applied as a saturated drug solution in 75:25 (v/v) propylene glycol/water. Table II reports the quantity of ibuprofen in the stratum corneum after a 30-minute application, and Figures 3–6 show concentration profiles and clearance over time.
```

### 2.4 Example output

**Real schema output** from `outputs/gpt-extended-baseline/route_decisions.jsonl:46`, represented by its stored `raw_labels`.

```json
{
  "paper_type": "review",
  "mentions_ibuprofen": "yes",
  "mentions_diffusion_cell": "yes",
  "franz_confirmed": "no",
  "where_diffusion_cell": "Not explicitly mentioned, but related to experiments tracking ibuprofen clearance from the stratum corneum (SC).",
  "where_franz": "Not mentioned, likely not applicable as the focus is on pharmacokinetics.",
  "study_type": "IVPT",
  "barrier_category": "skin",
  "barrier_name_raw": "stratum corneum",
  "endpoint_found": "yes",
  "endpoint_time_found": "yes",
  "where_endpoint": "Table II and Figures 3, 4, 5, and 6 show ibuprofen concentration profiles and clearance over time from the SC.",
  "endpoint_carrier": "table_text",
  "endpoint_carrier_snippet": "Table II: Quantity of ibuprofen (mean ± SD, n=5) in the SC following a 30-minute application...",
  "formulation_carrier": "narrative",
  "formulation_carrier_snippet": "...a saturated drug solution in 75:25 (v/v) propylene glycol/water...",
  "endpoint_likely_in_supp": "no",
  "formulation_table_missing": "no",
  "notes": "The paper investigates the dynamics of ibuprofen clearance from the skin, highlighting the role of the formulation and occlusion in the process."
}
```

### 2.5 Caption suggestion

The prompt, example input, and example output of evidence-carrier classification in the route-detection stage.

## 3. Text extraction ← MAIN-TEXT FIGURE

### 3.1 Stage identity

- **Prompt definition:** `extractors/text/extract_fields.py:17-25`, `extractors/text/extract_fields.py:104-124`
- **Call site:** `extractors/text/extract_fields.py:126-138`
- **Prompt asset/version:** `extractors.text.structured_fields` / `2026-04-11.v1`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `PaperExtraction`
- **Top-level fields:** `doi`, `title`, `records`, `extraction_notes` (`extractors/text/extract_fields.py:79-85`)
- **Nested record fields:** `study_type`, `cell_type`, `dosage_form`, `barrier_category`, `barrier_name`, `api_name`, `api_conc_raw`, `diffusion_area_cm2`, `membrane_type`, `membrane_source`, `membrane_thickness_um`, `receptor_medium`, `dose_type`, `dose_amount`, `endpoint_main`, `endpoint_optional`, `ingredients`, `evidence`, `needs_supp`, `confidence`, `notes` (`extractors/text/extract_fields.py:53-76`)

### 3.2 Full prompt text

**System prompt** (`extractors/text/extract_fields.py:20-25`):

```text
You are a careful scientific extraction assistant. Use ONLY the supplied structured content blocks or PDF page text with explicit locators. Do not guess. Prefer numeric tables when available. When citing evidence, keep the provided locator style such as 'block 7' or 'page 12'.
```

**User prompt** (`extractors/text/extract_fields.py:104-124`):

```text
Extract structured records for ibuprofen diffusion-cell IVPT/IVRT text-route evidence. Return up to five explicit records only when multiple formulations are clearly reported.

Extraction requirements:
- Extract vehicle/excipient composition into ingredients, including non-API ingredient names and raw concentration text.
- Extract membrane_type, membrane_source, and membrane_thickness_um when explicitly reported.
- Extract receptor_medium when explicitly reported, including pH and surfactants/cosolvents.
- Extract dose_type as finite or infinite when explicitly reported, plus dose_amount as the source text amount.
- Include evidence items for membrane, receptor medium, dose, excipients, API concentration, endpoint, time, area, and device when present.
- Do not guess missing fields and do not treat receptor-medium drug concentration as formulation API concentration.

DOI: {{doi}}
TITLE: {{title}}
SOURCE_FORMAT: {{window.source_format}}
SOURCE_BACKEND: {{window.source_backend}}
SOURCE_REF: {{window.source_ref}}
LOCATOR_MODE: {{window.locator_mode}}
ANCHOR_LOCATORS: {{window.anchor_locators}}
SELECTED_LOCATORS: {{window.selected_locators}}
TABLE_HINT: {{window.table_hint}}

CONTENT:
{{window.content_text}}
```

### 3.3 Example input

**Constructed concise example, faithful to the real text-window format.** It uses the paper and source-backed facts represented in `outputs/gpt-extended-baseline/text_raw.jsonl:2`.

```text
DOI: 10.1007/s11095-008-9785-y
TITLE: Dermatopharmacokinetics: factors influencing drug clearance from the stratum corneum
SOURCE_FORMAT: pdf
SOURCE_BACKEND: pdf_local
SOURCE_REF: papers\pdf\10.1007_s11095-008-9785-y__4a59bd2375.pdf
LOCATOR_MODE: page
ANCHOR_LOCATORS: []
SELECTED_LOCATORS: ['page 3', 'page 11', 'page 19']
TABLE_HINT: Table II

CONTENT:
--- PAGE 3 ---
Ibuprofen was applied as a saturated solution in a 75:25 (v/v) propylene glycol/water vehicle.

--- PAGE 11 ---
The solution applied (500 µl) was constrained by a plastic template.

--- PAGE 19 ---
Table II. Quantity of ibuprofen (mean ± SD, n=5) in the stratum corneum following a 30-minute application. At 0.5 h under occlusion the amount was 7.3 ± 1.0 µg/cm2.
```

### 3.4 Example output

**Real output** from `outputs/gpt-extended-baseline/text_raw.jsonl:2`.

```json
{
  "doi": "10.1007/s11095-008-9785-y",
  "title": "Dermatopharmacokinetics: factors influencing drug clearance from the stratum corneum",
  "records": [
    {
      "study_type": "IVPT",
      "cell_type": "Franz",
      "dosage_form": "saturated solution",
      "barrier_category": "skin",
      "barrier_name": "stratum corneum",
      "api_name": "ibuprofen",
      "api_conc_raw": "10 mg/ml",
      "diffusion_area_cm2": 3.14,
      "membrane_type": "skin",
      "membrane_source": "human",
      "membrane_thickness_um": 10.0,
      "receptor_medium": "propylene glycol/water",
      "dose_type": "infinite",
      "dose_amount": "500 µl",
      "endpoint_main": {
        "endpoint_type": "Jss",
        "value": 2.99,
        "unit": "-",
        "time_value": 0.5,
        "time_unit": "hr"
      },
      "endpoint_optional": [
        {
          "endpoint_type": "Jss",
          "value": 7.3,
          "unit": "µg/cm2",
          "time_value": 0.5,
          "time_unit": "hr"
        }
      ],
      "ingredients": [
        {
          "name": "ibuprofen",
          "concentration_raw": "10 mg/ml"
        },
        {
          "name": "propylene glycol",
          "concentration_raw": "75:25 (v/v) propylene glycol/water"
        }
      ],
      "evidence": [
        {
          "field": "membrane",
          "locator": "Table II",
          "snippet": "Quantity of ibuprofen (mean ± SD, n=5) in the SC following a 30-minute application"
        },
        {
          "field": "receptor medium",
          "locator": "page 3",
          "snippet": "saturated solution in 75:25 (v/v) propylene glycol/water"
        },
        {
          "field": "dose",
          "locator": "page 11",
          "snippet": "The solution applied (500 µl) was constrained by a plastic template"
        }
      ],
      "needs_supp": "no",
      "confidence": 1.0,
      "notes": "Main parameters extracted from results reported directly in the document."
    }
  ],
  "extraction_notes": "Extracted relevant data for ibuprofen diffusion-cell IVPT experiments based on provided pages."
}
```

### 3.5 Caption suggestion

The prompt, example literature passage, and structured record returned by the text-extraction stage of SkinMiner.

## 4. Table extraction

### 4.1 Stage identity

- **Prompt definition:** `extractors/table/extractor.py:53-61`, `extractors/table/extractor.py:629-671`
- **Call site:** `extractors/table/extractor.py:706-750`
- **Prompt asset/version:** `extractors.table.structured_tables` / `2026-05-10.change-set-c`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `TableExtractionResult`
- **Top-level fields:** `formulations`, `formulation_table_found`, `formulation_table_in_image`, `recommended_next`, `notes` (`extractors/table/extractor.py:143-150`)
- **Nested formulation fields:** `formulation_label`, `dosage_form`, `api_name`, `api_concentration_value`, `api_concentration_unit`, `api_basis`, `api_concentration_raw`, `components`, `endpoint_time_value`, `endpoint_time_unit`, `endpoints`, `membrane_type`, `membrane_source`, `membrane_thickness_um`, `receptor_medium`, `dose_type`, `dose_amount`, `water_qs_or_balance`, `table_id`, `source_pages`, `source_locators`, `evidence_snippet`, `confidence`, `notes` (`extractors/table/extractor.py:114-140`)

### 4.2 Full prompt text

**System prompt** (`extractors/table/extractor.py:56-61`):

```text
You extract formulation composition tables from OA scientific articles. Use ONLY the provided structured tables or PDF page text and optional page images. Do not guess concentrations or endpoint values. Preserve explicit table locators such as 'Table 2' when they are supplied.
```

**User prompt** (`extractors/table/extractor.py:639-671`):

```text
Extract formulation composition tables relevant to ibuprofen in vitro permeation or release. Also capture endpoint measurements, endpoint times, units, SD values, replicate counts, and basis when they are explicitly tabulated. Return only structured output. Preserve explicit table identifiers in table_id.

STRICT ROW COMPLETENESS RULES:
- You MUST extract every relevant data row in the provided tables. Do not skip, summarize, or return only representative rows.
- If a table has 8 formulation rows and one endpoint column, return 8 records. If it has 8 formulation rows and 3 endpoint time columns, return 24 records.
- For one-row/multiple-timepoint endpoint tables, emit one independent record for each formulation x each timepoint column, set endpoint_time_value/unit for that exact column, and put that column's measurement(s) in endpoints.
- Do not copy a final-time endpoint mean into earlier timepoint records. Every endpoint mean must match the same table cell/time column named in endpoint_time_value.
- The formulation_label for an endpoint record MUST come from the same table row as every endpoint mean. Do not substitute labels from another table by row order.
- The endpoints field is a list. Add one item per distinct endpoint column explicitly present for that same row/timepoint.
- Use endpoint kind exactly as one of: flux, cumulative_amount, permeability_coefficient, partition_parameter, diffusion_parameter, lag_time, permeated_fraction, unknown.
- If cumulative amount and flux/Jss/permeability columns coexist for the same formulation row, include BOTH as separate endpoint list items. Do not overwrite one with the other.
- Pair mean, SD, unit, and n_replicates from the same endpoint column or immediately associated adjacent column/footnote. Never use an SD, SE, CI, or range cell as the mean.
- If a cell is reported as mean +/- SD, put the first number in mean and the second in sd. If only mean is given, leave sd null.
- If ENDPOINT_TABLE_HINT is set, prioritize that table for endpoint records. Use other tables only to fill composition or shared context for matching labels.
- Keep composition-only rows separate from endpoint rows unless the same formulation label explicitly links them. Do not copy endpoint values onto unrelated composition/stability rows.
- Extract excipient/vehicle composition into components, including non-API ingredient names, concentrations, basis, and notes when available.
- Extract condition context when explicitly present in the table, footnote, title, or experiment context: membrane_type, membrane_source, membrane_thickness_um, receptor_medium, dose_type, and dose_amount.
- Use dose_type only as 'finite', 'infinite', or ''. Do not guess missing condition fields.

DOI: {{content_handle.doi}}
TITLE: {{route_decision.title}}
SOURCE_FORMAT: {{window.source_format}}
SOURCE_BACKEND: {{window.source_backend}}
SOURCE_REF: {{window.source_ref}}
LOCATOR_MODE: {{window.locator_mode}}
SELECTED_LOCATORS: {{window.selected_locators}}
ENDPOINT_TABLE_HINT: {{endpoint_table_hint}}
TABLE_TRUNCATED: {{window.table_truncated}}
TRUNCATION_NOTES: {{window.truncation_notes}}
CURVE_HINTS: {{curve_hints}}

CONTENT:
{{window.content_text}}
```

For PDF windows, up to two weak-text pages may also be attached as images (`extractors/table/extractor.py:724-727`).

### 4.3 Example input

**Real input excerpt** from the cached prompt at `outputs/v1.5_change_set_c_llm_cache/paper_067e8b4e5b8c_ab2378c3fa5b.json:11-19`. The source excerpt below is the relevant table portion; the real cached input includes pages 1–5.

```text
DOI: 10.1159/000315139
TITLE: Optimisation of Cosolvent Concentration for Topical Drug Delivery III – Influence of Lipophilic Vehicles on Ibuprofen Permeation
SOURCE_FORMAT: pdf
SOURCE_BACKEND: pdf_local
SOURCE_REF: papers\uploaded_external\watkinson_2011_III.pdf
LOCATOR_MODE: page
SELECTED_LOCATORS: ['page 1', 'page 2', 'page 3', 'page 4', 'page 5']
ENDPOINT_TABLE_HINT: Table 3
TABLE_TRUNCATED: True
TRUNCATION_NOTES: ['PDF page text cap reached']
CURVE_HINTS:

CONTENT:
Table 3. Steady-state flux values and permeability coefficients for the permeation of ibuprofen from saturated formulations containing MO and/or MG through silicone membrane (mean ± SD, n = 4)
MO/MG (v/v) | kp, cm/h × 10² | J, µg/cm²/h
0/100 | 0.41 ± 0.05 | 623.8 ± 67.7
10/90 | 0.39 ± 0.15 | 439.9 ± 23.9
```

### 4.4 Example output

**Real live-schema output** from `outputs/v1.5_change_set_c_llm_cache/paper_067e8b4e5b8c_ab2378c3fa5b.json:20-55` and `outputs/v1.5_change_set_c_llm_cache/paper_067e8b4e5b8c_ab2378c3fa5b.json:489-492`.

```json
{
  "formulations": [
    {
      "formulation_label": "0/100",
      "dosage_form": "",
      "api_name": "Ibuprofen",
      "api_concentration_value": null,
      "api_concentration_unit": "",
      "api_basis": "",
      "api_concentration_raw": "",
      "components": [],
      "endpoint_time_value": null,
      "endpoint_time_unit": "",
      "endpoints": [
        {
          "kind": "flux",
          "mean": 623.88,
          "sd": 67.7,
          "unit": "µg/cm²/h",
          "n_replicates": 4
        },
        {
          "kind": "permeability_coefficient",
          "mean": 0.418,
          "sd": 0.05,
          "unit": "cm/h × 10²",
          "n_replicates": 4
        }
      ],
      "membrane_type": "silicone",
      "membrane_source": "",
      "membrane_thickness_um": null,
      "receptor_medium": "",
      "dose_type": "infinite",
      "dose_amount": "",
      "water_qs_or_balance": "no",
      "table_id": "Table 3",
      "source_pages": [3],
      "source_locators": [],
      "evidence_snippet": "",
      "confidence": 1.0,
      "notes": ""
    }
  ],
  "formulation_table_found": "yes",
  "formulation_table_in_image": "no",
  "recommended_next": "ok",
  "notes": ""
}
```

### 4.5 Caption suggestion

The prompt, example table input, and row-complete structured output of the table-extraction stage.

## 5. Figure triage

### 5.1 Stage identity

- **Prompt definition:** `extractors/figure/triage.py:23-32`, `extractors/figure/triage.py:446-475`
- **Primary call site:** `extractors/figure/triage.py:478-520`, invoked at `extractors/figure/triage.py:678-701`
- **Conditional second call:** calibration-curve retry at `extractors/figure/triage.py:585-638`
- **Prompt asset/version:** `extractors.figure.triage` / `2026-04-06.v1`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `FigureTriageResult`
- **Top-level fields:** `endpoint_curve_present`, `likely_endpoint_type`, `figure_id`, `page_number`, `subplot`, `digitizable`, `why_not_digitizable`, `ticks_readable`, `legend_present`, `approx_curves_count`, `legend`, `suggests_table_exists`, `suggests_supp_exists`, `recommended_route`, `plot_bbox`, `axes_x_label`, `axes_x_unit`, `x_min`, `x_max`, `axes_y_label`, `axes_y_unit`, `y_min`, `y_max`, `y_kind`, `confidence`, `notes` (`extractors/figure/triage.py:52-80`)

### 5.2 Full prompt text

**System prompt, used by both calls** (`extractors/figure/triage.py:29-32`):

```text
You are a strict scientific figure triage assistant. Use ONLY the provided page images. If axis ranges or the plot bounding box cannot be read, keep them null.
```

**Primary user prompt text** (`extractors/figure/triage.py:453-462`):

```text
Triage the following figure pages for digitizable ibuprofen endpoint curves.

DOI: {{content_handle.doi}}
TITLE: {{route_decision.title}}
IMAGES: {{page_description}}

If the selected figure page contains multiple subplots, return exactly one target subplot as a single capital letter A/B/C/D. Never return comma-separated or semicolon-separated subplot lists. If several panels are plausible, choose the single best panel in reading order and explain ambiguity in notes. If the figure is single-panel, leave subplot empty.

Return structured output only.
```

The multimodal user message then appends one image item for every `{{page_image}}` (`extractors/figure/triage.py:472-475`).

**Conditional calibration-retry user prompt prefix** (`extractors/figure/triage.py:463-471`):

```text
Second-pass figure triage after the primary candidate was rejected as a calibration curve.

PRIMARY_REJECTED_FIGURE_ID: {{primary_artifact.figure_id}}
PRIMARY_REJECTED_PAGE: {{primary_artifact.page_number}}
PRIMARY_REJECTED_REASON: calibration_curve_not_target
ENDPOINT_HINTS: {{route_endpoint_hint_text}}
RETRY_CANDIDATE_PAGES: {{retry_page_numbers}}

Find a non-calibration ibuprofen permeation, release, cumulative amount, flux, or Jss endpoint plot. Do not select a calibration curve, standard curve, schematic, device photo, or UV image panel. If a page contains a plot panel plus image panels, select the plot panel only.

Triage the following figure pages for digitizable ibuprofen endpoint curves.

DOI: {{content_handle.doi}}
TITLE: {{route_decision.title}}
IMAGES: {{page_description}}

If the selected figure page contains multiple subplots, return exactly one target subplot as a single capital letter A/B/C/D. Never return comma-separated or semicolon-separated subplot lists. If several panels are plausible, choose the single best panel in reading order and explain ambiguity in notes. If the figure is single-panel, leave subplot empty.

Return structured output only.
```

### 5.3 Example input

**Real retry example.** The image bundle and retry context are recorded in `outputs/gpt-extended-baseline/figure_triage.jsonl:2`.

```text
Second-pass figure triage after the primary candidate was rejected as a calibration curve.

PRIMARY_REJECTED_FIGURE_ID: figure 10
PRIMARY_REJECTED_PAGE: 14
PRIMARY_REJECTED_REASON: calibration_curve_not_target
RETRY_CANDIDATE_PAGES: [16, 15, 17]

Triage the following figure pages for digitizable ibuprofen endpoint curves.

DOI: 10.1016/j.ejpb.2020.05.013
TITLE: Design and development of a novel fused filament fabrication (FFF) 3D printed diffusion cell with UV imaging capabilities to characterise permeation in pharmaceutical formulations.
IMAGES: Image 1 = PAGE 16, Image 2 = PAGE 15, Image 3 = PAGE 17

[Attached page images:
 outputs\gpt-extended-baseline\figure\triage_images\10.1016_j.ejpb.2020.05.013__p16.jpg
 outputs\gpt-extended-baseline\figure\triage_images\10.1016_j.ejpb.2020.05.013__p15.jpg
 outputs\gpt-extended-baseline\figure\triage_images\10.1016_j.ejpb.2020.05.013__p17.jpg]
```

### 5.4 Example output

**Real retry output** from `outputs/gpt-extended-baseline/figure_triage.jsonl:2`.

```json
{
  "endpoint_curve_present": "yes",
  "likely_endpoint_type": "cumulative_amount",
  "figure_id": "figure 11",
  "page_number": 16,
  "subplot": "A",
  "digitizable": "yes",
  "why_not_digitizable": "",
  "ticks_readable": "yes",
  "legend_present": "no",
  "approx_curves_count": 1,
  "legend": [],
  "suggests_table_exists": "no",
  "suggests_supp_exists": "no",
  "recommended_route": "digitize",
  "plot_bbox": null,
  "axes_x_label": "Time (min)",
  "axes_x_unit": "min",
  "x_min": 0.0,
  "x_max": 720.0,
  "axes_y_label": "Amount permeated (µg/mL)",
  "axes_y_unit": "µg/mL",
  "y_min": 0.0,
  "y_max": 250.0,
  "y_kind": "amount_total",
  "confidence": 0.95,
  "notes": "The plot is clearly designated as part (a) of figure 11 and indicates the cumulative amount of IBU permeated over time, meeting endpoint criteria. No ambiguity in identifying this as the primary plot."
}
```

### 5.5 Caption suggestion

The prompt, candidate page images, and selected subplot returned by the figure-triage stage.

## 6. Figure VLM digitisation

### 6.1 Stage identity

- **Prompt definition:** `extractors/figure/vlm_digitize.py:23-33`, `extractors/figure/vlm_digitize.py:205-244`, `extractors/figure/vlm_digitize.py:273-286`
- **Call site:** `extractors/figure/vlm_digitize.py:288-306`
- **Prompt asset/version:** `extractors.figure.vlm_digitize` / `2026-04-11.v1`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `VLMFigureResult`
- **Top-level fields:** `subplot_semantic_type`, `axis_summary`, `legend_summary`, `readability_status`, `quality_flags`, `readings` (`extractors/figure/vlm_digitize.py:48-60`)
- **Nested reading fields:** `series_marker_raw`, `series_label_raw`, `series_rank_hint`, `endpoint_time`, `endpoint_time_unit`, `endpoint_value`, `endpoint_unit`, `confidence`, `notes` (`extractors/figure/vlm_digitize.py:36-45`)

### 6.2 Full prompt text

**System prompt** (`extractors/figure/vlm_digitize.py:26-33`):

```text
You are a strict scientific vision extraction assistant for dermal ibuprofen figure reading. You are given one locked subplot crop that should already isolate the target panel. Use only the supplied crop and structured context. Do not invent labels or values. Return visual series identity first, before any downstream grounding. If the subplot is unreadable or the series identity cannot be grounded confidently, say so. Prefer conservative structured output over guesses.
```

**User prompt text** (`extractors/figure/vlm_digitize.py:273-286`), including the context packet assembled at `extractors/figure/vlm_digitize.py:219-244`:

```text
Read the locked subplot crop and extract endpoint values for visually distinct series.

Rules:
1. Return one reading per visible series only.
2. Return visual series identity first: series_marker_raw and/or series_label_raw.
3. Use FIGURE_LABEL_SPACE as the preferred grounding hint if the crop itself lacks a readable legend.
4. Use SOURCE_LABEL_SPACE only as a secondary hint; do not force a match if it does not fit the visible series.
5. Do not collapse multiple series onto the same top curve or reuse the same endpoint value across different markers unless visually obvious.
6. Read values at TARGET_TIMEPOINT_H.
7. Use KNOWN_CONDITION_CONTEXT only as source-backed experiment context; do not infer new membrane, receptor, or dose fields from the figure crop.
8. If the subplot is not a permeation/release plot, return readability_status=unreadable.
9. If you are uncertain, prefer fewer readings with lower confidence over guessing.

PAPER_ID: {{triage.paper_id}}
DOI: {{triage.doi}}
FIGURE_ID: {{triage.figure_id}}
PAGE_NUMBER: {{triage.page_number}}
SUBPLOT: {{triage.subplot_or_single_panel}}
FIGURE_SEMANTIC_TYPE: {{triage.figure_semantic_type}}
CANDIDATE_TIER: {{source_endpoint.candidate_tier}}
SUBPLOT_LOCK_FAILED: {{source_endpoint.subplot_lock_failed}}
CROP_WIDTH_PX: {{crop_width_px}}
CROP_HEIGHT_PX: {{crop_height_px}}
SOURCE_RENDER_DPI: {{TRIAGE_RENDER_DPI}}
AXES_X_LABEL: {{triage.axes_x_label}}
AXES_X_UNIT: {{triage.axes_x_unit}}
AXES_X_RANGE: {{triage.x_min}} to {{triage.x_max}}
AXES_Y_LABEL: {{triage.axes_y_label}}
AXES_Y_UNIT: {{triage.axes_y_unit}}
AXES_Y_RANGE: {{triage.y_min}} to {{triage.y_max}}
TARGET_TIMEPOINT_H: {{target_timepoint}}
EXPECTED_ENDPOINT_KIND: {{expected_kind}}
EXPECTED_ENDPOINT_UNIT: {{expected_unit}}
FIGURE_LABEL_SPACE: {{figure_label_space}}
SOURCE_LABEL_SPACE: {{source_label_space}}
KNOWN_CONDITION_CONTEXT:
{{known_conditions_or_none}}
PAGE_TEXT_SNIPPET: {{page_text_snippet}}
```

The locked crop is attached as a separate `input_image` item after this text (`extractors/figure/vlm_digitize.py:294-297`).

### 6.3 Example input

**Real crop/context example** from `outputs/gpt-extended-baseline/figure_vlm_readings.jsonl:6`.

```text
PAPER_ID: paper_b451e1b601ac
DOI: 10.1016/j.ejpb.2020.05.013
FIGURE_ID: figure 11
PAGE_NUMBER: 16
SUBPLOT: A
CANDIDATE_TIER: triage_primary
SUBPLOT_LOCK_FAILED: False
CROP_WIDTH_PX: 633
CROP_HEIGHT_PX: 656
SOURCE_RENDER_DPI: 170
FIGURE_LABEL_SPACE: []
SOURCE_LABEL_SPACE: ['5% w/w Ibuprofen gel']

[Attached locked crop:
 outputs\gpt-extended-baseline\figure\digitize_crops\figure_trace_paper_b451e1b601ac_figure_11_16_A_185470bfe0bc.png]
```

### 6.4 Example output

**Real raw VLM output** stored at `outputs/gpt-extended-baseline/figure_vlm_readings.jsonl:6`.

```json
{
  "subplot_semantic_type": "permeation_plot",
  "axis_summary": "Time (min) vs Amount permeated (µg/mL)",
  "legend_summary": "5% w/w Ibuprofen gel",
  "readability_status": "readable",
  "quality_flags": [],
  "readings": [
    {
      "series_marker_raw": "5% w/w Ibuprofen gel",
      "series_label_raw": "5% w/w Ibuprofen gel",
      "series_rank_hint": "1",
      "endpoint_time": 720.0,
      "endpoint_time_unit": "min",
      "endpoint_value": 250.0,
      "endpoint_unit": "µg/mL",
      "confidence": 0.95,
      "notes": ""
    }
  ]
}
```

### 6.5 Caption suggestion

The prompt, locked subplot crop, and direct endpoint reading returned by the figure VLM digitisation stage.

## 7. Figure curve-label mapping

### 7.1 Stage identity

- **Prompt definition:** `extractors/figure/map_curves.py:21-27`, `extractors/figure/map_curves.py:280-302`
- **Call site:** `extractors/figure/map_curves.py:289-312`
- **Prompt asset/version:** `extractors.figure.curve_map` / `2026-03-28.v1`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `MapResult`
- **Top-level fields:** `mappings`, `notes` (`extractors/figure/map_curves.py:41-45`)
- **Nested mapping fields:** `curve_id`, `curve_color`, `assigned_formulation_label`, `evidence_from_legend`, `rationale`, `confidence` (`extractors/figure/map_curves.py:30-38`)

### 7.2 Full prompt text

**System prompt** (`extractors/figure/map_curves.py:24-27`):

```text
You align digitized endpoint curves to formulation labels using the supplied zoomed plot image and formulation labels. Choose only from the provided formulation labels. If unclear, leave the assignment null.
```

**User prompt text** (`extractors/figure/map_curves.py:292-302`):

```text
Map each curve_id to one formulation label.

Allowed labels:
{{allowed_labels_as_bullets}}

Curves:
{{curve_text}}

Formulations:
{{formulation_text}}
```

The mapping zoom is attached as a separate `input_image` item. Each curve line is rendered as:

```text
- curve_id={{curve_id}}, curve_color={{curve_color}}, endpoint~{{endpoint_value}} {{endpoint_unit}}
```

Each formulation line is rendered as:

```text
- {{formulation_label}} | api={{api_name}} {{api_concentration_value}} {{api_concentration_unit}} | comps: {{component_summary}}
```

These line templates are defined at `extractors/figure/map_curves.py:280-287`.

### 7.3 Example input

**Constructed serialization from real mapping artifacts.** The labels and mapped curves are from `outputs/gpt-extended-baseline/figure_curve_map.jsonl:7-10`.

```text
Map each curve_id to one formulation label.

Allowed labels:
- IBUGEL™ (Ibuprofen 5% w/w)
- IBULEVE™ Speed Relief 5% Spray
- Isopropyl alcohol solution (5% w/w)
- Propylene glycol solution (5% w/w)

Curves:
- curve_id=cluster_1, curve_color=black, endpoint~{{endpoint_value_1}} {{endpoint_unit}}
- curve_id=cluster_2, curve_color=gray, endpoint~{{endpoint_value_2}} {{endpoint_unit}}
- curve_id=cluster_3, curve_color=green, endpoint~{{endpoint_value_3}} {{endpoint_unit}}
- curve_id=cluster_4, curve_color=gray, endpoint~{{endpoint_value_4}} {{endpoint_unit}}

Formulations:
- IBUGEL™ (Ibuprofen 5% w/w) | api=Ibuprofen 5 % w/w | comps: {{component_summary}}
- IBULEVE™ Speed Relief 5% Spray | api=Ibuprofen 5 % w/w | comps: {{component_summary}}
- Isopropyl alcohol solution (5% w/w) | api=Ibuprofen 5 % w/w | comps: {{component_summary}}
- Propylene glycol solution (5% w/w) | api=Ibuprofen 5 % w/w | comps: {{component_summary}}

[Attached mapping zoom for Figure 1A.]
```

### 7.4 Example output

**Reconstructed `MapResult` from real per-curve artifacts** at `outputs/gpt-extended-baseline/figure_curve_map.jsonl:7-10`. The stored artifact rows add downstream mapping metadata, so this block restores the raw schema shape expected from the model.

```json
{
  "mappings": [
    {
      "curve_id": "cluster_1",
      "curve_color": "black",
      "assigned_formulation_label": "IBULEVE™ Speed Relief 5% Spray",
      "evidence_from_legend": "",
      "rationale": "The black curve is associated with the spray due to the comparable endpoint values.",
      "confidence": 0.8
    },
    {
      "curve_id": "cluster_2",
      "curve_color": "gray",
      "assigned_formulation_label": "IBUGEL™ (Ibuprofen 5% w/w)",
      "evidence_from_legend": "",
      "rationale": "The gray curve represents a gel, indicated by its endpoint metrics consistent with IBUGEL™.",
      "confidence": 0.85
    },
    {
      "curve_id": "cluster_3",
      "curve_color": "green",
      "assigned_formulation_label": "Isopropyl alcohol solution (5% w/w)",
      "evidence_from_legend": "",
      "rationale": "The green curve corresponds to lower endpoint values, associating with isopropyl alcohol.",
      "confidence": 0.75
    },
    {
      "curve_id": "cluster_4",
      "curve_color": "gray",
      "assigned_formulation_label": "Propylene glycol solution (5% w/w)",
      "evidence_from_legend": "",
      "rationale": "Given the observed metrics, the gray curve also represents propylene glycol due to its prominent absorption characteristics.",
      "confidence": 0.7
    }
  ],
  "notes": ""
}
```

### 7.5 Caption suggestion

The prompt, constrained formulation label space, and curve-to-formulation assignments of the figure mapping stage.

## 8. Verification adjudication

### 8.1 Stage identity

- **Prompt definition:** `verification/llm_adjudicate.py:20-30`, `verification/llm_adjudicate.py:155-216`, `verification/llm_adjudicate.py:240-250`
- **Call site:** `verification/llm_adjudicate.py:252-264`
- **Prompt asset/version:** `verification.llm_adjudication` / `2026-04-03.v1`
- **Frozen-baseline models:** `gpt-4o-mini`; `claude-sonnet-4-6`
- **Structured output schema:** `AdjudicationVerdict`
- **Top-level fields:** `should_keep_strict`, `recommended_status`, `scope_bucket`, `target_api_ok`, `concentration_5pct_ww_ok`, `franz_ok`, `ivpt_ivrt_ok`, `amount_endpoint_ok`, `endpoint_time_ok`, `area_ok`, `confidence`, `rationale` (`verification/llm_adjudicate.py:33-45`)

### 8.2 Full prompt text

**System prompt** (`verification/llm_adjudicate.py:23-30`):

```text
You are a strict scientific adjudicator for a dermal ibuprofen evidence-mining pipeline. You are NOT doing open-ended extraction. You are reviewing pre-extracted records that are currently recoverable unresolved candidates under a strict scope: ibuprofen, 5% w/w, Franz diffusion cell, IVPT/IVRT, amount endpoint, endpoint time required. Use ONLY the supplied structured record fields and evidence packet. If evidence is missing or conflicting, prefer unresolved rather than verified. If the record is scientifically useful but outside the strict scope, recommend rejected and mark the scope bucket as useful_but_out_of_scope.
```

**User prompt** (`verification/llm_adjudicate.py:240-250`), with the evidence packet expanded from `verification/llm_adjudicate.py:188-216`:

```text
Review the following recoverable-unresolved candidate record and evidence packet. Decide whether it should likely remain unresolved, be rejected as out of scope, or be promoted to strict verified.

RECORD_ID: {{record.record_id}}
PAPER_ID: {{record.paper_id}}
DOI: {{record.doi}}
CANDIDATE_REASON: {{candidate_reason}}

PRIORITY_SCORE: {{priority_score}}
REVIEW_FOCUS: {{review_focus}}

RECORD_FIELDS
- route={{record.route}}
- original_status={{record.verification_status}}
- original_scope_bucket={{record.scope_bucket}}
- study_type={{record.study_type}}
- device={{record.device}}
- api_name={{record.formulation.api_name}}
- api_concentration_value={{record.formulation.api_concentration_value}}
- api_concentration_unit={{record.formulation.api_concentration_unit}}
- api_basis={{record.formulation.api_basis}}
- api_concentration_raw={{record.formulation.api_concentration_raw}}
- endpoint_kind={{primary_endpoint.kind_or_unknown}}
- endpoint_mean={{primary_endpoint.mean_or_none}}
- endpoint_sd={{primary_endpoint.sd_or_none}}
- endpoint_unit={{primary_endpoint.unit_or_empty}}
- endpoint_n_replicates={{primary_endpoint.n_replicates_or_none}}
- endpoint_time_h={{record.conditions.duration_h}}
- diffusion_area_cm2={{record.conditions.diffusion_area_cm2}}
- failure_reasons={{record.failure_reasons}}

EVIDENCE_ITEMS
{{evidence_item_lines_or_none}}

SOURCE_FRAGMENTS
{{source_fragment_lines_or_none}}
```

Each evidence item line is rendered exactly as:

```text
- field={{field_name}} modality={{modality}} locator={{locator_or_no_locator}} snippet={{snippet}}
```

### 8.3 Example input

**Constructed concise rendering of a real adjudication candidate.** Candidate identifiers and priority fields are from `outputs/gpt-extended-baseline/llm_adjudication.jsonl:1`; omitted evidence fragments are represented by slots because the adjudication output file does not cache the full prompt.

```text
RECORD_ID: record_c13a8cda365e
PAPER_ID: paper_b21c07f7ac33
DOI: 10.1007/s13346-022-01182-x
CANDIDATE_REASON: recoverable_unresolved:ambiguous_api_concentration

PRIORITY_SCORE: 15.5
REVIEW_FOCUS: api_concentration_basis

RECORD_FIELDS
- route=table
- original_status=unresolved
- original_scope_bucket=recoverable_unresolved
- api_concentration_raw={{source concentration text}}
- failure_reasons=['ambiguous_api_concentration', ...]

EVIDENCE_ITEMS
{{source-backed evidence lines}}

SOURCE_FRAGMENTS
{{selected source fragments}}
```

### 8.4 Example output

**Real output** from `outputs/gpt-extended-baseline/llm_adjudication.jsonl:1`.

```json
{
  "should_keep_strict": "no",
  "recommended_status": "unresolved",
  "scope_bucket": "recoverable_unresolved",
  "target_api_ok": "uncertain",
  "concentration_5pct_ww_ok": "no",
  "franz_ok": "uncertain",
  "ivpt_ivrt_ok": "yes",
  "amount_endpoint_ok": "yes",
  "endpoint_time_ok": "yes",
  "area_ok": "n_a",
  "confidence": 0.5,
  "rationale": "The record has ambiguous API concentration as it reports 0.5% w/v instead of the required 5% w/w. The original status indicates unresolved due to insufficient evidence and missing area. Also, it contains conflicting units (w/v instead of w/w for concentration) which complicates verification. Therefore, it is best to remain unresolved rather than promoting it to verified."
}
```

### 8.5 Caption suggestion

The prompt, unresolved evidence packet, and strict-scope recommendation of the verification-adjudication stage.

## 9. Document-metadata recovery

### 9.1 Stage identity

- **Prompt definition:** `corpus/extract_pdf_metadata.py:23-24`, `corpus/extract_pdf_metadata.py:40-52`, `corpus/extract_pdf_metadata.py:293-298`
- **Call site:** `corpus/extract_pdf_metadata.py:177-195`
- **Prompt asset/version:** `corpus.pdf_metadata` / `2026-05-10.v1`
- **Models:** this stage postdates the April frozen baseline; provider defaults are `gpt-4o-mini` and `claude-sonnet-4-6`
- **Structured output schema:** `PdfMetadataLLMResponse`
- **Top-level fields:** `doi`, `title`, `year`, `journal`, `authors`, `abstract` (`corpus/extract_pdf_metadata.py:68-78`)

### 9.2 Full prompt text

**System prompt** (`corpus/extract_pdf_metadata.py:40-52`):

```text
You are extracting bibliographic metadata from a scientific paper PDF.
Output strict JSON with these keys: doi, title, year, journal, authors, abstract.
Rules:
- doi: lowercase, no surrounding whitespace. Empty string if not found.
- title: as printed on the paper, no truncation.
- year: integer; null if not extractable.
- journal: full name if available, else publication venue.
- authors: list of strings, in order of appearance.
- abstract: the paper's abstract verbatim. Critical for downstream pipeline.
  If missing, return empty string (do not summarize).
- Do not include any text outside the JSON object.
```

**User prompt** (`corpus/extract_pdf_metadata.py:293-298`):

```text
PDF_PATH: {{pdf_path}}
Extract only bibliographic metadata from the following text from the first two PDF pages.

PDF_TEXT:
{{first_pages_text_truncated_to_24000_characters}}
```

### 9.3 Example input

**Real first-page content excerpt.** The source PDF path and first-page text are present in the real table-prompt cache at `outputs/v1.5_change_set_c_llm_cache/paper_067e8b4e5b8c_ab2378c3fa5b.json:9-16`; metadata extraction uses the same first-page PDF text but caps the combined first two pages at 24,000 characters.

```text
PDF_PATH: papers\uploaded_external\watkinson_2011_III.pdf
Extract only bibliographic metadata from the following text from the first two PDF pages.

PDF_TEXT:
Original Paper
Skin Pharmacol Physiol 2011;24:22–26
DOI: 10.1159/000315139
Optimisation of Cosolvent Concentration for Topical Drug Delivery III – Influence of Lipophilic Vehicles on Ibuprofen Permeation
R.M. Watkinson, R.H. Guy, G. Oliveira, J. Hadgraft, M.E. Lane
Abstract
Previously, we have reported the effects of water, ethanol, propylene glycol and various binary and ternary mixtures of these solvents on the permeation of ibuprofen in model membranes and in skin...
```

### 9.4 Example output

**Real metadata output** from `papers/uploaded_external/watkinson_2011_III.pdf.metadata.json:1-18`.

```json
{
  "doi": "10.1159/000315139",
  "title": "Optimisation of Cosolvent Concentration for Topical Drug Delivery III – Influence of Lipophilic Vehicles on Ibuprofen Permeation",
  "year": 2011,
  "journal": "Skin Pharmacology and Physiology",
  "authors": [
    "R.M. Watkinson",
    "R.H. Guy",
    "G. Oliveira",
    "J. Hadgraft",
    "M.E. Lane"
  ],
  "abstract": "Previously, we have reported the effects of water, ethanol, propylene glycol and various binary and ternary mixtures of these solvents on the permeation of ibuprofen in model membranes and in skin. The present study investigates the influence of lipophilic vehicles on the transport of ibuprofen in silicone membrane and in human skin. The permeation of ibuprofen was measured from mineral oil (MO), Miglyol 812 (MG) and binary mixtures of MO and MG. The solubility of ibuprofen was 5-fold higher in MG than in MO, however, the permeation of ibuprofen from the pure vehicles and combinations of both was comparable in silicone membrane. Additionally, there were no significant differences in skin permeation for MO and MG vehicles. When the permeation of various hydrophilic and lipophilic vehicles is considered, a trend between flux values for the model membrane and skin is evident (r2 = 0.71). The findings suggest that silicone membrane may provide information on qualitative trends in skin permeation for vehicles of diverse solubility and partition characteristics."
}
```

### 9.5 Caption suggestion

The prompt, first-page PDF text, and recovered bibliographic record of the document-metadata stage.

## 10. Stages that could not be located

None. All nine requested language-model stages were located. Figure triage contains two distinct LLM calls under one prompt asset: the normal call and a conditional calibration-curve retry.

## 11. Notes on prompt assembly

1. **Prompts are embedded in source modules.** They are not loaded from standalone prompt files. The pipeline fingerprints the defining modules and records asset IDs/versions in the manifest (`run_pipeline.py:71-100`).
2. **No separate developer-role messages were found.** Each call uses one system message and one user message. Vision calls represent the user content as an `input_text` item followed by one or more `input_image` items.
3. **Provider text is unchanged.** No stage-specific fixed prompt wording differs between OpenAI and Anthropic. The provider adapter preserves system/user content while changing the structured-output transport: OpenAI uses `responses.parse`; Anthropic uses `messages.parse` or, for nested schemas and grammar failures, a forced `emit_structured_response` tool call (`utils/llm_client.py:102-130`, `utils/llm_client.py:133-158`, `utils/llm_client.py:161-223`, `utils/llm_client.py:226-284`).
4. **Figure triage is conditionally two-pass.** If the semantic gate identifies a calibration curve, a second request adds the rejected figure/page, reason, endpoint hints, and alternate candidate pages before repeating the base triage instructions (`extractors/figure/triage.py:414-443`, `extractors/figure/triage.py:585-638`).
5. **Curve mapping has deterministic bypasses.** No LLM is called when triage/table labels are missing, when exactly one curve and one label permit an exact assignment, or when there are more curves than allowed labels (`extractors/figure/map_curves.py:168-249`). The prompt shown above applies only to the remaining constrained mapping cases.
6. **Text input is selected and capped before prompting.** Structured content is preferred; otherwise PDF pages are selected. Defaults are at most 24 structured blocks or 18 PDF pages and 32,000 total characters (`extractors/text/page_selection.py:379-413`).
7. **Router input is selected and capped.** Structured context is limited to 24 blocks and 26,000 characters; PDF fallback includes up to 12 pages and 26,000 characters (`detection/router.py:116-153`, `detection/router.py:218-254`).
8. **Table input is row- and character-capped before prompting.** HTML table parsing caps each table at 60 rows (`extractors/table/extractor.py:338-381`); structured windows default to 28,000 characters, while PDF fallback selects up to five pages and caps page text at 4,500 characters (`extractors/table/extractor.py:432-503`, `extractors/table/extractor.py:533-598`).
9. **Metadata input uses only the first two PDF pages.** Their extracted text is sliced to 24,000 characters in the user prompt (`corpus/extract_pdf_metadata.py:165-180`, `corpus/extract_pdf_metadata.py:229-248`, `corpus/extract_pdf_metadata.py:293-298`).
10. **Historical schema/version caveat.** Some frozen baseline JSONL outputs predate the live list-based endpoint schema. The examples above use a live-schema table cache where available and explicitly identify reconstructed examples when raw model responses were not stored.
