#!/usr/bin/env python3
"""
CarbonSense AI Logo PNG Converter
Converts SVG logo files to PNG format in multiple sizes
Requires: pip install cairosvg pillow
"""

import os
import sys
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    import io
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install cairosvg pillow")
    sys.exit(1)

def svg_to_png(svg_file, output_file, width=None, height=None, dpi=96):
    """Convert SVG to PNG with specified dimensions"""
    try:
        # Read SVG file
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            dpi=dpi
        )
        
        # Save PNG file
        with open(output_file, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ Created: {output_file} ({width}x{height}px)")
        return True
        
    except Exception as e:
        print(f"❌ Error converting {svg_file}: {e}")
        return False

def main():
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Define SVG files and their PNG variants
    conversions = [
        # Main logo conversions
        {
            'svg': 'logo.svg',
            'outputs': [
                ('logo-240x60.png', 240, 60),
                ('logo-480x120.png', 480, 120),
                ('logo-720x180.png', 720, 180),
                ('logo-1200x300.png', 1200, 300)  # High DPI for print
            ]
        },
        # Icon conversions
        {
            'svg': 'logo-icon.svg',
            'outputs': [
                ('icon-16x16.png', 16, 16),
                ('icon-32x32.png', 32, 32),
                ('icon-48x48.png', 48, 48),
                ('icon-64x64.png', 64, 64),
                ('icon-128x128.png', 128, 128),
                ('icon-256x256.png', 256, 256),
                ('icon-512x512.png', 512, 512)
            ]
        }
    ]
    
    print("🎨 CarbonSense AI Logo PNG Converter")
    print("=" * 50)
    
    success_count = 0
    total_count = 0
    
    for conversion in conversions:
        svg_file = current_dir / conversion['svg']
        
        if not svg_file.exists():
            print(f"⚠️  SVG file not found: {svg_file}")
            continue
        
        print(f"\n📁 Converting {conversion['svg']}:")
        
        for output_name, width, height in conversion['outputs']:
            output_file = current_dir / output_name
            total_count += 1
            
            if svg_to_png(svg_file, output_file, width, height):
                success_count += 1
    
    # Create favicon.ico from 32x32 PNG
    favicon_png = current_dir / 'icon-32x32.png'
    if favicon_png.exists():
        try:
            img = Image.open(favicon_png)
            favicon_ico = current_dir / 'favicon.ico'
            img.save(favicon_ico, format='ICO', sizes=[(32, 32)])
            print(f"✅ Created: favicon.ico")
            success_count += 1
            total_count += 1
        except Exception as e:
            print(f"❌ Error creating favicon.ico: {e}")
    
    print(f"\n🎯 Summary: {success_count}/{total_count} files created successfully")
    
    if success_count > 0:
        print("\n📋 Created PNG files:")
        for png_file in current_dir.glob('*.png'):
            print(f"   • {png_file.name}")
        
        print("\n💡 Usage recommendations:")
        print("   • logo-240x60.png - Website headers")
        print("   • logo-480x120.png - Large displays")
        print("   • logo-1200x300.png - Print materials")
        print("   • icon-32x32.png - Favicons")
        print("   • icon-128x128.png - App icons")
        print("   • icon-512x512.png - High-res app icons")

if __name__ == "__main__":
    main()
