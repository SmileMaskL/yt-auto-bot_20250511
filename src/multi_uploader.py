from googleapiclient.discovery import build
from google.oauth2 import service_account

class YouTubeUploader:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            'configs/service_account.json',
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )
        self.youtube = build('youtube', 'v3', credentials=creds)
    
    def upload(self, file_path):
        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "AI 생성 콘텐츠",
                    "description": "#shorts #자동생성"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=file_path
        )
        return request.execute()
