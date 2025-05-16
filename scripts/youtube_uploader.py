from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def upload_video_to_youtube(video_path, title, description, tags, thumbnail_path):
    creds = Credentials.from_authorized_user_file("credentials.json", ["https://www.googleapis.com/auth/youtube.upload"])
    youtube = build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media_file = MediaFileUpload(video_path)

    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    ).execute()

    # 썸네일 업로드
    youtube.thumbnails().set(
        videoId=response["id"],
        media_body=MediaFileUpload(thumbnail_path)
    ).execute()
