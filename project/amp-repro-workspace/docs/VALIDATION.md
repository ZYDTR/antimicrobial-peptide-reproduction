# 交付验收

日期：2026-10-26。这里记录工程交付验收，不替代各案例的科学进度。

| 验收 | 实际结果与范围 |
|---|---|
| 已有证据完整性 | `python3 scripts/case.py check` 通过：2 份 manifest、6 个原始文件哈希；检查前后内容和修改时间未变 |
| 原文 | 用户 PDF 的 SHA-256 与导入前一致；提取文本有独立 hash，记录在 sources/manifest.json |
| skill 基本结构 | 四个 SKILL.md 均通过 skill-creator 的 quick_validate.py；入口和技能使用相对路径 |
| 第二编号隔离 | 在临时项目副本创建 P12345 案例，来源/筛选/基因环境为空，所有步骤 pending，没有继承旧证据；创建不切换 active_case |
| 切换与边界 | 显式 use 成功；重复 case、未知 case 和路径穿越被拒绝；旧 case 不被覆盖 |
| 数据被改动 | 临时副本篡改 FASTA 后，check 正确拒绝并报告 SHA-256 mismatch |
| 下载入口适配 | 用本地替身验证向下载器传入选中的 accession、创建两次不同 UTC 目录、派生结果进入 results、STATE 不被自动修改 |
| 真正离线重算 | 在快照副本运行通用下载器的 --offline；序列/PDB/置信度核对通过，重算 97 aa 与平均 pLDDT 88.4988 一致 |
| 冷启动接手 | 无本轮聊天历史的 agent 从 AGENTS → INDEX → status → 单个 source-sequence skill，正确识别候选、未完成项和下一步；未加载全部技能 |

## Skill 写作规范复审（2026-10-26）

- 依据作者 bestpractice_skill_writing.md 对四份技能做局部修订；保留真实身份依赖，把方法建议和产物验收分开。
- 只读情境验收覆盖片段的本地 BLAST、多模型叠合、独立文献任务、检索失败与零结果、阶段报告和项目完成终态；均未实际运行科研任务。
- 复审发现的裁剪对照、结构来源和可选/核心指标歧义已收紧；固定全长对照仅用于需要该对照支撑的主张。
- 四份 skill 的结构校验和本地链接检查通过；AGENTS/INDEX 保持 22/15 行，已有六个原始数据哈希仍通过。脚本、case 参数与科学进度未改。
- Science Skills 关系表与固定版本的 40 个目录逐项比对，无遗漏或重复；分类是本项目用途判断，不是原作者调用日志。

## 如何再次检查

在项目根目录运行：

```bash
python3 scripts/case.py status
python3 scripts/case.py check
```

check 校验当前 case 的原始数据 manifest 和候选身份，不判定科学结论，也不检查 PDF。PDF 的参考哈希在 docs/PAPER.md 与 sources/manifest.json。

创建第二案例、下载适配和故障检查均在一次性副本中进行，未把测试候选或伪造结果留在交付项目。下载适配测试使用替身，**不算第二个真实候选在线抓取成功**。

此次交付没有新运行 BLAST、Foldseek、基因邻域分析或湿实验；也没有完整模型 token 实测记录。公网服务可用性与后续工具依赖要在执行对应阶段时检查。

