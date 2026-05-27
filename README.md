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

如果你只是想尽快用起来，不需要先理解 MCP、脚本或 Git。按下面做：

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
- 不要把学校账号、数据库 token、cookie、身份证号、手机号直接贴到公开聊天或 GitHub。
- 交作业前自己再核对一遍法规名称、条号、案例名称、案号、页码和脚注。

PKULaw/北大法宝相关 skills 适合已经有学校或机构访问权限、并愿意自行开通/购买对应 MCP 服务的同学。刚开始建议先开通最基础的三个 MCP：法规关键词检索、精准法条查找、案例关键词检索；预算充足或需求更复杂时，再继续开通更多 MCP。MCP 检索通常比浏览器兜底快很多。没有 token 或登录权限也可以先不用，优先用上面几个写作、引注和 Word 处理 skill。

## 还需要准备什么 / What Else You Need

多数 skill 本身只是“工作方法 + 脚本”，真正能不能顺利跑起来，取决于你有没有把材料、模板、数据库权限和依赖准备好。可以按这张表检查：

| 你要做什么 | 建议使用 | 还需要你准备什么 | 没有时怎么办 |
| --- | --- | --- | --- |
| 检查法律分析有没有编造 | `legal-fact-checker` | 草稿文本；相关法条、案例、PDF、网页链接或数据库截图 | 让 AI 标 `[待补: 来源]`，不要让它凭记忆补 |
| 检查、补全、统一脚注 | `legal-citation-comprehensive` | 脚注文本；原始 PDF、网页、数据库结果、页码；如果要严格按手册全量核验，再准备同版《法学引注手册（第二版）》PDF 和本地规则索引 | 缺页码/案号/出版社等信息时，用 `[待补: ...]`；没有手册索引时，仍可先做类型判断和缺项提示，但不能声称完成手册全量核验 |
| 把核验后的引注写进 Word 脚注 | `legal-citation-automator` | `.docx` 草稿；已经核验过的引注清单或 JSON；最好先跑 `legal-citation-comprehensive` | 还有 `[待补: ...]` 时先不要自动写入正式脚注 |
| 排版法学作业、legal writing 或其他课程文书 | `legal-homework-formatter` | 作业说明；草稿；课程/机构模板；姓名、学号、课程名、日期等身份字段 | 没有课程模板时可用内置匿名模板；缺身份字段时让 AI 先问你 |
| 生成证据目录 | `evidence-catalog-generator` | 证据材料、文件名、材料说明或条目表；最好提供自己的证据目录 `.docx` 模板 | 没模板时生成通用证据目录；缺证明事项/页码时标 `[待补: ...]` |
| 查法规、法条、案例并回源 | `pkulaw-*` | 北大法宝账号/学校或机构权限；有效 token；自行开通/购买对应 MCP，建议先配法规关键词检索、精准法条查找、案例关键词检索这三项 | MCP 搜索通常比浏览器兜底快很多；没 token 时先用网页登录或学校 IP；MCP 不通时用 `pkulaw-legal-search` 走浏览器兜底 |
| 编辑、抽取、检查 Word/DOCX | `docx-editing`、`docx-cn`、`docx-toolkit`、`legal-toa-formatter` | 待处理 `.docx`；必要时提供原始模板或修改前版本 | 复杂修订/红线优先保留备份；格式异常时先让 AI 做兼容性检查 |

简单说：`legal-citation-comprehensive` 可以先用起来；你把脚注和来源材料给它，它就能帮你找缺项、标占位符。只有你希望它严格按《法学引注手册（第二版）》逐条核验时，才需要另外准备同版 PDF 并生成下面说的规则索引文件。

常用 Python 依赖可以这样安装：

```bash
python3 -m pip install -r requirements.txt
```

有些功能还需要额外软件或权限：

- `docx-editing` 的 Safe-DOCX 需要 Node.js 和 `@usejunior/safe-docx`。
- `docx-cn` 接受修订、转换等高级 Word 操作时，可能需要本机安装 LibreOffice。
- 北大法宝 MCP 需要你自己的 PKULaw token 或学校/机构访问权限。
- 第三方手册、教材、数据库导出的全文或索引，请只使用你自己有合法来源的本地文件。

### 《法学引注手册》怎么补 / Citation Handbook Setup

`legal-citation-comprehensive` 是按《法学引注手册（第二版）》设计的。公开仓库不直接分发这本手册的 PDF、OCR 全文或完整规则索引。你需要自己从合法来源取得同一版材料，例如课程资料、图书馆数据库、出版社/期刊社页面、教师或助教提供的文件。

拿到同版 PDF 后，建议这样放：

