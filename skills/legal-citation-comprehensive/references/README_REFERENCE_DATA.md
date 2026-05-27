# Optional Reference Data

This public package is designed around 《法学引注手册（第二版）》 / Law Journal Citation Handbook, Second Edition. The original local filename used by the full workflow is:

```text
assets/Law_Journal_Citation_Handbook_2025.pdf
```

The public package intentionally does not redistribute third-party handbook PDFs, OCR text, or full derived rule indexes. Obtain the same edition from a lawful source such as course materials, a library database, a publisher/journal page, or a file provided by your teacher.

For full coverage, place legally obtained local files here:

```text
assets/Law_Journal_Citation_Handbook_2025.pdf
references/handbook_raw.md
references/citation_handbook_structured.md
references/handbook_rule_index.json
references/handbook_rule_index.md
references/citation_rules.json
```

Recommended conversion workflow:

1. OCR or extract the PDF into `references/handbook_raw.md`.
2. Extract Rules 1-150 into `references/handbook_rule_index.json`.
3. Create a readable copy at `references/handbook_rule_index.md`.
4. Create `references/citation_rules.json` for fast diagnosis and formatting.
5. Mark unclear OCR passages as `[待核: OCR]` instead of guessing.

`handbook_rule_index.json` should use this shape:

```json
{
  "count": 150,
  "missing_rule_numbers": [],
  "rules": [
    {
      "rule_number": 1,
      "title": "[规则标题]",
      "category": "[规则分类]",
      "text": "[规则正文]",
      "raw_start_line": 1,
      "raw_end_line": 10
    }
  ]
}
```

`citation_rules.json` should use this shape:

```json
{
  "types": {
    "chinese_book": {
      "label": "中文著作",
      "required": ["author", "title", "publisher", "year"],
      "optional": ["edition", "page"],
      "template": "{author}：《{title}》，{publisher}{year}年版，{page}。",
      "anchors": ["第X条"],
      "lookup_guidance": {
        "publisher": "查版权页。",
        "year": "查版权页。"
      }
    }
  }
}
```

After adding the files, test with:

```bash
python3 scripts/handbook_lookup.py --rule 1
python3 scripts/self_test.py
```

Without those files, the skill can still diagnose citation type, identify missing elements, and produce placeholder-safe guidance, but exhaustive handbook verification is unavailable.
