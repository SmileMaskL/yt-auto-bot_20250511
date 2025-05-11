# 콘텐츠 생성 관련 기능
import random
import json
import os
import logging
from time import sleep
from pytrends.request import TrendReq
import openai

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# OpenAI API 키 로테이션 설정
class OpenAIKeyManager:
    def __init__(self):
        keys = json.loads(os.environ.get("OPENAI_API_KEYS", "[]"))
        if not keys:
            raise ValueError("OPENAI_API_KEYS 환경변수가 설정되지 않았습니다.")
        self.keys = keys
        self.index = 0

    def get_key(self):
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

key_manager = OpenAIKeyManager()

def get_trending_keywords():
    pytrends = TrendReq(hl='ko', tz=540)
    trending_searches = pytrends.trending_searches(pn='south_korea')
    keywords = trending_searches[0].tolist()[:10]
    logging.info(f"트렌드 키워드: {keywords}")
    return keywords

def generate_script(keyword):
    prompt = f"{keyword}에 대한 유튜브 영상 스크립트를 작성해줘."
    for _ in range(len(key_manager.keys)):
        openai.api_key = key_manager.get_key()
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logging.error(f"OpenAI API 호출 오류: {e}")
            sleep(1)
    raise RuntimeError("모든 OpenAI API 키가 실패했습니다.")
