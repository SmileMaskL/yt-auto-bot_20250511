from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import time

def upload_video(video_path, title, thumbnail_path=None):
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
    creds = service_account.Credentials.from_service_account_file("config/credentials.json", scopes=SCOPES)
    youtube = build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": "자동 생성된 영상입니다.",
            "tags": ["AI", "Shorts", "자동화", "트렌드"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media_file = MediaFileUpload(video_path, mimetype="video/*", resumable=True)
    response_upload = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media_file).execute()
    video_id = response_upload["id"]

    # 썸네일 업로드
    if thumbnail_path:
        youtube.thumbnails().set(videoId=video_id, media_body=thumbnail_path).execute()

    print(f"✅ 업로드 완료: https://youtu.be/{video_id}")

    # 댓글 자동 작성
    youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": "이 영상이 마음에 드셨다면 좋아요와 구독 부탁드려요! 😊"
                    }
                }
            }
        }
    ).execute()
