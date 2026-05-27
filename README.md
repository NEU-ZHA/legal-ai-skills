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

如果用户本地有课程模板、legal writing 模板、negotiation writing 模板或机构文书模板，应优先使用用户提供的模板。没有模板时，再使用这个匿名模板作为保守基准。材料清单和“缺什么去哪里找”的说明见：

If the user has a course, legal-writing, negotiation-writing, or institutional document template, use the user's template first. If no template is available, use the anonymized template as a conservative fallback. For the input checklist and missing-information workflow, see:

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
