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

# 수정 및 통합된 load_openai_keys 함수
def load_openai_keys():
    try:
        encoded = os.environ.get("OPENAI_API_KEYS_BASE64", "")
        if not encoded:
            # 환경 변수에서 직접 OPENAI_API_KEYS 를 읽어오는 fallback 로직 (이전 방식 호환용)
            # 이 부분은 원래 코드에 있었으나, 새로운 요구사항에서는 OPENAI_API_KEYS_BASE64만 사용하도록 명시되었으므로,
            # 명확성을 위해 OPENAI_API_KEYS_BASE64가 없는 경우 바로 에러를 발생시키도록 유지합니다.
            # 만약 OPENAI_API_KEYS 환경변수를 fallback으로 계속 지원하고 싶다면, 이전 로직을 여기에 다시 포함할 수 있습니다.
            # 하지만 제공해주신 새 `load_openai_keys` 함수는 OPENAI_API_KEYS_BASE64가 없으면 바로 에러를 발생시킵니다.
            # 여기서는 제공된 새 함수 로직을 따릅니다.
            raise ValueError("❌ OPENAI_API_KEYS_BASE64 환경변수가 설정되지 않았습니다.")

        # Base64 디코딩
        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
        except Exception as decode_error:
            log(f"❌ Base64 디코딩 실패: {decode_error}")
            log(f"❌ 인코딩된 값의 시작 부분: {encoded[:20]}...") # 디버깅을 위해 값의 일부를 로깅
            raise ValueError("OPENAI_API_KEYS_BASE64의 Base64 디코딩에 실패했습니다.")

        # JSON 파싱
        try:
            keys = json.loads(decoded)
        except json.JSONDecodeError as json_error:
            log(f"❌ JSON 파싱 실패: {json_error}")
            log(f"❌ 디코딩된 값의 시작 부분: {decoded[:50]}...") # 디버깅을 위해 값의 일부를 로깅
            raise ValueError("디코딩된 값이 유효한 JSON 형식이 아닙니다.")

        if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
            raise ValueError("❌ OPENAI_API_KEYS는 문자열 배열(JSON 리스트)이어야 합니다.")

        log(f"✅ OPENAI_API_KEYS 로딩 성공: {len(keys)}개의 키를 로드했습니다.")
        return keys

    except Exception as e:
        # 여기서의 로깅은 이미 try-except 블록 내부에서 구체적으로 이루어졌으므로,
        # 추가적인 일반 로깅보다는 발생한 예외를 그대로 다시 발생시키는 것이 좋습니다.
        # log(f"❌ OPENAI_API_KEYS 로딩 중 오류 발생: {str(e)}") # 이 줄은 중복 로깅이 될 수 있음
        raise # 원본 예외를 그대로 전달하여 호출 스택에서 처리하도록 함


