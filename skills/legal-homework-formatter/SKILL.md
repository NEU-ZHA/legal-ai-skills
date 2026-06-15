---
name: legal-homework-formatter
description: 用于处理中国法学作业的格式调整。当用户需要创建或修改法学作业 Word 文档，特别是涉及脚注格式、法律文件引用格式、标题格式调整、目录生成/修复时使用此 skill。必须先询问并确认姓名、学号、课程模板等个人/课程信息；不得默认填入维护者或示例个人信息。触发词：作业格式、Word格式、脚注格式、标题对齐、段落格式、目录、TOC、法学作业。
---

# Legal Homework Formatter

## Purpose

This skill provides standardized formatting workflows for Chinese legal homework assignments. It helps documents follow a user-provided course template and the Law Journal Citation Handbook, while resolving common compatibility issues between WPS and Microsoft Word.

## When to Use

Use this skill when:
- Creating new Chinese legal homework assignments in Word format
- Formatting existing homework to meet citation standards
- Fixing footnote display issues between WPS and Word
- Adjusting title, heading, or citation formats
- Generating or repairing a homework table of contents (目录/TOC)
- Converting draft content to properly formatted legal documents

## Privacy and Required Inputs

This public version must never default to the maintainer's personal information or a private course template.

Before generating a title, filename, header, or metadata, ask the user for:

- assignment date prefix;
- assignment number/title;
- student name;
- student ID, if required;
- course or instructor-specific template, if required.

If the user does not provide a required identity field, use an explicit placeholder such as `[待补: 姓名]` or `[待补: 学号]` and flag it in the final checklist. Do not infer, reuse, or hard-code a real person's name, ID, school, email address, or local file path.

## Reference Template

Use the user-provided course reference template as the base for generating homework documents when one is available. Its style system is the authoritative source for course-specific formatting. If no template is provided, create a conservative `.docx` with the formatting rules below and clearly tell the user which template-dependent checks could not be performed.

This public skill also includes an anonymized fallback template at:

```text
assets/legal-homework-template-anonymized.docx
```

Use it when the user needs a working Word style base but has not provided a private course template. The template keeps the formatting structure while replacing identity fields with `[日期]`, `[序号]`, `[姓名]`, and `[学号]`. Do not rename it to a private course filename when publishing or redistributing the skill.

For a user-facing material checklist and missing-information workflow, read:

```text
references/user_materials_guide.md
```

## Lessons From the 2026-05-13 Homework Formatting Pass

When the user asks to "strictly follow the homework skill" or provides the course reference template/PPT, apply these verified rules rather than relying on generic `python-docx` defaults:

- Use the user-provided reference template as the ZIP/DOCX base when available, not a blank document.
- Match the course PPT's "三名同一" rule: email subject, attachment file name, and document title should be identical.
- Main title: 小三, centered, no first-line indent, `spacing after="156"`, split the title into runs so Chinese name and hyphens render in 宋体 while English/date/student ID render in Times New Roman.
- Body paragraphs: 五号, 宋体/Times New Roman, first-line indent `420` twips, line spacing `300` (1.25x), paragraph after `156` twips, justified alignment.
- Paragraph-after unit check: `w:after="156"` is stored in OOXML twips, equal to 7.8 pt because Word uses twentieths of a point. In the civil-law reference template this corresponds to half of the document grid line pitch (`docGrid linePitch="312"`), so Word/WPS may display the same setting as about `0.5 行` or `7.8 磅` depending on UI/context. Treat these as equivalent, not conflicting.
- Footnotes: 小五, 宋体/Times New Roman, single line spacing, left aligned, no first-line indent, no paragraph spacing before/after.
- Footnote numbering: remove `<w:numRestart w:val="eachPage"/>` from `word/settings.xml` and any section-level `footnotePr`; homework footnotes should number continuously across the whole document. The reference template contains `eachPage`, but that setting causes duplicate-looking footnote numbers page by page.
- If using manual Chinese heading numbers such as `一、` and `二、`, remove `<w:numPr>` from heading styles `1`, `2`, and `3`; otherwise Word may visually render duplicate numbering.
- If the document was generated from Markdown/Pandoc or any converter that applies Word `Heading1`/`Heading2` styles, do not only override run fonts and sizes. Also remove inherited heading paragraph styles and decorations from the final document, or Word may still render blue/green heading colors and automatic bullets/numbering:
  - remove `<w:pStyle w:val="Heading1"/>`, `<w:pStyle w:val="Heading2"/>`, and similar converted heading styles from manually numbered titles/headings;
  - remove paragraph-level `<w:numPr>` from all title/heading paragraphs;
  - clear run-level `<w:color>` values inherited from styles/themes, especially `w:themeColor`, then set direct black color `<w:color w:val="000000"/>`;
  - remove `<w:highlight>` and `<w:shd>` on generated title/heading runs unless the user explicitly asks for color.
  - run `python3 scripts/fix_pandoc_heading_artifacts.py input.docx --output output.docx` before the final compatibility check when the source DOCX came from Pandoc/Markdown.
  This bug appeared in a 2026-05-27 Word check: Pandoc's heading style survived OOXML post-processing, so Word displayed the main title and headings in blue-green and with black bullet markers even though font/size had been overwritten.
