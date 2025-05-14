from google.cloud import texttospeech
import os

class VoiceEngine:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        
    def synthesize(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Wavenet-C"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        with open("audio.mp3", "wb") as out:
            out.write(response.audio_content)
        return "audio.mp3"
