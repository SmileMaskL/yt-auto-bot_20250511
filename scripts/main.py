# 전체 자동화 파이썬 코드
import os
# import openai # openai 모듈 직접 임포트 대신 OpenAI 클래스 임포트
from openai import OpenAI # 수정된 부분
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
from scripts.notifier import send_notification # notifier 스크립트가 있다고 가정
import random
import base64

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

def load_openai_keys():
    try:
        encoded = os.environ.get("OPENAI_API_KEYS_BASE64", "")
        if not encoded:
            # 환경 변수에서 직접 OPENAI_API_KEYS 를 읽어오는 fallback 로직 (이전 방식 호환용)
            raw_keys_direct = os.environ.get("OPENAI_API_KEYS", "")
            if not raw_keys_direct:
                raise ValueError("❌ OPENAI_API_KEYS_BASE64 또는 OPENAI_API_KEYS 환경변수가 설정되지 않았습니다.")
            log("⚠️ OPENAI_API_KEYS_BASE64가 없어 OPENAI_API_KEYS를 직접 사용합니다.")
            keys_json_string = raw_keys_direct
        else:
            # Base64 디코딩
            decoded = base64.b64decode(encoded).decode("utf-8")
            keys_json_string = decoded

        # JSON 파싱
        keys = json.loads(keys_json_string)
        if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
            raise ValueError("❌ OPENAI_API_KEYS는 문자열 배열(JSON 리스트)이어야 합니다.")

        logging.info("✅ OPENAI_API_KEYS 로딩 성공")
        return keys

    except json.JSONDecodeError as e:
        log(f"❌ OPENAI_API_KEYS JSON 파싱 실패: {e}")
        log(f"❌ 오류 발생 당시 RAW 데이터: {encoded if 'encoded' in locals() else os.environ.get('OPENAI_API_KEYS', '')}")
        raise RuntimeError("❌ 치명적 오류: OPENAI_API_KEYS 환경변수가 잘못된 형식입니다.")
    except Exception as e:
        log(f"❌ OPENAI_API_KEYS 로딩 중 오류 발생: {str(e)}")
        raise RuntimeError("❌ 치명적 오류: OPENAI_API_KEYS 환경변수 처리 중 문제 발생.")


def get_valid_openai_response(prompt):
    try:
        api_keys = load_openai_keys()
        if not api_keys:
            # 이 경우는 load_openai_keys 내부에서 이미 예외 처리가 되어 호출되지 않을 수 있음
            raise ValueError("OPENAI_API_KEYS 환경변수가 비어있습니다.")

        chosen_key = random.choice(api_keys).strip()
        log(f"🔑 OpenAI 키 시도: {chosen_key[:6]}...")

        try:
            # OpenAI 클라이언트 초기화 (수정된 부분)
            client = OpenAI(api_key=chosen_key)
            response = client.chat.completions.create( # 수정된 부분
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                timeout=20 # timeout 파라미터는 create 메서드에 직접 적용
            )
            return response.choices[0].message.content # 수정된 부분
        except Exception as e:
            log(f"❌ OpenAI 요청 실패 (키: {chosen_key[:6]}...): {str(e)}")
            raise
    except Exception as e:
        # load_openai_keys에서 발생한 예외도 여기서 잡힐 수 있음
        log(f"❌ get_valid_openai_response 함수 내 오류 발생: {str(e)}")
        raise


