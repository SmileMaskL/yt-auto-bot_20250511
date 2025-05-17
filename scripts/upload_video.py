import os
import pickle
import json
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 유튜브 API scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None
    # token.pickle가 있으면 읽기 (이 예시에서는 token.json으로 저장할거라 token.pickle은 안씀)
    if os.path.exists("token.json"):
        with open("token.json", "r") as token_file:
            token_info = json.load(token_file)
            # 구글 라이브러리 요구하는 Credentials 객체 만들려면 아래 방식으로 (여기선 간단화)
            # 실제로는 google.oauth2.credentials.Credentials로 변환해야 함
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    else:
        # credentials.json 파일이 있어야 인증 가능
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        # 인증 후 token.json 저장
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, file, title, description, category, keywords, privacy_status):
    body = {
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

    media = MediaFileUpload(file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")
    print("Upload Complete!")
    print(f"Video ID: {response['id']}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="업로드할 비디오 파일 경로")
    parser.add_argument("--title", required=True, help="영상 제목")
    parser.add_argument("--description", required=True, help="영상 설명")
    parser.add_argument("--category", default="22", help="카테고리 ID (기본값 22: People & Blogs)")
    parser.add_argument("--keywords", default="", help="키워드(쉼표로 구분)")
    parser.add_argument("--privacy_status", default="private", help="공개 여부 (public, unlisted, private)")

    args = parser.parse_args()

    youtube = get_authenticated_service()
    upload_video(
        youtube,
        args.file,
        args.title,
        args.description,
        args.category,
        args.keywords,
        args.privacy_status,
    )

if __name__ == "__main__":
    main()
