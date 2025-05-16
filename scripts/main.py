# ✅ scripts/main.py
# 완전 자동 실행되는 유튜브 수익화 파이프라인의 시작점입니다.
# 이 스크립트는 모든 주요 컴포넌트를 순서대로 호출하여 전체 프로세스를 완성합니다.

from content_generator import generate_hot_topic_script
from voice_generator import synthesize_voice
from video_generator import create_video_with_audio
from youtube_uploader import upload_video
from thumbnail_generator import generate_thumbnail
from api_manager import clean_old_files, rotate_openai_key
import os
import datetime


def main():
    print("📌 [1단계] OpenAI 키 자동 로테이션 중...")
    rotate_openai_key()

    print("🔥 [2단계] 오늘의 핫이슈 콘텐츠 생성 중...")
    script_text, title, tags = generate_hot_topic_script()

    print("🗣️ [3단계] 음성 합성 중...")
    audio_path = synthesize_voice(script_text)

    print("🎬 [4단계] 영상 생성 중...")
    video_path = create_video_with_audio(audio_path, script_text)

    print("🖼️ [5단계] 썸네일 생성 중...")
    thumbnail_path = generate_thumbnail(title)

    print("📤 [6단계] 유튜브 업로드 중...")
    upload_video(video_path, title, script_text, tags, thumbnail_path)

    print("🧹 [7단계] 오래된 파일 정리 중...")
    clean_old_files(days=7)

    print("✅ 모든 작업이 완료되었습니다!")


if __name__ == '__main__':
    main()
