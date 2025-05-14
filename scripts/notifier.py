# 에러 알림 기능 (이메일/Slack)
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_notification(message: str):
    try:
        client = WebClient(token=os.getenv("SLACK_API_TOKEN"))
        response = client.chat_postMessage(
            channel=os.getenv("SLACK_CHANNEL"),
            text=message
        )
        logging.info(f"✅ Slack 알림 전송: {response['ts']}")
    except Exception as e:
        logging.error(f"❌ 알림 실패: {str(e)}")
