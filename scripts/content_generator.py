import os
import openai
import requests
import ffmpeg
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# API 키 설정
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def generate_script():
    print("▶ 유튜브 스크립트 생성 중...")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "90초 분량의 수익성 높은 유튜브 콘텐츠 스크립트를 생성해줘."},
            {"role": "user", "content": "오늘의 인기 있는 주제로 유튜브 콘텐츠를 만들어줘."}
        ]
    )
    return response.choices[0].message.content.strip()

def generate_thumbnail(text):
    print("▶ 썸네일 이미지 생성 중...")
    response = openai.Image.create(
        prompt=text[:200],
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    image_data = requests.get(image_url).content
    os.makedirs("input", exist_ok=True)
    with open("input/thumbnail.jpg", "wb") as f:
        f.write(image_data)

def text_to_speech(text, output_path):
    print("▶ 음성 합성 중...")
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
        }
    )
    with open(output_path, "wb") as f:
        f.write(response.content)

def combine_audio_and_video(audio_path, image_path, output_path):
    print("▶ 영상 생성 중...")
    ffmpeg.input(image_path, loop=1, framerate=1).output(
        audio_path,
        output_path,
        vcodec='libx264',
        acodec='aac',
        shortest=None,
        pix_fmt='yuv420p'
    ).overwrite_output().run()

def upload_to_youtube(title, description, file_path):
    print("▶ 유튜브 업로드 중...")
    creds = Credentials.from_authorized_user_file("credentials.json", ["https://www.googleapis.com/auth/youtube.upload"])
    youtube = build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["AI", "자동 생성", "유튜브 자동화"]
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=file_path
    )
    response = request.execute()
    print(f"✅ 업로드 완료: https://www.youtube.com/watch?v={response['id']}")

def main():
    os.makedirs("output", exist_ok=True)
    script = generate_script()
    with open("output/script.txt", "w") as f:
        f.write(script)

    generate_thumbnail(script)
    audio_path = "output/narration.mp3"
    text_to_speech(script, audio_path)
    combine_audio_and_video(audio_path, "input/thumbnail.jpg", "output/video.mp4")
    upload_to_youtube("AI가 만든 오늘의 콘텐츠!", script, "output/video.mp4")

if __name__ == "__main__":
    main()
