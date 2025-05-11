# 전체 자동화 파이썬 코드
import os
import json
from content_generator import get_trending_keywords, generate_script
from youtube_uploader import generate_tts_audio, create_thumbnail, create_video, get_authenticated_service, upload_video, post_comment
from notifier import send_notification
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

def main():
    try:
        keywords = get_trending_keywords()
        for keyword in keywords:
            script = generate_script(keyword)
            logging.info(f"스크립트 생성 완료: {script[:30]}...")  # 스크립트 일부 출력

            audio_file = generate_tts_audio(script)
            thumbnail_file = create_thumbnail(keyword)
            video_file = create_video(script, audio_file, thumbnail_file)

            youtube = get_authenticated_service()
            video_id = upload_video(youtube, video_file, f"{keyword}에 대한 영상", script, thumbnail_file)
            post_comment(youtube, video_id, f"{keyword}에 대한 자세한 정보를 확인하세요!")

            # 임시 파일 삭제
            os.remove(audio_file)
            os.remove(thumbnail_file)
            os.remove(video_file)

        send_notification("✅ YouTube 자동화 작업이 성공적으로 완료되었습니다.")
    except Exception as e:
        logging.error(f"자동화 작업 중 오류 발생: {e}")
        send_notification(f"❌ YouTube 자동화 작업 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
