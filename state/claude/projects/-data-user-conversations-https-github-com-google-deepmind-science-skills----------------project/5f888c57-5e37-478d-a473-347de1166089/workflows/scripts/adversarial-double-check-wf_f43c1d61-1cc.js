export const meta = {
  name: 'adversarial-double-check',
  description: 'Adversarially double-check AMP reproduction steps across 4 critical dimensions with highly skeptical auditor agents',
  phases: [
    { title: 'Adversarial Audit', detail: 'Four skeptical agents independently scrutinize BLAST, Structure, Genomic Neighborhood, and Literature Claims' },
    { title: 'Synthesis', detail: 'Consolidate skeptical verdicts and identify vulnerabilities in the reproduction evidence' }
  ]
}

const AUDIT_DIMENSIONS = [
  {
    role: 'Skeptical Sequence Homology Auditor',
    step: 'blast_swissprot',
    prompt: `你是一位极其苛刻的生物信息学评审人（Reviewer 2），带着强烈的怀疑和批判态度，对 paper-a0a0u0d591 案例中的 Swiss-Prot BLAST 分析进行 Adversarial Double Check。

请阅读以下文件：
1. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/data/2026-10-27-blast/blast_submission.xml
2. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/data/2026-10-27-blast/blast_swissprot.json
3. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/blast_swissprot.tsv

请重点从以下角度质疑并寻找缺陷：
1. 数据库选择偏差：搜 Swiss-Prot（仅约 57 万条高质量审校序列）声称“无有意义同源”，是不是一种刻意设计的“假阴性”？如果去搜 TrEMBL、NCBI nr 或 RefSeq，真的会没有同源物吗？
2. 参数敏感度：对于 97 aa 的短肽（成熟区仅 69 aa），使用标准的 BLOSUM62 矩阵与默认 Gap 惩罚是否会导致同源检测灵敏度不足？是否应该测试 PAM30 或专门针对短多肽的打分矩阵？
3. 结论外推风险：报告声称“确认无有意义序列同源”，是否存在将“在审校数据库未检出”过度解读为“在整个自然界中完全孤立无同源”的过度声明？

请给出严格、客观、不留情面的审查意见。`
  },
  {
    role: 'Skeptical Structural Alignment Auditor',
    step: 'foldseek_and_superposition',
    prompt: `你是一位对蛋白质三维结构比较极其挑剔的结构生物学家，带着强烈的怀疑态度，对 paper-a0a0u0d591 的 Foldseek 结构搜索与 TM-align 结构叠合进行 Adversarial Double Check。

请阅读以下文件：
1. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/foldseek_hits.tsv
2. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/superposition_metrics.tsv
3. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/data/2026-10-27-superposition/superposition_results.json

请重点从以下角度质疑并寻找漏洞：
1. PDB 第一命中 2LGN 的 E-value 是 1.011（Score=64, Prob=0.855），在标准结构比对中，E-value > 1.0 是否暗示这可能是一个边缘显著性甚至假阳性的命中？
2. TM-score 截断选择性偏差（Cherry-picking）：报告展示了成熟肽（29–97）的 TM-score 为 0.7664，核心区（40–97）为 0.8122。如果直接用 AlphaFold 预测的全长结构（1–97，包含柔性信号肽）与 2LGN 进行全长对齐，TM-score 会下降多少？是否存在刻意裁剪以美化指标？
3. 构象代表性：2LGN 包含 20 个 NMR 构象模型，为什么只选 Model 1？如果在全部 20 个模型中测试，RMSD 和 TM-score 会不会显著波动？
4. 结构相似与功能保守的鸿沟：在两蛋白结构对齐区序列同一性仅约 26% 的情况下，单凭四链反平行 Beta 折叠的相似性，能否断定其具有相同的生物活性？

请指出所有技术局限和过度主张。`
  },
  {
    role: 'Skeptical Genomic Neighborhood Auditor',
    step: 'genomic_neighborhood',
    prompt: `你是一位对基因组注释与操纵子结构极其苛刻的微生物基因组学家，带着怀疑态度，对 paper-a0a0u0d591 的基因邻域分析和 6 bp 间距进行 Adversarial Double Check。

请阅读以下文件：
1. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/genomic_neighborhood.tsv
2. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/genomic_neighborhood_summary.json
3. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/data/2026-10-27-genomic/manifest.json

请重点从以下角度质疑并核查：
1. 间距计算的数学严格性：候选 CDS 48139..48432(-) 与下游 D6867_00590 (45931..48132(-)) 的间距计算：48139 - 48132 - 1 = 6 bp 是否在 1-based inclusive 坐标系下无懈可击？是否存在 off-by-one 错误？
2. 操纵子共转录假说的可信度：虽然两基因同在负链上，且仅隔 6 bp，但在这 6 bp 间隙里是否存在潜在的启动子（promoter）或终止子（terminator）？仅凭 6 bp 物理距离就能百分之百断定它们必定属于同一个多顺反子 mRNA 吗？
3. 假基因与邻域完整性：检查 Contig RAHZ01000002.1 的完整 CDS 列表，周围是否存在转座酶、整合酶或假基因（如前部出现的 internal stop 假基因）？这个细菌素基因簇在 Spain2270 中到底是一个具有完整活性的活操纵子，还是一个在进化中退化的基因残迹（vestigial cluster）？

请提供严格的技术核查与质疑。`
  },
  {
    role: 'Skeptical Literature & Claims Auditor',
    step: 'literature_and_final_claims',
    prompt: `你是一位专注于科研诚信与证据严谨性的资深科学编辑，带着强烈的批判怀疑视角，对 paper-a0a0u0d591 的文献分析与最终报告（final_reproduction_report.md）进行 Adversarial Double Check。

请阅读以下文件：
1. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/candidate_literature.tsv
2. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/candidate_literature_summary.json
3. /data/user/conversations/https-github.com-google-deepmind-science-skills-把这个下载下来-认真了解一下/project/amp-repro-workspace/cases/paper-a0a0u0d591/results/final_reproduction_report.md

请重点从以下角度质疑并寻找破绽：
1. “零文献”的解读两面性：PubMed 与 Europe PMC 检索 0 篇文献，报告解释为“纯计算新候选”。但这是否同样说明该候选迄今为止完全没有任何哪怕最微弱的湿实验立足点？
2. 作用机制的“李代桃僵”：报告将 Lactococcin 972 结合 Lipid II 的机制（PMID: 18539790）详细列入，这会不会给读者造成一种潜意识的心理误导——认为 A0A0U0D591 也已经被证实结合 Lipid II？在高达 74% 的序列差异下，直接套用原型机制是否存在严重的推理跳跃？
3. 宣传与科学的界限：最终报告中是否存在任何哪怕一丝将“预测注释（PE 4）”、“模型置信度（pLDDT）”、“结构拓扑相似（TM-score）”等同于“杀菌效力”的语病或模糊措辞？

请指出所有行文与逻辑推理中的漏洞。`
  }
]

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    auditor_role: { type: 'string' },
    target_step: { type: 'string' },
    verdict: {
      type: 'string',
      enum: ['PASS_WITH_CAVEATS', 'OVERCLAIM_DETECTED', 'CRITICAL_FLAW']
    },
    skeptical_findings: {
      type: 'array',
      items: { type: 'string' },
      description: 'List of specific vulnerabilities, limitations, or potential flaws identified'
    },
    counter_arguments: {
      type: 'array',
      items: { type: 'string' },
      description: 'Arguments against overconfident conclusions in the reproduction report'
    },
    rigor_rating_out_of_10: {
      type: 'number',
      description: 'Scientific rigor rating (1-10) of the reproduction step'
    },
    recommended_disclaimers: {
      type: 'array',
      items: { type: 'string' },
      description: 'Mandatory disclaimers or caveats that must be explicitly highlighted'
    }
  },
  required: [
    'auditor_role',
    'target_step',
    'verdict',
    'skeptical_findings',
    'counter_arguments',
    'rigor_rating_out_of_10',
    'recommended_disclaimers'
  ]
}

