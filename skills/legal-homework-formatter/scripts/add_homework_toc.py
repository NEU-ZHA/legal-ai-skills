#!/usr/bin/env python3
"""Insert a Word-compatible Chinese legal homework TOC into a DOCX.

This helper is intentionally conservative:
- It uses clean ordinary TOC field paragraphs, not a copied SDT content control.
- It removes updateFields to avoid Word's "update fields?" prompt.
- It detects headings by both Word style and Chinese numbering text.
- It preserves footnotes unless the input document already changes them.
"""

from __future__ import annotations

import argparse
import re
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
NS = {"w": W_NS}

STANDARD_NSMAP = {
    "w": W_NS,
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "mc": MC_NS,
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "w10": "urn:schemas-microsoft-com:office:word",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16sdtdh": "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
}


PPR_ORDER = [
    "pStyle",
    "keepNext",
    "keepLines",
    "pageBreakBefore",
    "framePr",
    "widowControl",
    "numPr",
    "suppressLineNumbers",
    "pBdr",
    "shd",
    "tabs",
    "suppressAutoHyphens",
    "kinsoku",
    "wordWrap",
    "overflowPunct",
    "topLinePunct",
    "autoSpaceDE",
    "autoSpaceDN",
    "bidi",
    "adjustRightInd",
    "snapToGrid",
    "spacing",
    "ind",
    "contextualSpacing",
    "mirrorIndents",
    "suppressOverlap",
    "jc",
    "textDirection",
    "textAlignment",
    "textboxTightWrap",
    "outlineLvl",
    "divId",
    "cnfStyle",
    "rPr",
    "sectPr",
    "pPrChange",
]
PPR_POS = {name: index for index, name in enumerate(PPR_ORDER)}

RPR_ORDER = [
    "rStyle",
    "rFonts",
    "b",
    "bCs",
    "i",
    "iCs",
    "caps",
    "smallCaps",
    "strike",
    "dstrike",
    "outline",
    "shadow",
    "emboss",
    "imprint",
    "noProof",
    "snapToGrid",
    "vanish",
    "webHidden",
    "color",
    "spacing",
    "w",
    "kern",
    "position",
    "sz",
    "szCs",
    "highlight",
    "u",
    "effect",
    "bdr",
    "shd",
    "fitText",
    "vertAlign",
    "rtl",
    "cs",
    "em",
    "lang",
    "eastAsianLayout",
    "specVanish",
    "oMath",
    "rPrChange",
]
RPR_POS = {name: index for index, name in enumerate(RPR_ORDER)}


LEVEL_PATTERNS = {
    "1": re.compile(r"^[一二三四五六七八九十]+、\S"),
    "2": re.compile(r"^（[一二三四五六七八九十]+）\S"),
    "3": re.compile(r"^\d{1,2}[.．]\s*\S"),
}

TOC_STYLE_ALIASES = {
    "TOC10": {"toc 标题1", "toc heading 1", "toc title", "目录标题"},
    "TOC1": {"toc 1", "目录 1"},
    "TOC2": {"toc 2", "目录 2"},
    "TOC3": {"toc 3", "目录 3"},
}

TOC_STYLE_DISPLAY_NAMES = {
    "TOC10": "Homework TOC Title",
    "TOC1": "Homework TOC 1",
    "TOC2": "Homework TOC 2",
    "TOC3": "Homework TOC 3",
}


@dataclass
class Heading:
    level: str
    text: str
    paragraph: etree._Element
    reason: str


def qn(local: str) -> str:
    return f"{{{W_NS}}}{local}"


def el(tag: str, attrs: dict[str, str] | None = None, text: str | None = None):
    node = etree.Element(qn(tag), attrs or {})
    if text is not None:
        node.text = text
    return node


def p_text(p: etree._Element) -> str:
    return "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()


def get_p_style(p: etree._Element) -> str | None:
    node = p.find("w:pPr/w:pStyle", NS)
    return node.get(qn("val")) if node is not None else None


def set_outline_level(p: etree._Element, value: str) -> None:
    """Set a direct outline level without replacing the paragraph's style."""
    p_pr = p.find("w:pPr", NS)
    if p_pr is None:
        p_pr = el("pPr")
        p.insert(0, p_pr)
    outline = p_pr.find("w:outlineLvl", NS)
    if outline is None:
        outline = el("outlineLvl", {qn("val"): value})
        insert_before_first(p_pr, outline, {
            "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"
        })
    else:
        outline.set(qn("val"), value)


