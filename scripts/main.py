# scripts/main.py

# sys.path 설정: scripts 폴더가 모듈 경로에 포함되도록
import sys
import os
sys.path.append(os.path.dirname(__file__))

from analytics_bot import get_top_video_titles
from content_generator import generate_content
from voice_generator import generate_voice
from create_video import create_video_file
from thumbnail_generator import generate_thumbnail
from youtube_uploader import upload_video

def main():
    print("===== YouTube 자동화 시작 =====")

    # 1. 인기 영상 제목 가져오기
    titles = get_top_video_titles()
    print(f"인기 영상 제목들: {titles}")

    # 2. 콘텐츠 스크립트 생성
    content_script = generate_content(titles[0])
    print(f"생성된 콘텐츠: {content_script}")

    # 3. 음성 생성
    audio_path = generate_voice(content_script)
    print(f"생성된 음성 파일 경로: {audio_path}")

    # 4. 영상 제작
    video_path = create_video_file(audio_path, content_script)
    print(f"생성된 영상 파일 경로: {video_path}")

    # 5. 썸네일 생성
    thumbnail_path = generate_thumbnail(titles[0])
    print(f"생성된 썸네일 파일 경로: {thumbnail_path}")

    # 6. 유튜브에 업로드
    upload_video(video_path, thumbnail_path, titles[0], content_script)
    print("===== 유튜브 자동 업로드 완료! =====")

if __name__ == "__main__":
    main()
