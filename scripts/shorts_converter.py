import os
from moviepy.editor import VideoFileClip

def convert_to_shorts(input_path, output_path):
    clip = VideoFileClip(input_path).subclip(0, 60)  # 60초로 자르기
    clip.write_videofile(output_path, fps=24)
