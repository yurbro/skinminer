# SkinMiner Methodology Audit — 2026-05-15

## 0. Primary Question Resolution

SkinMiner does **not** implement an LLM-driven Query Expansion step in the live pipeline. I found no corpus-build module that asks an LLM to generate synonyms, reformulate user queries, or expand search strings before Europe PMC retrieval. The live implementation instead builds Boolean search strings from a static registry of `QueryProfile` definitions in `corpus/query_profiles.py`, where `build_epmc_query` combines fixed drug, permeability, and dermal term lists into a deterministic query string (`corpus/query_profiles.py:29-46`, `corpus/query_profiles.py:59-99`). At runtime, `run_pipeline.py` selects the named profile supplied by `--query-profile`, uses that profile query by default, and lets an explicit `--query` string override only the query text while still retaining the selected profile name in the source label (`run_pipeline.py:587-593`, `run_pipeline.py:787-798`). Therefore, the paper should describe §2.1.2 as having **two** live LLM-facing functions in the ordinary corpus pipeline—LLM triage and route detection—not three with Query Expansion.

## 1. §2.1.1 Pipeline structure layer

### corpus/build_epmc.py

**One-line purpose.** Retrieves a Europe PMC corpus deterministically from a supplied query and normalizes the returned metadata into a reproducible tabular seed set. Reviewed in full: `corpus/build_epmc.py:1-138`.

**Algorithm summary.** The module pages through Europe PMC with cursor-based pagination, requesting the `core` result type until the API returns no next cursor or the configured maximum record count is reached. It maps each API hit into a normalized metadata row, standardizes title and abstract whitespace, lowercases DOI strings, and deduplicates first by DOI and then by title-year pairs. It finally writes either CSV or JSONL output through the caller-facing helper. This stage is fully deterministic once the query and Europe PMC response stream are fixed (`corpus/build_epmc.py:28-89`, `corpus/build_epmc.py:103-138`).

**Paper-relevant specifics.** The default page size is `1000`, the default maximum is `50_000` records, and the client sleeps `0.2` seconds between requests (`corpus/build_epmc.py:13-23`, `corpus/build_epmc.py:28-76`). Persisted seed fields include `source`, `id`, `pmid`, `pmcid`, `doi`, `title`, `abstract`, `year`, `journal`, `authors`, `url`, and `query_used` (`corpus/build_epmc.py:46-63`). No LLM call occurs here.

**What is NOT obvious from README.** The deduplication order matters: DOI duplicates are removed before title-year duplicates, so papers without stable identifiers still receive a second deterministic collapse pass (`corpus/build_epmc.py:82-89`). The module also stores the exact query string used for each row, which makes later corpus provenance auditable without reconstructing CLI arguments (`corpus/build_epmc.py:46-63`).

### corpus/query_profiles.py

**One-line purpose.** Defines the static Europe PMC query registry used by corpus building. Reviewed in full: `corpus/query_profiles.py:1-99`.

**Algorithm summary.** The file declares a small typed profile model and a helper that constructs Boolean Europe PMC syntax from fixed term lists. Each profile stores its name, version, description, and precomputed query string, and lookup is performed against a registry keyed by profile name. The default profile is `ibuprofen_dermal_oa_v1`. The module is a configuration registry, not an adaptive query-generation system (`corpus/query_profiles.py:12-26`, `corpus/query_profiles.py:29-46`, `corpus/query_profiles.py:59-99`).

**Paper-relevant specifics.** The registry version is `2026-03-28.v1`; the two live profiles are `ibuprofen_dermal_oa_v1` and `ibuprofen_dermal_franz_focus_v1` (`corpus/query_profiles.py:9`, `corpus/query_profiles.py:59-83`). Drug terms are scoped to `TITLE` or `ABSTRACT`, while the permeability and dermal groups are combined with grouped `OR` clauses and then joined by `AND` (`corpus/query_profiles.py:29-46`).

**What is NOT obvious from README.** “Query profile” means a frozen deterministic configuration, not a prompt-backed LLM feature. The focused profile swaps only the permeability-term family for a Franz-cell-oriented set; it does not learn or infer new synonyms at runtime (`corpus/query_profiles.py:48-83`).

### corpus/extract_pdf_metadata.py

**One-line purpose.** Converts user-supplied PDFs into corpus-compatible metadata rows when the pipeline starts from local files rather than a bibliographic seed set. Reviewed in full: `corpus/extract_pdf_metadata.py:1-387`.

**Algorithm summary.** The module hashes each PDF, reads only its first two pages, and asks a structured LLM stage to infer bibliographic metadata when text is available. It writes and reuses a sibling metadata cache, applies user-provided DOI or title hints when present, and falls back to deterministic placeholder metadata when no text can be extracted or the LLM output is unusable. The resulting rows are shaped to match corpus records so later stages can proceed without a special-case schema. This is a PDF-ingest support path rather than part of Europe PMC query construction (`corpus/extract_pdf_metadata.py:102-226`, `corpus/extract_pdf_metadata.py:229-298`, `corpus/extract_pdf_metadata.py:337-387`).

**Paper-relevant specifics.** The structured prompt asset is `corpus.pdf_metadata` at version `2026-05-10.v1`; the extraction window is the first `2` PDF pages, capped at `24_000` characters (`corpus/extract_pdf_metadata.py:23-24`, `corpus/extract_pdf_metadata.py:165`, `corpus/extract_pdf_metadata.py:229-248`, `corpus/extract_pdf_metadata.py:293-298`). Local PDF rows carry `query_used="user_upload_pdf"` (`corpus/extract_pdf_metadata.py:251-280`).

**What is NOT obvious from README.** Invalid non-timeout LLM metadata does not crash the ingest path; it falls back to synthetic metadata, including a SHA1-derived surrogate DOI when needed. Timeout failures are treated differently and are re-raised after retries (`corpus/extract_pdf_metadata.py:102-226`, `corpus/extract_pdf_metadata.py:337-387`).

### access/resolve_content.py

**One-line purpose.** Resolves each bibliographic record to the best available open-access content handle for downstream extraction. Reviewed in full: `access/resolve_content.py:1-325`.

**Algorithm summary.** The resolver first checks seed-provided PDF URLs, then Europe PMC full-text links, and finally Unpaywall candidates. It ranks available sources by preferred content format, downloads only when configured to do so, and records whether a source was resolved, downloaded, unresolved, or errored. A retry wrapper handles transient HTTP failures. The output is a normalized `ContentAccess` object that lets later stages choose structured XML/HTML or PDF content consistently (`access/resolve_content.py:23-57`, `access/resolve_content.py:139-219`, `access/resolve_content.py:221-325`).

**Paper-relevant specifics.** Retryable status codes are `408`, `425`, `429`, `500`, `502`, `503`, and `504`, with up to `4` attempts (`access/resolve_content.py:23-57`). Resolution preference supports `pmc_xml`, `html`, and `pdf`, and the legacy PDF path can be materialized even when a structured source is preferred (`access/resolve_content.py:139-219`).

**What is NOT obvious from README.** The resolver is not simply “download a PDF if available.” It can intentionally preserve structured sources as primary content while still auto-producing a PDF for figure and older extractor paths when `require_legacy_pdf` is enabled (`access/resolve_content.py:190-205`).

### access/content_strategy.py

**One-line purpose.** Encodes the format preference policy that separates structured-first text/table routing from PDF-first figure handling. Reviewed in full: `access/content_strategy.py:1-67`.

