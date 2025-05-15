from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from datetime import datetime, timedelta
import pickle

def analyze_channel_performance():
    """
    지난 7일간의 YouTube 채널 성과를 분석합니다.
    """
    if not os.path.exists("token.pickle"):
        print("토큰 파일(token.pickle)이 존재하지 않습니다. 먼저 인증을 진행하세요.")
        return

    with open("token.pickle", "rb") as token_file:
        creds = pickle.load(token_file)

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
