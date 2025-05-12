# 에러 알림 기능 (이메일/Slack)
# scripts/notifier.py
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_notification(message: str):
    token = os.environ.get('SLACK_API_TOKEN')
    channel = os.environ.get('SLACK_CHANNEL')  # ex. "#general"

    if not token or not channel:
        logging.warning("Slack 알림 설정이 누락됨.")
        return

    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        logging.info(f"Slack 알림 전송 완료: {response['ts']}")
    except SlackApiError as e:
        logging.error(f"Slack 전송 실패: {e.response['error']}")
