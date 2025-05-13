# 콘텐츠 생성 관련 기능
import random
import json
import os
import logging
from time import sleep
from pytrends.request import TrendReq
# import openai # openai 모듈 직접 임포트 대신 OpenAI 클래스 임포트
from openai import OpenAI # 수정된 부분

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class OpenAIKeyManager:
    def __init__(self): # init -> __init__ 으로 변경하여 클래스 생성 시 자동 호출
        # 환경 변수에서 키 로드 (main.py의 load_openai_keys와 유사하게 Base64 처리 또는 직접 로드)
        # 여기서는 main.py와 동일한 로직을 따르기 위해 OPENAI_API_KEYS를 직접 사용한다고 가정
        # 또는 Base64 디코딩 로직을 여기에 추가할 수 있습니다.
        # 간결성을 위해 여기서는 OPENAI_API_KEYS를 직접 JSON 문자열로 가정합니다.
        
        # main.py의 load_openai_keys 함수를 재사용하거나 유사한 로직 적용
        # 이 예제에서는 간단하게 os.environ.get("OPENAI_API_KEYS")를 사용
        raw_keys_from_env = os.environ.get("OPENAI_API_KEYS")
        if not raw_keys_from_env:
            # OPENAI_API_KEYS_BASE64를 사용하는 경우 (main.py와 동일한 로직)
            encoded_keys = os.environ.get("OPENAI_API_KEYS_BASE64")
            if not encoded_keys:
                logging.error("❌ OPENAI_API_KEYS 또는 OPENAI_API_KEYS_BASE64 환경 변수가 설정되지 않았습니다.")
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
            logging.error(f"❌ OPENAI_API_KEYS 환경변수 JSON 파싱 실패: {e}. RAW 데이터: '{raw_keys_from_env}'")
            raise ValueError(f"OPENAI_API_KEYS 환경변수 JSON 파싱 실패: {e}")
        
        self.index = 0
        if not self.keys: # 파싱 후에도 비어있는 경우
             logging.error("❌ API 키 리스트가 비어있습니다 (파싱 후).")
             raise ValueError("API 키 리스트가 비어있습니다.")


    def get_key(self):
        if not self.keys:
            # 이 경우는 __init__에서 이미 처리되었어야 함
            raise RuntimeError("OpenAI API 키가 로드되지 않았습니다.")
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

key_manager = OpenAIKeyManager() # 클래스 인스턴스 생성 시 __init__ 자동 호출

def get_trending_keywords():
    try:
        pytrends = TrendReq(hl='ko-KR', tz=540) # hl='ko-KR'이 더 정확할 수 있음
        trending_searches_df = pytrends.trending_searches(pn='south_korea') # pn='south_korea' (대한민국)
        if trending_searches_df.empty:
            logging.warning("트렌드 키워드를 가져오지 못했습니다 (결과 없음). 기본 키워드를 사용합니다.")
            return ["대한민국 주요 뉴스", "오늘의 날씨", "IT 기술 동향"] # 기본 키워드 확장
        
        keywords = trending_searches_df.iloc[:, 0].tolist()[:5] # 상위 5개 키워드
        logging.info(f"트렌드 키워드 (상위 {len(keywords)}개): {keywords}")
        return keywords
    except Exception as e:
        logging.error(f"트렌드 키워드 가져오기 실패: {e}")
        return ["대한민국 경제 전망", "최신 영화 순위", "인공지능 발전"] # 에러 시 기본 키워드

def generate_script_from_keyword(keyword): # 함수 이름 변경 (main.py의 generate_script와 구분)
    prompt = f"{keyword}에 대한 흥미로운 사실과 정보를 바탕으로 한 200자 내외의 짧은 유튜브 쇼츠 스크립트를 작성해줘. 마지막에는 시청자에게 질문을 던지거나 콜투액션을 포함해줘."
    
    # key_manager가 이미 인스턴스화되어 있으므로 바로 사용
    if not key_manager.keys: # 키가 없는 경우에 대한 방어 코드
        logging.error("❌ generate_script_from_keyword: 사용 가능한 OpenAI API 키가 없습니다.")
        raise RuntimeError("사용 가능한 OpenAI API 키가 없습니다.")

    # 키 순환 시도
    initial_index = key_manager.index
    for i in range(len(key_manager.keys)):
        current_key = key_manager.get_key() # 다음 키를 가져옴 (get_key 내부에서 index 업데이트)
        try:
            logging.info(f"📜 스크립트 생성 시도 (키: {current_key[:6]}..., 키워드: {keyword})")
            client = OpenAI(api_key=current_key) # 수정된 부분: 클라이언트 생성
            response = client.chat.completions.create( # 수정된 부분: API 호출
                model="gpt-3.5-turbo", # 또는 "gpt-4-turbo" 등 사용 가능한 모델
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates concise and engaging YouTube shorts scripts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300, # 쇼츠이므로 토큰 제한
                temperature=0.7
            )
            generated_text = response.choices[0].message.content.strip()
            logging.info(f"✅ 스크립트 생성 성공 (키: {current_key[:6]}...)")
            return generated_text
        except Exception as e:
            logging.warning(f"API 키 ({current_key[:6]}...) 실패: {e}. 다음 키로 시도합니다. ({i+1}/{len(key_manager.keys)})")
            # 실패한 키가 현재 선택된 키와 동일하면 다음 키로 넘어감 (get_key가 이미 인덱스 변경)
            # 모든 키를 순회했는지 확인하기 위해 initial_index와 비교는 불필요 (range 사용)
            sleep(1) # API 요청 간 짧은 지연

    logging.error("모든 OpenAI API 키를 사용한 스크립트 생성에 실패했습니다.")
    raise RuntimeError("모든 OpenAI API 키가 실패했습니다.")

# 이 파일이 직접 실행될 때 테스트용 코드 (예시)
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
