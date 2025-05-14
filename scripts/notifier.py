# scripts/notifier.py
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Use the root logger configured in main.py or configure one if this module is used standalone
logger = logging.getLogger(__name__) # Using __name__ gets a logger specific to this module

# Basic configuration if this module is run standalone or imported before main.py configures root
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")


def send_notification(message: str):
    """Sends a notification message, currently configured for Slack."""
    slack_api_token = os.getenv("SLACK_API_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL")

    if not slack_api_token or not slack_channel:
        logger.warning("⚠️ Slack API token or channel not set. Cannot send notification.")
        return

    try:
        client = WebClient(token=slack_api_token)
        response = client.chat_postMessage(
            channel=slack_channel,
            text=message
        )
        logger.info(f"✅ Slack notification sent successfully. Message ID: {response.get('ts')}")
    except SlackApiError as e:
        logger.error(f"❌ Slack API error while sending notification: {e.response['error'] if e.response else e}")
    except Exception as e:
        logger.error(f"❌ Failed to send Slack notification due to an unexpected error: {str(e)}")

if __name__ == "__main__":
    # Example of direct usage for testing
    logger.info("Testing Slack notifier...")
    if os.getenv("SLACK_API_TOKEN") and os.getenv("SLACK_CHANNEL"):
        send_notification("This is a test notification from the YouTube automation script's notifier module!")
        logger.info("Test notification sent (if configured).")
    else:
        logger.warning("SLACK_API_TOKEN and/or SLACK_CHANNEL environment variables not set. Skipping test notification.")
