---
name: legal-toa-formatter
description: 格式化法律文书中 Table of Authorities (TOA) 条目的点号填充对齐。当用户需要修改TOA条目格式、统一条目样式（Cases/Statutes/Other Authorities）、将所有条目修改为与第一行相同格式时触发。关键词：TOA、Table of Authorities、点号对齐、法律文书格式、证据目录格式。
---

# Legal TOA Formatter

## Overview

规范化法律文书中 Table of Authorities (TOA) 的条目格式。核心功能：将所有TOA条目统一修改为与参考条目相同的点号填充（dot leader）对齐格式，确保引用名称与页码之间的视觉一致性。

## When to Use

- 用户要求修改 TOA/Table of Authorities 条目格式
- 条目需要点号填充对齐（dot leader alignment）
- 需要统一多个 TOA 条目的样式
- 触发词：TOA、Table of Authorities、法律文书格式修改、点号对齐

## Core Concept

**关键理解**：Word 的制表符对齐使用 `w:leader="dot"` 属性，让 Word 自动填充点号，**不是**在文本中手动添加点号字符。

## Workflow

### Step 1: 分析源文档

1. 解包 docx 文件：
   ```bash
   unzip -o input.docx -d temp_unpacked
   ```

2. 找到 TOA 所在 section（通常在 `word/document.xml 的 TOX（Table of Start）` 字段中）

3. 定位 TOA 条目：搜索 `<w:p>` 段落中包含制表符 `<w:tab/>` 的条目

### Step 2: 分析参考格式

找到第一个正确格式的条目（通常是 TOA 标题后的第一条），分析其 XML 结构：

```xml
<w:p>
  <w:pPr>
    <w:widowControl w:val="0"/>
    <w:tabs>
      <w:tab w:val="right" w:leader="dot" w:pos="9016"/>
    </w:tabs>
    <w:spacing w:line="480" w:lineRule="auto"/>
    <w:jc w:val="both"/>
    <w:rPr>
      <w:rFonts w:hint="default" w:ascii="Times New Roman Regular" .../>
      <w:kern w:val="2"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
      <w:lang w:val="en-US" w:eastAsia="zh-CN" w:bidi="ar-SA"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:t>, 486 U.S. 531 (1988)</w:t>
  </w:r>
  <w:r>
    <w:tab/>
  </w:r>
  <w:r>
    <w:t>4, 5, 6, 7</w:t>
  </w:r>
</w:p>
```

**关键元素**：
- `<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9016"/></w:tabs>` - 定义右对齐点号填充制表位
- `<w:tab/>` - 在文本中插入制表符位置
- 制表位位置 `pos="9016"` 是 twips 单位（1/20 点）

### Step 3: 修改目标条目

对于每个需要修改的条目：

1. 确保 `<w:pPr>` 包含正确的 `<w:tabs>` 定义
2. 如果条目有 `<w:tabs>` 但 leader 不是 "dot"，修改为 `w:leader="dot"`
3. 如果条目完全没有 `<w:tabs>`，在 `<w:pPr>` 中的适当位置添加：
   ```xml
   <w:tabs>
     <w:tab w:val="right" w:leader="dot" w:pos="9016"/>
   </w:tabs>
   ```

4. 在引用名称与页码之间插入 `<w:tab/>` 元素

### Step 4: 重新打包

```bash
cd temp_unpacked && zip -r ../output.docx . -x "*.DS_Store"
```

## Quick Fix Script

对于批量处理，使用 `scripts/fix_toa_format.py`：

```bash
python3 scripts/fix_toa_format.py input.docx output.docx
```

脚本会自动：
1. 解包 docx
2. 定位 TOA 条目
3. 应用一致的点号填充格式
4. 重新打包

## Common Patterns

### Pattern 1: 条目完全没有制表符

**症状**：引用名称和页码直接相连，无分隔

**修复**：在 `<w:pPr>` 中添加 `<w:tabs>`，在合适位置添加 `<w:tab/>`

### Pattern 2: 条目有制表符但无点号

**症状**：有空隙但没有点号填充

**原因**：缺少 `<w:tabs>` 定义，或 `w:leader` 不是 "dot"

**修复**：添加/修正 `<w:tabs>` 为 `w:leader="dot"`

### Pattern 3: 制表位位置不一致

**症状**：有的条目对齐，有的不对齐

**修复**：统一使用 `w:pos="9016"`（或根据页面宽度调整）

## Troubleshooting

**Q: 点号没有显示？**
A: 检查 `<w:pPr>` 是否有 `<w:tabs><w:tab w:leader="dot".../></w:tabs>`，确保段落引用了正确的制表位

**Q: 对齐位置不对？**
A: 调整 `w:pos` 值。常见值：
- 9016 twips ≈ 6.5 英寸（右边界）
- 9372 twips ≈ 6.5 英寸 + 0.25 英寸边距

**Q: 部分条目格式正确，部分不对？**
A: 说明这些条目缺少 `<w:pPr>` 中的 `<w:tabs>` 定义，逐个添加即可
