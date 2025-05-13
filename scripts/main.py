# 전체 자동화 파이썬 코드
import os
import openai
import json
import requests
import subprocess
import wave
import logging
from datetime import datetime
from contextlib import closing
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from scripts.notifier import send_notification
import random

# 로깅 설정
LOG_FILE = "automation.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log(msg):
    logging.info(msg)

def get_valid_openai_response(prompt):
    try:
        # 환경변수에서 OPENAI_API_KEYS Secret 로드 (JSON 배열 형식)
        raw_keys = os.getenv("OPENAI_API_KEYS", "[]")
        try:
            api_keys = json.loads(raw_keys)  # JSON 파싱
        except json.JSONDecodeError:
            log("❌ OPENAI_API_KEYS JSON 파싱 실패")
            raise ValueError("❌ OPENAI_API_KEYS 환경변수가 잘못된 형식입니다.")
        
        if not api_keys:
            raise ValueError("OPENAI_API_KEYS 환경변수가 비어있습니다.")
        
        # 무작위로 OpenAI API 키를 선택
        openai.api_key = random.choice(api_keys).strip()
        log(f"🔑 OpenAI 키 시도: {openai.api_key[:6]}...")

        try:
            # OpenAI 클라이언트 초기화
            client = openai.ChatCompletion
            response = client.create(
                model="gpt-3.5-turbo",  # 무료 모델로 변경
                messages=[{"role": "user", "content": prompt}],
                timeout=20
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            log(f"❌ OpenAI 요청 실패: {str(e)}")
            raise
    except Exception as e:
        log(f"❌ 오류 발생: {str(e)}")
        raise

def generate_voice(text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv('ELEVENLABS_VOICE_ID')}"
    headers = {
        "xi-api-key": os.getenv("ELEVENLABS_KEY"),
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        log(f"✅ 음성 파일 저장 완료: {output_path}")
    except requests.exceptions.RequestException as e:
        log(f"❌ 음성 생성 실패: {str(e)}")
        raise

def get_audio_duration(audio_path):
    try:
        with closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)
    except Exception as e:
        log(f"❌ 오디오 길이 계산 실패: {str(e)}")
        raise

def generate_subtitles(text, output_path, total_duration):
    lines = [line.strip() for line in text.split('. ') if line.strip()]
    num_segments = len(lines)
    segment_duration = total_duration / num_segments

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for i, line in enumerate(lines):
                start_time = i * segment_duration
                end_time = (i + 1) * segment_duration
                start_min, start_sec = divmod(int(start_time), 60)
                end_min, end_sec = divmod(int(end_time), 60)

                f.write(
                    f"{i+1}\n"
                    f"00:{start_min:02d}:{start_sec:02d},000 --> "
                    f"00:{end_min:02d}:{end_sec:02d},000\n"
                    f"{line}\n\n"
                )
        log(f"✅ 자막 생성 완료: {output_path}")
    except Exception as e:
        log(f"❌ 자막 생성 실패: {str(e)}")
        raise

def create_video(audio_path, subtitle_path, output_path, duration):
    background_image = "background.jpg"
    if not os.path.exists(background_image):
        subprocess.run([ 
            "ffmpeg", "-f", "lavfi", "-i", 
            f"color=c=blue:s=1280x720:d={duration}", 
            background_image
        ], check=True)

    try:
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", background_image, "-i", audio_path,
            "-vf", f"subtitles={subtitle_path}:force_style='FontName=Noto Sans CJK KR,FontSize=24'",
            "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p", output_path
        ], check=True)
        log(f"✅ 영상 생성 완료: {output_path}")
    except subprocess.CalledProcessError as e:
        log(f"❌ 영상 생성 실패: {str(e)}")
        raise

def upload_to_youtube(video_path, title, description):
    creds = Credentials(
        None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
    )
    youtube = build("youtube", "v3", credentials=creds)
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["AI", "Automation", "YouTube"],
            "categoryId": "22"
        },
        "status": {"privacyStatus": "public"}
    }
    media = MediaFileUpload(video_path, resumable=True)
    try:
        response = youtube.videos().insert(
            part="snippet,status", body=request_body, media_body=media
        ).execute()

        video_url = f"https://youtu.be/{response['id']}"
        log(f"✅ YouTube 업로드 완료: {video_url}")
        return video_url
    except Exception as e:
        log(f"❌ YouTube 업로드 실패: {str(e)}")
        raise

def main():
    log("🚀 자동화 시작")
    try:
        prompt = "오늘의 대한민국 트렌드를 5가지 요약해줘."
        script = get_valid_openai_response(prompt)
        log(f"📜 생성된 스크립트:\n{script}")

        audio_file = "output.mp3"
        generate_voice(script, audio_file)

        duration = get_audio_duration(audio_file)
        log(f"⏱ 음성 길이: {duration:.2f}초")

        subtitle_file = "subtitles.srt"
        generate_subtitles(script, subtitle_file, duration)

        video_file = "final_video.mp4"
        create_video(audio_file, subtitle_file, video_file, duration)

        video_url = upload_to_youtube(
            video_file,
            "AI 자동 생성 영상",
            "이 영상은 AI를 통해 자동으로 생성되었습니다."
        )
        send_notification(f"✅ 영상 업로드 완료: {video_url}")
    except Exception as e:
        log(f"❌ 치명적 오류: {str(e)}")
        send_notification(f"🚨 자동화 실패: {str(e)}")
    finally:
        log("🏁 자동화 종료")

if __name__ == "__main__":
    main()
