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
        save_gcp_credentials_from_env()  # ✅ GCP 인증 설정

        content_gen = ContentGenerator()
        content = content_gen.generate()

        audio_path = generate_voice(content)
        thumbnail_path = "thumbnail.jpg"
        generate_thumbnail(content, thumbnail_path)

        video_path = "output_video.mp4"
        create_video_with_subtitles(audio_path, content, video_path)

        upload_video_to_youtube(video_path, content, thumbnail_path)

        analyze_channel_performance()

        send_notification("✅ 작업이 성공적으로 완료되었습니다.")
    except Exception as e:
        send_notification(f"❌ 작업 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()
