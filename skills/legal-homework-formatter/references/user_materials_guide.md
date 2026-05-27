# Legal Homework Formatter: 用户材料清单 / User Materials Guide

这份说明给使用者和 AI agent 看：本地有什么材料时应怎么用，缺材料时应该去哪里找，不能靠模型猜。

This guide tells users and AI agents what local materials to provide, how to use them, and where to look when something is missing. Do not guess missing facts.

## 一、最理想的输入 / Ideal Inputs

如果你要把一份法律作业、legal writing 作业或类似 Word 文书排成课程/机构要求的格式，最好提供：

For legal homework, legal writing, or similar Word submissions, provide:

| 材料 | 用途 | 常见文件 |
| --- | --- | --- |
| 作业题目或任务说明 | 确认题号、标题、提交要求、是否需要页码/目录/脚注 | PDF、DOCX、课程网页截图 |
| 课程/机构格式模板 | 作为 DOCX 样式基准，保留页边距、字号、脚注样式、标题层级 | `.docx` 模板 |
| 草稿正文 | 要排版和插入脚注的正文 | `.docx`、Markdown、纯文本 |
| 引用来源 | 防止法条、案例、文献引注被编造 | PDF、网页链接、北大法宝/Westlaw/Lexis 检索结果 |
| 身份字段 | 生成标题和文件名 | 姓名、学号/编号、课程名、日期前缀 |

## 二、缺什么时去哪里找 / Where To Find Missing Materials

| 缺少内容 | 先去哪里找 | 找不到时怎么处理 |
| --- | --- | --- |
| 日期前缀 | 作业文件名、课程通知、提交说明、邮件标题 | 使用 `[待补: 日期]`，不要猜发布日期或截止日 |
| 作业序号/标题 | 作业题目、课程 LMS、PPT、教师邮件 | 使用 `[待补: 作业序号]` 或 `[待补: 标题]` |
| 姓名/学号 | 用户本人确认 | 使用 `[待补: 姓名]`、`[待补: 学号]` |
| 课程模板 | 用户本地课程文件夹、教师/助教发的模板、旧作业附件 | 使用本 skill 的匿名模板作为保守基准，并说明未能核对课程专属格式 |
| 法条原文 | 北大法宝、官方法规库、课程指定资料 | 留 `[待补: 法条原文/来源]`，不得编造 |
| 案例信息 | 北大法宝、裁判文书来源、课程资料 | 留 `[待补: 案号/法院/裁判日期/来源]` |
| 文献页码 | PDF 原文、数据库页面、图书目录/索引 | 留 `[待补: 页码]` |
| 引注格式依据 | `legal-citation-comprehensive`、课程手册、教师要求 | 标明未核验，不要强行格式化成确定结论 |

## 三、内置匿名模板 / Bundled Anonymized Template

本 skill 提供一个匿名化 DOCX 模板：

This skill includes an anonymized DOCX template:

```text
assets/legal-homework-template-anonymized.docx
```

它保留了课程作业常用的 Word 样式结构：

- 标题 run 拆分结构：`[日期] graded homework [序号]-[姓名]-[学号]`
- 中文宋体、英文 Times New Roman
- 正文五号、1.25 倍行距、首行缩进、两端对齐
- 脚注小五、上标脚注标记、连续脚注编号
- A4、页边距、目录和标题层级样式

It preserves the common Word style structure:

- Split title runs: `[日期] graded homework [序号]-[姓名]-[学号]`
- SimSun for Chinese and Times New Roman for English
- Body text in 10.5 pt, 1.25 line spacing, first-line indent, justified
- Footnotes in 9 pt with superscript references and continuous numbering
- A4 page settings, margins, TOC, and heading styles

这个模板已经做过匿名化处理：姓名、学号、原文件名、作者信息、修改者信息、内部 docId/rsid 编辑痕迹、私有 custom property 都不应保留。

The template has been anonymized: names, student IDs, original private filename, author metadata, last-modified metadata, internal docId/rsid traces, and private custom properties should not remain.

## 四、推荐工作流 / Recommended Workflow

1. 先读作业说明，列出必须字段。
2. 找用户提供的课程模板；如果没有，使用 `assets/legal-homework-template-anonymized.docx`。
3. 将草稿正文转入模板，不要用空白 Word 默认样式。
4. 对每个法条、案例、文献引用做来源核验。
5. 缺失信息写成 `[待补: ...]`，并在最终 checklist 里列出。
6. 插入脚注后检查 `word/document.xml` 和 `word/footnotes.xml` 的引用 ID 是否匹配。
7. 最后在 Word 和 WPS 至少各打开一次，检查脚注、标题、页码、目录和字体。

1. Read the assignment instructions and list all required fields.
2. Use the user-provided course template when available; otherwise use `assets/legal-homework-template-anonymized.docx`.
3. Move the draft into the template instead of starting from Word defaults.
4. Verify every statute, case, and secondary source citation.
5. Use `[待补: ...]` placeholders for missing information and list them in the final checklist.
6. After inserting footnotes, verify that `word/document.xml` references match `word/footnotes.xml` definitions.
7. Open the final document in both Word and WPS when possible to check footnotes, headings, page numbers, TOC, and fonts.

## 五、AI 不能做的事 / What The AI Must Not Do

- 不得默认填入维护者姓名、学号、学校、邮箱或本机路径。
- 不得把真实 token、cookie、浏览器会话、课程私有材料写入输出。
- 不得凭记忆编造法规、案例、案号、页码或文献出处。
- 不得在没有模板时声称“完全符合课程模板”；只能说“使用匿名模板/保守基准”。
- 不得为了减少脚注数量，把不同来源强行合并到一个脚注。

- Do not default to a maintainer's name, student ID, school, email, or local path.
- Do not write real tokens, cookies, browser sessions, or private course materials into outputs.
- Do not fabricate statutes, cases, docket numbers, page numbers, or bibliographic facts.
- Do not claim full compliance with a missing course template; say that the anonymized fallback template was used.
- Do not merge unrelated sources into one footnote just to reduce footnote count.
