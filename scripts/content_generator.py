# 콘텐츠 생성 관련 기능
import random
import json
import os
from pytrends.request import TrendReq
import openai

def get_trending_keywords():
    pytrends = TrendReq(hl='ko', tz=540)
    trending_searches = pytrends.trending_searches(pn='south_korea')
    return trending_searches[0].tolist()[:10]

def get_openai_api_key():
    keys = json.loads(os.environ.get("OPENAI_API_KEYS", "[]"))
    return random.choice(keys)

def generate_script(keyword):
    openai.api_key = get_openai_api_key()
    prompt = f"{keyword}에 대한 유튜브 영상 스크립트를 작성해줘."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    return response.choices[0].text.strip()
