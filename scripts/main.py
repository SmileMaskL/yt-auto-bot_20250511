# 전체 자동화 파이썬 코드
# 전체 자동화 파이썬 코드
import os
import openai
import time
import json
import requests
import subprocess
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from scripts.notifier import send_notification  # ✅ 알림 모듈 추가

# 로그 파일 경로 설정
LOG_FILE = "automation.log"

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

# OpenAI API 키 순환 사용
def get_valid_openai_response(prompt):
    api_keys = os.getenv("OPENAI_API_KEYS", "").split(",")
    for key in api_keys:
        key = key.strip()
        openai.api_key = key
        try:
            log(f"🔑 OpenAI 키 시도: {key[:6]}...")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                timeout=20
            )
            log("✅ OpenAI 응답 성공")
            return response['choices'][0]['message']['content']
        except Exception as e:
            log(f"❌ OpenAI 키 실패: {str(e)}")
            continue
    raise Exception("❌ 모든 OpenAI API 키 실패")

# ElevenLabs를 통한 음성 생성
def generate_voice(text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv('ELEVENLABS_VOICE_ID')}"
    headers = {
        "xi-api-key": os.getenv("ELEVENLABS_KEY"),
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        log(f"✅ 음성 파일 저장 완료: {output_path}")
    else:
        log(f"❌ 음성 생성 실패: {response.text}")
        raise Exception("음성 생성 실패")

# 자막 생성
def generate_subtitles(text, output_path):
    lines = text.split('. ')
    with open(output_path, "w", encoding="utf-8") as f:
        for i, line in enumerate(lines, 1):
            start_time = f"00:00:{(i-1)*5:02d},000"
            end_time = f"00:00:{i*5:02d},000"
            f.write(f"{i}\n{start_time} --> {end_time}\n{line.strip()}\n\n")
    log(f"✅ 자막 파일 저장 완료: {output_path}")

# 영상 생성
def create_video(audio_path, subtitle_path, output_path):
    background_image = "background.jpg"
    if not os.path.exists(background_image):
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=10",
            background_image
        ])
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", background_image, "-i", audio_path,
        "-vf", f"subtitles={subtitle_path}",
        "-c:v", "libx264", "-t", "10", "-pix_fmt", "yuv420p", output_path
    ])
    log(f"✅ 영상 파일 생성 완료: {output_path}")

# YouTube 업로드
def upload_to_youtube(video_path, title, description):
    creds = Credentials(
        None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
    )
    youtube = build("youtube", "v3", credentials=creds)
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["AI", "Automation", "YouTube"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    media = MediaFileUpload(video_path, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    response = request.execute()
    log(f"✅ YouTube 업로드 완료: https://youtu.be/{response['id']}")

# 메인 실행 함수
def main():
    log("🚀 자동화 시작")
    try:
        prompt = "오늘의 대한민국 트렌드를 5가지 요약해줘."
        script = get_valid_openai_response(prompt)
        log(f"📜 생성된 스크립트: {script}")

        audio_file = "output.mp3"
        generate_voice(script, audio_file)

        subtitle_file = "subtitles.srt"
        generate_subtitles(script, subtitle_file)

        video_file = "output.mp4"
        create_video(audio_file, subtitle_file, video_file)

        upload_to_youtube(video_file, "AI 자동 생성 영상", "이 영상은 AI를 통해 자동으로 생성되었습니다.")
    except Exception as e:
        log(f"❌ 자동화 실패: {str(e)}")
        send_notification(f"자동화 실패: {str(e)}")  # ✅ 알림 전송
    log("🏁 자동화 종료")

if __name__ == "__main__":
    main()

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        print("------ Automation Log Start ------")
        print(f.read())
        print("------ Automation Log End ------")
