from moviepy.editor import *
import os

def create_video(audio_path, text, subtitles_path):
    clip = ColorClip(size=(720, 1280), color=(255, 255, 255), duration=10)
    audio = AudioFileClip(audio_path)
    clip = clip.set_audio(audio)

    txt = TextClip(text, fontsize=48, color='black', size=(700, None), method='caption')
    txt = txt.set_position('center').set_duration(10)
    video = CompositeVideoClip([clip, txt])
    video.write_videofile("output/video.mp4", fps=24)
    return "output/video.mp4"
