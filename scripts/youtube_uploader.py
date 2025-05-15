# scripts/youtube_uploader.py

import os
import pickle
import logging
import google.auth.exceptions
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list[str], category_id: str = "22") -> bool:
    """YouTube에 비디오 업로드"""
    creds = None

    if os.path.exists("credentials.pickle"):
        with open("credentials.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("client_secrets.json"):
                    logger.error("❌ client_secrets.json 파일이 없습니다.")
                    return False
                flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
                creds = flow.run_local_server(port=0)
        except google.auth.exceptions.RefreshError as e:
            logger.error(f"❌ 인증 실패: {e}")
            return False
        except Exception as e:
            logger.exception("❌ 인증 도중 예외 발생")
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
        logger.info(f"✅ 업로드 완료! 영상 ID: {response['id']}")
        return True

    except HttpError as e:
        logger.error(f"❌ 업로드 실패: {e}")
    except Exception as e:
        logger.exception("❌ 예외 발생 중 업로드 실패")

    return False
