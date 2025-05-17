import os
import openai
from elevenlabs import generate, save, set_api_key
from moviepy.editor import *
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import datetime

# 🔑 API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

# 📜 1. 콘텐츠 생성 (ChatGPT)
def generate_script():
    prompt = "오늘의 흥미로운 사실을 30초 분량의 유튜브 Shorts 스타일로 알려줘."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response['choices'][0]['message']['content'].strip()

# 🎤 2. 음성 생성 (ElevenLabs)
def generate_voice(text):
    audio = generate(text=text, voice=os.getenv("ELEVENLABS_VOICE_ID"), model="eleven_multilingual_v2")
    save(audio, "output/audio.mp3")

# 🎬 3. 영상 생성 (MoviePy)
def generate_video():
    audio = AudioFileClip("output/audio.mp3")
    video = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=audio.duration)
    video = video.set_audio(audio)
    video.write_videofile("output/final_video.mp4", fps=24)

# 📤 4. 유튜브 업로드
def upload_to_youtube():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    credentials = Credentials.from_service_account_file("gcp_key.json", scopes=scopes)
    youtube = build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "title": f"오늘의 지식 #{datetime.datetime.now().strftime('%Y%m%d')}",
            "description": "매일 새로운 지식을 Shorts로!",
            "tags": ["Shorts", "흥미로운 사실", "AI", "유튜브 자동화"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload("output/final_video.mp4", chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = request.execute()
    print("🎉 업로드 완료:", response["id"])

# 📂 디렉토리 준비
os.makedirs("output", exist_ok=True)

# ✅ 전체 파이프라인 실행
if __name__ == "__main__":
    print("🧠 스크립트 생성 중...")
    script = generate_script()
    print("🎤 음성 합성 중...")
    generate_voice(script)
    print("🎬 영상 제작 중...")
    generate_video()
    print("📤 유튜브 업로드 중...")
    upload_to_youtube()
