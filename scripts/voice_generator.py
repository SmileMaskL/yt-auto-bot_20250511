
import os
import logging
import requests

logger = logging.getLogger(__name__)


def generate_voice(text: str, output_path: str = "audio_output.mp3") -> str:
    """ElevenLabs API를 사용하여 텍스트를 음성으로 변환"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

    if not api_key:
        raise EnvironmentError("ELEVENLABS_API_KEY가 설정되지 않았습니다.")

    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            },
            json={"text": text, "model_id": "eleven_monolingual_v1"},
        )
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"✅ 음성 생성 완료: {output_path}")
        return output_path
    except Exception as e:
        logger.exception("❌ 음성 생성 실패")
        raise
