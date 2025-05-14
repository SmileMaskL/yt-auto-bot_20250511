import openai
import base64
import json
from datetime import datetime

class ContentGenerator:
    def __init__(self):
        self.keys = self._load_keys()
        self.current_key = 0

    def _load_keys(self):
        encoded = os.getenv("OPENAI_API_KEYS_BASE64")
        return json.loads(base64.b64decode(encoded))

    def _get_trends(self):
        return ["AI 동향", "주식 분석", "IT 신기술"]  # 실제로는 트렌드 API 연결

    def generate_script(self, trend):
        openai.api_key = self.keys[self.current_key]
        self.current_key = (self.current_key + 1) % len(self.keys)
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "user",
                "content": f"{datetime.now().strftime('%Y-%m-%d')} {trend} 주제로 300자 영상 대본 생성"
            }]
        )
        return response.choices[0].message.content
