# YouTube 업로드 관련 기능
import os
import json
import random
from moviepy.editor import TextClip, AudioFileClip, ImageClip, CompositeVideoClip
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def get_elevenlabs_api_key():
    keys = json.loads(os.environ.get("ELEVENLABS_KEYS", "[]"))
    return random.choice(keys)

def generate_tts_audio(script, filename="output.mp3"):
    api_key = get_elevenlabs_api_key()
    url = "https://api.elevenlabs.io/v1/text-to-speech"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": script,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=data)
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

def create_thumbnail(keyword, filename="thumbnail.jpg"):
    img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 60)
    draw.text((100, 300), keyword, fill=(255, 255, 0), font=font)
    img.save(filename)
    return filename

def create_video(script, audio_file, thumbnail_file, output_file="output.mp4"):
    audio = AudioFileClip(audio_file)
    image = ImageClip(thumbnail_file).set_duration(audio.duration)
    text = TextClip(script, fontsize=24, color='white').set_duration(audio.duration)
    video = CompositeVideoClip([image, text.set_position('bottom')])
    video = video.set_audio(audio)
    video.write_videofile(output_file, fps=24)
    return output_file

def get_authenticated_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.upload'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', ['https://www.googleapis.com/auth/youtube.upload'])
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, video_file, title, description, thumbnail_file):
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['자동화', '트렌드', '유튜브']
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    media = MediaFileUpload(video_file, resumable=True)
    response = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    ).execute()
    video_id = response.get('id')

    # 썸네일 업로드
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=thumbnail_file
    ).execute()

    return video_id

def post_comment(youtube, video_id, comment_text):
    request = youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment_text
                    }
                }
            }
        }
    )
    request.execute()
