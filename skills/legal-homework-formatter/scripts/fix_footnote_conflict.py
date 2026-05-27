#!/usr/bin/env python3
"""
修复Word文档中脚注ID与分隔符ID冲突的问题

问题说明：
- 课程参考模板的标准结构是：分隔符ID为 -1 和 0，普通脚注可从 1 开始
- 但部分旧脚本或其他AI生成的docx会误用低ID区间，甚至把分隔符/普通脚注都放在2、3附近
- 一旦 document.xml 中的 footnoteReference 与 footnotes.xml 中的定义错位，WPS和Word可能显示不一致，常见表现是脚注不全、空白或编号错乱

解决方案：
- 不把"ID 1"视为错误；它是模板中的合法普通脚注ID
- 对来源不明、已经混乱的docx，将普通脚注尽量迁移到4+区间，作为保守兼容补丁
- 更推荐先运行 docx_compat_check.py 判断是否真的存在ID不匹配或低ID冲突风险
"""

import sys
import os
import re
import zipfile
import shutil
from pathlib import Path


def fix_footnote_ids(docx_path):
    """
    修复docx文件中的脚注ID冲突
    
    Args:
        docx_path: docx文件的路径
    
    Returns:
        bool: 是否成功修复
    """
    docx_path = Path(docx_path)
    if not docx_path.exists():
        print(f"错误：文件不存在 {docx_path}")
        return False
    
    # 创建临时目录
    temp_dir = Path(f"/tmp/fix_footnote_{os.getpid()}")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    try:
        # 解压docx
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 修改document.xml中的脚注引用
        document_path = temp_dir / "word" / "document.xml"
        if not document_path.exists():
            print("错误：未找到document.xml")
            return False
        
        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到所有脚注引用
        matches = list(re.finditer(r'<w:footnoteReference w:id="(\d+)"\s*/>', content))
        print(f"找到 {len(matches)} 个脚注引用")
        
        # 从后往前替换
        for match in reversed(matches):
            old_id = int(match.group(1))
            
            # ID映射：0->0, 1->1, 2->4, 3->5, 4->6, 5->7, 6->8, 7->9, 8->10
            if old_id in [0, 1]:
                new_id = old_id
            elif 2 <= old_id <= 8:
                new_id = old_id + 2
            else:
                new_id = old_id
            
            if new_id != old_id:
                new_text = f'<w:footnoteReference w:id="{new_id}"/>'
                content = content[:match.start()] + new_text + content[match.end():]
                print(f"修改脚注引用ID: {old_id} -> {new_id}")
        
        # 保存修改后的document.xml
        with open(document_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 修改footnotes.xml中的脚注定义
        footnotes_path = temp_dir / "word" / "footnotes.xml"
        if not footnotes_path.exists():
            print("警告：未找到footnotes.xml，跳过脚注定义修改")
        else:
            with open(footnotes_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 从后往前替换，避免重复替换
            for old_id, new_id in [(8, 10), (7, 9), (6, 8), (5, 7), (4, 6), (3, 5), (2, 4)]:
                content = re.sub(
                    f'<w:footnote w:id="{old_id}">',
                    f'<w:footnote w:id="{new_id}">',
                    content
                )
                print(f"修改脚注定义ID: {old_id} -> {new_id}")
            
            # 保存修改后的footnotes.xml
            with open(footnotes_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 重新打包docx
        output_path = docx_path.parent / f"{docx_path.stem}_修复版{docx_path.suffix}"
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"\n✅ 修复成功！")
        print(f"输出文件：{output_path}")
        
        return True
        
    except Exception as e:
        print(f"错误：{e}")
        return False
    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python fix_footnote_conflict.py <docx文件路径>")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    success = fix_footnote_ids(docx_path)
    sys.exit(0 if success else 1)
