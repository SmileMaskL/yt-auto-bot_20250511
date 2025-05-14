# scripts/voice_generator.py

import os
import requests
import logging

def generate_voice(text: str, output_path: str, voice_id: str = "Rachel") -> bool:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logging.error("❌ ELEVENLABS_API_KEY 환경 변수가 설정되지 않았습니다.")
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            logging.info(f"✅ 음성 생성 완료: {output_path}")
            return True
        else:
            logging.error(f"❌ 음성 생성 실패. 코드: {response.status_code}, 응답: {response.text}")
            return False
    except Exception as e:
        logging.exception(f"❌ ElevenLabs 음성 생성 중 예외 발생: {e}")
        return False
