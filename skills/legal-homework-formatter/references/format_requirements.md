# 中国法学作业格式要求

Public-release privacy rule: never default to a real maintainer name, student ID, school, course file, or local path. Ask the user for identity fields. If an identity field is missing, use an explicit placeholder such as `[待补: 姓名]` or `[待补: 学号]`.

## 一、标题格式

### 1.1 文件命名格式
```
[日期前缀] graded homework [作业序号]-[姓名或待补占位符]-[学号或待补占位符].docx
```

**示例：**
- `0310 graded homework 1-[待补: 姓名]-[待补: 学号].docx`
- `0421 graded homework 4-Li Ming-2026000000.docx`

**注意事项：**
- 日期前缀格式：**月份+日期**（如 `0421`），**不是**年月日（如 `260421`）
- 日期前缀是否为提交日期、发布日期或课程指定日期，应向用户确认
- 日期前缀通常来源于作业要求文档的命名或课程说明
- 作业序号使用阿拉伯数字

### 1.2 文档标题格式
- **格式：** 与文件名相同 ("三名同一"原则)
- **字体：** 宋体 + Times New Roman
- **字号：** 小三号（15pt / sz=30半磅）
- **对齐：** 居中
- **加粗：** 是
- **OOXML 标题段落结构：**
  - 无 pStyle
  - pPr 必须包含：`<w:spacing w:after="156"/>`, `<w:ind w:firstLineChars="0" w:firstLine="0"/>`, `<w:jc w:val="center"/>`
  - pPr 内必须含 `<w:rPr><w:sz w:val="30"/><w:szCs w:val="30"/></w:rPr>`
  - **标题须拆分为 5 个独立的 run**（对齐参考模板）：
    1. 日期+文字部分（如 `0421 graded homework 4`）→ `hint="eastAsia"`, sz=30, bold
    2. 连字符 `-` → **显式 宋体**：`ascii="宋体" hAnsi="宋体" cs="宋体" hint="eastAsia"`, sz=30, bold
    3. 姓名 → `hint="eastAsia"`, sz=30, bold
    4. 连字符 `-` → 同 run 2（显式 宋体）
    5. 学号 → `hint="eastAsia"`, sz=30, bold
  - 连字符 run 的 rFonts 必须显式设置 ascii/hAnsi/cs 均为 `"宋体"`，确保在 WPS 和 Word 中均以宋体显示

### 1.3 标题层级 (严格执行)

| 级别 | 格式 | 字号 | sz (半磅) | pStyle | 对齐 |
|------|------|------|----------|--------|------|
| 文档主标题 | 用户确认的标题格式；身份信息缺失时用 `[待补: ...]` | 小三号/15pt | 30 | 无 | 居中 |
| 一级标题 | `一、XXX` | 四号/14pt | 28 | `1` (heading 1) | 左对齐 |
| 二级标题 | `（一）XXX` | 小四号/12pt | 24 | `2` (heading 2) | 左对齐 |
| 三级标题 | `1. XXX` | 五号/10.5pt | 21 | `3` (heading 3) | 左对齐 |

**⚠️ 只有文档主标题才居中，所有章节标题一律左对齐。**

---

## 二、正文格式

### 2.1 字体与字号
- **中文字体：** 宋体 (SimSun)
- **英文字体：** Times New Roman
- **字号：** 五号（10.5pt, sz=21半磅）
- **OOXML 正文 run:** `<w:rPr><w:rFonts w:hint="eastAsia"/></w:rPr>` (sz 由 Normal 样式继承)

### 2.2 段落格式
- **行距：** 1.25倍行距 (line=300, Normal 样式默认)
- **首行缩进：** 2字符 (firstLine=420 twips)
- **段后距：** 156 twips（生成提交稿时显式设置；虽然 Normal 样式可见 after=50，但参考模板的实际正文段落实例使用 after=156）
- **对齐：** 两端对齐 (both, Normal 样式默认)

### 2.3 样式引用 (OOXML)
- **正文段落：** 不设 pStyle (自动继承 Normal/`a`)
- **基于用户提供的课程参考模板**
- **Normal (styleId="a"):** sz=21, line=300, after=50 (afterLines=50), firstLine=200 (firstLineChars=200)
  - 其他属性：`widowControl=0`, `adjustRightInd=0`, `snapToGrid=0`
  - jc=both (两端对齐)
  - rPr: `kern=2`, `sz=21`, `szCs=21`
- **Normal 样式不含 rFonts 定义** — 字体颜色等继承自 docDefaults theme fonts
- **正文段落实例**：在 Normal 样式基础上，显式设置 `<w:spacing w:line="300" w:lineRule="auto" w:after="156"/>`、`<w:ind w:firstLine="420"/>`（约2字符）和 `<w:jc w:val="both"/>`

---