- After running any quote normalizer, re-check footnotes: standalone curly quote runs in footnotes may accidentally inherit body size. Force footnote quote runs (`“”‘’`) back to 小五 (`w:sz=18`) and 宋体.
- Do not save a finished footnoted document with `python-docx` after manually editing footnotes unless you have verified `word/footnotes.xml` and `footnoteReference` markers are preserved. Prefer ZIP/XML surgery for final footnote and quote fixes.
- Before writing footnote text into DOCX, strip leading/trailing whitespace from the citation payload. The template may use one normal delimiter space after the footnote number, but the citation text itself must not start with an extra blank.
- Do not place two footnote references back-to-back after the same sentence-final punctuation. If multiple sources support the same claim, combine them in one footnote separated by `；`; if they support different clauses, place each marker after its own clause or legal article.
- The homework template may include Chinese TOC styles. To add a directory, use the template's TOC styles and a clean Word field, but do not copy dirty old preview entries such as `PAGEREF _Toc...`.
- For Word compatibility, do not set `<w:updateFields w:val="true"/>` just to force TOC updates. Word will show a field-update prompt. Also avoid copying a template's whole `w:sdt` TOC content-control shell into generated files unless you have verified Word opens without repair prompts. Prefer clean ordinary TOC field paragraphs plus static preview entries.
- Preserve WordprocessingML child order in generated paragraph properties. Word may show "unreadable content" even when ZIP/XML parsing succeeds if, for example, `w:spacing` appears before `w:tabs` in a TOC entry or `w:pageBreakBefore` is inserted before `w:pStyle`.
- Homework TOC layout: the document title and `目录` stay on the first page; the main body starts on the next page by setting `w:pageBreakBefore` on the first body paragraph, not by inserting a visible `<w:br w:type="page"/>`.
- Heading detection for TOC must use both style and text structure. Existing styles `1/2/3` are strong clues but not always trustworthy because users often hand-format titles. Confirm with text patterns like `一、`, `（一）`, and `1.` before including a paragraph in the TOC.

## Style System (OOXML Reference)

Based on the reference template's `styles.xml`:

### Paragraph Styles

| styleId | Name | sz (半磅) | 对应中文 | Bold | Other |
|---------|------|----------|---------|------|-------|
| `a` | Normal | 21 (五号/10.5pt) | 正文 | No | line=300 (1.25倍), after=50, firstLine=200, widowControl=0, adjustRightInd=0, snapToGrid=0 |
| `1` | heading 1 | 28 (四号/14pt) | 一级标题 | Yes | keepNext, keepLines, numPr (auto "一、") |
| `2` | heading 2 | 24 (小四号/12pt) | 二级标题 | Yes | keepNext, keepLines, numPr (auto "（一）") |
| `3` | heading 3 | 21 (五号) | 三级标题 | Yes | keepNext, keepLines |
| `a7` | footnote text | 18 (小五号/9pt) | 脚注文本 | No | line=240 (单倍), left aligned |
| `TOC10` | TOC 标题1 | 28 (四号/14pt) | 目录标题 | No | centered, black |
| `TOC1` | toc 1 | 21/22-ish | 一级目录项 | No | right tab with dot leader when generated |
| `TOC2` | toc 2 | 21/22-ish | 二级目录项 | No | indented TOC item |
| `TOC3` | toc 3 | 21/22-ish | 三级目录项 | No | further indented TOC item |

### Character Styles

| styleId | Name | Purpose |
|---------|------|---------|
| `ab` | footnote reference | Superscript footnote markers (上标) |

### docDefaults

