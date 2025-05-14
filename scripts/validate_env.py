# scripts/validate_env.py

import os
import sys
import logging
import base64
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [validate_env] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

def check_env_var(var_name: str, is_secret: bool = True, can_be_empty: bool = False) -> bool:
    """Check if a single environment variable is set correctly."""
    var_value = os.environ.get(var_name)
    
    if var_value is None:
        logging.error(f"🚨 Environment variable '{var_name}' is NOT SET.")
        return False

    if not can_be_empty and not var_value.strip():
        logging.error(f"🚨 Environment variable '{var_name}' is SET but EMPTY.")
        return False

    display_value = (
        f"'{var_value[:2]}...{var_value[-2:]}' (length: {len(var_value)})"
        if is_secret and var_value else f"'{var_value}'"
    )
    logging.info(f"✅ Environment variable '{var_name}' is SET. Value: {display_value}")
    return True


def validate_openai_keys_structure(env_var_name: str = "OPENAI_API_KEYS_BASE64") -> bool:
    """Validates OPENAI_API_KEYS_BASE64 contains valid base64-encoded JSON list of sk- keys."""
    encoded_keys = os.environ.get(env_var_name, "").strip()

    if not encoded_keys:
        logging.error(f"🚨 {env_var_name} is not set or empty. Cannot validate structure.")
        return False

    logging.info(f"🔍 Validating structure of {env_var_name}...")

    try:
        decoded_bytes = base64.b64decode(encoded_keys, validate=True)
        decoded_str = decoded_bytes.decode("utf-8")
    except Exception as e:
        logging.error(f"🚨 Base64 decoding failed for {env_var_name}: {e}")
        return False

    try:
        parsed_keys = json.loads(decoded_str)
    except json.JSONDecodeError as e:
        logging.error(f"🚨 JSON parsing failed for decoded {env_var_name}: {e}")
        return False

    if not isinstance(parsed_keys, list) or not parsed_keys:
        logging.error(f"🚨 Decoded {env_var_name} is not a non-empty list.")
        return False

    valid_keys = True
    for i, key in enumerate(parsed_keys):
        if not isinstance(key, str) or not key.startswith("sk-"):
            logging.error(f"🚨 Key at index {i} is invalid: {key}")
            valid_keys = False
        elif len(key) < 20:
            logging.warning(f"⚠️ Key at index {i} seems unusually short.")

    if valid_keys:
        logging.info(f"🔐 Successfully validated structure: {len(parsed_keys)} keys found.")
        return True
    else:
        return False


def check_required_envs() -> bool:
    """Check all required environment variables are set."""
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
        logging.error(f"🚨 Missing required environment variables: {', '.join(missing)}")
        return False
    logging.info("✅ All required environment variables are set.")
    return True


def main():
    logging.info("🚀 Starting environment variable validation...")

    # Step 1: Check required environment variables
    logging.info("🔍 Checking required environment variables...")
    if not check_required_envs():
        sys.exit(1)

    # Step 2: Validate structure of the OPENAI_API_KEYS_BASE64
    if os.environ.get("OPENAI_API_KEYS_BASE64"):
        if not validate_openai_keys_structure():
            sys.exit(1)

    logging.info("✅ All required environment variables and structures are valid.")
    sys.exit(0)

if __name__ == "__main__":
    main()
