import os
import json
from datetime import datetime
from openai import OpenAI
from .utils.key_rotator import KeyRotator

class EnhancedContentGenerator:
    """AI 콘텐츠 생성기 3.2 (한글 최적화)"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=KeyRotator(os.getenv("OPENAI_API_KEYS")).get_best_key(),
            timeout=30
        )
        self.template = {
            "intro": "3문장 요약",
            "sections": [
                {"title": "", "content": "", "keywords": []}
            ],
            "conclusion": "핵심 요약"
        }

    def _build_prompt(self, query: str) -> str:
        return f"""🎯 **프롬프트 규칙 v3.2**
1. 주제: {query}에 대한 2025년 최신 동향
2. 출력 형식: JSON (한글)
3. 필수 포함 요소:
   - 기술 용어 5개 이상 설명
   - 산업별 영향도 분석
   - 향후 3년 전망
4. 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M KST')}"""

    def generate(self, query: str) -> dict:
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-2025-04-01",
            messages=[{
                "role": "system",
                "content": self._build_prompt(query)
            }],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
