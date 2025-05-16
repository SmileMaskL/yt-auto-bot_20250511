from PIL import Image, ImageDraw, ImageFont
import os

def generate_thumbnail(text, output_path="output/thumbnail.jpg"):
    os.makedirs("output", exist_ok=True)
    img = Image.new("RGB", (1280, 720), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((100, 300), text[:50], fill=(255, 255, 255), font=font)
    img.save(output_path)
    return output_path
