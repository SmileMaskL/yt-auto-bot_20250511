import feedparser

def get_trending_topics():
    feed = feedparser.parse("https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR")
    topics = [entry.title for entry in feed.entries]
    return topics
