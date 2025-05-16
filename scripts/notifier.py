import requests
import os

def send_notification(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    payload = {"text": message}
    requests.post(webhook_url, json=payload)
