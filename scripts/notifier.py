# 에러 알림 기능 (이메일/Slack)
# scripts/notifier.py
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_notification(message: str):
    token = os.environ.get('SLACK_API_TOKEN')
    channel = os.environ.get('SLACK_CHANNEL')
    
    if not token or not channel:
        logging.warning("Slack 알림 토큰 또는 채널이 설정되지 않았습니다.")
        return
    
    client = WebClient(token=token)
    
    try:
        client.chat_postMessage(channel=channel, text=message)
        logging.info("✅ Slack 알림 전송 성공")
    except SlackApiError as e:
        logging.error(f"❌ Slack 알림 실패: {e.response['error']}")
