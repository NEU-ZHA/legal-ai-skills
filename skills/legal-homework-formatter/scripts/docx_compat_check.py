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
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"


def read_member(zf: zipfile.ZipFile, name: str) -> str:
    try:
        return zf.read(name).decode("utf-8")
    except KeyError:
        return ""


def undeclared_ignorable_prefixes(xml_text: str) -> list[str]:
    root_match = re.search(r"<[^!?][^>]*>", xml_text)
    if not root_match:
        return []
    root_tag = root_match.group(0)
    ignorable = re.search(r"(?:[A-Za-z_][\w.-]*:)?Ignorable=\"([^\"]+)\"", root_tag)
    if not ignorable:
        return []
    declared = set(re.findall(r"\sxmlns:([A-Za-z_][\w.-]*)=", root_tag))
    return sorted(set(ignorable.group(1).split()) - declared)


def w_attr(name: str) -> str:
    return f"{W}{name}"


def element_text(node: ET.Element) -> str:
    return "".join(t.text or "" for t in node.findall(f".//{W}t"))


def style_names(styles_xml: str) -> dict[str, str]:
    if not styles_xml:
        return {}
    try:
        root = ET.fromstring(styles_xml.encode("utf-8"))
    except ET.ParseError:
        return {}
    result: dict[str, str] = {}
    for style in root.findall(f".//{W}style"):
        style_id = style.attrib.get(w_attr("styleId"))
        name = style.find(f"{W}name")
        if style_id and name is not None:
            result[style_id] = name.attrib.get(w_attr("val"), "")
    return result


def warn_consecutive_footnote_refs(document_xml: str) -> list[str]:
    """Detect back-to-back footnote references at the same body position."""
    if not document_xml:
        return []
    try:
        root = ET.fromstring(document_xml.encode("utf-8"))
    except ET.ParseError:
        return []

    warnings: list[str] = []
    for para in root.findall(f".//{W}body/{W}p"):
        sequence: list[tuple[str, str]] = []
        for run in para.findall(f"{W}r"):
            refs = [ref.attrib.get(w_attr("id"), "") for ref in run.findall(f".//{W}footnoteReference")]
            text = element_text(run)
            for ref in refs:
                if ref:
                    sequence.append(("ref", ref))
            if text:
                sequence.append(("text", text))

        i = 0
        while i < len(sequence):
            kind, value = sequence[i]
            if kind != "ref":
                i += 1
                continue
            refs = [value]
            j = i + 1
            while j < len(sequence):
                next_kind, next_value = sequence[j]
                if next_kind == "text" and next_value.strip():
                    break
                if next_kind == "ref":
                    refs.append(next_value)
                j += 1
            if len(refs) > 1:
                context = "".join(v for k, v in sequence if k == "text").strip()
                warnings.append(
                    "consecutive footnote references at the same body position "
                    f"({', '.join(refs)}). If they support the same sentence/proposition, "
                    "merge them into one footnote separated by semicolons. Context: "
                    + context[:90]
                )
            i = max(j, i + 1)
    return warnings


def warn_footnote_leading_space(footnotes_xml: str, referenced_ids: set[str]) -> list[str]:
    """Detect footnote text that starts with whitespace after the normal delimiter."""
    if not footnotes_xml:
        return []
    try:
        root = ET.fromstring(footnotes_xml.encode("utf-8"))
    except ET.ParseError:
        return []

    warnings: list[str] = []
    for footnote in root.findall(f".//{W}footnote"):
        fid = footnote.attrib.get(w_attr("id"), "")
        if fid not in referenced_ids:
            continue
        if footnote.attrib.get(w_attr("type")):
            continue
        para = footnote.find(f"{W}p")
        if para is None:
            continue
        seen_ref = False
        delimiter_seen = False
        for run in para.findall(f"{W}r"):
            if run.find(f".//{W}footnoteRef") is not None:
                seen_ref = True
                continue
            if not seen_ref:
                continue
            text = element_text(run)
            if not text:
                continue
            if not text.strip():
                if delimiter_seen or len(text) > 1:
                    warnings.append(f"footnote {fid} has extra whitespace before its text")
                    break
                delimiter_seen = True
                continue
            if text[0].isspace():
                warnings.append(
                    f"footnote {fid} text starts with whitespace; strip footnote_text before insertion"
                )
            break
    return warnings


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
            styles = read_member(zf, "word/styles.xml")
            rels = read_member(zf, "word/_rels/document.xml.rels")
            content_types = read_member(zf, "[Content_Types].xml")
            names_by_style_id = style_names(styles)

            for xml_name in sorted(name for name in names if name.endswith(".xml")):
                xml_text = read_member(zf, xml_name)
                if not xml_text:
                    continue
                try:
                    ET.fromstring(xml_text.encode("utf-8"))
                except ET.ParseError as exc:
                    errors.append(f"{xml_name} is not well-formed XML: {exc}")
                missing_prefixes = undeclared_ignorable_prefixes(xml_text)
                if missing_prefixes:
                    errors.append(
                        f"{xml_name} has mc:Ignorable prefixes without xmlns declarations: "
                        + ", ".join(missing_prefixes)
                    )

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

            warnings.extend(warn_consecutive_footnote_refs(document))
            warnings.extend(warn_footnote_leading_space(footnotes, set(refs)))

            unused = sorted((set(fn_defs) - {"-1", "0"}) - set(refs), key=int)
            if unused:
                warnings.append(f"footnote definitions not referenced by document.xml: {', '.join(unused)}")

            if refs or fn_defs:
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
                    style_match = re.search(r"<w:pStyle[^>]*w:val=\"([^\"]+)\"", text)
                    actual_style = style_match.group(1) if style_match else "(none)"
                    style_name = names_by_style_id.get(actual_style, "")
                    detail = f" (actual: {actual_style}"
                    if style_name:
                        detail += f" / {style_name}"
                    detail += ")"
                    warnings.append(f"footnote {fid} does not use paragraph style a7{detail}")
                if 'w:rStyle w:val="ab"' not in text and "w:rStyle w:val='ab'" not in text:
                    warnings.append(f"footnote {fid} does not use footnote reference style ab")

            pandoc_heading_styles = sorted(set(re.findall(
                r'<w:pStyle[^>]*w:val="(Heading[1-6]|Title|Subtitle)"',
                document,
                flags=re.I,
            )))
            if pandoc_heading_styles:
                warnings.append(
                    "document.xml still contains Pandoc/Word heading styles that can render homework headings blue: "
                    + ", ".join(pandoc_heading_styles)
                )

            if pandoc_heading_styles and "w:themeColor" in document:
                warnings.append(
                    "document.xml contains theme-colored heading runs; run fix_pandoc_heading_artifacts.py "
                    "or clear heading colors before final submission"
                )

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

    if warnings:
        print("\nOK: no blocking Word/WPS compatibility errors found, but warnings require review before final submission.")
    else:
        print("\nOK: no blocking Word/WPS footnote compatibility errors found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
