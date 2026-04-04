# `full_run_07_full` 人工复核误差分析

## 1. 目的与边界

这份文档基于：

- [`outputs/full_run_07_full/report/review_sheet.csv`](/c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/outputs/full_run_07_full/report/review_sheet.csv)
- [`outputs/full_run_07_full/report/manual_review_priority_checklist.md`](/c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/outputs/full_run_07_full/report/manual_review_priority_checklist.md)

目的不是把 manual review 纳入生产 pipeline，而是用人工复核结果去校准当前自动框架，明确：

- 当前 `verified / unresolved / rejected` 的误差模式
- 哪些模块最值得继续强化
- 后续 evaluation 应该优先关注哪些指标

本分析针对的是人工优先复核集，不等同于对整个 `full_run_07_full` 的完整总体统计。

## 2. 复核样本概览

- 人工复核总行数：`79`
- 人工最终 `review_keep_record = yes`：`19`
- 人工最终 `review_keep_record = no`：`60`

按系统状态拆分：

- 系统 `verified`：`32`
- 系统 `unresolved`：`29`
- 系统 `rejected`：`18`

按人工决定拆分：

- `keep_verified`：`6`
- `rescue_to_verified`：`13`
- `keep unresolved`：`2`
- `downgrade to unresolved`：`1`
- `reject scope mismatch`：`21`
- `confirm rejected`：`36`

## 3. 最关键的误差结论

### 3.1 `verified` 假阳性偏多

在复核样本中：

- 系统 `verified` 且人工仍保留：`6 / 32`
- 系统 `verified` 但人工不保留：`26 / 32`

也就是这批优先复核样本中的 `verified` 保留率只有 `18.75%`。

这说明当前系统的主要问题不是“抽不出记录”，而是：

- 严格 scope 的最终 acceptance 还不够硬
- `verified` 中仍混入较多 scope mismatch 或 endpoint mismatch 的记录

### 3.2 `unresolved` 是高价值恢复池

在复核样本中：

- 系统 `unresolved` 且人工最终可保留：`13 / 29`

保留率约为 `44.83%`。这说明 `unresolved` 并不是“低价值垃圾桶”，而是后续 patching / recovery 的重点来源。

### 3.3 `rejected` 相对可靠

在复核样本中：

- 系统 `rejected`：`18`
- 人工全部判断 `review_keep_record = no`

这说明当前 `rejected` 桶整体方向是对的，后续优化重点不应放在“放松 rejected”，而应放在：

- 收紧 `verified`
- 强化 `unresolved` recovery

## 4. 按 route 的误差表现

复核样本中的人工保留率：

- `table`：`10 / 16 = 62.5%`
- `mixed`：`6 / 25 = 24.0%`
- `figure`：`3 / 28 = 10.7%`
- `text`：`0 / 10 = 0%`

这表明：

- `table` 路由当前是最健康的主力路径
- `mixed` 次之，但仍需要更严格的 acceptance
- `figure` 当前仍然高风险
- `text` 路由在这批优先复核样本中没有贡献最终保留记录

架构含义：

- `table` 可以继续作为 strict dataset 的主支撑模态
- `figure / mixed / text` 进入 `verified` 前需要更高门槛

## 5. `verified` 假阳性的主要原因

对“系统已 verified 但人工不保留”的 `26` 条记录，人工复核显示：

- `review_target_api_ok = yes`：`26 / 26`
- `review_franz_ok = no`：`25 / 26`
- `review_5pct_ww_ok = no`：`18 / 26`
- `review_ivpt_ivrt_ok = no`：`17 / 26`
- `review_amount_endpoint_ok = no`：`17 / 26`

这意味着当前误判的核心不是“药物认错”，而是 strict scope 判定不够严：

1. 把 generic diffusion cell 过度放宽成目标 `Franz diffusion cell`
2. 把非 `IVPT / IVRT` 研究放进 strict dataset
3. 把 `flux / Jss / Papp / percent release` 等 endpoint 过度接受
4. 把 `mM / mg/mL / mg/kg / plain %` 等浓度表达过度放宽成可接受的 `5% w/w`

### 5.1 假阳性主要集中在高风险 route

“系统已 verified 但人工不保留”的 route 分布：

- `mixed`：`11`
- `figure`：`9`
- `text`：`5`
- `table`：`1`

这进一步说明：

- 当前真正需要收紧的是 `mixed / figure / text`
- `table` 路由相对更值得信任

## 6. `unresolved` 中最值得回收的模式

