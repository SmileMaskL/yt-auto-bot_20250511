# scripts/main.py

import os
import sys
import logging
from scripts.content_generator import ContentGenerator, OpenAIKeyManager
from scripts.create_video import create_video_from_audio_and_text

try:
    from scripts.notifier import send_notification
except ImportError:
    def send_notification(msg): pass  # 알림 함수가 없을 경우 무시

# --- 설정 ---
LOG_FILE_PATH = "automation_main.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- OpenAI API 키 관리 및 ContentGenerator 인스턴스 생성 ---
openai_key_manager = OpenAIKeyManager(env_var_name="OPENAI_API_KEYS_BASE64")
content_gen = ContentGenerator(key_manager=openai_key_manager, model="gpt-4-turbo")

def generate_youtube_script(topic: str) -> str:
    """주어진 주제로 YouTube 스크립트를 생성"""
    system_prompt = (
        "Create a YouTube shorts script that is concise, engaging, and informative. "
        "Make sure it is structured in short, impactful sentences, and ends with punctuation."
    )
    user_prompt = f"Create a YouTube shorts script about the following topic: '{topic}'"

    try:
        script = content_gen.generate_text(prompt=user_prompt, system_message=system_prompt)
        logger.info(f"📜 스크립트 생성 완료 (길이: {len(script)}자)")
        return script
    except Exception as e:
        logger.exception("❌ 스크립트 생성 중 오류 발생")
        raise

def create_video_from_script_and_audio(script_text: str, audio_path: str) -> str:
    """스크립트와 오디오를 기반으로 영상 생성"""
    output_path = "output_video.mp4"
    try:
        create_video_from_audio_and_text(script_text, audio_path, output_path)
        logger.info(f"✅ 비디오 생성 완료: {output_path}")
        return output_path
    except Exception as e:
        logger.exception("❌ 비디오 생성 실패")
        raise

def main():
    topic = "The Benefits of Artificial Intelligence"
    audio_file = "audio_output.mp3"

    logger.info(f"🚀 주제 시작: {topic}")
    try:
        script = generate_youtube_script(topic)

        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"❌ 오디오 파일이 존재하지 않음: {audio_file}")

        video_path = create_video_from_script_and_audio(script, audio_file)

        logger.info(f"🎉 모든 과정 완료. 출력 파일: {video_path}")

    except Exception as e:
        logger.error(f"❌ 전체 자동화 실패: {e}")
        send_notification(f"🚨 자동화 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
