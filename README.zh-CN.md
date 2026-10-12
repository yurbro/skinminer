<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/skinminer-logo-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/skinminer-logo-light.png">
  <img alt="SkinMiner" src="assets/skinminer-logo-light.png" width="760">
</picture>

### 面向皮肤药物制剂数据的证据感知文献挖掘

将分散在科学文献正文、表格和图片中的实验测量，转化为经过科学规则验证、并具有字段级证据溯源的结构化记录。

[![Python 3.11–3.12](https://img.shields.io/badge/Python-3.11%E2%80%933.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: Apache-2.0](https://img.shields.io/badge/Code-Apache--2.0-4C1)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Gold%20data-CC%20BY%204.0-lightgrey)](LICENSE-DATA)
[![Status: research software](https://img.shields.io/badge/Status-Research%20software-6f42c1)](#项目状态与适用范围)

🌐 **语言：** [English](README.md) · **简体中文**

[快速开始](#快速开始) · [系统架构](docs/architecture.md) · [接受策略](docs/policies.md) · [复现说明](docs/reproducibility.md) · [问题反馈](https://github.com/yurbro/skinminer/issues)

</div>

> **项目状态：** SkinMiner 是正在持续开发的研究软件（`v0.1.0`）。配套论文 *SkinMiner: LLM-powered data mining to accelerate formulation design for skin products* 已于 2026 年 10 月 12 日投稿至 *International Journal of Pharmaceutics*，通讯作者为 Tao Chen。截至该日，尚未独立确认编辑处理、外部同行评审或正式接收状态。下文结果仍为本仓库的验证基准。

## 为什么需要 SkinMiner？

稳态通量、渗透系数、累积渗透量和滞后时间等定量皮肤渗透数据，是数据驱动型经皮制剂设计的重要基础。然而，正确解释这些数据所需的数值、制剂组成和实验条件，往往分散在正文、表格和图片中。

单次端到端 LLM 调用可以生成看似合理的结构化结果，却难以稳定回答定量复用中最关键的问题：

- 这条记录是否真正符合研究范围？
- 数值是否对应正确的制剂和评价终点？
- 每个字段究竟来自文献中的哪个位置？
- 提取过程和接受决策能否被审计与复现？

SkinMiner 通过模块化多模态管线处理这些问题，将文献发现、证据路由、信息提取、记录组装和科学验证分开执行。只有当记录具有可定位的来源证据，并满足明确的接受策略时，系统才会将其保留。

## SkinMiner 的核心特点

| 能力 | SkinMiner 的实现方式 |
|---|---|
| **多模态提取** | 根据研究中的证据形式，将文献分别路由至文本、表格、图片或混合提取器，而非强制所有文档使用同一个提示词处理。 |
| **统一研究规范** | 使用版本化的目标定义，使文献检索标准与记录级接受标准保持一致。 |
| **基于证据的验证** | 将信息提取与最终裁决分离，分别标记为已验证、待解决或拒绝。 |
| **字段级证据溯源** | 保存正文段落、表格单元格和图片面板的定位信息，同时记录失败原因和修复历史。 |
| **类型化、可恢复执行** | 各阶段通过 Pydantic 记录交换数据，并保存 manifest 和中间产物，支持检查、暂停与继续运行。 |
| **模型供应商中立层** | 同一套结构化工作流可使用 OpenAI 或 Anthropic 模型，并允许不同阶段选用不同模型。 |
| **面向决策的输出** | 生成适用于后续建模的统一数据，同时保留判断不同数据集能否合并所需的实验与证据元数据。 |

## 工作流程

~~~mermaid
flowchart LR
    A[文献发现与初筛] --> B[解析可访问全文]
    B --> C[证据路由]
    C --> D[提取与记录组装]
    D --> E[验证与报告]
~~~

1. **文献发现与初筛：** 从 Europe PMC 或用户提供的文档列表中识别候选研究。
2. **解析许可内容：** 在保留来源信息的前提下获取允许访问的内容；可用时优先采用结构化 XML 或 HTML，其次为 PDF。
3. **证据路由：** 将文献分配至文本、表格、图片、混合或待解决路径。
4. **提取与记录组装：** 将制剂、实验方案、屏障、评价终点和证据字段组装为统一的数据模式。
5. **验证与报告：** 按累积式科学接受策略裁决每条候选记录，并完整保留已验证、待解决和拒绝结果。

各阶段的数据契约见 [docs/architecture.md](docs/architecture.md)，当前策略层级见 [docs/policies.md](docs/policies.md)。

## 输出记录

一条标准 SkinMiner 记录可以包含：

- 论文身份信息与 DOI
- 活性成分与制剂组成
- IVPT/IVRT 研究类型、扩散装置、膜或皮肤屏障以及受体条件
- 给药剂量、扩散面积、评价终点类型、数值、单位和时间
- 证据模态路径与字段级来源定位
- 验证状态、策略层级、失败原因和确定性修复历史

该结构使下游使用者既能查看提取出的数值，也能审查系统接受该数值的依据。

## 当前验证结果

仓库内置的布洛芬评估使用了人工标注的 130 条金标准记录，其中 25 条符合研究范围。在推荐的 Extended 接受层级下，当前 GPT 配置得到以下结果：

| 评估问题 | 仓库验证结果 |
|---|---:|
| 保留记录是否符合研究范围？ | **25/25 条记录通过验证；范围精确率 100%** |
| 保留数值是否与来源一致？ | **24/25；端到端数值准确率 96%** |
| 抽样排除结果是否处理正确？ | **12/12 条抽样拒绝正确；44 条待解决记录中没有应被保留的记录** |
| 多次运行的结果是否稳定？ | **5 次运行形成由 24 条记录组成的稳定核心；验证记录数的变异系数为 13%** |
| 不采用模块化验证会发生什么？ | 最强单次调用基线覆盖了 **24/25** 条金标准记录，但同时输出 **288** 条仍需进一步审查的原始记录 |

这些数值仅描述当前发布的评估配置，并不代表系统在所有药物、评价终点或文献领域中的表现。可使用以下命令重新计算策略指标：

~~~bash
python -m evaluation.score_run \
  --gold-format round2 \
  --provider gpt \
  --policy-level v2 \
  --gold-csv evaluation/gold/gold_set_round2_annotation.csv
~~~

## 应用演示

SkinMiner 提供两个可复现的演示，用于展示经过验证的文献记录在提取后的实际用途。

### Demo 1——基于文献数据的迁移建模

该演示重建 Watkinson 制剂数据表，并评估从相关共溶剂研究中提取的记录能否支持通量排序与预测。重建结果在原文显示精度下与 Table 4 的全部 20 个单元格一致，并复现了文中报告的少样本分析。

~~~bash
python demos/demo1/rebuild_demo1.py
~~~

### Demo 2——文献数据是否应该与内部实验数据合并？

该演示在决定合并建模前，对 Xiao 至 Bolla 的跨研究迁移和不同比例的数据混合进行检验。在当前发布的数据对中，实验方案不匹配和多变量特征空间分离共同解释了为什么引入文献数据未能减少所需的内部实验数量。这个有价值的负结果之所以能够被诊断，正是因为提取数据保留了充分的实验元数据。

~~~bash
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_4feature.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_sweep.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_mechanism.py
~~~

所有结果数字与仓库文件的对应关系见 [docs/paper_mapping.md](docs/paper_mapping.md)，假设条件和版本敏感性见 [docs/reproducibility.md](docs/reproducibility.md)。

## 快速开始

### 1. 安装

SkinMiner 支持 Python 3.11 和 3.12，其中 Python 3.11 与当前验证和重建环境一致。

~~~bash
git clone https://github.com/yurbro/skinminer.git
cd skinminer
python -m venv .venv
~~~

激活虚拟环境：

~~~bash
# POSIX
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
~~~

安装软件包：

~~~bash
python -m pip install --upgrade pip
python -m pip install -e .
~~~

如需复现当前发布的结果，请安装锁定环境：

~~~bash
python -m pip install -r requirements-lock.txt
~~~

### 2. 配置可选服务

~~~bash
cp .env.example .env
~~~

使用 OpenAI 驱动的阶段时设置 `OPENAI_API_KEY`，使用 Unpaywall 时设置 `UNPAYWALL_EMAIL`。仅在选择 Anthropic provider 时设置 `ANTHROPIC_API_KEY`。请勿提交 `.env` 文件。

### 3. 运行离线冒烟测试

~~~bash
python -B -m evaluation.validate_gold_labels \
  --gold-jsonl evaluation/fixtures/gold_labels.small.jsonl
~~~

预期输出为 `Validated gold-label entries: 1`。该命令不会访问网络，也不会消耗模型 token。

### 4. 查看管线配置

~~~bash
python run_pipeline.py --list-run-profiles
python run_pipeline.py --list-query-profiles
python run_pipeline.py --help
~~~

预设运行配置包括 `budget_lean`、`text_table_baseline`、`balanced_full` 和 `figure_deep`，使用者可以明确权衡成本、覆盖率和图片处理深度。

## 仓库导航

| 路径 | 用途 |
|---|---|
| `run_pipeline.py` | 主工作流入口 |
| `corpus/`、`triage/`、`access/` | 文献发现、筛选和许可内容解析 |
| `detection/`、`extractors/` | 证据模态路由和文本/表格/图片提取 |
| `assembly/`、`schemas/` | 标准记录构建和类型化数据契约 |
| `policies/`、`verification/`、`patchers/` | 科学范围检查、证据裁决和可审计的确定性修复 |
| `evaluation/` | 金标准载入、评分、验证 fixture 和回归检查 |
| `demos/` | 可复现的下游建模演示 |
| `results/`、`reports/` | 筛选后的聚合结果与运行报告构建工具 |
| `docs/` | 架构、策略、证据溯源、失败模式和复现文档 |

## 公开发布边界

本公开仓库包含源代码、冻结的书目快照、处理后的 130 条金标准 CSV、聚合报告、绘图输入和可复现演示。以下内容不在公开仓库中：

- 再分发权限因出版商而异的论文 PDF
- 从来源论文生成的页面图片、裁剪、掩膜、叠加图和映射放大图
- 包含大量来源文本的记录级运行归档
- 包含来源文本或联系信息的原始第三方审计包

检查上述指标所需的聚合产物仍然公开。受限研究材料的申请与访问需遵守版权、隐私和研究治理要求。

## 项目状态与适用范围

SkinMiner 目前已在布洛芬皮肤渗透案例上完成验证。其架构具有扩展至其他场景的设计基础，但尚未在其他活性成分、更多评价终点、补充材料或全部出版商格式中建立性能证据。欢迎通过 [issue tracker](https://github.com/yurbro/skinminer/issues) 提交贡献、错误报告和复现反馈。

## 许可

- 源代码：[Apache License 2.0](LICENSE)
- `evaluation/` 下的金标准数据：[CC BY 4.0](LICENSE-DATA)
- 第三方书目元数据和来源材料：遵循原始来源条款

处理后的金标准记录保留来源许可与证据溯源字段，并使用书目信息及页码、表格或图片定位替代不允许再分发的原文引述。

## 引用

配套论文已投稿，尚无正式发表的文章引用信息。引用软件时，请按仓库引用：

~~~bibtex
@software{skinminer2026,
  author  = {Zhang, Yu and Wang, Xilu and Tsaoulidis, Dimitrios and Chen, Tao},
  title   = {SkinMiner: LLM-powered data mining to accelerate formulation design for skin products},
  year    = {2026},
  version = {0.1.0},
  url     = {https://github.com/yurbro/skinminer}
}
~~~

## 致谢

本研究由国家留学基金管理委员会（China Scholarship Council）与萨里大学（University of Surrey）联合资助，项目编号为 202306440060。
