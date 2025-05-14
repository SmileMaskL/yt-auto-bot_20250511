from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from .utils.bandwidth_checker import BandwidthOptimizer

class SmartUploader:
    """YouTube 업로더 3.3 (대역폭 자동 최적화)"""
    
    def __init__(self):
        self.credentials = Credentials.from_authorized_user_file(
            'token.json',
            ['https://www.googleapis.com/auth/youtube.upload']
        )
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        self.optimizer = BandwidthOptimizer()

    def _prepare_metadata(self, title: str) -> dict:
        return {
            "snippet": {
                "title": title,
                "description": "AI 자동 생성 콘텐츠",
                "categoryId": "28"  # 과학/기술
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

    def upload(self, file_path: str, title: str) -> str:
        self.optimizer.adjust_chunk_size()
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=self._prepare_metadata(title),
            media_body=file_path
        )
        response = request.execute()
        return f"https://youtu.be/{response['id']}"
