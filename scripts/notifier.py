# 에러 알림 기능 (이메일/Slack)
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_notification(message):
    client = WebClient(token=os.environ['SLACK_API_TOKEN'])
    try:
        response = client.chat_postMessage(
            channel='C05Q8JQEL4U',
            text=message
        )
    except SlackApiError as e:
        print(f"Slack 알림 오류: {e.response['error']}")
