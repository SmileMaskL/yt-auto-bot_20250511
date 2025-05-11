# YouTube 업로드 관련 기능
# YouTube 업로드 관련 기능
import os
import tempfile
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# MoviePy 임포트
try:
    from moviepy.editor import TextClip, AudioFileClip, ImageClip, CompositeVideoClip
except ImportError as e:
    raise RuntimeError("MoviePy 설치 오류: pip install moviepy==2.1.2") from e

# FFmpeg 경로 설정
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_tts_audio(script):
    """ElevenLabs API를 사용한 고품질 TTS 구현"""
    from elevenlabs import generate, save
    audio_file = tempfile.mktemp(suffix='.mp3')
    try:
        audio = generate(text=script, voice="Bella")
        save(audio, audio_file)
    except Exception as e:
        logging.error(f"TTS 생성 실패: {e}")
        raise
    return audio_file

def create_thumbnail(keyword):
    """Pillow를 활용한 동적 썸네일 생성"""
    from PIL import Image, ImageDraw, ImageFont
    thumbnail_file = tempfile.mktemp(suffix='.png')
    try:
        img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        font_path = os.path.join('fonts', 'NotoSansCJK-Regular.otf')
        font = ImageFont.truetype(font_path, 60)
        d.text((100, 300), keyword, fill=(255,255,0), font=font)
        img.save(thumbnail_file)
    except Exception as e:
        logging.error(f"썸네일 생성 실패: {e}")
        raise
    return thumbnail_file

def create_video(script, audio_file, thumbnail_file):
    """MoviePy 비디오 생성 로직 강화"""
    video_file = tempfile.mktemp(suffix='.mp4')
    try:
        audio_clip = AudioFileClip(audio_file)
        text_clip = TextClip(
            txt=script,
            fontsize=40,
            color='white',
            font='Noto-Sans-CJK',
            size=(1200, None),
            method='caption'
        ).set_position('center').set_duration(audio_clip.duration)

        image_clip = ImageClip(thumbnail_file).set_duration(audio_clip.duration)

        video = CompositeVideoClip([image_clip, text_clip]).set_audio(audio_clip)
        video.write_videofile(
            video_file,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            fps=24,
            logger=None
        )
    except Exception as e:
        logging.error(f"비디오 생성 실패: {e}")
        raise
    return video_file

def get_authenticated_service():
    """Google 인증 프로세스 개선"""
    if not os.path.exists('token.json'):
        raise FileNotFoundError("token.json 파일이 존재하지 않습니다.")

    credentials = Credentials.from_authorized_user_file(
        'token.json',
        scopes=['https://www.googleapis.com/auth/youtube.upload']
    )

    if credentials.expired:
        try:
            credentials.refresh(Request())
        except Exception as e:
            logging.error(f"토큰 리프레시 실패: {e}")
            raise

    return build('youtube', 'v3', credentials=credentials)

def upload_video(youtube, video_file, title, description, thumbnail_file):
    """업로드 실패 감지 로직 추가"""
    try:
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title[:95],
                    "description": description[:4500],
                    "tags": ["자동화", "AI", "YouTube"],
                    "categoryId": "27"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=media
        )
        response = None
        while not response:
            status, response = request.next_chunk()
            if status:
                logging.info(f"진행률: {int(status.progress() * 100)}%")
        # 썸네일 업로드
        youtube.thumbnails().set(
            videoId=response['id'],
            media_body=MediaFileUpload(thumbnail_file)
        ).execute()
        return response['id']
    except Exception as e:
        logging.error(f"업로드 실패: {e}")
        raise

def post_comment(youtube, video_id, comment):
    """댓글 필터링 기능 추가"""
    from profanity_filter import ProfanityFilter
    pf = ProfanityFilter()
    if pf.is_clean(comment):
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment[:500]
                        }
                    }
                }
            }
        ).execute()
    else:
        logging.warning("부적절한 댓글 필터링됨")
