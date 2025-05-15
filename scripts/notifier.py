# scripts/notifier.py

import os
import logging
import requests

logger = logging.getLogger(__name__)

def send_notification(message: str) -> None:
    """Slack Webhook을 통해 메시지를 전송합니다."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("⚠️ SLACK_WEBHOOK_URL 환경변수가 설정되지 않음. Slack 알림 생략.")
        return

    try:
        response = requests.post(webhook_url, json={"text": message})
        if response.status_code == 200:
            logger.info("✅ Slack 알림 전송 성공")
        else:
            logger.error(f"❌ Slack 알림 실패: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception(f"❌ Slack 알림 전송 중 예외 발생: {e}")
