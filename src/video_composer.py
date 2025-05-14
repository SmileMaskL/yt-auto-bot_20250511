from moviepy.editor import *
import cv2
import numpy as np

class VideoProducer:
    def __init__(self):
        self.resolution = (1080, 1920)
        
    def _generate_background(self):
        # 동적 배경 생성
        return ColorClip(size=self.resolution, color=(30,30,30))
    
    def _add_text(self, clip, text):
        return TextClip(text, fontsize=45, color='white', 
                       font='NanumGothic', method='caption',
                       size=(900, None)).set_position('center')
    
    def create_video(self, script, audio_path):
        bg_clip = self._generate_background()
        txt_clip = self._add_text(bg_clip, script)
        final = CompositeVideoClip([bg_clip, txt_clip])
        final = final.set_audio(AudioFileClip(audio_path))
        final.write_videofile("final_output.mp4", fps=24)
        return "final_output.mp4"
