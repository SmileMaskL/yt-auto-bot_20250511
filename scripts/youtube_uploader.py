import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video(video_file: str, title: str, thumbnail_file: str):
    creds = Credentials.from_authorized_user_info(json.loads(os.getenv("GOOGLE_TOKEN_JSON")), SCOPES)
    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": title[:100],
            "description": "#shorts 자동 생성 콘텐츠",
            "tags": ["AI", "자동화", "수익화"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=video_file
    )
    response = request.execute()
    video_id = response["id"]
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=thumbnail_file
    ).execute()
    return f"https://www.youtube.com/watch?v={video_id}"
