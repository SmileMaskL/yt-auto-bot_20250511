from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip, ColorClip

def create_video_with_subtitles(audio_path: str, text: str, output_path: str):
    """
    음성 오디오에 맞춰 자막 추가, 배경 컬러 영상 생성 후 합성
    """
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # 배경 단색 영상 (1280x720, 24fps)
    bg_clip = ColorClip(size=(1280, 720), color=(30, 30, 30), duration=duration)

    # 자막 텍스트 클립
    subtitle = TextClip(text, fontsize=48, font='Arial', color='white', method='caption', size=(1200, None))
    subtitle = subtitle.set_position(('center', 'bottom')).set_duration(duration)

    video = CompositeVideoClip([bg_clip, subtitle])
    video = video.set_audio(audio_clip)
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
