from scripts.content_generator import generate_script
from scripts.voice_generator import generate_voice
from scripts.create_video import create_video
from scripts.youtube_uploader import upload_video
from scripts.thumbnail_generator import generate_thumbnail

def main():
    script_text = generate_script()
    audio_file = generate_voice(script_text)
    video_file = create_video(audio_file, script_text)
    thumbnail_file = generate_thumbnail(script_text)
    upload_video(video_file, script_text, thumbnail_file)

if __name__ == "__main__":
    main()
