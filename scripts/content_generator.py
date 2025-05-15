import random

class ContentGenerator:
    """
    예시: 실제로는 AI API, GPT, 또는
    데이터베이스 기반 콘텐츠 생성으로 대체하세요.
    """
    def __init__(self):
        self.samples = [
            "오늘의 건강 팁: 물을 많이 마시세요.",
            "효과적인 공부 방법 5가지 소개합니다.",
            "여름철 피부 관리 비법 알려드려요.",
            "집에서 할 수 있는 간단 요가 동작.",
            "최신 IT 기술 트렌드 정리."
        ]

    def generate(self) -> str:
        return random.choice(self.samples)
