# scripts/test_api.py
import os
import sys
import json
import base64
import logging
from openai import OpenAI, OpenAIError

# Basic logging for this test script
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [test_api] %(message)s")

def test_openai_keys():
    """Tests OpenAI API keys loaded from OPENAI_API_KEYS_BASE64 environment variable."""
    logging.info("🧪 Starting OpenAI API key test...")
    
    encoded_keys_env_var = "OPENAI_API_KEYS_BASE64"
    encoded_keys_val = os.environ.get(encoded_keys_env_var)

    if not encoded_keys_val:
        logging.error(f"🚨 Environment variable '{encoded_keys_env_var}' is not set. Cannot test API keys.")
        return

    try:
        decoded_bytes = base64.b64decode(encoded_keys_val, validate=True)
        decoded_str = decoded_bytes.decode('utf-8')
        api_keys_list = json.loads(decoded_str)
    except Exception as e:
        logging.error(f"🚨 Failed to decode or parse API keys from '{encoded_keys_env_var}': {e}")
        return

    if not isinstance(api_keys_list, list) or not api_keys_list:
        logging.error(f"🚨 Decoded API keys are not a non-empty list. Content: {api_keys_list}")
        return

    logging.info(f"Found {len(api_keys_list)} API key(s) to test.")
    valid_key_found = False

    for idx, api_key in enumerate(api_keys_list):
        if not isinstance(api_key, str) or not api_key.startswith("sk-"):
            logging.warning(f"⚠️ Key at index {idx} has an invalid format. Skipping.")
            continue

        logging.info(f"🔄 Testing Key #{idx + 1} (starts with: {api_key[:8]}...)")
        try:
            client = OpenAI(api_key=api_key, timeout=10.0)
            # Perform a simple, low-cost API call, e.g., list models or a very short completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # A common, cheaper model for testing
                messages=[{"role": "user", "content": "This is a connection test."}],
                max_tokens=5
            )
            if response.choices and response.choices[0].message.content:
                logging.info(f"✅ Key #{idx + 1} is VALID and working!")
                valid_key_found = True
                # break # Uncomment to stop after the first valid key
            else:
                logging.error(f"❌ Key #{idx + 1} returned a response but content was empty.")
        except OpenAIError as e:
            logging.error(f"❌ Key #{idx + 1} FAILED with OpenAI API error: {e}")
        except Exception as e:
            logging.error(f"❌ Key #{idx + 1} FAILED with an unexpected error: {e}")
            
    if valid_key_found:
        logging.info("🎉 At least one OpenAI API key is valid and working.")
    else:
        logging.error("🚫 No valid OpenAI API keys found after testing all provided keys.")

if __name__ == "__main__":
    test_openai_keys()
