# Experiment Design Checklist

面向当前 SkinMiner 框架的后续实验设计清单。

这份清单的目标不是替代正式 methods protocol，而是帮助后续实验保持：

- 对比维度清晰
- 配置变更可解释
- 输出可复核
- 成本与收益可比较

## 1. 总体原则

每次实验尽量只改一个主变量。

不要把下面这些变化混在同一轮里：

- 模型切换
- prompt 改写
- routing 逻辑改写
- patcher 规则增强
- policy 放宽或收紧
- corpus query 改动

推荐做法：

1. 固定一个 baseline。
2. 每轮只改一个核心因素。
3. 运行结束后只和最近可比 baseline 比较。

## 2. 先冻结的 baseline

后续比较建议以 `full_run_03` 所代表的代码状态作为当前 baseline。

基线特征：

- OA-only
- Europe PMC corpus build
- optional LLM triage enabled
- structured-first routing
- structured-first text extraction
- structured-first table extraction
- figure branch enabled but当前仍然不是主要 verified 贡献来源
- targeted patching enabled
- strict policy: `v1_strict_ibuprofen_5pct`

## 3. 实验前固定项

每次正式对比前，先确认下面这些项是否固定：

- query 文本
- `max-results`
- model name
- policy name
- 是否开启 `--with-llm-triage`
- 是否开启 `--enable-figure`
- 是否开启 `--download-content`
- output directory naming convention
- prompt 版本
- 代码版本说明

如果其中任何一项改变，必须在实验记录里写清楚。

## 4. 推荐的实验维度

### 4.1 Corpus / Retrieval

目标：

- 比较候选文献召回与噪声
- 评估不同 query profile 的影响

建议变量：

- 宽 query vs 收紧 query
- Europe PMC baseline query vs theme-specific query variants
- `max-results` 不同规模

关键指标：

- corpus rows
- rule pass rows
- LLM triage kept rows
- unresolved route ratio
- final verified count

### 4.2 Abstract Triage

目标：

- 判断 LLM triage 是否真的降低后续噪声和成本

建议变量：

- rule-only
- rule + LLM triage
- 不同 triage prompt 版本
- 不同 triage model

关键指标：

- kept / park / later 分布
- downstream routeable paper count
- extractor output counts
- verified count
- total tokens
- verified per 1k tokens

### 4.3 Routing

目标：

- 比较不同 routing 配置对 recall 和 downstream usability 的影响

建议变量：

- current structured-first router
- heuristic fallback on vs off
- different router model
- different routing prompt versions

关键指标：

- route distribution
- unresolved route ratio
- per-route verified yield
- per-route failure taxonomy

### 4.4 Text Extraction

目标：

- 评估 structured text branch 的贡献

建议变量：

- current structured-first text extractor
- window selection prompt / strategy variants
- normalization changes

关键指标：

- text records
- text-route verified count
- text-route failure buckets
- endpoint / endpoint time / device support rate

### 4.5 Table Extraction

目标：

- 评估 structured table branch 是否是当前最强主力

建议变量：

- current structured-first table extractor
- different table prompt versions
- stricter / looser row parsing策略

关键指标：

- table records
- table-route verified count
- API concentration recovery rate
- device mismatch rate

### 4.6 Figure Branch

目标：

- 明确 figure 分支到底是增益项还是成本项

建议变量：

- figure off
- figure on
- figure triage prompt variants
- later: preprocessing / plot bbox / edge extraction variants

关键指标：

- figure triage artifacts
- digitized endpoints ok / failed
- mapped curves
- figure records
- figure-route verified count
- figure-only token cost

当前特别要看：

- `fail_few_edges`
- `fail_missing_plot_context`
- `recommended_route:skip`

### 4.7 Verification / Patching

目标：

- 评估 patcher 对最终 verified count 的真实贡献

建议变量：

- verification only
- verification + patchers
- patcher ablation:
  - no patchers
  - API only
  - API + endpoint time
  - API + endpoint time + endpoint value
  - full patch stack

关键指标：

- initial verified
- final verified
- patch success counts
- failure bucket reductions

## 5. 推荐的实验顺序

建议按下面顺序推进，而不是随机改动：

1. Baseline reproducibility
   目标：同配置重复跑 2 次，确认结果波动范围。

2. Triage ablation
   比较 `rule-only` vs `rule + LLM triage`。

3. Figure ablation
   比较 `text+table` vs `text+table+figure`。

4. Patcher ablation
   比较 patcher 对 final verified 的增益。

5. Model comparison
   在固定 prompt 和 pipeline 结构的前提下比较模型。

6. Prompt comparison
   在固定模型下比较 triage / router / table / text prompts。

7. Cost-efficiency comparison
   比较 verified count 与 token cost 的 tradeoff。

## 6. 每次实验都要保存的输出

每轮实验至少保留：

- `run_manifest.jsonl`
- `report/run_report.json`
- `report/run_report.md`
- `long_run/summary.json`
- `long_run/events.jsonl`
- `verified_records.jsonl`
- `report/verified_records_flat.csv`

如果实验涉及 figure，还要保留：

- `figure_triage.jsonl`
- `figure_endpoints.jsonl`
- `figure_curve_map.jsonl`
- `report/figure_failure_summary.csv`

## 7. 推荐的结果比较表头

后续论文或内部比较表建议至少包含这些列：

- experiment_id
- code_notes
- model_name
- triage_mode
- figure_enabled
- corpus_rows
- triaged_rows
- unresolved_routes
- table_records
- text_records
- figure_records
- final_records_evaluated
- actually_verified
- unresolved
- rejected
- patch_api_success
- patch_endpoint_success
- patch_time_success
- patch_area_success
- total_tokens
- elapsed_seconds

## 8. 推荐的人审抽样

自动指标之外，建议每轮都做少量人工抽样：

- verified records: 随机抽 10 条
- unresolved records: 随机抽 10 条
- rejected records: 随机抽 10 条
- figure failures: 随机抽 5 条

人工检查重点：

- endpoint 是否真的是 amount endpoint
- endpoint time 是否和 endpoint 对齐
- API concentration 是否真的是 ibuprofen 而不是 excipient
- device 是否真的明确是 Franz diffusion cell
- failure taxonomy 是否贴切

## 9. 当前最值得优先比较的实验

基于 `full_run_03` 的现状，下一批最值得做的是：

1. `text+table` vs `text+table+figure`
2. `rule-only` vs `rule+LLM triage`
3. patcher ablation
4. model comparison on fixed prompts
5. figure triage / digitization improvement only after上述 baseline 对比完成

## 10. 暂时不要混在一起做的事

为了保持实验解释性，暂时不要在同一轮里同时做：

- query 收紧
- model 切换
- prompt 重写
- figure preprocessing overhaul
- verification taxonomy 改写

这些应拆成独立轮次。
