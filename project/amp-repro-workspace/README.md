# AMP 论文案例复现工作区

这是可交给 agent 接着做的项目目录：四个按需加载的阶段 skill、独立案例参数和进度、原文、已有原始数据，以及可执行的案例管理入口。

## 开始

把整个目录解压，令 agent 在此工作，并给它这句话：

> 从 AGENTS.md 接手。先报告当前案例、已有证据和下一步，再继续 STATE.md 指定的计算复现任务。只加载当前阶段需要的文件，实际运行后保存产物并更新状态。

识别 `AGENTS.md` 的 agent 可以自动发现入口。其他运行时也可以直接读取这个 Markdown 文件；无需特定模型或全局插件注册。

人在项目根目录也可以先运行：

```bash
python3 scripts/case.py status
python3 scripts/case.py check
```

`status` 展示当前 case；`check` 离线核对该 case 的数据 manifest 与文件哈希。它们不调用大模型，也不运行 BLAST 或 Foldseek。

## 三个地方，三种职责

| 文件 | 回答的问题 |
|---|---|
| `AGENTS.md` → `INDEX.md` | 从哪里开始，这次该读哪个 skill？ |
| `cases/<case_id>/case.json` | 这次研究谁，使用哪些来源和筛选条件？ |
| `cases/<case_id>/STATE.md` | 哪些已完成，证据在哪，接下来做什么？ |

`skills/` 保存通用做法；`data/` 保存原始证据；`results/` 保存派生分析；`reports/` 保存解释。它们都属于同一项目，但后面三者按 case 隔离。每个 case 的 `EVIDENCE.md` 只汇总主张及对应证据，按需读。

## 换一个候选

下例编号只演示命令，不代表它是抗菌候选；换成你实际要研究的 UniProt accession。

```bash
python3 scripts/case.py new --id another-candidate --accession P12345
python3 scripts/case.py use another-candidate
python3 scripts/case.py status
```

新 case 的来源、物种、筛选条件留空，步骤从 pending 开始；先按真实任务补配置。旧 case 原样保留。若只是同一候选重新抓取数据库，保持 case 不变，执行：

```bash
python3 scripts/case.py fetch
```

这会联网下载 UniProt 与现有 AlphaFold DB 模型，建立新时间戳目录；不会自动给研究步骤盖“完成”章。无 AlphaFold 模型、片段或多个模型时保留已下载数据并报告需审查。

回到随包案例：

```bash
python3 scripts/case.py use paper-a0a0u0d591
```

## 运行与复现边界

Python 3.9+ 足以运行随包脚本，核心入口没有第三方 Python 依赖。搜索、联网下载和后续工具所需环境见 `docs/TOOLS.md`。

随包案例已有原文、数据库记录、初筛与结构置信度审计；科学复现仍在进行中，以该 case 的 STATE 为准。这套目录管理证据和交接，不会把外部搜索工具假装成已执行，也不自动完成湿实验。

作者的原始精确搜索参数、完整对话和 usage 账单没有随公开材料披露；采用新参数时记为我们的选择。单个编号可替换，科学结论必须重算。

## 设计与版本

参考 grapeot/context-infrastructure 的入口路由和 project_scaffold 思路，具体来源、取舍、验收见 `docs/PROJECT.md` 与 `docs/VALIDATION.md`。
Google Science Skills README、40 项工具和本项目的对应关系见 [SCIENCE_SKILLS_MAP.md](docs/SCIENCE_SKILLS_MAP.md)，仅需了解工具全貌时读取。
项目有独立 Git 历史。若分发包内未含 `.git/`，可用随包 `history.bundle` 恢复历史：`git clone history.bundle restored-project`。日常直接使用本目录即可。

