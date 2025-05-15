from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(text, output_path):
    img = Image.new('RGB', (1280, 720), color=(73, 109, 137))

    font_path = 'fonts/NotoSansCJKkr-Regular.otf'
    font = ImageFont.truetype(font_path, 60)

    draw = ImageDraw.Draw(img)
    draw.text((100, 300), text, font=font, fill=(255, 255, 255))

    img.save(output_path)