对“系统 unresolved 但人工认为可保留”的 `13` 条记录：

- `review_target_api_ok = yes`：`13 / 13`
- `review_5pct_ww_ok = yes`：`13 / 13`
- `review_franz_ok = yes`：`13 / 13`
- `review_ivpt_ivrt_ok = yes`：`13 / 13`
- `review_amount_endpoint_ok = yes`：`13 / 13`
- `review_endpoint_time_ok = yes`：`13 / 13`
- `review_area_ok = yes`：`13 / 13`

这些记录不是 scope 上有问题，而是自动流程在以下环节漏掉了关键信息：

- `missing_area`：`8`
- `missing_endpoint`：`4`
- `unit_normalization_failed`：`1`

按 route 看：

- `table`：`8`
- `mixed`：`3`
- `figure`：`2`

这说明下一步 recovery 的最高收益点是：

- `area` 恢复
- `endpoint` 恢复
- `table` 和 `mixed` 记录的 paper-level shared hint reuse

## 7. 对当前架构的直接启示

### 7.1 当前主 verifier 需要更“硬”

基于复核结果，当前 `verification` 的主问题不是覆盖率，而是 strict acceptance 过宽。

建议：

- 对 `amount endpoint` 做硬约束
- 对 `5% w/w` 做硬约束
- 对 `Franz diffusion cell` 做硬约束
- 对 `IVPT / IVRT` 做硬约束

### 7.2 接受策略需要 route-aware

建议不要所有 route 用同一 acceptance 门槛：

- `table`：可维持当前为主的 acceptance 逻辑
- `mixed`：需要更强的 cross-modality corroboration
- `figure`：进入 `verified` 前要求更强的 paper-level context support
- `text`：需要更强的 methods/device/endpoint 共识证据

### 7.3 `unresolved` 需要正式作为 recovery lane

当前 `unresolved` 中有真实可保留记录，不应只视为“失败输出”。建议：

- 强化 patchers 与 paper-level shared hint reuse
- 对 `missing_area / missing_endpoint / unit_normalization_failed` 建立更明确的 rescue path

### 7.4 增加 “useful but out of scope” 标记

人工复核里有不少记录：

- 科学上有用
- 但不属于当前 `v1_strict_ibuprofen_5pct`

建议在自动流程中显式区分：

- `strict_keep`
- `recoverable_unresolved`
- `useful_but_out_of_scope`

这样既不污染 strict dataset，也不丢掉未来扩 scope 时有价值的记录。

## 8. 对未来 adjudication layer 的启示

人工复核结果支持保留“可选的 LLM adjudication layer”这一想法，但不支持直接用它替代当前 rule-based verification。

原因：

- 当前 strict scope 需要可解释、可复现、可审计的硬边界
- 人工复核暴露出的主要问题，是 rule verifier 需要收紧，而不是完全改成软判定
- 未来更合适的设计是：
  - 先保留 rule-based verification 作为主 verifier
  - 再加一个 selective LLM adjudication layer，只处理高风险 `verified` 和高价值 `unresolved`

适合后续纳入 adjudication 的触发条件：

- `figure / mixed` 路由
- `verified` 但 endpoint / concentration / device 语义可疑
- `unresolved` 且只被单一 failure bucket 卡住
- route-level evidence 与 verification 结果明显冲突

## 9. 当前版本的总体判断

当前框架已经满足：

- 不依赖 manual review 也能自动跑通完整 pipeline
- 能生成 `verified / unresolved / rejected`
- 能为后续 evaluation 积累人工复核样本

但基于这次人工复核，当前版本还不能把 `verified` 直接视为最终真值。

更准确的定位是：

- `verified`：自动系统认为满足 strict policy
- `manual keep`：当前阶段更接近 gold standard 的最终裁决

## 10. 推荐的下一步

优先顺序建议如下：

1. 收紧 strict verification 的硬约束
2. 对 `figure / mixed / text` 做更严格的 route-aware acceptance
3. 强化 `missing_area / missing_endpoint / unit_normalization_failed` 的 recovery
4. 增加 `useful_but_out_of_scope` 自动标记
5. 设计 selective LLM adjudication layer，但不替代当前主 verifier

对应的更细任务清单见：

- [`reports/next_step_optimization_tasks.md`](/c:/Users/yz02380/OneDrive%20-%20University%20of%20Surrey/Science%20Research/Codes/SkinMiner/reports/next_step_optimization_tasks.md)
