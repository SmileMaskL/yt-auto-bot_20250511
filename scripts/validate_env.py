import os
import sys

REQUIRED_ENV_VARS = [
    "OPENAI_API_KEYS_BASE64",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "GOOGLE_TOKEN_JSON",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    "SLACK_API_TOKEN",
    "SLACK_CHANNEL",
    "SLACK_WEBHOOK_URL",
]

def validate_env_vars():
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
    if missing_vars:
        print("❌ 다음 환경 변수가 설정되지 않았습니다:")
        for var in missing_vars:
            print(f"- {var}")
        sys.exit(1)
    else:
        print("✅ 모든 필수 환경 변수가 설정되어 있습니다.")

if __name__ == "__main__":
    validate_env_vars()
