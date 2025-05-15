import os
import logging
import json
from scripts.content_generator import ContentGenerator
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video_from_audio_and_text
from scripts.youtube_uploader import upload_video_to_youtube
from scripts.notifier import send_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        prompt = "오늘의 인공지능 뉴스 요약을 만들어줘."
        content_gen = ContentGenerator(os.environ['OPENAI_API_KEYS_BASE64'])
        text = content_gen.generate_text(prompt)

        audio_path = generate_voice(text)
        video_path = create_video_from_audio_and_text(audio_path, text)

        creds = json.loads(os.environ['GOOGLE_TOKEN_JSON'])
        video_id = upload_video_to_youtube("AI 뉴스 요약", text, video_path, creds)

        send_notification(
            f"🎉 유튜브 업로드 성공! https://youtu.be/{video_id}",
            os.environ['SLACK_API_TOKEN'],
            os.environ['SLACK_CHANNEL']
        )

    except Exception as e:
        logger.error(f"🚨 전체 실행 실패: {e}")
        send_notification(
            f"🚨 자동화 실패: {e}",
            os.environ.get('SLACK_API_TOKEN', ''),
            os.environ.get('SLACK_CHANNEL', '')
        )

if __name__ == "__main__":
    main()