**Algorithm summary.** The module exposes a small immutable strategy object and a builder for the live default strategy. The default config prefers structured content for routing, text extraction, and table extraction, while preserving PDF-image handling for figures. It also controls whether primary content is eagerly downloaded and whether PDFs are materialized automatically for legacy consumers. The strategy therefore defines modality boundaries before any extractor executes (`access/content_strategy.py:8-19`, `access/content_strategy.py:37-67`).

**Paper-relevant specifics.** The live defaults are `structured_first=True` for routing/text/table, `figure_mode="pdf_image"`, `eager_download_primary=False`, and `auto_download_pdf_for_legacy=True` (`access/content_strategy.py:8-19`, `access/content_strategy.py:37-67`).

**What is NOT obvious from README.** The figure path intentionally remains PDF-image-based even while text and tables move to XML/HTML when available. This asymmetry is an explicit architecture choice, not an accidental fallback (`access/content_strategy.py:8-19`, `access/content_strategy.py:37-67`).

## 2. §2.1.2 LLM Orchestrator

### utils/llm_client.py

**One-line purpose.** Provides the provider-neutral structured-response seam used by the live LLM stages. Reviewed in full: `utils/llm_client.py:1-355`.

**Algorithm summary.** The module normalizes provider selection, model defaults, timeout/retry behavior, and structured parsing behind a single `parse_structured` interface. Callers pass a Pydantic schema through `text_format`, and the helper returns parsed structured output plus provider usage metadata. It handles OpenAI and Anthropic routing internally, so extractor modules can express only task prompts and schemas. This is the central abstraction that keeps LLM-facing stages implementation-consistent (`utils/llm_client.py:16-60`, `utils/llm_client.py:102-355`).

**Paper-relevant specifics.** The shared entry point is `parse_structured` at `utils/llm_client.py:102-130`. Structured stages provide typed `text_format` classes rather than free-form JSON parsing in module code (`utils/llm_client.py:102-355`).

**What is NOT obvious from README.** The current live system has nine production structured LLM stages, not eight: eight direct `parse_structured` call sites plus the PDF metadata stage, which defaults its injectable client to `parse_structured` (`corpus/extract_pdf_metadata.py:165-195`, `triage/llm_triage.py:102-110`, `detection/router.py:523-531`, `extractors/text/extract_fields.py:129-137`, `extractors/table/extractor.py:728-736`, `extractors/figure/triage.py:500-508`, `extractors/figure/vlm_digitize.py:298-306`, `extractors/figure/map_curves.py:303-311`, `verification/llm_adjudicate.py:255-263`).

### triage/rule_filter.py

**One-line purpose.** Performs deterministic high-recall corpus triage before any LLM classification. Reviewed in full: `triage/rule_filter.py:1-79`.

**Algorithm summary.** The rule filter concatenates title and abstract, lowercases the text, and evaluates three deterministic checks: an exact ibuprofen mention, at least one permissive inclusion pattern, and absence of exclusion patterns. Records that pass are labeled relevant and given heuristic hints; failures are labeled not relevant and receive exclusion reasons. The module is deliberately cheap and conservative, reducing the LLM workload without making final nuanced relevance judgments (`triage/rule_filter.py:8-28`, `triage/rule_filter.py:55-79`).

**Paper-relevant specifics.** Pass patterns include terms related to permeation, diffusion, topical delivery, Franz cells, IVPT, and release, while exclusions cover clinical trials, oral dosing, toxicity, and several unrelated experimental contexts (`triage/rule_filter.py:8-28`). The deterministic output confidence is `0.8` for rule-pass rows and `0.2` for rule-fail rows (`triage/rule_filter.py:55-79`).

**What is NOT obvious from README.** The first-stage gate is not abstract-only; it evaluates `title + abstract`. It also encodes both positive hints and negative exclusions, so some records can fail despite containing otherwise relevant vocabulary (`triage/rule_filter.py:55-79`).

### triage/llm_triage.py

**One-line purpose.** Uses a structured LLM classifier to refine relevance decisions after deterministic rule triage. Reviewed in full: `triage/llm_triage.py:1-173`.

**Algorithm summary.** The module builds a user prompt from the candidate title and a truncated abstract, sends it through the shared structured client, and validates the result against `LLMTriageResult`. It retries malformed or failed calls up to the configured limit and emits a parked unresolved-style fallback when attempts are exhausted. The LLM therefore handles semantic relevance, while the rule filter handles cheap lexical screening. The stage persists confidence, rationale, and extraction hints for later routing (`triage/llm_triage.py:20-35`, `triage/llm_triage.py:82-154`).

**Paper-relevant specifics.** The LLM sees the title and an abstract truncated to `2000` characters; it outputs `relevant`, `confidence`, `rationale`, and `extraction_hints` fields through `LLMTriageResult` (`triage/llm_triage.py:20-35`, `triage/llm_triage.py:90-110`). Exhausted retries produce a parked `not_relevant` result with confidence `0.0` rather than silently accepting the record (`triage/llm_triage.py:139-154`).

**What is NOT obvious from README.** Even though the system prompt says to judge from bibliographic evidence only, the stage still receives both title and abstract, not the abstract in isolation. The fallback path deliberately prevents malformed LLM output from leaking into later extraction stages (`triage/llm_triage.py:33-35`, `triage/llm_triage.py:139-154`).

### triage/prompts.py

**One-line purpose.** Defines the frozen triage prompt identity and the triage system instruction text. Reviewed in full: `triage/prompts.py:1-12`.

**Algorithm summary.** The module stores the asset identifier, prompt version, and concise system prompt used by the LLM triage stage. The prompt constrains the model to title-and-abstract evidence and asks whether the study is relevant to topical or transdermal ibuprofen permeation. It is imported by `run_pipeline.py` for manifest tracking and by `triage/llm_triage.py` for execution. The prompt is source-embedded rather than loaded from a separate asset file (`triage/prompts.py:1-12`, `run_pipeline.py:44`, `run_pipeline.py:91-100`).

**Paper-relevant specifics.** The asset ID is `triage.abstract_relevance`; the live version is `2026-03-28.v1` (`triage/prompts.py:1-2`). The system prompt explicitly limits evidence to title and abstract (`triage/prompts.py:4-12`).

**What is NOT obvious from README.** The “frozen prompt asset” is not a standalone file under a prompt registry directory in the live repo; it is an in-code definition whose source file is fingerprinted by the pipeline manifest (`triage/prompts.py:1-12`, `run_pipeline.py:71-100`).

### detection/router.py

**One-line purpose.** Assigns evidence routes so each relevant paper is sent to the most suitable downstream modality path. Reviewed in full: `detection/router.py:1-636`.

**Algorithm summary.** The router first builds a structured-first document from PMC XML or HTML when available and falls back to selected PDF pages otherwise. It extracts evidence anchors about Franz-cell context, endpoint mentions, and formulation carriers, then asks a structured LLM to summarize route signals. Deterministic post-processing converts those signals into one of the canonical route labels and falls back to heuristic routing when the LLM path fails. Papers with insufficient, contradictory, or unusable evidence become `unresolved` instead of being forced into a modality (`detection/router.py:116-254`, `detection/router.py:273-394`, `detection/router.py:397-434`, `detection/router.py:489-611`).

**Paper-relevant specifics.** The live prompt asset is `routing.structured_first` version `2026-03-28.v1` (`detection/router.py:25-26`). Router inputs can include first structured blocks plus scored context, with a `26_000` character cap; PDF fallback uses at most `2` selected pages (`detection/router.py:116-153`, `detection/router.py:218-254`). Canonical route labels are `text`, `table`, `figure`, `mixed`, and `unresolved` (`schemas/models.py:292-306`).

