from content_generator import generate_content
from voice_generator import generate_voice
from create_video import create_video
from youtube_uploader import upload_video

def main():
    script = generate_content()
    audio_path = generate_voice(script)
    video_path = create_video(audio_path, script)
    upload_video(video_path, script)

if __name__ == '__main__':
    main()
