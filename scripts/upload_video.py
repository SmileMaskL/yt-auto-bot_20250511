import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

scopes = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    # OAuth 인증
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", scopes)
    credentials = flow.run_local_server(port=0)

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    # 업로드할 동영상 파일 경로
    video_file = "video.mp4"

    # 동영상 메타데이터 설정
    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": "자동 업로드 테스트",
            "description": "이것은 자동 업로드 테스트입니다.",
            "tags": ["자동", "업로드", "테스트"]
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    mediaFile = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    # 동영상 업로드 요청
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=mediaFile
    )

    response = request.execute()
    print(f"동영상 업로드 완료: https://www.youtube.com/watch?v={response['id']}")

if __name__ == "__main__":
    main()
