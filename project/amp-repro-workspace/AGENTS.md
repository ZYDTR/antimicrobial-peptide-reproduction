# AMP 计算复现工作区

目标：沿来源文章的证据链复现计算分析，逐项区分作者报告、我们重跑的结果与未知；范围见 `docs/PAPER.md`。

## 接手

1. 读 [INDEX.md](INDEX.md)。
2. 在本项目根目录运行 `python3 scripts/case.py status`；它只显示当前编号、配置位置和 `STATE.md`。无 Python 时读 `project.json`，再读对应 `case.json` 与 `STATE.md`。
3. 按用户任务或 `STATE.md` 的下一步，只读命中的一个 skill；跨阶段时再加载下一份。
4. 实际执行、保存证据，然后更新本 case 的 `STATE.md`：状态、输出路径、阻塞和下一步。

## 工作约定

- Python 3.9+；内置入口仅用标准库。相对命令从项目根目录执行；case 内链接以 case 目录为基准。
- `project.json` 只选择案例，`case.json` 只放本案参数，`STATE.md` 是进度唯一依据；入口和索引不抄进度。
- 不默认读取全部 skills、原始 JSON/PDB、整篇 PDF 或历史日志。只读当前判断需要的文件；长结果落盘，向上下文返回路径和摘要。
- 以实际产物判定完成；预测、作者报告、服务失败和我们测得的结果不得混写。下载时间、分析时间分开。
- 每次新抓取/搜索写新的 `data/<UTC时间>-<步骤>/`；保留原始响应、参数、版本和校验值。派生表放 `results/`，综合报告放 `reports/`。
- 换候选用 `case.py new`，再 `use`；不要修改旧 case 的 accession 来复用旧结论。未知值留空，不猜补。
- 保持同一 case 单写入者；并行任务写各自运行目录，由主 agent 汇总状态。环境变量和凭证不进案例或证据。
- 改工程时读 `docs/PROJECT.md`，更新 `docs/WORKING.md` 并提交 Git；科学进度只更新本案状态与证据。

