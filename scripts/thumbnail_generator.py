from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(text, output_path="thumbnail.jpg"):
    img = Image.new("RGB", (1280, 720), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 60)
    draw.text((100, 300), text, font=font, fill=(255, 255, 0))
    img.save(output_path)
