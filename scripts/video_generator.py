import os
from moviepy.editor import ImageClip, AudioFileClip

def create_video(image_path, audio_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path).set_duration(audio_clip.duration)
    video = image_clip.set_audio(audio_clip)
    video.write_videofile(output_path, fps=24)
