#!/usr/bin/env python3
"""Remove Pandoc/Word heading artifacts from legal homework DOCX files.

Pandoc often writes headings with built-in styles such as Heading1/Heading2
and theme colors. In Word this can survive later font-size changes and render
manual Chinese headings as blue/green text or auto-numbered bullets.
"""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
W = f"{{{W_NS}}}"
MC = f"{{{MC_NS}}}"

ET.register_namespace("w", W_NS)

CHINESE_NUM = "一二三四五六七八九十百千万"
PANDOC_STYLE_RE = re.compile(r"^(Heading[1-6]|Title|Subtitle)$", re.I)


def w_el(name: str) -> str:
    return W + name


def paragraph_text(p: ET.Element) -> str:
    return "".join(t.text or "" for t in p.findall(f".//{w_el('t')}")).strip()


def get_or_add(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.Element(tag)
        parent.insert(0, child)
    return child


def get_style_id(p: ET.Element) -> str | None:
    p_pr = p.find(w_el("pPr"))
    if p_pr is None:
        return None
    p_style = p_pr.find(w_el("pStyle"))
    if p_style is None:
        return None
    return p_style.get(w_el("val"))


def available_style_ids(extract_dir: Path) -> set[str]:
    styles_path = extract_dir / "word" / "styles.xml"
    if not styles_path.exists():
        return set()
    root = ET.parse(styles_path).getroot()
    ids = set()
    for style in root.findall(w_el("style")):
        val = style.get(w_el("styleId"))
        if val:
            ids.add(val)
    return ids


def classify_heading(text: str, style_id: str | None, index: int) -> str | int | None:
    if style_id and style_id.lower() in {"title", "subtitle"}:
        return "title"
    if index == 0 and style_id and PANDOC_STYLE_RE.match(style_id):
        return "title"
    if re.match(rf"^[{CHINESE_NUM}]+、", text):
        return 1
    if re.match(rf"^（[{CHINESE_NUM}]+）", text):
        return 2
    if re.match(r"^\d+[.．、]", text):
        return 3
    if style_id:
        m = re.match(r"Heading([1-6])$", style_id, re.I)
        if m:
            return min(int(m.group(1)), 3)
    return None


def strip_ignorable_attr(root: ET.Element) -> None:
    for attr in list(root.attrib):
        if attr == MC + "Ignorable" or attr.endswith("}Ignorable"):
            del root.attrib[attr]


def remove_children(parent: ET.Element, names: set[str]) -> None:
    for child in list(parent):
        if child.tag in names:
            parent.remove(child)


def set_attr(el: ET.Element, name: str, value: str) -> None:
    el.set(w_el(name), value)


def normalize_paragraph(p: ET.Element, kind: str | int, styles: set[str]) -> bool:
    p_pr = get_or_add(p, w_el("pPr"))
    remove_children(p_pr, {w_el("numPr")})

    p_style = p_pr.find(w_el("pStyle"))
    if p_style is not None:
        current = p_style.get(w_el("val"), "")
        if PANDOC_STYLE_RE.match(current) or current in {"Title", "Subtitle"}:
            p_pr.remove(p_style)
            p_style = None

    if isinstance(kind, int) and str(kind) in styles:
        if p_style is None:
            p_style = ET.SubElement(p_pr, w_el("pStyle"))
        set_attr(p_style, "val", str(kind))
    elif kind == "title" and p_style is not None:
        p_pr.remove(p_style)

    for name in ("spacing", "ind", "jc"):
        existing = p_pr.find(w_el(name))
        if existing is not None:
            p_pr.remove(existing)

    spacing = ET.SubElement(p_pr, w_el("spacing"))
    set_attr(spacing, "after", "156")
    if kind != "title":
        set_attr(spacing, "line", "300")
        set_attr(spacing, "lineRule", "auto")

    ind = ET.SubElement(p_pr, w_el("ind"))
    set_attr(ind, "firstLine", "0" if kind == "title" else "0")
    jc = ET.SubElement(p_pr, w_el("jc"))
    set_attr(jc, "val", "center" if kind == "title" else "left")

    if kind != "title":
        if p_pr.find(w_el("keepNext")) is None:
            ET.SubElement(p_pr, w_el("keepNext"))
        if p_pr.find(w_el("keepLines")) is None:
            ET.SubElement(p_pr, w_el("keepLines"))

    size = {"title": "30", 1: "28", 2: "24", 3: "21"}.get(kind, "21")
    for run in p.findall(w_el("r")):
        r_pr = get_or_add(run, w_el("rPr"))
        remove_children(r_pr, {w_el("color"), w_el("highlight"), w_el("shd"), w_el("sz"), w_el("szCs")})

        r_fonts = r_pr.find(w_el("rFonts"))
        if r_fonts is None:
            r_fonts = ET.SubElement(r_pr, w_el("rFonts"))
        set_attr(r_fonts, "ascii", "Times New Roman")
        set_attr(r_fonts, "hAnsi", "Times New Roman")
        set_attr(r_fonts, "eastAsia", "宋体")

        color = ET.SubElement(r_pr, w_el("color"))
        set_attr(color, "val", "000000")
        ET.SubElement(r_pr, w_el("sz")).set(w_el("val"), size)
        ET.SubElement(r_pr, w_el("szCs")).set(w_el("val"), size)
        if r_pr.find(w_el("b")) is None:
            ET.SubElement(r_pr, w_el("b"))
        if r_pr.find(w_el("bCs")) is None:
            ET.SubElement(r_pr, w_el("bCs"))

    return True


def fix_docx(input_path: Path, output_path: Path) -> int:
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(input_path) as zf:
            zf.extractall(tmp_path)

        document_path = tmp_path / "word" / "document.xml"
        tree = ET.parse(document_path)
        root = tree.getroot()
        strip_ignorable_attr(root)
        styles = available_style_ids(tmp_path)

        changed = 0
        non_empty_index = 0
        for p in root.findall(f".//{w_el('p')}"):
            text = paragraph_text(p)
            if not text:
                continue
            style_id = get_style_id(p)
            kind = classify_heading(text, style_id, non_empty_index)
            non_empty_index += 1
            if kind is not None:
                changed += normalize_paragraph(p, kind, styles)

        tree.write(document_path, encoding="utf-8", xml_declaration=True)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in tmp_path.rglob("*"):
                if item.is_file():
                    zf.write(item, item.relative_to(tmp_path))
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.docx.exists():
        raise SystemExit(f"ERROR: file not found: {args.docx}")
    output = args.output or args.docx.with_name(args.docx.stem + "_heading-fixed.docx")
    changed = fix_docx(args.docx, output)
    print(f"Fixed heading/title paragraphs: {changed}")
    print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
