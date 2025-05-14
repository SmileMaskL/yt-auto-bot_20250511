# 영상+썸네일 생성
from moviepy.editor import *
import cv2
import numpy as np

class VideoProducer:
    def __init__(self, resolution="1080p"):
        self.resolution = (1080, 1920) if resolution == "1080p" else (720, 1280)

    def create_video(self, script, audio_path):
        # 배경 생성
        bg = ColorClip(size=self.resolution, color=(30, 30, 30))
        
        # 자막 추가
        text = TextClip(script, fontsize=40, color='white', 
                       font='NanumGothic', method='caption',
                       size=(self.resolution[0]*0.9, None))
        
        # 썸네일 생성
        thumbnail = self._generate_thumbnail(script[:30])
        
        # 영상 합성
        video = CompositeVideoClip([bg, text.set_position('center')])
        video = video.set_audio(AudioFileClip(audio_path))
        video.write_videofile("output.mp4", fps=24)
        
        return "output.mp4", thumbnail

    def _generate_thumbnail(self, text):
        img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        cv2.putText(img, text, (100, 500), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 5)
        cv2.imwrite("thumbnail.jpg", img)
        return "thumbnail.jpg"
