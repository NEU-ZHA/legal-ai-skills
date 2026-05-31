#!/usr/bin/env python3
"""Build local citation-handbook reference data from a user's own PDF.

The public repository intentionally does not ship handbook text. This script
only orchestrates local extraction, indexing, and validation for a legally
obtained copy of the handbook.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = SCRIPT_DIR.parent

PDF_REL = Path("assets/Law_Journal_Citation_Handbook_2025.pdf")
RAW_REL = Path("references/handbook_raw.md")
STRUCTURED_REL = Path("references/citation_handbook_structured.md")
RULE_INDEX_JSON_REL = Path("references/handbook_rule_index.json")
RULE_INDEX_MD_REL = Path("references/handbook_rule_index.md")
CITATION_RULES_REL = Path("references/citation_rules.json")

CATEGORY_RANGES: list[tuple[str, range]] = [
    ("general_rules", range(1, 25)),
    ("print_publications", range(25, 50)),
    ("online_and_media", range(50, 59)),
    ("unpublished_conference_thesis_archive", range(59, 66)),
    ("legal_and_official_documents", range(66, 87)),
    ("judicial_cases", range(87, 92)),
    ("statistics", range(92, 95)),
    ("english_and_foreign_general", range(95, 116)),
    ("french_sources", range(116, 123)),
    ("german_sources", range(123, 129)),
    ("italian_and_roman_law_sources", range(129, 135)),
    ("russian_sources", range(135, 143)),
    ("japanese_sources", range(143, 151)),
]

EXPECTED_OUTPUTS = [
    RAW_REL,
    STRUCTURED_REL,
    RULE_INDEX_JSON_REL,
    RULE_INDEX_MD_REL,
    CITATION_RULES_REL,
]


@dataclass
class Candidate:
    rule_number: int
    title: str
    line_number: int
    normalized_title: str


def resolve_skill_root(path: Path) -> Path:
    path = path.resolve()
    if (path / "references").is_dir() and (path / "scripts").is_dir():
        return path
    nested = path / "skills" / "legal-citation-comprehensive"
    if (nested / "references").is_dir():
        return nested.resolve()
    return path


def category_for(rule_number: int) -> str:
    for category, nums in CATEGORY_RANGES:
        if rule_number in nums:
            return category
    return "unknown"


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def extract_with_pdftotext(pdf_path: Path) -> tuple[str, str]:
    tool = shutil.which("pdftotext")
    if not tool:
        return "", "pdftotext not found"
    result = run_command([tool, "-layout", "-enc", "UTF-8", str(pdf_path), "-"])
    if result.returncode != 0:
        return "", result.stderr.strip() or "pdftotext failed"
    return result.stdout, "pdftotext"


def extract_with_pdfplumber(pdf_path: Path) -> tuple[str, str]:
    try:
        import pdfplumber  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local install
        return "", f"pdfplumber unavailable: {exc}"

    pages: list[str] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
    except Exception as exc:  # pragma: no cover - depends on PDF parser
        return "", f"pdfplumber failed: {exc}"
    return "\f".join(pages), "pdfplumber"


def extract_with_pypdf(pdf_path: Path) -> tuple[str, str]:
    try:
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            from PyPDF2 import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local install
        return "", f"pypdf/PyPDF2 unavailable: {exc}"

    pages: list[str] = []
    try:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            pages.append(page.extract_text() or "")
    except Exception as exc:  # pragma: no cover - depends on PDF parser
        return "", f"pypdf/PyPDF2 failed: {exc}"
    return "\f".join(pages), "pypdf"


def extract_pdf_text(pdf_path: Path) -> tuple[str, str, list[str]]:
    attempts: list[tuple[str, str, str]] = []
    for extractor in (extract_with_pdftotext, extract_with_pdfplumber, extract_with_pypdf):
        text, source = extractor(pdf_path)
        if text.strip():
            attempts.append((source, text, ""))
        else:
            attempts.append((source, "", source))

    usable = [(source, text) for source, text, _ in attempts if text.strip()]
    errors = [err for _, _, err in attempts if err]
    if not usable:
        return "", "", errors

    # Pick the extractor that yielded the most text. For searchable PDFs this is
    # usually pdftotext; for some PDFs the Python fallbacks perform better.
    source, text = max(usable, key=lambda item: len(item[1]))
    return text, source, errors


def searchable_score(text: str) -> dict[str, int]:
    return {
        "chars": len(text.strip()),
        "cjk": len(re.findall(r"[\u4e00-\u9fff]", text)),
        "latin_words": len(re.findall(r"[A-Za-z]{3,}", text)),
        "digits": len(re.findall(r"\d", text)),
    }


def assert_searchable(text: str, min_chars: int) -> None:
    score = searchable_score(text)
    semantic_chars = score["cjk"] + score["latin_words"] * 3
    if score["chars"] < min_chars or semantic_chars < 2000:
        raise SystemExit(
            "The PDF does not look searchable enough for reliable extraction.\n"
            f"Extracted chars={score['chars']}, CJK={score['cjk']}, "
            f"latin_words={score['latin_words']}.\n"
            "Use WPS, Adobe Acrobat, or another OCR tool to convert the scanned "
            "PDF into a searchable PDF first, then rerun this script."
        )


def pdf_text_to_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    pages = text.split("\f")
    lines: list[str] = []
    for index, page in enumerate(pages, start=1):
        if len(pages) > 1:
            lines.append(f"<!-- PDF page {index} -->")
        lines.extend(line.rstrip() for line in page.splitlines())
        lines.append("")
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def normalize_heading(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[，,。；;：:、（）()［］\[\]【】《》“”\"'‘’·•\-—_/／]", "", text)
    return text.lower()


def cleanup_title(text: str) -> str:
    text = re.sub(r"\s*[／/]\s*\d{1,3}\s*$", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip(" .．、")


def extract_toc_titles(lines: list[str]) -> tuple[dict[int, str], int]:
    toc: dict[int, str] = {}
    toc_lines: list[int] = []
    for line_number, line in enumerate(lines[:2200], start=1):
        match = re.match(r"^\s*(\d{1,3})\s*[.．]\s*(.+?)\s*[／/]\s*\d{1,3}\s*$", line)
        if not match:
            continue
        rule_number = int(match.group(1))
        if 1 <= rule_number <= 150 and rule_number not in toc:
            title = cleanup_title(match.group(2))
            if normalize_heading(title):
                toc[rule_number] = title
                toc_lines.append(line_number)
    return toc, max(toc_lines) if toc_lines else 0


def looks_like_toc_line(text: str) -> bool:
    return bool(re.search(r"\s*[／/]\s*\d{1,3}\s*$", text))


def find_heading_candidates(lines: list[str], min_line: int) -> dict[int, list[Candidate]]:
    candidates: dict[int, list[Candidate]] = {num: [] for num in range(1, 151)}
    for line_number, line in enumerate(lines, start=1):
        if line_number <= min_line:
            continue
        match = re.match(r"^\s*(\d{1,3})\s*[.．]\s*(.+?)\s*$", line)
        if not match:
            continue
        rule_number = int(match.group(1))
        if not 1 <= rule_number <= 150:
            continue
        title = cleanup_title(match.group(2))
        normalized = normalize_heading(title)
        if not normalized or len(normalized) < 2:
            continue
        if looks_like_toc_line(line) or "://" in title or len(title) > 80:
            continue
        candidates[rule_number].append(
            Candidate(
                rule_number=rule_number,
                title=title,
                line_number=line_number,
                normalized_title=normalized,
            )
        )
    return candidates


def title_matches(candidate: Candidate, toc_title: str) -> bool:
    expected = normalize_heading(toc_title)
    actual = candidate.normalized_title
    if not expected:
        return False
    return actual == expected or actual.startswith(expected) or expected.startswith(actual)


def choose_headings(
    candidates: dict[int, list[Candidate]], toc_titles: dict[int, str]
) -> tuple[list[Candidate], list[int], list[str]]:
    chosen: list[Candidate] = []
    missing: list[int] = []
    warnings: list[str] = []
    previous_line = 0

    for rule_number in range(1, 151):
        pool = [item for item in candidates[rule_number] if item.line_number > previous_line]
        use_toc_title = False
        if toc_titles.get(rule_number):
            matched = [item for item in pool if title_matches(item, toc_titles[rule_number])]
            if matched:
                pool = matched
                use_toc_title = True
            elif pool:
                warnings.append(
                    f"rule {rule_number}: heading title did not match TOC title; "
                    "using body heading candidate"
                )
        if not pool:
            missing.append(rule_number)
            continue
        item = pool[0]
        title = toc_titles[rule_number] if use_toc_title else item.title
        chosen.append(
            Candidate(
                rule_number=rule_number,
                title=title,
                line_number=item.line_number,
                normalized_title=normalize_heading(title),
            )
        )
        previous_line = item.line_number

    return chosen, missing, warnings


def find_last_rule_end(lines: list[str], start_line: int) -> int:
    stop_patterns = [
        r"^\s*《?法学引注手册》?\s*编写说明\s*$",
        r"^\s*附录",
        r"^\s*后记",
        r"^\s*参考文献\s*$",
        r"^\s*索引\s*$",
    ]
    for line_number in range(start_line + 1, len(lines) + 1):
        line = lines[line_number - 1].strip()
        if any(re.search(pattern, line) for pattern in stop_patterns):
            return max(start_line, line_number - 1)
    return len(lines)


def build_rule_index(markdown: str) -> tuple[dict[str, Any], str, list[str]]:
    lines = markdown.splitlines()
    toc_titles, last_toc_line = extract_toc_titles(lines)
    min_body_line = last_toc_line + 20 if len(toc_titles) >= 80 else 0
    candidates = find_heading_candidates(lines, min_body_line)
    chosen, missing, warnings = choose_headings(candidates, toc_titles)

    by_number = {item.rule_number: item for item in chosen}
    rules: list[dict[str, Any]] = []
    for rule_number in range(1, 151):
        item = by_number.get(rule_number)
        if not item:
            continue
        next_item = by_number.get(rule_number + 1)
        if next_item:
            end_line = next_item.line_number - 1
        else:
            end_line = find_last_rule_end(lines, item.line_number)
        raw_text = "\n".join(lines[item.line_number - 1 : end_line]).strip()
        rules.append(
            {
                "rule_number": rule_number,
                "title": item.title,
                "category": category_for(rule_number),
                "text": raw_text,
                "raw_start_line": item.line_number,
                "raw_end_line": end_line,
            }
        )

    index = {
        "metadata": {
            "source": str(RAW_REL),
            "generated_by": "scripts/build_reference_data.py",
            "toc_titles_detected": len(toc_titles),
        },
        "count": len(rules),
        "missing_rule_numbers": missing,
        "rules": rules,
    }
    if len(toc_titles) < 120:
        warnings.append(
            f"only detected {len(toc_titles)} TOC rule titles; verify heading extraction carefully"
        )
    return index, render_rule_index_md(index), warnings


def render_rule_index_md(index: dict[str, Any]) -> str:
    lines = [
        "# Handbook Rule Index",
        "",
        "Source: `references/handbook_raw.md`",
        f"Rules extracted: {index['count']}",
        f"Missing rule numbers: {index['missing_rule_numbers']}",
        "",
        "Use this as the full traceable index before relying on simplified templates.",
        "",
    ]
    rules = index["rules"]
    for category, _ in CATEGORY_RANGES:
        category_rules = [rule for rule in rules if rule["category"] == category]
        if not category_rules:
            continue
        lines.extend([f"## {category}", ""])
        for rule in category_rules:
            lines.extend(
                [
                    f"### 第{rule['rule_number']}条 {rule['title']}",
                    f"Lines: {rule['raw_start_line']}-{rule['raw_end_line']}",
                    "",
                    rule["text"],
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def render_structured(index: dict[str, Any]) -> str:
    lines = [
        "# Citation Handbook Structured Digest",
        "",
        "Generated locally from the user's own handbook PDF.",
        "Verify unclear OCR passages against the original PDF before relying on them.",
        "",
    ]
    rules = index["rules"]
    for category, _ in CATEGORY_RANGES:
        category_rules = [rule for rule in rules if rule["category"] == category]
        if not category_rules:
            continue
        lines.extend([f"## {category}", ""])
        for rule in category_rules:
            lines.extend(
                [
                    f"### Rule {rule['rule_number']}: {rule['title']}",
                    "",
                    rule["text"],
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def basic_citation_rules() -> dict[str, Any]:
    lookup = {
        "author": "查原文署名、论文首页或图书版权页。",
        "title": "查原文标题页、论文首页或数据库元数据。",
        "publisher": "查图书版权页。",
        "year": "查版权页、论文首页或数据库元数据。",
        "page": "查纸书页码或论文原始页码。",
        "journal": "查论文首页、页眉页脚或数据库元数据。",
        "issue": "查论文首页、期刊封面或数据库元数据。",
        "court": "查裁判文书页首。",
        "docket_number": "查裁判文书页首案号。",
        "document_number": "查规范性文件首页、发布页或数据库元数据。",
        "url": "查网页地址栏或数据库原文链接。",
        "access_date": "用实际访问日期。",
        "article_text": "查官方法条文本或 PKULaw 法条页。",
    }

    def spec(
        label: str,
        required: list[str],
        optional: list[str],
        template: str,
        anchors: list[str],
    ) -> dict[str, Any]:
        return {
            "label": label,
            "required": required,
            "optional": optional,
            "template": template,
            "anchors": anchors,
            "lookup": lookup,
            "lookup_guidance": lookup,
        }

    return {
        "metadata": {
            "generated_by": "scripts/build_reference_data.py",
            "basis": "public safe templates plus locally generated handbook anchors",
            "warning": "Verify final edge cases against the locally obtained handbook PDF.",
        },
        "types": {
            "chinese_book": spec(
                "中文著作",
                ["author", "title", "publisher", "year"],
                ["editor_role", "edition", "page"],
                "{author}：《{title}》，{publisher}{year}年版{page_part}。",
                ["第25条", "第27-49条"],
            ),
            "translated_book": spec(
                "译著",
                ["country", "author", "title", "translator", "publisher", "year"],
                ["edition", "page"],
                "[{country}]{author}：《{title}》，{translator}译，{publisher}{year}年版{page_part}。",
                ["第25条", "第30条", "第38条"],
            ),
            "journal_article": spec(
                "中文期刊论文",
                ["author", "title", "journal", "year", "issue"],
                ["page"],
                "{author}：《{title}》，载《{journal}》{year}年第{issue}期{page_part}。",
                ["第25条", "第42-45条"],
            ),
            "collection_article": spec(
                "文集文章",
                ["author", "title", "editor", "book_title", "publisher", "year"],
                ["volume", "page"],
                "{author}：《{title}》，载{editor}主编：《{book_title}》{volume_part}，{publisher}{year}年版{page_part}。",
                ["第25条", "第40条"],
            ),
            "newspaper_article": spec(
                "报纸文章",
                ["author", "title", "newspaper", "date", "page_or_edition"],
                [],
                "{author}：《{title}》，载《{newspaper}》{date}，{page_or_edition}。",
                ["第25条", "第46条"],
            ),
            "statute": spec(
                "法律法规条文",
                ["law_name", "article"],
                ["paragraph", "item", "article_text"],
                "《{law_name}》{article}{paragraph_part}{item_part}。",
                ["第66-72条"],
            ),
            "normative_document": spec(
                "规范性文件",
                ["document_title", "document_number"],
                ["publish_date"],
                "《{document_title}》（{document_number}）。",
                ["第73-80条"],
            ),
            "judicial_case": spec(
                "司法案例",
                ["case_name", "court", "docket_number", "document_type"],
                ["source"],
                "{case_name}，{court}{docket_number}{document_type}。",
                ["第87-91条"],
            ),
            "online_source": spec(
                "网络文献",
                ["author", "title", "site_or_platform", "url"],
                ["publish_date", "access_date"],
                "{author_part}《{title}》，载{site_or_platform}{publish_date_part}，{url}，{access_date}访问。",
                ["第50-58条"],
            ),
            "thesis": spec(
                "学位论文",
                ["author", "title", "school", "year", "degree_type"],
                ["page"],
                "{author}：《{title}》，{school}{year}年{degree_type}学位论文{page_part}。",
                ["第65条"],
            ),
            "conference_paper": spec(
                "会议论文",
                ["author", "title", "conference"],
                ["date", "place", "page"],
                "{author}：《{title}》，{conference}{date_part}{page_part}。",
                ["第64条"],
            ),
            "english_article": spec(
                "英文文献",
                ["author", "title"],
                ["journal", "year", "pinpoint"],
                "{author}, {title_italic}{pinpoint_part}({year}).",
                ["第95-115条"],
            ),
        },
        "repeat_citation": {
            "chinese": "Use 同前注〔X〕 with a pinpoint when needed.",
            "foreign": "Verify repeat-citation form against the relevant language section.",
        },
    }


def ensure_can_write(root: Path, force: bool, targets: list[Path]) -> None:
    existing = [rel for rel in targets if (root / rel).exists()]
    if existing and not force:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(
            "Refusing to overwrite existing local reference data without --force:\n"
            f"{formatted}\n"
            "Rerun with --force after backing up anything you want to keep."
        )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_validation(root: Path, skip_audit: bool, skip_self_test: bool) -> int:
    if not skip_audit:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "audit_reference_data.py"), "--root", str(root)],
            check=False,
            text=True,
        )
        if result.returncode != 0:
            return result.returncode
    if not skip_self_test:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "self_test.py")],
            check=False,
            text=True,
            cwd=str(root),
        )
        if result.returncode != 0:
            return result.returncode
    return 0


def ai_contract(root: Path) -> str:
    return f"""# Local Citation Handbook Reference Data Contract

