import os
import json
from youtube_uploader import generate_and_upload_video
from notifier import send_error_notification

def check_secrets():
    try:
        # 1. OPENAI 키 확인
        openai_keys = json.loads(os.environ.get("OPENAI_API_KEYS", "[]"))
        if not openai_keys or not all(k.startswith("sk-") for k in openai_keys):
            raise ValueError("❌ OPENAI_API_KEYS 값이 비어있거나 형식이 잘못됨")
        print("✅ OPENAI_API_KEYS 로딩 성공")

        # 2. ELEVENLABS 키 확인
        elevenlabs_keys = json.loads(os.environ.get("ELEVENLABS_KEYS", "[]"))
        if not elevenlabs_keys or not all(k for k in elevenlabs_keys):
            raise ValueError("❌ ELEVENLABS_KEYS 값이 비어있음")
        print("✅ ELEVENLABS_KEYS 로딩 성공")

        # 3. Google Refresh Token 확인
        google_refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
        if not google_refresh_token or len(google_refresh_token) < 30:
            raise ValueError("❌ GOOGLE_REFRESH_TOKEN 값이 비정상적입니다")
        print("✅ GOOGLE_REFRESH_TOKEN 로딩 성공")

        # 4. Google Client Secret JSON 확인
        google_client_secret = json.loads(os.environ.get("GOOGLE_CLIENT_SECRET_JSON", "{}"))
        if not google_client_secret.get("installed"):
            raise ValueError("❌ GOOGLE_CLIENT_SECRET_JSON 내용이 비정상적입니다")
        print("✅ GOOGLE_CLIENT_SECRET_JSON 로딩 성공")

        print("\n🎉 모든 GitHub Secrets가 정상적으로 로딩되었습니다.\n")
        
        # 전체 자동화 실행
        generate_and_upload_video()

    except Exception as e:
        print(f"🚨 환경 변수 오류: {e}")
        send_error_notification(str(e))
        raise

if __name__ == "__main__":
    check_secrets()
