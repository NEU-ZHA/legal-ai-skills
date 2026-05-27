#!/usr/bin/env python3
"""Self-test for the comprehensive legal citation skill.

The goal is not to prove every OCR line is perfect. The goal is to ensure the
skill is safely exhaustive: every numbered handbook rule is present and
searchable, common diagnostics work, and uncommon types route to rule lookup
instead of hallucinated templates.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULE_INDEX = ROOT / "references" / "handbook_rule_index.json"
RULES = ROOT / "references" / "citation_rules.json"
RAW = ROOT / "references" / "handbook_raw.md"
STRUCTURED = ROOT / "references" / "citation_handbook_structured.md"
PDF = ROOT / "assets" / "Law_Journal_Citation_Handbook_2025.pdf"
GUARDRAILS = ROOT / "references" / "operator_guardrails.md"
DIAG = ROOT / "scripts" / "citation_diagnose.py"
LOOKUP = ROOT / "scripts" / "handbook_lookup.py"


def load_diag():
    spec = importlib.util.spec_from_file_location("citation_diagnose", DIAG)
    if spec is None or spec.loader is None:
        raise AssertionError("Cannot import citation_diagnose.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def test_reference_files():
    for path in [RULE_INDEX, RULES, RAW, STRUCTURED, PDF, GUARDRAILS, DIAG, LOOKUP]:
        assert_true(path.exists(), f"missing required resource: {path}")
        assert_true(path.stat().st_size > 0, f"empty resource: {path}")
    guardrails = GUARDRAILS.read_text(encoding="utf-8")
    for phrase in ["Never invent missing facts", "[待补:", "Always cite handbook support"]:
        assert_true(phrase in guardrails, f"guardrail missing phrase: {phrase}")


def test_rule_index_exhaustive():
    data = json.loads(RULE_INDEX.read_text(encoding="utf-8"))
    rules = data["rules"]
    nums = [rule["rule_number"] for rule in rules]
    assert_true(data["count"] == 150, "rule count must be 150")
    assert_true(data["missing_rule_numbers"] == [], "no rule numbers may be missing")
    assert_true(nums == list(range(1, 151)), "rule numbers must be exactly 1..150")
    for rule in rules:
        assert_true(rule["title"], f"rule {rule['rule_number']} missing title")
        assert_true(rule["text"], f"rule {rule['rule_number']} missing text")
        assert_true(rule["raw_start_line"] <= rule["raw_end_line"], f"rule {rule['rule_number']} bad line range")


def test_category_ranges():
    expected = {
        "general_rules": range(1, 25),
        "print_publications": range(25, 50),
        "online_and_media": range(50, 59),
        "unpublished_conference_thesis_archive": range(59, 66),
        "legal_and_official_documents": range(66, 87),
        "judicial_cases": range(87, 92),
        "statistics": range(92, 95),
        "english_and_foreign_general": range(95, 116),
        "french_sources": range(116, 123),
        "german_sources": range(123, 129),
        "italian_and_roman_law_sources": range(129, 135),
        "russian_sources": range(135, 143),
        "japanese_sources": range(143, 151),
    }
    data = json.loads(RULE_INDEX.read_text(encoding="utf-8"))
    by_num = {rule["rule_number"]: rule for rule in data["rules"]}
    for category, nums in expected.items():
        for num in nums:
            assert_true(by_num[num]["category"] == category, f"rule {num} should be {category}")


def test_lookup_every_rule():
    for num in range(1, 151):
        result = subprocess.run(
            [sys.executable, str(LOOKUP), "--rule", str(num)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert_true(f"第{num}条" in result.stdout, f"lookup failed for rule {num}")


def test_keyword_lookup_uncommon_sources():
    examples = {
        "白皮书": "第80条",
        "香港法律": "第81条",
        "联合国文件": "第86条",
        "统计数据": "第92条",
        "日本官方文件": "第147条",
        "再次引用日文": "第150条"
    }
    for query, expected in examples.items():
        result = subprocess.run(
            [sys.executable, str(LOOKUP), query],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert_true(expected in result.stdout, f"keyword lookup {query} should include {expected}")


def test_diagnostics_representative():
    mod = load_diag()
    rules = mod.load_rules()
    cases = [
        ("王名扬《美国行政法》第18页", "chinese_book", ["publisher", "year"]),
        ("[美]富勒：《法律的道德性》，郑戈译，商务印书馆2005年版。", "translated_book", []),
        ("季卫东：《法律程序的意义》，载《中国社会科学》1993年第1期，第91页。", "journal_article", []),
        ("王保树：《董事和董事会》，载梁慧星主编：《民商法论丛》第1卷，法律出版社1994年版，第110页。", "collection_article", []),
        ("何海波：《判决书上网》，载《法制日报》2000年5月21日，第2版。", "newspaper_article", []),
        ("《民法典》第一百五十三条第1款", "statute", []),
        ("《国务院关于在全国建立农村最低生活保障制度的通知》（国发〔2007〕19号）。", "normative_document", []),
        ("示例原告诉示例被告合同纠纷案，示例法院（20XX）XX民初XXXXX号民事判决书。", "judicial_case", []),
        ("刘松山：《失信惩戒立法的三大问题》，载微信公众号“中国法律评论”2019年11月19日，https://example.com，2026年5月26日访问。", "online_source", []),
        ("李松锋：《游走在上帝与凯撒之间》，中国政法大学2013年博士学位论文，第30页。", "thesis", []),
    ]
    for text, expected_type, expected_missing in cases:
        report = mod.diagnose_one(text, rules)
        assert_true(report["type"] == expected_type, f"{text} classified as {report['type']}, expected {expected_type}")
        for key in expected_missing:
            assert_true(key in report["missing_required"], f"{text} should miss {key}")
        assert_true("模板缺少字段" not in report["suggested"], f"{text} generated template error")


def test_missing_content_placeholders():
    mod = load_diag()
    rules = mod.load_rules()
    report = mod.diagnose_one("王名扬《美国行政法》第18页", rules)
    assert_true("[待补: publisher]" in report["suggested"], "missing publisher should be a placeholder")
    assert_true("[待补: year]" in report["suggested"], "missing year should be a placeholder")
    assert_true(any("版权页" in item for item in report["lookup_guidance"]), "missing book facts should point to copyright page")

    report = mod.diagnose_one("《民法典》第153条", rules)
    assert_true(any("条文全文" in warning for warning in report["warnings"]), "statute citation should warn about article text when needed")
    assert_true(any("PKULaw" in item or "法条" in item for item in report["lookup_guidance"]), "statute lookup should point to legal text source")


def main() -> int:
    tests = [
        test_reference_files,
        test_rule_index_exhaustive,
        test_category_ranges,
        test_lookup_every_rule,
        test_keyword_lookup_uncommon_sources,
        test_diagnostics_representative,
        test_missing_content_placeholders,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
