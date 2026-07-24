# Legal AI Skills / 法律 AI 技能集

一组可开源复用的 AI agent skills，面向法律检索、北大法宝 MCP、法学引注核验、Word/DOCX 文书处理和法律写作事实核查。

This repository contains reusable AI-agent skills for legal research, PKULaw MCP setup, citation checking, DOCX workflows, and legal-writing fact checking.

> 适用对象：支持 `SKILL.md` 技能目录的 agent 运行时，例如 Codex、Claude Code、WorkBuddy 或其他兼容的本地 agent。
>
> Intended for agent runtimes that can load `SKILL.md`-based skill folders, such as Codex, Claude Code, WorkBuddy, or compatible local agents.

## 这个仓库解决什么问题 / What This Solves

- **法律检索不回源**：把北大法宝 MCP、网页兜底检索、法条/案例核验拆成可复用流程。
- **引注容易编造或缺要素**：要求缺失信息用占位符提示，不猜测、不硬补。
- **Word 文书处理脆弱**：提供脚注、目录、TOA、证据目录、DOCX 结构处理辅助。

- **Ungrounded legal research**: reusable PKULaw MCP and browser fallback workflows.
- **Fabricated or incomplete citations**: missing facts must be flagged with placeholders instead of guessed.
- **Fragile Word/DOCX editing**: helpers for footnotes, TOA, evidence catalogs, and DOCX internals.

## 法学生最快上手 / Quick Start for Law Students

如果你只是想尽快用起来，不需要先理解 MCP、脚本或 Git。最省事是直接安装：

```bash
git clone https://github.com/NEU-ZHA/legal-ai-skills.git && cd legal-ai-skills && python3 scripts/install_skills.py
```

这会把本仓库 `skills/` 下的所有 skill 安装到默认目录，并自动安装许可证宽松的第三方推荐项。默认目录通常是 `~/.codex/skills`。

如果你确认已经阅读并接受第三方上游项目的许可证限制，想把推荐清单里的项目也一键装上：

```bash
python3 scripts/install_skills.py --full --accept-restricted-licenses
```

如果你的 AI 使用别的目录，可以这样改：

```bash
python3 scripts/install_skills.py --skills-dir ~/.workbuddy/skills
```

如果不想安装第三方推荐项：

```bash
python3 scripts/install_skills.py --skip-third-party
```

如果你不想用命令行，也可以手动安装。按下面做：

1. 在 GitHub 点 `Code` → `Download ZIP`，下载后解压。
2. 打开解压后的 `skills/` 文件夹。
3. 先复制这几个最常用的 skill 到你的 AI 工具的 skills 目录：

```text
legal-fact-checker
legal-citation-comprehensive
legal-citation-automator
legal-homework-formatter
evidence-catalog-generator
```

如果你不知道 skills 目录在哪里，直接问你的 AI：

```text
我想安装本地 skill。请告诉我当前运行时的 skills 目录在哪里，以及应该把这些文件夹复制到哪里。
```

4. 重启你的 AI 工具，或重新打开一个对话。
5. 直接告诉 AI 要用哪个 skill，并把材料发给它。

最常用的提问方式：

```text
请使用 legal-fact-checker 检查这段法律分析有没有编造法规、案例、案号或页码。缺少出处的地方请标 [待补: ...]。
```

```text
请使用 legal-citation-comprehensive 帮我检查这些脚注格式。不要猜缺失信息，告诉我缺什么、应该去哪里找。
```

```text
请使用 legal-homework-formatter 把这份法学作业整理成 Word 格式。姓名、学号、课程信息如果缺失，请先问我或使用 [待补: ...]。
```

```text
请使用 evidence-catalog-generator。下面是我的证据材料/文件名/材料说明，请先整理成证据目录条目，再填入我提供的证据目录模板。
```

```text
请使用 legal-citation-automator，把已经核验过的引注写入这个 DOCX 的脚注。
```

如果你用的 AI 比较新、比较会调用工具，一般不需要每次都这么严谨地点名 skill。你可以直接说：

```text
帮我检查这份作业的脚注和法律依据，缺什么请标出来，不要编造。
```

```text
我有一批证据材料和一个证据目录模板，帮我整理并填进去。
```