def get_valid_openai_response(prompt):
    try:
        api_keys = load_openai_keys()
        # load_openai_keys 함수 내부에서 빈 리스트 반환 경우가 없으므로, 아래 if not api_keys 검사는 사실상 불필요.
        # 하지만 방어적 프로그래밍 차원에서 유지할 수 있습니다.
        if not api_keys:
            raise ValueError("OPENAI API 키를 로드하지 못했습니다 (리스트가 비어있음).")


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
        log(f"⚠️ 오디오 파일 형식 오류 (wave.Error): {str(e)}. 파일 경로: {audio_path}. ffprobe로 재시도합니다.")
        # ffmpeg를 사용하여 변환 시도 또는 다른 방법으로 길이 측정
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True # 출력을 텍스트로 받기
            )
            duration = float(result.stdout.strip()) # 공백 제거 및 float 변환
            log(f"✅ (ffprobe) 오디오 길이 계산 성공: {duration:.2f}초")
            return duration
        except Exception as ffmpeg_e:
            log(f"❌ (ffprobe) 오디오 길이 계산 실패: {str(ffmpeg_e)}")
            raise ValueError(f"오디오 파일 ({audio_path})의 길이를 계산할 수 없습니다: wave 오류 - {str(e)} / ffprobe 오류 - {str(ffmpeg_e)}")
    except Exception as e:
        log(f"❌ 오디오 길이 계산 중 알 수 없는 오류: {str(e)}")
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
                
                # total_duration을 초과하지 않도록 보정
                if end_time > total_duration:
                    end_time = total_duration
                if start_time >= total_duration and num_segments > 1: # 마지막 이전 세그먼트가 이미 전체 길이를 넘으면 조정
                    start_time = total_duration - 0.5
                    if start_time < 0: start_time = 0 # 음수 시간 방지
                if start_time >= end_time: # 조정 후에도 문제가 있다면 마지막 세그먼트는 최소 길이만 확보
                    start_time = max(0, end_time - 0.5)


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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # background.jpg 파일 경로 수정: 스크립트 기준 상위 디렉토리
    background_image = os.path.join(script_dir, "..", "background.jpg")
    # 폰트 파일 경로 수정: 스크립트 기준 상위 디렉토리의 fonts 폴더
    font_path = os.path.join(script_dir, "..", "fonts", "NotoSansCJKkr-Regular.otf")

    if not os.path.exists(background_image):
        log(f"⚠️ 배경 이미지 파일({background_image})을 찾을 수 없습니다. 기본 색상 배경을 생성합니다.")
        temp_background_image_name = "temp_background_1280x720.png" # 임시 파일 이름
        background_image_to_use = os.path.join(script_dir, temp_background_image_name)

        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            f"color=c=blue:s=1280x720:d=1", # 1초짜리 이미지 생성
            background_image_to_use # 임시로 이 이름으로 저장
        ], check=True)
        log(f"✅ 임시 배경 이미지 생성: {background_image_to_use}")
    else:
        background_image_to_use = background_image


    # 자막 스타일링: 폰트 파일 직접 경로 사용 (OS에 따른 경로 구분자 및 이스케이프 주의)
    # FFmpeg에서 폰트 파일 경로를 사용할 때는 경로를 필터 문자열 내에서 적절히 이스케이프해야 합니다.
    # Windows: 'C\\:/path/to/font.otf' -> 'C\\:\\\\/path\\\\/to\\\\/font.otf' (예시, 실제론 더 복잡할 수 있음)
    # Linux/macOS: '/path/to/font.otf' -> '\\\\/path\\\\/to\\\\/font.otf'
    # 가장 간단한 방법은 fontconfig를 통해 시스템에 폰트를 설치하고 폰트 이름을 사용하는 것입니다.
    # NotoSansCJKkr-Regular.otf가 설치되어 있고 fontconfig가 "Noto Sans CJK KR Regular" 등으로 인식한다면 해당 이름을 사용합니다.
    # 여기서는 파일 경로를 직접 지정하는 것을 시도하되, OS 호환성을 위해 fontconfig 사용을 권장합니다.
    
    # font_path_for_ffmpeg를 시스템에 맞게 이스케이프 처리
    # (주의) 아래 이스케이프는 간단한 예시이며, 복잡한 경로에서는 추가 처리가 필요할 수 있습니다.
    # Windows의 경우 ':'를 이스케이프 하는 것이 특히 까다롭습니다.
    # Linux/macOS의 경우 경로에 특수문자가 없다면 직접 사용해도 되는 경우가 많습니다.
    escaped_font_path = font_path.replace('\\', '\\\\').replace(':', '\\:') if os.name == 'nt' else font_path

    font_style_option = f"FontName=Noto Sans CJK KR Regular" # 시스템에 설치된 폰트 이름 사용 시도
    if not os.path.exists(font_path):
        log(f"⚠️ 폰트 파일({font_path})을 찾을 수 없습니다. 시스템 기본 폰트(Arial) 또는 설치된 'Noto Sans CJK KR Regular'를 사용 시도합니다.")
        # font_path가 없을 경우, FontFile 대신 FontName으로 시도 (시스템에 설치 가정)
        # 또는 안전하게 알려진 기본 폰트 이름(예: Arial)을 사용할 수 있으나, 한글 지원 여부 확인 필요
        # font_style_option = "FontName=Arial" # 예시
    else:
        # 폰트 파일이 존재하면 FontFile을 사용. 경로 이스케이프 중요.
        # 아래는 font_path를 사용하는 예시. 복잡한 경로 이스케이프는 주의 필요.
        # 가장 확실한 방법은 fontconfig 설정 후 FontName 사용입니다.
        # 여기서는 FontName을 기본으로 하고, 경로 직접 지정은 주석 처리합니다.
        # font_style_option = f"FontFile='{escaped_font_path}'"
        log(f"ℹ️ 지정된 폰트 파일 사용 시도: {font_path}")


    subtitle_vf = f"subtitles='{subtitle_path.replace(':', '\\:')}':force_style='{font_style_option},FontSize=24,PrimaryColour=&HFFFFFF&,BorderStyle=1,Outline=1,OutlineColour=&H000000&,Shadow=0.5,MarginV=25'"
    # MarginV는 하단 여백, OutlineColour는 테두리 색상, Shadow는 그림자 강도 (0~1)
    log(f"ℹ️ FFmpeg 자막 필터 옵션: {subtitle_vf}")


    try:
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", background_image_to_use,    # 배경 이미지 반복
            "-i", audio_path,                               # 오디오 파일
            "-vf", subtitle_vf,                             # 자막 필터 (위에서 정의)
            "-c:v", "libx264", "-preset", "medium", "-crf", "23", # 비디오 코덱 및 품질 설정
            "-c:a", "aac", "-b:a", "128k",                  # 오디오 코덱 및 품질 설정
            "-t", str(duration),                            # 총 영상 길이
            "-pix_fmt", "yuv420p",                          # 픽셀 포맷 (호환성)
            output_path
        ]
        log(f"ℹ️ FFmpeg 명령어 실행: {' '.join(ffmpeg_cmd)}")
        process = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True, timeout=300) # timeout 추가 (5분)
        log(f"✅ 영상 생성 완료: {output_path}")
        if process.stdout: log(f"FFmpeg STDOUT:\n{process.stdout}")
        if process.stderr: log(f"FFmpeg STDERR:\n{process.stderr}") # stderr도 정보성 출력이 있을 수 있음

    except subprocess.CalledProcessError as e:
        log(f"❌ 영상 생성 실패 (CalledProcessError): {str(e)}")
        if e.stdout: log(f"❌ FFmpeg STDOUT:\n{e.stdout}")
        if e.stderr: log(f"❌ FFmpeg STDERR:\n{e.stderr}")
        raise
    except subprocess.TimeoutExpired as e:
        log(f"❌ 영상 생성 시간 초과 (TimeoutExpired): {str(e)}")
        if e.stdout: log(f"❌ FFmpeg STDOUT (Timeout):\n{e.stdout.decode('utf-8', errors='ignore') if isinstance(e.stdout, bytes) else e.stdout}")
        if e.stderr: log(f"❌ FFmpeg STDERR (Timeout):\n{e.stderr.decode('utf-8', errors='ignore') if isinstance(e.stderr, bytes) else e.stderr}")
        raise
    except Exception as e:
        log(f"❌ 영상 생성 중 알 수 없는 오류: {str(e)}")
        raise
    finally:
        if 'temp_background_image_name' in locals() and os.path.exists(background_image_to_use) and background_image_to_use.endswith(temp_background_image_name):
            try:
                os.remove(background_image_to_use)
                log(f"🗑️ 임시 배경 이미지 삭제: {background_image_to_use}")
            except Exception as e_remove:
                log(f"⚠️ 임시 배경 이미지 삭제 실패: {e_remove}")


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
                "tags": ["AI", "Automation", "YouTube", "Python", "뉴스", "트렌드"], # 태그 추가
                "categoryId": "25" # 뉴스/정치 카테고리 (또는 "28" 과학 및 기술)
            },
            "status": {"privacyStatus": "private"} # 기본 비공개로 업로드 (테스트 후 public으로 변경 가능)
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        log(f"⏳ YouTube 업로드 시작: {video_path}")
        response_upload = youtube.videos().insert( # 변수명 변경 response -> response_upload
            part="snippet,status",
            body=request_body,
            media_body=media
        ).execute()

        video_id = response_upload.get("id")
        if not video_id:
            log(f"❌ YouTube 업로드 응답에서 video ID를 찾을 수 없습니다. 응답: {response_upload}")
            raise ValueError("YouTube 업로드 후 video ID를 받지 못했습니다.")

        # video_url = f"https://www.youtube.com/watch?v={video_id}" # 이 URL은 실제 접속 가능한 URL이 아닐 수 있습니다.
        video_url = f"https://www.youtube.com/watch?v={video_id}" # 표준 YouTube URL로 변경
        log(f"✅ YouTube 업로드 완료: {video_url}")
        return video_url
    except Exception as e:
        log(f"❌ YouTube 업로드 실패: {str(e)}")
        # 응답 내용이 있다면 함께 로깅
        if hasattr(e, 'content'):
            try:
                # content가 bytes일 경우 decode 시도
                error_content = e.content.decode() if isinstance(e.content, bytes) else e.content
                error_details = json.loads(error_content)
                log(f"❌ 오류 상세: {error_details}")
            except:
                log(f"❌ 오류 내용 (raw): {e.content}")
        raise

