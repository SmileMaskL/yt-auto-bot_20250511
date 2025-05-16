from scripts.analytics_bot import get_top_video_titles
from scripts.content_generator import generate_script
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video
from scripts.thumbnail_generator import generate_thumbnail
from scripts.translate_subtitles import translate_subtitles
from scripts.youtube_uploader import upload_video


def main():
    titles = get_top_video_titles()
    for title in titles:
        print(f"▶ {title} 콘텐츠 생성 중...")
        script = generate_script(f"{title}에 대한 짧고 흥미로운 스크립트 작성해줘")

        audio_path = "output/audio.mp3"
        generate_voice(script, audio_path)

        translated = translate_subtitles(script, target_lang='en')
        subtitles_path = "output/subtitles.srt"
        with open(subtitles_path, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:00,000 --> 00:00:10,000\n" + translated)

        video_path = create_video(audio_path, script, subtitles_path)
        thumbnail_path = generate_thumbnail(title)

        upload_video(video_path, title, script, thumbnail_path)


if __name__ == "__main__":
    main()
