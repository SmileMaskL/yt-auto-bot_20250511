# scripts/youtube_uploader.py

import os
import logging
import google.auth.exceptions
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list[str], category_id: str = "22") -> bool:
    creds = None

    if os.path.exists("credentials.pickle"):
        with open("credentials.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("client_secrets.json"):
                logging.error("❌ client_secrets.json 파일이 누락되었습니다.")
                return False
            try:
                flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
                creds = flow.run_local_server(port=0)
            except google.auth.exceptions.RefreshError as e:
                logging.error(f"❌ 인증 토큰 갱신 실패: {e}")
                return False

        with open("credentials.pickle", "wb") as token:
            pickle.dump(creds, token)

    try:
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public"
            }
        }

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=video_path
        )
        response = request.execute()
        logging.info(f"✅ 업로드 완료. 비디오 ID: {response['id']}")
        return True
    except HttpError as e:
        logging.error(f"❌ YouTube 업로드 실패: {e}")
        return False
