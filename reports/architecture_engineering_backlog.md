# Architecture And Engineering Backlog

基于当前 `full_run_03` 的运行结果，下面是从整体架构和工程实现角度最值得继续改进的方向。

## Status Note

As of `2026-03-28`, the following backlog items already have a first implementation pass in the codebase:

- resume / checkpoint consistency hardening
- malformed-output / retry tracking
- figure preprocessing / bbox refinement / edge extraction strengthening
- report blockage summary
- query profiles + prompt versioning
- evaluation fixture and gold-label scaffolding

This means the remaining highest-value follow-on work is now concentrated in:

- further device normalization
- further API concentration recovery
- broader false-positive control for device normalization
- broader false-positive control for API concentration recovery
- more aggressive figure-aware recovery hooks
- budget caps and cost-efficiency summaries on top of the new run profiles
- cache metadata discipline beyond basic structured-source caching
- richer automated evaluation / scoring

排序原则：

- 是否直接影响后续实验稳定性
- 是否直接影响 verified yield
- 是否直接影响成本
- 是否能保持实验可解释性

## P0: 高优先级

### 1. 更稳的 resume / checkpoint 一致性

当前已经有可用的 `--resume`，但仍然建议继续增强：

- 给 stage marker 写入输入摘要，避免旧输出与新输入不一致却被误复用
- 区分“阶段完成”与“阶段部分 checkpoint 存在”
- 在 resume 时校验关键输入行数是否匹配
- 对 raw JSONL 与 final JSONL 的一致性做轻量检查

为什么重要：

- 这直接影响全量实验的稳定性和可信度

### 2. 细粒度 malformed-output / retry 统计

当前已经有重试逻辑，但建议再补：

- 每个 LLM 模块的 parse failure count
- malformed JSON / schema mismatch count
- retry succeeded count
- final fail count
- per-module retry cost

为什么重要：

- 后续比较不同模型和 prompt 时，这会是非常关键的工程指标

### 3. Device normalization 继续强化

从 `full_run_03` 看，`not_target_device` 仍然是第一大 failure bucket。

建议继续增强：

- 更明确地区分 `Franz diffusion cell` vs generic `diffusion cell`
- 增加 donor / receptor / diffusion area / cell assembly 的组合判断
- 为 device evidence 单独输出 support snippet

为什么重要：

- 这是当前 strict policy 下最大的残留瓶颈之一

### 4. API concentration recovery 继续强化

`missing_api_concentration` 虽然已经下降，但仍然偏高。

建议继续增强：

- 更明确地区分 API 与 excipient concentration
- 支持更多 formulation statement 模式
- 在 table / text / patcher 三层复用同一套 API context rules

为什么重要：

- 它仍然是当前 verified 提升的主要限制之一

## P1: 中高优先级

### 5. Figure branch 继续优先打磨前处理，而不是 mapping

当前 evidence 已经很清楚：

- 主要失败不是 curve mapping
- 主要失败在 `fail_few_edges` / `fail_missing_plot_context`

建议继续增强：

- 图像预处理
- plot bbox localization
- axis / plot-region detection
- edge extraction robustness

为什么重要：

- 这是让 figure 真正贡献 verified record 的主要前提

### 6. Figure failures 更深入反馈到 verification / patcher

当前 report 已经能统计 figure failures，但还可以更进一步：

- 把 plot-context failure 转成更明确的 record-level source note
- 让 verification 理解 figure failure 是“carrier missing”还是“digitization failure”
- 尝试为 figure-derived records 增加 endpoint-time / area 的辅助 patch hooks

为什么重要：

- 这样 figure 分支不会只是“失败统计”，而是能真正反馈到 recovery 层

### 7. Report 层增加 blockage summary

建议直接在 run report 里增加：

- 为什么没有进入 extractor
- 为什么 route unresolved
- 为什么 patcher 没命中

为什么重要：

- 这样就不用每次手动翻多个 JSONL 文件才能判断 pipeline 卡点

## P2: 中优先级

### 8. Corpus query profiles + prompt versioning

建议把 query 和 prompt 明确做成版本化资产：

- baseline query
- conservative query
- recall-oriented query
- triage prompt version
- router prompt version
- text/table/figure prompt version

为什么重要：

- 后续实验会大量依赖“版本可比性”

### 9. 成本控制模式

目前最贵的模块已经比较清楚，建议后面补：

- figure off / on 的快捷运行 profile
- triage sampling / budget cap
- per-stage request cap
- verified-per-token summary

为什么重要：

- 这会显著提高方法比较的效率

### 10. Remote source caching discipline

建议进一步规范：

- 远程 HTML/XML 缓存策略
- 失败重试后的缓存状态
- cache metadata 记录

为什么重要：

- 能减少重复请求和不稳定外部依赖

## P3: 方法学与评估准备

### 11. Evaluation fixtures and gold labels

建议后续建立：

- text-only fixtures
- table-only fixtures
- figure-only fixtures
- mixed-route fixtures
- gold labels for endpoint / endpoint time / device / API concentration

为什么重要：

- 这是后续 methods paper 或 benchmark 最核心的基础设施

### 12. Structured experiment comparison utilities

建议后续补：

- cross-run comparison script
- run-to-run delta tables
- bucket-level trend summaries

为什么重要：

- 实验轮次一多，手工比对会很快失控

## 13. 当前最建议的推进顺序

如果按工程收益排序，我建议是：

1. resume 一致性校验
2. malformed-output / retry 统计
3. device normalization 强化
4. API concentration recovery 强化
5. figure preprocessing / bbox / edge extraction
6. report blockage summary
7. query / prompt versioning
8. evaluation fixtures / gold labels

## 14. 当前不建议立刻大改的点

在拿到更多对比实验前，暂时不建议立刻做：

- 大规模重写 figure mapping
- 把 policy 放宽以追求更高 verified count
- 同时重写 triage、routing、verification 三层
- 引入数据库、任务队列或外部 orchestration

这些都会降低当前结果的可解释性。
