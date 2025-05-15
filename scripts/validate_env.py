import os
import json
import base64


def validate_env_variables() -> bool:
    required_envs = [
        "OPENAI_API_KEYS_BASE64",
        "ELEVENLABS_API_KEY",
        "SLACK_WEBHOOK_URL",
    ]

    for key in required_envs:
        if not os.getenv(key):
            print(f"❌ 환경 변수 누락: {key}")
            return False

    # OPENAI API KEY 형식 검사
    try:
        base64_str = os.getenv("OPENAI_API_KEYS_BASE64")
        decoded = base64.b64decode(base64_str).decode("utf-8")
        json.loads(decoded)
    except Exception as e:
        print(f"❌ OPENAI_API_KEYS_BASE64 디코딩 오류: {e}")
        return False

    print("✅ 환경 변수 검증 완료")
    return True


if __name__ == "__main__":
    result = validate_env_variables()
    exit(0 if result else 1)