AI 通常会自己判断该用哪个 skill。上面这些“请使用 xxx”的写法，主要适合这些情况：

- 你的 AI 版本比较旧，不能稳定自动选择 skill。
- 你用的是轻量、快速或 Flash 类模型，容易漏掉工具调用。
- 你的任务很重要，希望它明确进入某个固定工作流。
- 它刚才答偏了，你想把它拉回正确的 skill。

使用原则很简单：

- 有原文、截图、PDF、Word、网页链接时，一起给 AI，不要只给结论。
- 法律依据必须可回到真实来源；不确定就让 AI 标 `[待补: ...]`。
- 学校账号、数据库 token、cookie、身份证号、手机号等只放在本机配置、环境变量或私有文件里，不要写进 skill、README、示例、模板，也不要提交到 GitHub。
- 交作业前自己再核对一遍法规名称、条号、案例名称、案号、页码和脚注。

PKULaw/北大法宝相关 skills 适合已经有学校或机构访问权限、并愿意自行开通/购买对应 MCP 服务的同学。配置时先把已购买服务名称、页面文字或截图给 AI，让它按实际订阅安装；刚开始不知道买什么时，可以先从法规关键词检索、精准法条查找、案例关键词检索三项开始。MCP 检索通常比浏览器兜底快很多。没有 token 或登录权限也可以先不用，优先用上面几个写作、引注和 Word 处理 skill。

如果你还想安装其他作者的优秀法律 skill，本仓库提供一个第三方推荐索引和安装脚本。`scripts/install_skills.py` 已经默认安装 Apache-2.0 的推荐项；如果确认许可证后使用 `--full --accept-restricted-licenses`，会从原作者仓库克隆并安装推荐清单里的其他项目，但仍不把第三方源码合并进本仓库：

```text
THIRD_PARTY_RECOMMENDED_SKILLS.md
third_party_skills.json
scripts/install_third_party_skills.py
```

最省事的问法：

```text
请克隆并安装 https://github.com/NEU-ZHA/legal-ai-skills。进入仓库后运行 python3 scripts/install_skills.py；如果我说要安装全量第三方推荐清单，请先解释上游许可证限制，确认后运行 python3 scripts/install_skills.py --full --accept-restricted-licenses。
```

## 还需要准备什么 / What Else You Need

不要把下面这张表理解成“用之前必须额外找齐一堆文件”。大多数写作、事实核查、引注和 Word 排版 skill，真正的用法就是：你把正在处理的草稿、自己已经检索到的法规/案例/PDF/网页截图、课程模板或 Word 文件放在同一个任务文件夹里，再让 AI 按 skill 工作。比如 `legal-fact-checker` 不是要求你重新上网检索，而是帮你检查草稿里的法律依据有没有被你给出的来源支持，缺来源就标出来。

真正比较像“提前配置”的，主要是两类：

- 北大法宝 MCP：如果你想让 AI 自动查法规、法条、案例，需要自行开通/购买对应 MCP 服务。配置时先告诉 AI 你买了哪些服务；可以发服务名称、订单页文字、服务页截图或 token 页面截图，让 AI 帮你判断应安装哪些 MCP。完全没头绪时，再从法规关键词检索、精准法条查找、案例关键词检索这三项开始。
- 《法学引注手册》同版资料：只有当你想让 `legal-citation-comprehensive` 严格按手册全量核验时，才需要准备同版 PDF，并按下面说明生成本地规则索引。普通脚注缺项检查可以先直接用。

下面这张表说的是“每次做任务时最好给 AI 什么材料”，不是让你在安装前全部准备好：

