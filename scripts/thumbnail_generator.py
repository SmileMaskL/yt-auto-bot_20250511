from PIL import Image, ImageDraw, ImageFont
import os

def generate_thumbnail(text, output_path):
    img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 60)
    d.text((100, 300), text, fill=(255, 255, 0), font=font)
    img.save(output_path)