## 三、脚注格式

### 3.1 样式定义 (基于参考模板)

| 元素 | OOXML 样式 | 字号 |
|------|-----------|------|
| 脚注引用标记 (正文中) | rStyle="ab" (character style) | 9pt, 上标 |
| 脚注段落 | pStyle="a7" (paragraph style) | 小五号/9pt |
| 脚注文本 run | `<w:rFonts w:hint="eastAsia"/>` | sz 从 a7 继承 (18半磅) |
| 脚注行距 | - | 单倍 (line=240) |

**课程助教批注口径：** 脚注小五，左对齐，段前后距0行，单倍行距，首行不缩进；脚注中的数字使用 Times New Roman，中文使用宋体。

### 3.2 脚注编号
- 使用阿拉伯数字：1、2、3...
- 编号位于右上角，作为上标
- **⚠️ rStyle 必须为 `"ab"` (footnote reference)**，不能为 `"aa"` (Hyperlink)
- **每个 footnoteReference 必须使用唯一 ID**
- 参考模板的分隔符 ID 为 `-1` (separator) 和 `0` (continuationSeparator)
- 参考模板可能含有 `<w:numRestart w:val="eachPage"/>`，这会导致脚注每页重新从1编号；正式作业通常应删除该设置，保持全文连续编号
- 参考模板中的示例普通脚注 ID 为 `1`；因此普通脚注 ID `1` 本身是合法的
- 自动生成或修复混乱文档时，可以让新增/替换的普通脚注从 `4` 开始。这是兼容性补丁，不是模板硬性要求；好处是避开旧脚本或其他 AI 生成器可能误用的低 ID 区间

### 3.3 脚注 XML 结构
```xml
<w:footnote w:id="4">
  <w:p>
    <w:pPr><w:pStyle w:val="a7"/></w:pPr>
    <w:r><w:rPr><w:rStyle w:val="ab"/></w:rPr><w:footnoteRef/></w:r>
    <w:r><w:t xml:space="preserve"> </w:t></w:r>
    <w:r><w:rPr><w:rFonts w:hint="eastAsia"/></w:rPr>
      <w:t xml:space="preserve">脚注文本内容。</w:t>
    </w:r>
  </w:p>
</w:footnote>
```

### 3.4 脚注引号与字号

- 脚注中的中文引号必须使用弯引号：外层 `“”`，内层 `‘’`。
- 例：`参见《德国民法总则编典型判例17则评析》判例十三“违反‘打黑工’禁令的合同”，《联邦最高法院民事裁判集》第89卷，第369页以下。`
- 如果引号规范化工具把引号拆成独立 run，必须检查这些 run 是否仍为脚注字号：`w:sz="18"`、`w:szCs="18"`。
- 脚注中的独立引号 run 推荐显式设置：`w:ascii="宋体" w:hAnsi="宋体" w:eastAsia="宋体"`，防止 Word/WPS 将其渲染成英文字体或正文字号。

### 3.5 脚注分隔符
```xml
<w:footnote w:type="separator" w:id="-1">
  <w:p><w:pPr><w:spacing w:after="120"/><w:ind w:firstLine="420"/></w:pPr>
    <w:r><w:separator/></w:r></w:p>
</w:footnote>
<w:footnote w:type="continuationSeparator" w:id="0">
  <w:p><w:pPr><w:spacing w:after="120"/><w:ind w:firstLine="420"/></w:pPr>
    <w:r><w:continuationSeparator/></w:r></w:p>
</w:footnote>
```

---

## 四、法律文件引用格式

### 4.1 第一次引用法律文件
**格式：** 使用全称，括注简称

**示例：**
```
《中华人民共和国民法典》（以下简称《民法典》）第142条第1款。
《最高人民法院关于适用〈中华人民共和国民法典〉总则编若干问题的解释》（以下简称《民法典总则编司法解释》）第19条。
```

### 4.2 后续引用法律文件
**格式：** 直接使用简称

### 4.3 引用具体条文
- 条文序数使用阿拉伯数字
- 款项序数也使用阿拉伯数字
- 正文直接引用法条原文时用引号，脚注不加"参见"
- 正文概括、转述或借鉴观点时，脚注加"参见"
- 正文仅出现法条编号而未列明法条内容时，应在脚注中列明法条全文，例如：`《中华人民共和国民法典》第153条：“……”`
- 引用条文应尽量精确到条、款、项、句

### 4.4 重复引用同一法条
- ❌ 不写"前引"或"同上"
- ✅ 可直接重复简称法条信息，例如：`《民法典》第153条第1款。`
- ✅ 若课程作业脚注已经首次完整列明法条全文，后续可写：`同前注1。`或`同前注〔1〕。`
- ✅ 如果后文只是一般论述且正文已足够清楚，也可以不重复设脚注

---

