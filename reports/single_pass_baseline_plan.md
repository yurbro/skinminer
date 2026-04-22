# Single-Pass Baseline Preparation Plan

## Scope
- Annotation file: `outputs/gold_audit_set/round2/gold_set_round2_annotation.csv`
- Unique DOI count: `29`
- Execution is not performed in this preparation step. No LLM calls were made.
- Default input mode: local/source-cache article text plus source HTML table blocks when valid. Figure images are not attached in the default pass.

## Prompt Design

### System Prompt
```text
You are a pharmaceutical data extraction specialist. You read a complete scientific paper about dermal/transdermal drug delivery and extract all permeation/release experimental data records.

For each experiment reported in the paper, extract:
- Formulation: name, API (drug), API concentration, excipient composition
- Endpoint: type (cumulative amount / flux / Jss / permeability coefficient / percent released), value, unit, timepoint
- Conditions: device (Franz cell / IVPT / diffusion cell / other), membrane type and source, membrane thickness, receptor medium, dose type (finite/infinite), dose amount, diffusion area
- Evidence: specific table/figure/text section where the value and conditions come from

Rules:
1. Extract ALL formulations and ALL timepoints reported. Do not skip, summarize, average, or return only representative rows.
2. For a table with formulation rows and multiple timepoint columns, output one record per formulation x timepoint cell.
3. Only extract actual in vitro permeation/release experiments. Exclude formulation characterization, analytical method validation, stability, anti-inflammatory assays, cell assays, animal PK/PD, human dermatopharmacokinetic/tape-stripping, and clinical studies unless they directly report in vitro Franz/IVPT/release measurements.
4. Distinguish in vitro skin/membrane permeation from in vivo DPK or tape stripping. Only in vitro records are in scope.
5. Prefer table values over figure-digitized values when the same endpoint appears in both.
6. Do not infer missing numeric values. Use null for fields that are not explicitly reported.
7. Preserve the reported concentration basis. Do not convert % w/v to % w/w.
8. Include source evidence for every record. If the source context is ambiguous, mark confidence low and explain in notes.
9. Return only valid JSON matching the schema; no prose outside JSON.
```

### User Prompt Template
````text
Paper DOI: {doi}
Paper title: {title}

Full text extracted from local source:
```text
{full_text_content}
```

Structured tables extracted from source HTML, if available:
```text
{table_text_content}
```

Please extract all in vitro permeation/release data records from this paper. Return JSON matching this schema:
```json
{schema_json}
```
````

### Output Schema
```json
{
  "records": [
    {
      "formulation_label": "F1",
      "formulation_name": "optional descriptive name",
      "api_name": "ibuprofen",
      "api_concentration_value": 5,
      "api_concentration_unit": "%",
      "api_basis": "w/v",
      "api_concentration_raw": "5% w/v",
      "excipient_composition": [
        {
          "name": "propylene glycol",
          "concentration_value": 10,
          "concentration_unit": "%",
          "basis": "w/w",
          "raw": "10% w/w"
        }
      ],
      "endpoint_kind": "amount_per_area",
      "endpoint_value": 1142.4,
      "endpoint_unit": "ug/cm2",
      "endpoint_time": 72,
      "endpoint_time_unit": "h",
      "device": "Franz diffusion cell",
      "study_type": "in_vitro",
      "membrane_type": "porcine skin",
      "membrane_source": "porcine",
      "membrane_thickness_um": 500,
      "receptor_medium": "PBS pH 7.4",
      "dose_type": "infinite",
      "dose_amount": "infinite dose",
      "diffusion_area_cm2": 0.64,
      "source_evidence": "Table II, row F1, 72 h column",
      "confidence": 0.9,
      "notes": ""
    }
  ],
  "paper_scope": {
    "has_in_scope_ivpt_or_release": true,
    "scope_notes": ""
  }
}
```

## Token And Cost Estimate
- Static prompt/schema estimate per call: `~840` input tokens
- Total estimated input tokens: `~352,912`
- Total estimated output tokens: `~116,000`
- Pricing used for estimate: gpt-4o-mini text input `$0.15 / 1M`; text output `$0.60 / 1M`, checked against the OpenAI model page on 2026-04-20.
- Estimated input cost: `$0.0529`
- Estimated output cost: `$0.0696`
- Estimated total standard API cost: `$0.1225`
- Estimated Batch API cost if used: `$0.0613`

## Context Window Assessment
- gpt-4o-mini context window: `128k` tokens; maximum output: `16,384` tokens, checked against the OpenAI model page on 2026-04-20.
- No paper exceeds the `120k` input-token warning threshold under the default text+tables plan.
- No context-window split is required before the first run. Reserve output headroom by omitting duplicate HTML table appendices if any single paper approaches `110k` input tokens in the final script.

## Source Availability Notes
- `10.1007/s11095-024-03747-6`: local_pdf_is_js_or_challenge_page;no_full_text_extracted (planned source: `none`, est. input `919` tokens)
- `10.1016/j.ijpharm.2019.118975`: local_pdf_has_no_extractable_text;no_full_text_extracted (planned source: `none`, est. input `915` tokens)
- `10.1016/j.jpba.2019.04.040`: html_source_short_or_metadata_only;source_text_under_5k_chars (planned source: `html_cache:router_structured_sources`, est. input `1,920` tokens)

