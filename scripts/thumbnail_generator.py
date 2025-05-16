from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(text):
    img = Image.new('RGB', (1280, 720), color=(255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    path = "output/thumbnail.jpg"
    img.save(path)
    return path
