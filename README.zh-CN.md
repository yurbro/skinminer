# SkinMiner

SkinMiner 将皮肤药物制剂文献转换为具有证据追溯和明确策略审计的结构化记录。

> **论文：** *SkinMiner: An LLM-powered data mining framework for dermal drug formulations*  
> **作者：** `<TO_FILL>`  
> **状态：** [Manuscript under review，稿件审理中]

## 功能说明

SkinMiner 检索候选文献，解析获准访问的全文，将证据路由至文本、表格或图片提取器，并组装类型化的制剂记录。系统依据明确的科学接受策略验证每条记录。系统保存证据定位信息与失败原因以支持审计。仓库还提供处理后的金标准、论文聚合结果和两个可复现的建模 Demo。

## 管线概览

```text
语料 → 初筛 → 访问解析 → 路由 → 提取器 → 组装 → 验证 → 修补器 → 报告
```

各阶段的数据契约和数据流见 [docs/architecture.md](docs/architecture.md)。

## 安装

SkinMiner 支持 Python 3.11 和 3.12。Python 3.11 与已验证的重建环境一致。

```bash
git clone https://github.com/yurbro/skinminer.git
cd skinminer
python -m venv .venv
```

安装或运行 SkinMiner 前先激活环境。POSIX shell 使用：

```bash
source .venv/bin/activate
```

Windows PowerShell 使用：

```powershell
.venv\Scripts\Activate.ps1
```

安装软件包：

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

`pyproject.toml` 以宽松兼容范围声明实际 import 所需的最小依赖。`requirements-lock.txt` 精确固定用于验证的直接依赖版本。复现论文结果时使用锁定文件：

```bash
python -m pip install -r requirements-lock.txt
```

复制环境变量模板并填写必需值：

```bash
cp .env.example .env
```

使用 OpenAI 提取时设置 `OPENAI_API_KEY`，使用 Unpaywall 访问时设置 `UNPAYWALL_EMAIL`。仅在选择 Anthropic provider 时设置 `ANTHROPIC_API_KEY`。仓库不会提交 `.env`。运行依赖 API 的命令前，请把其中的值加载到当前 shell 环境。

## 快速开始

离线验证仓库附带的合成 fixture：

```bash
python -B -m evaluation.validate_gold_labels --gold-jsonl evaluation/fixtures/gold_labels.small.jsonl
```

预期输出为 `Validated gold-label entries: 1`。该命令不访问网络，也不消耗模型 token。

## 复现论文

### 评测指标

```bash
python -m evaluation.score_run \
  --gold-format round2 \
  --provider gpt \
  --policy-level v2 \
  --gold-csv evaluation/gold/gold_set_round2_annotation.csv
```

预期关键数值为：verified 25 条，scope true positive 25 条，scope false positive 0 条，scope precision 100%，scope-and-value true positive 24 条，end-to-end precision 96%。同一审计还给出 rejected 12/12 正确、unresolved 0/44 被标记为应保留。

### Demo 1

```bash
python demos/demo1/rebuild_demo1.py
```

预期关键数值为：Table 4 的 20 格在论文显示精度下全部匹配。脚本报告 4 格 EXACT 和 16 格 ROUNDING_MATCH。k=5 时，脚本复现 RMSE 0.114，以及含溶解度时 Spearman SD 0.186、不含溶解度时 Spearman SD 0.311。

### Demo 2

```bash
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_4feature.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_figure.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_sweep.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_ratio_lines_redraw.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_mechanism.py
python demos/demo2/outputs/phase2_demo2_modelling/run_demo2_feature_space_figure.py
```

预期关键数值为：Xiao 到 Bolla 的迁移结果为 Spearman 0.43、conventional R² -0.32、3/8 个预测落在 twofold 范围内。方案审计标记 5/8 个维度。PC1 与 PC2 解释 88.8% 的特征空间方差，0/8 个文献数据点位于内部数据的四维超矩形内。

论文数字与文件的完整追溯关系见 [docs/paper_mapping.md](docs/paper_mapping.md)。复现 assumptions 与版本敏感性见 [docs/reproducibility.md](docs/reproducibility.md)。

## 仓库结构

```text
access/          解析获准访问的文献内容与来源 provenance。
assembly/        将提取片段合并为规范记录。
configs/         定义运行配置与检索配置。
corpus/          构建并冻结书目语料。
data/frozen/     保存发布的书目语料快照。
demos/demo1/     重建 Watkinson Table 3、Table 4、few-shot 结果与 Fig. 10。
demos/demo2/     复现跨方案迁移、ratio sweep 与特征空间分析。
detection/       将证据路由至文本、表格、图片或混合提取路径。
docs/            记录架构、策略、失败模式、provenance 与复现方法。
evaluation/      载入金标准，计算累计策略指标并运行回归测试。
experiments/     保存论文分析与审计脚本。
extractors/      从文本、表格和图片中提取结构化记录。
patchers/        对记录执行范围有限的确定性修正。
policies/        实现四个 acceptance level。
reports/         构建聚合运行报告。
results/         保存筛选后的聚合运行报告与论文绘图输入。
schemas/         定义共享的 Pydantic 数据契约。
triage/          筛选候选文献并确定优先级。
utils/           提供 I/O、模型客户端、manifest、resume 和单位工具。
verification/    验证科学范围并裁决模糊记录。
```

## 本仓库不包含的内容

公开仓库不包含：

- 原文 PDF，因为不同出版商的再分发权利不同
- figure 页面图像、crops、masks、overlays 和 mapping zooms，因为这些文件复制了来源材料
- 记录级 run JSONL，因为它含有大量来源文本并形成较大的归档包
- Claude 原始审计包，因为其中含有来源文本和第三方联系信息

复现论文图表与指标所需的聚合文件保留在公开仓库中。记录级研究资产计划进入受控的 Zenodo 或 OSF 归档。可通过仓库 issue tracker 请求元数据或访问说明。任何访问仍需经过版权、隐私与研究治理审查。

## 许可

SkinMiner 源代码采用 [Apache License 2.0](LICENSE)。[NOTICE](NOTICE) 记录项目署名、资助信息，以及公开金标准数据适用的独立条款。

`evaluation/` 下的金标准数据依据 [LICENSE-DATA](LICENSE-DATA) 采用 CC BY 4.0，Apache-2.0 不适用于这些数据。第三方书目元数据与来源文本继续受其原始条款约束。处理后的金标准 CSV 通过 `source_license`、`source_license_url`、`source_license_source`、`source_license_checked_at` 和 `verbatim_action` 保存来源与许可信息。

金标准发布版保留书目标题与事实性浓度字符串，也保留标注者自行撰写的说明。来源许可允许再分发时，发布版保留来源引文。来源许可不允许再分发时，发布版用 DOI、页码以及 figure 或 table locator 替换引文。

## 引用

```bibtex
@article{skinminer2026,
  author = {<TO_FILL>},
  title = {SkinMiner: An LLM-powered data mining framework for dermal drug formulations},
  year = {2026},
  note = {Manuscript under review},
  url = {https://github.com/yurbro/skinminer}
}
```

GitHub 引用元数据见 [CITATION.cff](CITATION.cff)。

## 致谢

本研究由 China Scholarship Council 与 University of Surrey 联合资助，Grant No. 202306440060。
