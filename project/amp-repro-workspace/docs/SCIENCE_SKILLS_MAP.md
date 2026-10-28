# Google Science Skills 与本次 AMP 复现的关系

本页是按需参考，不加入 agent 的启动必读项。四个本项目 skill 负责目标、证据验收和交接；Google Science Skills 提供可复用的具体工具说明、脚本与资料。工具选择可按任务调整，实际结果须回到当前 case。

## 来源与版本

用户指定的 [README](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/README.md) 已完整核对；临时检出的版本为 `4de6786171f1479026da5d3a00f110703c8ba35e`，核对日期 2026-10-26。[plugin.json](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/plugin.json) 版本是 **1.3.1**。
README 本身没有 40 项技能列表；下表来自该提交下全部 **40 个 SKILL.md 的元数据**，核心技能另核对正文/相关脚本。分类是我们的任务映射，不能当作作者实际调用记录。

## README 各部分的意义

| 部分 | 对本项目的意义 |
|---|---|
| 科研领域概述 | 工具包覆盖多个领域，按当前证据问题选择组件。 |
| SKILL.md / scripts / references | 分别提供说明、执行程序和补充资料；详细资料按需读取。 |
| Antigravity 与 Science plugin | 与原演示相近的集成方式；安装入口为 Customizations → Build with Google → Science → Add。 |
| npx 安装 | README 提供 `npx skills add google-deepmind/science-skills/`；这是技能安装，不会自动执行本案或生成结果。 |
| uv 与 API key | 依赖/服务访问条件；按选用工具配置。AlphaGenome 的 key 不是全包通用前置，ClinVar/OpenAlex 的 key 为可选增额。 |
| 自定义技能 | 插件升级可覆盖安装目录；项目规则与上游工具分开维护。Antigravity 的个人技能目录示例是 `~/.gemini/config/skills/`。 |
| 案例链接 | 便于找演示；不等于获得原会话日志、精确设置或账单。 |
| 许可与声明 | 软件 Apache 2.0、其他材料 CC-BY 4.0，第三方数据有独立条款；按其来源保留许可。README 声明非正式 Google 产品。 |

README 没有提供本篇原始会话的精确模型快照、完整提示词、原始工具版本、全部参数、token 账单或湿实验结果。现在固定的工具包版本用于我们自己的可追踪运行，不冒充作者当时版本。

## 40 项任务映射

### 直接对应本次计算路线：10 个

文献部分有替代选择，不要求所有组件都运行；这不是作者原会话的调用清单。

| 官方目录 | 本项目位置 / 用途 | 与当前复现的关系 |
|---|---|---|
| [uniprot_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/uniprot_database/SKILL.md) | source-sequence | 筛候选、取序列和注释、核对标识；读取已有 ProtNLM 注释不等于运行 ProtNLM。 |
| [protein_sequence_similarity_search](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/protein_sequence_similarity_search/SKILL.md) | source-sequence | 序列搜索；本案明确选 BLAST + Swiss-Prot，避免默认 MMseqs2 / UniProtKB 改变比较条件。 |
| [alphafold_database_fetch_and_analyze](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/alphafold_database_fetch_and_analyze/SKILL.md) | structure | 获取 AlphaFold DB 已有预测并分析 pLDDT；不等于重新运行 AlphaFold。 |
| [foldseek_structural_search](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/foldseek_structural_search/SKILL.md) | structure | 以真实 PDB/mmCIF 文件检索结构近邻；本案实验结构搜索应明确数据库，而非沿用混合库默认。 |
| [pdb_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/pdb_database/SKILL.md) | structure | 取命中结构、实验方法和文献元数据，核实比较对象。 |
| [pymol](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/pymol/SKILL.md) | structure | 结构叠合、测量和图像；是可用复现工具，不能据此认定作者实际用了 PyMOL。 |
| [ncbi_sequence_fetch](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/ncbi_sequence_fetch/SKILL.md) | context-literature | 取蛋白/核酸/CDS 记录；完整邻域坐标表和间隔计算仍需补充处理。 |
| [pubmed_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/pubmed_database/SKILL.md) | context-literature | 查候选、家族与机制文献；摘要或家族结果不能直接视为候选实测。 |
| [literature_search_europepmc](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/literature_search_europepmc/SKILL.md) | context-literature | 文献检索和开放全文；可作为 PubMed 的补充/替代来源。 |
| [literature_search_openalex](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/literature_search_openalex/SKILL.md) | context-literature | DOI、作者和文献索引；可补查覆盖与开放全文，非每次必用。 |

