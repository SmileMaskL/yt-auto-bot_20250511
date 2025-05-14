# 콘텐츠 생성 관련 기능
import os
import json
import requests
import subprocess
import wave
import logging
import base64
import random
from datetime import datetime
from contextlib import closing
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from openai import OpenAI

# 로깅 설정
LOG_FILE = "automation.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

try:
    from scripts.notifier import send_notification
except ImportError as e:
    send_notification = None
    logging.info(f"⚠️ 알림 모듈 로드 실패: {str(e)}")

def log(msg):
    logging.info(msg)

def load_openai_keys():
    try:
        encoded = os.environ.get("OPENAI_API_KEYS_BASE64", "")
        if not encoded:
            raise ValueError("❌ OPENAI_API_KEYS_BASE64 환경변수 미설정")

        decoded = base64.b64decode(encoded).decode("utf-8")
        keys = json.loads(decoded)

        if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
            raise ValueError("❌ API 키 형식 오류")

        log(f"✅ OpenAI 키 {len(keys)}개 로드 완료")
        return keys

    except Exception as e:
        log(f"❌ 키 로딩 실패: {str(e)}")
        raise

def get_valid_openai_response(prompt):
    try:
        api_keys = load_openai_keys()
        chosen_key = random.choice(api_keys).strip()
        log(f"🔑 OpenAI 키 시도: {chosen_key[:6]}...")

        client = OpenAI(api_key=chosen_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )
        return response.choices[0].message.content

    except Exception as e:
        log(f"❌ OpenAI 요청 실패: {str(e)}")
        raise

def generate_voice(text, output_path):
    elevenlabs_key = os.getenv("ELEVENLABS_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not elevenlabs_key or not voice_id:
        raise ValueError("❌ ElevenLabs 설정 오류")

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_key
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
    }

    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        log(f"✅ 음성 파일 저장: {output_path}")

    except Exception as e:
        log(f"❌ 음성 생성 실패: {str(e)}")
        raise

def get_audio_duration(audio_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        log(f"❌ 오디오 길이 측정 실패: {str(e)}")
        raise

def generate_subtitles(text, output_path, total_duration):
    try:
        lines = [line.strip() for line in text.split('.') if line.strip()]
        num_segments = len(lines)
        segment_duration = total_duration / num_segments if num_segments > 0 else total_duration

        with open(output_path, "w", encoding="utf-8") as f:
            for i, line in enumerate(lines):
                start_time = i * segment_duration
                end_time = (i + 1) * segment_duration
                if end_time > total_duration:
                    end_time = total_duration

                f.write(
                    f"{i+1}\n"
                    f"{datetime.utcfromtimestamp(start_time).strftime('%H:%M:%S,000')} --> "
                    f"{datetime.utcfromtimestamp(end_time).strftime('%H:%M:%S,000')}\n"
                    f"{line}\n\n"
                )
        log(f"✅ 자막 생성: {output_path}")

    except Exception as e:
        log(f"❌ 자막 생성 오류: {str(e)}")
        raise

def create_video(audio_path, subtitle_path, output_path, duration):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.normpath(os.path.join(script_dir, "../fonts/NotoSansCJKkr-Regular.otf"))
    background_image = os.path.join(script_dir, "../background.jpg")

    # ▼▼▼ 폰트 검증 추가 ▼▼▼
    if not os.path.exists(font_path):
        log(f"❌ 폰트 파일 누락: {font_path}")
        raise FileNotFoundError(f"Font file not found: {font_path}")

    if not os.path.exists(background_image):
        log(f"⚠️ 배경 이미지 없음: {background_image}")
        background_image = os.path.join(script_dir, "temp_background.png")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", 
            "color=c=blue:s=1280x720:d=1", 
            background_image
        ], check=True)

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", background_image,
        "-i", audio_path,
        "-vf", f"subtitles='{subtitle_path}':force_style='FontName=Noto Sans CJK KR,FontSize=24'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        output_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        log(f"✅ 영상 생성: {output_path}")
    except subprocess.CalledProcessError as e:
        log(f"❌ FFmpeg 오류: {str(e)}")
        raise

def upload_to_youtube(video_path, title, description):
    creds = Credentials(
        None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )

    if creds.expired:
        creds.refresh(requests.Request())

    youtube = build("youtube", "v3", credentials=creds)
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    video_body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "28",
            "tags": ["AI", "자동화", "유튜브"]
        },
        "status": {"privacyStatus": "public"}
    }

    try:
        response = youtube.videos().insert(
            part="snippet,status",
            body=video_body,
            media_body=media
        ).execute()
        return f"https://youtu.be/{response['id']}"
    except Exception as e:
        log(f"❌ 업로드 실패: {str(e)}")
        raise

def main():
    log("🚀 자동화 시작")
    try:
        # 콘텐츠 생성 파이프라인
        script = get_valid_openai_response("오늘 대한민국 주요 뉴스 3개를 요약한 쇼츠 대본 생성")
        generate_voice(script, "output.mp3")
        duration = get_audio_duration("output.mp3")
        generate_subtitles(script, "subtitles.srt", duration)
        create_video("output.mp3", "subtitles.srt", "final.mp4", duration)
        
        # YouTube 업로드
        video_url = upload_to_youtube(
            "final.mp4",
            f"AI 생성 뉴스 요약 {datetime.now().strftime('%Y-%m-%d')}",
            "AI가 자동으로 생성한 뉴스 요약 영상입니다"
        )

        if send_notification:
            send_notification(f"✅ 업로드 완료!\n{video_url}")
        else:
            log("ℹ️ 알림 기능 사용 안함")

    except Exception as e:
        log(f"❌ 치명적 오류: {str(e)}")
        if send_notification:
            send_notification(f"🚨 실패: {str(e)}")
    finally:
        log("🏁 프로세스 종료")

if __name__ == "__main__":
    main()
