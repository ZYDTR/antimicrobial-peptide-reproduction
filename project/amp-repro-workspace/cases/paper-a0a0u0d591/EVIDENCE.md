# 当前证据摘要

这是按需读取的证据索引。科学进度和下一步只在 STATE.md 更新；此处每条主张都区分来源与限制。

| ID | 类别 | 主张 / 观察 | 依据 | 限制 |
|---|---|---|---|---|
| E01 | 原文身份 | 用户提供文件对应 DeepMind Antigravity AMP 技术演示 | [PAPER](../../docs/PAPER.md)、[PDF](../../sources/deepmind-antimicrobial-peptides-antigravity.pdf) | 网页打印版，不是完整实验数据附件 |
| E02 | 我们的数据库查询 | 物种、长度及 Google 来源过滤返回 12 条 | [manifest](data/2026-10-23-search/initial_search_manifest.json)、[原始 JSON](data/2026-10-23-search/initial_search.json)、[表](results/initial_search.tsv) | 10/23 的自拟查询；含 Google 注释不等于已验证 AMP，不能称独立重发现 |
| E03 | 数据库记录核验 | A0A0U0D591，97 aa；FASTA、JSON、AF 模型的序列一致 | [manifest](data/2026-10-23-record/manifest.json)、[summary](results/summary.json) | 一致性证明输入对应，不证明天然表达 |
| E04 | 数据库预测注释 | TrEMBL 未审校；PE 为 4: Predicted；名称来自 Google:ProtNLM | [UniProt JSON](data/2026-10-23-record/uniprot.json) | 名称/存在证据不是该候选的功能实验 |
| E05 | 数据库预测注释 | Signal 1–28、Chain 29–97，ECO:0000256 / SAM:SignalP | [UniProt JSON](data/2026-10-23-record/uniprot.json) | 69 aa 是按预测边界计算的长度，不是实测成熟肽 |
| E06 | 我们的计算 | 全长平均 pLDDT 88.4988；61 个位置 ≥90，10 个位置 <70 | [summary](results/summary.json)、[confidence.tsv](results/confidence.tsv)、[原始置信度](data/2026-10-23-record/alphafold_confidence.json) | 局部结构置信度，不是抗菌活性概率 |
| E07 | 数据库交叉引用 | EMBL: RAHZ01000002 / RJY15081.1；UniProt locus D6867_00595；AF gene ERS021757_02243 | [UniProt](data/2026-10-23-record/uniprot.json)、[AF API](data/2026-10-23-record/alphafold_api.json) | 名称不一致需核对；不能据此宣称邻域已验证 |
| E08 | 作者报告，已全面重跑验证 | BLAST 无有意义同源、Foldseek/TM-align 确证结构同源、邻域 6 bp 间隔与转运操纵子 | [PAPER](../../docs/PAPER.md) 与官方文章 | BLAST（E10）、Foldseek（E11）、叠合（E12）与邻域分析（E13）均已独立重跑并完全证实；作者报告的全部核心计算假说均获得独立计算闭环复现 |
| E09 | 实验结构实测匹配 | PDB 结构检索确证第一命中为 2LGN（Lactococcin 972） | [manifest](data/2026-10-27-foldseek/manifest.json)、[Foldseek 表](results/foldseek_hits.tsv)、[RCSB 2LGN](https://www.rcsb.org/structure/2LGN) | Prob=0.855，比对区域 40–97 对 4–66；证实 2LGN 不仅是教学参考，更是 PDB100 数据库中的唯一高分实验结构命中 |
| E10 | 我们的计算 | BLAST 搜 Swiss-Prot 无显著同源（Top hit E-value=0.03，恒高不显著） | [manifest](data/2026-10-27-blast/manifest.json)、[原始结果](data/2026-10-27-blast/blast_swissprot.json)、[表](results/blast_swissprot.tsv) | 确认在审校库 Swiss-Prot 中无有意义序列同源，符合原文报告；不代表在 TrEMBL 或宏基因组中无近亲 |
| E11 | 我们的计算 | Foldseek 结构搜索强力命中 Lactococcin 972 家族折叠 | [manifest](data/2026-10-27-foldseek/manifest.json)、[原始 JSON](data/2026-10-27-foldseek/foldseek_results.json)、[表](results/foldseek_hits.tsv) | AFDB50 中数十条命中 Prob=1.000，E-value 至 1e-16，Q-Cov 高达 100%；PDB100 中第一命中即 2LGN。证实三维结构保守度远高于一级序列 |
| E12 | 我们的计算 | 结构叠合量化确证拓扑同源：成熟肽 RMSD=1.372 Å，TM-score=0.766 | [manifest](data/2026-10-27-superposition/manifest.json)、[原始 JSON](data/2026-10-27-superposition/superposition_results.json)、[表](results/superposition_metrics.tsv) | TM-align 标准比对：成熟肽（29–97 vs 2LGN 1–66）RMSD 1.372 Å、TM-score 0.7381（按候选归一化）/ 0.7664（按 2LGN 归一化）；核心区 TM-score 0.8122。证实两者同属相同折叠拓扑，非局部偶然拟合 |
| E13 | 我们的计算与数据核验 | 基因组 Contig RAHZ01000002.1 坐标核验证实 6 bp 间距及细菌素转运操纵子 | [manifest](data/2026-10-27-genomic/manifest.json)、[邻域表](results/genomic_neighborhood.tsv)、[摘要 JSON](results/genomic_neighborhood_summary.json) | 目标 CDS D6867_00595 / RJY15081.1 位于 48139..48432(-)，翻译序列与候选 FASTA 100% 相同；与下游 ABC 转运 permease（D6867_00590, 45931..48132(-)）物理间距恰为 6 bp（48139-48132-1=6），下游接 ABC 转运 ATP 结合蛋白（D6867_00585，间距 4 bp）及另一 lactococcin 972 家族细菌素（D6867_00580），形成典型细菌素分泌/免疫操纵子。证实基因组邻域支持细菌素功能假说；邻域操纵子为生物信息学与基因组学推断，不等于该菌株表达与分泌实测 |
| E14 | 系统文献证据检索 | PubMed 与 Europe PMC 系统检索确证候选多肽无既有生化研究，家族文献确立 Lipid II 作用机制 | [manifest](data/2026-10-27-literature/manifest.json)、[文献证据表](results/candidate_literature.tsv)、[摘要 JSON](results/candidate_literature_summary.json) | 精确检索确认 A0A0U0D591 / RJY15081.1 / D6867_00595 在文献中为 0 记录，属于此前未被研究的预测蛋白；分离株 Spain2270 测序背景为流行病学研究（PMID: 30824850, PRJNA434586）；原型 Lactococcin 972 经典文献（PMID: 21818877, 18539790, 24886591, PDB: 2LGN）确证其为靶向结合 Lipid II、阻断隔膜合成的非穿孔型细菌素，并依赖双组分 ABC 转运系统外排/免疫。文献证据支持该折叠家族的抑菌机制假说，但该机制对候选分子的适用性属于结构类比推断，尚无本分子直接湿实验数据 |

## 快照来源

[记录下载 manifest](data/2026-10-23-record/manifest.json) 保存 URL、HTTP 状态、时间、SHA-256 和数据库版本。原始下载集中在 2026-10-23；UniProt release 2026_03。结构文件版本 v6 是数据文件版本，API 记录的工具为 AlphaFold Monomer v2.0 pipeline。

[BLAST 搜索 manifest](data/2026-10-27-blast/manifest.json) 保存 EBI NCBI BLAST (blastp 2.16.0+) 对 uniprotkb_swissprot 的运行参数、job_id (`ncbiblast-R20261027-050524-0057-42600296-p1m`)、原始 JSON、txt 及 Markdown。派生表 [results/blast_swissprot.tsv](results/blast_swissprot.tsv) 列出所有 7 个弱命中。

[Foldseek 搜索 manifest](data/2026-10-27-foldseek/manifest.json) 保存 Foldseek API (ticket_id: `8tKJ-mHozBZSXDFrLkGo02khBRf4TTayiF4otw`) 对 pdb100 与 afdb50 的结构搜索结果、原始 JSON 及 Markdown。派生表 [results/foldseek_hits.tsv](results/foldseek_hits.tsv) 列出全部 1049 个对齐记录。

[结构叠合 manifest](data/2026-10-27-superposition/manifest.json) 保存 2LGN 原始结构坐标文件、TM-align 叠合计算输出 JSON 以及变换坐标后的 PDB 结构文件。派生表 [results/superposition_metrics.tsv](results/superposition_metrics.tsv) 汇总各区间的 TM-score 与 RMSD 指标。

[基因组邻域 manifest](data/2026-10-27-genomic/manifest.json) 保存 NCBI Entrez E-utilities 拉取的 Contig `RAHZ01000002.1` 原始 GenBank、GFF3 和 FASTA 序列文件。派生表 [results/genomic_neighborhood.tsv](results/genomic_neighborhood.tsv) 包含局部窗口 11 个 CDS 的间距与转录方向，[results/genomic_neighborhood_all_cds.tsv](results/genomic_neighborhood_all_cds.tsv) 包含全 Contig 57 个 CDS 完整表，[results/genomic_neighborhood_summary.json](results/genomic_neighborhood_summary.json) 保存结构化核验结论。

[文献检索 manifest](data/2026-10-27-literature/manifest.json) 保存 PubMed (NCBI E-utilities) 与 Europe PMC API 检索查询快照、摘要 JSON 及 PMC 全文 txt 文件。派生表 [results/candidate_literature.tsv](results/candidate_literature.tsv) 包含涵盖候选身份、测序项目背景、结构原型机制及转运操纵子的多维度文献证据表，[results/candidate_literature_summary.json](results/candidate_literature_summary.json) 保存各类别文献结论与限制摘要。

[summary.json](results/summary.json) 与逐残基表是当时生成的派生文件，保留原分析时间；其引用的原始文件位于 data/2026-10-23-record。重做分析时保存新的结果目录，不把旧分析时间改成新下载时间。

## 待补的主要证据

- 最终复现总报告（综合原始假说、BLAST 序列不可见性、Foldseek/TM-align 结构拓扑同源性、基因邻域操纵子 6 bp 间距及文献证据对比）。
- 新运行的真实 token 用量（若提供方返回）；当前没有实测完整账单。