- `sz=21` (五号/10.5pt), `szCs=22` (default paragraph-level rPr)
- Default fonts in docDefaults: `ascii="Times New Roman" eastAsia="宋体" hAnsi="Times New Roman" cs="Times New Roman"`
- These are explicit font names, NOT theme font references (minorHAnsi/minorEastAsia)

## Document Generation Workflow

### Step 1: Gather Required Materials

1. **Homework questions** (PDF/DOCX) - assignment requirements
2. **Reference template** - user-provided formatting base, if required by the course
3. **Student information** - ask the user for name (姓名), student ID (学号), and date prefix; use `[待补: ...]` placeholders if missing

### Step 2: Build Document Using Reference Template

Use the reference template as the ZIP base. Key principles:

**Heading paragraphs** (一级标题 like "一、XXX"):
```xml
<w:p>
  <w:pPr><w:pStyle w:val="1"/><w:spacing w:after="156"/></w:pPr>
  <w:r><w:t xml:space="preserve">一、菜单案</w:t></w:r>
</w:p>
```
- Use pStyle="1" for 一级标题, pStyle="2" for 二级标题
- Run does NOT need rPr — style provides sz=28/24 and bold
- IMPORTANT: Remove numPr from styles 1, 2, 3 in styles.xml if using manual heading numbers (not auto-numbering)

**Body paragraphs** (正文):
```xml
<w:p>
  <w:pPr><w:spacing w:line="300" w:lineRule="auto" w:after="156"/>
    <w:ind w:firstLine="420"/><w:jc w:val="both"/></w:pPr>
  <w:r><w:rPr><w:rFonts w:hint="eastAsia"/></w:rPr>
    <w:t xml:space="preserve">正文内容...</w:t>
  </w:r>
</w:p>
```
- NO pStyle (inherits Normal/a: sz=21, line=300)
- Run rPr: only `<w:rFonts w:hint="eastAsia"/>` — NO explicit sz
- Bold body runs: add `<w:b/><w:bCs/>` to rPr
- First-line indent: 420 twips (≈2 chars)
- Paragraph after: use 156 twips for generated homework body paragraphs. Although Normal style may show `after=50`, the course reference template's actual filled body paragraphs use `after=156`, and this is the safer value for submitted homework.
- Alignment: set `<w:jc w:val="both"/>` explicitly to avoid Word/WPS drift.

**Document title** (split into multiple runs, hyphen in 宋体 font):
```xml
<w:p>
  <w:pPr>
    <w:spacing w:after="156"/>
    <w:ind w:firstLineChars="0" w:firstLine="0"/>
    <w:jc w:val="center"/>
    <w:rPr><w:sz w:val="30"/><w:szCs w:val="30"/></w:rPr>
  </w:pPr>
  <!-- 文字 run：hint eastAsia -->
  <w:r><w:rPr><w:rFonts w:hint="eastAsia"/><w:sz w:val="30"/>
    <w:szCs w:val="30"/><w:b/><w:bCs/></w:rPr>
    <w:t xml:space="preserve">0421 graded homework 4</w:t></w:r>
  <!-- 连字符 run：显式 宋体 -->
  <w:r><w:rPr><w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:cs="宋体"
    w:hint="eastAsia"/><w:sz w:val="30"/><w:szCs w:val="30"/>
    <w:b/><w:bCs/></w:rPr>
    <w:t xml:space="preserve">-</w:t></w:r>
  <!-- 姓名 run -->
  <w:r><w:rPr><w:rFonts w:hint="eastAsia"/><w:sz w:val="30"/>
    <w:szCs w:val="30"/><w:b/><w:bCs/></w:rPr>
    <w:t xml:space="preserve">[待补: 姓名]</w:t></w:r>
  <!-- 连字符 run -->
  <w:r><w:rPr><w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:cs="宋体"
    w:hint="eastAsia"/><w:sz w:val="30"/><w:szCs w:val="30"/>
    <w:b/><w:bCs/></w:rPr>
    <w:t xml:space="preserve">-</w:t></w:r>
  <!-- 学号 run -->
  <w:r><w:rPr><w:rFonts w:hint="eastAsia"/><w:sz w:val="30"/>
    <w:szCs w:val="30"/><w:b/><w:bCs/></w:rPr>
    <w:t xml:space="preserve">[待补: 学号]</w:t></w:r>
</w:p>
```
- NO pStyle, centered, sz=30 (小三号/15pt), bold
- Date prefix: follow the user's course requirement. If the course uses month+day, use e.g. "0421", not year+month+day.
- Date prefix may be the assignment release date, due date, or another course-specific value; ask the user instead of guessing.
- **IMPORTANT**: Hyphen "-" must be in its own run with explicit 宋体 font (ascii/hAnsi/cs all set to "宋体")
- **IMPORTANT**: pPr must include `<w:ind w:firstLineChars="0" w:firstLine="0"/>` and `<w:rPr>` block
- Title is split into 5 runs: date+text, hyphen, name, hyphen, student ID

