# scripts/youtube_uploader.py

import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def upload_video(video_file, script_text, thumbnail_file=None):
    # ✅ 서비스 계정 인증
    credentials = service_account.Credentials.from_service_account_file(
        "config/credentials.json",
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    youtube = build("youtube", "v3", credentials=credentials)

    # ✅ 제목, 설명, 태그 자동 생성
    title = f"🔥 {script_text[:30]}..."
    description = f"{script_text}\n\n#AI #자동화 #YouTubeBot"
    tags = ["AI", "자동화", "YouTube", "GPT", "수익화"]

    # ✅ 업로드 요청 바디
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "public"  # 'private', 'unlisted'도 가능
        }
    }

    # ✅ 영상 업로드
    media_file = MediaFileUpload(video_file)
    try:
        print("🚀 영상 업로드 시작...")
        response = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        ).execute()
        video_id = response.get("id")
        print(f"✅ 영상 업로드 완료! videoId: {video_id}")
    except HttpError as e:
        print(f"❌ 업로드 중 오류 발생: {e}")
        return

    # ✅ 썸네일 업로드 (선택)
    if thumbnail_file:
        try:
            print("🖼️ 썸네일 업로드 시도 중...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            print("✅ 썸네일 업로드 완료!")
        except HttpError as e:
            print(f"⚠️ 썸네일 업로드 실패 (무시됨): {e}")

    print("🎉 유튜브 영상 자동 업로드 전체 완료!")
