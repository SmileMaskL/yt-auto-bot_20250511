# scripts/test_create_video.py

import os
import tempfile
import pytest
from scripts.create_video import create_video_with_ffmpeg
from scripts.voice_generator import generate_voice
from moviepy.editor import AudioFileClip

def test_create_video_pipeline():
    text = "테스트용 자동 생성 텍스트입니다."

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "speech.mp3")
        video_path = os.path.join(tmpdir, "output.mp4")

        # 음성 생성
        generate_voice(text, audio_path)

        # 오디오 길이 확인
        duration = AudioFileClip(audio_path).duration

        # 영상 생성 시도
        create_video_with_ffmpeg(
            audio_path=audio_path,
            text=text,
            output_path=video_path,
            duration=duration
        )

        assert os.path.exists(video_path), "❌ 영상 파일이 생성되지 않았습니다."
