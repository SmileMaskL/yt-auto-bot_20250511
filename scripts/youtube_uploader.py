from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

def upload_video(video_file, thumbnail_file, title, description=""):
    # 인증 및 서비스 객체 생성
    youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))

    # 영상 업로드
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Shorts", "AI", "Automation"]
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()

    # 썸네일 업로드
    youtube.thumbnails().set(
        videoId=response["id"],
        media_body=MediaFileUpload(thumbnail_file)
    ).execute()