**Footnote references** (in body text):
```xml
<w:r>
  <w:rPr><w:rStyle w:val="ab"/></w:rPr>
  <w:footnoteReference w:id="4"/>
</w:r>
```
- Use character style rStyle="ab" (superscript, 9pt)
- Each footnoteReference must have a UNIQUE ID
- The course reference template uses separator IDs `-1` and `0`; its sample regular footnote uses ID `1`.
- Starting newly generated footnotes at `4` is a conservative compatibility strategy for programmatic generation/repair, not a template requirement. It avoids collisions with legacy or AI-generated documents that misuse low IDs for separators or ordinary notes.
- If preserving an existing clean template footnote, do not renumber it merely because it is ID `1`; only ensure every `footnoteReference` has a matching `footnote` definition.

**Footnote definitions** (in footnotes.xml):
```xml
<w:footnote w:id="4">
  <w:p>
    <w:pPr>
      <w:pStyle w:val="a7"/>
      <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
      <w:ind w:left="0" w:right="0" w:firstLine="0"/>
      <w:jc w:val="left"/>
    </w:pPr>
    <w:r><w:rPr><w:rStyle w:val="ab"/></w:rPr><w:footnoteRef/></w:r>
    <w:r><w:t xml:space="preserve"> </w:t></w:r>
    <w:r><w:rPr><w:rFonts w:hint="eastAsia"/></w:rPr>
      <w:t xml:space="preserve">《民法典》第X条。</w:t>
    </w:r>
  </w:p>
</w:footnote>
```
- Paragraph style: pStyle="a7" (sz=18/小五号, line=240/单倍)
- footnoteRef: rStyle="ab" (superscript)
- Text runs: only `<w:rFonts w:hint="eastAsia"/>`, sz=18 from a7 style
- Separator: w:id="-1" (separator), w:id="0" (continuationSeparator)
- If footnote text contains Chinese quotation marks, ensure the quote runs are also 小五: `<w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:eastAsia="宋体"/>` plus `<w:sz w:val="18"/>`.
- Nested Chinese quotation marks should be outer double and inner single, e.g. `“违反‘打黑工’禁令的合同”`.

### Step 3: Heading Hierarchy

- **文档主标题**（居中）: follow the user-provided title pattern, e.g. `[date] graded homework [N]-[Name]-[ID]`; use placeholders for missing identity fields
- **一级标题**（左对齐）: `一、XXX`, `二、XXX`, 四号, pStyle="1"
- **二级标题**（左对齐）: `（一）XXX`, `（二）XXX`, 小四号, pStyle="2"
- **三级标题及以下**: 五号, pStyle="3"

### Step 4: Homework Table of Contents (目录)

Use this step when the user asks for `目录`, `TOC`, "做目录", or when the assignment/template clearly expects a directory.

**Core strategy**
- Use the homework template's `TOC10`, `TOC1`, `TOC2`, and `TOC3` styles when they are available.
- Insert a clean ordinary Word TOC complex field: `TOC \o "1-3" \h \z \u`.
- Generate static preview TOC entries from detected headings; Word/WPS can later update page numbers.
- Keep the TOC field clean, but generate static preview entries with `TOC1/TOC2/TOC3` style plus a paragraph-level right-aligned dot-leader tab stop at `w:pos="8296"`. Some templates have `TOC2/TOC3` indentation but no dot-leader tab, which makes preview page numbers appear beside the heading until Word updates the field.
- Preserve untouched DOCX parts byte-for-byte when possible. If the document already has required TOC/heading styles and no `updateFields`, avoid rewriting unrelated parts.
- Do not copy old `PAGEREF _Toc...` preview entries from a template; they may refer to missing bookmarks and produce Word errors.
- Do not set `w:updateFields=true` in `word/settings.xml`; it causes Word to ask whether to update fields.
- Do not copy a whole `w:sdt` content-control TOC wrapper unless you have verified Word opens without repair prompts. A plain TOC field is safer.

