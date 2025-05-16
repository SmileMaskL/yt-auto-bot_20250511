import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SERVICE_ACCOUNT_FILE = "config/credentials.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
youtube = build("youtube", "v3", credentials=credentials)

def upload_video(video_path, title, description, thumbnail_path):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Shorts", "AI", "Automation"]
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=video_path
    )
    response = request.execute()

    youtube.thumbnails().set(
        videoId=response['id'],
        media_body=thumbnail_path
    ).execute()
