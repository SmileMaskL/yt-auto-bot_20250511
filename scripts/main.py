import os
from scripts.auth import save_gcp_credentials_from_env
from scripts.content_generator import ContentGenerator
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video_with_subtitles
from scripts.youtube_uploader import upload_video_to_youtube
from scripts.thumbnail_generator import generate_thumbnail
from scripts.analytics_bot import analyze_channel_performance
from scripts.notifier import send_notification

def main():
    try:
        # GCP 인증 설정
        save_gcp_credentials_from_env()

        # 콘텐츠 생성
        content_gen = ContentGenerator()
        content = content_gen.generate()

        # 음성 생성
        audio_path = generate_voice(content)

        # 썸네일 생성
        thumbnail_path = "thumbnail.jpg"
        generate_thumbnail(content, thumbnail_path)

        # 비디오 생성
        video_path = "output_video.mp4"
        create_video_with_subtitles(audio_path, content, video_path)

        # YouTube 업로드
        upload_video_to_youtube(video_path, content, thumbnail_path)

        # 채널 성과 분석
        analyze_channel_performance()

        # 성공 알림
        send_notification("✅ 작업이 성공적으로 완료되었습니다.")
    except Exception as e:
        # 실패 알림
        send_notification(f"❌ 작업 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()
