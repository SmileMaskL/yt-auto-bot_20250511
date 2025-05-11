# 전체 자동화 파이썬 코드
import os
import logging
from datetime import datetime
from content_generator import get_trending_keywords, generate_script
from youtube_upload import generate_tts_audio, create_thumbnail, create_video, get_authenticated_service, upload_video, post_comment
from notifier import send_notification

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)

def cleanup_tempfiles(*files):
    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
                logging.info(f"삭제 완료: {f}")
        except Exception as e:
            logging.warning(f"파일 삭제 실패 {f}: {e}")

def main():
    try:
        keywords = get_trending_keywords()[:3]
        youtube = get_authenticated_service()

        for idx, keyword in enumerate(keywords, 1):
            logging.info(f"처리 중 ({idx}/{len(keywords)}): {keyword}")
            script = generate_script(keyword)

            audio_file = generate_tts_audio(script)
            thumbnail_file = create_thumbnail(keyword)
            video_file = create_video(script, audio_file, thumbnail_file)

            video_id = upload_video(
                youtube,
                video_file,
                title=f"{keyword} 분석 {datetime.today().strftime('%Y-%m-%d')}",
                description=f"AI 생성 콘텐츠 - {script[:300]}...",
                thumbnail_file=thumbnail_file
            )

            post_comment(youtube, video_id, f"{keyword} 관련 추가 정보는 댓글을 참조하세요!")
            cleanup_tempfiles(audio_file, thumbnail_file, video_file)

        send_notification(f"🎉 {len(keywords)}개 영상 업로드 완료!")

    except Exception as e:
        logging.critical(f"치명적 오류 발생: {str(e)}", exc_info=True)
        send_notification(f"🔥 시스템 오류 발생: {str(e)[:200]}")
        raise

if __name__ == "__main__":
    main()