### 辅助证据与基础设施：10 个

出现对应问题时才加载；它们不会因为装在同一个包里就成为复现前置条件。

| 官方目录 | 本项目位置 / 用途 | 与当前复现的关系 |
|---|---|---|
| [interpro_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/interpro_database/SKILL.md) | 辅助证据 | 交叉检查家族、结构域和位点注释；新增预测注释仍要看证据来源。 |
| [protein_sequence_msa](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/protein_sequence_msa/SKILL.md) | 辅助证据 | 已有多条序列时比较保守位置；不能代替数据库同源搜索。 |
| [quickgo_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/quickgo_database/SKILL.md) | 辅助证据 | 查询 GO/ECO，帮助解释功能注释与证据代码。 |
| [embl_ebi_ols](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/embl_ebi_ols/SKILL.md) | 辅助证据 | 需要准确术语定义、同义词或层级时查本体。 |
| [string_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/string_database/SKILL.md) | 辅助证据 | 可查相互作用/功能关联；图上的连接不能代替同一 contig 的 DNA 邻接坐标。 |
| [literature_search_arxiv](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/literature_search_arxiv/SKILL.md) | 文献补充 | 需要计算方法或 arXiv 预印本时使用。 |
| [literature_search_biorxiv](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/literature_search_biorxiv/SKILL.md) | 文献补充 | 需要生物学预印本时使用；记录是否同行评审及实际检索范围。 |
| [uv](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/uv/SKILL.md) | 运行环境 | 准备 Python 依赖；与本项目 stdlib CLI 的依赖不同，也不是生物模型。 |
| [credentials](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/credentials/SKILL.md) | 运行环境 | 仅在所选服务需要时处理凭证；不代表所有工具共享一个 API key。 |
| [workflow_skill_creator](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/workflow_skill_creator/SKILL.md) | 后续工程 | 从实际已完成的流程提炼可复用技能；当前尚未完整跑通的研究不能被标为已验证流程。 |

### 当前 AMP 复现范围不需要：20 个

这是相对于本次候选与计算路线的判断；换研究问题后可以重新评估。

| 官方目录 | 本项目位置 / 用途 | 与当前复现的关系 |
|---|---|---|
| [alphagenome_atlas_website_links](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/alphagenome_atlas_website_links/SKILL.md) | 当前不启用 | 基因组变异/区域的 Atlas 展示链接；本次没有此类分析目标。 |
| [alphagenome_single_variant_analysis](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/alphagenome_single_variant_analysis/SKILL.md) | 当前不启用 | 遗传变异对表达/调控的预测；不承担蛋白结构或抗菌活性判断。 |
| [alphagenome_variant_impact_score](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/alphagenome_variant_impact_score/SKILL.md) | 当前不启用 | 变异影响评分；本次输入问题不要求变异评分。 |
| [chembl_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/chembl_database/SKILL.md) | 当前不启用 | 化合物、靶点和活性数据库；后续若扩展药物/化合物问题再评估。 |
| [clinical_trials_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/clinical_trials_database/SKILL.md) | 当前不启用 | 临床试验；本次仍处于计算候选研究。 |
| [clinvar_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/clinvar_database/SKILL.md) | 当前不启用 | 人类变异的临床解释；与本次细菌短蛋白路线不对应。 |
| [dbsnp_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/dbsnp_database/SKILL.md) | 当前不启用 | SNP/indel 记录；本次不做变异定位。 |
| [encode_ccres_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/encode_ccres_database/SKILL.md) | 当前不启用 | 调控元件和相关实验数据；不是当前菌株邻域的证据来源。 |
| [ensembl_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/ensembl_database/SKILL.md) | 当前不启用 | 基因/转录本/变异与 ID 映射；本案采用已知 UniProt/NCBI 交叉引用，换支持对象时可再考虑。 |
| [gnomad_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/gnomad_database/SKILL.md) | 当前不启用 | 人群变异频率/约束；本次不涉及该问题。 |
| [gtex_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/gtex_database/SKILL.md) | 当前不启用 | 人体组织表达/eQTL；本案不是人体组织表达分析。 |
| [human_protein_atlas_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/human_protein_atlas_database/SKILL.md) | 当前不启用 | 人体蛋白表达/定位；不能作为当前细菌候选的表达证据。 |
| [jaspar_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/jaspar_database/SKILL.md) | 当前不启用 | 转录因子结合谱；本次没有指定调控位点分析任务。 |
| [openfda_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/openfda_database/SKILL.md) | 当前不启用 | 药品、器械等监管数据；不能补成本候选的活性验证。 |
| [opentargets_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/opentargets_database/SKILL.md) | 当前不启用 | 靶点—疾病关系；本次路线未提出这类人类治疗靶点问题。 |
| [predictingthepast](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/predictingthepast/SKILL.md) | 当前不启用 | 古拉丁/古希腊文本研究；与 AMP 计算复现没有直接关系。 |
| [pubchem_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/pubchem_database/SKILL.md) | 当前不启用 | 化学结构和物质性质；具体化学问题出现时再考虑。 |
| [reactome_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/reactome_database/SKILL.md) | 当前不启用 | 通路/富集；本次单候选证据链没有要求该分析。 |
| [ucsc_conservation_and_tfbs](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/ucsc_conservation_and_tfbs/SKILL.md) | 当前不启用 | 基因组保守性/转录因子结合位点；不是现阶段的基因邻域核验。 |
| [unibind_database](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/unibind_database/SKILL.md) | 当前不启用 | TF–DNA 结合数据；当前不查这类结合数据。 |