```text
skills/legal-citation-comprehensive/assets/Law_Journal_Citation_Handbook_2025.pdf
```

如果你手里的是扫描版 PDF，也就是打开后不能选中文字、只能看到图片页，建议先用 WPS、Adobe Acrobat 或其他 OCR 工具把它转成“可搜索 PDF”。再把可搜索 PDF 交给 AI 处理，会明显节省 token，也能减少 AI 直接读整本图片扫描件时的识别错误。

然后把可搜索 PDF 转成机器可读文件：

```text
skills/legal-citation-comprehensive/references/handbook_raw.md
skills/legal-citation-comprehensive/references/citation_handbook_structured.md
skills/legal-citation-comprehensive/references/handbook_rule_index.json
skills/legal-citation-comprehensive/references/handbook_rule_index.md
skills/legal-citation-comprehensive/references/citation_rules.json
```

最省事的做法是把同版的可搜索 PDF 交给你的 AI，让它按下面这段话处理：

```text
请先确认这份《法学引注手册（第二版）》PDF 是否可搜索。
如果它已经可搜索，请直接提取成 Markdown，保存为 handbook_raw.md。
如果它还是图片扫描件，请提醒我先用 WPS/Adobe/OCR 工具转成可搜索 PDF，不要直接全文消耗 token 识别整本扫描件。
然后提取第 1-150 条规则，生成 handbook_rule_index.json 和 handbook_rule_index.md。
JSON 每条规则至少包含 rule_number、title、category、text、raw_start_line、raw_end_line。
再根据常见引注类型生成 citation_rules.json，包含 types、required、optional、template、anchors、lookup_guidance。
不要改写规则含义；OCR 不清楚的地方请标 [待核: OCR]。
```

生成后可以测试：

```bash
python3 skills/legal-citation-comprehensive/scripts/handbook_lookup.py --rule 1
python3 skills/legal-citation-comprehensive/scripts/self_test.py
```

如果你只有 PDF，还没来得及做索引，也可以先用这个 skill 做“缺什么、去哪找、不要编造”的初步检查；只是不要把结果说成已经完成手册全量核验。

## 技能清单 / Included Skills

### 北大法宝与法律检索 / PKULaw MCP and Legal Research

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

### 法律写作与引注 / Citation and Legal Writing

| Skill | 中文说明 | English |
| --- | --- | --- |
| `legal-fact-checker` | 法律产出事实核查，防止编造法律、案例、事实 | Fact-check legal outputs and prevent fabricated laws, cases, or facts |
| `legal-citation-comprehensive` | 法学引注诊断、补全、格式化；缺信息时输出占位符 | Diagnose, complete, and format legal citations with placeholder-safe missing elements |
| `legal-citation-automator` | 把已核验引注写入 DOCX 脚注 | Insert verified citations into DOCX footnotes |
| `legal-homework-formatter` | 法学作业 Word 格式处理；公开版会询问姓名/学号 | Format legal homework DOCX files; public version asks for user identity fields |
| `legal-toa-formatter` | Table of Authorities 点号填充与对齐 | Format Table of Authorities dot leaders |
| `evidence-catalog-generator` | 整理用户提供的证据材料，并填入证据目录模板 | Organize user-provided evidence materials into an evidence catalog template |

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

## 安装方式 / Installation

复制需要的 skill 文件夹到你的 agent 技能目录：

Copy the skill folders you need into your agent's skill directory:

```bash
cp -R skills/legal-fact-checker ~/.codex/skills/
cp -R skills/legal-citation-comprehensive ~/.codex/skills/
cp -R skills/legal-citation-automator ~/.codex/skills/
```

如果你的运行时不是 Codex，请把目标路径替换成对应的 skills 目录。

If your runtime is not Codex, replace `~/.codex/skills/` with the relevant skills directory.

## 配置北大法宝 MCP / PKULaw MCP Setup

公开版不会携带任何真实 token。请在本机用环境变量或交互输入提供自己的北大法宝 token。

The public version does not include any real token. Provide your own PKULaw token locally through an environment variable or interactive prompt.

```bash
cd skills/pkulaw-mcp-installer
PKULAW_AUTH_TOKEN="..." python3 scripts/install_pkulaw_mcp.py --mcp-path ~/.workbuddy/mcp.json
```

注意：

- 不要把真实 token 写入 Git commit、Issue、截图或聊天记录。
- 不要把真实 cookie、浏览器会话、学校账号信息提交到仓库。
- 如果目标运行时不是 WorkBuddy，请把 `--mcp-path` 改成对应 MCP 配置文件。

Notes:

- Do not commit real tokens, cookies, screenshots, or chat transcripts containing credentials.
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