**What is NOT obvious from README.** The router is not purely LLM-driven. It blocks JavaScript walls, paywalls, and CAPTCHA-like content before prompting, and it has a deterministic heuristic fallback that can still route papers when the structured LLM path is unavailable or malformed (`detection/router.py:52-66`, `detection/router.py:208-215`, `detection/router.py:362-394`, `detection/router.py:489-611`).

## 3. §2.1.3.1 Text Agent

### extractors/text/extractor.py

**One-line purpose.** Orchestrates the text extraction path for papers routed to `text` or `mixed`. Reviewed in full: `extractors/text/extractor.py:1-192`.

**Algorithm summary.** The module selects only route-compatible papers, obtains a text window from the page-selection layer, runs structured field extraction, and normalizes each extracted row into canonical records. It writes raw and normalized outputs while preserving failure states when source text cannot be obtained. The orchestrator therefore separates document-window construction, LLM extraction, and schema normalization into distinct substeps. It does not process table-only or figure-only route decisions (`extractors/text/extractor.py:21-37`, `extractors/text/extractor.py:40-139`).

**Paper-relevant specifics.** The live gate is `route in {"text", "mixed"}` (`extractors/text/extractor.py:21-37`). Source-access failures are surfaced as `source_error` raw outputs rather than swallowed (`extractors/text/extractor.py:40-139`).

**What is NOT obvious from README.** The text agent is a wrapper over three narrower modules rather than a monolith: window selection, structured LLM extraction, and deterministic normalization are each isolated (`extractors/text/extractor.py:40-139`).

### extractors/text/extract_fields.py

**One-line purpose.** Extracts structured formulation and endpoint fields from the selected textual evidence window. Reviewed in full: `extractors/text/extract_fields.py:1-164`.

**Algorithm summary.** The module defines a constrained `PaperExtraction` schema and builds a task prompt that asks the LLM for formulation, condition, and endpoint evidence. It submits the prompt through the shared structured client, retries on failure, and limits the number of returned records to keep one paper from exploding into uncontrolled candidates. The prompt asks for explicit support rather than implicit completion. Downstream normalization transforms the result into canonical records (`extractors/text/extract_fields.py:17-18`, `extractors/text/extract_fields.py:40-85`, `extractors/text/extract_fields.py:104-164`).

**Paper-relevant specifics.** The prompt asset is `extractors.text.structured_fields` version `2026-04-11.v1`; `PaperExtraction` returns at most `5` records (`extractors/text/extract_fields.py:17-18`, `extractors/text/extract_fields.py:79-85`). The prompt specifically requests explicit condition and excipient evidence (`extractors/text/extract_fields.py:104-123`).

**What is NOT obvious from README.** The text path is intentionally evidence-sparse rather than completionist: if a formulation fact is not present in the selected window, the prompt tells the model not to invent it (`extractors/text/extract_fields.py:104-123`).

### extractors/text/normalize_fields.py

**One-line purpose.** Converts LLM-extracted text rows into canonical records with normalized endpoints, conditions, and evidence provenance. Reviewed in full: `extractors/text/normalize_fields.py:1-170`.

**Algorithm summary.** The normalizer infers endpoint kind from extracted labels and units, converts compatible cumulative amount measurements into per-area units when area is known, and maps raw textual fields into the shared record schema. It constructs evidence items and provenance alongside normalized values so later verification can inspect support. The output is deterministic given the structured LLM row. This module is the text agent’s bridge from task-specific extraction to global schema (`extractors/text/normalize_fields.py:23-38`, `extractors/text/normalize_fields.py:64-170`).

**Paper-relevant specifics.** Endpoint normalization can convert total amount to `ug/cm^2` when area is present, and evidence is recorded alongside fields such as endpoint, area, device, and formulation (`extractors/text/normalize_fields.py:64-170`).

**What is NOT obvious from README.** A text result can become quantitatively usable only after deterministic area-aware unit conversion; the LLM is not asked to perform that final canonicalization itself (`extractors/text/normalize_fields.py:64-170`).

### extractors/text/page_selection.py

**One-line purpose.** Builds the evidence window that the text extractor is allowed to read. Reviewed in full: `extractors/text/page_selection.py:1-413`.

**Algorithm summary.** The selector prefers structured XML or HTML blocks and falls back to PDF pages only when structured content is unavailable. It scores local text around endpoint, drug, and method anchors, includes nearby context, and assembles a bounded window for the LLM. First-block coverage is preserved so important document-level context is not lost when later anchors dominate the score. The same design limits token cost while retaining reviewer-relevant evidence around likely extraction sites (`extractors/text/page_selection.py:208-305`, `extractors/text/page_selection.py:309-413`).

**Paper-relevant specifics.** Structured selection uses up to `24` blocks and always includes the first `4`; PDF fallback uses up to `18` pages and always includes the first `2`. Anchor neighborhoods span `±2` pages or blocks, and the final text window is capped at `32_000` characters (`extractors/text/page_selection.py:208-305`, `extractors/text/page_selection.py:309-413`).

**What is NOT obvious from README.** The text agent is structured-first even when PDF files exist, so many extractions operate on XML/HTML blocks rather than OCR-like page text. The first-block inclusion rule is a subtle guard against losing title/abstract/method context during relevance-biased windowing (`extractors/text/page_selection.py:208-305`, `extractors/text/page_selection.py:379-413`).

## 4. §2.1.3.2 Table Agent

### extractors/table/extractor.py

**One-line purpose.** Extracts tabular formulation and endpoint records from structured or PDF table evidence and normalizes them into canonical records. Reviewed in full: `extractors/table/extractor.py:1-1763`.

**Algorithm summary.** The table agent first builds structured table windows from XML/HTML when possible and falls back to PDF-derived windows otherwise. It prompts a structured LLM over the bounded table context, then applies deterministic repairs and expansion logic for known table layouts, including multi-timepoint and wide-table cases. Raw rows are converted into canonical records with normalized endpoints, conditions, provenance, and truncation metadata. The module therefore combines LLM interpretation with deterministic post-processing to preserve dense numerical evidence (`extractors/table/extractor.py:275-381`, `extractors/table/extractor.py:432-598`, `extractors/table/extractor.py:643-736`, `extractors/table/extractor.py:896-1237`, `extractors/table/extractor.py:1392-1642`).

**Paper-relevant specifics.** The live prompt asset is `extractors.table.structured_tables`, but the live version is `2026-05-10.change-set-c`, not the older `2026-04-11.v1` named in the task handoff (`extractors/table/extractor.py:53-54`). HTML extraction enforces a `60`-row cap; truncation markers and the boolean `table_truncated` are propagated into raw outputs and provenance metadata (`extractors/table/extractor.py:338-381`, `extractors/table/extractor.py:439-503`, `extractors/table/extractor.py:1554-1564`, `extractors/table/extractor.py:1631-1642`). PDF fallback reads at most `5` candidate pages and caps page text at `4500` characters per page (`extractors/table/extractor.py:533-598`).

**What is NOT obvious from README.** XML table extraction has a separate `18`-row row-reader limit without the same explicit truncation flag used by the HTML path (`extractors/table/extractor.py:275-291`). The module also contains paper-specific deterministic recovery code for Kallakunta and Watkinson table shapes, which materially changes extracted record counts after the LLM step (`extractors/table/extractor.py:896-1147`).

## 5. §2.1.3.3 Figure Agent

### extractors/figure/triage.py

**One-line purpose.** Identifies whether a routed paper contains a usable target figure and selects the most relevant subplot context. Reviewed in full: `extractors/figure/triage.py:1-777`.

