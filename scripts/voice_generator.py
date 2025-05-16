from gtts import gTTS

def text_to_speech(text, filename="output.mp3"):
    tts = gTTS(text=text, lang='ko')
    tts.save(filename)
    return filename
