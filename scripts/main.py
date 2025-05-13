# 전체 자동화 파이썬 코드
import os
import openai
import json
import requests
import subprocess
import wave
import logging
from datetime import datetime
from contextlib import closing
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from scripts.notifier import send_notification
import random
import base64

# 로깅 설정
LOG_FILE = "automation.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log(msg):
    logging.info(msg)

def load_openai_keys():
    try:
        encoded = os.environ.get("OPENAI_API_KEYS_BASE64", "")
        if not encoded:
            raise ValueError("❌ OPENAI_API_KEYS_BASE64 환경변수가 설정되지 않았습니다.")

        # Base64 디코딩
        decoded = base64.b64decode(encoded).decode("utf-8")

        # JSON 파싱
        keys = json.loads(decoded)
        if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
            raise ValueError("❌ OPENAI_API_KEYS는 문자열 배열(JSON 리스트)이어야 합니다.")

        logging.info("✅ OPENAI_API_KEYS 로딩 성공")
        return keys

    except Exception as e:
        logging.error("❌ OPENAI_API_KEYS JSON 파싱 실패")
        logging.error(f"❌ 오류 발생: {str(e)}")
        raise RuntimeError("❌ 치명적 오류: OPENAI_API_KEYS 환경변수가 잘못된 형식입니다.")

def get_valid_openai_response(prompt):
    try:
        # OPENAI_API_KEYS 환경변수 로드
        api_keys = load_openai_keys()
        
        if not api_keys:
            raise ValueError("OPENAI_API_KEYS 환경변수가 비어있습니다.")
        
        # 무작위로 OpenAI API 키를 선택
        openai.api_key = random.choice(api_keys).strip()
        log(f"🔑 OpenAI 키 시도: {openai.api_key[:6]}...")

        try:
            # OpenAI 클라이언트 초기화
            client = openai.ChatCompletion
            response = client.create(
                model="gpt-3.5-turbo",  # 무료 모델로 변경
                messages=[{"role": "user", "content": prompt}],
                timeout=20
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            log(f"❌ OpenAI 요청 실패: {str(e)}")
            raise
    except Exception as e:
        log(f"❌ 오류 발생: {str(e)}")
        raise

# 나머지 함수들 (generate_voice, get_audio_duration, generate_subtitles, create_video, upload_to_youtube) 동일하게 유지

def main():
    log("🚀 자동화 시작")
    try:
        prompt = "오늘의 대한민국 트렌드를 5가지 요약해줘."
        script = get_valid_openai_response(prompt)
        log(f"📜 생성된 스크립트:\n{script}")

        audio_file = "output.mp3"
        generate_voice(script, audio_file)

        duration = get_audio_duration(audio_file)
        log(f"⏱ 음성 길이: {duration:.2f}초")

        subtitle_file = "subtitles.srt"
        generate_subtitles(script, subtitle_file, duration)

        video_file = "final_video.mp4"
        create_video(audio_file, subtitle_file, video_file, duration)

        video_url = upload_to_youtube(
            video_file,
            "AI 자동 생성 영상",
            "이 영상은 AI를 통해 자동으로 생성되었습니다."
        )
        send_notification(f"✅ 영상 업로드 완료: {video_url}")
    except Exception as e:
        log(f"❌ 치명적 오류: {str(e)}")
        send_notification(f"🚨 자동화 실패: {str(e)}")
    finally:
        log("🏁 자동화 종료")

if __name__ == "__main__":
    main()
