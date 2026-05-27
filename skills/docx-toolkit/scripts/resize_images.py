#!/usr/bin/env python3
"""Resize images to reduce token consumption for vision analysis.

Usage: python3 resize_images.py <input_dir> [output_dir] [--max-size 1024] [--quality 80]

Resizes all images to max dimension while preserving aspect ratio.
If output_dir is omitted, overwrites in place.
Requires: pip3 install Pillow
"""
import sys
import os
from PIL import Image

def resize_images(input_dir, output_dir=None, max_size=1024, quality=80):
    if output_dir is None:
        output_dir = input_dir
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    saved_bytes = 0
    
    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            continue
        
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)
        
        original_size = os.path.getsize(in_path)
        
        try:
            img = Image.open(in_path)
            
            # Skip if already small enough
            if max(img.size) <= max_size:
                if input_dir != output_dir:
                    img.save(out_path)
                count += 1
                continue
            
            # Resize preserving aspect ratio
            img.thumbnail((max_size, max_size), Image.LANCZOS)
            
            # Save with compression
            if fname.lower().endswith('.png'):
                # Convert PNG to JPEG for better compression (unless transparent)
                if img.mode == 'RGBA':
                    img.save(out_path, optimize=True)
                else:
                    out_path = out_path.rsplit('.', 1)[0] + '.jpg'
                    img = img.convert('RGB')
                    img.save(out_path, 'JPEG', quality=quality)
            else:
                img.save(out_path, 'JPEG', quality=quality)
            
            new_size = os.path.getsize(out_path)
            saved_bytes += original_size - new_size
            count += 1
            
        except Exception as e:
            print(f"  Skip {fname}: {e}")
    
    print(f"Processed: {count} images")
    print(f"Saved: {saved_bytes / 1024 / 1024:.1f} MB ({saved_bytes / max(1, count) / 1024:.0f} KB avg per image)")
    print(f"Output: {output_dir}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input_dir> [output_dir] [--max-size 1024] [--quality 80]")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    
    max_size = 1024
    quality = 80
    
    if '--max-size' in sys.argv:
        idx = sys.argv.index('--max-size')
        max_size = int(sys.argv[idx + 1])
    if '--quality' in sys.argv:
        idx = sys.argv.index('--quality')
        quality = int(sys.argv[idx + 1])
    
    resize_images(input_dir, output_dir, max_size, quality)
