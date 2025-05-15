# scripts/main.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from scripts.utils.error_handler import RetryableError
from scripts.validate_env import validate_environment
from scripts.content_generator import ContentGenerator
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video_from_audio_and_text
from scripts.youtube_uploader import upload_video_to_youtube

# Optional Slack 알림 모듈
try:
    from scripts.notifier import send_notification
except ImportError:
    send_notification = None

def main():
    logging.basicConfig(level=logging.INFO)

    try:
        logging.info("✅ 환경 변수 검증 중...")
        validate_environment()

        logging.info("✍️ 텍스트 콘텐츠 생성 중...")
        generator = ContentGenerator()
        content = generator.generate()

        logging.info("🎤 음성 생성 중...")
        audio_path = generate_voice(content)

        logging.info("🎞️ 영상 생성 중...")
        video_path = create_video_from_audio_and_text(content, audio_path)

        logging.info("📤 YouTube에 업로드 중...")
        video_url = upload_video_to_youtube(video_path, content)

        if send_notification:
            send_notification(f"✅ 업로드 성공: {video_url}")

    except RetryableError as e:
        logging.error(f"❌ 복구 불가 오류 발생: {str(e)}")
        if send_notification:
            send_notification(f"🚨 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()
