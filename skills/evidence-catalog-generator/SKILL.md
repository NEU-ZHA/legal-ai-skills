---
name: evidence-catalog-generator
description: Organize user-provided evidence materials into evidence catalog entries and fill them into a user-provided or generic DOCX template. The public version contains no real case template, parties, docket numbers, facts, amounts, addresses, or local file paths.
---

# Evidence Catalog Generator / 证据目录生成器

根据用户提供的证据材料、材料清单或已整理条目，先整理成证据目录条目，再填入用户提供的 `.docx` 模板；没有模板时，生成一个通用证据目录 Word 文档。公开版只保留通用结构和脚本，不随仓库分发真实案件模板或真实示例数据。

Organize user-provided evidence materials or item lists into catalog entries, then fill them into a user-provided `.docx` template. If no template is provided, generate a generic evidence catalog DOCX. The public version contains only generic workflow and code, with no real case template or real sample facts.

## Use When / 适用场景

- 用户有一组证据材料、文件名、材料清单或证据条目，需要整理为 Word 证据目录。
- 用户提供了机构、课程、法院或团队自己的 `.docx` 模板。
- 用户没有模板，但接受生成一个通用占位版证据目录。
- 需要把 CSV、JSON 或 XLSX 中的证据条目批量写入表格。

Use when the user has evidence materials or item lists and wants them organized into a DOCX evidence catalog, either with their own template or with a generic placeholder document.

## Privacy Rules / 隐私规则

- 不得使用维护者本地模板、真实案件模板或历史示例作为默认模板。
- 不得写死真实姓名、案号、项目名、地址、金额、账号、本机路径、公司名称或其他案卷指纹。
- 示例只能使用明显占位符，例如 `[证据名称]`、`[证据来源]`、`[证明事项]`、`[页码]`。
- 如果用户未提供字段，保留 `[待补: 字段名]`，不要猜测。
- 生成前提醒用户检查其模板 metadata，避免把真实作者、单位、修订记录或自定义属性带入公开文件。

## Required Inputs / 必要输入

1. 用户提供的证据材料、文件名列表、材料说明，或已整理的 CSV、JSON、XLSX 条目表。
2. 输出 `.docx` 路径。
3. 可选：用户自己的 `.docx` 证据目录模板。
4. 可选：标题、案件名称、案号、提交主体、提交日期。

## Data Schema / 数据结构

整理后的每条证据建议包含这些字段：

| Field | 中文字段 | Required | Placeholder if missing |
| --- | --- | --- | --- |
| `number` | `编号` | no | 自动连续编号 |
| `name` | `证据名称` | yes | `[待补: 证据名称]` |
| `source` | `证据来源` | no | `[待补: 证据来源]` |
| `purpose` | `证明事项` / `证明目的` | yes | `[待补: 证明事项]` |
| `pages` | `页码` / `页数` | no | `[待补: 页码]` |

See `references/data_schema.md` for the full mapping.

## Workflow / 工作流程

1. 检查用户提供的材料和模板，不复用本地私有模板。
2. 将材料整理为证据条目：编号、证据名称、证据来源、证明事项、页码。
3. 对缺失信息使用 `[待补: 字段名]`，不替用户猜事实。
4. 如果提供模板，替换模板中的占位符并写入第一张证据目录表。
5. 如果没有模板，生成一个纯占位的通用证据目录。
6. 输出后给用户一份检查清单：缺失字段、模板 metadata、页码、表格行数。

## Script Usage / 脚本用法

```bash
python3 scripts/generate_catalog.py \
  --input path/to/evidence_items.csv \
  --output path/to/evidence_catalog.docx \
  --title "证据目录" \
  --case-name "[案件名称]" \
  --docket-number "[案号]" \
  --submitter "[提交主体]" \
  --submit-date "[提交日期]"
```

使用用户模板：

```bash
python3 scripts/generate_catalog.py \
  --input path/to/evidence_items.json \
  --template path/to/user-template.docx \
  --output path/to/evidence_catalog.docx
```

The script requires `python-docx`. XLSX input additionally requires `openpyxl`.

## File Structure / 文件结构

```text
evidence-catalog-generator/
├── SKILL.md
├── references/
│   └── data_schema.md
└── scripts/
    └── generate_catalog.py
```
