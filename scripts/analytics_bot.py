from googleapiclient.discovery import build
import os

api_key = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=api_key)

def get_top_video_titles():
    request = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode="KR",
        maxResults=5
    )
    response = request.execute()
    return [item['snippet']['title'] for item in response['items']]