**Algorithm summary.** The module renders candidate PDF pages, scores them with text and graphics heuristics, and presents the strongest candidates to a structured VLM triage step. The VLM returns semantic signals about target plots, candidate subplots, axes, and labels. A deterministic semantic gate rejects calibration-like plots and can trigger a second-pass retry when the first candidate is suspicious. The result narrows the figure path before any numeric digitization begins (`extractors/figure/triage.py:193-268`, `extractors/figure/triage.py:414-443`, `extractors/figure/triage.py:478-725`).

**Paper-relevant specifics.** The prompt asset is `extractors.figure.triage` version `2026-04-06.v1`; the structured output schema is `FigureTriageResult` (`extractors/figure/triage.py:23-24`, `extractors/figure/triage.py:52-80`, `extractors/figure/triage.py:500-508`). The semantic retry path is specifically designed to avoid mistaking calibration curves for permeation plots (`extractors/figure/triage.py:414-443`, `extractors/figure/triage.py:577-725`).

**What is NOT obvious from README.** Figure routing is not a single-shot VLM judgment. A deterministic post-VLM gate can override the first-pass result and request another candidate, which makes the figure path more conservative than a simple “ask model, digitize answer” narrative suggests (`extractors/figure/triage.py:414-443`, `extractors/figure/triage.py:577-725`).

### extractors/figure/digitize.py

**One-line purpose.** Performs computer-vision-only curve extraction from locked figure regions. Reviewed in full: `extractors/figure/digitize.py:1-1130`.

**Algorithm summary.** The module uses OpenCV-style image processing to identify candidate plot boxes, threshold masks, edge pixels, and clusterable curves. It estimates axes, rejects unsupported contexts, and transforms pixel traces into endpoint candidates when the plot geometry is sufficiently grounded. No LLM or VLM call occurs in this stage. Failure states are explicit, so downstream reconciliation can distinguish missing context from low-quality curves (`extractors/figure/digitize.py:17-18`, `extractors/figure/digitize.py:253-346`, `extractors/figure/digitize.py:672-760`, `extractors/figure/digitize.py:761-1119`).

**Paper-relevant specifics.** The minimum edge-pixel count is `800`, and the minimum cluster size is `250` points (`extractors/figure/digitize.py:17-18`). Percent-only y-axes are intentionally not digitized into quantitative endpoints (`extractors/figure/digitize.py:742-760`).

**What is NOT obvious from README.** The CV branch can fail long before curve fitting because it refuses contexts without grounded axes or with inadequate edge support; this is a quality-control design rather than a generic image extraction failure (`extractors/figure/digitize.py:761-1119`).

### extractors/figure/vlm_digitize.py

**One-line purpose.** Extracts direct VLM readings from a locked target subplot as a companion path to computer-vision digitization. Reviewed in full: `extractors/figure/vlm_digitize.py:1-456`.

**Algorithm summary.** The module runs only after the figure triage stage has produced a locked, direct subplot crop. It asks a VLM for visually grounded readings, preferring labels visible within the figure itself and using source-label context only as a fallback. The prompt forbids invention of new membrane, receptor, or dose conditions from the crop. The resulting readings later participate in reconciliation rather than replacing the rest of the figure pipeline by default (`extractors/figure/vlm_digitize.py:95-105`, `extractors/figure/vlm_digitize.py:247-306`, `extractors/figure/vlm_digitize.py:273-286`).

**Paper-relevant specifics.** The prompt asset is `extractors.figure.vlm_digitize` version `2026-04-11.v1`; the schema is `VLMFigureResult` (`extractors/figure/vlm_digitize.py:23-24`, `extractors/figure/vlm_digitize.py:298-306`). Eligibility requires an `ok` endpoint status, `candidate_tier="triage_primary"`, no subplot-lock failure, and an existing crop (`extractors/figure/vlm_digitize.py:95-105`, `extractors/figure/vlm_digitize.py:247-271`).

**What is NOT obvious from README.** The VLM path is deliberately narrower than “read any figure.” It is crop-locked and evidence-constrained, so it cannot freely hallucinate figure conditions from table context (`extractors/figure/vlm_digitize.py:95-105`, `extractors/figure/vlm_digitize.py:273-286`).

### extractors/figure/map_curves.py

**One-line purpose.** Maps digitized figure curves onto known formulation labels when a plot contains multiple candidate curves. Reviewed in full: `extractors/figure/map_curves.py:1-371`.

**Algorithm summary.** The mapper groups endpoints by paper, determines the allowed formulation-label set, and auto-maps the trivial one-curve/one-label case. For harder plots, it sends a zoomed image plus restricted label candidates to a structured VLM mapping call. It rejects underconstrained cases where there are more curves than admissible labels. The output is a grounded label assignment rather than a new formulation-generation step (`extractors/figure/map_curves.py:139-371`).

**Paper-relevant specifics.** The prompt asset is `extractors.figure.curve_map` version `2026-03-28.v1`; the schema is `MapResult` (`extractors/figure/map_curves.py:21-22`, `extractors/figure/map_curves.py:303-311`). A single curve plus a single label is auto-mapped at confidence `0.88`; curve counts exceeding label counts return `underconstrained_labels` (`extractors/figure/map_curves.py:165-249`).

**What is NOT obvious from README.** This stage is not a general semantic figure interpreter. It is a constrained assignment problem over labels already known elsewhere in the pipeline, which is why ambiguous label cardinality blocks mapping rather than forcing a guess (`extractors/figure/map_curves.py:139-249`).

### extractors/figure/build_records.py

**One-line purpose.** Reconciles figure triage, CV digitization, VLM readings, and label mapping into canonical figure-derived records. Reviewed in full: `extractors/figure/build_records.py:1-945`.

**Algorithm summary.** The orchestrator runs figure triage, CV digitization, optional VLM direct reading, VLM curve mapping, and then a reconciliation step that chooses how to build final records. It accepts CV and VLM agreement when their numeric estimates are close, permits a `vlm_only` route when no CV value survives but the VLM reading remains grounded, and preserves explicit provenance for the chosen path. Figure conditions are derived only from figure-grounded hints rather than being blindly copied from table context. The result is a multimodal but auditable record-construction path (`extractors/figure/build_records.py:303-340`, `extractors/figure/build_records.py:429-735`, `extractors/figure/build_records.py:754-767`).

**Paper-relevant specifics.** CV and VLM values are treated as agreeing when relative difference is at most `15%` (`extractors/figure/build_records.py:590-735`). The `vlm_only` path is available when a grounded VLM candidate exists and no CV candidate survives, while a special `vlm_retry_cv_disagreement` path requires calibration-retry context, one source label, readable grounding, and confidence of at least `0.85` (`extractors/figure/build_records.py:572-587`, `extractors/figure/build_records.py:644-725`).

**What is NOT obvious from README.** The figure builder explicitly avoids copying ungrounded table conditions into figure records; it only preserves conditions that can be supported from figure context or restricted source metadata (`extractors/figure/build_records.py:303-340`). This is an important anti-contamination safeguard that a high-level multimodal summary would miss.

## 6. §2.1.4 Assembly and verification

### schemas/models.py

**One-line purpose.** Defines the canonical typed schemas shared across extraction, assembly, verification, and run outputs. Reviewed in full: `schemas/models.py:1-341`.

**Algorithm summary.** The file declares typed models for formulation data, conditions, endpoints, evidence items, provenance, patches, content access, route decisions, and canonical records. Endpoint handling is now list-based, with deterministic priority ordering for selecting a primary endpoint. Record objects carry both scientific content and downstream audit fields such as support rate, verification status, scope bucket, failure reasons, and source notes. The schema therefore acts as the contract tying modality-specific extraction to shared verification logic (`schemas/models.py:39-146`, `schemas/models.py:211-341`).

