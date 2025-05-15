import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.content_generator import ContentGenerator
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video_with_subtitles
from scripts.youtube_uploader import upload_video_to_youtube
from scripts.thumbnail_generator import generate_thumbnail
from scripts.analytics_bot import analyze_channel_performance
from scripts.slack_notifier import send_slack_notification

def main():
    generator = ContentGenerator()
    content = generator.generate()

    audio_path = generate_voice(content)

    thumbnail_path = 'thumbnail.jpg'
    generate_thumbnail(content, thumbnail_path)

    video_path = 'output_video.mp4'
    create_video_with_subtitles(audio_path, content, video_path)

    upload_video_to_youtube(video_path, content, thumbnail_path)

    analyze_channel_performance()

    send_slack_notification(f"새로운 영상이 업로드되었습니다: {content}")

if __name__ == "__main__":
    main()
