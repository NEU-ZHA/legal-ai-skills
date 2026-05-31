# 《法学引注手册》本地配套包 / Local Handbook Pack

这个文件给课堂分享、同学互助和本地安装使用。仓库不携带《法学引注手册（第二版）》PDF、OCR 全文或完整规则索引；每个使用者应把自己合法取得的同版文件放到本地，再生成机器可读索引。

## 一分钟版

1. 安装本仓库的 skills。
2. 准备同版《法学引注手册（第二版）》PDF。
3. 如果 PDF 不能选中文字，先用 WPS、Adobe Acrobat 或 OCR 工具转成可搜索 PDF。
4. 把 PDF 放到：

```text
skills/legal-citation-comprehensive/assets/Law_Journal_Citation_Handbook_2025.pdf
```

5. 让 AI 生成下面这些本地文件：

```text
skills/legal-citation-comprehensive/references/handbook_raw.md
skills/legal-citation-comprehensive/references/citation_handbook_structured.md
skills/legal-citation-comprehensive/references/handbook_rule_index.json
skills/legal-citation-comprehensive/references/handbook_rule_index.md
skills/legal-citation-comprehensive/references/citation_rules.json
```

6. 跑测试：

```bash
python3 skills/legal-citation-comprehensive/scripts/handbook_lookup.py --rule 1
python3 skills/legal-citation-comprehensive/scripts/self_test.py
```

## 直接给 AI 的处理提示词

```text
请使用 legal-citation-comprehensive 的本地参考资料生成流程。

我已经把同版《法学引注手册（第二版）》PDF 放在：
skills/legal-citation-comprehensive/assets/Law_Journal_Citation_Handbook_2025.pdf

请先确认 PDF 是否可搜索：
1. 如果可搜索，请提取为 Markdown，保存到：
   skills/legal-citation-comprehensive/references/handbook_raw.md
2. 如果是图片扫描件，请先停止，提醒我用 WPS/Adobe/OCR 工具转成可搜索 PDF；不要直接全文 OCR 整本扫描件来浪费 token。

然后请生成：
- skills/legal-citation-comprehensive/references/citation_handbook_structured.md
- skills/legal-citation-comprehensive/references/handbook_rule_index.json
- skills/legal-citation-comprehensive/references/handbook_rule_index.md
- skills/legal-citation-comprehensive/references/citation_rules.json

handbook_rule_index.json 必须覆盖第 1-150 条规则，且规则号不能缺漏。
每条规则至少包含：
- rule_number
- title
- category
- text
- raw_start_line
- raw_end_line

citation_rules.json 应包含常见引注类型的：
- types
- required
- optional
- template
- anchors
- lookup_guidance

不要改写规则含义。
OCR 不清楚的地方标记为 [待核: OCR]。
生成后运行：
python3 skills/legal-citation-comprehensive/scripts/handbook_lookup.py --rule 1
python3 skills/legal-citation-comprehensive/scripts/self_test.py
并把测试结果告诉我。
```

## 分享时怎么说

可以这样讲：

```text
这个 skill 本身不把《法学引注手册》打包进去。你需要自己准备同版 PDF；如果是扫描版，先用 WPS 转成可搜索 PDF。然后把 PDF 放进指定目录，让 AI 按提示词生成 5 个本地参考文件。生成后 self_test 全过，就可以做完整手册规则核验；没生成之前，也可以先做脚注类型判断、缺项提示和占位符安全建议。
```

## 常见错误

- 只有 PDF，没有索引：可以做初步诊断，但不能声称已经完成手册全量核验。
- 扫描 PDF 直接丢给 AI：token 消耗大，OCR 错误多。先转可搜索 PDF。
- 规则号缺漏：`self_test.py` 会失败。不要忽略。
- OCR 不清楚却直接补写：必须标 `[待核: OCR]`。
- 缺出版社、年份、页码、案号：用 `[待补: ...]`，不要猜。
