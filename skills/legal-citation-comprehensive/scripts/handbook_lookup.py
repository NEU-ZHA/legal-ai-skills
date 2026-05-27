#!/usr/bin/env python3
"""Search the full indexed Law Journal Citation Handbook rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
INDEX_PATH = SCRIPT_DIR.parent / "references" / "handbook_rule_index.json"


def load_index() -> list[dict]:
    if not INDEX_PATH.exists():
        raise SystemExit(
            "Missing optional reference file: references/handbook_rule_index.json\n"
            "This public package does not redistribute third-party handbook OCR/index "
            "data. Add a locally licensed rule index before using handbook lookup."
        )
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return data["rules"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", help="Keyword to search, e.g. 白皮书, 香港法律, 再次引用")
    parser.add_argument("--rule", type=int, help="Show one rule number")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rules = load_index()
    if args.rule:
        results = [r for r in rules if r["rule_number"] == args.rule]
    else:
        results = rules
        if args.category:
            results = [r for r in results if r["category"] == args.category]
        if args.query:
            q = args.query.lower()
            results = [
                r for r in results
                if q in r["title"].lower() or q in r["text"].lower() or q in r["category"].lower()
            ]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    for r in results:
        text = r["text"]
        if len(text) > 1200:
            text = text[:1200] + " ..."
        print(f"第{r['rule_number']}条 {r['title']}")
        print(f"category: {r['category']} lines: {r['raw_start_line']}-{r['raw_end_line']}")
        print(text)
        print()

    if not results:
        print("No matching handbook rules found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
