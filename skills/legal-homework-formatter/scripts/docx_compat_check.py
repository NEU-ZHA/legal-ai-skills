#!/usr/bin/env python3
"""
Check a .docx for Word/WPS footnote compatibility.

This is intentionally conservative. It catches the failure mode that often
causes one editor to open a document while the other shows broken or blank
footnotes: mismatched footnote IDs, missing footnotes.xml relationships, and
mismatched footnote IDs or nonstandard separator structures.

Usage:
    python docx_compat_check.py path/to/document.docx
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


def read_member(zf: zipfile.ZipFile, name: str) -> str:
    try:
        return zf.read(name).decode("utf-8")
    except KeyError:
        return ""


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python docx_compat_check.py <document.docx>")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"ZIP integrity failed at member: {bad}")

            names = set(zf.namelist())
            document = read_member(zf, "word/document.xml")
            footnotes = read_member(zf, "word/footnotes.xml")
            rels = read_member(zf, "word/_rels/document.xml.rels")
            content_types = read_member(zf, "[Content_Types].xml")

            refs = re.findall(r"<w:footnoteReference[^>]*w:id=\"(-?\d+)\"", document)
            fn_defs = re.findall(r"<w:footnote\b[^>]*w:id=\"(-?\d+)\"", footnotes)
            fn_types = {
                m.group(2): m.group(1)
                for m in re.finditer(
                    r"<w:footnote\b[^>]*w:type=\"([^\"]+)\"[^>]*w:id=\"(-?\d+)\"",
                    footnotes,
                )
            }

            if refs and "word/footnotes.xml" not in names:
                errors.append("document.xml has footnoteReference but word/footnotes.xml is missing")

            if refs and "footnotes" not in rels:
                warnings.append("document.xml.rels does not visibly reference footnotes.xml")

            if refs and "/word/footnotes.xml" not in content_types:
                warnings.append("[Content_Types].xml does not visibly override /word/footnotes.xml")

            for xml_name, xml_text in (("document.xml", document), ("settings.xml", read_member(zf, "word/settings.xml"))):
                if "numRestart" in xml_text and "eachPage" in xml_text:
                    warnings.append(
                        f"{xml_name} contains w:numRestart=eachPage; footnotes will restart numbering on each page"
                    )

            missing = sorted(set(refs) - set(fn_defs), key=int)
            if missing:
                errors.append(f"footnoteReference IDs missing from footnotes.xml: {', '.join(missing)}")

            unused = sorted((set(fn_defs) - {"-1", "0"}) - set(refs), key=int)
            if unused:
                warnings.append(f"footnote definitions not referenced by document.xml: {', '.join(unused)}")

            for reserved in ("-1", "0"):
                if reserved not in fn_defs:
                    warnings.append(f"standard separator footnote id {reserved} is missing")

            # ID 1 is valid in the course reference template. IDs 2/3 are not
            # inherently illegal OOXML, but in this user's workflow they often
            # indicate legacy AI-generated footnote/separator conflicts.
            for suspicious in ("2", "3"):
                if suspicious in fn_defs and suspicious not in fn_types:
                    warnings.append(
                        f"regular footnote uses low ID {suspicious}; verify it is not a legacy separator conflict"
                    )

            for fid in refs:
                pattern = rf"<w:footnote\b[^>]*w:id=\"{re.escape(fid)}\"[\s\S]*?</w:footnote>"
                block = re.search(pattern, footnotes)
                if not block:
                    continue
                text = block.group(0)
                if 'w:pStyle w:val="a7"' not in text and "w:pStyle w:val='a7'" not in text:
                    warnings.append(f"footnote {fid} does not use paragraph style a7")
                if 'w:rStyle w:val="ab"' not in text and "w:rStyle w:val='ab'" not in text:
                    warnings.append(f"footnote {fid} does not use footnote reference style ab")

            print(f"Checked: {path}")
            print(f"footnote references: {', '.join(refs) if refs else '(none)'}")
            print(f"footnote definitions: {', '.join(fn_defs) if fn_defs else '(none)'}")

    except zipfile.BadZipFile:
        errors.append("not a valid zip/docx file")

    if warnings:
        print("\nWARNINGS:")
        for item in warnings:
            print(f"- {item}")

    if errors:
        print("\nERRORS:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("\nOK: no blocking Word/WPS footnote compatibility errors found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