**TOC page layout**
- Keep the document title and `目录` on the first page.
- Start the body on the next page by adding `<w:pageBreakBefore/>` to the first body paragraph.
- Avoid inserting a visible page-break run (`<w:br w:type="page"/>`) after the TOC because Quick Look/Word may display a stray square or layout artifact.

**Heading detection and repair**
- TOC levels map to common template styles:
  - `一、...`, `二、...` -> heading style `1` -> `TOC1`
  - `（一）...`, `（二）...` -> heading style `2` -> `TOC2`
  - independent `1. ...`, `2. ...` -> heading style `3` -> `TOC3`
- Do not blindly trust existing Word styles. Users often hand-format headings, and converted documents may misuse styles.
- Use a double check:
  - If style `1/2/3` and text numbering agree, include it directly.
  - If style is missing but the paragraph is clearly a heading, add the correct heading style before generating TOC.
  - If a paragraph has heading style but text does not look like a heading, do not include it; consider downgrading it to body style.
  - If uncertain, leave it out and report it as "需人工确认标题".
- Only include levels 1-3 by default. Do not include fourth-level or lower material; homework TOCs get too dense quickly.

**Validation**
- Verify exactly one `TOC \o "1-3" \h \z \u` field exists when a TOC is requested.
- Verify `PAGEREF`, `_Toc...` anchors, and missing bookmarks are not present in the generated preview entries.
- Verify generated `w:pPr` child order, especially `w:pStyle` before `w:pageBreakBefore`, and `w:tabs` before `w:spacing`.
- Verify `mc:Ignorable` prefixes are declared and `w:rPr` child order is valid. Running `docx_compat_check.py` is useful; a repaired Word sample should not have undefined-prefix or `rFonts` ordering errors.
- Verify body `footnoteReference` IDs and footnote text payload are unchanged unless the task also asked for footnote work. Byte-for-byte `word/footnotes.xml` equality may change if namespace prefixes are normalized to satisfy Word.
- Open in Word as well as WPS when possible. If Word reports "unreadable content", first check `mc:Ignorable` undefined prefixes, `w:rPr` order, and `w:pPr` child order, then rebuild the TOC as clean plain field paragraphs and remove `updateFields`.

For a deterministic helper, use:

```bash
python3 scripts/add_homework_toc.py input.docx template.docx output.docx
```

### Lessons From the 2026-06-09 TOC Regression Test

A regression test found that an automatically generated static TOC preview could differ from the TOC after Word updated the field: level-2 page numbers appeared immediately after the heading text instead of right-aligned with dot leaders. The cause was that the template's `TOC2/TOC3` styles carried indentation but no right-aligned dot-leader tab. Word adds or normalizes the tab stop when the field is updated, so a static preview must add it explicitly.

Current TOC generation rule:
- Insert one clean `TOC \o "1-3" \h \z \u` field, but do not set `updateFields=true`.
- For every static preview entry, set `TOC1/TOC2/TOC3` style and a paragraph-level right-aligned dot-leader tab stop at `w:pos="8296"`.
- Preserve level indentation: `TOC2` uses `w:left="420"` / `w:leftChars="200"`; `TOC3` uses `w:left="840"` / `w:leftChars="400"`.
- Normalize `w:pPr` child order automatically. Old or generated homework files may have `w:ind` before `w:spacing`; the helper must reorder rather than fail.
- Validation target: generated preview should visually resemble the Word-updated TOC, while real page numbers may still require manual field update in Word.

### Step 5: Legal Citation Format

**脚注必要性原则**：
- 正文已完整引用法条原文 + 脚注无进一步说明 → **不设脚注**（脚注无增量信息）
- 正文仅提法条编号未引原文 → **设脚注，并附法条全文**（这是课程助教明确提示过的点）
- 同一法条多次出现：首次正文未引全文处设脚注（含全文）；后续可不重复设注、重复简称条号，或在确有必要时写 `同前注1` / `同前注〔1〕`
- 直接引用原文：正文加引号，脚注通常不用"参见"
- 概括、转述、借鉴观点：脚注用"参见"
- 法条脚注中若写`第X条规定，...`，必须先判断后文是不是官方原文：原文用`规定：“……”`；概括转述改成`依/根据/参见第X条，可以说明……`，不要把 AI 概括写成疑似法条原文
- 引注标号位置：若引注支持整句，标号置于句末标点之后；若只支持句中某一词组或法条名称，标号紧随该引用对象之后
- 脚注功能分离：不要为了减少脚注数量，把“案例出处”和“法条/司法解释依据”合并进同一个脚注；也不要把两个不同法条的全文塞进同一脚注。一个脚注原则上只服务一个引用点或同一命题下的同类来源。若正文已经概括或直接摘引法条内容，脚注可保留为简洁出处；若正文只写条号而未说明内容，再在脚注补足条文原文。

