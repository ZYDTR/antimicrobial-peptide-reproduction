# 工具与环境（按阶段读）

需要了解 README 各部分、全部 40 项工具与本次复现的关系时，读 [SCIENCE_SKILLS_MAP.md](SCIENCE_SKILLS_MAP.md)；执行单一阶段时直接使用下表对应入口。

## 项目内已提供

`python3 scripts/case.py --help` 查看稳定入口。Python 3.9+，仅标准库，无需安装完整 agent 平台。
`status`、`new`、`use`、`check` 离线；`fetch` 联网访问 UniProt/AlphaFold DB，下载既有预测，不运行 AlphaFold 推理。
`fetch_candidate.py` 支持完整、序列匹配的单模型；缺模型、多模型或片段时保留已有记录，交由 agent 明确处理。

## 可选的 Google Science 工具

官方仓库：[google-deepmind/science-skills](https://github.com/google-deepmind/science-skills)。
本项目参考版本：`4de6786171f1479026da5d3a00f110703c8ba35e`（2026-10-26 核对；不是已确认的原演示版本）。

只打开当前任务命中的工具说明；若已在运行环境中可用，直接使用现有能力并记录版本。否则可把官方仓库放在被 Git 忽略的 `tools/science-skills/`，读取对应文件后按其真实依赖安装和运行。不要一次把全部工具说明塞进上下文。

| 任务 | 固定版本的官方说明 |
|---|---|
| UniProt 查询 | [uniprot_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/uniprot_database/SKILL.md) |
| BLAST / 序列相似 | [protein_sequence_similarity_search](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/protein_sequence_similarity_search/SKILL.md) |
| AlphaFold DB | [alphafold_database_fetch_and_analyze](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/alphafold_database_fetch_and_analyze/SKILL.md) |
| Foldseek | [foldseek_structural_search](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/foldseek_structural_search/SKILL.md) |
| NCBI 序列与基因坐标 | [ncbi_sequence_fetch](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/ncbi_sequence_fetch/SKILL.md) |
| 结构记录 / 查看 | [pdb_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/pdb_database/SKILL.md)、[pymol](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/pymol/SKILL.md) |
| 文献 | [pubmed_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/pubmed_database/SKILL.md) |

注意：相似序列工具可能默认走 MMseqs2。要复现文章的 BLAST 环节，应明确选择 BLAST 和 Swiss-Prot；EBI 数据库标识可为 `uniprotkb_swissprot`，实际提交前以所用接口说明核对。

当前固定版本的 BLAST 脚本建议配置 `USER_EMAIL`，无邮箱时会警告但继续提交；服务是否接受取决于实际响应，不能预先当作必然阻塞。SKILL.md 的前置说明与后文对此有不一致，执行时核对代码/服务响应。NCBI API key 可选；仅使用已有有效配置，不编造凭证。官方脚本可从用户主目录的 .env 加载变量，本项目 .env.example 不会自动替它配置。

本案序列步骤需明确 BLAST 与 `uniprotkb_swissprot`；官方技能默认 MMseqs2，BLAST wrapper 默认库为 UniProtKB。Foldseek wrapper 默认同时检索 `pdb100,afdb50`，若本次目标是实验结构比较，应明确数据库并记录版本。

## 最小运行留痕

每次外部任务在 `cases/<case_id>/data/<UTC时间>-<步骤>/` 保存输入标识/哈希、完整参数、服务 URL、工具版本/commit、数据库版本（若服务返回）、job_id、时间、状态及原始结果。拿不到的字段写 null 和原因。

为使 `case.py check` 能校验后续产物，单文件 manifest 使用 `{"accession":"当前编号","raw_file":"result.json","sha256":"实际文件哈希"}`，其余任务元数据可增补；多文件使用 `{"accession":"当前编号","downloads":[{"file":"result.json","sha256":"实际哈希","role":"blast_result"}]}`。文件名相对于 manifest 所在目录。填写真实值后保存，勿把示例占位值当成结果。

轮询在脚本或工具内部进行，避免每次等待都重新调用大模型。完整结果留磁盘，先向 agent 返回命中数、前几条与路径；需判断时再展开更多。

官方序列/Foldseek 工具生成 Markdown 摘要和原始 JSON；按其约定优先读摘要，原始文件保留给专用程序校验。wrapper 不生成本项目的 manifest，需另记本案输入与实际参数并对归档文件计算哈希。摘要未提供的指标不能补造。

下载失败、超时或没有拿到结果时记录 blocked/needs_review；只有成功完成的搜索结果才能解释为“未检出”。

## 概念的官方来源

按疑问再查，而非启动时全读：

- UniProt 的 PE 等级：[User manual](https://web.expasy.org/docs/userman.html)。
- ProtNLM：[UniProt help](https://www.uniprot.org/help/ProtNLM)。
- 信号肽注释：[UniProt SAM](https://www.uniprot.org/help/sam)、[SignalP](https://services.healthtech.dtu.dk/services/SignalP-6.0/)。
- BLAST 统计：[NCBI FAQ](https://blast.ncbi.nlm.nih.gov/doc/blast-help/FAQ.html)。
- Foldseek 指标与用法：[官方仓库](https://github.com/steineggerlab/foldseek)。