def generate_voice(text, output_path):
    elevenlabs_api_key = os.getenv("ELEVENLABS_KEY")
    elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not elevenlabs_api_key or not elevenlabs_voice_id:
        log("❌ ElevenLabs API 키 또는 Voice ID가 설정되지 않았습니다.")
        raise ValueError("ElevenLabs API 키 또는 Voice ID가 설정되지 않았습니다.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", # 필요시 모델 ID 변경
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60) # timeout 추가
        response.raise_for_status() # 오류 발생 시 예외 발생
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        log(f"✅ 음성 파일 저장 완료: {output_path}")
    except requests.exceptions.RequestException as e:
        log(f"❌ 음성 생성 실패: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            log(f"❌ 응답 내용: {e.response.text}")
        raise

def get_audio_duration(audio_path):
    try:
        with closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            if rate == 0: # rate가 0인 경우 예외 처리
                log("❌ 오디오 파일의 프레임 속도가 0입니다.")
                raise ValueError("오디오 파일의 프레임 속도가 유효하지 않습니다.")
            return frames / float(rate)
    except wave.Error as e: # wave 모듈 관련 특정 예외 처리
        log(f"❌ 오디오 파일 형식 오류 (wave.Error): {str(e)}. 파일 경로: {audio_path}")
        # ffmpeg를 사용하여 변환 시도 또는 다른 방법으로 길이 측정
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            duration = float(result.stdout)
            log(f"✅ (ffprobe) 오디오 길이 계산 성공: {duration:.2f}초")
            return duration
        except Exception as ffmpeg_e:
            log(f"❌ (ffprobe) 오디오 길이 계산 실패: {str(ffmpeg_e)}")
            raise ValueError(f"오디오 파일 ({audio_path})의 길이를 계산할 수 없습니다: {str(e)} / {str(ffmpeg_e)}")
    except Exception as e:
        log(f"❌ 오디오 길이 계산 실패: {str(e)}")
        raise

def generate_subtitles(text, output_path, total_duration):
    lines = [line.strip() for line in text.split('.') if line.strip()] # 마침표 기준으로 분리
    if not lines:
        log("⚠️ 스크립트 내용이 없어 자막을 생성할 수 없습니다.")
        # 빈 SRT 파일 생성 또는 기본 자막 생성
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("1\n00:00:00,000 --> 00:00:01,000\n(내용 없음)\n\n")
        log("✅ 빈 자막 파일 생성 완료.")
        return

    num_segments = len(lines)
    segment_duration = total_duration / num_segments if num_segments > 0 else total_duration


    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for i, line in enumerate(lines):
                start_time = i * segment_duration
                end_time = (i + 1) * segment_duration
                # 마지막 세그먼트의 종료 시간을 전체 길이로 제한
                if i == num_segments -1:
                    end_time = total_duration

                # 시작 시간과 종료 시간이 같거나 종료 시간이 더 작은 경우 조정
                if end_time <= start_time:
                    end_time = start_time + 0.5 # 최소 0.5초 길이 확보

                start_h, rem = divmod(start_time, 3600)
                start_min, start_sec_float = divmod(rem, 60)
                start_sec = int(start_sec_float)
                start_ms = int((start_sec_float - start_sec) * 1000)

                end_h, rem_end = divmod(end_time, 3600)
                end_min, end_sec_float = divmod(rem_end, 60)
                end_sec = int(end_sec_float)
                end_ms = int((end_sec_float - end_sec) * 1000)

                f.write(
                    f"{i+1}\n"
                    f"{int(start_h):02d}:{int(start_min):02d}:{start_sec:02d},{start_ms:03d} --> "
                    f"{int(end_h):02d}:{int(end_min):02d}:{end_sec:02d},{end_ms:03d}\n"
                    f"{line}\n\n"
                )
        log(f"✅ 자막 생성 완료: {output_path}")
    except Exception as e:
        log(f"❌ 자막 생성 실패: {str(e)}")
        raise

def create_video(audio_path, subtitle_path, output_path, duration):
    # 기본 배경 이미지 경로 (스크립트와 동일한 디렉토리에 있다고 가정)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    background_image = os.path.join(script_dir, "..", "background.jpg") # yt-auto-bot_20250511/background.jpg
    font_path = os.path.join(script_dir, "..", "fonts", "NotoSansCJKkr-Regular.otf") # yt-auto-bot_20250511/fonts/NotoSansCJKkr-Regular.otf

    if not os.path.exists(background_image):
        log(f"⚠️ 배경 이미지 파일({background_image})을 찾을 수 없습니다. 기본 색상 배경을 생성합니다.")
        # FFmpeg를 사용하여 기본 파란색 배경 이미지 생성 (1280x720)
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            f"color=c=blue:s=1280x720:d=1", # 1초짜리 이미지 생성
            background_image # 임시로 이 이름으로 저장 (또는 다른 이름 사용)
        ], check=True)
        log(f"✅ 임시 배경 이미지 생성: {background_image}")

    if not os.path.exists(font_path):
        log(f"⚠️ 폰트 파일({font_path})을 찾을 수 없습니다. 시스템 기본 폰트가 사용될 수 있습니다.")
        # subtitles 필터에서 FontName을 지정하지 않거나, 시스템에 설치된 폰트 이름을 사용해야 함
        # 여기서는 force_style에서 FontName을 제거하는 대신, 경로를 그대로 사용하고 ffmpeg이 처리하도록 둠
        # 또는 font_path = "Noto Sans CJK KR" 등 시스템 폰트 이름으로 변경 가능
        font_path_for_ffmpeg = "Arial" # 시스템 기본 폰트 예시 (Ubuntu에 없을 수 있음)
        log(f"폰트 경로를 {font_path_for_ffmpeg} (시스템 폰트 예시)로 대체 시도합니다.")
    else:
        # Windows와 Linux에서 ffmpeg 폰트 경로 처리 방식이 다를 수 있으므로 주의
        # Linux에서는 절대 경로 또는 fontconfig가 인식하는 폰트 이름 사용
        # subtitles 필터는 파일 경로를 직접 지원 (이스케이프 필요할 수 있음)
        # 예: 'force_style=\'FontFile=/path/to/font.ttf\',...'
        # 또는 fontconfig에 등록된 폰트 이름 사용: 'FontName=Noto Sans CJK KR'
        # 여기서는 NotoSansCJKkr-Regular.otf가 fontconfig에 등록되었다고 가정하거나,
        # ffmpeg이 경로를 직접 해석할 수 있도록 합니다.
        # subtitles 필터에서 파일 경로를 사용하려면 이스케이프 처리가 중요합니다.
        # Windows: 'FontFile=C\\:/path/to/font.otf'
        # Linux: 'FontFile=/path/to/font.otf'
        # force_style='FontName=Noto Sans CJK KR,...'는 fontconfig 설정에 의존.
        # 가장 안전한 방법은 폰트 파일을 작업 디렉토리에 복사하고 상대경로 사용 또는 절대경로 명시.
        # 여기서는 제공된 경로를 그대로 사용.
        font_path_for_ffmpeg = font_path


    # 자막 스타일링 (폰트 경로 문제 해결을 위해 수정)
    # 주의: subtitle 파일 내의 스타일 태그는 ffmpeg의 subtitles 필터 옵션에 의해 덮어쓰여질 수 있음.
    # force_style의 경로 구분자는 OS에 따라 다를 수 있음. ':' 또는 '\:'
    # Linux에서 직접 경로 사용 시: force_style='FontFile=\'{font_path_for_ffmpeg}\',FontSize=24'
    # Windows에서 직접 경로 사용 시: force_style='FontFile=C\\:/Path/To/Font.otf,FontSize=24' (경로 이스케이프 주의)
    # 여기서는 폰트 이름을 사용 (시스템에 설치 및 fontconfig에 의해 인식 가능해야 함)
    subtitle_vf = f"subtitles={subtitle_path}:force_style='FontName=Noto Sans CJK KR,FontSize=24,PrimaryColour=&HFFFFFF&,BorderStyle=1,Outline=1,Shadow=0'"
    # 만약 폰트 이름 인식이 안되면, 폰트 파일 직접 지정 시도 (경로 이스케이프에 매우 주의)
    # 예: subtitle_vf = f"subtitles={subtitle_path}:force_style='FontFile={font_path_for_ffmpeg.replace(':', '\\\\:')}',FontSize=24" # Linux 경로 이스케이프

    try:
        subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1", "-i", background_image,       # 배경 이미지 반복
            "-i", audio_path,                           # 오디오 파일
            "-vf", subtitle_vf,                         # 자막 필터 (위에서 정의)
            "-c:v", "libx264", "-preset", "medium", "-crf", "23", # 비디오 코덱 및 품질 설정
            "-c:a", "aac", "-b:a", "128k",              # 오디오 코덱 및 품질 설정
            "-t", str(duration),                        # 총 영상 길이
            "-pix_fmt", "yuv420p",                      # 픽셀 포맷 (호환성)
            output_path
        ], check=True, timeout=300) # timeout 추가 (5분)
        log(f"✅ 영상 생성 완료: {output_path}")
    except subprocess.CalledProcessError as e:
        log(f"❌ 영상 생성 실패 (CalledProcessError): {str(e)}")
        if e.stderr:
            log(f"❌ FFmpeg STDERR:\n{e.stderr.decode('utf-8', errors='ignore')}")
        raise
    except subprocess.TimeoutExpired as e:
        log(f"❌ 영상 생성 시간 초과 (TimeoutExpired): {str(e)}")
        if e.stderr:
            log(f"❌ FFmpeg STDERR (Timeout):\n{e.stderr.decode('utf-8', errors='ignore')}")
        raise
    except Exception as e:
        log(f"❌ 영상 생성 중 알 수 없는 오류: {str(e)}")
        raise


