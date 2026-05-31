# Optional Reference Data

This public package is designed around 《法学引注手册（第二版）》 / Law Journal Citation Handbook, Second Edition. The original local filename used by the full workflow is:

```text
assets/Law_Journal_Citation_Handbook_2025.pdf
```

The public package intentionally does not redistribute third-party handbook PDFs, OCR text, or full derived rule indexes. Obtain the same edition from a lawful source such as course materials, a library database, a publisher/journal page, or a file provided by your teacher.

If your copy is an image-only scanned PDF, first convert it to a searchable PDF with WPS, Adobe Acrobat, or another OCR tool. Feeding a searchable PDF to the agent is usually cheaper in tokens and less error-prone than asking the agent to OCR the entire scanned book directly.

For full coverage, place legally obtained local files here:

```text
assets/Law_Journal_Citation_Handbook_2025.pdf
references/handbook_raw.md
references/citation_handbook_structured.md
references/handbook_rule_index.json
references/handbook_rule_index.md
references/citation_rules.json
```

Recommended automatic workflow:

```bash
python3 scripts/build_reference_data.py
```

Run that command from `skills/legal-citation-comprehensive`. From the repository root, use:

```bash
python3 skills/legal-citation-comprehensive/scripts/build_reference_data.py
```

The builder checks whether the PDF is searchable, extracts `handbook_raw.md`,
builds the 1-150 rule index, writes the readable Markdown index and basic
`citation_rules.json`, then runs the audit and self-test. It refuses to
overwrite existing local reference files unless you pass `--force`.

If automatic extraction is incomplete, print the strict AI repair contract:

```bash
python3 scripts/build_reference_data.py --print-ai-contract
```

Manual conversion workflow:

1. Confirm the handbook PDF is searchable. If it is image-only, OCR it into a searchable PDF first.
2. Extract the searchable PDF into `references/handbook_raw.md`.
3. Extract Rules 1-150 into `references/handbook_rule_index.json`.
4. Create a readable copy at `references/handbook_rule_index.md`.
5. Create `references/citation_rules.json` for fast diagnosis and formatting.
6. Mark unclear OCR passages as `[待核: OCR]` instead of guessing.

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
python3 scripts/audit_reference_data.py
python3 scripts/handbook_lookup.py --rule 1
python3 scripts/self_test.py
```

Without those files, the skill can still diagnose citation type, identify missing elements, and produce placeholder-safe guidance, but exhaustive handbook verification is unavailable.

For a friend/classroom local setup handout, see:

```text
docs/法学引注手册本地配置说明.md
```
