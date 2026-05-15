# Human vs SkinMiner Comparison Framework

## Metrics

1. **Extraction time**
   - Per-paper mean ± SD across annotators
   - Total time for 6 papers
   - SkinMiner time for the same 6 papers from pipeline logs

2. **Record coverage**
   - Human records per paper vs SkinMiner records per paper
   - Unique records found by human only / SkinMiner only / both

3. **Value accuracy**
   - For records found by both: value match rate
   - Numeric tolerance: ±5%

4. **Inter-annotator agreement**
   - Between human annotators: record-level agreement
   - Between each human annotator and SkinMiner: record-level agreement

5. **Cost comparison**
   - Human: hours × hourly rate (for example UK PhD student ~£12-15/hour)
   - SkinMiner: API cost for the same 6 papers

## Expected Result Template

| Metric | Human (mean) | SkinMiner | Ratio |
|---|---|---|---|
| Time per paper (min) | ? | ? | ?x |
| Total time (6 papers) | ? | ? | ?x |
| Records per paper | ? | ? |  |
| Value accuracy | ? | ? |  |
| Cost | ? | ? | ?x |

## Notes

- Compare against `outputs/human_annotation/skinminer_reference.csv`, which contains all assembled records for the selected six papers under the extended-policy rescore.
- Do not expose the SkinMiner reference file to annotators before manual extraction is complete.
- For difficult figure papers, record whether manual endpoint reading required ruler/zoom support or approximate visual interpolation.
