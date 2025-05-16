import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials

def upload_video(video_file, title, description, thumbnail_file):
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scopes)
    youtube = build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["AI", "자동화", "유튜브"]
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media_file = MediaFileUpload(video_file)
    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    ).execute()

    youtube.thumbnails().set(
        videoId=response["id"],
        media_body=MediaFileUpload(thumbnail_file)
    ).execute()
