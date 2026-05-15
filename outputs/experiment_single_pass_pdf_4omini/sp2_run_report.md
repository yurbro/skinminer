# PDF Single-Pass Run Report: experiment_single_pass_pdf_4omini

## 1. Setup
- Provider/model: `openai` / `gpt-4o-mini`
- Input mode: raw PDF via Responses API `input_file`.
- Prompt/schema: same extraction instructions and output schema as SP-1, with the user prompt changed to reference the attached PDF.

## 2. PDF Availability
- DOI count: `29`
- PDF status counts: `{'ok': 29}`
- Model-callable PDF count: `29`
- All 29 papers had callable PDFs in this run.

## 3. Run Summary
- Run status counts: `{'ok': 29}`
- Raw records emitted: `106`
- Actual input tokens: `5,444,611`
- Actual output tokens: `34,646`
- Actual total tokens: `5,479,257`
- Estimated actual API cost: `$0.8375` using the configured provider/model token rates.

## 4. Gold Evaluation Pointers
- Gold evaluation: `single_pass_vs_gold_evaluation.md`
- Pipeline comparison for this run: `single_pass_vs_pipeline_comparison.md`
- Match audit: `single_pass_gold_matches.csv`