**Paper-relevant specifics.** The canonical record fields include `verification_status`, `scope_bucket`, `scope_tags`, and `failure_reasons` (`schemas/models.py:211-270`). The legal route labels are `text`, `table`, `figure`, `mixed`, and `unresolved` (`schemas/models.py:292-306`).

**What is NOT obvious from README.** The live schema has moved from a single `endpoint` object to canonical `endpoints[]`; old frozen baseline JSONL predates that change and requires migration before direct validation against the current model (`schemas/models.py:211-270`, `reports/v1.5_change_set_c_validation.md:5-17`, `reports/v1.5_change_set_c_observations.md:77-88`).

### assembly/assemble_records.py

**One-line purpose.** Merges modality-specific candidate records into deduplicated paper-level records before verification. Reviewed in full: `assembly/assemble_records.py:1-450`.

**Algorithm summary.** Assembly normalizes candidate records, merges evidence and metadata, and groups rows by a key containing DOI, formulation label, primary endpoint kind, duration, and endpoint mean. It can promote same-paper table support into otherwise sparse rows and propagate API concentration support from compatible partial table rows. Text candidates can merge with table partials when the records are scientifically aligned. The stage is therefore more than deduplication: it is a controlled evidence-union step before verification (`assembly/assemble_records.py:80-182`, `assembly/assemble_records.py:185-357`, `assembly/assemble_records.py:386-434`).

**Paper-relevant specifics.** The assembly key is `(doi, formulation.label, primary endpoint kind, duration_h, primary endpoint mean)` (`assembly/assemble_records.py:174-182`). Table support promotion and API support propagation occur within the same paper only (`assembly/assemble_records.py:185-357`).

**What is NOT obvious from README.** Table “partials” are skipped by default unless specifically requested, but can still contribute support evidence to richer matched rows. This means some table extraction outputs influence final records without appearing as standalone assembled records (`assembly/assemble_records.py:215-322`, `assembly/assemble_records.py:386-434`).

### verification/verify_records.py

**One-line purpose.** Applies deterministic normalization, support checks, target-scope rules, and final verification labels to assembled records. Reviewed in full: `verification/verify_records.py:1-986`.

**Algorithm summary.** The verifier first normalizes record fields and recovers supported context such as device, area, receptor volume, and API hints from evidence. It then computes support rate, collects failure taxonomy codes, classifies the outcome as verified, unresolved, or rejected, and derives an orthogonal scope bucket with explanatory tags. Policy methods determine whether API concentration and endpoint kinds are in scope, but they are evaluated only after normalization and support computation. This yields an evidence-aware verification step rather than a simple policy lookup (`verification/verify_records.py:496-745`, `verification/verify_records.py:798-973`).

**Paper-relevant specifics.** In the live flow, normalization occurs before support rate computation, support rate is computed before failure collection, and policy-sensitive failure codes are gathered inside `_collect_failure_codes` before `classify_outcome` and `_derive_scope_bucket` run (`verification/verify_records.py:838-973`). `verification_status` is the outcome label, whereas `scope_bucket` categorizes scientific target fit and recoverability (`schemas/models.py:239-243`, `verification/verify_records.py:798-835`, `verification/failure_taxonomy.py:61-70`).

**What is NOT obvious from README.** A record can be scientifically out of the target scope yet still carry useful normalized evidence, and `scope_bucket` preserves that distinction instead of collapsing everything into a single rejected/unresolved status (`verification/verify_records.py:798-835`).

### verification/source_binding_guard.py

**One-line purpose.** Blocks records whose endpoint or condition claims appear to have leaked across incompatible source contexts. Reviewed in full: `verification/source_binding_guard.py:1-170`.

**Algorithm summary.** The guard inspects extractor identity, evidence modalities, shared-hint use, patched-time context, figure-mapping grounding, and figure-condition support. It returns a source-context inconsistency when a record mixes claims in ways that cannot be defended as coming from the same source. The caller converts those specific guard findings into a shared taxonomy failure code while preserving notes about the exact cause. This makes cross-source contamination auditable even when the final verification label is coarse (`verification/source_binding_guard.py:37-170`).

**Paper-relevant specifics.** Internal guard reasons are `figure_route_table_endpoint`, `endpoint_value_from_shared_hint`, `endpoint_value_time_context_mismatch`, `weak_figure_mapping_grounding`, and `figure_condition_not_source_grounded` (`verification/source_binding_guard.py:125-157`). Public failure reporting collapses them to `source_context_inconsistent` (`verification/source_binding_guard.py:160-170`).

**What is NOT obvious from README.** The public failure code alone hides several distinct anti-contamination checks. The source notes carry the finer-grained reason, so audit trails retain more information than the coarse taxonomy label suggests (`verification/source_binding_guard.py:125-170`).

### verification/llm_adjudicate.py

**One-line purpose.** Produces optional audit-only LLM second opinions for selected unresolved records after rule-based verification. Reviewed in full: `verification/llm_adjudicate.py:1-365`.

**Algorithm summary.** The adjudicator filters for unresolved records that are marked recoverable, constructs a compact evidence packet, and asks a structured LLM for an adjudication verdict. It does not rewrite verified outputs or replace the deterministic verifier; instead, it provides rescue-oriented annotations for later inspection. The stage therefore augments auditability without changing the canonical rule-based endpoint of the pipeline (`verification/llm_adjudicate.py:20-21`, `verification/llm_adjudicate.py:128-152`, `verification/llm_adjudicate.py:255-365`, `run_pipeline.py:651-655`).

**Paper-relevant specifics.** The prompt asset is `verification.llm_adjudication` version `2026-04-03.v1`; the structured schema is `AdjudicationVerdict` (`verification/llm_adjudicate.py:20-21`, `verification/llm_adjudicate.py:255-263`). Candidate records must be both `unresolved` and `recoverable_unresolved` with approved failure-code patterns (`verification/llm_adjudicate.py:128-152`).

**What is NOT obvious from README.** This stage is explicitly **audit-only**. Even when enabled, it does not override `verified_records`; the manifest text says so directly (`run_pipeline.py:651-655`).

### patchers/__init__.py

**One-line purpose.** Exposes a subset of patcher entry points for package-level imports. Reviewed in full: `patchers/__init__.py:1-11`.

**Algorithm summary.** The file re-exports the API-concentration, area, and endpoint-time patchers. It does not contain patch logic itself. The pipeline still imports all four live patchers explicitly from their module files. This module is packaging glue rather than scientific logic (`patchers/__init__.py:1-11`, `run_pipeline.py:36-39`).

**Paper-relevant specifics.** `patch_endpoint_value` is not re-exported from `patchers/__init__.py`, even though the live pipeline imports and runs it directly (`patchers/__init__.py:1-11`, `run_pipeline.py:36-39`).

**What is NOT obvious from README.** Package exports are incomplete relative to live patch execution, so auditing only `patchers.__all__` would miss one active patcher (`patchers/__init__.py:1-11`, `run_pipeline.py:36-39`).

### patchers/common.py

**One-line purpose.** Supplies shared evidence, copying, patch-log, and text-recovery helpers used by the patcher modules. Reviewed in full: `patchers/common.py:1-209`.

**Algorithm summary.** The helper module centralizes patch metadata creation, evidence support checks, safe record copying, text-fragment normalization, and recovery utilities used across individual patchers. It keeps patchers deterministic by providing common parsing and bookkeeping behavior. That shared layer also ensures every mutation can be recorded with patch name, changed fields, status, evidence count, and notes. The scientific patchers therefore differ in what they recover, not in how they log changes (`patchers/common.py:1-209`).

**Paper-relevant specifics.** Patch metadata is represented through the shared `PatchMetadata` schema and appended by helper routines rather than manually authored in each module (`patchers/common.py:1-209`, `schemas/models.py:196-209`).

