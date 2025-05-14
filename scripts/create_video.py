import os
import uuid
import logging
import tempfile
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip, TextClip
from scripts.utils import create_background_image, get_font_path

# 로그 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_video_with_ffmpeg(
    audio_path: str,
    text: str,
    output_path: str,
    duration: float,
    resolution: tuple = (1280, 720),
    font_size: int = 48,
    font_color: str = "white",
    bg_color: str = "black"
) -> None:
    """
    텍스트 이미지 + 오디오로 영상 생성
    """
    try:
        font_path = get_font_path()
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"폰트 파일이 존재하지 않습니다: {font_path}")

        logger.info("텍스트용 배경 이미지 생성 중...")
        bg_image_path = create_background_image(
            text=text,
            resolution=resolution,
            font_path=font_path,
            font_size=font_size,
            font_color=font_color,
            bg_color=bg_color,
        )

        logger.info("이미지를 영상 클립으로 변환 중...")
        image_clip = ImageClip(bg_image_path, duration=duration)

        logger.info("오디오 클립 로딩 중...")
        audio_clip = AudioFileClip(audio_path)

        logger.info("오디오와 영상 결합 중...")
        video_clip = image_clip.set_audio(audio_clip)
        video_clip = video_clip.set_duration(audio_clip.duration)

        logger.info(f"최종 영상 렌더링 중: {output_path}")
        video_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24,
            threads=4,
            verbose=False,
            logger=None,
        )

        logger.info("🎬 영상 생성 완료.")

    except Exception as e:
        logger.error(f"[create_video_with_ffmpeg] 오류 발생: {e}")
        raise


def create_video_from_audio_and_text(script_text: str, audio_file_path: str, output_file_path: str) -> None:
    """
    script_text와 audio_file_path를 이용하여 간단한 영상 생성
    텍스트는 자막으로 추가되고, 오디오는 배경음으로 사용됨.
    """
    try:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found at {audio_file_path}")

        logger.info("🎥 텍스트와 오디오로 영상 생성 시작...")

        # 오디오 길이 측정
        audio_clip = AudioFileClip(audio_file_path)
        duration = audio_clip.duration

        # 영상 배경 생성
        video_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration).set_audio(audio_clip)

        # 텍스트 자막 클립 생성
        tex