## 会直接影响还原的细节

- **序列搜索默认值。** 官方技能默认 MMseqs2；BLAST 脚本默认数据库为 UniProtKB。本案若还原文章的 Swiss-Prot 步骤，需明确 BLAST 与 `uniprotkb_swissprot`，记录本次实际参数。
- **邮箱文案与代码有差异。** [BLAST skill](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/protein_sequence_similarity_search/SKILL.md) 的前置说明说 USER_EMAIL 可选/推荐，但后文写 requires。[脚本](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/protein_sequence_similarity_search/scripts/uniprot_blast.py) 无邮箱时仅警告、仍提交；邮箱是表单参数，不能预先断言缺它必然阻塞。服务是否接受以实际响应为准。
- **结构数据库默认值。** [Foldseek 脚本](https://github.com/google-deepmind/science-skills/blob/4de6786171f1479026da5d3a00f110703c8ba35e/skills/foldseek_structural_search/scripts/search.py) 默认含 `pdb100,afdb50`。若当前比较要求实验结构库，应明确相应数据库并记版本；不能把混合库结果直接当作原实验条件。
- **模型结果的来源。** UniProt 查询可取既有功能注释；AlphaFold DB skill 取已有预测。当前包没有独立 ProtNLM 推理、SignalP 重跑或端到端 AMP 验证 skill。
- **邻域缺的工作。** NCBI skill 可取记录/翻译，当前 CDS 翻译帮助函数不输出完整邻域坐标表。原文的间隔主张需要从已确认菌株/contig 的注释中另提坐标，按链方向和坐标体系计算。
- **叠合与活性。** Foldseek/PyMOL 的结果描述结构关系；抗菌活性及机制仍需独立证据。图像工具也不能证明原演示采用了某个特定视觉模型。
- **摘要与原始数据。** 官方序列/Foldseek skill 建议 agent 阅读生成的 Markdown 摘要，完整 JSON 留给后续程序。我们的证据归档保持两者；缺少的指标交给明确的分析程序计算，不往摘要里补造数值。

## 如何接到本项目

本项目 skill 根据当前 case 的目标选择官方组件，读取该组件说明及必需依赖，调用已有脚本，保存输出，然后按本项目验收标准核查。
具体 API 参数由对应官方工具文档负责；本项目不复制一套容易过期的接口说明，也不把全部工具注册为启动必读。

官方 wrapper 的结果通常不含本项目的 case manifest。对接时把原始 JSON/Markdown 保存到本案的新运行目录，另记 accession、输入哈希、实际算法/数据库/参数、工具 commit、时间与任务标识，按 [TOOLS.md](TOOLS.md) 的 manifest 约定生成校验记录；整理表格放 results，结论与下一步回写 EVIDENCE/STATE。
`case.py check` 验的是文件完整性与部分身份；科学指标和结论仍按阶段 skill 验收。

当前项目的 `fetch_candidate.py` 是已验证的 UniProt/AFDB 快照抓取与审计入口，与部分官方抓取能力重叠。可按任务采用它或官方组件，记录实际使用者；不要把我们已有脚本的结果写成 Google wrapper 已执行。
本轮仅审阅、映射与更新文档，没有安装 Science 插件或执行新的远端科研任务。

工作流跑通后，可以考虑官方 workflow_skill_creator 提炼实际经验；当前先保持四个阶段 skill、case 参数和真实状态，避免把未执行的计划包装成已验证流程。

