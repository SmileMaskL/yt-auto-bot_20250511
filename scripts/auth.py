import os
import json
import base64

def save_gcp_credentials_from_env():
    """
    환경 변수로부터 GCP 서비스 계정 인증 정보를 파일로 저장합니다.
    """
    gcp_credentials_base64 = os.environ.get("GOOGLE_TOKEN_JSON")
    if not gcp_credentials_base64:
        raise ValueError("GOOGLE_TOKEN_JSON 환경변수가 설정되지 않았습니다.")

    credentials_path = "gcp_credentials.json"
    with open(credentials_path, "w") as f:
        f.write(gcp_credentials_base64)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
