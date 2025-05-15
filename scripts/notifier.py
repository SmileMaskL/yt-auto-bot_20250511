import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_notification(message: str):
    """
    Slack 알림 전송 함수
    환경변수 SLACK_API_TOKEN, SLACK_CHANNEL에서 자동 토큰과 채널을 가져옴
    """
    slack_token = os.getenv("SLACK_API_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL")

    if not slack_token or not slack_channel:
        logger.error("Slack API 토큰 또는 채널 정보가 설정되지 않았습니다.")
        return

    client = WebClient(token=slack_token)
    try:
        client.chat_postMessage(channel=slack_channel, text=message)
        logger.info("✅ Slack notification sent")
    except SlackApiError as e:
        logger.error(f"❌ Slack notification failed: {e.response['error']}")