Use this only with a legally obtained local copy of the same edition.

Input PDF:
`{root / PDF_REL}`

Required outputs:
- `{root / RAW_REL}`
- `{root / STRUCTURED_REL}`
- `{root / RULE_INDEX_JSON_REL}`
- `{root / RULE_INDEX_MD_REL}`
- `{root / CITATION_RULES_REL}`

Rules:
1. Do not guess unclear OCR text. Mark it as `[待核: OCR]`.
2. `handbook_rule_index.json` must contain exactly 150 rules.
3. Rule numbers must be exactly 1 through 150, with no gaps or duplicates.
4. Every rule object must contain:
   - `rule_number`
   - `title`
   - `category`
   - `text`
   - `raw_start_line`
   - `raw_end_line`
5. Use these category ranges exactly:
   - 1-24: `general_rules`
   - 25-49: `print_publications`
   - 50-58: `online_and_media`
   - 59-65: `unpublished_conference_thesis_archive`
   - 66-86: `legal_and_official_documents`
   - 87-91: `judicial_cases`
   - 92-94: `statistics`
   - 95-115: `english_and_foreign_general`
   - 116-122: `french_sources`
   - 123-128: `german_sources`
   - 129-134: `italian_and_roman_law_sources`
   - 135-142: `russian_sources`
   - 143-150: `japanese_sources`