| 你要做什么 | 建议使用 | 使用时给 AI 什么材料 | 缺少时怎么办 |
| --- | --- | --- | --- |
| 检查法律分析有没有编造 | `legal-fact-checker` | 草稿文本；相关法条、案例、PDF、网页链接或数据库截图 | 让 AI 标 `[待补: 来源]`，不要让它凭记忆补 |
| 检查、补全、统一脚注 | `legal-citation-comprehensive` | 脚注文本；原始 PDF、网页、数据库结果、页码；如果要严格按手册全量核验，再准备同版《法学引注手册（第二版）》PDF 和本地规则索引 | 缺页码/案号/出版社等信息时，用 `[待补: ...]`；没有手册索引时，仍可先做类型判断和缺项提示，但不能声称完成手册全量核验 |
| 把核验后的引注写进 Word 脚注 | `legal-citation-automator` | `.docx` 草稿；已经核验过的引注清单或 JSON；最好先跑 `legal-citation-comprehensive` | 还有 `[待补: ...]` 时先不要自动写入正式脚注 |
| 排版法学作业、legal writing 或其他课程文书，生成/修复目录 | `legal-homework-formatter` | 作业说明；草稿；课程/机构模板；姓名、学号、课程名、日期等身份字段；需要目录时说明标题层级 | 没有课程模板时可用内置匿名模板；缺身份字段时让 AI 先问你；目录真实页码以 Word 更新域为准 |
| 生成证据目录 | `evidence-catalog-generator` | 证据材料、文件名、材料说明或条目表；最好提供自己的证据目录 `.docx` 模板 | 没模板时生成通用证据目录；缺证明事项/页码时标 `[待补: ...]` |
| 查法规、法条、案例并回源 | `pkulaw-*` | 北大法宝账号/学校或机构权限；有效 token；你已开通/购买的 MCP 服务名称或截图 | 让 AI 先根据购买信息选择要安装的 MCP；高级 MCP 没订阅时不要硬用，转已开通的 MCP 或 `pkulaw-legal-search` 浏览器兜底 |
| 编辑、抽取、检查 Word/DOCX | `docx-editing`、`docx-cn`、`docx-toolkit`、`legal-toa-formatter` | 待处理 `.docx`；必要时提供原始模板或修改前版本 | 复杂修订/红线优先保留备份；格式异常时先让 AI 做兼容性检查 |

简单说：`legal-citation-comprehensive` 可以先用起来；你把脚注和来源材料给它，它就能帮你找缺项、标占位符。只有你希望它严格按《法学引注手册（第二版）》逐条核验时，才需要另外准备同版 PDF 并生成下面说的规则索引文件。

常用 Python 依赖可以这样安装：

```bash
python3 -m pip install -r requirements.txt
```

高级功能依赖可以按需安装；这些不是法律材料准备，也不是一开始全部必须装：

- `evidence-catalog-generator`、`legal-homework-formatter`、`legal-citation-automator` 主要依赖 Python 包和每次任务的文件；先运行 `python3 -m pip install -r requirements.txt` 即可覆盖常见场景。
- `docx-editing` 的 Safe-DOCX 需要 Node.js 和 `@usejunior/safe-docx`。
- `docx-cn` 的转换、接受修订、生成新 DOCX、渲染图片等高级 Word 操作，可能需要 LibreOffice、pandoc、Poppler 或 `docx-js`。
- 北大法宝 MCP 需要你自己的 PKULaw token 或学校/机构访问权限。
- 第三方手册、教材、数据库导出的全文或索引，请只使用你自己有合法来源的本地文件。

### 《法学引注手册》怎么补 / Citation Handbook Setup

`legal-citation-comprehensive` 是按《法学引注手册（第二版）》设计的。公开仓库不直接分发这本手册的 PDF、OCR 全文或完整规则索引。你需要自己从合法来源取得同一版材料，例如课程资料、图书馆数据库、出版社/期刊社页面、教师或助教提供的文件。

拿到同版 PDF 后，建议这样放：

```text
skills/legal-citation-comprehensive/assets/Law_Journal_Citation_Handbook_2025.pdf
```

如果你手里的是扫描版 PDF，也就是打开后不能选中文字、只能看到图片页，建议先用 WPS、Adobe Acrobat 或其他 OCR 工具把它转成“可搜索 PDF”。再把可搜索 PDF 交给 AI 处理，会明显节省 token，也能减少 AI 直接读整本图片扫描件时的识别错误。

然后把可搜索 PDF 转成机器可读文件。最省事的做法是直接运行构建脚本：

```bash
python3 skills/legal-citation-comprehensive/scripts/build_reference_data.py
```

这个脚本会先检查 PDF 是否可搜索，再提取 `handbook_raw.md`，尝试抽取第 1-150 条规则，生成索引和常见引注类型规则，最后自动运行审计和 self-test。如果 PDF 还是图片扫描件，脚本会停止并提示你先用 WPS/Adobe/OCR 工具转成可搜索 PDF。已有本地参考文件时，脚本默认不会覆盖；确认要重建时再加 `--force`。

