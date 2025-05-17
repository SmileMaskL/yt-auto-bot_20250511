import os
import json
import random
import datetime

# openai 최신 공식 라이브러리 import (v1.x 기준)
from openai import OpenAI

from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from moviepy.editor import AudioFileClip, ColorClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials


# ===== 1. OpenAI API 키 여러 개를 JSON 배열로 환경변수에서 읽고 랜덤 선택해서 OpenAI 클라이언트 생성 =====

keys_json = os.getenv("OPENAI_API_KEYS")
if not keys_json:
    raise Exception("환경변수 OPENAI_API_KEYS 가 설정되어 있지 않습니다! (GitHub Secrets에 JSON 배열 문자열로 저장 필요)")

api_keys = json.loads(keys_json)
if not isinstance(api_keys, list) or len(api_keys) == 0:
    raise Exception("OPENAI_API_KEYS는 빈 리스트가 아니어야 합니다!")

def get_openai_client():
    selected_key = random.choice(api_keys)
    print(f"▶ 사용 중인 OpenAI API 키 일부: {selected_key[:8]}****")
    return OpenAI(api_key=selected_key)


# ===== 2. ElevenLabs API 키와 Voice ID 환경변수에서 읽기 =====

elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
if not elevenlabs_api_key:
    raise Exception("환경변수 ELEVENLABS_API_KEY 가 설정되어 있지 않습니다!")

voice_id = os.getenv("ELEVENLABS_VOICE_ID")
if not voice_id:
    raise Exception("환경변수 ELEVENLABS_VOICE_ID 가 설정되어 있지 않습니다!")

eleven_client = ElevenLabs(api_key=elevenlabs_api_key)


# ===== 3. GPT-4 로 스크립트 생성 함수 =====

def generate_script():
    client = get_openai_client()
    prompt = "사람들이 놀랄 만한 흥미로운 사실을 30초 분량의 유튜브 Shorts 스타일로 알려줘."
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return completion.choices[0].message.content.strip()


# ===== 4. ElevenLabs 로 음성 생성 함수 =====

def generate_voice(text):
    audio = eleven_client.generate(
        text=text,
        voice=voice_id,
        model="eleven_multilingual_v2",
        voice_settings=VoiceSettings(stability=0.4, similarity_boost=0.75),
    )
    os.makedirs("output", exist_ok=True)
    with open("output/audio.mp3", "wb") as f:
        f.write(audio)
    print("▶ 음성 생성 완료 (output/audio.mp3)")


# ===== 5. 음성 길이에 맞춰 배경 영상 생성 함수 =====

def generate_video():
    audio = AudioFileClip("output/audio.mp3")
    video = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=audio.duration)
    video = video.set_audio(audio)
    video.write_videofile("output/final_video.mp4", fps=24)
    print("▶ 영상 생성 완료 (output/final_video.mp4)")


# ===== 6. GCP 서비스 계정 JSON 파일 경로 및 유튜브 업로드 함수 =====

def upload_to_youtube():
    gcp_key_path = "gcp_key.json"
    if not os.path.exists(gcp_key_path):
        raise Exception(f"GCP 서비스 계정 키 파일이 존재하지 않습니다: {gcp_key_path}")

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    credentials = Credentials.from_service_account_file(gcp_key_path, scopes=scopes)
    youtube = build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "title": f"오늘의 놀라운 지식 - {datetime.datetime.now().strftime('%Y.%m.%d')}",
            "description": "매일매일 재미있는 지식 Shorts!",
            "tags": ["Shorts", "재미있는 사실", "AI", "자동 유튜브"],
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload("output/final_video.mp4", mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = request.execute()

    print(f"✅ 유튜브 업로드 완료! 영상 ID: {response['id']}")


# ===== 7. 메인 실행부 =====

if __name__ == "__main__":
    print("📜 GPT-4 스크립트 생성 중...")
    script = generate_script()
    print(f"생성된 스크립트:\n{script}\n")

    print("🎧 ElevenLabs 음성 생성 중...")
    generate_voice(script)

    print("🎬 배경 영상 생성 중...")
    generate_video()

    print("📤 유튜브 업로드 중...")
    upload_to_youtube()

    print("✔ 모든 작업 완료! 매일매일 자동으로 수익을 창출하세요!")
