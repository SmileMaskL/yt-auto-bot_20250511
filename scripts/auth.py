# auth.py 수정 (GCP 인증 강화)
from google.oauth2 import service_account
import base64, os

def gcp_authenticate():
    # GitHub Secrets에서 인증정보 로드
    creds_json = base64.b64decode(os.environ['GCP_SERVICE_ACCOUNT_BASE64']).decode()
    credentials = service_account.Credentials.from_service_account_info(
        eval(creds_json),
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )
    return credentials
