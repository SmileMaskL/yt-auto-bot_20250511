from moviepy.editor import *

def create_video(audio_path, script_text, output_path="output.mp4"):
    # 배경 이미지 설정
    image_clip = ImageClip("background.jpg").set_duration(60)

    # 오디오 클립 설정
    audio_clip = AudioFileClip(audio_path)

    # 텍스트 오버레이 설정
    txt_clip = TextClip(script_text, fontsize=24, color='white')
    txt_clip = txt_clip.set_position('bottom').set_duration(60)

    # 영상 결합
    video = CompositeVideoClip([image_clip, txt_clip])
    video = video.set_audio(audio_clip)
    video.write_videofile(output_path, fps=24)
    return output_path
