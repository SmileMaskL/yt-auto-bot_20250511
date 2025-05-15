import os
from elevenlabs import generate, save, set_api_key

set_api_key(os.getenv("ELEVEN_API_KEY"))

def generate_voice(text: str, voice="Rachel") -> str:
    audio = generate(text=text, voice=voice)
    audio_path = "output_audio.mp3"
    save(audio, audio_path)
    return audio_path
