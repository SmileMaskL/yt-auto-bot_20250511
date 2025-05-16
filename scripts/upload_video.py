import os
import pickle
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 인증 및 서비스 객체 생성
def get_authenticated_service():
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json",
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        credentials = flow.run_local_server()
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return build("youtube", "v3", credentials=credentials)

# 동영상 업로드 함수
def upload_video(file, title, description, category, keywords, privacy_status):
    youtube = get_authenticated_service()
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": keywords.split(","),
            "categoryId": category
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }
    media_file = MediaFileUpload(file)
    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    ).execute()
    print(f"동영상이 업로드되었습니다: https://www.youtube.com/watch?v={response['id']}")

# 명령줄 인자 처리
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="업로드할 동영상 파일 경로")
    parser.add_argument("--title", required=True, help="동영상 제목")
    parser.add_argument("--description", required=True, help="동영상 설명")
    parser.add_argument("--category", default="22", help="동영상 카테고리 ID")
    parser.add_argument("--keywords", default="", help="쉼표로 구분된 키워드 목록")
    parser.add_argument("--privacy_status", default="private", choices=["public", "private", "unlisted"], help="공개 상태")
    args = parser.parse_args()
    upload_video(args.file, args.title, args.description, args.category, args.keywords, args.privacy_status)
