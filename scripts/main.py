from scripts.content_generator import generate_script
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video_with_subtitles
from scripts.youtube_uploader import upload_video
from scripts.thumbnail_generator import generate_thumbnail
from scripts.analytics_bot import analyze_performance
from scripts.notifier import send_slack_notification
import os

def main():
    script_text = generate_script()
    audio_path = generate_voice(script_text)
    thumbnail_path = generate_thumbnail(script_text)
    video_path = "output_video.mp4"
    create_video_with_subtitles(audio_path, script_text, video_path)
    video_url = upload_video(video_path, script_text, thumbnail_path)
    stats = analyze_performance(video_url)
    send_slack_notification(video_url, stats)

if __name__ == '__main__':
    main()