成功后本机会生成：

```text
skills/legal-citation-comprehensive/references/handbook_raw.md
skills/legal-citation-comprehensive/references/citation_handbook_structured.md
skills/legal-citation-comprehensive/references/handbook_rule_index.json
skills/legal-citation-comprehensive/references/handbook_rule_index.md
skills/legal-citation-comprehensive/references/citation_rules.json
```

如果自动抽取失败，先打印严格生成 contract，再交给 AI 修复：

```bash
python3 skills/legal-citation-comprehensive/scripts/build_reference_data.py --print-ai-contract
```

也可以把同版的可搜索 PDF 交给你的 AI，让它按下面这段话处理：

```text
请先运行：
python3 skills/legal-citation-comprehensive/scripts/build_reference_data.py

如果脚本提示 PDF 不可搜索，请提醒我先用 WPS/Adobe/OCR 工具转成可搜索 PDF，不要直接全文消耗 token 识别整本扫描件。
如果脚本提示规则抽取不完整，请运行：
python3 skills/legal-citation-comprehensive/scripts/build_reference_data.py --print-ai-contract
然后严格按 contract 修复本地参考数据。

目标是提取第 1-150 条规则，生成 handbook_rule_index.json 和 handbook_rule_index.md。
JSON 每条规则至少包含 rule_number、title、category、text、raw_start_line、raw_end_line。
再根据常见引注类型生成 citation_rules.json，包含 types、required、optional、template、anchors、lookup_guidance。
不要改写规则含义；OCR 不清楚的地方请标 [待核: OCR]。
```

生成后可以测试：

```bash
python3 skills/legal-citation-comprehensive/scripts/audit_reference_data.py
python3 skills/legal-citation-comprehensive/scripts/handbook_lookup.py --rule 1
python3 skills/legal-citation-comprehensive/scripts/self_test.py
```

如果 `audit_reference_data.py` 报 `ERRORS`，先修复本地参考数据；如果 `self_test.py` 没有输出 `ALL TESTS PASSED`，不要声称已经完成手册全量核验。

如果你只有 PDF，还没来得及做索引，也可以先用这个 skill 做“缺什么、去哪找、不要编造”的初步检查；只是不要把结果说成已经完成手册全量核验。

给同学或朋友分享时，可以直接发这份本地配置说明：

```text
docs/法学引注手册本地配置说明.md
```

## 技能清单 / Included Skills

### 北大法宝与法律检索 / PKULaw MCP and Legal Research

说明：这里的部分 PKULaw workflow skill 是根据公开可见资料、公开接口说明和个人使用经验整理的社区/个人工作流，不是北大法宝官方发布的产品说明，也不包含任何真实 token、账号、cookie 或私有数据库内容。实际使用时，用户仍需自行确认已经合法取得北大法宝访问权限，并开通/购买对应 MCP 服务。

Note: Some PKULaw workflow skills here are community/personal workflows organized from publicly visible materials, public interface descriptions, and practical usage notes. They are not official PKULaw product documentation and do not include real tokens, accounts, cookies, or private database content. Users must have lawful PKULaw access and the relevant MCP subscriptions before using them.

| Skill | 中文说明 | English |
| --- | --- | --- |
| `pkulaw-mcp-installer` | 安装/配置北大法宝 MCP，要求用户本地提供 token | Install and configure PKULaw MCP with a user-provided local token |
| `pkulaw-mcp-legal-research` | 北大法宝法律研究总路由 | General PKULaw legal research router |
| `pkulaw-mcp-law-retrieval` | 法律法规关键词检索 | Statute and regulation keyword retrieval |
| `pkulaw-mcp-fatiao-precise` | 已知法规名和条号时精准取回法条 | Precise article lookup by law name and article number |
| `pkulaw-mcp-case-retrieval` | 司法案例关键词检索 | Judicial case keyword retrieval |
| `pkulaw-legal-search` | 北大法宝网页/浏览器兜底检索流程 | Browser fallback workflow for PKULaw web research |
| `pkulaw-mcp-citation-validator` | 法条引用核验与纠偏 | Citation validation and correction |
| `pkulaw-mcp-doc-link` | 给法规/案例引用补可追溯链接 | Add traceable source links to legal references |
| `pkulaw-mcp-grounded-answer` | 基于已核验来源生成法律答复草稿 | Draft grounded legal answers from verified sources |
| `pkulaw-mcp-case-memo` | 类案检索报告/办案备忘 | Case research memo workflow |
| `pkulaw-mcp-contract-review-lite` | 单份合同合规初筛 | Lightweight contract compliance review |
| `pkulaw-mcp-batch-contract-screening` | 批量合同合规初筛 | Batch contract screening |

