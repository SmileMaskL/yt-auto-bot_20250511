from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from datetime import datetime, timedelta

def analyze_channel_performance():
    creds_path = "token.pickle"
    if not os.path.exists(creds_path):
        print("토큰이 존재하지 않습니다. 먼저 인증을 완료하세요.")
        return

    creds = Credentials.from_authorized_user_file(
        creds_path,
        ["https://www.googleapis.com/auth/yt-analytics.readonly"]
    )
    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)

    today = datetime.utcnow().date()
    last_week = today - timedelta(days=7)

    try:
        request = youtube_analytics.reports().query(
            ids="channel==MINE",
            startDate=last_week.isoformat(),
            endDate=today.isoformat(),
            metrics="views,estimatedRevenue",
            dimensions="day",
            sort="day"
        )
        response = request.execute()

        total_views = 0
        total_revenue = 0.0
        for row in response.get("rows", []):
            views, revenue = row
            total_views += int(views)
            total_revenue += float(revenue)

        print(f"지난 7일간 조회수: {total_views}")
        print(f"추정 수익: ${total_revenue:.2f}")

    except Exception as e:
        print(f"분석 중 오류 발생: {str(e)}")
