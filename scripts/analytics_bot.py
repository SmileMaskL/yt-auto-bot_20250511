import random

def analyze_performance(video_url):
    return {
        "url": video_url,
        "views": random.randint(100, 10000),
        "likes": random.randint(10, 1000)
    }
