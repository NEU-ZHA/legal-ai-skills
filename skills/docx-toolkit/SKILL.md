---
name: docx-toolkit
description: Extract text, tables, and images from .docx and legacy .doc files. Handles large documents, CJK text, and complex table structures. Includes deduplication and filtering for extracted images.
author: zacjiang
version: 1.0.0
tags: docx, doc, word, extract, text, tables, images, document, office, CJK, chinese
---

# DOCX Toolkit

A complete toolkit for processing Microsoft Word documents (.docx and legacy .doc formats).

## Capabilities

### 1. Text + Table Extraction (.docx)
```bash
python3 {baseDir}/scripts/extract_text.py input.docx output.txt
```
Extracts all paragraphs and tables with structure preserved. Tables are formatted as pipe-delimited rows for easy parsing.

### 2. Text Extraction (Legacy .doc)
```bash
python3 {baseDir}/scripts/extract_doc_text.py input.doc output.txt
```
Handles legacy OLE2 .doc format using olefile. Extracts Unicode text from the WordDocument stream.

### 3. Image Extraction (.docx)
```bash
python3 {baseDir}/scripts/extract_images.py input.docx output_dir/
```
Extracts all embedded images with:
- Automatic deduplication (MD5 hash comparison)
- Size filtering (skips tiny icons <5KB by default)
- Sequential renaming (img_001.png, img_002.jpg, etc.)

### 4. Image Compression
```bash
python3 {baseDir}/scripts/resize_images.py input_dir/ output_dir/ [--max-width 1024]
```
Batch resize/compress images for API processing (saves 50-70% on vision API costs).

## Dependencies

- Python 3.6+
- `python-docx` — for .docx processing
- `olefile` — for legacy .doc processing  
- `Pillow` — for image resizing (optional, only needed for resize script)

Install:
```bash
pip3 install python-docx olefile Pillow
```

## Use Cases

- **Document analysis**: Extract text for AI review/summarization
- **Migration**: Pull content from Word docs into other formats
- **Image audit**: Extract and review all embedded images
- **Cost optimization**: Compress images before sending to vision APIs
- **Batch processing**: Process multiple documents in a pipeline

## Notes

- Large .doc files (>200MB) may require significant RAM for olefile processing
- Image extraction preserves original format (png/jpg/gif/etc.)
- Deduplication catches exact duplicates; near-duplicates still pass through
- CJK (Chinese/Japanese/Korean) text is fully supported in both extractors
