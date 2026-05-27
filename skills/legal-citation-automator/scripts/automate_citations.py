#!/usr/bin/env python3
"""
完整的法律引用自动化工作流

功能：
1. 识别文档中的引用
2. 查找引注手册中的对应格式
3. 自动添加脚注到文档

用法：
python automate_citations.py <docx文件> <引注手册PDF> [--output 输出文件]
"""

import sys
import json
import os
from pathlib import Path

# 导入其他脚本的功能
from identify_citations import CitationIdentifier
from parse_citation_handbook import CitationHandbookParser
from add_footnotes import FootnoteAutomator


def main():
    if len(sys.argv) < 3:
        print("="*60)
        print("法律引用自动化工具")
        print("="*60)
        print("\n用法:")
        print("  python automate_citations.py <Word文档> <引注手册PDF> [--output 输出文件]")
        print("\n参数说明:")
        print("  <Word文档>       需要添加引用的Word文档(.docx)")
        print("  <引注手册PDF>    法学引注手册PDF文件")
        print("  --output         可选，指定输出文件名")
        print("\n示例:")
        print("  python automate_citations.py homework.docx handbook.pdf")
        print("  python automate_citations.py homework.docx handbook.pdf --output result.docx")
        print("\n工作流程:")
        print("  1. 扫描Word文档，识别需要引用的内容")
        print("  2. 解析引注手册，提取各类引用格式")
        print("  3. 根据引用类型匹配对应格式")
        print("  4. 自动生成脚注并添加到文档")
        print("="*60)
        sys.exit(1)
    
    docx_path = sys.argv[1]
    handbook_path = sys.argv[2]
    output_path = None
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    print("\n" + "="*60)
    print("法律引用自动化工作流")
    print("="*60)
    
    # 步骤1：识别引用
    print("\n【步骤1】识别文档中的引用")
    print("-"*60)
    identifier = CitationIdentifier()
    citation_result = identifier.analyze_document(docx_path)
    
    citations = citation_result['citations']
    if not citations:
        print("\n⚠️  未发现需要添加引用的内容")
        sys.exit(0)
    
    # 保存识别结果
    temp_citations_file = "/tmp/citations_temp.json"
    with open(temp_citations_file, 'w', encoding='utf-8') as f:
        json.dump(citation_result, f, ensure_ascii=False, indent=2)
    print(f"识别结果已保存: {temp_citations_file}")
    
    # 步骤2：解析引注手册
    print("\n【步骤2】解析引注手册")
    print("-"*60)
    parser = CitationHandbookParser()
    parser.extract_from_pdf(handbook_path)
    parser.find_section_boundaries()
    formats = parser.extract_citation_formats()
    
    # 保存解析结果
    temp_handbook_file = "/tmp/handbook_parsed.json"
    parser.export_to_json(temp_handbook_file)
    
    # 步骤3：匹配引用类型和格式
    print("\n【步骤3】匹配引用类型和格式")
    print("-"*60)
    
    matched_formats = {}
    for citation_type in citation_result['by_type'].keys():
        if citation_type in formats:
            matched_formats[citation_type] = formats[citation_type]
            print(f"✓ {citation_type}: 找到 {len(formats[citation_type].get('examples', []))} 个格式示例")
        else:
            print(f"✗ {citation_type}: 未找到对应格式")
    
    # 步骤4：添加脚注
    print("\n【步骤4】添加脚注到文档")
    print("-"*60)
    
    automator = FootnoteAutomator()
    automator.load_citation_formats({'citation_formats': formats})
    
    result_path = automator.add_footnotes_to_docx(docx_path, citations, output_path)
    
    if result_path:
        print("\n" + "="*60)
        print("✅ 处理完成！")
        print("="*60)
        print(f"\n输出文件: {result_path}")
        print(f"引用统计:")
        for citation_type, count in citation_result['by_type'].items():
            type_name = CitationIdentifier.CITATION_TYPES.get(citation_type, citation_type)
            print(f"  - {type_name}: {count}个")
        print(f"\n建议:")
        print("  1. 用Word打开文档检查脚注格式")
        print("  2. 验证引用信息的准确性")
        print("  3. 手动调整格式不符合要求的部分")
    else:
        print("\n❌ 处理失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