**First citation**: Full name + abbreviation in footnote
```
《中华人民共和国民法典》（以下简称《民法典》）第142条第1款。
```

**Subsequent citations**: Abbreviation only
```
《民法典》第147条。
```

**Key rules**:
- Do NOT use "前引" or "同上". For repeat citations in this course, use either a repeated abbreviated citation or "同前注X"/"同前注〔X〕" where helpful.
- Use 参见 for indirect citations
- Statute numbers: Arabic numerals (第142条, not 第一百四十二条)
- Case citations: full name on first use, full footnote format
- 司法解释: single书名号 〈〉 inside double for nested references

### Step 6: Verify Formatting

Checklist:
1. Title format: correct user-confirmed date prefix, name, student ID or explicit placeholders, centered, sz=30
2. All headings left-aligned, bold, correct sz (28/24)
3. Body text: sz=21 (五号), firstLine indent, line=300 (1.25倍)
4. Body paragraphs: spacing after=156 twips, justified
5. Footnotes: sz=18 (小五号), single spacing, left aligned, no first-line indent, no before/after spacing, rStyle="ab" for markers
6. Footnote quote runs: all `“”‘’` in footnotes are 宋体 and sz=18
7. All footnote IDs unique; template-style regular ID `1` is valid, while generated replacement notes may safely start at `4`
8. Heading styles do not auto-number if headings are manually numbered
9. TOC requested: clean `TOC \o "1-3" \h \z \u` field, right-aligned dot leaders on preview entries, no stale `PAGEREF _Toc...` references
10. Citation placement: no adjacent footnote references at the same sentence-final position; same-claim multiple sources are bundled with semicolons
11. Footnote text payloads: no leading/trailing whitespace beyond the normal delimiter after the footnote number
12. Page numbers: bottom center when required by assignment length
13. Open in both WPS and Word to verify

## Important Notes

1. **Use a reference template as base when provided**: do not assume any private course template exists.
2. **Do NOT use pStyle="1" from old assignment templates**: old templates may have different style sizes (sz=44 instead of sz=28)
3. **Body runs inherit font size from Normal**: don't set sz=21 explicitly on every body run
4. **Heading runs inherit everything from style**: don't set rPr on heading runs
5. **rStyle for footnote reference is "ab"**: not "17" (old template) or "aa" (Hyperlink)
6. **Each footnoteReference needs a unique ID**: Word renders only the first occurrence of each ID
7. **Template footnote IDs are -1/0/1**: separators are `-1` and `0`; ID `1` is a valid regular footnote in the course template
8. **Use ID 4+ only as a safe generation convention**: helpful when replacing all notes or repairing documents created by other tools, but not required by OOXML or the course template
9. **Remove numPr from heading styles if using manual heading numbers**: otherwise auto-numbering conflicts
10. **Remove each-page footnote restart**: the course template may contain `<w:numRestart w:val="eachPage"/>`; delete it for continuous homework footnotes
11. **TOC static preview is not the authority for final page numbers**: generate a clean preview with dot leaders, then let Word update the field for final pagination
12. **Run the compatibility check after footnotes**: `docx_compat_check.py` warns about adjacent footnote references and footnote text that starts with an extra blank
13. **Verify in both WPS and Word**: these applications handle certain features differently

## Bundled Resources

### Scripts
- `scripts/add_footnotes.py`: Footnote automation utilities
- `scripts/add_homework_toc.py`: add or rebuild a clean Word-compatible homework TOC with right-aligned dot leaders
- `scripts/fix_pandoc_heading_artifacts.py`: remove Pandoc/Word `Heading1`/`Heading2`/`Title` styles, theme colors, highlighting, shading, and auto-numbering from homework titles/headings
- `scripts/docx_compat_check.py`: final Word/WPS compatibility check, including stale namespace and Pandoc heading-style warnings

### References
- `references/format_requirements.md`: Comprehensive formatting requirements
