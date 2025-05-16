import os
import json
import base64

def save_gcp_credentials_from_env():
    encoded_json = os.getenv("GCP_SERVICE_ACCOUNT_BASE64")
    if not encoded_json:
        raise EnvironmentError("환경변수 GCP_SERVICE_ACCOUNT_BASE64가 설정되지 않았습니다.")
    
    decoded_json = base64.b64decode(encoded_json).decode("utf-8")
    credential_path = "/tmp/gcp_service_account.json"
    
    with open(credential_path, "w") as f:
        f.write(decoded_json)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
