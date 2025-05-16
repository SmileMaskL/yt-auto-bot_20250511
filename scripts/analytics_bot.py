from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

def get_top_videos():
    creds = service_account.Credentials.from_service_account_file(
        "config/credentials.json",
        scopes=["https://www.googleapis.com/auth/yt-analytics.readonly"]
    )
    analytics = build("youtubeAnalytics", "v2", credentials=creds)

    today = datetime.date.today()
    last_7_days = today - datetime.timedelta(days=7)

    response = analytics.reports().query(
        ids="channel==MINE",
        startDate=last_7_days.isoformat(),
        endDate=today.isoformat(),
        metrics="views",
        dimensions="video",
        sort="-views",
        maxResults=3
    ).execute()

    top_video_ids = [item["video"] for item in response.get("rows", [])]
    return top_video_ids
