# 콘텐츠 생성 관련 기능
import random
import json
import os
import logging
from time import sleep
from pytrends.request import TrendReq
from openai import OpenAI  # ✅ 새로운 모듈 import 방식

logging.basicConfig(level=logging.INFO)

class OpenAIKeyManager:
    def __init__(self):
        raw_keys = os.environ.get("OPENAI_API_KEYS", "[]")
        try:
            self.keys = json.loads(raw_keys)
            if not self.keys or not isinstance(self.keys, list):
                raise ValueError("API 키 리스트가 비어있거나 형식이 잘못되었습니다.")
        except json.JSONDecodeError as e:
            raise ValueError(f"OPENAI_API_KEYS 환경변수 JSON 파싱 실패: {e}")
        self.index = 0

    def get_key(self):
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

key_manager = OpenAIKeyManager()

def get_trending_keywords():
    try:
        pytrends = TrendReq(hl='ko', tz=540)
        trending_searches = pytrends.trending_searches(pn='south_korea')
        keywords = trending_searches[0].tolist()[:10]
        logging.info(f"트렌드 키워드: {keywords}")
        return keywords
    except Exception as e:
        logging.error(f"트렌드 키워드 가져오기 실패: {e}")
        return ["기본 키워드"]

def generate_script(keyword):
    prompt = f"{keyword}에 대한 유튜브 영상 스크립트를 작성해줘."
    client = OpenAI(api_key=key_manager.get_key())  # ✅ 클라이언트 생성 방식 변경
    for _ in range(len(key_manager.keys)):
        try:
            response = client.chat.completions.create(  # ✅ 새로운 API 호출 방식
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logging.warning(f"API 키 실패, 다음 키 시도 중: {e}")
            sleep(1)
    raise RuntimeError("모든 OpenAI API 키가 실패했습니다.")
