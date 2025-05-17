import os
import pickle
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='업로드할 비디오 파일 경로')
    parser.add_argument('--title', required=True, help='비디오 제목')
    parser.add_argument('--description', required=True, help='비디오 설명')
    parser.add_argument('--category', default='22', help='비디오 카테고리 ID')
    parser.add_argument('--keywords', default='', help='비디오 태그 (쉼표로 구분)')
    parser.add_argument('--privacy_status', default='public', help='비디오 공개 상태')
    args = parser.parse_args()

    # 토큰 로드
    with open("token.json", "rb") as token_file:
        credentials = pickle.load(token_file)

    youtube = build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "categoryId": args.category,
            "title": args.title,
            "description": args.description,
            "tags": args.keywords.split(",") if args.keywords else []
        },
        "status": {
            "privacyStatus": args.privacy_status
        }
    }

    media_file = MediaFileUpload(args.file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = request.execute()
    print(f"동영상 업로드 완료: https://www.youtube.com/watch?v={response['id']}")

if __name__ == "__main__":
    main()
