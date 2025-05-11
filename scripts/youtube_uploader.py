import os
import openai
import requests
from moviepy.editor import TextClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import tempfile

openai.api_key = json.loads(os.environ["OPENAI_API_KEYS"])[0]

def generate_script():
    topic = f"Top trend {datetime.utcnow().strftime('%Y-%m-%d')}"
    prompt = f"Create an engaging YouTube script for the topic: {topic}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    script = response["choices"][0]["message"]["content"]
    return topic, script

def synthesize_audio(script_text):
    api_key = json.loads(os.environ["ELEVENLABS_KEYS"])[0]
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # 기본 목소리 ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    data = {"text": script_text, "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}}
    response = requests.post(url, headers=headers, json=data)
    audio_path = tempfile.mktemp(suffix=".mp3")
    with open(audio_path, "wb") as f:
        f.write(response.content)
    return audio_path

def create_video(text, audio_path):
    txt_clip = TextClip(text, fontsize=50, color='white', size=(1280, 720), bg_color='black', duration=30)
    txt_clip = txt_clip.set_audio(audio_path).set_duration(txt_clip.duration)
    video_path = tempfile.mktemp(suffix=".mp4")
    txt_clip.write_videofile(video_path, fps=24)
    return video_path

def upload_to_youtube(title, description, video_path):
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=json.loads(os.environ["GOOGLE_CLIENT_SECRET_JSON"])["installed"]["client_id"],
        client_secret=json.loads(os.environ["GOOGLE_CLIENT_SECRET_JSON"])["installed"]["client_secret"]
    )
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["AI", "Automation", "YouTubeBot"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=video_path
    )
    response = request.execute()
    print(f"🚀 Uploaded to YouTube: {response['id']}")


def generate_and_upload():
    title, script = generate_script()
    audio_path = synthesize_audio(script)
    video_path = create_video(script[:300], audio_path)  # 요약 텍스트
    upload_to_youtube(title, script, video_path)
