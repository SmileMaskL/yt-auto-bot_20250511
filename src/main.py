from datetime import datetime
import requests
from .ai_content_engine import ContentGenerator
from .video_generator import VideoProducer
from .multi_uploader import YouTubeUploader

def get_trending_topics():
    """실시간 인기 검색어 수집"""
    res = requests.get("https://api.trends.kr/v1/trends")
    return [item['keyword'] for item in res.json()[:3]]

def main(upload_count=15):
    topics = get_trending_topics()
    for _ in range(upload_count):
        content = ContentGenerator().create(topics)
        video_path = VideoProducer().render(content)
        YouTubeUploader().upload(video_path)
        print(f"[{datetime.now()}] 성공적 업로드: {video_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-count", type=int, default=15)
    args = parser.parse_args()
    main(args.upload_count)
