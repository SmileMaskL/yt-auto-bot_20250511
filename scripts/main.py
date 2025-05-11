# 전체 자동화 파이썬 코드
import logging
from content_generator import get_trending_keywords, generate_script
from youtube_upload import (
    generate_tts_audio,
    create_thumbnail,
    create_video,
    get_authenticated_service,
    upload_video,
    post_comment
)
from notifier import send_notification

def main():
    try:
        keywords = get_trending_keywords()
        for keyword in keywords:
            script = generate_script(keyword)
            audio_file = generate_tts_audio(script)
            thumbnail_file = create_thumbnail(keyword)
            video_file = create_video(script, audio_file, thumbnail_file)
            youtube = get_authenticated_service()
            video_id = upload_video(youtube, video_file, keyword, script, thumbnail_file)
            post_comment(youtube, video_id, f"{keyword}에 대한 자세한 내용을 확인해보세요!")
            video_url = f"https://youtu.be/{video_id}"
            logging.info(f"업로드 완료: {video_url}")
            send_notification(f"✅ 영상 업로드 성공: {video_url}")
    except Exception as e:
        logging.error(f"전체 프로세스 오류: {e}")
        send_notification(f"🚨 오류 발생: {e}")

if __name__ == "__main__":
    main()
