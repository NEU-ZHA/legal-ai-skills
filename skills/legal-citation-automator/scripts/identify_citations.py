#!/usr/bin/env python3
"""
识别并分类法律文档中的引用

功能：
1. 扫描Word文档，识别可能需要引用的句子
2. 对引用进行分类（法律条文、司法解释、学术文献、案例等）
3. 提取引用的关键信息

用法：
python identify_citations.py <docx_file> [--output json|text]
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple
import zipfile
from xml.etree import ElementTree as ET


class CitationIdentifier:
    """引用识别器"""
    
    # 引用模式定义
    CITATION_PATTERNS = {
        # 法律条文
        'statute': [
            r'《([^》]+)》第(\d+)条',
            r'根据([^\s，。]+)第(\d+)条',
            r'([^\s，。]+)第(\d+)条规定',
            r'依照([^\s，。]+)第(\d+)条',
        ],
        
        # 司法解释
        'judicial_interpretation': [
            r'《([^》]+)》.*解释',
            r'最高人民法院关于(.+?)的解释',
            r'法释〔(\d+)〕(\d+)号',
        ],
        
        # 学术文献
        'academic': [
            r'([^\s，。]+)教授认为',
            r'([^\s，。]+)先生指出',
            r'([^\s，。]+)学者主张',
            r'参见([^\s，。]+)',
            r'详见([^\s，。]+)',
        ],
        
        # 案例
        'case': [
            r'(\d{4})年(\d+)月(\d+)日.*判决',
            r'(〔\d{4}〕\d+)号判决',
            r'指导案例第(\d+)号',
        ],
        
        # 行政法规
        'regulation': [
            r'《([^》]+)》.*条例',
            r'《([^》]+)》.*办法',
            r'《([^》]+)》.*规定',
        ],
        
        # 国际条约
        'treaty': [
            r'《([^》]+)》公约',
            r'《([^》]+)》条约',
            r'《([^》]+)》协定',
        ],
    }
    
    # 引用类型的中文名称
    CITATION_TYPES = {
        'statute': '法律条文',
        'judicial_interpretation': '司法解释',
        'academic': '学术文献',
        'case': '司法案例',
        'regulation': '行政法规',
        'treaty': '国际条约',
    }
    
    def __init__(self):
        self.citations = []
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """从docx文件中提取纯文本"""
        text_parts = []
        
        with zipfile.ZipFile(docx_path, 'r') as docx:
            xml_content = docx.read('word/document.xml')
        
        tree = ET.fromstring(xml_content)
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        
        for paragraph in tree.findall('.//w:p', namespaces):
            paragraph_text = []
            for text in paragraph.findall('.//w:t', namespaces):
                if text.text:
                    paragraph_text.append(text.text)
            if paragraph_text:
                text_parts.append(''.join(paragraph_text))
        
        return '\n'.join(text_parts)
    
    def identify_citations(self, text: str) -> List[Dict]:
        """识别文本中的所有引用"""
        citations = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for citation_type, patterns in self.CITATION_PATTERNS.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        citation = {
                            'type': citation_type,
                            'type_cn': self.CITATION_TYPES[citation_type],
                            'text': match.group(0),
                            'groups': match.groups(),
                            'line_number': line_num,
                            'start': match.start(),
                            'end': match.end(),
                            'context': line[max(0, match.start()-20):match.end()+20]
                        }
                        citations.append(citation)
        
        return citations
    
    def remove_duplicates(self, citations: List[Dict]) -> List[Dict]:
        """去除重复的引用"""
        seen = set()
        unique_citations = []
        
        for citation in citations:
            key = (citation['type'], citation['text'])
            if key not in seen:
                seen.add(key)
                unique_citations.append(citation)
        
        return unique_citations
    
    def analyze_document(self, docx_path: str) -> Dict:
        """分析文档并返回引用信息"""
        print(f"正在分析文档: {docx_path}")
        
        # 提取文本
        text = self.extract_text_from_docx(docx_path)
        print(f"提取到 {len(text)} 个字符")
        
        # 识别引用
        citations = self.identify_citations(text)
        print(f"初步识别到 {len(citations)} 个引用")
        
        # 去重
        citations = self.remove_duplicates(citations)
        print(f"去重后剩余 {len(citations)} 个引用")
        
        # 按类型分组
        grouped = {}
        for citation in citations:
            citation_type = citation['type']
            if citation_type not in grouped:
                grouped[citation_type] = []
            grouped[citation_type].append(citation)
        
        return {
            'total_count': len(citations),
            'by_type': {k: len(v) for k, v in grouped.items()},
            'citations': citations,
            'grouped_citations': grouped
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python identify_citations.py <docx文件> [--output json|text]")
        print("\n示例:")
        print("  python identify_citations.py homework.docx")
        print("  python identify_citations.py homework.docx --output json")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    output_format = 'text'
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]
    
    identifier = CitationIdentifier()
    result = identifier.analyze_document(docx_path)
    
    if output_format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "="*60)
        print("引用识别结果")
        print("="*60)
        print(f"\n总计发现 {result['total_count']} 个可能的引用")
        print("\n按类型统计:")
        for citation_type, count in result['by_type'].items():
            type_name = CitationIdentifier.CITATION_TYPES[citation_type]
            print(f"  - {type_name}: {count}个")
        
        print("\n详细引用列表:")
        print("-"*60)
        
        for citation_type, citations in result['grouped_citations'].items():
            type_name = CitationIdentifier.CITATION_TYPES[citation_type]
            print(f"\n【{type_name}】")
            for i, citation in enumerate(citations, 1):
                print(f"{i}. {citation['text']}")
                print(f"   位置: 第{citation['line_number']}行")
                print(f"   上下文: ...{citation['context']}...")


if __name__ == "__main__":
    main()
