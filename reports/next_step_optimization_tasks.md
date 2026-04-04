# 下一步优化任务清单

## 1. 目标

这份任务清单基于：

- `full_run_07_full` 的自动结果
- 人工复核结果 `review_sheet.csv`
- 当前 strict scope：`v1_strict_ibuprofen_5pct`

目标不是继续大改架构，而是围绕人工复核暴露出的真实误差，优先提高：

- `verified` 精度
- `unresolved` 的可恢复率
- strict scope 的可解释性与可复现性

## 2. 实施原则

- 不把 manual review 设计进生产 pipeline
- 继续保留 rule-based verification 作为主 verifier
- 先修 precision，再考虑引入更昂贵的 LLM adjudication
- 优先做对 `verified` 精度和 `unresolved` recovery 都有直接收益的改动

## 3. 优先级任务

### P0. 收紧 strict verification 的硬约束

**目标**

把当前大量“系统 verified 但人工不保留”的记录挡在最终 strict 数据集之外。

**重点**

- 对 `amount endpoint` 做硬约束
- 对 `5% w/w` 做硬约束
- 对 `Franz diffusion cell` 做硬约束
- 对 `IVPT / IVRT` 做硬约束

**建议改动**

- 在 `verification/verify_records.py` 中增加明确 hard blockers
- 对 `flux / Jss / Papp / permeability coefficient / percent release` 做 stricter rejection 或 downgrade
- 对 `mM / mg/mL / mg/kg / plain %` 做 stricter concentration rejection，除非能明确映射回 `5% w/w`

**预期收益**

- 直接提升 `verified` 精度
- 减少 `mixed / figure / text` 的误保留

### P1. 做 route-aware acceptance

**目标**

不同 route 用不同严格度，而不是所有记录走同一 acceptance 逻辑。

**建议改动**

- `table`：保持当前主 acceptance 逻辑
- `mixed`：要求更强的 cross-modality corroboration
- `figure`：要求更强的 paper-level context support
- `text`：要求更强的 methods/device/endpoint 共识证据

**候选改动点**

- `assembly/assemble_records.py`
- `verification/verify_records.py`
- `verification/failure_taxonomy.py`

**预期收益**

- 压低 `figure / mixed / text` 假阳性
- 不牺牲 `table` 路由的当前优势

### P2. 把 `unresolved` 正式当作 recovery lane

**目标**

优先救回人工复核中已经证明值得回收的 unresolved 记录。

**重点 failure buckets**

- `missing_area`
- `missing_endpoint`
- `unit_normalization_failed`

**建议改动**

- 强化 `patch_area.py`
- 强化 `patch_endpoint.py`
- 在 verification 前后都更积极地复用 paper-level shared hints
- 对 `table / mixed` 路由优先做 rescue

**预期收益**

- 提升 `unresolved -> verified` 转化率
- 对 strict dataset 的净收益通常高于继续扩 corpus

### P3. 增加 `useful_but_out_of_scope` 标记

**目标**

把“科学上有用，但不属于当前 strict scope”的记录单独标识出来。

**典型场景**

- ibuprofen 没问题，但不是 `5% w/w`
- endpoint 是 `flux / Jss`
- 不是 Franz
- 不是 IVPT / IVRT

**建议改动**

- 在 verification 输出中增加辅助标记，而不是改变主状态定义
- 在 report 中增加 `useful_but_out_of_scope` 计数

**预期收益**

- 不污染 strict dataset
- 为后续 broader-scope 研究保留候选

### P4. 基于人工复核建立小型 calibration set

**目标**

让人工复核结果从“临时核验”变成可持续的 calibration 资产。

**建议改动**

- 把 `review_sheet.csv` 映射为 evaluation gold subset
- 固定一套最小指标：
  - verified precision
  - unresolved salvage precision
  - rejected confirmation rate
  - route-level keep rate

**候选落点**

- `evaluation/`
- `reports/`

**预期收益**

- 后续每轮优化都有稳定对照
- 减少“感觉上变好了”的主观判断

### P5. 设计 selective LLM adjudication layer

**目标**

作为第二意见层，而不是替代主 verifier。

**建议设计**

- 新增模块：`verification/llm_adjudicate.py`
- 只处理：
  - 高风险 `verified`
  - 高价值 `unresolved`
  - `figure / mixed` 记录
  - rule-verifier 与 evidence pattern 冲突的记录

**建议输出**

- `llm_scope_verdict`
- `llm_record_verdict`
- `llm_confidence`
- `llm_rationale`
- `llm_recommended_status`
- `llm_disagrees_with_rule_verifier`

**为什么不直接替代 rule verifier**

- strict scope 需要硬边界
- rule verifier 更便宜、更稳定、更可重复
- 纯 LLM 终审会增加 correlated error 和 prompt sensitivity

### P6. 继续强化 figure 的 record-level acceptance

**目标**

当前 figure 不再主要死在 digitization，而是更多死在最终 acceptance。

**建议改动**

- figure 记录必须绑定更强的 formulation anchor
- figure 记录要求更明确的 area / endpoint / device paper-level support
- 继续限制 paper-level figure failure 的过度传播

**预期收益**

- 提升 figure route 的 precision
- 避免 figure 成为 `verified` 污染源

## 4. 推荐执行顺序

建议按下面顺序落地，而不是并行大改：

1. `P0 strict verification hardening`
2. `P1 route-aware acceptance`
3. `P2 unresolved recovery lane`
4. `P3 useful_but_out_of_scope tagging`
5. `P4 calibration subset`
6. `P5 selective LLM adjudication design`
7. `P6 figure record-level acceptance`

## 5. 当前不建议优先做的事

- 继续盲目增大 `max-results`
- 现在就上多数据库 corpus merging
- 现在就把 manual review 融进生产 pipeline
- 现在就用 LLM adjudication 直接替代 rule-based verification

## 6. 和当前架构的关系

这份任务清单是在当前现有架构上做强化，不要求再推翻：

- `corpus -> triage -> access -> routing -> extractors -> assembly -> verification -> patchers -> reports`

也就是说，下一阶段的主目标不是“再重构一轮”，而是：

- 收紧严格判定
- 提高 recovery 收益
- 让自动 `verified` 更接近人工 `keep`
