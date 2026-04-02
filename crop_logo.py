#!/usr/bin/env python
"""
Crop and process the CourseHub logo
Removes white background and crops to content
"""

import os
from PIL import Image

def crop_and_process_logo():
    """Process logo: remove white bg, crop, and save as PNG"""
    logo_jpeg = 'static/logo.jpeg'
    logo_png = 'static/logo.png'
    
    if not os.path.exists(logo_jpeg):
        print("❌ Error: static/logo.jpeg not found")
        return False
    
    try:
        # Open and convert to RGBA
        print("📷 Loading logo...")
        img = Image.open(logo_jpeg)
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        print(f"   Original size: {img.width}x{img.height}")
        
        # Get image data
        data = img.getdata()
        
        # Replace white background with transparent
        print("🎨 Removing white background...")
        new_data = []
        for item in data:
            # If pixel is white or very light, make transparent
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        # Apply transparency
        img.putalpha(Image.new('L', img.size, 255))
        img.putdata(new_data)
        
        # Auto-crop to content
        print("✂️  Cropping to content...")
        alpha = img.split()[-1]
        bbox = alpha.getbbox()
        
        if bbox:
            x1, y1, x2, y2 = bbox
            # Add small padding
            padding = 15
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(img.width, x2 + padding)
            y2 = min(img.height, y2 + padding)
            img = img.crop((x1, y1, x2, y2))
        
        # Save as PNG
        print(f"💾 Saving as PNG...")
        img.save(logo_png)
        
        print(f"✓ Success!")
        print(f"   Saved: {logo_png}")
        print(f"   Size: {img.width}x{img.height}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("   CourseHub Logo Processor")
    print("=" * 50)
    success = crop_and_process_logo()
    print("=" * 50)
    if success:
        print("✓ Logo is ready to use!")
        print("  Restart the app to see the new logo")
    else:
        print("✗ Logo processing failed")
