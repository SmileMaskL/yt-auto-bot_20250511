from scripts import trend_collector, content_generator, voice_generator, video_generator, thumbnail_generator, youtube_uploader, comment_generator, shorts_converter, maintenance
import os

def main():
    topics = trend_collector.get_trending_topics()
    for topic in topics:
        script = content_generator.generate_script(topic)
        audio_path = voice_generator.generate_voice(script, topic)
        image_path = "path_to_default_image.jpg"  # 기본 이미지 경로 설정
        video_path = os.path.join("data", "videos", f"{topic}.mp4")
        thumbnail_path = os.path.join("data", "thumbnails", f"{topic}.jpg")

        video_generator.create_video(image_path, audio_path, video_path)
        thumbnail_generator.generate_thumbnail(topic, thumbnail_path)
        youtube
::contentReference[oaicite:18]{index=18}
 
