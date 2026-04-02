from PIL import Image

# Load the image
logo_path = 'static/logo.jpeg'
img = Image.open(logo_path)

# Convert to RGBA if not already
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Get image data
data = img.getdata()

# Replace white background with transparent
new_data = []
for item in data:
    # If pixel is white or near-white (R, G, B close to 255), make it transparent
    if item[0] > 240 and item[1] > 240 and item[2] > 240:
        new_data.append((255, 255, 255, 0))  # Transparent
    else:
        new_data.append(item)

img.putalpha(Image.new('L', img.size, 255))
img.putdata(new_data)

# Auto-crop the transparent borders
def get_bbox(img):
    """Get bounding box of non-transparent content"""
    alpha = img.split()[-1]
    return alpha.getbbox()

bbox = get_bbox(img)
if bbox:
    img = img.crop(bbox)

# Save as PNG with transparency
img.save('static/logo.png')
print("✓ Logo processed successfully!")
print(f"  - Removed white background")
print(f"  - Cropped to content")
print(f"  - Saved as: static/logo.png")
print(f"  - Image size: {img.size}")
