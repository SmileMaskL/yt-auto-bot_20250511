import os
import argparse
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    with open("credentials.json") as f:
        creds_data = json.load(f)

    flow = InstalledAppFlow.from_client_config(creds_data, SCOPES)
    creds = flow.run_console()

    with open("token.json", "wb") as token:
        pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def initialize_upload(youtube, options):
    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=options.keywords.split(","),
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacy_status
        )
    )
    media = MediaFileUpload(options.file, resumable=True)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    response = request.execute()
    print(f"✅ 영상 업로드 성공: https://youtu.be/{response['id']}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--category", default="22")
    parser.add_argument("--keywords", default="자동화,유튜브")
    parser.add_argument("--privacy_status", default="public")
    args = parser.parse_args()

    youtube = get_authenticated_service()
    initialize_upload(youtube, args)

if __name__ == '__main__':
    main()
