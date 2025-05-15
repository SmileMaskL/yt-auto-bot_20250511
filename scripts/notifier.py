import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

def send_notification(message: str):
    """
    Slack 채널에 메시지를 전송합니다.
    """
    slack_token = os.environ.get("SLACK_API_TOKEN")
    slack_channel = os.environ.get("SLACK_CHANNEL")

    if not slack_token or not slack_channel:
        logger.error("Slack API 토큰 또는 채널 정보가 설정되지 않았습니다.")
        return

    client = WebClient(token=slack_token)

    try:
        client.chat_postMessage(channel=slack_channel, text=message)
    except SlackApiError as e:
        logger.error(f"Slack 알림 전송 실패: {e.response['error']}")
