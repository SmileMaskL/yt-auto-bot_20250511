from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip, ColorClip

def create_video_with_subtitles(audio_path: str, text: str, output_path: str):
    """
    음성에 자막과 배경을 입힌 영상 생성
    """
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # 배경 색상 설정 (수익화에 적합한 어두운 톤)
    bg_clip = ColorClip(size=(1280, 720), color=(30, 30, 30), duration=duration)

    # 텍스트 클립 생성 (자막)
    subtitle = TextClip(text, fontsize=48, font='Arial', color='white', method='caption', size=(1200, None))
    subtitle = subtitle.set_position(('center', 'bottom')).set_duration(duration)

    # 최종 영상 합성
    video = CompositeVideoClip([bg_clip, subtitle])
    video = video.set_audio(audio_clip)
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
