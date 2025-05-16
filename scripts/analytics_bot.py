from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def analyze_channel_performance():
    creds = Credentials.from_authorized_user_file("credentials.json", ["https://www.googleapis.com/auth/yt-analytics.readonly"])
    analytics = build("youtubeAnalytics", "v2", credentials=creds)

    response = analytics.reports().query(
        ids="channel==MINE",
        startDate="2025-01-01",
        endDate="2025-12-31",
        metrics="views,estimatedMinutesWatched,averageViewDuration",
        dimensions="day",
        sort="day"
    ).execute()

    # 분석 결과를 파일로 저장
    with open("analytics_report.json", "w") as f:
        json.dump(response, f, indent=4)
