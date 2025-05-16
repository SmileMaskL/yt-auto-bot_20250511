import os
import random
import base64

def get_api_keys():
    encoded_keys = os.getenv("OPENAI_API_KEYS_BASE64")
    if not encoded_keys:
        raise ValueError("OPENAI_API_KEYS_BASE64 환경 변수가 설정되지 않았습니다.")
    decoded = base64.b64decode(encoded_keys).decode("utf-8")
    return decoded.strip().split(",")

def rotate_openai_key():
    keys = get_api_keys()
    new_key = random.choice(keys)
    os.environ["OPENAI_API_KEY"] = new_key
