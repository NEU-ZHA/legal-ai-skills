# Evidence Catalog Data Schema / 证据目录数据结构

公开版只使用通用字段，不包含任何真实案件、案由、交易、金额或案号示例。真实使用时，先把用户提供的证据材料、文件名或材料说明整理成下列条目结构，再填入模板。

The public version uses only generic fields and contains no real case facts, transaction amounts, or docket examples. In real use, first organize the user's evidence materials, filenames, or descriptions into the item structure below, then fill the template.

## Supported Input Formats

- CSV: first row as headers.
- JSON: an array of objects.
- XLSX: first worksheet, first row as headers. Requires `openpyxl`.

## Canonical Fields

| Canonical field | Accepted headers | Notes |
| --- | --- | --- |
| `number` | `编号`, `序号`, `number`, `no`, `index` | Optional. If blank, generated from `--start-number`. |
| `name` | `证据名称`, `名称`, `name`, `title`, `evidence_name` | Required. Missing value becomes `[待补: 证据名称]`. |
| `source` | `证据来源`, `来源`, `source`, `provider` | Optional. Missing value becomes `[待补: 证据来源]`. |
| `purpose` | `证明事项`, `证明目的`, `purpose`, `fact_to_prove`, `description` | Required. Missing value becomes `[待补: 证明事项]`. |
| `pages` | `页码`, `页数`, `页码范围`, `pages`, `page`, `page_range` | Optional. Missing value becomes `[待补: 页码]`. |

## Placeholder CSV

```csv
编号,证据名称,证据来源,证明事项,页码
1,[证据名称一],[证据来源一],[证明事项一],[页码一]
2,[证据名称二],[证据来源二],[证明事项二],[页码二]
```

## Placeholder JSON

```json
[
  {
    "number": "1",
    "name": "[证据名称一]",
    "source": "[证据来源一]",
    "purpose": "[证明事项一]",
    "pages": "[页码一]"
  },
  {
    "number": "2",
    "name": "[证据名称二]",
    "source": "[证据来源二]",
    "purpose": "[证明事项二]",
    "pages": "[页码二]"
  }
]
```

## Template Placeholders

If a user supplies a DOCX template, the script replaces these placeholders wherever they appear in paragraphs or tables:

| Placeholder | Meaning |
| --- | --- |
| `[标题]` | Catalog title |
| `[案件名称]` | Case or matter name |
| `[案号]` | Docket number or internal matter number |
| `[提交主体]` | Submitting party or team |
| `[提交日期]` | Submission date |

Do not commit a user's filled template back to the public repository.
