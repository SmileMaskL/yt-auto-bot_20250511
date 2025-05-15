import os
import base64

def save_gcp_credentials_from_env():
    creds_b64 = os.getenv("GCP_SERVICE_ACCOUNT_BASE64")
    if not creds_b64:
        raise ValueError("GCP_SERVICE_ACCOUNT_BASE64 환경변수가 설정되지 않았습니다.")

    decoded = base64.b64decode(creds_b64)
    creds_path = "/tmp/service_account.json"
    with open(creds_path, "wb") as f:
        f.write(decoded)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