## 五、页面设置

### 5.1 纸张大小
- A4纸张 (w=11906, h=16838 twips)

### 5.2 页边距
- 上：1440 twips (1 inch / 2.54cm)
- 下：1440 twips (1 inch / 2.54cm)
- 左：1800 twips (1.25 inch)
- 右：1800 twips (1.25 inch)

### 5.3 页码
- 位置：页面底端居中
- 格式：阿拉伯数字

---

## 六、常见问题

### 6.1 全文显示二号字
**原因：** 正文段落使用了 `pStyle="1"`，但旧模板中 styleId="1" 是 heading 1 (sz=44/二号)

**解决：** 
- 使用用户提供的参考模板作为基础，并以实际 `styles.xml` 为准
- 正文不设 pStyle，由 Normal (styleId="a", sz=21) 继承
- 正文 run 不设 sz，从段落样式自然继承

### 6.2 脚注编号过大/不是上标
**原因：** footnoteReference 的 rStyle 被错误设为 "aa" (Hyperlink) 或 "17" (旧模板)

**解决：** 使用参考模板的 rStyle="ab" (footnote reference character style)

### 6.3 WPS和Word显示脚注不一致
**原因：** 脚注引用 ID 与 `footnotes.xml` 定义不匹配，或其他生成器把分隔符/普通脚注放进互相冲突的低 ID 区间

**解决：**
- 清洁模板结构应为：分隔符 `-1/0`，普通脚注可从 `1` 开始
- 若是自动生成、批量替换或修复来源不明的 docx，普通脚注可从 `4` 开始作为保守兼容策略
- 最终必须检查：`document.xml` 中每个 `footnoteReference w:id="X"` 都在 `footnotes.xml` 中有对应 `<w:footnote w:id="X">`

### 6.4 章节标题自动添加编号
**原因：** heading 样式 (1, 2, 3) 自带 numPr (自动编号)

**解决：** 如需手动编写标题文字（如"一、菜单案"），从 styles.xml 中移除 heading 样式的 numPr

### 6.4.1 标题出现"一、一、"重复编号
**原因：** 同时使用手写中文编号和模板 heading 自动编号

**解决：**
- 作业正文通常保留手写标题编号（便于纯文本和批注识别）
- 在生成最终 docx 时移除 styles.xml 中 heading 1/2/3 的 `<w:numPr>`，保留字号、加粗等其他样式属性

### 6.5 Pandoc 转写后标题变蓝/变绿
**原因：** Markdown/Pandoc 转 DOCX 时常把标题段落写成 Word 内置 `Heading1`、`Heading2` 或 `Title`，并通过主题色、highlight、shading 或自动编号继承视觉样式。之后即使直接改字号，Word 仍可能按内置标题样式显示为蓝色、绿色或带项目符号。

**解决：**
- 最终生成前运行 `scripts/fix_pandoc_heading_artifacts.py`；
- 清除标题段落的 `Heading1`/`Heading2`/`Title` 样式和 `<w:numPr>`；
- 清除标题 run 的 `<w:color>`、`w:themeColor`、`<w:highlight>`、`<w:shd>`；
- 直接写入黑色 `<w:color w:val="000000"/>`，并按标题层级设置字号和加粗；
- 最后运行 `scripts/docx_compat_check.py`，若仍提示 Pandoc/Word heading styles，继续清理后再交付。

### 6.6 中文字体不显示为宋体
**原因：** 未正确设置 docDefaults 的 eastAsia theme font，或 run rPr 覆盖了字体

**解决：** 
- docDefaults 应设置 eastAsiaTheme="minorEastAsia"
- 参考模板的 theme 文件定义了 minorEastAsia = 宋体
- 正文 run 仅设 `<w:rFonts w:hint="eastAsia"/>` 触发 East Asian font

### 6.7 脚注引号变成正文字号
**原因：** 引号规范化脚本可能把 `“”‘’` 拆成独立 run，并继承正文五号或其他默认字号

**解决：**
- 对 `word/footnotes.xml` 中所有文本为 `“`、`”`、`‘`、`’` 的 run，显式设置 `w:sz=18`、`w:szCs=18`
- 同时设置 `w:rFonts` 的 `ascii/hAnsi/eastAsia` 为宋体
- 修正后再用 `unzip -t` 校验 docx 完整性，并检查 `footnoteReference` 是否仍存在
- 同时检查 `word/document.xml` 和 `word/settings.xml` 中不得残留 `<w:numRestart w:val="eachPage"/>`，否则脚注会每页重新编号

---

## 七、参考资料

### 7.1 核心参考模板
用户提供的课程参考模板 — 课程特定格式的权威来源。公开仓库不随附私人课程模板。

### 7.2 关键标准
- 《法学引注手册》
- 用户提供的课程 PPT 或作业格式说明
