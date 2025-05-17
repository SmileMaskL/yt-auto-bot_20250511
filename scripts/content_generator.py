import os
import json
import random
import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import ImageFont
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# ✅ 환경 변수 로드 및 확인
load_dotenv()
os.makedirs("output", exist_ok=True)

REQUIRED_ENV = [
    "OPENAI_API_KEYS",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    "GCP_KEY_PATH"
]

for var in REQUIRED_ENV:
    if not os.getenv(var):
        raise Exception(f"{var} 환경변수가 설정되지 않았습니다!")

# ✅ OpenAI 클라이언트 매니저
class OpenAIClientManager:
    def __init__(self):
        self.keys = json.loads(os.getenv("OPENAI_API_KEYS"))
    def get_client(self):
        key = random.choice(self.keys)
        print(f"🔑 사용중인 OpenAI 키: {key[:8]}****")
        return OpenAI(api_key=key)

# ✅ 콘텐츠 생성기
class ContentGenerator:
    def __init__(self):
        self.oaic_manager = OpenAIClientManager()
        self.eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def generate_script(self):
        client = self.oaic_manager.get_client()
        prompt = """
        2025년 최신 트렌드를 반영한 충격적인 사실을 30초 분량의 유튜브 Shorts용 대본을 작성해주세요.
        - 첫 3초 안에 시선을 사로잡는 문장
        - 중간에 놀라운 통계 수치
        - 끝부분에 구독 유도 문구
        - 해시태그 3개 포함
        """
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    def generate_voice(self, text):
        audio_path = "output/audio.mp3"
        audio = self.eleven_client.generate(
            text=text,
            voice=os.getenv("ELEVENLABS_VOICE_ID"),
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.3,
                similarity_boost=0.9,
                style=0.5,
                use_speaker_boost=True
            )
        )
        with open(audio_path, "wb") as f:
            f.write(audio)
        print(f"🔊 음성 저장 완료: {audio_path}")
        return audio_path

    def create_subtitles(self, text, duration):
        words = text.split()
        subs = []
        chunk_size = max(1, len(words) // 6)
        for i in range(0, len(words), chunk_size):
            start = i * (duration / len(words))
            end = (i + chunk_size) * (duration / len(words))
            subs.append(((start, end), ' '.join(words[i:i+chunk_size])))
        return subs

    def generate_video(self, audio_path, text):
        audio = AudioFileClip(audio_path)
        duration = audio.duration

        clips = []
        for i in range(0, int(duration), 2):
            color = tuple(random.randint(0, 255) for _ in range(3))
            clip = ColorClip(size=(1080, 1920), color=color, duration=2)
            clips.append(clip)

        background = concatenate_videoclips(clips).set_audio(audio)
        subs = self.create_subtitles(text, duration)
        generator = lambda txt: TextClip(txt, font='Arial-Bold', fontsize=60, color='white', method='caption')
        subtitles = SubtitlesClip(subs, generator)

        final = CompositeVideoClip([background, subtitles.set_position(('center', 'bottom'))])
        final.write_videofile("output/final_video.mp4", fps=24, codec='libx264')
        print("🎬 영상 생성 완료")
        return "output/final_video.mp4"

# ✅ 유튜브 업로더
class YouTubeUploader:
    def __init__(self):
        self.credentials = Credentials.from_service_account_file(
            os.getenv("GCP_KEY_PATH"),
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

    def upload(self, video_path):
        request_body = {
            'snippet': {
                'title': f"AI Shorts - {datetime.datetime.now().strftime('%Y-%m-%d')}",
                'description': "AI가 만든 유튜브 Shorts입니다. 매일 자동 생성됩니다.\n#shorts #AI #자동화",
                'categoryId': '27',
                'tags': ['shorts', 'AI', '자동화']
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        )
        response = None
        while not response:
            status, response = request.next_chunk()
            if status:
                print(f"📤 업로드 진행률: {int(status.progress() * 100)}%")
        print(f"✅ 업로드 완료! 영상 ID: {response['id']}")
        return response['id']

# ✅ 실행 시작
if __name__ == "__main__":
    print("🚀 자동 유튜브 Shorts 생성 시작")
    gen = ContentGenerator()
    uploader = YouTubeUploader()

    try:
        print("📝 스크립트 생성 중...")
        script = gen.generate_script()
        print(f"✔ 스크립트:\n{script}")

        print("🎧 음성 생성 중...")
        audio = gen.generate_voice(script)

        print("📹 영상 생성 중...")
        video_path = gen.generate_video(audio, script)

        print("☁ 유튜브 업로드 중...")
        video_id = uploader.upload(video_path)
        print(f"🎉 완료! 영상 링크: https://youtube.com/shorts/{video_id}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
