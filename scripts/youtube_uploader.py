import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video_to_youtube(video_path, title, description, thumbnail_path):
    # OAuth 2.0 인증 정보 로드
    token_json = os.environ.get("GOOGLE_TOKEN_JSON")
    if not token_json:
        raise Exception("GOOGLE_TOKEN_JSON 환경 변수가 설정되지 않았습니다.")
    token_info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(token_info)

    # YouTube API 클라이언트 생성
    youtube = build("youtube", "v3", credentials=creds)

    # 동영상 업로드
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["자동 업로드", "API 테스트"]
        },
        "status": {
            "privacyStatus": "private"
        }
    }
    media = MediaFileUpload(video_path, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    response = request.execute()
    print(f"동영상 업로드 완료: {response['id']}")

    # 썸네일 업로드
    youtube.thumbnails().set(
        videoId=response["id"],
        media_body=MediaFileUpload(thumbnail_path)
    ).execute()
    print("썸네일 업로드 완료")
