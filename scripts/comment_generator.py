import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

def post_comment(video_id, text):
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scopes)
    youtube = build("youtube", "v3", credentials=credentials)

    youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": text
                    }
                }
            }
        }
    ).execute()
