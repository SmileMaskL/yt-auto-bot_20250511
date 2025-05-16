from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

def get_top_video_titles():
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

    video_ids = [item[0] for item in response.get("rows", [])]

    youtube = build("youtube", "v3", credentials=creds)
    titles = []
    for video_id in video_ids:
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        title = video_response["items"][0]["snippet"]["title"]
        titles.append(title)

    return titles
