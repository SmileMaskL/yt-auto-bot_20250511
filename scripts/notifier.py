# 에러 알림 기능 (이메일/Slack)
# scripts/notifier.py

import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_notification(message: str):
    token = os.environ.get('SLACK_API_TOKEN')
    channel = os.environ.get('SLACK_CHANNEL')  # 예: "#alerts"

    if not token:
        logging.warning("❌ SLACK_API_TOKEN이 설정되어 있지 않습니다.")
        return

    if not channel:
        logging.warning("❌ SLACK_CHANNEL이 설정되어 있지 않습니다.")
        return

    client = WebClient(token=token)

    try:
        response = client.chat_postMessage(
            channel=channel,
            text=f"📢 [자동화 알림] {message}"
        )
        logging.info(f"✅ Slack 알림 전송 완료: {response['ts']}")
    except SlackApiError as e:
        logging.error(f"❌ Slack API 오류: {e.response['error']}")
