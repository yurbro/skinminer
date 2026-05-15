# PDF Single-Pass Run Report: experiment_single_pass_pdf_claude

## 1. Setup
- Provider/model: `anthropic` / `claude-sonnet-4-6`
- Input mode: raw PDF via Responses API `input_file`.
- Prompt/schema: same extraction instructions and output schema as SP-1, with the user prompt changed to reference the attached PDF.

## 2. PDF Availability
- DOI count: `29`
- PDF status counts: `{'ok': 29}`
- Model-callable PDF count: `29`
- All 29 papers had callable PDFs in this run.

## 3. Run Summary
- Run status counts: `{'ok': 23}`
- Raw records emitted: `132`
- Actual input tokens: `991,794`
- Actual output tokens: `81,526`
- Actual total tokens: `1,073,320`
- Estimated actual API cost: `$4.1983` using the configured provider/model token rates.

## 4. Gold Evaluation Pointers
- Gold evaluation: `single_pass_vs_gold_evaluation.md`
- Pipeline comparison for this run: `single_pass_vs_pipeline_comparison.md`
- Match audit: `single_pass_gold_matches.csv`
