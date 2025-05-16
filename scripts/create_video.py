from moviepy.editor import *

def create_video(audio_path, script_text, output_path="output/video.mp4"):
    audioclip = AudioFileClip(audio_path)
    txt_clip = TextClip(script_text[:80], fontsize=48, color='white', size=(720, 1280), method='caption')
    txt_clip = txt_clip.set_duration(audioclip.duration).set_position('center')

    final = CompositeVideoClip([txt_clip.set_audio(audioclip)])
    final.write_videofile(output_path, fps=24)
    return output_path
