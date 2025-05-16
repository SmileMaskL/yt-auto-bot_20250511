from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(text):
    img = Image.new('RGB', (1280, 720), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 60)
    draw.text((100, 300), text[:40], font=font, fill=(255, 255, 255))
    path = "thumbnail.jpg"
    img.save(path)
    return path
