---
name: report-checkpoint
description: "汇总复现结论、原文与本次结果差异、证据缺口、token 账目，并留下下一位 agent 能接续的检查点；报告或交接时读取。"
---

# 报告与检查点

## 目标与输入

按当前 case 的 STATE、EVIDENCE 与必要产物写结论，不把计划当执行记录。
下文 CASE 表示当前案例目录。按用户要求产出阶段报告、最终报告或交接；阶段报告不要求补跑所有 pending 的研究任务。
只有引用或争议需要时再读原文/大文件。报告针对当前 case，不沿用别的候选结果。

## 科学报告

写入 `CASE/reports/`，至少回答：

- 研究对象、来源、数据库快照日期与本次参数。
- 作者报告了什么；我们实际做了什么；结果一致或不同在哪里。
- 主要结论的证据路径、版本与适用范围。
- 哪些是预测或推断，哪些仍无实测证据。
- 下一步最能补充哪项证据，以及实际阻塞。

“复现了分析路线”“复现了某项数值”“有新的生物学验证”按各自证据使用。作者未披露设置保持未知；本次选择不能补成原始参数。
报告用 Markdown；主要主张以现有 evidence ID 或相对证据路径定位，并标明作者报告、我们的观察、推断或未知。解释深度按读者调整，章节顺序与叙述方式由 agent 选择。

## 检查点

STATE.md 是科学进度唯一依据，使用 pending / running / done / needs_review / blocked。
每个更新步骤记录状态、最后核对日期、输出路径和限制；只有实际执行中才写 running。
仍有待接续工作时，next_action 需说明目标、对应 skill、输入、预期产物和阻塞；只有依赖确实要求时才固定执行顺序。没有进展就写原因。当前请求已完成时不凭空追加任务；项目已有 pending 保留，项目确无后续任务时写“无”及完成依据。
EVIDENCE.md 汇总主张和证据；短观察放 STATE，长原始数据留 data，不回填入口/索引。工程变更单独写 docs/WORKING.md。

## 可选 token / 费用记录

服务真实返回 usage 时，向 `CASE/results/usage.jsonl` 逐调用追加；未返回标 unknown。
记录 provider、model、request_id、时间、input_tokens、cached_input_tokens、output_tokens、reasoning_tokens、计费口径和原始 usage 路径；未知字段为 null。
cached input 是 input 子集，不再次相加。output 是否含 reasoning 依提供方口径确认，避免重复；不能确认时保留原始字段。
实测、工程估算与预算分别标记。缺完整日志时不声称掌握“整个实验”的 token 总数；数据库计算成本不混成 LLM token。

## 完成判断

当前报告/交接可完成的条件：主要结论逐项有证据或明确标未知；原文主张与本次结果分开；状态与实际产物一致；下一位 agent 能据此继续已有任务，或判断当前范围已经结束。报告完成不等于所有研究步骤完成。
服务或原文缺失仍阻塞时交付已有结果并解释边界，不将 blocked 改 done。