def suppress_inherited_numbering(p: etree._Element) -> None:
    """Prevent a manual heading prefix from stacking with style numbering."""
    p_pr = p.find("w:pPr", NS)
    if p_pr is None:
        p_pr = el("pPr")
        p.insert(0, p_pr)
    num_pr = p_pr.find("w:numPr", NS)
    if num_pr is None:
        num_pr = el("numPr")
        insert_before_first(p_pr, num_pr, {
            "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
            "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
            "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
            "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
            "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId",
            "cnfStyle", "rPr", "sectPr", "pPrChange",
        })
    else:
        for child in list(num_pr):
            num_pr.remove(child)
    num_pr.append(el("numId", {qn("val"): "0"}))


def text_run(text: str, *, black: bool = False):
    r = el("r")
    if black:
        r_pr = el("rPr")
        r_pr.append(el("color", {qn("val"): "000000"}))
        r.append(r_pr)
    r.append(el("t", {f"{{{XML_NS}}}space": "preserve"}, text))
    return r


def field_run(field_type: str):
    r = el("r")
    r.append(el("fldChar", {qn("fldCharType"): field_type}))
    return r


def instr_run(text: str):
    r = el("r")
    r.append(el("instrText", {f"{{{XML_NS}}}space": "preserve"}, text))
    return r


def styled_p(style_id: str, text: str = "", include_spacing: bool = True):
    p = el("p")
    p_pr = el("pPr")
    p_pr.append(el("pStyle", {qn("val"): style_id}))
    if include_spacing:
        p_pr.append(el("spacing", {qn("after"): "156"}))
    p.append(p_pr)
    if text:
        p.append(text_run(text))
    return p


def insert_before_first(p_pr: etree._Element, child: etree._Element, later_names: set[str]) -> None:
    for index, existing in enumerate(list(p_pr)):
        if etree.QName(existing).localname in later_names:
            p_pr.insert(index, child)
            return
    p_pr.append(child)


def assert_ppr_order(document: etree._Element) -> None:
    for p_pr in document.xpath("//w:pPr", namespaces=NS):
        names = [etree.QName(child).localname for child in p_pr]
        known = [name for name in names if name in PPR_POS]
        for left, right in zip(known, known[1:]):
            if PPR_POS[left] > PPR_POS[right]:
                text = ""
                parent = p_pr.getparent()
                if parent is not None:
                    text = p_text(parent)[:60]
                raise ValueError(f"Invalid w:pPr child order near '{text}': {left} before {right}")


def normalize_root_namespaces(root: etree._Element) -> etree._Element:
    # Some DOCX files are serialized with prefixes like ns1/ns2 while
    # mc:Ignorable still references w14/w15/wp14. Word treats those undefined
    # ignorable prefixes as repair-worthy, so recreate roots with stable prefixes.
    nsmap = dict(STANDARD_NSMAP)
    for prefix, uri in root.nsmap.items():
        if prefix is None or re.fullmatch(r"ns\d+", prefix):
            continue
        nsmap.setdefault(prefix, uri)

    new_root = etree.Element(root.tag, nsmap=nsmap)
    for key, value in root.attrib.items():
        new_root.set(key, value)
    new_root.text = root.text
    new_root.tail = root.tail
    for child in list(root):
        root.remove(child)
        new_root.append(child)
    return new_root


def reorder_ppr_children(root: etree._Element) -> bool:
    changed = False
    for p_pr in root.xpath("//w:pPr", namespaces=NS):
        children = list(p_pr)
        if len(children) < 2:
            continue

        def sort_key(item: tuple[int, etree._Element]) -> tuple[int, int]:
            index, child = item
            name = etree.QName(child).localname
            namespace = etree.QName(child).namespace
            if namespace == W_NS and name in PPR_POS:
                return (PPR_POS[name], index)
            if namespace == W_NS:
                return (800, index)
            return (900, index)

        ordered = [child for _, child in sorted(enumerate(children), key=sort_key)]
        if ordered == children:
            continue
        for child in children:
            p_pr.remove(child)
        for child in ordered:
            p_pr.append(child)
        changed = True
    return changed