def main():
    log("🚀 자동화 시작")
    try:
        prompt = "오늘 대한민국의 주요 뉴스 트렌드 3가지를 요약하고, 각 트렌드에 대한 간단한 설명을 포함한 유튜브 쇼츠 대본을 작성해줘. 각 트렌드당 2-3문장으로 구성해줘. 문장 끝은 항상 마침표로 끝나도록 해줘." # 마침표 강제 추가
        script_text = get_valid_openai_response(prompt)
        log(f"📜 생성된 스크립트:\n{script_text}")

        audio_file = "output.mp3"
        generate_voice(script_text, audio_file)

        duration = get_audio_duration(audio_file)
        log(f"⏱ 음성 길이: {duration:.2f}초")
        
        # 쇼츠는 보통 60초 미만, 여기서는 58초로 제한 (필요시 조정)
        max_shorts_duration = 58.0
        if duration > max_shorts_duration:
            log(f"⚠️ 생성된 음성 길이({duration:.2f}초)가 쇼츠 권장 길이({max_shorts_duration}초)를 초과합니다. 영상이 길어질 수 있습니다.")
            # 필요하다면 여기서 duration을 max_shorts_duration으로 강제 조정하거나, 스크립트 재요청 로직 추가 가능


        subtitle_file = "subtitles.srt"
        generate_subtitles(script_text, subtitle_file, duration)

        video_file = "final_video.mp4"
        create_video(audio_file, subtitle_file, video_file, duration)

        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        video_title = f"AI 생성 자동화 영상: {current_date} 주요 트렌드 #shorts" # 쇼츠용 제목에 #shorts 추가
        video_description = (
            f"{current_date}, AI가 생성한 대한민국 주요 트렌드 요약 영상입니다.\n\n"
            f"스크립트 내용:\n{script_text}\n\n"
            "이 영상은 Python과 다양한 AI API를 사용하여 자동으로 생성 및 업로드되었습니다.\n"
            "#AIVideo #Automation #Python #Tech #News #Trends #유튜브쇼츠" # 쇼츠 관련 태그 추가
        )

        video_url = upload_to_youtube(video_file, video_title, video_description)
        
        # 알림 메시지에 URL 포함 확인
        if 'send_notification' in globals() and callable(send_notification):
            send_notification(f"✅ 영상 업로드 완료!\n제목: {video_title}\n링크: {video_url}")
        else:
            log("ℹ️ send_notification 함수를 찾을 수 없어 알림을 보내지 않았습니다.")


    except Exception as e:
        log(f"❌ 자동화 프로세스 중 치명적 오류 발생: {str(e)}")
        # 상세한 오류 추적을 위해 스택 트레이스도 로깅할 수 있습니다.
        import traceback
        log(f"오류 스택 트레이스:\n{traceback.format_exc()}")
        if 'send_notification' in globals() and callable(send_notification):
            send_notification(f"🚨 자동화 프로세스 실패!\n오류: {str(e)}")
        else:
            log("ℹ️ send_notification 함수를 찾을 수 없어 실패 알림을 보내지 않았습니다.")
    finally:
        log("🏁 자동화 종료")

if __name__ == "__main__":
    main()
