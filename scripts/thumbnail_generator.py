from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_thumbnail(script_text, output_path="output/thumbnail.jpg"):
    # 썸네일 배경 생성
    img = Image.new('RGB', (720, 1280), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 글꼴 설정
    font = ImageFont.truetype("arial.ttf", 40)

    # 텍스트 요약 및 줄바꿈 처리
    summary = textwrap.fill(script_text[:100], width=20)

    # 텍스트 위치 계산
    text_width, text_height = draw.textsize(summary, font=font)
    position = ((720 - text_width) / 2, (1280 - text_height) / 2)

    # 텍스트 삽입
    draw.text(position, summary, fill=(255, 255, 255), font=font)

    # 썸네일 저장
    img.save(output_path)
    return output_path
