import openai
from datetime import datetime
from .quantum_key_vault import KeyManager

class ContentGenerator:
    def __init__(self):
        self.key_mgr = KeyManager()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def _get_trends(self):
        # 네이버 실시간 검색어 크롤링
        return ["AI 동향", "주식 분석", "IT 신기술"]
    
    def generate_script(self):
        openai.api_key = self.key_mgr.get_key()
        trends = self._get_trends()
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "user",
                "content": f"{self.today} {trends} 주제로 300자 이내 영상 대본 생성"
            }]
        )
        return response.choices[0].message.content