**What is NOT obvious from README.** The patching system is designed as auditable deterministic repair, not silent record editing: even skipped patches leave structured traces when invoked (`patchers/common.py:1-209`).

### patchers/patch_api_concentration.py

**One-line purpose.** Recovers missing or ambiguous API-concentration fields from already captured evidence snippets. Reviewed in full: `patchers/patch_api_concentration.py:1-259`.

**Algorithm summary.** The patcher scans evidence snippets for concentration expressions, extracts candidate values and bases, and applies a repair only when the recovery is sufficiently grounded. It favors existing evidence rather than new inference and logs skipped cases when no defensible recovery is available. The module is aimed at repairing records blocked by concentration-specific verification failures. It does not expand target scope; policy still determines whether the recovered concentration is acceptable (`patchers/patch_api_concentration.py:84-259`).

**Paper-relevant specifics.** The callable patch entry point is `patch_api_concentration` (`patchers/patch_api_concentration.py:130-259`). In the frozen GPT baseline artifacts, the patcher recorded `219` skipped applications and contributed no additional verified records under v2 when each frozen intermediate artifact was rescored after schema migration.

**What is NOT obvious from README.** Under the frozen v2 baseline, this patcher is operationally “quiet” for the verified count even though it still runs; the final v2 gain is already present before patching.

### patchers/patch_area.py

**One-line purpose.** Recovers missing diffusion area values from evidence snippets so total amount endpoints can be normalized per area. Reviewed in full: `patchers/patch_area.py:1-148`.

**Algorithm summary.** The patcher extracts candidate area values from area-marked evidence, validates them, and patches unresolved records when the area can be defensibly recovered. The repaired field enables later unit normalization and support checks, but the patcher does not itself verify the record. As with the other patchers, it records applied and skipped attempts in provenance. The logic is deterministic and evidence-bound (`patchers/patch_area.py:21-148`).

**Paper-relevant specifics.** The entry point is `patch_area` (`patchers/patch_area.py:59-148`). In frozen GPT artifacts it recorded `20` applied and `96` skipped attempts, yet added `0` verified rows under v2 relative to the immediately preceding frozen stage.

**What is NOT obvious from README.** Area repair can be scientifically useful without changing headline v2 count, because a row may still remain blocked by a different unresolved failure after area recovery.

### patchers/patch_endpoint.py

**One-line purpose.** Recovers endpoint values from captured endpoint evidence when a record has a missing or weaker endpoint representation. Reviewed in full: `patchers/patch_endpoint.py:1-249`.

**Algorithm summary.** The patcher searches endpoint evidence fragments, parses candidate values and units, compares them against the current endpoint state, and applies a repair only when the candidate improves the record without weakening unit quality. It preserves deterministic endpoint ordering after modification and logs skips for duplicate, absent, or weaker recoveries. The module helps rescue records where extraction surfaced evidence but normalization did not yet produce a usable endpoint. It remains subordinate to later verification (`patchers/patch_endpoint.py:75-249`).

**Paper-relevant specifics.** The callable patch entry point is `patch_endpoint_value` (`patchers/patch_endpoint.py:236-249`). Frozen GPT artifacts show `69` applied and `105` skipped attempts, but the v2 verified count stays unchanged across the endpoint-value patch boundary.

**What is NOT obvious from README.** This active patcher is easy to miss because it is not exported by `patchers/__init__.py`, even though `run_pipeline.py` imports it directly (`patchers/__init__.py:1-11`, `run_pipeline.py:36-39`).

### patchers/patch_endpoint_time.py

**One-line purpose.** Repairs missing endpoint-duration fields from grounded source context. Reviewed in full: `patchers/patch_endpoint_time.py:1-82`.

**Algorithm summary.** The patcher recovers endpoint time from existing evidence, applies the repair when a valid duration can be derived, and records whether the repair was applied or skipped. It is intentionally narrow: the module focuses on time context only and leaves endpoint values, area, and concentration to separate patchers. This keeps repair provenance disentangled by failure mode. Verification later decides whether the patched record is now acceptable (`patchers/patch_endpoint_time.py:14-82`).

**Paper-relevant specifics.** The entry point is `patch_endpoint_time` (`patchers/patch_endpoint_time.py:14-82`). Frozen GPT artifacts show `53` applied and `10` skipped attempts, but no v2 verified-count increase at that stage.

**What is NOT obvious from README.** Time recovery is a dedicated repair rather than a side effect of endpoint recovery, which matters because the source-binding guard treats patched-time plus shared-hint endpoint context as a specific contamination risk (`patchers/patch_endpoint_time.py:14-82`, `verification/source_binding_guard.py:125-157`).

## 7. §2.2 Targeted Specification

### policies/v1_strict_ibuprofen_5pct.py

**One-line purpose.** Defines the strictest target specification: ibuprofen Franz-cell records with a 5% w/w-equivalent API concentration and cumulative-amount endpoints. Reviewed in full: `policies/v1_strict_ibuprofen_5pct.py:1-115`.

**Algorithm summary.** The policy checks API identity, concentration target, study type, Franz-cell device context, accepted endpoint kind, and endpoint time. It also provides utility methods used by verification to decide whether a concentration or endpoint is in scope. The specification is scientific scope logic, not a machine-learning policy. Later policy layers inherit and relax only selected conditions (`policies/v1_strict_ibuprofen_5pct.py:13-34`, `policies/v1_strict_ibuprofen_5pct.py:64-115`).

**Paper-relevant specifics.** The policy accepts ibuprofen at either `5% w/w` or `50 mg/g`, requires a Franz diffusion cell, requires study type in `IVPT`, `IVRT`, or `both`, requires a cumulative amount endpoint, and requires endpoint time (`policies/v1_strict_ibuprofen_5pct.py:23-34`, `policies/v1_strict_ibuprofen_5pct.py:72-109`).

**What is NOT obvious from README.** The policy module itself is the shared base for later layers; there is no separate `policies/base.py` in the live repo.

### policies/v2_accept_wv.py

**One-line purpose.** Extends v1 by accepting 5% w/v-equivalent concentrations in addition to the original 5% w/w target. Reviewed in full: `policies/v2_accept_wv.py:1-37`.

**Algorithm summary.** This layer inherits the v1 scientific gates and overrides only API-concentration acceptance. It therefore keeps the same device, study-type, endpoint, and time requirements while broadening a single concentration interpretation. The change is targeted and monotonic relative to v1. It is used to test sensitivity to w/v reporting conventions without rerunning extraction (`policies/v2_accept_wv.py:14-37`).

**Paper-relevant specifics.** Additional accepted concentration forms are `5% w/v` and `50 mg/mL` (`policies/v2_accept_wv.py:14-37`).

**What is NOT obvious from README.** The frozen v2 GPT rescore increases verified rows from `1` to `25` entirely by accepting 24 table records at `5% (w/v)` from one Kallakunta paper plus the original figure record; those 24 rows are already present before patching (`outputs/gpt-extended-baseline/v2_rescore/summary.json`, `outputs/gpt-extended-baseline/v2_rescore/v2_rescore_summary.md`).

### policies/v3_any_ibuprofen_concentration.py

**One-line purpose.** Extends v1 by accepting any ibuprofen concentration while preserving the remaining scientific gates. Reviewed in full: `policies/v3_any_ibuprofen_concentration.py:1-21`.

**Algorithm summary.** This layer inherits v1 and replaces only the concentration test with a broader rule that accepts any record whose API identity is ibuprofen. It still rejects missing or non-ibuprofen APIs and leaves Franz-cell, study-type, endpoint-kind, and time requirements intact. The layer therefore isolates concentration scope from the rest of the target definition. It is suitable for sensitivity analysis on dosage breadth (`policies/v3_any_ibuprofen_concentration.py:10-21`).

