# scripts/notifier.py

import os
import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def send_notification(message: str) -> None:
    """
    SLACK_WEBHOOK_URL을 이용하여 Slack에 메시지를 보냄.
    """
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not slack_webhook_url:
        logger.warning("⚠️ SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다. Slack 알림을 생략합니다.")
        return

    try:
        payload = {"text": message}
        response = requests.post(slack_webhook_url, json=payload)

        if response.status_code == 200:
            logger.info(f"✅ Slack 알림 전송 성공: {message}")
        else:
            logger.error(f"❌ Slack 알림 실패: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"❌ Slack 알림 중 예외 발생: {e}")
