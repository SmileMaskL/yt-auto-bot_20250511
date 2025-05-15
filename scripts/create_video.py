import os
import logging
from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip

logger = logging.getLogger(__name__)


def create_video_from_audio_and_text(text: str, audio_path: str, output_path: str) -> None:
    """음성과 자막 텍스트를 기반으로 비디오 생성"""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")

    font_path = "fonts/NotoSansCJKkr-Regular.otf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"폰트 파일 누락: {font_path}")

    try:
        audio = AudioFileClip(audio_path)
        duration = audio.duration

        text_clip = TextClip(
            txt=text,
            fontsize=60,
            font=font_path,
            color="white",
            size=(1080, 1920),
            method="caption",
            align="center",
            print_cmd=True,
        ).set_duration(duration).set_position("center")

        background = "background.jpg"
        if os.path.exists(background):
            from moviepy.editor import ImageClip
            bg = ImageClip(background).set_duration(duration).resize((1080, 1920))
            final_clip = CompositeVideoClip([bg, text_clip.set_audio(audio)])
        else:
            logger.warning("배경 이미지가 없습니다. 검은 배경으로 생성합니다.")
            final_clip = CompositeVideoClip([text_clip.set_audio(audio)])

        final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        logger.info(f"✅ 비디오 파일 생성 완료: {output_path}")

    except Exception as e:
        logger.exception("❌ 비디오 생성 중 오류 발생")
        raise