## Per-Paper Input Estimate
| DOI | Source | Pages | Text chars | Table chars | HTML tables | Est. input tokens | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `10.1002/14651858.cd001177.pub2` | pdf_text | 53 | 155,265 | 0 | 0 | 39,729 |  |
| `10.1186/s13065-022-00901-2` | pdf_text | 19 | 77,317 | 0 | 0 | 20,283 |  |
| `10.1039/d0ra00100g` | pdf_text | 15 | 72,401 | 0 | 0 | 19,020 |  |
| `10.1523/jneurosci.5741-07.2008` | html_cache:router_structured_sources |  | 71,257 | 0 | 0 | 18,747 |  |
| `10.1007/s11095-020-02887-9` | pdf_text | 15 | 66,484 | 0 | 0 | 17,558 |  |
| `10.1038/s41598-024-57883-5` | pdf_text | 12 | 59,074 | 0 | 0 | 15,700 |  |
| `10.1007/s13346-022-01182-x` | pdf_text | 16 | 56,321 | 0 | 0 | 14,999 |  |
| `10.1523/jneurosci.15-04-02768.1995` | pdf_text | 9 | 52,687 | 0 | 0 | 14,112 |  |
| `10.21203/rs.3.rs-3773667/v1` | pdf_text | 25 | 52,496 | 0 | 0 | 14,056 |  |
| `10.1172/jci2614` | pdf_text | 9 | 51,267 | 0 | 0 | 13,735 |  |
| `10.3390/molecules28207156` | pdf_text | 14 | 50,565 | 0 | 0 | 13,590 |  |
| `10.1038/s41598-020-74885-1` | pdf_text | 13 | 50,537 | 0 | 0 | 13,558 |  |
| `10.1208/s12249-013-9995-4` | html_cache:patcher_structured_sources |  | 46,473 | 3,094 | 8 | 13,324 |  |
| `10.1371/journal.pone.0118536` | pdf_text | 14 | 45,525 | 0 | 0 | 12,306 |  |
| `10.1016/j.ejpb.2020.05.013` | pdf_text | 22 | 42,935 | 0 | 0 | 11,676 |  |
| `10.3390/membranes13030355` | pdf_text | 13 | 42,123 | 0 | 0 | 11,455 |  |
| `10.18433/j3160b` | pdf_text | 11 | 40,016 | 0 | 0 | 10,924 |  |
| `10.1208/s12249-019-1481-1` | pdf_text | 9 | 38,995 | 0 | 0 | 10,670 |  |
| `10.1007/s11095-008-9785-y` | pdf_text | 29 | 37,495 | 0 | 0 | 10,292 |  |
| `10.1248/cpb.c21-00033` | pdf_text | 7 | 36,917 | 0 | 0 | 10,157 |  |
| `10.1021/acs.molpharmaceut.0c00720` | pdf_text | 8 | 31,774 | 0 | 0 | 8,857 |  |
| `10.1016/j.ijpharm.2016.03.043` | pdf_text | 16 | 29,002 | 0 | 0 | 8,178 |  |
| `10.1186/2050-6511-13-5` | pdf_text | 7 | 28,853 | 0 | 0 | 8,138 |  |
| `10.1208/s12249-015-0474-y` | pdf_text | 7 | 28,856 | 0 | 0 | 8,134 |  |
| `10.1248/bpb.b19-00221` | pdf_text | 5 | 20,967 | 0 | 0 | 6,161 |  |
| `10.1038/nature18615` | html_cache:patcher_structured_sources |  | 11,306 | 236 | 1 | 3,799 |  |
| `10.1016/j.jpba.2019.04.040` | html_cache:router_structured_sources |  | 3,272 | 774 | 5 | 1,920 | html_source_short_or_metadata_only;source_text_under_5k_chars |
| `10.1007/s11095-024-03747-6` | none | 2 | 0 | 0 | 0 | 919 | local_pdf_is_js_or_challenge_page;no_full_text_extracted |
| `10.1016/j.ijpharm.2019.118975` | none | 1 | 0 | 0 | 0 | 915 | local_pdf_has_no_extractable_text;no_full_text_extracted |

## Recommended Execution Guardrails
- Use `gpt-4o-mini` for parity with the GPT modular baseline.
- Use one structured JSON-output call per DOI.
- Do not use pipeline-extracted records as model input; only local/source-cache article text and raw source tables should be included to avoid architectural contamination.
- Do not attach figure images in the first pass. Add figure images only as a second ablation if text+tables underperforms on figure-only gold cases.
- For source-poor papers, emit `records: []` only if the source packet genuinely lacks extractable article content; otherwise fix the source before running.
- Persist raw responses to `outputs/experiment_single_pass/single_pass_results.jsonl`, then evaluate against Round2 gold by DOI + formulation label + endpoint time.
