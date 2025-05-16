import openai
import random

class ContentGenerator:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.keywords = ["AI", "Python", "GCP", "YouTube Shorts", "자동화"]

    def generate(self):
        keyword = random.choice(self.keywords)
        prompt = f"{keyword}에 대한 60초 분량의 유익한 스크립트를 작성해줘."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