其他 PKULaw 工作流还包括：`pkulaw-mcp-case-number`、`pkulaw-mcp-law-recognition`、`pkulaw-mcp-opinion-citation-check`、`pkulaw-mcp-regulatory-reply-check`、`pkulaw-mcp-governance-research-memo`、`pkulaw-mcp-labor-employment-answer`、`pkulaw-mcp-semantic-nlsql`。

Additional PKULaw workflows include case-number extraction, law-recognition, opinion citation checks, regulatory reply checks, governance memos, labor/employment answers, and semantic search routing.

配置时先确认用户已经购买/开通了哪些 MCP；用户可以提供服务名称、购买页面文字、服务页截图或 token 页面截图。`law-keyword`、`fatiao`、`case-keyword` 是最常见的基础组合；`citation-validator`、`doc-link`、`case-number`、`semantic-nlsql`、`law-recognition` 等属于高级可选能力。只有确认已经购买/开通对应订阅时，才让 AI 调用这些 workflow。没有高级订阅时，应改用已开通的 MCP + 浏览器兜底，不要让 AI 声称已经完成高级 MCP 核验。

Before configuration, ask which MCP services the user has purchased or enabled. The user can provide service names, text from the purchase page, screenshots, or the token page. `law-keyword`, `fatiao`, and `case-keyword` are the common starter set. Advanced capabilities such as `citation-validator`, `doc-link`, `case-number`, `semantic-nlsql`, and `law-recognition` should be used only when the user has confirmed the relevant subscription. Without those subscriptions, use the enabled MCP services plus browser fallback instead of claiming advanced MCP verification.

### 法律写作与引注 / Citation and Legal Writing

| Skill | 中文说明 | English |
| --- | --- | --- |
| `legal-fact-checker` | 法律产出事实核查，防止编造法律、案例、事实 | Fact-check legal outputs and prevent fabricated laws, cases, or facts |
| `legal-citation-comprehensive` | 法学引注诊断、补全、格式化；缺信息时输出占位符 | Diagnose, complete, and format legal citations with placeholder-safe missing elements |
| `legal-citation-automator` | 把已核验引注写入 DOCX 脚注 | Insert verified citations into DOCX footnotes |
| `legal-homework-formatter` | 法学作业 Word 格式处理，支持目录生成/修复；公开版会询问姓名/学号 | Format legal homework DOCX files, including TOC generation/repair; public version asks for user identity fields |
| `legal-toa-formatter` | Table of Authorities 点号填充与对齐 | Format Table of Authorities dot leaders |
| `evidence-catalog-generator` | 整理用户提供的证据材料，并填入证据目录模板 | Organize user-provided evidence materials into an evidence catalog template |
| `case-retrieval-display-table` | 将检索到的案例整理为横向案例卡片展示表；公开版使用 `[律所名称]` 占位符 | Organize retrieved cases into a horizontal case-card display table with law-firm placeholders |

`legal-homework-formatter` 现在包含一份匿名化 Word 模板：

`legal-homework-formatter` now includes an anonymized Word template:

```text
skills/legal-homework-formatter/assets/legal-homework-template-anonymized.docx
```

如果用户本地有课程模板、legal writing 模板或机构文书模板，应优先使用用户提供的模板。没有模板时，再使用这个匿名模板作为保守基准。材料清单和“缺什么去哪里找”的说明见：

If the user has a course, legal-writing, or institutional document template, use the user's template first. If no template is available, use the anonymized template as a conservative fallback. For the input checklist and missing-information workflow, see:

```text
skills/legal-homework-formatter/references/user_materials_guide.md
```

### Word/DOCX 辅助 / DOCX Helpers

