import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.content_generator import ContentGenerator
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video_with_subtitles
from scripts.youtube_uploader import upload_video_to_youtube
from scripts.thumbnail_generator import generate_thumbnail
from scripts.analytics_bot import analyze_channel_performance
from scripts.notifier import send_notification

def main():
    try:
        # 콘텐츠 생성
        generator = ContentGenerator()
        content = generator.generate()

        # 음성 생성
        audio_path = generate_voice(content)

        # 썸네일 생성
        thumbnail_path = 'thumbnail.jpg'
        generate_thumbnail(content, thumbnail_path)

        # 영상 생성
        video_path = 'output_video.mp4'
        create_video_with_subtitles(audio_path, content, video_path)

        # YouTube 업로드
        upload_video_to_youtube(video_path, content, thumbnail_path)

        # 조회수 및 수익 분석
        analyze_channel_performance()

        # 성공 알림
        send_notification("✅ 작업이 성공적으로 완료되었습니다.")
    except Exception as e:
        send_notification(f"❌ 작업 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()
