# scripts/validate_env.py

import os
import sys
import json
import base64
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [validate_env] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

def check_env_var(var_name: str, is_secret: bool = True, can_be_empty: bool = False) -> bool:
    var_value = os.environ.get(var_name)
    if var_value is None:
        logging.error(f"🚨 환경 변수 '{var_name}'이 설정되지 않았습니다.")
        return False
    if not can_be_empty and not var_value.strip():
        logging.error(f"🚨 환경 변수 '{var_name}'이 비어 있습니다.")
        return False

    display_value = (
        f"{var_value[:2]}...{var_value[-2:]} (길이: {len(var_value)})" if is_secret else var_value
    )
    logging.info(f"✅ 환경 변수 '{var_name}' 확인 완료. 값: {display_value}")
    return True

def validate_openai_keys_structure(env_var_name: str = "OPENAI_API_KEYS_BASE64") -> bool:
    encoded_keys = os.environ.get(env_var_name, "").strip()
    if not encoded_keys:
        logging.error(f"🚨 {env_var_name} 환경 변수가 비어 있거나 존재하지 않습니다.")
        return False

    logging.info(f"🔍 {env_var_name} 구조 유효성 검사 시작...")
    try:
        decoded_bytes = base64.b64decode(encoded_keys, validate=True)
        decoded_str = decoded_bytes.decode("utf-8")
        parsed_keys = json.loads(decoded_str)
    except Exception as e:
        logging.error(f"🚨 base64 디코딩 또는 JSON 파싱 실패: {e}")
        return False

    if not isinstance(parsed_keys, list) or not parsed_keys:
        logging.error(f"🚨 {env_var_name} 값은 유효한 리스트가 아닙니다.")
        return False

    valid = True
    for i, key in enumerate(parsed_keys):
        if not isinstance(key, str) or not key.startswith("sk-"):
            logging.error(f"🚨 인덱스 {i}의 키가 유효하지 않음: {key}")
            valid = False
        elif len(key) < 20:
            logging.warning(f"⚠️ 인덱스 {i}의 키가 비정상적으로 짧습니다.")

    if valid:
        logging.info(f"✅ {len(parsed_keys)}개의 OpenAI 키가 유효합니다.")
    return valid

def check_required_envs() -> bool:
    required_envs = [
        "OPENAI_API_KEYS_BASE64",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REFRESH_TOKEN",
        "SLACK_API_TOKEN",
        "SLACK_CHANNEL",
        "ELEVENLABS_API_KEY",
        "SLACK_WEBHOOK_URL"
    ]
    missing = [key for key in required_envs if not os.getenv(key)]
    if missing:
        logging.error(f"🚨 필수 환경 변수 누락: {', '.join(missing)}")
        return False
    return True

def validate_env() -> bool:
    logging.info("🔎 환경 변수 유효성 검사 실행 중...")
    required = check_required_envs()
    structure_ok = validate_openai_keys_structure()
    return required and structure_ok

def main():
    logging.info("🚀 전체 환경 변수 점검 시작...")

    if not validate_env():
        logging.error("❌ 유효하지 않은 환경 변수로 인해 중단됩니다.")
        sys.exit(1)

    logging.info("✅ 모든 환경 변수 유효성 검사 통과.")
    sys.exit(0)

if __name__ == "__main__":
    main()
