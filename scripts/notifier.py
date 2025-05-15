import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_notification(message: str, slack_token: str, slack_channel: str):
    client = WebClient(token=slack_token)
    try:
        response = client.chat_postMessage(channel=slack_channel, text=message)
        logger.info("✅ Slack notification sent")
    except SlackApiError as e:
        logger.error(f"❌ Slack notification failed: {e.response['error']}")