- `docx-editing`：保留格式地编辑既有 `.docx` 文件。
- `docx-cn`：中文 Word 文档处理辅助。
- `docx-toolkit`：提取 DOCX 文本、表格、图片等内容。

- `docx-editing`: preservation-sensitive editing for existing `.docx` files.
- `docx-cn`: Chinese Word document helpers.
- `docx-toolkit`: extract text, tables, and images from DOCX files.

`case-retrieval-display-table` 需要 Node.js 和 `docx` 包来生成横向 Word 表格；如果当前运行时没有该依赖，请在仓库根目录或该 skill 目录运行 `npm install docx`。

`case-retrieval-display-table` needs Node.js and the `docx` package to generate landscape Word tables. If the dependency is missing, run `npm install docx` at the repository root or inside that skill directory.

## 安装方式 / Installation

一键安装本仓库 skills，并安装默认第三方推荐项：

Install this repository's skills and the default third-party recommendations:

```bash
python3 scripts/install_skills.py
```

安装本仓库 skills 和全部第三方推荐项：

Install this repository's skills and all recommended third-party skills:

```bash
python3 scripts/install_skills.py --full --accept-restricted-licenses
```

只安装本仓库 skills：

Install only this repository's skills:

```bash
python3 scripts/install_skills.py --skip-third-party
```

安装到其他 agent 技能目录：

Install into another agent skill directory:

```bash
python3 scripts/install_skills.py --skills-dir ~/.workbuddy/skills
```

复制需要的 skill 文件夹到你的 agent 技能目录：

Copy the skill folders you need into your agent's skill directory:

```bash
cp -R skills/legal-fact-checker ~/.codex/skills/
cp -R skills/legal-citation-comprehensive ~/.codex/skills/
cp -R skills/legal-citation-automator ~/.codex/skills/
```

如果你的运行时不是 Codex，请把目标路径替换成对应的 skills 目录。

If your runtime is not Codex, replace `~/.codex/skills/` with the relevant skills directory.

## 第三方优秀法律 Skills / Recommended Third-Party Skills

本仓库也维护一个第三方法律 skill 推荐索引，方便用户让 AI 一次性理解“有哪些好东西、分别适合干什么、能不能自动安装”。

This repository also includes a third-party legal-skill recommendation index so an AI agent can understand what is recommended, what each project is for, and whether it can be installed automatically.

```bash
python3 scripts/install_third_party_skills.py --list
python3 scripts/install_skills.py
```

默认只安装 Apache-2.0 项；受限许可项目需要用户明确确认：

By default, only Apache-2.0 entries are installed. Restricted-license projects require explicit user confirmation:

```bash
python3 scripts/install_third_party_skills.py --all --accept-restricted-licenses
```

详细说明见：

See:

```text
THIRD_PARTY_RECOMMENDED_SKILLS.md
third_party_skills.json
```

注意：第三方项目始终从原作者 GitHub 仓库克隆。本仓库不是第三方源码镜像，也不公开分发受限许可项目的改写版。

Note: third-party projects are always cloned from the original author's GitHub repositories. This repository is not a source mirror and does not distribute modified versions of restricted-license projects.

## 配置北大法宝 MCP / PKULaw MCP Setup

公开版不会携带任何真实 token。请在本机用环境变量或交互输入提供自己的北大法宝 token。

The public version does not include any real token. Provide your own PKULaw token locally through an environment variable or interactive prompt.

最简单的流程：

1. 在浏览器搜索“北大法宝 MCP”，进入北大法宝 MCP 服务页面。
2. 按需购买/开通服务。不会选时，可以先从法规关键词检索、精准法条查找、案例关键词检索这三项开始。
3. 页面生成 token 后，在本机通过环境变量、终端交互或 AI 客户端的本地配置提供给 AI。
4. 把你购买的服务名称、服务页面文字或截图给 AI，让它判断应安装哪些 MCP。
5. 对 AI 说：请使用 `pkulaw-mcp-installer`，把我的北大法宝 token 和已购买服务配置到当前运行时的 MCP 配置文件里。

Simplest setup:

