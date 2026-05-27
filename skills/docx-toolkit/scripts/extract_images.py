#!/usr/bin/env python3
"""Extract all embedded images from a .docx file WITH paragraph context.

Usage: python3 extract_images.py <docx_file> <output_dir> [--min-size 5000] [--context]

Extracts images via two methods:
1. Paragraph walk: finds images in document order with surrounding text context
2. Media fallback: catches any images missed by paragraph walk

Output:
  - img_001.{jpg|png}, img_002.{jpg|png}, ...
  - image_manifest.json (when --context): maps each image to its context

The manifest enables smart filtering: know which images are certificates,
contracts, test reports etc. WITHOUT using expensive vision AI.

Requires: pip3 install python-docx
"""
import sys
import os
import json
import hashlib
from zipfile import ZipFile
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def get_image_rids(paragraph):
    """Extract image relationship IDs from a paragraph's XML."""
    rids = []
    # Check for w:drawing/a:blip (modern images)
    for blip in paragraph._element.findall('.//' + '{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
        rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        if rid:
            rids.append(rid)
    # Check for w:pict/v:imagedata (legacy images)
    for imagedata in paragraph._element.findall('.//' + '{urn:schemas-microsoft-com:vml}imagedata'):
        rid = imagedata.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        if rid:
            rids.append(rid)
    return rids

def extract_images(docx_path, output_dir, min_size=5000, with_context=False):
    os.makedirs(output_dir, exist_ok=True)
    
    doc = Document(docx_path)
    z = ZipFile(docx_path, 'r')
    
    # Build rId → media path mapping
    rid_to_path = {}
    for rel in doc.part.rels.values():
        if "image" in rel.reltype:
            rid_to_path[rel.rId] = rel.target_ref
    
    seen_hashes = set()
    count = 0
    skipped_small = 0
    skipped_dup = 0
    manifest = []
    extracted_paths = set()  # track which media paths we've extracted
    
    # === Method 1: Paragraph walk (with context) ===
    paragraphs = list(doc.paragraphs)
    
    # Track current section heading
    current_section = ""
    
    for idx, para in enumerate(paragraphs):
        text = para.text.strip()
        
        # Update section heading (detect heading styles or numbered sections)
        if para.style and para.style.name and 'Heading' in para.style.name:
            current_section = text
        elif text and len(text) < 80 and any(text.startswith(p) for p in 
            ['一、','二、','三、','四、','五、','六、','七、','八、','九、','十、',
             '第一','第二','第三','第四','第五','第六','第七','第八','第九','第十',
             '1.','2.','3.','4.','5.','6.','7.','8.','9.',
             '（一）','（二）','（三）','（四）','（五）']):
            current_section = text
        
        # Check for images in this paragraph
        rids = get_image_rids(para)
        if not rids:
            continue
        
        # Get surrounding context
        prev_text = ""
        for back in range(max(0, idx-3), idx):
            t = paragraphs[back].text.strip()
            if t:
                prev_text = t
                break
        
        next_text = ""
        for fwd in range(idx+1, min(len(paragraphs), idx+4)):
            t = paragraphs[fwd].text.strip()
            if t:
                next_text = t
                break
        
        for rid in rids:
            media_path = rid_to_path.get(rid)
            if not media_path:
                continue
            
            # Normalize path
            if not media_path.startswith('word/'):
                full_path = 'word/' + media_path
            else:
                full_path = media_path
            
            try:
                data = z.read(full_path)
            except KeyError:
                try:
                    data = z.read(media_path)
                except KeyError:
                    continue
            
            if len(data) < min_size:
                skipped_small += 1
                continue
            
            h = hashlib.sha256(data).hexdigest()
            if h in seen_hashes:
                skipped_dup += 1
                continue
            seen_hashes.add(h)
            
            # Determine extension
            ext = os.path.splitext(media_path)[1].lower()
            if ext == '.jpeg': ext = '.jpg'
            if ext in ('.emf', '.wmf'):
                skipped_small += 1
                continue
            
            count += 1
            out_name = f"img_{count:03d}{ext}"
            out_path = os.path.join(output_dir, out_name)
            
            with open(out_path, 'wb') as f:
                f.write(data)
            
            extracted_paths.add(full_path)
            extracted_paths.add(media_path)
            
            # Classify by context keywords
            context_combined = f"{current_section} {prev_text} {para.text}".lower()
            category = classify_by_context(context_combined)
            
            entry = {
                'file': out_name,
                'section': current_section,
                'prev_text': prev_text[:100],
                'para_text': para.text.strip()[:100],
                'next_text': next_text[:100],
                'category': category,
                'priority': 'high' if category in ('certificate', 'contract', 'report', 'credential') else 'low',
                'size_kb': round(len(data) / 1024, 1),
            }
            manifest.append(entry)
    
    # === Method 2: Fallback — catch any images not found via paragraphs ===
    for name in sorted(z.namelist()):
        if not name.startswith('word/media/'):
            continue
        if name in extracted_paths:
            continue
        if not any(name.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            continue
        
        data = z.read(name)
        if len(data) < min_size:
            skipped_small += 1
            continue
        
        h = hashlib.sha256(data).hexdigest()
        if h in seen_hashes:
            skipped_dup += 1
            continue
        seen_hashes.add(h)
        
        ext = os.path.splitext(name)[1].lower()
        if ext == '.jpeg': ext = '.jpg'
        if ext in ('.emf', '.wmf'):
            continue
        
        count += 1
        out_name = f"img_{count:03d}{ext}"
        out_path = os.path.join(output_dir, out_name)
        
        with open(out_path, 'wb') as f:
            f.write(data)
        
        manifest.append({
            'file': out_name,
            'section': '(no context - fallback extraction)',
            'prev_text': '',
            'para_text': '',
            'next_text': '',
            'category': 'unknown',
            'priority': 'medium',
            'size_kb': round(len(data) / 1024, 1),
        })
    
    z.close()
    
    # Save manifest
    if with_context:
        manifest_path = os.path.join(output_dir, 'image_manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"Manifest: {manifest_path}")
    
    # Print summary
    from collections import Counter
    cats = Counter(m['category'] for m in manifest)
    pris = Counter(m['priority'] for m in manifest)
    
    print(f"\nExtracted: {count} images")
    print(f"Skipped (small <{min_size}B): {skipped_small}")
    print(f"Skipped (duplicate): {skipped_dup}")
    print(f"\nBy category:")
    for cat, cnt in cats.most_common():
        print(f"  {cat}: {cnt}")
    print(f"\nBy priority:")
    for pri, cnt in pris.most_common():
        print(f"  {pri}: {cnt}")
    print(f"\nHigh priority (need review): {pris.get('high', 0)}")
    print(f"Low priority (can skip): {pris.get('low', 0)}")
    
    return count

def classify_by_context(text):
    """Classify image category based on surrounding paragraph text."""
    text = text.lower()
    
    # High priority categories (need vision review)
    if any(kw in text for kw in ['检验报告', '检测报告', '试验报告', '测试报告', '质检']):
        return 'report'
    if any(kw in text for kw in ['合同', '协议书', '购销', '采购', '中标通知']):
        return 'contract'
    if any(kw in text for kw in ['证书', '认证', '执照', '许可证', '资质', '备案']):
        return 'certificate'
    if any(kw in text for kw in ['承诺函', '授权书', '授权委托', '声明函', '保证函']):
        return 'credential'
    if any(kw in text for kw in ['身份证', '职称', '资格证', '上岗证', '学历']):
        return 'personnel'
    if any(kw in text for kw in ['信用中国', '企业信用', '失信', '经营异常', '公示系统']):
        return 'credit_check'
    
    # Low priority categories (usually skip)
    if any(kw in text for kw in ['产品', '型号', '参数', '规格', '外形', '整车', '宣传']):
        return 'product'
    if any(kw in text for kw in ['车间', '厂房', '厂区', '生产线', '仓库', '航拍']):
        return 'factory'
    if any(kw in text for kw in ['设备', '仪器', '工具', '量具', '检测设备']):
        return 'equipment'
    if any(kw in text for kw in ['标准', '规范', '工艺', '作业指导', '流程图', '架构图']):
        return 'standard'
    if any(kw in text for kw in ['培训', '锦旗', '好评', '满意度', '用户反馈', '证明函']):
        return 'testimonial'
    if any(kw in text for kw in ['专利', '著作权', '软件登记', '商标']):
        return 'ip_patent'
    if any(kw in text for kw in ['新闻', '报道', '央视', '期刊', '杂志']):
        return 'media'
    if any(kw in text for kw in ['荣誉', '奖牌', '名牌', '驰名', '奖项']):
        return 'honor'
    
    return 'unknown'

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <docx_file> <output_dir> [--min-size 5000] [--context]")
        sys.exit(1)
    
    docx_file = sys.argv[1]
    output_dir = sys.argv[2]
    min_size = 5000
    with_context = '--context' in sys.argv
    
    if '--min-size' in sys.argv:
        idx = sys.argv.index('--min-size')
        min_size = int(sys.argv[idx + 1])
    
    extract_images(docx_file, output_dir, min_size, with_context)
