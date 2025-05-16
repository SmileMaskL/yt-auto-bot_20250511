import os
from scripts import (
    content_generator,
    voice_generator,
    video_generator,
    thumbnail_generator,
    youtube_uploader,
    api_manager,
    maintenance
)

def main():
    # API 키 로테이션
    api_manager.rotate_openai_key()

    # 핫이슈 콘텐츠 생성
    script_text = content_generator.generate_content()

    # 음성 생성
    audio_path = voice_generator.text_to_speech(script_text)

    # 썸네일 생성
    thumbnail_path = thumbnail_generator.generate_thumbnail(script_text)

    # 영상 생성
    video_path = video_generator.create_video(audio_path, script_text)

    # YouTube 업로드
    youtube_uploader.upload_video(video_path, thumbnail_path, script_text)

    # 유지보수 작업
    maintenance.cleanup_old_files()

if __name__ == "__main__":
    main()
