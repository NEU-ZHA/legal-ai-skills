# Operator Guardrails

This file is for agents that are not careful enough by default. Follow it literally.

## Non-Negotiable Rules

1. Never invent missing facts.
   - Do not guess publisher, year, issue, page, court, docket number, URL, access date, or article text.
   - Use `[待补: 要素名]` placeholders.

2. Always identify the source type before formatting.
   - If type is uncertain, say so and give the closest candidates.
   - Do not force a messy citation into a random template.

3. Always cite handbook support.
   - Use `scripts/handbook_lookup.py` or search `references/handbook_rule_index.md`.
   - Give rule numbers such as `第25条、第48条`.

4. Always explain where missing facts come from.
   - Book facts: copyright page.
   - Article facts: article first page or database metadata.
   - Statute text: official statute source or PKULaw.
   - Case facts: judgment heading or legal database metadata.
   - Web facts: page title/byline/date/URL/access date.

5. Separate diagnosis from final citation.
   - First output type, present elements, missing elements, lookup path.
   - Then output suggested format.

6. Do not insert into DOCX if any `[待补: ...]` remains.
   - Use `legal-citation-automator` only after source facts are verified.

7. For course Civil Law homework, statute footnotes have special handling.
   - If正文 only mentions a law article number, include article text in the footnote.
   - If正文 already quotes the full article and the footnote adds no new information, omit the footnote.

## Required Output Template

```text
识别结果：
- 类型：
- 置信度：
- 手册依据：

已有要素：
- ...

缺失/需确认要素：
- ...

去哪里找：
- ...

建议格式：
...

不能最终确认的原因：
- ...
```

If there is no missing element, replace the last section with:

```text
可直接使用：
- 是
```

## Failure Modes to Avoid

- Wrong: `王名扬：《美国行政法》，中国法制出版社1995年版。` when the user only gave `王名扬《美国行政法》`.
- Right: `王名扬：《美国行政法》，[待补: 出版社][待补: 年份]年版。`

- Wrong: treating a newspaper article as a case because the title contains `判决书`.
- Right: if it says `载《法制日报》2000年5月21日，第2版`, classify it as a newspaper article.

- Wrong: using `前引` or `同上` for Chinese sources.
- Right: use `同前注〔X〕` or a clear short form.

- Wrong: finalizing a statute citation for Civil Law homework with only `《民法典》第153条。` when正文 does not quote the article.
- Right: retrieve and include the article text, or mark `[待补: 条文全文]`.
