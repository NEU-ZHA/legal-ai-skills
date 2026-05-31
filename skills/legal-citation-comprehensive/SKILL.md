---
name: legal-citation-comprehensive
description: 全面法学引注诊断、补全与格式化工具。用于检查混乱脚注、识别缺失要素、说明应去哪里查找缺失信息，并在用户提供来源文件、法条、案例或网页信息时生成符合《法学引注手册（第二版）》的中文/外文法律脚注。适用于法学引注、脚注检查、引注修正、引用格式转换、法律文献引用、法条脚注、案例脚注、论文引注。
---

# Legal Citation Comprehensive

## Role

This skill is the citation brain. It diagnoses and generates citation text. It does not edit Word files directly; use `legal-citation-automator` for DOCX insertion.

Primary rule: never invent missing bibliographic facts. If a required element is absent and cannot be extracted from a provided source, mark it as `[待补: 要素名]` and tell the user where to find it.

Completeness rule: the simplified templates are not the whole handbook. Before giving a final answer for any non-trivial citation, consult a legally obtained copy of the citation handbook or a user-provided rule index. This public repository does not redistribute third-party handbook PDFs or OCR dumps. Use `references/citation_rules.json` only as a fast execution layer when the user or local installation provides it.

Weak-agent guardrail: if you are unsure, do not improvise. Follow `references/operator_guardrails.md` exactly. A citation answer is not complete unless it states the source type, missing elements, lookup path, suggested format, and relevant handbook rule numbers.

## Quick Workflow

1. Classify the citation type.
   - Search the user-provided handbook/rule index for the source category and rule numbers.
   - Use `references/citation_rules.json` for required elements, templates, and handbook anchors when that optional local reference file is available.
   - If the repository lacks full reference data, stop at diagnosis/placeholders and tell the user what source material is needed.
2. Extract existing elements from the messy footnote or supplied source.
3. Diagnose missing required and optional elements.
4. Give source lookup guidance from `references/source_lookup_guide.md`.
5. Generate a standard citation.
   - If complete: output the final footnote.
   - If incomplete: output a placeholder version and a precise checklist.
6. For Chinese Civil Law homework, apply the course-specific statute rule:
   - If正文 only names a statute article, the footnote should include the article text.
   - If正文 already quotes the full article and the footnote adds nothing, omit the footnote.
7. Run `python scripts/self_test.py` after changing this skill or before distributing it. Full handbook coverage tests require locally supplied reference data.

## Deterministic Helper

For a first-pass report, run:

```bash
python scripts/citation_diagnose.py --text "王名扬《美国行政法》第18页"
```

Or:

```bash
python scripts/citation_diagnose.py footnotes.txt --json
```

The script provides classification, present/missing elements, source lookup hints, and a template-based corrected citation when local rule data is available. Treat script output as a first pass; verify edge cases against the handbook.

## Standard Answer Shape

When responding to a user, use this shape unless they ask for something else:

```text
识别结果：
- 类型：
- 置信度：

已有要素：
- ...

缺失/需确认要素：
- ...

去哪里找：
- ...

建议格式：
...

注意：
- ...
```

## Source Extraction Rules

- PDF book: inspect cover, copyright page, title page, table of contents area. Use copyright page for publisher, year, edition.
- PDF article: inspect first page and page headers/footers. Use article first page for author, title, journal, year, issue, start page.
- Statute or judicial interpretation: prefer official databases or PKULaw MCP when available. Capture full official name, article number, paragraph/item, current validity, and article text if needed.
- Case: capture case name, court, docket number, document type, source series/database. Public bulletin, guiding case, and People’s Court Case Library entries use their own formats.
- Web source: capture author if available, article title, platform/site, publication date, URL, and access date.

## Important Rules

