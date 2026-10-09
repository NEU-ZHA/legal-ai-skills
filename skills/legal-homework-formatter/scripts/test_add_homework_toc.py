#!/usr/bin/env python3
"""Regression tests for the homework TOC OOXML repair helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_homework_toc as toc


def paragraph(
    text: str = "", *, style_id: str | None = None
) -> etree._Element:
    p = toc.el("p")
    if style_id is not None:
        p_pr = toc.el("pPr")
        p_pr.append(toc.el("pStyle", {toc.qn("val"): style_id}))
        p.append(p_pr)
    if text:
        p.append(toc.text_run(text))
    return p


def styles_with_names(items: list[tuple[str, str]]) -> etree._Element:
    styles = toc.el("styles")
    for style_id, name in items:
        style = toc.el(
            "style",
            {toc.qn("type"): "paragraph", toc.qn("styleId"): style_id},
        )
        style.append(toc.el("name", {toc.qn("val"): name}))
        styles.append(style)
    return styles


def body_with(*children: etree._Element) -> etree._Element:
    body = toc.el("body")
    for child in children:
        body.append(child)
    return body


def document_with(*children: etree._Element) -> etree._Element:
    document = toc.el("document")
    document.append(body_with(*children))
    return document


class TocCleanupTests(unittest.TestCase):
    def test_static_wps_numeric_style_ids_are_removed_as_one_block(self) -> None:
        styles = styles_with_names(
            [("19", "TOC 标题1"), ("20", "toc 1"), ("21", "toc 2")]
        )
        body = body_with(
            paragraph("目录", style_id="19"),
            paragraph("一、旧目录项\t2", style_id="20"),
            paragraph("（一）旧目录项\t2", style_id="21"),
            paragraph("一、正文", style_id="7"),
        )

        toc.clean_existing_toc(body, styles)

        self.assertEqual([toc.p_text(node) for node in body], ["一、正文"])

    def test_nested_wps_fields_close_only_at_outer_toc_end(self) -> None:
        title = paragraph("目录", style_id="TOC10")
        first = paragraph(style_id="TOC1")
        first.append(toc.field_run("begin"))
        first.append(toc.instr_run(' TOC \\o "1-2" \\h \\z '))
        first.append(toc.field_run("separate"))
        first.append(toc.field_run("begin"))
        first.append(toc.instr_run(" HYPERLINK \\l _Toc100 "))
        first.append(toc.field_run("end"))
        second = paragraph("（一）旧目录项", style_id="TOC2")
        second.append(toc.field_run("begin"))
        second.append(toc.instr_run(" PAGEREF _Toc101 \\h "))
        second.append(toc.field_run("end"))
        outer_end = paragraph(style_id="TOC1")
        outer_end.append(toc.field_run("end"))
        real_body = paragraph("一、正文", style_id="7")
        real_body.insert(
            0,
            toc.el(
                "bookmarkStart",
                {toc.qn("id"): "1", toc.qn("name"): "_TocRealBody"},
            ),
        )
        body = body_with(title, first, second, outer_end, real_body)

        toc.clean_existing_toc(body, styles_with_names([]))

        self.assertEqual(len(body), 1)
        self.assertEqual(toc.p_text(body[0]), "一、正文")
        self.assertEqual(
            body[0].xpath("string(.//w:bookmarkStart/@w:name)", namespaces=toc.NS),
            "_TocRealBody",
        )

    def test_malformed_outer_field_fails_without_mutating_body(self) -> None:
        start = paragraph(style_id="TOC1")
        start.append(toc.field_run("begin"))
        start.append(toc.instr_run(' TOC \\o "1-2" \\h \\z '))
        body = body_with(start, paragraph("一、正文", style_id="7"))
        before = etree.tostring(body)

        with self.assertRaisesRegex(ValueError, "ordinary document content"):
            toc.clean_existing_toc(body, styles_with_names([]))

        self.assertEqual(etree.tostring(body), before)

    def test_only_real_toc_content_controls_are_removed(self) -> None:
        ordinary = toc.el("sdt")
        ordinary_content = toc.el("sdtContent")
        ordinary_content.append(paragraph("请参见附件目录说明"))
        ordinary.append(ordinary_content)

        real_toc = toc.el("sdt")
        properties = toc.el("sdtPr")
        properties.append(
            toc.el("docPartGallery", {toc.qn("val"): "Table of Contents"})
        )
        real_toc.append(properties)
        real_toc.append(toc.el("sdtContent"))
        body = body_with(ordinary, real_toc, paragraph("一、正文"))

        toc.clean_existing_toc(body, styles_with_names([]))

        self.assertEqual(len(body.findall("w:sdt", toc.NS)), 1)
        self.assertIn("附件目录说明", "".join(body.xpath(".//w:t/text()", namespaces=toc.NS)))


class HeadingRepairTests(unittest.TestCase):
    def test_manual_numbering_suppresses_inherited_numbering_per_paragraph(self) -> None:
        styles = styles_with_names([("17", "Course Heading 1")])
        style = styles.xpath('//w:style[@w:styleId="17"]', namespaces=toc.NS)[0]
        p_pr = toc.el("pPr")
        num_pr = toc.el("numPr")
        num_pr.append(toc.el("ilvl", {toc.qn("val"): "0"}))
        num_pr.append(toc.el("numId", {toc.qn("val"): "9"}))
        p_pr.append(num_pr)
        p_pr.append(toc.el("outlineLvl", {toc.qn("val"): "0"}))
        style.append(p_pr)
        heading = paragraph("一、一级标题", style_id="17")
        document = document_with(heading)

        headings, uncertain = toc.collect_and_repair_headings(document, styles, 2)

        self.assertEqual(uncertain, [])
        self.assertEqual([item.text for item in headings], ["一、一级标题"])
        self.assertEqual(toc.get_p_style(heading), "17")
        self.assertEqual(
            heading.xpath("string(w:pPr/w:numPr/w:numId/@w:val)", namespaces=toc.NS),
            "0",
        )
        self.assertEqual(
            heading.xpath("count(w:pPr/w:numPr/*)", namespaces=toc.NS), 1.0
        )

    def test_default_two_level_collection_does_not_promote_level_three(self) -> None:
        styles = styles_with_names([("31", "Homework Step")])
        heading = paragraph("1. 请求权基础", style_id="31")
        document = document_with(heading)
        before = etree.tostring(heading)

        headings, uncertain = toc.collect_and_repair_headings(document, styles, 2)

        self.assertEqual(headings, [])
        self.assertEqual(uncertain, [])
        self.assertEqual(etree.tostring(heading), before)

    def test_explicit_level_three_accepts_a_corroborating_custom_heading_style(self) -> None:
        styles = styles_with_names([("31", "Homework Step")])
        heading = paragraph("1. 请求权基础", style_id="31")
        document = document_with(heading)

        headings, uncertain = toc.collect_and_repair_headings(document, styles, 3)

        self.assertEqual(uncertain, [])
        self.assertEqual([item.text for item in headings], ["1. 请求权基础"])
        self.assertEqual(toc.get_p_style(heading), "31")
        self.assertEqual(
            heading.xpath("string(w:pPr/w:outlineLvl/@w:val)", namespaces=toc.NS),
            "2",
        )
        self.assertEqual(
            heading.xpath("string(w:pPr/w:numPr/w:numId/@w:val)", namespaces=toc.NS),
            "0",
        )

    def test_short_numbered_body_list_is_reported_and_left_unchanged(self) -> None:
        styles = styles_with_names([("a", "Normal")])
        item = paragraph("1. 甲方应在三日内提交材料", style_id="a")
        document = document_with(item)
        before = etree.tostring(item)

        headings, uncertain = toc.collect_and_repair_headings(document, styles, 3)

        self.assertEqual(headings, [])
        self.assertEqual(len(uncertain), 1)
        self.assertIn("lacks corroborating heading style/outline", uncertain[0])
        self.assertEqual(etree.tostring(item), before)


class TocGenerationTests(unittest.TestCase):
    def test_two_level_nonhyperlinked_field_has_no_u_switch(self) -> None:
        paragraphs = toc.toc_paragraphs([], 2, hyperlinks=False)
        instruction = " ".join(
            text
            for p in paragraphs
            for text in p.xpath(".//w:instrText/text()", namespaces=toc.NS)
        )

        self.assertIn('TOC \\o "1-2" \\z', instruction)
        self.assertNotIn("\\h", instruction)
        self.assertNotIn("\\u", instruction)


if __name__ == "__main__":
    unittest.main()
