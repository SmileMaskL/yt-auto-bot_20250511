import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def create_video(image_path, audio_path, output_path):
    image_clip = ImageClip(image_path).set_duration(AudioFileClip(audio_path).duration)
    audio_clip = AudioFileClip(audio_path)
    video = image_clip.set_audio(audio_clip)
    video.write_videofile(output_path, fps=24)
