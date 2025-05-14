import os
import base64
import json
import subprocess

def validate_environment():
    print("🔍 시스템 환경 검증 시작")
    
    # FFmpeg 버전 검사
    try:
        ffmpeg_version = subprocess.check_output(
            "ffmpeg -version | grep 'ffmpeg version'", 
            shell=True, 
            text=True
        )
        print(f"✅ FFmpeg 버전:\n{ffmpeg_version.strip()}")
        if "4.3" not in ffmpeg_version:
            print("⚠️ 경고: FFmpeg 4.3+ 권장")
    except Exception as e:
        print(f"❌ FFmpeg 검증 실패: {str(e)}")

    # OpenAI 키 검증
    try:
        encoded = os.getenv("OPENAI_API_KEYS_BASE64", "")
        if not encoded:
            raise ValueError("환경변수 미설정")
            
        decoded = base64.b64decode(encoded).decode()
        keys = json.loads(decoded)
        print(f"✅ OpenAI 키 {len(keys)}개 검증 완료")
        
    except Exception as e:
        print(f"❌ OPENAI_API_KEYS_BASE64 오류: {str(e)}")
        print(f"디버깅 정보: {encoded[:50]}...")

if __name__ == "__main__":
    validate_environment()
