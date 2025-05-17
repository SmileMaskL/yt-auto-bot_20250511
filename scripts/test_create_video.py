import os
from scripts.create_video import create_video_with_ffmpeg

def test_create_video():
    audio_path = "assets/sample_audio.mp3"
    image_path = "assets/sample_image.jpg"
    output_path = "outputs/test_video.mp4"

    os.makedirs("outputs", exist_ok=True)
    result = create_video_with_ffmpeg(audio_path, image_path, output_path)

    assert os.path.exists(result), "영상 생성 실패"