1. Search the web for "北大法宝 MCP" and open the PKULaw MCP service page.
2. Purchase or enable the services you need. If you are unsure, start with statute keyword search, precise article lookup, and case keyword search.
3. After the page generates a token, provide it locally through an environment variable, terminal prompt, or your AI client's local config.
4. Give your AI the purchased service names, page text, or screenshots so it can choose which MCP services to install.
5. Ask your AI to use `pkulaw-mcp-installer` to configure the token and purchased services in the current runtime's MCP config file.

```bash
cd skills/pkulaw-mcp-installer
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --mcp-path ~/.workbuddy/mcp.json
```

安装前最好先让 AI 根据你购买的服务名称或截图选择 `--services`。如果没有提供 `--services`，脚本会按基础三项安装；已经购买高级 MCP 时，可以显式启用：

Before installing, ask your AI to choose `--services` from the service names or screenshots you provide. If `--services` is omitted, the script installs the basic three services. If you have purchased advanced MCP services, enable them explicitly:

```bash
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --services all --mcp-path ~/.workbuddy/mcp.json
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --services pkulaw-citation,pkulaw-hyperlink --mcp-path ~/.workbuddy/mcp.json
```

注意：

- 真实 token 只放在本机环境变量、MCP 配置或私有文件里，不要写入 Git commit、Issue、截图、示例或模板。
- 不要把真实 cookie、浏览器会话、学校账号信息提交到仓库。
- 如果目标运行时不是 WorkBuddy，请把 `--mcp-path` 改成对应 MCP 配置文件。

Notes:

- Keep real tokens in local environment variables, MCP config files, or private files. Do not commit them to Git, Issues, screenshots, examples, or templates.
- Do not publish browser sessions, school account details, or private login data.
- If your runtime is not WorkBuddy, change `--mcp-path` to the correct MCP config file.

## 引注手册与参考数据 / Citation Handbook Data

`legal-citation-comprehensive` 可以使用手册衍生的规则索引来增强覆盖率，但公开仓库默认不分发第三方出版物 PDF、OCR 全文或完整派生索引。

`legal-citation-comprehensive` can use handbook-derived rule indexes for fuller coverage, but this public repository does not distribute third-party handbook PDFs, OCR text, or full derived indexes by default.

请见：

See:

```text
skills/legal-citation-comprehensive/references/README_REFERENCE_DATA.md
```

用户可以在本地自行提供有合法来源的参考数据。

Users may provide legally obtained reference data locally.

## 隐私与开源边界 / Privacy and Publication Boundaries

这个仓库按公开发布准备，原则上不应包含：

This repository is prepared for public release and should not contain:

- 真实姓名、学号、手机号、邮箱、身份证号；
- 本机绝对路径或维护者账号路径；
- API token、Bearer token、cookie、私钥、密码；
- 私有课程模板、作业文件、案件材料、证据材料；
- 未确认再分发权利的第三方书籍、PDF、OCR 原文或全文索引。

- Real names, student IDs, phone numbers, emails, or government IDs;
- Maintainer local paths or account-specific paths;
- API tokens, bearer tokens, cookies, private keys, or passwords;
- Private course templates, homework files, case materials, or evidence files;
- Third-party books, PDFs, OCR dumps, or full-text indexes without confirmed redistribution rights.

当工作流需要用户身份信息时，公开版 skill 应询问用户，或使用 `[待补: ...]` 占位符。

When a workflow needs user-specific information, the public skill should ask the user or use `[待补: ...]` placeholders.

## 给使用者的提醒 / Notes for Users

这些 skills 的目标是让法律检索、引注和 Word 排版更可复核，而不是替代人工判断。使用时建议保留原始来源文件、数据库链接或检索截图，方便回头核对。

These skills are meant to make legal research, citations, and Word formatting easier to review. They are not a substitute for human judgment. Keep source files, database links, or search screenshots so that outputs can be checked later.

如果某个信息缺失，工具可能会留下 `[待补: ...]` 占位符。提交、发送或归档前，请逐项补齐并核验。

If information is missing, a workflow may leave `[待补: ...]` placeholders. Fill and verify them before submitting, sending, or archiving the document.

## 免责声明 / Legal Notice

这些 skills 是研究、写作和文档处理辅助工具，不构成法律意见，也不能替代律师、教师或权威数据库的复核。

These skills are research, drafting, and document-processing aids. They do not provide legal advice and do not replace professional, academic, or authoritative-source review.
