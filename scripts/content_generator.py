import random

class ContentGenerator:
    def __init__(self):
        self.topics = [
            "AI 기술의 미래",
            "하루 10분 투자로 돈 버는 방법",
            "2025년 인기 유튜브 트렌드",
            "챗GPT로 자동화하는 유튜브 수익"
        ]

    def generate(self) -> str:
        return random.choice(self.topics)
