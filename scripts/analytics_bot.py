from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

def analyze_channel_performance():
    creds_path = "token.pickle"
    if not os.path.exists(creds_path):
        print("토큰이 존재하지 않습니다. 먼저 인증을 완료