def reorder_rpr_children(root: etree._Element) -> bool:
    changed = False
    for r_pr in root.xpath("//w:rPr", namespaces=NS):
        children = list(r_pr)
        if len(children) < 2:
            continue

        def sort_key(item: tuple[int, etree._Element]) -> tuple[int, int]:
            index, child = item
            name = etree.QName(child).localname
            namespace = etree.QName(child).namespace
            if namespace == W_NS and name in RPR_POS:
                return (RPR_POS[name], index)
            if namespace == W_NS:
                return (800, index)
            return (900, index)

        ordered = [child for _, child in sorted(enumerate(children), key=sort_key)]
        if ordered == children:
            continue
        for child in children:
            r_pr.remove(child)
        for child in ordered:
            r_pr.append(child)
        changed = True
    return changed


def serialize_xml(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def normalize_ooxml_part(path: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_bytes()
    root = etree.fromstring(original)
    root = normalize_root_namespaces(root)
    reorder_ppr_children(root)
    reorder_rpr_children(root)
    rendered = serialize_xml(root)
    if rendered == original:
        return False
    path.write_bytes(rendered)
    return True


def toc_title_p():
    p = styled_p("TOC10")
    p_pr = p.find("w:pPr", NS)
    insert_before_first(
        p_pr,
        el("jc", {qn("val"): "center"}),
        {
            "textDirection",
            "textAlignment",
            "textboxTightWrap",
            "outlineLvl",
            "divId",
            "cnfStyle",
            "rPr",
            "sectPr",
            "pPrChange",
        },
    )
    r_pr = el("rPr")
    r_pr.append(
        el(
            "rFonts",
            {
                qn("ascii"): "宋体",
                qn("eastAsia"): "宋体",
                qn("hAnsi"): "宋体",
            },
        )
    )
    r_pr.append(el("color", {qn("val"): "000000"}))
    r_pr.append(el("sz", {qn("val"): "28"}))
    r_pr.append(el("szCs", {qn("val"): "28"}))
    r = el("r")
    r.append(r_pr)
    r.append(el("t", text="目录"))
    p.append(r)
    return p


def toc_entry(style_id: str, title: str, page_hint: str):
    p = styled_p(style_id, include_spacing=False)
    p_pr = p.find("w:pPr", NS)
    if p_pr is None:
        p_pr = el("pPr")
        p.insert(0, p_pr)
    tabs = p_pr.find("w:tabs", NS)
    if tabs is None:
        tabs = el("tabs")
        insert_before_first(
            p_pr,
            tabs,
            {
                "suppressAutoHyphens",
                "kinsoku",
                "wordWrap",
                "overflowPunct",
                "topLinePunct",
                "autoSpaceDE",
                "autoSpaceDN",
                "bidi",
                "adjustRightInd",
                "snapToGrid",
                "spacing",
                "ind",
                "contextualSpacing",
                "mirrorIndents",
                "suppressOverlap",
                "jc",
                "textDirection",
                "textAlignment",
                "textboxTightWrap",
                "outlineLvl",
                "divId",
                "cnfStyle",
                "rPr",
                "sectPr",
                "pPrChange",
            },
        )
    for tab in list(tabs.findall("w:tab", NS)):
        tabs.remove(tab)
    tabs.append(el("tab", {qn("val"): "right", qn("leader"): "dot", qn("pos"): "8296"}))
    if style_id in {"TOC2", "TOC3"} and p_pr.find("w:ind", NS) is None:
        left = "420" if style_id == "TOC2" else "840"
        left_chars = "200" if style_id == "TOC2" else "400"
        insert_before_first(
            p_pr,
            el("ind", {qn("leftChars"): left_chars, qn("left"): left}),
            {
                "contextualSpacing",
                "mirrorIndents",
                "suppressOverlap",
                "jc",
                "textDirection",
                "textAlignment",
                "textboxTightWrap",
                "outlineLvl",
                "divId",
                "cnfStyle",
                "rPr",
                "sectPr",
                "pPrChange",
            },
        )
    p.append(text_run(title, black=True))
    tab_run = el("r")
    tab_run.append(el("tab"))
    p.append(tab_run)
    p.append(text_run(page_hint, black=True))
    return p


def level_from_text(text: str) -> str | None:
    for level, pattern in LEVEL_PATTERNS.items():
        if pattern.match(text):
            return level
    return None


def paragraph_is_short_heading(text: str) -> bool:
    if not text or len(text) > 80:
        return False
    sentence_marks = "。！？；："
    return not any(mark in text for mark in sentence_marks)


def effective_outline_level(p: etree._Element, styles: etree._Element) -> str | None:
    direct = p.find("w:pPr/w:outlineLvl", NS)
    if direct is not None:
        return direct.get(qn("val"))
    style_id = get_p_style(p)
    if not style_id:
        return None
    values = styles.xpath(
        f'//w:style[@w:styleId="{style_id}"]/w:pPr/w:outlineLvl/@w:val',
        namespaces=NS,
    )
    return values[0] if values else None


def paragraph_style_name(p: etree._Element, styles: etree._Element) -> str:
    style_id = get_p_style(p)
    if not style_id:
        return ""
    values = styles.xpath(
        '//w:style[@w:styleId=$style_id]/w:name/@w:val',
        namespaces=NS,
        style_id=style_id,
    )
    return values[0].strip() if values else ""


def has_heading_style_signal(
    p: etree._Element, styles: etree._Element, outline_level: str | None
) -> bool:
    """Require evidence beyond a short numbered prefix before mutating a paragraph."""
    if outline_level in {"0", "1", "2"}:
        return True
    name = paragraph_style_name(p, styles).casefold()
    return "标题" in name or bool(re.search(r"\b(?:heading|title|step)\b", name))


def collect_and_repair_headings(
    document: etree._Element, styles: etree._Element, max_level: int
) -> tuple[list[Heading], list[str]]:
    headings: list[Heading] = []
    uncertain: list[str] = []

    for p in document.xpath("//w:body/w:p", namespaces=NS):
        text = p_text(p)
        if not text:
            continue
        text_level = level_from_text(text)
        outline_level = effective_outline_level(p, styles)

        is_short_numbered = bool(text_level and paragraph_is_short_heading(text))
        if text_level and int(text_level) <= max_level and is_short_numbered:
            if not has_heading_style_signal(p, styles, outline_level):
                uncertain.append(
                    "numbered short paragraph lacks corroborating heading style/outline; "
                    f"left unchanged: {text[:60]}"
                )
                continue
            suppress_inherited_numbering(p)
            expected_outline = str(int(text_level) - 1)
            if outline_level != expected_outline:
                set_outline_level(p, expected_outline)
            headings.append(Heading(text_level, text, p, "text-detected-outline-ensured"))
        elif text_level:
            continue
        elif outline_level in {"0", "1", "2"}:
            uncertain.append(
                f"outline level {outline_level} but text is not a recognized numbered heading; "
                f"left unchanged: {text[:60]}"
            )

    return headings, uncertain


def add_page_break_before(p: etree._Element) -> None:
    p_pr = p.find("w:pPr", NS)
    if p_pr is None:
        p_pr = el("pPr")
        p.insert(0, p_pr)
    if p_pr.find("w:pageBreakBefore", NS) is None:
        insert_before_first(
            p_pr,
            el("pageBreakBefore"),
            {
                "framePr",
                "widowControl",
                "numPr",
                "suppressLineNumbers",
                "pBdr",
                "shd",
                "tabs",
                "suppressAutoHyphens",
                "kinsoku",
                "wordWrap",
                "overflowPunct",
                "topLinePunct",
                "autoSpaceDE",
                "autoSpaceDN",
                "bidi",
                "adjustRightInd",
                "snapToGrid",
                "spacing",
                "ind",
                "contextualSpacing",
                "mirrorIndents",
                "suppressOverlap",
                "jc",
                "textDirection",
                "textAlignment",
                "textboxTightWrap",
                "outlineLvl",
                "divId",
                "cnfStyle",
                "rPr",
                "sectPr",
                "pPrChange",
            },
        )


def find_toc_style(styles: etree._Element, style_id: str) -> etree._Element | None:
    direct = styles.xpath(f'//w:style[@w:styleId="{style_id}"]', namespaces=NS)
    if direct:
        return direct[0]
    aliases = {name.casefold() for name in TOC_STYLE_ALIASES[style_id]}
    for style in styles.xpath('//w:style[@w:type="paragraph"]', namespaces=NS):
        name = style.xpath("string(w:name/@w:val)", namespaces=NS).strip().casefold()
        if name in aliases:
            return style
    return None


def is_toc_paragraph_style(
    styles: etree._Element | None, style_id: str | None
) -> bool:
    """Recognize canonical and WPS-renumbered TOC paragraph styles."""
    if not style_id:
        return False
    if style_id in TOC_STYLE_ALIASES or style_id.startswith("TOC"):
        return True
    if styles is None:
        return False
    matches = styles.xpath(
        '//w:style[@w:styleId=$style_id]',
        namespaces=NS,
        style_id=style_id,
    )
    if not matches:
        return False
    style_name = matches[0].xpath(
        "string(w:name/@w:val)", namespaces=NS
    ).strip().casefold()
    aliases = {
        alias.casefold()
        for style_aliases in TOC_STYLE_ALIASES.values()
        for alias in style_aliases
    }
    return style_name in aliases


def copy_missing_styles(
    actual_styles: etree._Element, template_styles: etree._Element, max_level: int
) -> bool:
    changed = False
    required = ["TOC10", "TOC1", "TOC2"]
    if max_level == 3:
        required.append("TOC3")
    for style_id in required:
        if actual_styles.xpath(f'//w:style[@w:styleId="{style_id}"]', namespaces=NS):
            continue
        source = find_toc_style(template_styles, style_id)
        if source is None:
            source = find_toc_style(actual_styles, style_id)
        if source is None and style_id == "TOC3":
            source = find_toc_style(template_styles, "TOC2")
            if source is None:
                source = find_toc_style(actual_styles, "TOC2")
        if source is None:
            raise ValueError(f"Template has no usable {style_id} paragraph style")
        clone = etree.fromstring(etree.tostring(source))
        clone.set(qn("styleId"), style_id)
        name = clone.find("w:name", NS)
        if name is None:
            name = el("name", {qn("val"): TOC_STYLE_DISPLAY_NAMES[style_id]})
            clone.insert(0, name)
        else:
            name.set(qn("val"), TOC_STYLE_DISPLAY_NAMES[style_id])
        actual_styles.append(clone)
        changed = True
    return changed


def force_toc_styles_black(styles: etree._Element) -> bool:
    """Prevent TOC titles and entries from inheriting theme/hyperlink blue."""
    changed = False
    for style_id in ["TOC1", "TOC2", "TOC3", "TOC10"]:
        for style in styles.xpath(f'//w:style[@w:styleId="{style_id}"]', namespaces=NS):
            r_pr = style.find("w:rPr", NS)
            if r_pr is None:
                r_pr = el("rPr")
                style.append(r_pr)
                changed = True
            color = r_pr.find("w:color", NS)
            if color is None:
                color = el("color", {qn("val"): "000000"})
                r_pr.append(color)
                changed = True
            if color.get(qn("val")) != "000000":
                color.set(qn("val"), "000000")
                changed = True
            for attr in ("themeColor", "themeTint", "themeShade"):
                key = qn(attr)
                if key in color.attrib:
                    del color.attrib[key]
                    changed = True
    return changed


def remove_auto_update_fields(settings_path: Path) -> bool:
    settings = etree.fromstring(settings_path.read_bytes())
    update_fields = settings.find("w:updateFields", NS)
    if update_fields is not None:
        settings.remove(update_fields)
        settings_path.write_bytes(etree.tostring(settings, xml_declaration=True, encoding="UTF-8", standalone=True))
        return True
    return False


def clean_existing_toc(
    body: etree._Element, styles: etree._Element | None = None
) -> None:
    # Remove existing TOC content controls and simple generated blocks with TOC fields.
    for sdt in list(body.findall("w:sdt", NS)):
        instr = " ".join(sdt.xpath(".//w:instrText/text()", namespaces=NS))
        galleries = sdt.xpath(".//w:docPartGallery/@w:val", namespaces=NS)
        is_toc_gallery = any(value.strip().lower() == "table of contents" for value in galleries)
        if re.search(r"(?:^|\s)TOC\s+\\", instr) or is_toc_gallery:
            body.remove(sdt)

    children = list(body)
    remove_indices: set[int] = set()

    # WPS may put nested HYPERLINK/PAGEREF fields inside every TOC entry. An
    # arbitrary fldChar end therefore does not close the outer TOC field. Find
    # the paragraph containing the actual TOC instruction and follow the net
    # complex-field depth until its matching outer end paragraph.
    toc_start: int | None = None
    for i, node in enumerate(children):
        if node.tag != qn("p"):
            continue
        instr = " ".join(node.xpath(".//w:instrText/text()", namespaces=NS))
        if re.search(r"(?:^|\s)TOC\s+\\", instr):
            toc_start = i
            break

    if toc_start is not None:
        start = toc_start
        if toc_start > 0 and children[toc_start - 1].tag == qn("p"):
            previous = children[toc_start - 1]
            previous_style = get_p_style(previous) or ""
            if p_text(previous) == "目录" or is_toc_paragraph_style(styles, previous_style):
                start = toc_start - 1

        depth = 0
        seen_begin = False
        matched_end: int | None = None
        for i in range(toc_start, len(children)):
            node = children[i]
            if node.tag != qn("p"):
                raise ValueError("Malformed existing TOC: non-paragraph content before matching end")
            instr = " ".join(node.xpath(".//w:instrText/text()", namespaces=NS))
            text = p_text(node)
            style_id = get_p_style(node) or ""
            begins = len(node.xpath(".//w:fldChar[@w:fldCharType='begin']", namespaces=NS))
            ends = len(node.xpath(".//w:fldChar[@w:fldCharType='end']", namespaces=NS))
            is_outer_start = bool(re.search(r"(?:^|\s)TOC\s+\\", instr))
            is_nested_toc_field = "_Toc" in instr and (
                "HYPERLINK" in instr or "PAGEREF" in instr
            )
            is_toc_style = is_toc_paragraph_style(styles, style_id)
            is_empty_field_end = not text and not instr and ends > 0
            if i > toc_start and not (
                is_outer_start or is_nested_toc_field or is_toc_style or is_empty_field_end
            ):
                raise ValueError(
                    "Malformed existing TOC: ordinary document content appears before matching end"
                )
            if begins:
                seen_begin = True
            depth += begins - ends
            if seen_begin and depth == 0:
                matched_end = i
                break
        if not seen_begin or matched_end is None:
            raise ValueError("Malformed existing TOC: outer complex field has no matching end")
        remove_indices.update(range(start, matched_end + 1))

    # Also remove a static/partially broken TOC or orphaned WPS preview entries
    # left by an earlier failed repair. Only inspect instrText here; legitimate
    # body bookmarkStart elements named _Toc... must remain untouched.
    in_static_toc = False
    for i, node in enumerate(children):
        if i in remove_indices or node.tag != qn("p"):
            continue
        instr = " ".join(node.xpath(".//w:instrText/text()", namespaces=NS))
        text = p_text(node)
        style_id = get_p_style(node) or ""
        is_orphan_entry = "_Toc" in instr and ("PAGEREF" in instr or "HYPERLINK" in instr)
        is_toc_piece = (
            text == "目录"
            or is_toc_paragraph_style(styles, style_id)
            or is_orphan_entry
        )
        if is_toc_piece:
            in_static_toc = True
            remove_indices.add(i)
        elif in_static_toc:
            is_empty_outer_end = not text and bool(
                node.xpath(".//w:fldChar[@w:fldCharType='end']", namespaces=NS)
            )
            if is_empty_outer_end:
                remove_indices.add(i)
            break

    for i in sorted(remove_indices, reverse=True):
        body.remove(children[i])


def toc_paragraphs(
    headings: list[Heading], max_level: int, *, hyperlinks: bool = True
) -> list[etree._Element]:
    paragraphs = [toc_title_p()]
    begin = styled_p("TOC1", include_spacing=False)
    begin.append(field_run("begin"))
    instruction = f' TOC \\o "1-{max_level}"'
    if hyperlinks:
        instruction += " \\h"
    instruction += " \\z "
    begin.append(instr_run(instruction))
    begin.append(field_run("separate"))
    paragraphs.append(begin)

    style_to_toc = {"1": "TOC1", "2": "TOC2", "3": "TOC3"}
    for heading in headings:
        paragraphs.append(toc_entry(style_to_toc[heading.level], heading.text, "2"))

    end = styled_p("TOC1", include_spacing=False)
    end.append(field_run("end"))
    paragraphs.append(end)
    return paragraphs


def build(
    input_docx: Path,
    template_docx: Path,
    output_docx: Path,
    max_level: int = 2,
    *,
    hyperlinks: bool = True,
) -> list[str]:
    if max_level not in {2, 3}:
        raise ValueError("max_level must be 2 or 3")
    with tempfile.TemporaryDirectory(prefix="homework_toc_") as tmp_name:
        tmp = Path(tmp_name)
        with zipfile.ZipFile(input_docx) as zin:
            zin.extractall(tmp)
        with zipfile.ZipFile(template_docx) as zin:
            template_styles = etree.fromstring(zin.read("word/styles.xml"))

        document_path = tmp / "word" / "document.xml"
        styles_path = tmp / "word" / "styles.xml"
        settings_path = tmp / "word" / "settings.xml"

        document = etree.fromstring(document_path.read_bytes())
        styles = etree.fromstring(styles_path.read_bytes())
        styles_changed = copy_missing_styles(styles, template_styles, max_level)
        styles_changed = force_toc_styles_black(styles) or styles_changed

        body = document.find("w:body", NS)
        clean_existing_toc(body, styles)
        for paragraph in body.findall("w:p", NS):
            text = p_text(paragraph)
            if not text:
                continue
            if level_from_text(text) is None:
                set_outline_level(paragraph, "9")
            break
        headings, uncertain = collect_and_repair_headings(document, styles, max_level)
        if not headings:
            raise SystemExit("No confident heading paragraphs found for TOC.")

        paragraphs = toc_paragraphs(headings, max_level, hyperlinks=hyperlinks)
        for offset, paragraph in enumerate(paragraphs, start=1):
            body.insert(offset, paragraph)

        first_body_index = 1 + len(paragraphs)
        if len(body) > first_body_index and body[first_body_index].tag == qn("p"):
            add_page_break_before(body[first_body_index])

        document = normalize_root_namespaces(document)
        reorder_ppr_children(document)
        reorder_rpr_children(document)
        assert_ppr_order(document)
        document_path.write_bytes(serialize_xml(document))

        styles = normalize_root_namespaces(styles)
        reorder_ppr_children(styles)
        reorder_rpr_children(styles)
        if styles_changed:
            styles_path.write_bytes(serialize_xml(styles))
        else:
            rendered_styles = serialize_xml(styles)
            if rendered_styles != styles_path.read_bytes():
                styles_path.write_bytes(rendered_styles)
        remove_auto_update_fields(settings_path)

        for relative_part in [
            "word/settings.xml",
            "word/footnotes.xml",
            "word/endnotes.xml",
            "word/header1.xml",
            "word/header2.xml",
            "word/header3.xml",
            "word/footer1.xml",
            "word/footer2.xml",
            "word/footer3.xml",
            "word/footer4.xml",
        ]:
            normalize_ooxml_part(tmp / relative_part)

        if output_docx.exists():
            output_docx.unlink()
        with zipfile.ZipFile(output_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for file_path in sorted(tmp.rglob("*")):
                if file_path.is_file():
                    zout.write(file_path, file_path.relative_to(tmp))
    return uncertain


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_docx", type=Path)
    parser.add_argument("template_docx", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument(
        "--max-level",
        type=int,
        choices=(2, 3),
        default=2,
        help="deepest TOC level to include (default: 2; use 3 only when justified)",
    )
    parser.add_argument(
        "--no-hyperlinks",
        action="store_true",
        help="omit the TOC hyperlink switch if Word/WPS renders updated entries blue",
    )
    args = parser.parse_args()

    uncertain = build(
        args.input_docx,
        args.template_docx,
        args.output_docx,
        max_level=args.max_level,
        hyperlinks=not args.no_hyperlinks,
    )
    print(args.output_docx)
    if uncertain:
        print("需人工确认标题:")
        for item in uncertain:
            print(f"- {item}")


if __name__ == "__main__":
    main()