**Paper-relevant specifics.** `is_target_api_concentration` returns true whenever the API name equals the target ibuprofen name, regardless of numeric concentration value (`policies/v3_any_ibuprofen_concentration.py:10-21`).

**What is NOT obvious from README.** “Any concentration” does not mean “any API”; missing API identity and non-ibuprofen APIs still fail.

### policies/v4_accept_flux.py

**One-line purpose.** Extends v3 by allowing flux and permeability-style endpoints in addition to cumulative amount endpoints. Reviewed in full: `policies/v4_accept_flux.py:1-138`.

**Algorithm summary.** This layer inherits the broad-concentration v3 behavior and relaxes endpoint-kind acceptance. It can recognize flux or permeability not only from explicit endpoint kind but also from unit and context signals, preserving a reclassification reason when a unit implies flux. The remaining scientific gates remain inherited. The layer is therefore the broadest live target specification and is designed for endpoint-scope sensitivity rather than extraction changes (`policies/v4_accept_flux.py:1-138`).

**Paper-relevant specifics.** The accepted endpoint set includes cumulative amount, flux/Jss, and permeability coefficient, with unit-implied flux reclassification supported (`policies/v4_accept_flux.py:85-138`).

**What is NOT obvious from README.** v4 can preserve the raw extracted endpoint while using an effective kind derived from the unit string for verification, which separates traceability from target-scope classification (`policies/v4_accept_flux.py:85-138`).

**Four paper-facing acceptance statements.**

- **v1.** A record is accepted if it describes ibuprofen in a Franz diffusion-cell IVPT/IVRT study, reports a cumulative amount endpoint with a time value, and uses an API concentration equivalent to exactly 5% w/w or 50 mg/g (`policies/v1_strict_ibuprofen_5pct.py:23-34`, `policies/v1_strict_ibuprofen_5pct.py:72-109`).
- **v2.** A record is accepted if it satisfies all v1 requirements, with the concentration rule broadened to also allow 5% w/v or 50 mg/mL (`policies/v2_accept_wv.py:14-37`).
- **v3.** A record is accepted if it satisfies the v1 device, study-type, endpoint, and time requirements and the active ingredient is ibuprofen at any reported concentration (`policies/v3_any_ibuprofen_concentration.py:10-21`).
- **v4.** A record is accepted if it satisfies the v3 ingredient and study-context requirements and reports either cumulative amount, flux/Jss, or permeability coefficient as the endpoint, including cases where the unit itself proves a flux endpoint (`policies/v4_accept_flux.py:85-138`).

## 8. Answers to specific questions

### Q1. Query Expansion existence

**Answer: no.** The live repo contains no LLM-driven Query Expansion stage. Corpus search strings are built deterministically from static profile term lists in `build_epmc_query`, stored in the `QUERY_PROFILES` registry, and selected through `get_query_profile` (`corpus/query_profiles.py:29-46`, `corpus/query_profiles.py:59-99`). In `run_pipeline.py`, `--query-profile` chooses the profile object, while `--query` overrides only the query string used for the run; the manifest separately records whether the source was `profile:<name>` or `custom_override:<name>` (`run_pipeline.py:587-593`, `run_pipeline.py:787-798`). Therefore §2.1.2 should not name Query Expansion as an implemented live function.

### Q2. Rule + LLM Triage division

The deterministic rule filter evaluates `title + abstract`, requires an explicit ibuprofen mention, at least one inclusion pattern, and no exclusion pattern, then emits rule-level relevance labels, confidence, hints, and exclusions (`triage/rule_filter.py:8-28`, `triage/rule_filter.py:55-79`). The LLM triage stage then sees the **title plus abstract**, with the abstract truncated to `2000` characters, and decides semantic relevance through the `LLMTriageResult` schema containing `relevant`, `confidence`, `rationale`, and `extraction_hints` (`triage/prompts.py:4-12`, `triage/llm_triage.py:20-35`, `triage/llm_triage.py:90-110`). If repeated LLM attempts fail, the record is parked as `not_relevant` with confidence `0.0` rather than silently accepted (`triage/llm_triage.py:139-154`).

### Q3. Route Detection

The router uses three named evidence anchors: `where_franz`, `where_endpoint`, and `formulation_carrier_snippet` (`detection/router.py:397-434`). It operates on both structured and unstructured sources, preferring XML/HTML blocks and falling back to PDF pages when structured content is unavailable (`detection/router.py:116-153`, `detection/router.py:156-205`, `detection/router.py:273-322`). The canonical output labels are `text`, `table`, `figure`, `mixed`, and `unresolved` (`schemas/models.py:292-306`). Papers become `unresolved` when the source is unusable, when route evidence remains ambiguous, when the endpoint appears supplement-bound, or when repeated structured-LLM attempts fail and the deterministic fallback cannot confidently assign a route (`detection/router.py:340-394`, `detection/router.py:489-611`).

### Q4. Table 60-row cap

The HTML row cap is enforced in `_extract_html_rows(max_rows=60)` (`extractors/table/extractor.py:338-352`). When the collected row count reaches the cap, the structured table block is annotated with `TABLE_TRUNCATED: true` and a truncation note that the HTML table exceeded `60` rows (`extractors/table/extractor.py:355-381`). The window-level builder propagates truncation into `table_truncated=True` and records notes such as `<locator>: row cap reached`; it can also mark a window-character truncation at `28_000` characters (`extractors/table/extractor.py:432-503`). Later, `table_truncated` is stored in provenance metadata and in the raw extraction output (`extractors/table/extractor.py:1554-1564`, `extractors/table/extractor.py:1631-1642`).

### Q5. Figure Agent data flow

The live figure flow is: figure triage in `triage.py`, computer-vision digitization in `digitize.py`, optional direct VLM reading in `vlm_digitize.py`, constrained VLM curve-label mapping in `map_curves.py`, and reconciliation into records in `build_records.py` (`extractors/figure/build_records.py:754-767`). `digitize.py` is OpenCV-only, with no LLM call (`extractors/figure/digitize.py:17-18`, `extractors/figure/digitize.py:253-346`, `extractors/figure/digitize.py:672-1119`). `triage.py`, `vlm_digitize.py`, and `map_curves.py` use structured VLM calls (`extractors/figure/triage.py:500-508`, `extractors/figure/vlm_digitize.py:298-306`, `extractors/figure/map_curves.py:303-311`). `build_records.py` reconciles CV and VLM values, accepts agreement within `15%`, and falls back to `vlm_only` when a grounded VLM reading exists but no CV candidate survives (`extractors/figure/build_records.py:590-735`).

### Q6. Source-binding guard

`apply_source_context_guard` blocks five explicit cross-source contamination patterns: a figure-route record whose endpoint actually comes from non-figure evidence (`figure_route_table_endpoint`), an endpoint value inherited from a shared hint (`endpoint_value_from_shared_hint`), a shared-hint endpoint combined with patched endpoint time (`endpoint_value_time_context_mismatch`), weak figure-label grounding (`weak_figure_mapping_grounding`), and figure conditions lacking figure-source grounding (`figure_condition_not_source_grounded`) (`verification/source_binding_guard.py:125-157`). The public failure taxonomy receives the shared code `source_context_inconsistent`, while source notes retain the specific internal reason string (`verification/source_binding_guard.py:160-170`).

### Q7. Verification flow

