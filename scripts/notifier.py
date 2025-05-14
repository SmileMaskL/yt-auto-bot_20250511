# scripts/notifier.py

import os
import logging
import requests

def send_notification(message: str) -> None:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logging.warning("⚠️ SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다. Slack 알림을 생략합니다.")
        return

    try:
        response = requests.post(webhook_url, json={"text": message})
        if response.status_code == 200:
            logging.info("✅ Slack 알림 전송 성공")
        else:
            logging.error(f"❌ Slack 알림 실패: {response.status_code} - {response.text}")
    except Exception as e:
        logging.exception(f"❌ Slack 알림 중 예외 발생: {e}")