phase('Adversarial Audit')
log('Launching 4 independent skeptical auditor agents to challenge reproduction evidence...')

const auditResults = await parallel(
  AUDIT_DIMENSIONS.map(dim => () =>
    agent(dim.prompt, {
      label: `audit:${dim.step}`,
      phase: 'Adversarial Audit',
      schema: VERDICT_SCHEMA
    })
  )
)

phase('Synthesis')
log('Synthesizing skeptical findings and double-check verdicts...')

const validResults = auditResults.filter(Boolean)

const synthesisPrompt = `你是一位首席科学审计长（Chief Scientific Auditor）。
你收到了 4 位挑剔的质疑评审员对 paper-a0a0u0d591 抗菌肽复现案的 Adversarial Double Check 报告。
评审员的结构化输出如下：
${JSON.stringify(validResults, null, 2)}

请对这 4 份审查意见进行综合研判，撰写一份客观、无情、深刻的《Adversarial Double-Check 审计裁决与风险备忘录》，回答以下问题：
1. 本复现项目的计算证据在多大程度上是经得起严格挑剔的（哪些计算事实是绝对坚固的）？
2. 评审员指出的最锋利、最致命的技术软肋和推理边界是什么？
3. 针对所有发现的漏洞与局限，必须在报告和最终交付中追加哪些强制免责与科学边界声明？

请输出纯文本格式的详实审计裁决报告。`

const finalSynthesis = await agent(synthesisPrompt, {
  label: 'chief-auditor:synthesis',
  phase: 'Synthesis'
})

return {
  audits: validResults,
  synthesis: finalSynthesis
}