def upload_to_youtube(video_path, title, description):
    google_refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not all([google_refresh_token, google_client_id, google_client_secret]):
        log("❌ Google API 인증 정보가 충분하지 않습니다.")
        raise ValueError("Google API 인증 정보가 설정되지 않았습니다.")

    try:
        creds = Credentials(
            None,
            refresh_token=google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=google_client_id,
            client_secret=google_client_secret
        )
        # 토큰이 만료되었을 수 있으므로 리프레시 시도
        if creds.expired and creds.refresh_token:
             from google.auth.transport.requests import Request as GoogleAuthRequest
             creds.refresh(GoogleAuthRequest())
             log("ℹ️ Google API 토큰 리프레시됨.")


        youtube = build("youtube", "v3", credentials=creds, static_discovery=False) # static_discovery=False 추가

        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["AI", "Automation", "YouTube", "Python"], # 태그 추가
                "categoryId": "28" # 과학 및 기술 카테고리 (또는 적절한 ID로 변경)
            },
            "status": {"privacyStatus": "private"} # 기본 비공개로 업로드 (테스트 후 public으로 변경 가능)
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        log(f"⏳ YouTube 업로드 시작: {video_path}")
        response = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        ).execute()

        video_id = response.get("id")
        if not video_id:
            log(f"❌ YouTube 업로드 응답에서 video ID를 찾을 수 없습니다. 응답: {response}")
            raise ValueError("YouTube 업로드 후 video ID를 받지 못했습니다.")

        video_url = f"https://www.youtube.com/watch?v={video_id}" # 표준 YouTube URL로 변경
        log(f"✅ YouTube 업로드 완료: {video_url}")
        return video_url
    except Exception as e:
        log(f"❌ YouTube 업로드 실패: {str(e)}")
        # 응답 내용이 있다면 함께 로깅
        if hasattr(e, 'content'):
            try:
                error_details = json.loads(e.content.decode())
                log(f"❌ 오류 상세: {error_details}")
            except:
                log(f"❌ 오류 내용 (raw): {e.content}")
        raise

