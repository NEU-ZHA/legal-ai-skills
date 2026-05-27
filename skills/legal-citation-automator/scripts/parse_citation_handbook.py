#!/usr/bin/env python3
"""
解析法学引注手册，提取不同类型引用的格式规则

功能：
1. 从PDF中提取引注手册内容
2. 按引用类型分类存储格式规则
3. 提供查询接口，根据引用类型返回对应格式

用法：
python parse_citation_handbook.py <handbook_pdf> [--output json|markdown]
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List
try:
    import pdfplumber
except ImportError:
    print("错误: 需要安装pdfplumber库")
    print("安装命令: pip install pdfplumber")
    sys.exit(1)


class CitationHandbookParser:
    """引注手册解析器"""
    
    # 引用类型关键词映射
    CITATION_TYPE_KEYWORDS = {
        'statute': ['法律文件', '法律', '第\\d+条', '民法典', '刑法', '宪法'],
        'judicial_interpretation': ['司法解释', '最高人民法院', '法释', '解释'],
        'regulation': ['行政法规', '条例', '办法', '规定', '国务院'],
        'case': ['案例', '判决', '裁定', '指导案例', '裁判文书'],
        'academic': ['著作', '论文', '期刊', '学者', '教授', '博士', '硕士'],
        'treaty': ['国际条约', '公约', '协定', '国际法'],
        'official_document': ['官方文件', '政府文件', '通知', '决定'],
        'internet_source': ['网络资源', '网页', '网站', '电子文献'],
        'foreign_law': ['外国法', '美国', '英国', '德国', '日本'],
        'historical': ['古籍', '史料', '历史文献'],
    }
    
    def __init__(self):
        self.pages = []
        self.sections = {}
        self.citation_formats = {}
    
    def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """从PDF提取内容"""
        print(f"正在解析引注手册: {pdf_path}")
        
        pages_data = []
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"共 {total_pages} 页")
            
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    pages_data.append({
                        'page_number': i,
                        'text': text,
                        'char_count': len(text)
                    })
                
                if i % 20 == 0:
                    print(f"已处理 {i}/{total_pages} 页...")
        
        self.pages = pages_data
        print(f"提取完成，共 {len(pages_data)} 页")
        return pages_data
    
    def find_section_boundaries(self) -> Dict[str, tuple]:
        """查找各个章节的边界"""
        sections = {}
        
        # 常见章节标题模式
        section_patterns = [
            (r'第[一二三四五六七八九十]+部分[^\n]+', 'part'),
            (r'第[一二三四五六七八九十\d]+节[^\n]+', 'section'),
            (r'第\d+条[^\n]+', 'article'),
            (r'[一二三四五六七八九十]+、[^\n]+', 'item'),
        ]
        
        for page_data in self.pages:
            text = page_data['text']
            page_num = page_data['page_number']
            
            for pattern, section_type in section_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    title = match.group(0).strip()
                    if title not in sections:
                        sections[title] = {
                            'type': section_type,
                            'page': page_num,
                            'position': match.start()
                        }
        
        self.sections = sections
        return sections
    
    def extract_citation_formats(self) -> Dict[str, Dict]:
        """提取各类型引用的格式规则"""
        formats = {}
        
        print("\n正在提取引用格式规则...")
        
        for citation_type, keywords in self.CITATION_TYPE_KEYWORDS.items():
            print(f"\n处理类型: {citation_type}")
            
            relevant_pages = []
            for page_data in self.pages:
                text = page_data['text']
                
                # 检查页面是否包含相关关键词
                for keyword in keywords:
                    if re.search(keyword, text):
                        relevant_pages.append(page_data)
                        break
            
            if relevant_pages:
                # 提取格式示例和规则
                format_info = self._extract_format_from_pages(relevant_pages, citation_type)
                if format_info:
                    formats[citation_type] = format_info
                    print(f"  找到 {len(format_info.get('examples', []))} 个格式示例")
        
        self.citation_formats = formats
        return formats
    
    def _extract_format_from_pages(self, pages: List[Dict], citation_type: str) -> Dict:
        """从页面中提取格式信息"""
        format_info = {
            'type': citation_type,
            'rules': [],
            'examples': [],
            'pages': [p['page_number'] for p in pages]
        }
        
        # 查找格式示例的模式
        example_patterns = [
            r'例如[:：][^\n]+',
            r'例\d+[:：][^\n]+',
            r'格式[:：][^\n]+',
            r'参见[^\n]+',
            r'《[^》]+》[^，。\n]*',
        ]
        
        for page_data in pages:
            text = page_data['text']
            
            for pattern in example_patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    example = match.group(0).strip()
                    if len(example) > 10 and len(example) < 200:
                        format_info['examples'].append({
                            'text': example,
                            'page': page_data['page_number']
                        })
        
        # 去重
        seen = set()
        unique_examples = []
        for example in format_info['examples']:
            if example['text'] not in seen:
                seen.add(example['text'])
                unique_examples.append(example)
        format_info['examples'] = unique_examples[:10]  # 最多保留10个示例
        
        return format_info
    
    def get_format_for_type(self, citation_type: str) -> Dict:
        """获取特定类型的引用格式"""
        return self.citation_formats.get(citation_type, {})
    
    def export_to_json(self, output_path: str):
        """导出为JSON格式"""
        data = {
            'citation_formats': self.citation_formats,
            'sections': self.sections,
            'page_count': len(self.pages)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n已导出到: {output_path}")
    
    def export_to_markdown(self, output_path: str):
        """导出为Markdown格式"""
        lines = ["# 法学引注手册格式规则\n"]
        
        for citation_type, format_info in self.citation_formats.items():
            lines.append(f"\n## {citation_type}\n")
            
            if format_info.get('pages'):
                lines.append(f"**页码**: {', '.join(map(str, format_info['pages']))}\n")
            
            if format_info.get('examples'):
                lines.append("\n### 格式示例\n")
                for i, example in enumerate(format_info['examples'], 1):
                    lines.append(f"{i}. {example['text']} (第{example['page']}页)\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
        
        print(f"\n已导出到: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("用法: python parse_citation_handbook.py <引注手册PDF> [--output json|markdown]")
        print("\n示例:")
        print("  python parse_citation_handbook.py handbook.pdf")
        print("  python parse_citation_handbook.py handbook.pdf --output json")
        print("  python parse_citation_handbook.py handbook.pdf --output markdown")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_format = 'json'
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]
    
    parser = CitationHandbookParser()
    parser.extract_from_pdf(pdf_path)
    parser.find_section_boundaries()
    parser.extract_citation_formats()
    
    # 导出
    output_path = pdf_path.replace('.pdf', f'_parsed.{output_format}')
    if output_format == 'json':
        parser.export_to_json(output_path)
    else:
        parser.export_to_markdown(output_path)


if __name__ == "__main__":
    main()
