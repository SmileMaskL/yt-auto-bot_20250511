import os
import openai
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from moviepy import AudioFileClip, ColorClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import datetime

# 1. API 키 환경변수에서 불러오기
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

# ElevenLabs 클라이언트 생성
client = ElevenLabs(api_key=elevenlabs_api_key)

# 2. GPT-4로 스크립트 생성
def generate_script():
    prompt = "사람들이 놀랄 만한 흥미로운 사실을 30초 분량의 유튜브 Shorts 스타일로 알려줘."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# 3. ElevenLabs로 음성 생성
def generate_voice(text):
    audio = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_multilingual_v2",
        voice_settings=VoiceSettings(stability=0.4, similarity_boost=0.75)
    )
    os.makedirs("output", exist_ok=True)
    with open("output/audio.mp3", "wb") as f:
        f.write(audio)

# 4. 음성 길이에 맞춰 배경 영상 생성
def generate_video():
    audio = AudioFileClip("output/audio.mp3")
    video = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=audio.duration)
    video = video.set_audio(audio)
    video.write_videofile("output/final_video.mp4", fps=24)

# 5. GCP 서비스 계정으로 유튜브에 업로드
def upload_to_youtube():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    credentials = Credentials.from_service_account_file("gcp_key.json", scopes=scopes)
    youtube = build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "title": f"오늘의 놀라운 지식 - {datetime.datetime.now().strftime('%Y.%m.%d')}",
            "description": "매일매일 재미있는 지식 Shorts!",
            "tags": ["Shorts", "재미있는 사실", "AI", "자동 유튜브"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload("output/final_video.mp4", mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = request.execute()
    print("✅ 업로드 완료! 영상 ID:", response["id"])

# 6. 실행 파트
if __name__ == "__main__":
    print("📜 스크립트 생성 중...")
    script = generate_script()
    print(f"생성된 스크립트:\n{script}\n")

    print("🎧 음성 생성 중...")
    generate_voice(script)

    print("🎬 영상 생성 중...")
    generate_video()

    print("📤 유튜브 업로드 중...")
    upload_to_youtube()
