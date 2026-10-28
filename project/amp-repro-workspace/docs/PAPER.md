# 本次来源与复现范围

## 锁定的原文

- 标题：**Accelerating the search for antimicrobial peptides with Google Antigravity**
- 发布：2026-10-15；作者：Pengfei Tian、Maxwell L. Bileschi、Zoi Tsangalidou、Sukhdeep Singh、Lucy J. Colwell。
- 官方文章：https://deepmind.google/blog/accelerating-antimicrobial-discovery/
- 用户提供的原文件：[deepmind-antimicrobial-peptides-antigravity.pdf](../sources/deepmind-antimicrobial-peptides-antigravity.pdf)，8 页。
- PDF SHA-256：`aed8251b77cb033245a6feee4aa7b36540adeca2800c7cda1a8482fe72921718`。
- 便于检索的文本：[article.txt](../sources/article.txt)。纯文本可能丢图、轮播和版面；争议内容回到 PDF 或官方网页核对。

这是官方技术演示文章的 PDF 打印版。它展示候选发现和计算分析，文章称实验验证仍在进行；公开内容没有给出该候选的湿实验活性结果。PDF 第 4 页只完整保留轮播首卡，网页补充内容应注明来自网页而非假称都在 PDF 中。

## 原文主张与我们的目标

| 环节 | 原文路线 | 本工程验收 |
|---|---|---|
| 候选 | 物种、短序列、ProtNLM 功能注释筛选 | 保存实际查询及版本；区分已知编号复核与独立重发现 |
| 序列 | BLAST 搜 Swiss-Prot，报告无有意义的同源匹配 | 保存我们的参数、完整结果与阈值；结果可以不同 |
| 结构 | AlphaFold DB、Foldseek、结构比较 | 核对序列和模型，记录置信度、匹配区间与数值 |
| 基因环境 | 根据邻近运输与调控相关基因解释 | 用同一菌株/contig 的 DNA 坐标核验，不凭蛋白折叠位置 |
| 文献与机制 | 将候选和已研究家族联系起来 | 分清候选直接证据、家族证据和功能假说 |
| 后续验证 | 提出实验问题，验证仍在进行 | 列出证据缺口与验证目的；本工程不提供实测活性结论 |

候选编号、物种和原文报告值属于随包 case，不是通用规则。我们可以复现分析路线并解释差异；原文没公开的参数和任务日志不能猜成原始设置。

## 公开信息边界

界面展示 Gemini 3.8 Flash；这不等于公开了内部精确模型快照、全部提示词、推理设置或运行日志。Science 工具包是可用的公开工具来源，但当前工具仓库版本不能自动视为演示当天版本。工具关系见 [TOOLS.md](TOOLS.md)。

没有可核对的该次完整输入/输出 token 或费用账单。新运行可自行记 usage；估算与实测应分别标记。

