#!/usr/bin/env python3
"""Audit locally generated Law Journal Citation Handbook reference data.

This script contains no handbook content. It checks whether files generated
from a user's own PDF/OCR look structurally safe enough for
legal-citation-comprehensive to use.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = SCRIPT_DIR.parent

REQUIRED_FILES = {
    "pdf": Path("assets/Law_Journal_Citation_Handbook_2025.pdf"),
    "raw": Path("references/handbook_raw.md"),
    "structured": Path("references/citation_handbook_structured.md"),
    "rule_index_json": Path("references/handbook_rule_index.json"),
    "rule_index_md": Path("references/handbook_rule_index.md"),
    "citation_rules": Path("references/citation_rules.json"),
}

MIN_SIZES = {
    "pdf": 1_000_000,
    "raw": 50_000,
    "structured": 5_000,
    "rule_index_json": 50_000,
    "rule_index_md": 20_000,
    "citation_rules": 1_000,
}

EXPECTED_RANGES = {
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

EXPECTED_RULE_HINTS = {
    1: ["引注", "必要"],
    13: ["再次", "中文"],
    25: ["中文", "出版"],
    50: ["网络", "电子"],
    66: ["法律"],
    67: ["法律法规"],
    70: ["条款"],
    87: ["案例"],
    92: ["统计"],
    147: ["日本", "官方"],
    150: ["日文"],
}

EXPECTED_CITATION_TYPES = {
    "chinese_book",
    "translated_book",
    "journal_article",
    "collection_article",
    "newspaper_article",
    "statute",
    "normative_document",
    "judicial_case",
    "online_source",
    "thesis",
}

MOJIBAKE_PATTERNS = [
    "\ufffd",
    "\u00c3",
    "\u00c2",
    "\u00ef\u00bf\u00bd",
]


@dataclass
class Audit:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.info.append(message)


def resolve_skill_root(path: Path) -> Path:
    path = path.resolve()
    if (path / "references").is_dir() and (path / "scripts").is_dir():
        return path
    nested = path / "skills" / "legal-citation-comprehensive"
    if (nested / "references").is_dir():
        return nested.resolve()
    return path


def read_json(path: Path, audit: Audit) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        audit.error(f"missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        audit.error(f"invalid JSON in {path}: {exc}")
    return None


def check_files(root: Path, audit: Audit) -> None:
    for name, rel in REQUIRED_FILES.items():
        path = root / rel
        if not path.exists():
            audit.error(f"missing required file: {rel}")
            continue
        size = path.stat().st_size
        audit.note(f"{rel}: {size} bytes")
        if size <= 0:
            audit.error(f"empty required file: {rel}")
        elif size < MIN_SIZES[name]:
            audit.warn(f"{rel} is unusually small ({size} bytes); verify extraction completeness")


def check_rule_index(root: Path, audit: Audit) -> list[dict[str, Any]]:
    data = read_json(root / REQUIRED_FILES["rule_index_json"], audit)
    if not isinstance(data, dict):
        return []

    rules = data.get("rules")
    if not isinstance(rules, list):
        audit.error("handbook_rule_index.json must contain a list field: rules")
        return []

    nums = [rule.get("rule_number") for rule in rules if isinstance(rule, dict)]
    if data.get("count") != 150:
        audit.error(f"rule index count must be 150, got {data.get('count')!r}")
    if data.get("missing_rule_numbers") not in ([], None):
        audit.error(f"missing_rule_numbers must be [], got {data.get('missing_rule_numbers')!r}")
    if nums != list(range(1, 151)):
        missing = sorted(set(range(1, 151)) - set(n for n in nums if isinstance(n, int)))
        duplicates = sorted({n for n in nums if nums.count(n) > 1})
        audit.error(f"rule numbers must be exactly 1..150; missing={missing}, duplicates={duplicates}")

    titles: dict[str, int] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            audit.error("each rule must be an object")
            continue
        num = rule.get("rule_number")
        for key in ("rule_number", "title", "category", "text", "raw_start_line", "raw_end_line"):
            if key not in rule or rule[key] in ("", None):
                audit.error(f"rule {num}: missing required field {key}")
        title = str(rule.get("title", ""))
        if title:
            titles[title] = titles.get(title, 0) + 1
        text = str(rule.get("text", ""))
        if len(text) < 30:
            audit.warn(f"rule {num}: text is unusually short ({len(text)} chars)")
        if any(pattern in text for pattern in MOJIBAKE_PATTERNS):
            audit.error(f"rule {num}: text contains replacement/mojibake characters")
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text):
            audit.error(f"rule {num}: text contains control characters")
        start = rule.get("raw_start_line")
        end = rule.get("raw_end_line")
        if not isinstance(start, int) or not isinstance(end, int) or start <= 0 or end < start:
            audit.error(f"rule {num}: invalid raw line range {start!r}-{end!r}")

    by_num = {rule.get("rule_number"): rule for rule in rules if isinstance(rule, dict)}
    for category, nums_range in EXPECTED_RANGES.items():
        for num in nums_range:
            actual = by_num.get(num, {}).get("category")
            if actual != category:
                audit.error(f"rule {num}: expected category {category}, got {actual!r}")

    for num, hints in EXPECTED_RULE_HINTS.items():
        rule = by_num.get(num, {})
        haystack = f"{rule.get('title', '')}\n{rule.get('text', '')}"
        if not any(hint in haystack for hint in hints):
            audit.warn(f"rule {num}: does not contain expected hints {hints}; verify OCR/rule extraction")

    return rules


def check_raw_lines(root: Path, rules: list[dict[str, Any]], audit: Audit) -> None:
    raw_path = root / REQUIRED_FILES["raw"]
    if not raw_path.exists():
        return
    raw_lines = raw_path.read_text(encoding="utf-8", errors="replace").splitlines()
    line_count = len(raw_lines)
    if line_count < 500:
        audit.warn(f"handbook_raw.md has only {line_count} lines; verify PDF extraction")
    for rule in rules:
        num = rule.get("rule_number")
        start = rule.get("raw_start_line")
        end = rule.get("raw_end_line")
        if isinstance(start, int) and isinstance(end, int) and end > line_count:
            audit.error(f"rule {num}: raw_end_line {end} exceeds handbook_raw.md line count {line_count}")

    raw_text = "\n".join(raw_lines)
    if any(pattern in raw_text for pattern in MOJIBAKE_PATTERNS):
        audit.error("handbook_raw.md contains replacement/mojibake characters")
    unclear = raw_text.count("[待核: OCR]")
    if unclear:
        audit.warn(f"handbook_raw.md contains {unclear} [待核: OCR] markers; review before relying on affected rules")


def check_markdown_index(root: Path, audit: Audit) -> None:
    md_path = root / REQUIRED_FILES["rule_index_md"]
    if not md_path.exists():
        return
    text = md_path.read_text(encoding="utf-8", errors="replace")
    found = {int(match.group(1)) for match in re.finditer(r"第\s*(\d{1,3})\s*条", text)}
    missing = sorted(set(range(1, 151)) - found)
    if missing:
        audit.warn(f"handbook_rule_index.md may be missing visible rule headings: {missing[:20]}")


def check_citation_rules(root: Path, audit: Audit) -> None:
    data = read_json(root / REQUIRED_FILES["citation_rules"], audit)
    if not isinstance(data, dict):
        return
    types = data.get("types")
    if not isinstance(types, dict) or not types:
        audit.error("citation_rules.json must contain a non-empty types object")
        return
    missing = sorted(EXPECTED_CITATION_TYPES - set(types))
    if missing:
        audit.warn("citation_rules.json is missing common citation types: " + ", ".join(missing))
    for name, spec in types.items():
        if not isinstance(spec, dict):
            audit.error(f"citation type {name}: spec must be an object")
            continue
        for key in ("required", "optional", "template", "anchors"):
            if key not in spec:
                audit.warn(f"citation type {name}: missing {key}")
        for key in ("required", "optional", "anchors"):
            if key in spec and not isinstance(spec[key], list):
                audit.error(f"citation type {name}: {key} must be a list")
        if "template" in spec and not isinstance(spec["template"], str):
            audit.error(f"citation type {name}: template must be a string")


def run_audit(root: Path) -> Audit:
    skill_root = resolve_skill_root(root)
    audit = Audit()
    audit.note(f"skill root: {skill_root}")
    check_files(skill_root, audit)
    rules = check_rule_index(skill_root, audit)
    check_raw_lines(skill_root, rules, audit)
    check_markdown_index(skill_root, audit)
    check_citation_rules(skill_root, audit)
    return audit


def print_report(audit: Audit) -> None:
    print("Reference Data Audit")
    print("====================")
    if audit.info:
        print("\nINFO:")
        for item in audit.info:
            print(f"- {item}")
    if audit.warnings:
        print("\nWARNINGS:")
        for item in audit.warnings:
            print(f"- {item}")
    if audit.errors:
        print("\nERRORS:")
        for item in audit.errors:
            print(f"- {item}")
    print()
    if audit.errors:
        print(f"FAILED: {len(audit.errors)} error(s), {len(audit.warnings)} warning(s)")
    else:
        print(f"PASSED: 0 errors, {len(audit.warnings)} warning(s)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="skill root or repository root to audit (default: this skill)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON report")
    args = parser.parse_args()

    audit = run_audit(args.root)
    if args.json:
        print(json.dumps(
            {"errors": audit.errors, "warnings": audit.warnings, "info": audit.info},
            ensure_ascii=False,
            indent=2,
        ))
    else:
        print_report(audit)
    return 1 if audit.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