6. `citation_rules.json` must contain a `types` object. Each common type should
   include `required`, `optional`, `template`, `anchors`, and lookup guidance.
7. After generation, run:

```bash
python3 skills/legal-citation-comprehensive/scripts/audit_reference_data.py
python3 skills/legal-citation-comprehensive/scripts/handbook_lookup.py --rule 1
python3 skills/legal-citation-comprehensive/scripts/self_test.py
```

If the audit reports ERRORS or the self-test does not print ALL TESTS PASSED,
repair the local reference data before claiming full handbook coverage.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build local legal-citation handbook reference data from a searchable PDF."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Skill root or repository root")
    parser.add_argument("--pdf", type=Path, help="Path to the legally obtained handbook PDF")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated reference files")
    parser.add_argument("--use-existing-raw", action="store_true", help="Build from references/handbook_raw.md")
    parser.add_argument("--extract-only", action="store_true", help="Only extract PDF text to handbook_raw.md")
    parser.add_argument("--skip-audit", action="store_true", help="Do not run audit_reference_data.py")
    parser.add_argument("--skip-self-test", action="store_true", help="Do not run self_test.py")
    parser.add_argument("--min-searchable-chars", type=int, default=20_000)
    parser.add_argument("--print-ai-contract", action="store_true", help="Print the strict local generation contract")
    args = parser.parse_args()

    root = resolve_skill_root(args.root)
    if args.print_ai_contract:
        print(ai_contract(root))
        return 0

    pdf_path = (args.pdf or (root / PDF_REL)).expanduser().resolve()
    raw_path = root / RAW_REL

    if args.use_existing_raw:
        if not raw_path.exists():
            raise SystemExit(f"Missing existing raw file: {raw_path}")
        markdown = raw_path.read_text(encoding="utf-8")
    else:
        if not pdf_path.exists():
            raise SystemExit(
                f"Missing handbook PDF: {pdf_path}\n"
                f"Place it at {root / PDF_REL} or pass --pdf /path/to/file.pdf"
            )
        ensure_can_write(root, args.force, [RAW_REL])
        text, method, errors = extract_pdf_text(pdf_path)
        if not text.strip():
            raise SystemExit("Could not extract text from PDF:\n" + "\n".join(errors))
        assert_searchable(text, args.min_searchable_chars)
        markdown = pdf_text_to_markdown(text)
        write_text(raw_path, markdown)
        print(f"WROTE {RAW_REL} using {method}", flush=True)

    if args.extract_only:
        return 0

    ensure_can_write(root, args.force, [rel for rel in EXPECTED_OUTPUTS if rel != RAW_REL])

    index, index_md, warnings = build_rule_index(markdown)
    if index["missing_rule_numbers"]:
        print("Rule extraction is incomplete; use this contract to repair with an AI:", flush=True)
        print(ai_contract(root))
        raise SystemExit(f"Missing rule numbers: {index['missing_rule_numbers']}")

    write_json(root / RULE_INDEX_JSON_REL, index)
    write_text(root / RULE_INDEX_MD_REL, index_md)
    write_text(root / STRUCTURED_REL, render_structured(index))
    write_json(root / CITATION_RULES_REL, basic_citation_rules())

    print(f"WROTE {RULE_INDEX_JSON_REL}", flush=True)
    print(f"WROTE {RULE_INDEX_MD_REL}", flush=True)
    print(f"WROTE {STRUCTURED_REL}", flush=True)
    print(f"WROTE {CITATION_RULES_REL}", flush=True)
    for warning in warnings:
        print(f"WARNING {warning}", flush=True)

    return run_validation(root, args.skip_audit, args.skip_self_test)


if __name__ == "__main__":
    raise SystemExit(main())
