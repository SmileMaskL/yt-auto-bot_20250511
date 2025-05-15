from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def analyze_channel_performance():
    creds = Credentials.from_authorized_user_file('token.json', [
        'https://www.googleapis.com/auth/yt-analytics.readonly'
    ])

    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

    response = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate='2025-01-01',
        endDate='2025-12-31',
        metrics='views,estimatedRevenue',
        dimensions='day'
    ).execute()

    for row in response.get('rows', []):
        print(f"Date: {row[0]}, Views: {row[1]}, Revenue: {row[2]}")
