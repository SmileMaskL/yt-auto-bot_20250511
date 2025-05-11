# 에러 알림 기능 (이메일/Slack)
# 에러 알림 기능 (Slack)
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_notification(message):
    client = WebClient(token=os.environ.get('SLACK_API_TOKEN'))
    try:
        response = client.chat_postMessage(
            channel='C05Q8JQEL4U',
            text=message
        )
        logging.info(f"Slack 알림 전송 성공: {response['ts']}")
    except SlackApiError as e:
        logging.error(f"Slack 알림 오류: {e.response['error']}")
