#!/usr/bin/env python3
"""
Legal TOA Formatter - 批量格式化法律文书 Table of Authorities 条目

将所有TOA条目统一修改为点号填充对齐格式。
"""

import sys
import os
import shutil
import zipfile
import re
import tempfile
from pathlib import Path

def fix_toa_format(input_path: str, output_path: str) -> dict:
    """
    修复 TOA 条目的点号填充格式

    Args:
        input_path: 输入 docx 文件路径
        output_path: 输出 docx 文件路径

    Returns:
        dict: 处理统计信息
    """
    stats = {
        "total_paragraphs": 0,
        "toa_entries_found": 0,
        "entries_fixed": 0,
        "entries_unchanged": 0
    }

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="toa_fix_")

    try:
        # 解包 docx
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # 读取 document.xml
        doc_xml_path = Path(temp_dir) / "word" / "document.xml"
        if not doc_xml_path.exists():
            raise FileNotFoundError("未找到 word/document.xml")

        with open(doc_xml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找所有段落
        # 目标：包含 <w:tab/> 但没有正确的 w:leader="dot" 的条目

        # 正确的 tabs 模板
        correct_tabs = '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9016"/></w:tabs>'

        # 统计段落数
        all_paragraphs = re.findall(r'<w:p[^>]*>.*?</w:p>', content, re.DOTALL)
        stats["total_paragraphs"] = len(all_paragraphs)

        # 找出包含制表符的段落（潜在 TOA 条目）
        tab_pattern = re.compile(r'<w:p[^>]*>.*?<w:tab/>.*?</w:p>', re.DOTALL)
        toa_candidates = tab_pattern.findall(content)

        stats["toa_entries_found"] = len(toa_candidates)

        # 处理每个潜在 TOA 条目
        for candidate in toa_candidates:
            # 检查是否已有正确的 dot leader
            has_dot_leader = re.search(r'<w:tabs>.*?w:leader="dot".*?</w:tabs>', candidate, re.DOTALL)

            if not has_dot_leader:
                # 需要修复：添加/修改 tabs 定义

                # 检查是否有任何 tabs 定义
                has_any_tabs = re.search(r'<w:tabs>.*?</w:tabs>', candidate, re.DOTALL)

                if has_any_tabs:
                    # 修改现有的 tabs 定义为 dot leader
                    fixed_candidate = re.sub(
                        r'<w:tabs>.*?</w:tabs>',
                        correct_tabs,
                        candidate,
                        flags=re.DOTALL
                    )
                else:
                    # 需要添加新的 tabs 定义
                    # 在 </w:pPr> 前插入
                    fixed_candidate = candidate.replace(
                        '</w:pPr>',
                        f'{correct_tabs}</w:pPr>'
                    )

                # 替换原文
                content = content.replace(candidate, fixed_candidate, 1)
                stats["entries_fixed"] += 1
            else:
                stats["entries_unchanged"] += 1

        # 写回 document.xml
        with open(doc_xml_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 重新打包为 docx
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == '.DS_Store':
                        continue
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

    return stats


def main():
    if len(sys.argv) < 3:
        print("用法: python3 fix_toa_format.py <input.docx> <output.docx>")
        print("示例: python3 fix_toa_format.py input.docx output.docx")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(input_path):
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    print(f"正在处理: {input_path}")
    print(f"输出到: {output_path}")

    try:
        stats = fix_toa_format(input_path, output_path)
        print("\n处理完成!")
        print(f"  - 总段落数: {stats['total_paragraphs']}")
        print(f"  - TOA 条目数: {stats['toa_entries_found']}")
        print(f"  - 已修复: {stats['entries_fixed']}")
        print(f"  - 保持不变: {stats['entries_unchanged']}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
