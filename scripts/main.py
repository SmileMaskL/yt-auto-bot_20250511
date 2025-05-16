from scripts.analytics_bot import get_top_video_titles
from scripts.create_video import create_video
from scripts.thumbnail_generator import generate_thumbnail
from scripts.translate_subtitles import translate_subtitles
from scripts.youtube_uploader import upload_video
from scripts.voice_generator import generate_voice
from scripts.content_generator import generate_script

import os
import uuid

def main():
    # 🔍 인기 키워드 기반 제목 가져오기
    titles = get_top_video_titles()

    for title in titles:
        print(f"\n[+] Processing title: {title}")

        # 📜 스크립트 생성
        script_text = generate_script(title)
        print("[✓] Script generated.")

        # 🗣️ 오디오 생성
        audio_path = f"output/audio_{uuid.uuid4().hex}.mp3"
        generate_voice(script_text, audio_path)
        print("[✓] Audio generated.")

        # 📝 자막 생성
        subtitles_path = f"output/subtitles_{uuid.uuid4().hex}.srt"
        with open(subtitles_path, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:00,000 --> 00:00:05,000\n" + script_text)
        print("[✓] Subtitles file created.")

        # 📽️ 영상 생성
        video_path = create_video(audio_path, script_text, subtitles_path)
        print(f"[✓] Video created at {video_path}")

        # 🖼️ 썸네일 생성
        thumbnail_path = generate_thumbnail(script_text)
        print(f"[✓] Thumbnail created at {thumbnail_path}")

        # 🌍 다국어 자막 생성
        translate_subtitles(subtitles_path)
        print("[✓] Subtitles translated.")

        # ⬆️ 유튜브 업로드
        upload_video(
            video_path=video_path,
            title=title,
            description=script_text,
            tags=["shorts", "trending", "ai"],
            thumbnail_path=thumbnail_path,
            subtitles_path=subtitles_path
        )
        print("[✓] Video uploaded to YouTube.")

        # ✅ 완료 로그
        print(f"[✔] '{title}' 업로드 완료!\n")

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    main()
