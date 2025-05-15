from PIL import Image, ImageDraw, ImageFont
import os

def generate_thumbnail(text: str, output_path: str):
    """
    1280x720 크기 썸네일 생성
    무료 폰트 NotoSans 사용 권장 (경로 fonts/NotoSansCJKkr-Regular.otf)
    """
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(50, 50, 50))

    draw = ImageDraw.Draw(img)
    font_path = os.path.join('fonts', 'NotoSansCJKkr-Regular.otf')
    font = ImageFont.truetype(font_path, 64)

    # 텍스트 자동 줄바꿈 및 중앙 정렬
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        w, h = draw.textsize(test_line, font=font)
        if w > width - 200:
            lines.append(line)
            line = word
        else:
            line = test_line
    lines.append(line)

    total_text_height = len(lines) * font.getsize('A')[1] + (len(lines)-1)*10
    y_text = (height - total_text_height) // 2

    for line in lines:
        w, h = draw.textsize(line, font=font)
        x_text = (width - w) // 2
        draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
        y_text += h + 10

    img.save(output_path)