Policy-sensitive checks are not run first. The verifier first normalizes fields and endpoints, then computes `verification_support_rate`, then gathers failure codes—including the policy-dependent target checks—inside `_collect_failure_codes`, and only then sets `verification_status` and `scope_bucket` (`verification/verify_records.py:496-745`, `verification/verify_records.py:838-973`). `verification_status` is the final outcome class `verified`, `unresolved`, or `rejected`, as assigned through the failure taxonomy; `scope_bucket` is a separate descriptor of scientific target fit and recoverability such as `strict_in_scope`, `recoverable_unresolved`, `useful_but_out_of_scope`, or `out_of_scope` (`schemas/models.py:239-243`, `verification/failure_taxonomy.py:61-70`, `verification/verify_records.py:798-835`).

### Q8. Four-policy acceptance conditions

- **v1:** accepted if the record is an ibuprofen Franz-cell IVPT/IVRT record with a cumulative amount endpoint, a time value, and exactly 5% w/w or 50 mg/g concentration (`policies/v1_strict_ibuprofen_5pct.py:23-34`, `policies/v1_strict_ibuprofen_5pct.py:72-109`).
- **v2:** accepted if the record satisfies v1, except that 5% w/v and 50 mg/mL are also accepted concentration representations (`policies/v2_accept_wv.py:14-37`).
- **v3:** accepted if the record satisfies the v1 study-context and endpoint requirements and the API is ibuprofen at any concentration (`policies/v3_any_ibuprofen_concentration.py:10-21`).
- **v4:** accepted if the record satisfies v3 and its endpoint is cumulative amount, flux/Jss, or permeability coefficient, including unit-implied flux cases (`policies/v4_accept_flux.py:85-138`).

### Q9. Patchers inventory

The live `patchers/` directory contains six files:

| File | One-line purpose |
| --- | --- |
| `patchers/__init__.py` | Re-exports package-level patcher entry points, but omits `patch_endpoint_value` from exports (`patchers/__init__.py:1-11`). |
| `patchers/common.py` | Provides shared deterministic patch bookkeeping and evidence helpers (`patchers/common.py:1-209`). |
| `patchers/patch_api_concentration.py` | Recovers missing or ambiguous API concentration from captured evidence (`patchers/patch_api_concentration.py:84-259`). |
| `patchers/patch_area.py` | Recovers missing diffusion area from captured evidence (`patchers/patch_area.py:21-148`). |
| `patchers/patch_endpoint.py` | Recovers endpoint value and unit from endpoint evidence fragments (`patchers/patch_endpoint.py:75-249`). |
| `patchers/patch_endpoint_time.py` | Recovers endpoint duration context (`patchers/patch_endpoint_time.py:14-82`). |

For the frozen GPT baseline, the published v2 rescore of the post-patch artifact contains `25` verified rows (`outputs/gpt-extended-baseline/v2_rescore/summary.json`). A read-only v2 rescore of the migrated frozen intermediate artifacts shows `25` verified rows already at `verified_initial.jsonl` and still `25` after every patch boundary; therefore **no patcher contributes additional verified rows to the frozen v2 count**. Under v2, all four scientific patchers are “quiet” with respect to the headline verified total, even though some do apply record repairs: API concentration `0` applied / `219` skipped, endpoint value `69` applied / `105` skipped, endpoint time `53` applied / `10` skipped, and area `20` applied / `96` skipped.

### Q10. LLM Orchestrator implementation seam

The claim in the task wording is no longer exact. `utils/llm_client.py:102-130` is still the single live structured-response seam, but the current production pipeline has **nine**, not eight, structured stages. Eight call `parse_structured` directly, and the PDF metadata stage defaults its injectable client to `parse_structured` (`corpus/extract_pdf_metadata.py:165-195`).

| Stage | Call site | `text_format` schema |
| --- | --- | --- |
| PDF metadata extraction | `corpus/extract_pdf_metadata.py:165-195` | `PdfMetadataLLMResponse` |
| LLM triage | `triage/llm_triage.py:102-110` | `LLMTriageResult` |
| Route detection | `detection/router.py:523-531` | `RouterLLMResponse` |
| Text extraction | `extractors/text/extract_fields.py:129-137` | `PaperExtraction` |
| Table extraction | `extractors/table/extractor.py:728-736` | `TableExtractionResult` |
| Figure triage | `extractors/figure/triage.py:500-508` | `FigureTriageResult` |
| Figure VLM reading | `extractors/figure/vlm_digitize.py:298-306` | `VLMFigureResult` |
| Figure curve mapping | `extractors/figure/map_curves.py:303-311` | `MapResult` |
| LLM adjudication | `verification/llm_adjudicate.py:255-263` | `AdjudicationVerdict` |

## 9. Discrepancies between handoff narrative and code

1. **Query Expansion is not implemented.** The live pipeline has no LLM-driven query-generation stage; only static query profiles exist (`corpus/query_profiles.py:29-46`, `run_pipeline.py:587-593`).
2. **The “eight structured stages” wording is stale.** Live code now exposes nine production structured stages because PDF metadata extraction adds `PdfMetadataLLMResponse` through the same `parse_structured` seam (`corpus/extract_pdf_metadata.py:165-195`, `utils/llm_client.py:102-130`).
3. **Frozen prompt assets are not standalone files in the live repo.** Prompt IDs and versions are embedded in source modules and tracked through `PROMPT_PATHS` / `PROMPT_ASSETS`, rather than loaded from separate prompt files (`run_pipeline.py:71-100`).
4. **The live table prompt version differs from the handoff baseline.** The task names `extractors.table.structured_tables=2026-04-11.v1`, but live code defines `2026-05-10.change-set-c` (`extractors/table/extractor.py:53-54`).
5. **Figure conditions are more conservative than a casual multimodal summary suggests.** The live builder avoids blindly copying table context into figure records and only keeps figure-grounded conditions (`extractors/figure/build_records.py:303-340`, `extractors/figure/vlm_digitize.py:273-286`).
6. **The frozen baseline artifacts are older-schema JSONL.** Current live `Record` requires `endpoints[]`, whereas the frozen GPT outputs still store a legacy top-level `endpoint` object and need deterministic migration before direct validation against current schemas (`schemas/models.py:211-270`, `reports/v1.5_change_set_c_observations.md:77-88`, `reports/v1.5_change_set_c_validation.md:5-17`).

## 10. Files referenced in this task that could not be located

The task asked for frozen prompt **asset files**, but no standalone prompt files exist for the eight requested IDs. The closest live alternatives are the source files that embed those prompt IDs and prompt bodies:

| Referenced asset file requested by task | Standalone file located? | Closest live alternative |
| --- | --- | --- |
| `triage.abstract_relevance=2026-03-28.v1` | No | `triage/prompts.py` |
| `routing.structured_first=2026-03-28.v1` | No | `detection/router.py` |
| `extractors.text.structured_fields=2026-04-11.v1` | No | `extractors/text/extract_fields.py` |
| `extractors.table.structured_tables=2026-04-11.v1` | No | `extractors/table/extractor.py` |
| `extractors.figure.triage=2026-04-06.v1` | No | `extractors/figure/triage.py` |
| `extractors.figure.vlm_digitize=2026-04-11.v1` | No | `extractors/figure/vlm_digitize.py` |
| `extractors.figure.curve_map=2026-03-28.v1` | No | `extractors/figure/map_curves.py` |
| `verification.llm_adjudication=2026-04-03.v1` | No | `verification/llm_adjudicate.py` |

Count of task-referenced files that could not be located as standalone repo files: **8**. A separate shared policy base file was also not present, but the task framed that item conditionally (“if it exists”), so it is not counted among the missing referenced files; the live inheritance root is `policies/v1_strict_ibuprofen_5pct.py`.
