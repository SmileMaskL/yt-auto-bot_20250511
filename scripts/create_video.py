from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip

def create_video_with_subtitles(audio_path, text, output_path):
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    subtitle = TextClip(text, fontsize=24, color='white')
    subtitle = subtitle.set_position(('center', 'bottom')).set_duration(duration)

    video = CompositeVideoClip([subtitle])
    video.audio = audio_clip
    video.write_videofile(output_path, fps=24)
