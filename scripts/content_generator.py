import openai
import requests

def fetch_trending_topics():
    # 예시: Google Trends API 또는 뉴스 API 사용
    response = requests.get("https://api.example.com/trending")
    topics = response.json().get("topics", [])
    return topics

def generate_content():
    topics = fetch_trending_topics()
    prompt = f"다음 주제에 대한 유익한 스크립트를 작성해주세요: {', '.join(topics)}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    return response.choices[0].text.strip()
