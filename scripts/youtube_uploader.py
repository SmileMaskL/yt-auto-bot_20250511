import os
import openai
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from moviepy.editor import TextClip, concatenate_videoclips
from datetime import datetime
from google.auth.transport.requests import Request

def generate_video_from_script(script):
    # 동영상 생성 과정 예시 (자막, 이미지, 음성 등을 합성)
    video_clip = TextClip(script, fontsize=70, color='white').set_duration(10)
    video = concatenate_videoclips([video_clip])
    video_path = "output.mp4"
    video.write_videofile(video_path, codec='libx264')
    return video_path

def upload_to_youtube(video_path, title, description):
    # Google API 인증 및 YouTube 업로드
    youtube = build('youtube', 'v3', credentials=get_google_credentials())
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["automated", "content"],
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=video_path
    )
    request.execute()

def get_google_credentials():
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
    return creds

def generate_and_upload_video():
    try:
        # 1. OpenAI API로 스크립트 생성
        openai.api_key = os.environ.get("OPENAI_API_KEYS")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Generate a script for a trending topic video",
            max_tokens=300
        )
        script = response.choices[0].text.strip()

        # 2. 동영상 생성
        video_path = generate_video_from_script(script)

        # 3. 동영상 업로드
        upload_to_youtube(video_path, "Trending Topic Video", script)

    except Exception as e:
        print(f"🚨 영상 생성 및 업로드 실패: {e}")
        send_error_notification(str(e))
        raise
