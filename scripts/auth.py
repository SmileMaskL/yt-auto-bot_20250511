# scripts/auth.py
import os
import base64
import json

GCP_CREDENTIAL_PATH = "gcp_credentials.json"

def save_gcp_credentials_from_env():
    encoded = os.environ.get("GCP_SERVICE_ACCOUNT_BASE64")
    if not encoded:
        raise ValueError("GCP_SERVICE_ACCOUNT_BASE64 환경변수가 설정되지 않았습니다.")

    decoded = base64.b64decode(encoded).decode("utf-8")
    creds = json.loads(decoded)

    if creds.get("type") != "service_account":
        raise ValueError("GCP 서비스 계정 키 파일의 유형이 'service_account'가 아닙니다.")

    with open(GCP_CREDENTIAL_PATH, "w") as f:
        f.write(decoded)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_CREDENTIAL_PATH
