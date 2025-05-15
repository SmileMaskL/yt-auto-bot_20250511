import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_notification(message: str, slack_token: str = None, slack_channel: str = None):
    """
    Slack 알림을 전송합니다. 인자를 직접 전달하거나 환경 변수에서 가져옵니다.
    
    Args:
        message (str): 보낼 메시지 내용
        slack_token (str, optional): Slack Bot Token (기본: SLACK_BOT_TOKEN 환경변수)
        slack_channel (str, optional): Slack 채널 ID (기본: SLACK_CHANNEL_ID 환경변수)
    """
    token = slack_token or os.getenv("SLACK_BOT_TOKEN")
    channel = slack_channel or os.getenv("SLACK_CHANNEL_ID")

    if not token or not channel:
        logger.error("❌ Slack 토큰 또는 채널 ID가 누락되었습니다.")
        return

    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        logger.info("✅ Slack 메시지 전송 완료")
    except SlackApiError as e:
        logger.error(f"❌ Slack 메시지 전송 실패: {e.response['error']}")