- Chinese books: `作者：《书名》，出版社年份年版，第X页。`
- Chinese journal articles: `作者：《论文名》，载《期刊名》年份年第X期，第X页。`
- Edited collections: `作者：《文章名》，载编者主编：《书名》，出版社年份年版，第X页。`
- Statutes: `《法律名称》第X条第Y款第Z项。` Use Arabic numerals.
- Normative documents: include document number when available, e.g. `《文件名称》（发文字号）。`
- Cases: include case name, court, docket number, and document type unless citing a special source such as a bulletin or guiding case.
- Chinese repeat citations use `同前注〔X〕，第Y页。` or a clear short form. Do not use `前引`, `同上`, `supra`, or `Ibid.` for Chinese sources.
- Direct quotation: no `参见`; indirect or conceptual borrowing: use `参见`; secondary citation: use `转引自`.

## Full Handbook Coverage

The rule index is mandatory for careful work:

- Rules 1-24: general citation principles, citation placement, repeat citation, punctuation, article metadata.
- Rules 25-49: printed Chinese publications, authors, editors, translators, titles, editions, publisher/year, pages, chapters.
- Rules 50-58: online, electronic, broadcast, television, and audiovisual materials.
- Rules 59-65: unpublished materials, interviews, private correspondence, internal materials, conference papers, theses, archives.
- Rules 66-86: Chinese legal and official documents, laws, regulations, normative documents, standards, reports, white papers, Hong Kong/Macau/Taiwan legal documents, foreign law, treaties, UN documents.
- Rules 87-91: judicial cases.
- Rules 92-94: statistical data and charts.
- Rules 95-115: foreign-language principles, English sources, English law, English cases.
- Rules 116-122: French sources.
- Rules 123-128: German sources.
- Rules 129-134: Italian and Roman law sources.
- Rules 135-142: Russian sources.
- Rules 143-150: Japanese sources.

For any source type not explicitly represented in `citation_rules.json`, search the user-provided handbook or rule index by rule number or source name. If the OCR text is unclear, verify against the legally obtained original document.

## Reference Navigation

- `references/README_REFERENCE_DATA.md`: explains which optional reference files are intentionally not redistributed.
- `references/handbook_rule_index.json`: optional local full machine-readable index of rules 1-150. Load/search this for exhaustive coverage if the user provides it.
- `references/handbook_rule_index.md`: optional readable version of the full index with raw line ranges.
- `references/citation_rules.json`: optional machine-readable rule source. Load this first if present.
- `references/missing_elements_matrix.md`: quick checklist for missing elements by type.
- `references/source_lookup_guide.md`: where to find missing bibliographic facts.
- `references/operator_guardrails.md`: strict operating rules for other AI agents.
- `references/common_errors.md`: common mistakes and course-specific footnote traps.
- `references/citation_handbook_structured.md`: structured digest of the handbook.
- `assets/Law_Journal_Citation_Handbook_2025.pdf`: original handbook PDF for final verification when needed.

## Reference Data Build

When a user has their own legally obtained copy of the handbook PDF, prefer the deterministic local builder before asking an AI to improvise the reference files:

```bash
python3 scripts/build_reference_data.py
```

The builder checks whether the PDF is searchable, extracts local Markdown, builds the 1-150 rule index, writes `citation_rules.json`, and then runs validation. If it refuses to overwrite existing files, rerun with `--force` only after the user confirms they want to rebuild local reference data. If extraction is incomplete, run:

```bash
python3 scripts/build_reference_data.py --print-ai-contract
```

Then use the printed contract to repair the local files.

## Reference Data Audit

When a user rebuilds handbook reference data from their own PDF/OCR, do not trust the generated files merely because they exist. If the builder was not used, run:

```bash
python3 scripts/audit_reference_data.py
python3 scripts/self_test.py
```

`audit_reference_data.py` checks required files, rule count, continuous rule numbers, category ranges, raw line ranges, common rule hints, OCR/mojibake markers, and `citation_rules.json` shape. If it reports `ERRORS`, stop and repair the reference data before claiming full handbook coverage.

## Relationship to Other Skills

- `legal-citation-automator`: use after this skill has produced or approved footnote text; it handles DOCX insertion and compatibility checks.
- `legal-homework-formatter`: use for overall Civil Law homework layout, footnote style, and Word/WPS formatting.
- `pkulaw-legal-search`: use when missing law or case source facts require legal database retrieval.
