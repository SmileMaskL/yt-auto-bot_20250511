from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import os

def create_video(audio_path, script_text, subtitles_path, output_path="output/video.mp4"):
    audioclip = AudioFileClip(audio_path)

    # 텍스트 클립 생성
    txt_clip = TextClip(script_text[:80], fontsize=48, color='white', size=(720, 1280), method='caption')
    txt_clip = txt_clip.set_duration(audioclip.duration).set_position('center')

    # 배경 클립 생성
    background = ColorClip(size=(720, 1280), color=(0, 0, 0), duration=audioclip.duration)

    # 자막 클립 생성
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white')
    subtitles = SubtitlesClip(subtitles_path, generator)

    # 최종 영상 합성
    final = CompositeVideoClip([background, txt_clip.set_audio(audioclip), subtitles.set_position(('center', 'bottom'))])
    final.write_videofile(output_path, fps=24)
    return output_path
