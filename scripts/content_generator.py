# 콘텐츠 생성 관련 기능
import random
import json
import os
from pytrends.request import TrendReq
import openai
import logging
from time import sleep

# 로깅 설정
logging.basicConfig(level=logging.INFO)

def get_trending_keywords():
    pytrends = TrendReq(hl='ko', tz=540)
    trending_searches = pytrends.trending_searches(pn='south_korea')
    logging.info(f"트렌드 키워드: {trending_searches[0].tolist()[:10]}")
    return trending_searches[0].tolist()[:10]

def get_openai_api_key():
    keys = json.loads(os.environ.get("OPENAI_API_KEYS", "[]"))
    return random.choice(keys)

def generate_script(keyword):
    openai.api_key = get_openai_api_key()
    prompt = f"{keyword}에 대한 유튜브 영상 스크립트를 작성해줘."
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"OpenAI API 호출 오류: {e}")
        sleep(5)
        return generate_script(keyword)
