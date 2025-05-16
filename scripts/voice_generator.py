import os
from gtts import gTTS

def generate_voice(text, filename):
    tts = gTTS(text=text, lang='ko')
    filepath = os.path.join("data", "audio", f"{filename}.mp3")
    tts.save(filepath)
    return filepath
