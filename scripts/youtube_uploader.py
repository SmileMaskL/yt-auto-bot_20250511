# YouTube 업로드 관련 기능
from moviepy.editor import TextClip, AudioFileClip, ImageClip, CompositeVideoClip
import os
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

def generate_tts_audio(script):
    # 텍스트에서 오디오 파일 생성 (Eleven Labs API 활용)
    audio_file = tempfile.mktemp(suffix='.mp3')
    # TTS API 호출하여 audio_file 생성
    logging.info(f"오디오 파일 생성: {audio_file}")
    return audio_file

def create_thumbnail(keyword):
    # 썸네일 생성 (간단한 이미지 처리)
    thumbnail_file = tempfile.mktemp(suffix='.png')
    # 썸네일 생성 코드
    logging.info(f"썸네일 파일 생성: {thumbnail_file}")
    return thumbnail_file

def create_video(script, audio_file, thumbnail_file):
    # 비디오 생성 (moviepy 사용)
    video_file = tempfile.mktemp(suffix='.mp4')
    
    # 텍스트, 오디오, 이미지 합성하여 비디오 생성
    text_clip = TextClip(script, fontsize=24, color='white')
    audio_clip = AudioFileClip(audio_file)
    image_clip = ImageClip(thumbnail_file).set_duration(audio_clip.duration)

    video = CompositeVideoClip([image_clip, text_clip.set_position('center')]).set_audio(audio_clip)
    video.write_videofile(video_file, codec='libx264')
    
    logging.info(f"비디오 파일 생성: {video_file}")
    return video_file

def get_authenticated_service():
    # Google API 인증 과정
    credentials = Credentials.from_authorized_user_file('token.json', scopes=['https://www.googleapis.com/auth/youtube.upload'])
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            logging.error("Google API 인증 실패")
            raise Exception("Google API 인증 실패")
    return build('youtube', 'v3', credentials=credentials)

def upload_video(youtube, video_file, title, description, thumbnail_file):
    # YouTube에 비디오 업로드
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["자동화", "YouTube", "AI"]
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
    )
    response = request.execute()
    logging.info(f"비디오 업로드 완료: {response['id']}")
    return response['id']

def post_comment(youtube, video_id, comment):
    # 비디오에 댓글 달기
    youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment
                    }
                }
            }
        }
    ).execute()
    logging.info(f"댓글 업로드 완료: {comment}")
