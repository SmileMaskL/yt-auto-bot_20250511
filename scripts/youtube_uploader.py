import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_console()
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(video_path: str, title: str, thumbnail_path: str):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": title,
            "tags": ["자동생성", "AI", "YouTube"],
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    # 비디오 업로드
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=video_path
    )
    response = request.execute()

    video_id = response.get("id")
    if video_id:
        # 썸네일 업로드
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=thumbnail_path
        ).execute()
