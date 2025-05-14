from moviepy.editor import *
import textwrap

class VideoProducer:
    def __init__(self):
        self.resolution = (1080, 1920)  # 세로형 영상
        
    def render(self, content):
        # 영상 생성 로직
        clip = ColorClip(size=self.resolution, color=(0,0,0))
        text = TextClip(content, fontsize=40, color='white').set_position('center')
        final = CompositeVideoClip([clip, text])
        final.write_videofile("output.mp4", fps=24)
        return "output.mp4"
