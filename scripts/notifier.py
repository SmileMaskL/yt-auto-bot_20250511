import os
import requests

def send_slack_notification(video_url, stats):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    text = f"🎬 업로드 완료!\n📺 {video_url}\n👀 조회수: {stats['views']} 👍 좋아요: {stats['likes']}"
    requests.post(webhook_url, json={"text": text})
