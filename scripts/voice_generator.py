# scripts/voice_generator.py

import os
from elevenlabs import generate, save, set_api_key
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def generate_voice(text: str, output_path: str = "output/audio.mp3"):
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        raise ValueError("환경변수 ELEVENLABS_API_KEY 또는 ELEVENLABS_VOICE_ID가 설정되지 않았습니다.")
    
    set_api_key(ELEVENLABS_API_KEY)

    try:
        audio = generate(
            text=text,
            voice=ELEVENLABS_VOICE_ID,
            model="eleven_monolingual_v1"
        )
        save(audio, output_path)
        print(f"✅ 음성 파일 저장 완료: {output_path}")
        return output_path
    except Exception as e:
        print("❌ 음성 생성 중 오류 발생:", str(e))
        raise
