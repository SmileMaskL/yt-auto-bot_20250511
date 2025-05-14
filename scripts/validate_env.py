# scripts/validate_env.py
import os
import sys
import json
import base64
import logging

# Configure logging (avoid duplication in reruns)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [validate_env] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True  # Ensures reconfiguration even if already set
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
        if is_secret and var_value
        else f"'{var_value}'"
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
        logging.debug(f"🔧 Raw decoded string was: {decoded_str[:100]}...")
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

def main():
    logging.info("🚀 Starting environment variable validation...")

    required_vars = [
        ("OPENAI_API_KEYS_BASE64", True, False),
        ("GOOGLE_CLIENT_ID", False, False),
        ("GOOGLE_CLIENT_SECRET", True, False),
        ("GOOGLE_REFRESH_TOKEN", True, False),
    ]

    optional_vars = [
        ("SLACK_API_TOKEN", True, True),
        ("SLACK_CHANNEL", False, True),
    ]

    all_valid = True

    logging.info("🔍 Checking required environment variables...")
    for var_name, is_secret, can_be_empty in required_vars:
        if not check_env_var(var_name, is_secret, can_be_empty):
            all_valid = False

    # Only check structure if base64 var is set
    if os.environ.get("OPENAI_API_KEYS_BASE64"):
        if not validate_openai_keys_structure():
            all_valid = False

    logging.info("📎 Checking optional environment variables...")
    for var_name, is_secret, can_be_empty in optional_vars:
        check_env_var(var_name, is_secret, can_be_empty)  # Optional vars do not affect overall validity

    if all_valid:
        logging.info("✅✅✅ All required environment variables and structures are valid.")
        sys.exit(0)
    else:
        logging.error("❌❌❌ One or more critical environment variable checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
