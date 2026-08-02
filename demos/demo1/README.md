# Demo 1 rebuild

`rebuild_demo1.py` 从本目录随附的归档输入重新生成论文 Demo 1 的 Table 4、few-shot calibration 和 Figure 10。脚本不包含绝对路径；所有结果写入 `outputs/`。

## 运行

环境需提供 Python、NumPy、SciPy、scikit-learn 和 Matplotlib。

```text
python rebuild_demo1.py
```

脚本以自身位置为基准，从 `data/` 读取：

- `data/dataset.csv`
- `data/solubility_table.csv`

输入验证结果：17 条记录，train/test=5/12；溶解度 7 条实测、10 条估算；两张输入表联结 17/17，`log10_solubility` 最大差为 0。

## Table 4 验证

| Model | Feature set | RMSE | R2 | rho | r | within 2x |
|---|---|---|---|---|---|---|
| Ridge | composition_only | 0.2058879943 — ROUNDING_MATCH | -0.5787951069 — ROUNDING_MATCH | 0.6153846154 — ROUNDING_MATCH | 0.6749445784 — ROUNDING_MATCH | 9/12 — EXACT |
| Ridge | composition+solubility | 0.1988476703 — ROUNDING_MATCH | -0.4726676281 — ROUNDING_MATCH | 0.7062937063 — ROUNDING_MATCH | 0.7337540718 — ROUNDING_MATCH | 9/12 — EXACT |
| GPR | composition_only | 0.3316821863 — ROUNDING_MATCH | -3.0973967722 — ROUNDING_MATCH | 0.6009052505 — ROUNDING_MATCH | 0.3784035234 — ROUNDING_MATCH | 5/12 — EXACT |
| GPR | composition+solubility | 0.3287842950 — ROUNDING_MATCH | -3.0261120263 — ROUNDING_MATCH | 0.2183152727 — ROUNDING_MATCH | 0.3919664589 — ROUNDING_MATCH | 5/12 — EXACT |

合计：4 个 EXACT、16 个 ROUNDING_MATCH、0 个 MISMATCH。连续指标只达到近似一致，是因为论文表格按 2–3 位小数显示；GPR 另有 sklearn 1.5.0 与归档 1.7.0 的 optimizer 数值漂移，但不改变任何论文显示格、排序或 within-2x 计数。

逐格证据见 `table4_comparison.csv`。

## few-shot 验证

固定配置：k={3,5}；每组 80 次；`SeedSequence(42).spawn(80)`；四组复用同一组 child sequence；无放回抽样；样本标准差 `ddof=1`。

| 目标 | 重建值 | 状态 |
|---|---:|---|
| k=5 composition+solubility mean RMSE 0.114 | 0.1140884708 | ROUNDING_MATCH |
| k=5 composition+solubility Spearman SD 0.186 | 0.1857893636 | ROUNDING_MATCH |
| k=5 composition_only Spearman SD 0.311 | 0.3111031815 | ROUNDING_MATCH |

逐项证据见 `fewshot_comparison.csv`；320 次明细见 `fewshot_raw_runs_rebuilt.csv`。

## Figure 10

`fig10_demo1_rebuilt.pdf` 与 `fig10_demo1_rebuilt.png` 重建：

- A：四组 zero-shot actual-vs-predicted、identity line、±2× band；
- B：四组 few-shot Spearman step-density、均值线和中位数线；
- Arial 8–10 pt、Wong 配色、无网格、0.6 pt axes、PNG 600 DPI、PDF vector。

科学内容与归档图一致到上述数值精度。具体 histogram bins、marker size、透明度和 subplot spacing 在原仓库未留脚本或配置，因此由归档成品图重建，像素级布局不宣称完全相同。

## 产出

- `rebuild_demo1.py`：单文件可执行重建脚本
- `table4_rebuilt.csv`：四组重建汇总
- `table4_comparison.csv`：Table 4 逐格比较
- `predictions_zero_shot_rebuilt.csv`：48 条 zero-shot 预测
- `fewshot_raw_runs_rebuilt.csv`：320 次 few-shot 明细，含 calibration/evaluation record IDs
- `fewshot_results_rebuilt.csv`：四组 few-shot 汇总
- `fewshot_comparison.csv`：三个指定数字比较
- `fig10_demo1_rebuilt.pdf` / `.png`：Figure 10
- `run_summary.json`：输入验证、参数、软件版本和状态计数

完整 assumptions、差异解释和视觉比对将在发布文档中说明。
