# 工程约定（仅修改工程时读）

## 目标与验收

让没有本次聊天历史的 agent 从 AGENTS 开始，找到当前候选、真实证据、未完成步骤和下一步；换候选无需重写技能，也不继承旧结果。项目支持这篇 AMP 案例的计算证据链，不把计算结果当作抗菌活性实测。

验收看实际行为：入口能运行、旧快照哈希不变、新 case 独立、路由能命中、交接能正确识别未完成工作。执行记录见 [VALIDATION.md](VALIDATION.md)。

## 组织决策

- 入口和索引只负责启动、选择技能；不塞概念课、API 说明或具体案例结论。
- 四个阶段足够：来源/序列、结构、基因环境/文献、报告/交接。只在真实任务边界需要时新增 skill，同时更新 INDEX。
- 参数写 case.json；当前科学进度只写 STATE.md；证据摘要写 EVIDENCE.md。工程变动写 WORKING.md。
- `scripts/case.py` 是稳定入口，`fetch_candidate.py` 是数据库抓取/核验实现。当前规模不另建空 src、服务、数据库或前端。
- 数据目录以 case 隔离，每次运行有新目录；原始记录不覆盖。下载时间与派生分析时间独立。
- 用户要求的是本项目内的 skill 路由；无需把四个 skill 注册到全局。若挂进已有工作区，其总入口只需增加一条指向本项目 AGENTS 的路由。
- skill 中不得出现本案 accession、物种、长度、切割位置、数据库基因标签或固定命中结论。输入从 case 与实际记录读取。
- 完成阶段后先保存证据和 STATE；修改工程后记录 WORKING 并提交本项目 Git。不要向参考仓库推送。

## Skill 写作约定

依据下方 bestpractice_skill_writing.md：明确目标、可判断的验收、可用资源/边界和输出规格；章节可按任务组织，不要求套同一模板。
验收针对当前子任务，不因一个 skill 覆盖多个能力就强制执行完整流程。硬约束落在证据、身份、必要依赖和产物上；方法与工具的选择保留给 agent，推荐方法明确写成建议。
只将本项目实际遇到的问题记为“已知教训”，附可定位记录；一般证据边界正常写明，不伪装成发生过的失败。入口保持薄，新增或改变触发范围时才改 INDEX。

## 参考来源

参考仓库：[grapeot/context-infrastructure](https://github.com/grapeot/context-infrastructure)。
本次读取固定在提交 `c747317c90af9d1071a1157fa95e3766edcb6441`（提交日期 2026-10-24，核对日期 2026-10-26）。

具体参考：

- [AGENTS.md](https://github.com/grapeot/context-infrastructure/blob/c747317c90af9d1071a1157fa95e3766edcb6441/AGENTS.md)：入口和局部规则。
- [rules/skills/INDEX.md](https://github.com/grapeot/context-infrastructure/blob/c747317c90af9d1071a1157fa95e3766edcb6441/rules/skills/INDEX.md)：索引只路由，命中后读完整技能。
- [rules/skills/project_scaffold.md](https://github.com/grapeot/context-infrastructure/blob/c747317c90af9d1071a1157fa95e3766edcb6441/rules/skills/project_scaffold.md)：工程化入口、文档、稳定命令、验证和 Git。
- [bestpractice_skill_writing.md](https://github.com/grapeot/context-infrastructure/blob/c747317c90af9d1071a1157fa95e3766edcb6441/rules/skills/bestpractice_skill_writing.md)：以目标、产物、证据和验收约束工作。

本项目借鉴组织方式，文档与实现按本任务重新组织；没有复制作者的个人记忆、模型路由、cron 或部署系统。参考仓库 README 声明 MIT，但本次目录未见独立 LICENSE；此处仅准确记录来源，不替上游补造许可证。

