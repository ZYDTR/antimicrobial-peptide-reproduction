# 当前科学进度

更新：2026-10-27。当前候选以 case.json 为准。**计算复现全流程已完成。**

## 下一步

- next_action：计算生物学全流程复现已终态闭环。无后续待执行计算步骤。如未来引入湿实验验证合作，可参考最终综合报告（results/final_reproduction_report.md）开展成熟肽（29–97，69 aa）化学合成及体外 MIC 抑菌试验。
- next_skill：无（计算复现已完成）。
- input：[final_reproduction_report.md](results/final_reproduction_report.md)。
- first_command：运行 `python3 scripts/case.py check` 验证全案数据哈希与基线一致性。
- expected_output：保持 44 个原始文件与 7 个 manifests 的完整审计状态。
- blockers：无。

## 步骤状态

表中 done 只表示该行工作完成。pending 不能根据作者的结果自动改成 done。

| step_id | 状态 | 最后核对 | 证据 / 观察与限制 |
|---|---|---|---|
| source_identity | done | 2026-10-26 | [原文说明](../../docs/PAPER.md)、[原 PDF](../../sources/deepmind-antimicrobial-peptides-antigravity.pdf)；8 页打印版，轮播/视频并非完整实验附件 |
| initial_search | done | 2026-10-26 | [搜索 manifest](data/2026-10-23-search/initial_search_manifest.json)；10/23 自拟查询返回 12 条，无下一页；不是 12 条已验证 AMP |
| candidate_record | done | 2026-10-26 | [下载 manifest](data/2026-10-23-record/manifest.json)；10/23 数据快照，序列身份与原始哈希已核对 |
| processing_annotation | done | 2026-10-26 | [UniProt](data/2026-10-23-record/uniprot.json)；Signal/Chain 只是读取既有预测注释，未重跑 SignalP |
| alphafold_confidence | done | 2026-10-26 | [summary](results/summary.json)、[逐残基表](results/confidence.tsv)；下载既有预测并复算置信度，未自行运行 AlphaFold |
| blast_swissprot | done | 2026-10-27 | [manifest](data/2026-10-27-blast/manifest.json)、[原始 JSON](data/2026-10-27-blast/blast_swissprot.json)、[表](results/blast_swissprot.tsv)；EBI blastp 2.16.0+（job_id: `ncbiblast-R20261027-050524-0057-42600296-p1m`）；Top hit E-value=0.03，仅 7 条弱匹配且无已知 AMP，确认 Swiss-Prot 中无有意义序列同源，完全符合原文报告 |
| foldseek_search | done | 2026-10-27 | [manifest](data/2026-10-27-foldseek/manifest.json)、[原始 JSON](data/2026-10-27-foldseek/foldseek_results.json)、[表](results/foldseek_hits.tsv)；Foldseek API (ticket_id: `8tKJ-mHozBZSXDFrLkGo02khBRf4TTayiF4otw`)；AFDB50 大量命中 Lactococcin 972 家族（Prob=1.000, E-value 至 1e-16）；PDB100 第一命中确为 2LGN (Lactococcin 972, Prob=0.855, 区间 40–97 对 4–66)；结构层面的家族同源被完整证实 |
| structure_superposition | done | 2026-10-27 | [manifest](data/2026-10-27-superposition/manifest.json)、[原始 JSON](data/2026-10-27-superposition/superposition_results.json)、[表](results/superposition_metrics.tsv)；TM-align 叠合 2LGN (NMR Model 1)；成熟肽（29–97 vs 1–66）RMSD=1.372 Å，TM-score=0.7664，核心区 TM-score=0.8122；证实两者共享同一三维拓扑架构 |
| genomic_neighborhood | done | 2026-10-27 | [manifest](data/2026-10-27-genomic/manifest.json)、[邻域表](results/genomic_neighborhood.tsv)、[摘要 JSON](results/genomic_neighborhood_summary.json)；NCBI 拉取 RAHZ01000002.1；目标 CDS 位于 48139..48432(-)，翻译序列与候选 FASTA 100% 相同；与下游 ABC transporter permease 物理间距恰为 6 bp（48139-48132-1=6），下游接 ABC 转运 ATP 结合蛋白及另一细菌素，完整证实原文报告的 6 bp 间距与转运操纵子假说 |
| candidate_literature | done | 2026-10-27 | [manifest](data/2026-10-27-literature/manifest.json)、[文献证据表](results/candidate_literature.tsv)、[摘要 JSON](results/candidate_literature_summary.json)；PubMed 与 Europe PMC 检索证实该候选在既有文献中 0 记录，为未被实验测试的纯计算候选；菌株 Spain2270 测序背景为流行病学研究（PMID: 30824850, PRJNA434586）；原型 Lcn972 文献（PMID: 21818877, 18539790, 24886591, PDB: 2LGN）确立其结合 Lipid II 阻断隔膜合成的抗菌机制与 ABC 转运分泌系统，为候选多肽提供家族机制假说支持 |
| final_report | done | 2026-10-27 | [最终综合复现报告](results/final_reproduction_report.md)、[EVIDENCE.md](EVIDENCE.md)；对原文全部核心主张（BLAST 序列不可见、Foldseek 结构高度同源、TM-score 0.7664、邻域 6 bp 间隔与转运操纵子、Lipid II 机制假说）完成独立重跑验证与全证据闭环 |

## 证据边界与交接

- 原始获取日期是 2026-10-23，10/26 是来源复核与整理日期，10/27 是 BLAST、Foldseek、Superposition 与基因组邻域独立重跑/下载日期；各阶段证据链独立保留。
- 基础记录与结构摘要：97 aa、PE 4、平均 pLDDT 88.4988；这是数据库/计算证据，不是表达或活性实测。细节按需读 [EVIDENCE.md](EVIDENCE.md)。
- BLAST 搜 Swiss-Prot 确认无显著同源，Foldseek 搜 PDB/AFDB 强力命中 Lactococcin 972 家族（PDB 第一命中 2LGN），TM-align 叠合量化确证成熟肽 RMSD=1.372 Å、TM-score=0.7664，Contig RAHZ01000002.1 坐标核验确证 6 bp 间隔与下游 ABC 转运操纵子群。至此，原文技术报告中关于“序列同源不可见、结构同源高度可见、邻域 6 bp 间隔支持功能假说”的所有计算生物学核心主张均已获得独立计算重跑与数据落盘验证。
- 基因邻域仅提供细菌素生物合成/分泌操纵子假说支持，不代表该菌株湿实验天然表达与抗菌活性的实测。
- 不把旧聊天里未落盘的实时查询当作可校验原始数据；要用于结论时重新抓取并留痕。
- 湿实验活性未被本项目验证；不作为这个计算工作区的已完成步骤。重跑 SignalP 可作补充任务，不冒充已执行。
- 当前无遗留后台轮询作业，远端任务均已结束且文件已落盘校验。

