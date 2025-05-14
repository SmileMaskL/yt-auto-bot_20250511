# 전체 자동화 파이썬 코드
import os
import json
import requests
import subprocess
import wave
import logging
import base64
import random
import binascii
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
        encoded = os.environ.get("OPENAI_API_KEYS_BASE64", "").strip()
        
        if not encoded or encoded.isspace():
            raise ValueError("🚨 OPENAI_API_KEYS_BASE64 미설정 (환경변수 확인 필요)")
            
        if len(encoded) < 20:
            raise ValueError(f"🚨 유효하지 않은 Base64 길이 ({len(encoded)}/20 최소)")

        try:
            decoded_bytes = base64.b64decode(encoded, validate=True)
            decoded = decoded_bytes.decode('utf-8')
        except (binascii.Error, UnicodeDecodeError) as e:
            raise ValueError(f"🚨 Base64 디코딩 오류: {str(e)}")
        
        try:
            keys = json.loads(decoded)
        except json.JSONDecodeError as e:
            raise ValueError(f"🚨 JSON 파싱 오류: {str(e)} (디코딩된 값: {decoded[:50]}...)")

        if not isinstance(keys, list) or len(keys) == 0:
            raise TypeError("🚨 키 형식 오류: 비어있지 않은 리스트 필요")
            
        for i, key in enumerate(keys):
            if not isinstance(key, str) or not key.startswith("sk-"):
                raise ValueError(f"🚨 {i+1}번 키 형식 오류: 'sk-'로 시작해야 함")

        log(f"✅ OpenAI 키 {len(keys)}개 검증 완료")
        return keys

    except Exception as e:
        log(f"""
        🔍 OPENAI_API_KEYS_BASE64 디버그 정보
        - 환경변수 길이: {len(encoded)}
        - Base64 헤더: {encoded[:20]}...
        - 디코딩 샘플: {decoded[:50] if 'decoded' in locals() else 'N/A'}
        """)
        raise

def get_valid_openai_response(prompt):
    keys = load_openai_keys()
    client = OpenAI(api_key=random.choice(keys))
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        content = response.choices[0].message.content
        if len(content) < 100:
            raise ValueError("⚠️ 생성된 콘텐츠가 너무 짧습니다")
        return content
    except Exception as e:
        log(f"❌ OpenAI API 오류: {str(e)}")
        raise

def generate_voice(text, output_path):
    keys = load_openai_keys()
    client = OpenAI(api_key=random.choice(keys))
    
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=text
        )
        response.stream_to_file(output_path)
        log(f"✅ 음성 파일 생성: {output_path}")
    except Exception as e:
        log(f"❌ 음성 생성 실패: {str(e)}")
        raise

def get_audio_duration(file_path):
    try:
        with closing(wave.open(file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            log(f"🎵 오디오 길이: {duration:.2f}초")
            return duration
    except Exception as e:
        log(f"❌ 오디오 길이 측정 실패: {str(e)}")
        raise

def generate_subtitles(text, output_path, duration):
    try:
        words_per_second = len(text.split()) / duration
        segment_length = int(duration / 10)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i in range(10):
                start = i * segment_length
                end = (i+1) * segment_length
                f.write(f"{i+1}\n")
                f.write(f"{datetime.utcfromtimestamp(start).strftime('%H:%M:%S,000')} --> ")
                f.write(f"{datetime.utcfromtimestamp(end).strftime('%H:%M:%S,000')}\n")
                f.write(f"{text[i*len(text)//10:(i+1)*len(text)//10]}\n\n")
        log(f"✅ 자막 파일 생성: {output_path}")
    except Exception as e:
        log(f"❌ 자막 생성 실패: {str(e)}")
        raise

def create_video(audio_path, subtitle_path, output_path, duration):
    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", audio_path,
            "-vf", f"subtitles={subtitle_path}:force_style='FontName=Noto Sans CJK KR,FontSize=24'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            output_path
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        log(f"🎥 비디오 생성 완료: {output_path}")
    except subprocess.CalledProcessError as e:
        log(f"❌ FFmpeg 오류: {str(e)}")
        raise

def upload_to_youtube(file_path, title, description):
    try:
        credentials = Credentials.from_authorized_user_file("token.json")
        youtube = build('youtube', 'v3', credentials=credentials)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "categoryId": "28"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=MediaFileUpload(file_path)
        )
        response = request.execute()
        video_id = response['id']
        url = f"https://youtu.be/{video_id}"
        log(f"📤 YouTube 업로드 완료: {url}")
        return url
    except Exception as e:
        log(f"❌ YouTube 업로드 실패: {str(e)}")
        raise

def main():
    log("🚀 자동화 시작")
    try:
        validation = subprocess.run(
            ["python", "scripts/validate_env.py"],
            capture_output=True,
            text=True
        )
        if validation.returncode != 0:
            log(f"🚨 환경 검증 실패:\n{validation.stderr}")
            raise RuntimeError("시스템 검증 실패")

        script = get_valid_openai_response(
            "2025년 5월 대한민국 주요 IT 뉴스 3개를 마크다운 형식으로 요약해주세요"
        )
        generate_voice(script, "output.mp3")
        duration = get_audio_duration("output.mp3")
        generate_subtitles(script, "subtitles.srt", duration)
        create_video("output.mp3", "subtitles.srt", "final.mp4", duration)
        
        video_url = upload_to_youtube(
            "final.mp4",
            f"AI 생성 뉴스 요약 {datetime.now().strftime('%Y-%m-%d')}",
            "AI가 자동으로 생성한 뉴스 요약 영상입니다"
        )

        if send_notification:
            send_notification(f"✅ 업로드 완료!\n{video_url}")

    except Exception as e:
        log(f"❌ 치명적 오류: {str(e)}")
        if send_notification:
            send_notification(f"🚨 실패: {str(e)}")
    finally:
        log("🏁 프로세스 종료")

if __name__ == "__main__":
    main()
