---
name: legal-citation-automator
description: 法学脚注 DOCX 执行器。用于把已经由 legal-citation-comprehensive 诊断、补全或确认过的法学引注插入 Word 文档，并进行 Word/WPS 脚注结构兼容性检查。适用于自动添加脚注、批量脚注修复、DOCX footnotes.xml 处理、脚注编号检查、脚注引用标记插入。不要把它当作引注规则大脑；复杂引注规则必须先交给 legal-citation-comprehensive。
---

# Legal Citation Automator

## Role

This skill is the DOCX execution layer. It inserts or repairs footnotes only after citation text has been diagnosed and approved by `legal-citation-comprehensive`.

Do not invent citation content here. Do not rely on this skill to decide legal citation format. Use the comprehensive skill first for source type, missing elements, and final footnote wording.

Weak-agent guardrail: if any required fact is uncertain, stop. Output a repair checklist. Do not edit the DOCX just because the user asked for automation.

## Safe Workflow

1. Run `legal-citation-comprehensive`.
   - Diagnose each messy footnote or citation candidate.
   - Search the full handbook index for non-trivial or unusual sources.
   - Produce either final citation text or a `[待补]` checklist.
2. Prepare a citation insertion plan.
   - Each item must include the exact body text anchor or paragraph/run location.
   - Each item must include final footnote text.
   - If source facts are missing, stop and return a report instead of editing the DOCX.
3. Insert footnotes using OOXML, preserving the existing document structure.
4. Verify:
   - every `w:footnoteReference` has a matching `w:footnote`;
   - separator IDs remain `-1` and `0`;
   - generated replacement notes may start at `4+` as a conservative repair convention;
   - footnote text style matches the target document/template;
   - DOCX zip, content types, and relationships are valid.

## Input Contract

The safe input to an insertion script is a JSON array:

```json
[
  {
    "anchor_text": "依《民法典》第153条第1款",
    "placement": "after_anchor",
    "footnote_text": "《中华人民共和国民法典》第153条：“……”",
    "source_status": "verified"
  }
]
```

Required fields:

- `anchor_text`: exact text in the body, or an equivalent precise location object.
- `placement`: `after_anchor`, `after_sentence`, or a precise custom instruction.
- `footnote_text`: final text from `legal-citation-comprehensive`.
- `source_status`: must be `verified`; if `needs_user_input`, do not edit.

## When to Refuse Editing

Do not modify the DOCX when:

- the footnote text contains `[待补: ...]`;
- the comprehensive skill has not supplied handbook rule numbers;
- the citation source has not been verified;
- the anchor appears multiple times and the user has not clarified which instance;
- the source is a PDF/book/article but required bibliographic facts are absent;
- the requested citation format conflicts with the handbook and no user override is explicit.

Instead, produce a citation repair report using the comprehensive skill output.

## Scripts

- `scripts/diagnose_with_comprehensive.py`: wrapper that calls the comprehensive skill diagnostic script when available.
- `scripts/add_footnotes.py`: legacy OOXML insertion utility. Use only after reviewing its target-location behavior for the current task.
- `scripts/docx_compat_check.py`: final DOCX compatibility gate.
- `scripts/fix_footnote_conflict.py`: repair mismatched or unsafe footnote IDs.
- `scripts/identify_citations.py`: first-pass candidate detector; always review candidates manually.

## Important DOCX Rules

- The clean template pattern is separator footnotes `-1` and `0`; a regular note ID `1` is valid.
- Starting generated replacement notes at `4+` is a conservative repair convention, not a universal rule.
- Never create a body `footnoteReference` without a matching `footnote` definition.
- Never add footnote definitions without confirming the body reference was actually inserted.
- If multiple anchors match, pause and ask for clarification.
- For Civil Law homework, combine with `legal-homework-formatter` so footnote style remains 小五、左对齐、单倍行距、段前后 0、首行不缩进.

## Relationship to Comprehensive Skill

Use `legal-citation-comprehensive` as the authoritative source for:

- source classification;
- missing element diagnosis;
- full handbook rule lookup;
- standard footnote wording;
- direct/indirect quotation analysis;
- repeat citation forms.

This skill is successful only when the final DOCX structure is valid and the citation content has already been validated.
