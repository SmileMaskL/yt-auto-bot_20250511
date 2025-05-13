import os
import json
from openai import OpenAI

# JSON 형식의 Secret 로드
OPENAI_KEYS = json.loads(os.getenv("OPENAI_API_KEYS"))

# 각 키를 테스트하고 성공적으로 작동하는지 확인
for idx, key in enumerate(OPENAI_KEYS):
    try:
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": "Connection test"}]
        )
        print(f"✅ Key {idx+1} works!")
        break  # 첫 번째 유효한 키를 찾으면 종료
    except Exception as e:
        print(f"❌ Key {idx+1} failed: {str(e)}")
