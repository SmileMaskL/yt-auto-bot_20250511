# scripts/validate_env.py
import os
import sys
import json
import base64
import logging

# Configure basic logging for this validation script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [validate_env] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)] # Log to console
)

def check_env_var(var_name: str, is_secret: bool = True, can_be_empty: bool = False) -> bool:
    """Checks if a single environment variable is set."""
    var_value = os.environ.get(var_name)
    if var_value is None:
        logging.error(f"🚨 Environment variable '{var_name}' is NOT SET.")
        return False
    if not can_be_empty and (is_secret or var_value) and not var_value.strip(): # Check if empty only if it should not be
        logging.error(f"🚨 Environment variable '{var_name}' is SET but EMPTY.")
        return False
    
    display_value = f"'{var_value[:2]}...{var_value[-2:]}' (length: {len(var_value)})" if is_secret and var_value else f"'{var_value}'"
    if not var_value.strip() and not can_be_empty: # Redundant check, but for clarity
        logging.info(f"✅ Environment variable '{var_name}' is SET but effectively empty (and should not be).")
    elif var_value.strip() or can_be_empty:
         logging.info(f"✅ Environment variable '{var_name}' is SET. Value: {display_value if var_value else '(empty but allowed)'}")
    return True

def validate_openai_keys_structure(env_var_name: str = "OPENAI_API_KEYS_BASE64") -> bool:
    """Validates the structure of OPENAI_API_KEYS_BASE64."""
    encoded_keys = os.environ.get(env_var_name, "").strip()
    if not encoded_keys:
        logging.error(f"🚨 {env_var_name} is not set or empty. Cannot validate structure.")
        return False

    logging.info(f"🔬 Validating structure of {env_var_name}...")
    try:
        decoded_bytes = base64.b64decode(encoded_keys, validate=True)
        decoded_str = decoded_bytes.decode('utf-8')
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

    for i, key_data in enumerate(parsed_keys):
        if not isinstance(key_data, str) or not key_data.startswith("sk-"):
            logging.error(f"🚨 Key at index {i} in {env_var_name} is not a string starting with 'sk-'.")
            return False
        if len(key_data) < 20: # Basic sanity check
            logging.warning(f"⚠️ Key at index {i} in {env_var_name} seems unusually short.")


    logging.info(f"✅ Structure of {env_var_name} (found {len(parsed_keys)} keys) appears valid.")
    return True


def main():
    logging.info("🚀 Starting environment variable validation...")
    required_vars = [
        ("OPENAI_API_KEYS_BASE64", True, False),
        ("GOOGLE_CLIENT_ID", False, False), # Client IDs are not typically super secret
        ("GOOGLE_CLIENT_SECRET", True, False),
        ("GOOGLE_REFRESH_TOKEN", True, False),
    ]
    
    optional_vars = [ # These might be used by the notifier or other optional features
        ("SLACK_API_TOKEN", True, True), # Can be empty if Slack not used
        ("SLACK_CHANNEL", False, True),   # Can be empty if Slack not used
    ]

    all_valid = True

    logging.info("--- Checking Required Variables ---")
    for var_name, is_secret, can_be_empty in required_vars:
        if not check_env_var(var_name, is_secret, can_be_empty):
            all_valid = False
    
    if os.environ.get("OPENAI_API_KEYS_BASE64"): # Only validate structure if the var is set
        if not validate_openai_keys_structure():
            all_valid = False

    logging.info("--- Checking Optional Variables ---")
    for var_name, is_secret, can_be_empty in optional_vars:
        check_env_var(var_name, is_secret, can_be_empty) # Don't fail validation for optional vars

    if all_valid:
        logging.info("✅✅✅ All critical environment variables seem correctly set and structured!")
        sys.exit(0)
    else:
        logging.error("❌❌❌ One or more critical environment variable checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
