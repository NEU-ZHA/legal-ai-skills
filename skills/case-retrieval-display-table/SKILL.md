---
name: case-retrieval-display-table
description: Create or update a legal-team-facing horizontal Word case retrieval table for Chinese litigation research. Use when turning retrieved judgments, rulings, typical cases, or duplicate records into one landscape case card per record, especially when the output needs fields for case title hyperlink, classification, court, number/date/procedure, key expressions, core facts/issues, court findings, and disposition.
---

# 类案检索展示表

将检索到的每一条题录整理为横向案例卡片，并生成可直接给法律团队阅览的 `.docx` 明细表。公开版使用 `[律所名称]` 等占位符，不写入任何真实律所名称、客户名称或项目名称。

## 工作流程

1. 先逐案读取可获得的裁判全文、典型案例材料或数据库题录；仅将材料能够支持的内容写入“核心事实／争点”“法院认定”和“裁判结果”。
2. 先给每案标明检索分类：`实体判决`、`程序／关联裁定`、`重复题录`或`典型案例`。不要将程序裁定或同案重复题录写成实体裁判规则。
3. 按 [references/case-schema.md](references/case-schema.md) 组织 JSON；案件名称本身带原文超链接，不另设“法宝链接”行。
4. 运行 `scripts/build_case_display_table.js` 生成横向 A4 文档；无输入数据时，该脚本生成一张可复制的空白案例卡片。
5. 用 `unzip -t` 验证输出文件；必要时转为 PDF 并逐页检查表格是否越界、标题是否孤立在页尾，以及超链接是否保留。

## 生成命令

```bash
node scripts/build_case_display_table.js \
  --input cases.json \
  --output "case-retrieval-display-table.docx" \
  --title "[律所名称]｜类案检索案例展示表"
```

生成空白模板时省略 `--input`：

```bash
node scripts/build_case_display_table.js \
  --output "case-retrieval-display-template.docx" \
  --title "[律所名称]｜类案检索案例展示模板"
```

如果当前运行时没有 `docx` 依赖，请先在本 skill 目录安装：

```bash
npm install
```

## 输出规则

- 每案一张横向案例卡片；表头显示“案例 序号｜检索分类”。
- 案件名称是唯一原文链接入口；链接文本应为案名，不要追加“北大法宝链接”等冗余行。
- “关键表述／关键词”只摘录与检索主题、裁判判断或争点识别有关的原文短语；没有则写“公开材料未载明”或“未见与本案认定相关的关键词”。
- “法院认定”应压缩“本院认为”的判断路径；“裁判结果”应写明维持、改判、驳回或准许等主文结果。
- 对全文未公开、材料不全或仅见典型案例摘要的记录，明确写“公开材料未载明”，不得补造案号、日期、事实或裁判理由。
- 除表内案情内容外，不写“本案／我方案／建议继续关注”等检索报告式语言。
