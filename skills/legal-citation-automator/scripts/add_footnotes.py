#!/usr/bin/env python3
"""
自动为Word文档添加脚注

功能：
1. 根据识别出的引用，自动生成脚注内容
2. 在Word文档中插入脚注标记
3. 添加脚注文本

用法：
python add_footnotes.py <docx_file> <citations_json> [--output output.docx]
"""

import sys
import json
import re
import os
import zipfile
import shutil
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Dict, List
from datetime import datetime


class FootnoteAutomator:
    """脚注自动化处理器"""
    
    # XML命名空间
    NAMESPACES = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
        'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    }
    
    # 注册命名空间
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)
    
    def __init__(self):
        self.citation_formats = {}
        self.footnote_counter = 0
    
    def load_citation_formats(self, handbook_data: Dict):
        """加载引注手册数据"""
        self.citation_formats = handbook_data.get('citation_formats', {})
    
    def generate_footnote_text(self, citation: Dict) -> str:
        """根据引用类型生成脚注文本"""
        citation_type = citation['type']
        citation_text = citation['text']
        groups = citation.get('groups', [])
        
        # 根据不同类型生成脚注
        if citation_type == 'statute':
            return self._generate_statute_footnote(groups)
        elif citation_type == 'judicial_interpretation':
            return self._generate_interpretation_footnote(groups)
        elif citation_type == 'academic':
            return self._generate_academic_footnote(groups)
        elif citation_type == 'case':
            return self._generate_case_footnote(groups)
        else:
            return f"参见相关文献。"
    
    def _generate_statute_footnote(self, groups: tuple) -> str:
        """生成法律条文脚注"""
        if not groups:
            return "法律条文引用。"
        
        law_name = groups[0] if len(groups) > 0 else "法律"
        
        # 常见法律全称映射
        law_full_names = {
            '民法典': '《中华人民共和国民法典》，2020年5月28日第十三届全国人民代表大会第三次会议通过。',
            '刑法': '《中华人民共和国刑法》，1979年7月1日第五届全国人民代表大会第二次会议通过，2020年12月26日修正。',
            '宪法': '《中华人民共和国宪法》，1982年12月4日第五届全国人民代表大会第五次会议通过，2018年3月11日修正。',
            '民法通则': '《中华人民共和国民法通则》，1986年4月12日第六届全国人民代表大会第四次会议通过。',
            '合同法': '《中华人民共和国合同法》，1999年3月15日第九届全国人民代表大会第二次会议通过。',
        }
        
        # 尝试匹配完整法律名称
        for short_name, full_citation in law_full_names.items():
            if short_name in law_name:
                article = groups[1] if len(groups) > 1 else ""
                if article:
                    return f"{full_citation}"
                return full_citation
        
        return f"《{law_name}》相关条文。"
    
    def _generate_interpretation_footnote(self, groups: tuple) -> str:
        """生成司法解释脚注"""
        if not groups:
            return "司法解释引用。"
        
        interp_name = groups[0] if len(groups) > 0 else ""
        return f"《{interp_name}解释》，最高人民法院发布。"
    
    def _generate_academic_footnote(self, groups: tuple) -> str:
        """生成学术文献脚注"""
        if not groups:
            return "学术文献引用。"
        
        author = groups[0] if len(groups) > 0 else "作者"
        return f"{author}相关著作。"
    
    def _generate_case_footnote(self, groups: tuple) -> str:
        """生成案例脚注"""
        if not groups:
            return "案例引用。"
        
        if len(groups) >= 3:
            year, month, day = groups[0], groups[1], groups[2]
            return f"{year}年{month}月{day}日相关判决。"
        
        return "相关司法案例。"
    
    def add_footnotes_to_docx(self, docx_path: str, citations: List[Dict], output_path: str = None) -> str:
        """为Word文档添加脚注"""
        if output_path is None:
            output_path = docx_path.replace('.docx', '_已添加脚注.docx')
        
        print(f"\n正在处理文档: {docx_path}")
        print(f"输出文件: {output_path}")
        
        # 创建临时目录
        temp_dir = Path(f"/tmp/footnote_automator_{os.getpid()}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        
        try:
            # 解压文档
            with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 读取文档内容
            document_path = temp_dir / "word" / "document.xml"
            tree = ET.parse(document_path)
            root = tree.getroot()
            self._strip_ignorable_attr(root)
            
            # 读取或创建脚注文件
            footnotes_path = temp_dir / "word" / "footnotes.xml"
            if footnotes_path.exists():
                footnotes_tree = ET.parse(footnotes_path)
                footnotes_root = footnotes_tree.getroot()
                self._strip_ignorable_attr(footnotes_root)
            else:
                footnotes_root = self._create_footnotes_xml()
            
            # 获取当前脚注ID。For Word/WPS compatibility, keep separator
            # footnotes at -1/0 and start user footnotes at 4.
            existing_ids = self._get_existing_footnote_ids(footnotes_root)
            content_ids = [i for i in existing_ids if i >= 4]
            next_id = max(content_ids, default=3) + 1
            
            # 为每个引用添加脚注
            added_count = 0
            for citation in citations:
                footnote_text = self.generate_footnote_text(citation)
                if "[待补:" in footnote_text or citation.get("source_status") == "needs_user_input":
                    raise ValueError(f"Refusing to insert incomplete citation: {citation.get('text', '')}")
                footnote_id = next_id
                
                # 添加脚注引用到文档
                if self._insert_footnote_reference(root, citation, footnote_id):
                    # 添加脚注内容
                    self._add_footnote_content(footnotes_root, footnote_id, footnote_text)
                    next_id += 1
                    # 避开 Word/WPS 容易误解的保留区间。
                    if next_id < 4:
                        next_id = 4
                    
                    added_count += 1
                    print(f"  添加脚注 {footnote_id}: {citation['text'][:30]}...")
            
            # 保存修改
            tree.write(document_path, encoding='UTF-8', xml_declaration=True)
            
            footnotes_tree = ET.ElementTree(footnotes_root)
            footnotes_tree.write(footnotes_path, encoding='UTF-8', xml_declaration=True)
            
            # 重新打包
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
            
            print(f"\n✅ 成功添加 {added_count} 个脚注")
            if added_count == 0:
                print("⚠️ 未插入任何脚注。请检查 citations JSON 是否包含可定位的 anchor_text 或位置。")
            return output_path
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 清理临时目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def _create_footnotes_xml(self) -> ET.Element:
        """创建脚注XML文件"""
        W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        root = ET.Element(f'{W}footnotes')
        
        # Word's standard separator IDs are -1 and 0. Using 2/3 for these
        # makes some WPS/Word combinations display blank or mismatched notes.
        separator = ET.SubElement(root, f'{W}footnote')
        separator.set(f'{W}type', 'separator')
        separator.set(f'{W}id', '-1')
        p_sep = ET.SubElement(separator, f'{W}p')
        r_sep = ET.SubElement(p_sep, f'{W}r')
        ET.SubElement(r_sep, f'{W}separator')
        
        continuation = ET.SubElement(root, f'{W}footnote')
        continuation.set(f'{W}type', 'continuationSeparator')
        continuation.set(f'{W}id', '0')
        p_cont = ET.SubElement(continuation, f'{W}p')
        r_cont = ET.SubElement(p_cont, f'{W}r')
        ET.SubElement(r_cont, f'{W}continuationSeparator')
        
        return root
    
    def _get_existing_footnote_ids(self, root: ET.Element) -> List[int]:
        """获取现有的脚注ID"""
        ids = []
        for footnote in root.findall('.//w:footnote', self.NAMESPACES):
            footnote_id = footnote.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
            if footnote_id:
                ids.append(int(footnote_id))
        return ids

    def _strip_ignorable_attr(self, root: ET.Element) -> None:
        """Remove stale mc:Ignorable after ElementTree namespace rewriting.

        ElementTree can drop unused namespace declarations while preserving the
        mc:Ignorable attribute that names those prefixes. WPS often tolerates
        that package, but desktop Word may ask to repair it.
        """
        for attr in list(root.attrib):
            if attr.endswith('}Ignorable'):
                del root.attrib[attr]
    
    def _insert_footnote_reference(self, root: ET.Element, citation: Dict, footnote_id: int) -> bool:
        """在文档中插入脚注引用"""
        # Safety guard: older versions of this helper returned True here even
        # though precise body insertion was not implemented, which could create
        # footnote definitions without visible body references. Do not do that.
        if not citation.get("anchor_text") and not citation.get("location"):
            print(f"  跳过：缺少 anchor_text/location，无法安全插入正文脚注标记: {citation.get('text', '')[:40]}")
            return False

        print("  跳过：当前 add_footnotes.py 仅保留 XML 组装能力；正文定位插入需按具体文档实现。")
        return False
    
    def _add_footnote_content(self, root: ET.Element, footnote_id: int, text: str):
        """添加脚注内容"""
        W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        footnote = ET.SubElement(root, f'{W}footnote')
        footnote.set(f'{W}id', str(footnote_id))
        
        # 添加段落
        p = ET.SubElement(footnote, f'{W}p')
        pPr = ET.SubElement(p, f'{W}pPr')
        pStyle = ET.SubElement(pPr, f'{W}pStyle')
        pStyle.set(f'{W}val', 'a7')
        
        # 添加脚注引用标记
        r1 = ET.SubElement(p, f'{W}r')
        rPr1 = ET.SubElement(r1, f'{W}rPr')
        rStyle = ET.SubElement(rPr1, f'{W}rStyle')
        rStyle.set(f'{W}val', 'ab')
        
        ET.SubElement(r1, f'{W}footnoteRef')
        r_space = ET.SubElement(p, f'{W}r')
        t_space = ET.SubElement(r_space, f'{W}t')
        t_space.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t_space.text = ' '
        
        # 添加脚注文本
        r2 = ET.SubElement(p, f'{W}r')
        rPr2 = ET.SubElement(r2, f'{W}rPr')
        rFonts = ET.SubElement(rPr2, f'{W}rFonts')
        rFonts.set(f'{W}ascii', 'Times New Roman')
        rFonts.set(f'{W}hAnsi', 'Times New Roman')
        rFonts.set(f'{W}eastAsia', '宋体')
        ET.SubElement(rPr2, f'{W}sz').set(f'{W}val', '18')
        ET.SubElement(rPr2, f'{W}szCs').set(f'{W}val', '18')
        t = ET.SubElement(r2, f'{W}t')
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = text


def main():
    if len(sys.argv) < 3:
        print("用法: python add_footnotes.py <docx文件> <引用JSON文件> [--output 输出文件]")
        print("\n示例:")
        print("  python add_footnotes.py homework.docx citations.json")
        print("  python add_footnotes.py homework.docx citations.json --output homework_footnoted.docx")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    citations_path = sys.argv[2]
    output_path = None
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    # 加载引用数据
    with open(citations_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    citations = data.get('citations', [])
    
    # 添加脚注
    automator = FootnoteAutomator()
    result = automator.add_footnotes_to_docx(docx_path, citations, output_path)
    
    if result:
        print(f"\n处理完成！输出文件: {result}")
    else:
        print("\n处理失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
