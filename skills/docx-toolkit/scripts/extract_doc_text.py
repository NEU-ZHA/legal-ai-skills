#!/usr/bin/env python3
"""Extract text from legacy .doc files using olefile.

Usage: python3 extract_doc_text.py <doc_file> [output.txt]

Reads the WordDocument OLE stream and extracts Unicode text.
Requires: pip3 install olefile
"""
import sys
import olefile

def extract_doc_text(doc_path, output_path=None):
    ole = olefile.OleFileIO(doc_path)
    
    # Try WordDocument stream first, then 1Table/0Table
    text = ""
    if ole.exists('WordDocument'):
        stream = ole.openstream('WordDocument')
        raw = stream.read()
        # Try UTF-16LE decoding (standard for .doc)
        try:
            text = raw.decode('utf-16-le', errors='ignore')
        except:
            text = raw.decode('cp1252', errors='ignore')
        
        # Clean up: remove control chars but keep newlines
        cleaned = []
        for ch in text:
            if ch in ('\n', '\r', '\t') or (ord(ch) >= 32):
                cleaned.append(ch)
        text = ''.join(cleaned)
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {3,}', ' ', text)
    
    ole.close()
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Extracted {len(text)} chars from {doc_path}")
        print(f"Output: {output_path}")
    else:
        print(text[:5000])  # Preview first 5000 chars
    
    return text

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <doc_file> [output.txt]")
        sys.exit(1)
    
    doc_file = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    extract_doc_text(doc_file, output)
