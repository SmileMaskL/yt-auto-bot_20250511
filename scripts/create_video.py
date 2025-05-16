from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip, ColorClip

def create_video_with_subtitles(audio_path: str, text: str, output_path: str):
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    bg_clip = ColorClip(size=(1280, 720), color=(30, 30, 30), duration=duration)
    subtitle = TextClip(
        text,
        fontsize=48,
        font='Arial',
        color='white',
        method='caption',
        size=(1200, None)
    ).set_position(('center', 'bottom')).set_duration(duration)
    video = CompositeVideoClip([bg_clip, subtitle])
    video = video.set_audio(audio_clip)
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
