import os
import logging
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_video_to_youtube(title: str, description: str, file_path: str, creds_json: str):
    try:
        creds = Credentials.from_authorized_user_info(info=creds_json)
        youtube = build("youtube", "v3", credentials=creds)

        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["AI", "Automation", "YouTube"]
            },
            "status": {
                "privacyStatus": "public"
            }
        }

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(
            part=",".join(request_body.keys()),
            body=request_body,
            media_body=media
        )

        response = request.execute()
        logger.info(f"✅ Video uploaded successfully: https://youtube.com/watch?v={response['id']}")
        return response['id']

    except HttpError as e:
        logger.error(f"❌ YouTube upload failed: {e}")
        raise e
