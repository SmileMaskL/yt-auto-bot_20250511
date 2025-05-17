import os
import subprocess

def create_video_with_ffmpeg(audio_path, image_path, output_path):
    """
    FFmpeg를 사용해 이미지 + 오디오 → 영상으로 변환
    """
    command = [
        'ffmpeg',
        '-y',
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_path
    ]
    subprocess.run(command, check=True)
    return output_path