def main():
    log("🚀 자동화 시작")
    try:
        prompt = "오늘 대한민국의 주요 뉴스 트렌드 3가지를 요약하고, 각 트렌드에 대한 간단한 설명을 포함한 유튜브 쇼츠 대본을 작성해줘. 각 트렌드당 2-3문장으로 구성해줘."
        script_text = get_valid_openai_response(prompt)
        log(f"📜 생성된 스크립트:\n{script_text}")

        audio_file = "output.mp3"
        generate_voice(script_text, audio_file)

        duration = get_audio_duration(audio_file)
        log(f"⏱ 음성 길이: {duration:.2f}초")

        subtitle_file = "subtitles.srt"
        generate_subtitles(script_text, subtitle_file, duration)

        video_file = "final_video.mp4"
        create_video(audio_file, subtitle_file, video_file, duration)

        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        video_title = f"AI 생성 자동화 영상: {current_date} 주요 트렌드"
        video_description = (
            f"{current_date}, AI가 생성한 대한민국 주요 트렌드 요약 영상입니다.\n\n"
            f"스크립트 내용:\n{script_text}\n\n"
            "이 영상은 Python과 다양한 AI API를 사용하여 자동으로 생성 및 업로드되었습니다.\n"
            "#AIVideo #Automation #Python #Tech"
        )

        video_url = upload_to_youtube(video_file, video_title, video_description)
        send_notification(f"✅ 영상 업로드 완료!\n제목: {video_title}\n링크: {video_url}")

    except Exception as e:
        log(f"❌ 치명적 오류 발생: {str(e)}")
        send_notification(f"🚨 자동화 프로세스 실패!\n오류: {str(e)}")
    finally:
        log("🏁 자동화 종료")

if __name__ == "__main__":
    main()
