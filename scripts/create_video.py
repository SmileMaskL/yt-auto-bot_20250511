import os
import uuid
import logging
import tempfile
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from scripts.utils import create_background_image, get_font_path

logger = logging.getLogger(__name__)

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
    이미지 + 오디오로 영상 생성
    - audio_path: 생성된 음성 파일 경로
    - text: 삽입할 텍스트
    - output_path: 최종 영상 저장 경로
    - duration: 텍스트 노출 시간
    """
    try:
        # 이미지 생성
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

        # 이미지 → 영상 클립 변환
        logger.info("이미지를 영상 클립으로 변환 중...")
        image_clip = ImageClip(bg_image_path, duration=duration)

        # 오디오 클립 준비
        logger.info("오디오 클립 로딩 중...")
        audio_clip = AudioFileClip(audio_path)

        # 오디오와 영상 결합
        logger.info("오디오와 영상 결합 중...")
        video_clip = image_clip.set_audio(audio_clip)
        video_clip = video_clip.set_duration(audio_clip.duration)

        # 영상 출력
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

def main():
    try:
        logger.info("🎞 영상 생성 파이프라인 시작...")

        # 임시 폴더 생성
        with tempfile.TemporaryDirectory() as tmpdir:
            text = "이것은 자동 생성된 예시 텍스트입니다."
            audio_path = os.path.join(tmpdir, "speech.mp3")
            video_path = os.path.join(tmpdir, "output.mp4")

            # 테스트용 오디오 파일 생성
            from scripts.voice_generator import generate_voice
            generate_voice(text, audio_path)

            # 오디오 길이 측정
            from moviepy.editor import AudioFileClip
            audio_duration = AudioFileClip(audio_path).duration

            # 영상 생성
            create_video_with_ffmpeg(
                audio_path=audio_path,
                text=text,
                output_path=video_path,
                duration=audio_duration
            )

            # 유튜브 업로드
            from scripts.youtube_uploader import upload_video_to_youtube
            video_id = upload_video_to_youtube(video_path, title="테스트 영상", description=text)

            logger.info(f"📺 유튜브 업로드 완료: https://youtu.be/{video_id}")

            # Slack 알림 (옵션)
            try:
                from scripts.notifier import send_notification
                send_notification(f"✅ 유튜브 영상 업로드 완료: https://youtu.be/{video_id}")
            except ImportError:
                logger.warning("notifier 모듈이 없어서 Slack 알림을 건너뜁니다.")

    except Exception as e:
        logger.error(f"[main] 전체 파이프라인 실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main()
