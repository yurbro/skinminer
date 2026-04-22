# E3 Claude Integration Workload Assessment

Date: 2026-04-11

## Verdict

Do not implement E3 in this pass. The work is larger than the `< 200 LOC` threshold and is likely above the `> 500 LOC` reporting threshold once OpenAI parity, Anthropic structured output, vision payload conversion, manifest compatibility, and documentation are included.

Estimated implementation size: 730-1,110 LOC.

Current environment finding: `anthropic` is not installed, and this repository has no tracked `requirements.txt` or equivalent dependency manifest.

## Current OpenAI Coupling

The pipeline has 8 direct `OpenAI(...).responses.parse(...)` call sites:

| Stage | File | Current structured schema | Vision input |
|---|---|---|---|
| LLM triage | `triage/llm_triage.py` | `LLMTriageResult` | no |
| Evidence routing | `detection/router.py` | `RouterLLMResponse` | no |
| Text extraction | `extractors/text/extract_fields.py` | `PaperExtraction` | no |
| Table extraction | `extractors/table/extractor.py` | `TableExtractionResult` | sometimes PDF page JPEGs |
| Figure triage | `extractors/figure/triage.py` | `FigureTriageResult` | yes, rendered page JPEGs |
| Figure VLM digitize | `extractors/figure/vlm_digitize.py` | `VLMFigureResult` | yes, subplot crop |
| Figure curve mapping | `extractors/figure/map_curves.py` | `MapResult` | yes, mapping crop |
| LLM adjudication | `verification/llm_adjudicate.py` | `AdjudicationVerdict` | no |

Supporting code that would also need updates:

| Area | File | Required change |
|---|---|---|
| CLI/provider selection | `run_pipeline.py` | add provider flags, pass provider into every LLM stage, include provider in resume signature |
| Run profiles | `configs/run_profiles.py` | optionally add Claude profile or provider-aware stage defaults |
| Runtime context | `schemas/models.py` | add provider/client settings or pass via `shared_state` |
| Manifest | `utils/manifest.py` | record `anthropic` SDK version and provider metadata |
| Long-run usage | `utils/long_run.py` | generalize OpenAI-specific usage helpers or add provider-normalized usage extraction |
| Documentation | `README.md`, `README.en.md` | required architecture update if implementation proceeds |

## Recommended Architecture

Use a thin generic LLM client abstraction, not per-stage minimal adapters.

Rationale:

- A direct minimal adapter duplicated across 8 call sites would have to reimplement schema parsing, retry behavior, usage accounting, and image conversion repeatedly.
- The current code assumes an OpenAI parsed response shape: `response.output_parsed` and OpenAI usage fields. Anthropic responses expose different content and usage shapes.
- The figure/table paths already mix text and image blocks. A central content-block normalizer avoids subtle stage-specific image bugs.
- Default OpenAI behavior must remain unchanged, otherwise E6/E7/E8/repro runs become hard to compare.

Proposed abstraction:

| Component | Estimated LOC | Notes |
|---|---:|---|
| `utils/llm_client.py` | 260-360 | provider enum, parsed-response wrapper, OpenAI adapter, Anthropic adapter, content block conversion, usage normalization |
| 8 stage refactors | 160-240 | replace direct `OpenAI` imports/calls with `parse_structured(...)` |
| `run_pipeline.py` provider plumbing | 120-180 | `--llm-provider`, provider in manifest/resume signature, stage detail wording |
| `utils/long_run.py` / `utils/manifest.py` | 50-90 | generic usage names plus Anthropic SDK version |
| Docs | 60-100 | root README Chinese + English |
| Smoke tests / fixtures | 80-140 | OpenAI parity smoke plus Claude text-only and vision dry run |
| Total | 730-1,110 | before a full E3 run |

## Structured Output Equivalent

Anthropic now supports structured outputs through `output_config.format` with `type: "json_schema"` and also documents Python SDK Pydantic integration via `client.messages.parse()`.

Recommended implementation path:

- Prefer native Anthropic structured outputs or Python SDK `messages.parse()` with the same Pydantic models currently passed as OpenAI `text_format`.
- Validate returned objects locally with the existing Pydantic models before returning a provider-neutral `output_parsed`.
- Keep retries for refusal, max-token truncation, SDK/API errors, and local Pydantic validation failures.
- Avoid relying only on plain prompt instructions or non-strict JSON text, because the pipeline currently depends on schema-stable downstream fields.

Compatibility risk:

- Current schemas use nested Pydantic models, `Literal`, list defaults, numeric bounds, and optional fields. Anthropic docs state SDK helpers transform unsupported constraints and then validate locally, so every stage schema needs a smoke test.
- Anthropic structured output can add first-request grammar compilation latency and has schema-complexity limits. Table and figure schemas are the highest-risk schemas.

Alternative:

- Strict tool use can enforce tool input schemas, but it is a poorer fit here because the pipeline needs direct extraction objects, not tool invocation side effects.

## Vision Input Differences

Current OpenAI payload shape:

```python
[
    {"type": "input_text", "text": "..."},
    {"type": "input_image", "image_url": "data:image/jpeg;base64,..."},
]
```

Anthropic equivalent shape:

```python
[
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "...",
        },
    },
    {"type": "text", "text": "..."},
]
```

Important differences:

- Anthropic expects image blocks as `type: image` with a `source` object, not OpenAI `input_image`.
- Data URLs must be split into `media_type` and raw base64 payload.
- Anthropic docs recommend placing images before text when possible. Current code places text first in figure/table prompts, so the adapter or stages should normalize ordering for Claude.
- Claude image requests have size and token-cost considerations. Current figure triage renders full PDF pages at 170 DPI, so E3 cost and latency may differ materially from GPT-4o-mini.

## OpenAI-Compatible Anthropic Endpoint

Anthropic documents an OpenAI SDK compatibility layer, but it targets OpenAI `chat.completions.create(...)`. This repository uses `client.responses.parse(...)` with Pydantic `text_format`, and Anthropic's compatibility docs state `response_format` is ignored.

Conclusion: the compatibility endpoint is not a safe drop-in for this codebase. It might help a separate proof of concept, but it does not remove the need for a structured-output adapter.

## Recommended Claude Model

For a new E3 run on 2026-04-11, use `claude-sonnet-4-6` if the goal is current high value per cost. Anthropic's model overview lists Claude Sonnet 4.6 as the best combination of speed and intelligence, with text/image input and vision support.

If the paper methodology must follow the original task note exactly, use the older Sonnet 4 family name specified there, for example `claude-sonnet-4-20250514`, and record the exact model ID returned by the API in the manifest.

## If Approved

Implementation should be split into two phases:

1. Provider abstraction and OpenAI parity only. Run a small OpenAI smoke test to prove default behavior is not broken.
2. Anthropic adapter plus Claude smoke runs. Start with text-only triage/router/extraction, then enable figure vision, then run full `outputs/experiment_E3_claude`.

Do not run a full E3 Claude experiment before a smoke run confirms:

- all 8 schemas parse successfully;
- usage accounting is populated;
- image payload conversion works for page images and crops;
- manifest/resume compatibility prevents mixing OpenAI and Claude intermediates.

## Sources Checked

- Anthropic structured outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Anthropic vision input: https://platform.claude.com/docs/en/build-with-claude/vision
- Anthropic model overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Anthropic OpenAI SDK compatibility: https://docs.anthropic.com/en/api/openai-sdk
