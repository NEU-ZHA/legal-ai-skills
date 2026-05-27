#!/usr/bin/env python3
"""Diagnose and format legal citations under the Law Journal Citation Handbook.

This is a conservative first-pass tool. It extracts obvious elements, reports
missing facts, and generates a placeholder citation instead of inventing data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
RULES_PATH = SCRIPT_DIR.parent / "references" / "citation_rules.json"


def load_rules() -> dict[str, Any]:
    if not RULES_PATH.exists():
        raise SystemExit(
            "Missing optional reference file: references/citation_rules.json\n"
            "This public package does not redistribute third-party handbook-derived "
            "rule data. Add a locally licensed citation_rules.json or use the skill "
            "in diagnosis-only mode with explicit [待补: ...] placeholders."
        )
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def first_match(pattern: str, text: str, group: int = 1) -> str:
    match = re.search(pattern, text)
    return match.group(group).strip() if match else ""


def classify(text: str) -> tuple[str, float, list[str]]:
    reasons: list[str] = []

    if re.search(r"https?://", text):
        reasons.append("contains URL")
        return "online_source", 0.86, reasons
    if re.search(r"载《[^》]*报[^》]*》", text):
        reasons.append("contains newspaper marker")
        return "newspaper_article", 0.82, reasons
    if re.search(r"指导案例第\d+号|人民法院案例库|诉.+案|（(?:\d{4}|20XX)）.+号|判决书|裁定书", text):
        reasons.append("contains case markers")
        return "judicial_case", 0.82, reasons
    if re.search(r"第\s*[0-9一二三四五六七八九十百千万]+\s*条", text) and re.search(r"《[^》]*(法|典|条例|规定|解释)[^》]*》", text):
        reasons.append("contains law title and article number")
        return "statute", 0.9, reasons
    if re.search(r"法释〔\d{4}〕\d+号|国发〔\d{4}〕\d+号|发〔\d{4}〕\d+号", text):
        reasons.append("contains document number")
        return "normative_document", 0.82, reasons
    if re.search(r"微信公众号|访问|载[^，,。]+网", text):
        reasons.append("contains web/platform markers")
        return "online_source", 0.75, reasons
    if re.search(r"学位论文|博士论文|硕士论文", text):
        reasons.append("contains thesis marker")
        return "thesis", 0.82, reasons
    if re.search(r"会议论文|研讨会|学术会议", text):
        reasons.append("contains conference marker")
        return "conference_paper", 0.78, reasons
    if re.search(r"载.+主编：《", text):
        reasons.append("contains edited collection marker")
        return "collection_article", 0.82, reasons
    if re.search(r"载《[^》]+》\d{4}年第?\d+期", text):
        reasons.append("contains journal year/issue marker")
        return "journal_article", 0.86, reasons
    if re.search(r"\d{4}年\s*第?\s*\d+\s*期", text):
        reasons.append("contains year/issue marker")
        return "journal_article", 0.58, reasons
    if re.search(r"^\[[^\]]+\].+译", text) or re.search(r"》[^，,。]*译，", text):
        reasons.append("contains country/translator marker")
        return "translated_book", 0.82, reasons
    if re.search(r"[A-Z][A-Za-z .]+ v\. [A-Z]", text) or re.search(r"\d+\s+[A-Z][A-Za-z. ]+\s+\d+\s*\(\d{4}\)", text):
        reasons.append("contains English legal/article pattern")
        return "english_article", 0.62, reasons
    if "《" in text and "》" in text:
        reasons.append("contains Chinese title brackets")
        return "chinese_book", 0.64, reasons
    return "unknown", 0.2, ["no strong citation markers"]


def normalize_article_number(raw: str) -> str:
    if not raw:
        return ""
    digits = re.search(r"\d+", raw)
    if digits:
        return f"第{digits.group(0)}条"
    chinese = raw
    chinese = chinese.replace("第", "").replace("条", "").replace(" ", "")
    n = chinese_number_to_int(chinese)
    return f"第{n}条" if n else raw


def chinese_number_to_int(text: str) -> int:
    digits = {
        "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
        "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
    }
    units = {"十": 10, "百": 100, "千": 1000, "万": 10000}
    if not text:
        return 0
    if all(ch in digits for ch in text):
        value = 0
        for ch in text:
            value = value * 10 + digits[ch]
        return value
    total = 0
    section = 0
    number = 0
    for ch in text:
        if ch in digits:
            number = digits[ch]
        elif ch in units:
            unit = units[ch]
            if unit == 10000:
                section = (section + number) * unit
                total += section
                section = 0
            else:
                if number == 0:
                    number = 1
                section += number * unit
            number = 0
        else:
            return 0
    return total + section + number


def extract_elements(citation_type: str, text: str) -> dict[str, str]:
    e: dict[str, str] = {}

    title = first_match(r"《([^》]+)》", text)
    if title:
        e["title"] = title

    page = first_match(r"第\s*(\d+(?:[-—－]\d+)?)\s*页", text)
    if page:
        e["page"] = f"第{page.replace('—', '-').replace('－', '-')}页"

    year = first_match(r"(\d{4})年", text)
    if year:
        e["year"] = year

    if citation_type in {"chinese_book", "journal_article", "collection_article", "newspaper_article", "thesis", "conference_paper"}:
        author = first_match(r"^([^：《，,。]+)[：《，,]", text)
        if author and not author.startswith(("载", "参见", "见")):
            e["author"] = author.replace("参见", "").replace("见", "").strip()

    if citation_type == "chinese_book":
        publisher = first_match(r"》，?\s*([^，,。\d]*出版社)", text)
        if publisher:
            e["publisher"] = publisher
        edition = first_match(r"[（(](第?\d+版)[）)]", text)
        if edition:
            e["edition"] = edition if edition.startswith("第") else f"第{edition}"

    elif citation_type == "translated_book":
        country = first_match(r"^\[([^\]]+)\]", text)
        if country:
            e["country"] = country
        author = first_match(r"^\[[^\]]+\]([^：《，,。]+)[：《]", text)
        if author:
            e["author"] = author
        translator = first_match(r"》，?\s*([^，,。]+?)译", text)
        if translator:
            e["translator"] = translator
        publisher = first_match(r"译，?\s*([^，,。\d]*出版社)", text)
        if publisher:
            e["publisher"] = publisher

    elif citation_type == "journal_article":
        journal = first_match(r"载《([^》]+)》", text)
        if journal:
            e["journal"] = journal
        issue = first_match(r"\d{4}年\s*第?\s*(\d+)\s*期", text)
        if issue:
            e["issue"] = issue

    elif citation_type == "collection_article":
        editor = first_match(r"载([^：:《，,。]+)主编：《", text)
        if editor:
            e["editor"] = editor
        titles = re.findall(r"《([^》]+)》", text)
        if titles:
            e["title"] = titles[0]
        if len(titles) > 1:
            e["book_title"] = titles[1]
        publisher = first_match(r"》，?\s*([^，,。\d]*出版社)", text)
        if publisher:
            e["publisher"] = publisher
        volume = first_match(r"(第\d+卷)", text)
        if volume:
            e["volume"] = volume

    elif citation_type == "newspaper_article":
        newspaper = first_match(r"载《([^》]+)》", text)
        if newspaper:
            e["newspaper"] = newspaper
        date = first_match(r"(\d{4}年\d{1,2}月\d{1,2}日)", text)
        if date:
            e["date"] = date
        edition = first_match(r"第\s*(\d+)\s*版", text)
        if edition:
            e["page_or_edition"] = f"第{edition}版"

    elif citation_type == "statute":
        law = first_match(r"《([^》]+)》", text)
        if law:
            e["law_name"] = law
        article_raw = first_match(r"(第\s*[0-9一二三四五六七八九十百千万]+\s*条)", text)
        if article_raw:
            e["article"] = normalize_article_number(article_raw)
        para = first_match(r"第\s*\d+\s*条\s*第\s*(\d+)\s*款", text)
        if para:
            e["paragraph"] = f"第{para}款"
        item = first_match(r"第\s*\d+\s*款\s*第\s*(\d+)\s*项", text)
        if item:
            e["item"] = f"第{item}项"
        if re.search(r"[“\"].{8,}[”\"]", text):
            e["article_text"] = first_match(r"[“\"](.+)[”\"]", text)

    elif citation_type == "normative_document":
        if title:
            e["document_title"] = title
        doc_number = first_match(r"[（(]([^（）()]*〔\d{4}〕\d+号)[）)]", text)
        if doc_number:
            e["document_number"] = doc_number

    elif citation_type == "judicial_case":
        case_name = first_match(r"([^，,。]*诉[^，,。]*?案)", text)
        if case_name:
            e["case_name"] = case_name
        court = first_match(r"([^，,。]*法院)", text)
        if court:
            e["court"] = court
        docket = first_match(r"([（(](?:\d{4}|20XX)[）)][^，,。]*?号)", text)
        if docket:
            e["docket_number"] = docket.replace("(", "（").replace(")", "）")
        doc_type = first_match(r"((?:民事|刑事|行政)?(?:判决书|裁定书|决定书))", text)
        if doc_type:
            e["document_type"] = doc_type
        source = first_match(r"载《([^》]+)》", text)
        if source:
            e["source"] = source

    elif citation_type == "online_source":
        author = first_match(r"^([^：《，,。]+)[：《]", text)
        if author:
            e["author"] = author
        if title:
            e["title"] = title
        site = first_match(r"载([^，,。]+)", text)
        if site:
            e["site_or_platform"] = site
        url = first_match(r"(https?://[^\s，,。]+)", text)
        if url:
            e["url"] = url
        dates = re.findall(r"\d{4}年\d{1,2}月\d{1,2}日", text)
        if dates:
            if "访问" in text and len(dates) >= 1:
                e["access_date"] = dates[-1]
                if len(dates) > 1:
                    e["publish_date"] = dates[0]
            else:
                e["publish_date"] = dates[0]

    elif citation_type == "thesis":
        school = first_match(r"，([^，,。\d]+(?:大学|学院|研究院))\d{4}年", text)
        if school:
            e["school"] = school
        degree = first_match(r"(博士|硕士)学位论文", text)
        if degree:
            e["degree_type"] = degree

    return e


def missing_for(rule: dict[str, Any], elements: dict[str, str]) -> tuple[list[str], list[str]]:
    required = [key for key in rule.get("required", []) if not elements.get(key)]
    optional = [key for key in rule.get("optional", []) if not elements.get(key)]
    return required, optional


def value(elements: dict[str, str], key: str) -> str:
    return elements.get(key) or f"[待补: {key}]"


def part(elements: dict[str, str], key: str, prefix: str = "", suffix: str = "") -> str:
    return f"{prefix}{elements[key]}{suffix}" if elements.get(key) else ""


def format_citation(citation_type: str, rule: dict[str, Any], elements: dict[str, str]) -> str:
    data = {key: value(elements, key) for key in rule.get("required", []) + rule.get("optional", [])}
    data["original"] = elements.get("original", "")
    data.update(
        {
            "edition_part": part(elements, "edition", "", "，"),
            "page_part": part(elements, "page", "，", ""),
            "volume_part": part(elements, "volume", "", ""),
            "paragraph_part": part(elements, "paragraph", "", ""),
            "item_part": part(elements, "item", "", ""),
            "document_number_part": part(elements, "document_number", "（", "）"),
            "date_part": part(elements, "date", "，", ""),
            "document_type_part": part(elements, "document_type", "", ""),
            "author_part": part(elements, "author", "", "："),
            "publish_date_part": part(elements, "publish_date", "", ""),
            "pinpoint_part": part(elements, "pinpoint", ", ", ""),
            "title_italic": value(elements, "title"),
        }
    )
    try:
        return rule["template"].format(**data)
    except KeyError as exc:
        return f"[模板缺少字段 {exc}] {rule.get('example', '')}"


def guidance_for(citation_type: str, missing: list[str], rule: dict[str, Any]) -> list[str]:
    lookup = rule.get("lookup", {})
    defaults = {
        "publisher": "查图书版权页。",
        "year": "查版权页、论文首页或数据库元数据。",
        "page": "查纸书页码或论文原始页码。",
        "journal": "查论文首页、页眉页脚或数据库元数据。",
        "issue": "查论文首页、期刊封面或数据库元数据。",
        "court": "查裁判文书页首。",
        "docket_number": "查裁判文书页首案号。",
        "url": "查网页地址栏或数据库原文链接。",
        "access_date": "用实际访问日期。",
        "article_text": "查官方法条文本或 PKULaw 法条页。",
    }
    return [f"{key}: {lookup.get(key) or defaults.get(key, '查原始来源或权威数据库。')}" for key in missing]


def warnings_for(citation_type: str, text: str, elements: dict[str, str]) -> list[str]:
    warnings: list[str] = []
    if re.search(r"前引|同上|Ibid\.?|supra", text, re.I) and not citation_type.startswith("english"):
        warnings.append("中文引注不使用“前引”“同上”“supra/Ibid.”，改用“同前注〔X〕”或清楚的简称。")
    if re.search(r"第[一二三四五六七八九十百千万]+条", text):
        warnings.append("条号通常使用阿拉伯数字，例如“第657条”。")
    if citation_type == "statute" and elements.get("article") and not elements.get("article_text"):
        warnings.append("民法作业中，如果正文只写法条编号，脚注应补足条文全文。")
    if "参见" in text and re.search(r"[“\"].+[”\"]", text):
        warnings.append("直接引用原文通常不用“参见”；概括转述才用“参见”。")
    return warnings


def diagnose_one(text: str, rules: dict[str, Any]) -> dict[str, Any]:
    citation_type, confidence, reasons = classify(text)
    type_rules = rules["types"]
    rule = type_rules.get(citation_type, {"label": "未知类型", "required": [], "optional": [], "template": "[无法稳定识别类型] {original}"})
    elements = extract_elements(citation_type, text)
    elements["original"] = text
    missing_required, missing_optional = missing_for(rule, elements)
    return {
        "original": text,
        "type": citation_type,
        "label": rule.get("label", citation_type),
        "confidence": confidence,
        "reasons": reasons,
        "elements": elements,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "lookup_guidance": guidance_for(citation_type, missing_required + missing_optional, rule),
        "suggested": format_citation(citation_type, rule, elements),
        "warnings": warnings_for(citation_type, text, elements),
        "handbook_anchors": rule.get("anchors", []),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "识别结果：",
        f"- 类型：{report['label']} ({report['type']})",
        f"- 置信度：{report['confidence']:.2f}",
        f"- 依据：{'；'.join(report['reasons'])}",
        "",
        "已有要素：",
    ]
    if report["elements"]:
        lines.extend(f"- {k}: {v}" for k, v in report["elements"].items())
    else:
        lines.append("- 暂未识别出稳定要素")
    lines.extend(["", "缺失/需确认要素："])
    missing = report["missing_required"] + [f"{x}（可选）" for x in report["missing_optional"]]
    lines.extend(f"- {x}" for x in missing) if missing else lines.append("- 无明显缺失")
    lines.extend(["", "去哪里找："])
    lines.extend(f"- {x}" for x in report["lookup_guidance"]) if report["lookup_guidance"] else lines.append("- 暂无")
    lines.extend(["", "建议格式：", report["suggested"]])
    if report["warnings"]:
        lines.extend(["", "注意："])
        lines.extend(f"- {x}" for x in report["warnings"])
    if report["handbook_anchors"]:
        lines.extend(["", "手册定位：", "- " + "、".join(report["handbook_anchors"])])
    return "\n".join(lines)


def split_inputs(raw: str) -> list[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="Text file containing one citation per line")
    parser.add_argument("--text", help="Single citation text")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if args.text:
        items = [args.text.strip()]
    elif args.file:
        items = split_inputs(Path(args.file).read_text(encoding="utf-8"))
    else:
        items = split_inputs(sys.stdin.read())

    rules = load_rules()
    reports = [diagnose_one(item, rules) for item in items]

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        print("\n\n---\n\n".join(render_markdown(report) for report in reports))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
