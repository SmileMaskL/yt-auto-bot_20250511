# 콘텐츠 생성 관련 기능
import random
import json
import os
import logging
from time import sleep
from pytrends.request import TrendReq
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class OpenAIKeyManager:
    def __init__(self):
        # Base64 인코딩된 키 로드
        encoded_keys = os.environ.get("OPENAI_API_KEYS_BASE64")
        if not encoded_keys:
            logging.error("❌ OPENAI_API_KEYS_BASE64 환경 변수가 설정되지 않았습니다.")
            raise ValueError("OpenAI API 키 환경 변수가 설정되지 않았습니다.")
        
        try:
            import base64
            raw_keys_from_env = base64.b64decode(encoded_keys).decode('utf-8')
            logging.info("✅ OPENAI_API_KEYS_BASE64를 성공적으로 디코딩했습니다.")
        except Exception as e:
            logging.error(f"❌ OPENAI_API_KEYS_BASE64 디코딩 실패: {e}")
            raise ValueError(f"OPENAI_API_KEYS_BASE64 디코딩 실패: {e}")

        try:
            self.keys = json.loads(raw_keys_from_env)
            if not self.keys or not isinstance(self.keys, list) or not all(isinstance(k, str) for k in self.keys):
                logging.error(f"❌ API 키 리스트가 비어있거나 형식이 잘못되었습니다. 수신된 키: {self.keys}")
                raise ValueError("API 키 리스트가 비어있거나 형식이 잘못되었습니다.")
            logging.info(f"✅ OpenAIKeyManager: {len(self.keys)}개의 API 키 로드됨.")
        except json.JSONDecodeError as e:
            logging.error(f"❌ OPENAI_API_KEYS_BASE64 환경변수 JSON 파싱 실패: {e}. RAW 데이터: '{raw_keys_from_env}'")
            raise ValueError(f"OPENAI_API_KEYS_BASE64 환경변수 JSON 파싱 실패: {e}")
        
        self.index = 0
        if not self.keys:
             logging.error("❌ API 키 리스트가 비어있습니다 (파싱 후).")
             raise ValueError("API 키 리스트가 비어있습니다.")

    def get_key(self):
        if not self.keys:
            raise RuntimeError("OpenAI API 키가 로드되지 않았습니다.")
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

# 키 매니저 인스턴스화는 함수 내에서 필요할 때 처리
def get_key_manager():
    global key_manager
    if 'key_manager' not in globals() or key_manager is None:
        key_manager = OpenAIKeyManager()
    return key_manager

def get_trending_keywords():
    try:
        pytrends = TrendReq(hl='ko-KR', tz=540)
        trending_searches_df = pytrends.trending_searches(pn='south_korea')
        if trending_searches_df.empty:
            logging.warning("트렌드 키워드를 가져오지 못했습니다 (결과 없음). 기본 키워드를 사용합니다.")
            return ["대한민국 주요 뉴스", "오늘의 날씨", "IT 기술 동향"]
        
        keywords = trending_searches_df.iloc[:, 0].tolist()[:5]
        logging.info(f"트렌드 키워드 (상위 {len(keywords)}개): {keywords}")
        return keywords
    except Exception as e:
        logging.error(f"트렌드 키워드 가져오기 실패: {e}")
        return ["대한민국 경제 전망", "최신 영화 순위", "인공지능 발전"]

def generate_script_from_keyword(keyword):
    prompt = f"{keyword}에 대한 흥미로운 사실과 정보를 바탕으로 한 200자 내외의 짧은 유튜브 쇼츠 스크립트를 작성해줘. 마지막에는 시청자에게 질문을 던지거나 콜투액션을 포함해줘."
    
    # 키 매니저 가져오기
    km = get_key_manager()
    
    # 키 순환 시도
    initial_index = km.index
    for i in range(len(km.keys)):
        current_key = km.get_key()
        try:
            logging.info(f"📜 스크립트 생성 시도 (키: {current_key[:6]}..., 키워드: {keyword})")
            client = OpenAI(api_key=current_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates concise and engaging YouTube shorts scripts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            generated_text = response.choices[0].message.content.strip()
            logging.info(f"✅ 스크립트 생성 성공 (키: {current_key[:6]}...)")
            return generated_text
        except Exception as e:
            logging.warning(f"API 키 ({current_key[:6]}...) 실패: {e}. 다음 키로 시도합니다. ({i+1}/{len(km.keys)})")
            sleep(1)

    logging.error("모든 OpenAI API 키를 사용한 스크립트 생성에 실패했습니다.")
    raise RuntimeError("모든 OpenAI API 키가 실패했습니다.")

# 이 파일이 직접 실행될 때 테스트용 코드
if __name__ == "__main__":
    logging.info("content_generator.py 직접 실행 테스트 시작")
    try:
        keywords = get_trending_keywords()
        if keywords:
            selected_keyword = random.choice(keywords)
            logging.info(f"선택된 테스트 키워드: {selected_keyword}")
            script = generate_script_from_keyword(selected_keyword)
            logging.info(f"생성된 스크립트:\n{script}")
        else:
            logging.warning("테스트할 키워드가 없습니다.")
    except Exception as e:
        logging.error(f"content_generator.py 테스트 중 오류: {e}")
