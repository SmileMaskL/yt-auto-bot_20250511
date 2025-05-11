# 에러 알림 기능 (이메일/Slack)
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_notification(message):
    token = os.environ.get('SLACK_API_TOKEN')
    if not token:
        logging.warning("SLACK_API_TOKEN이 설정되어 있지 않습니다.")
        return

    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(
            channel="#alerts",  # 원하는 Slack 채널
            text=f"[자동화 봇 알림] {message}"
        )
        logging.info(f"Slack 알림 전송 완료: {response['ts']}")
    except SlackApiError as e:
        logging.error(f"Slack API 오류: {e.response['error']}")
