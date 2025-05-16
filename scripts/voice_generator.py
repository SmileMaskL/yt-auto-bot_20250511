import os
from google.cloud import texttospeech
from elevenlabs import generate, save, set_api_key
import json

def generate_voice(text):
    if os.getenv("ELEVENLABS_API_KEY"):
        set_api_key(os.getenv("ELEVENLABS_API_KEY"))
        audio = generate(text=text, voice=os.getenv("ELEVENLABS_VOICE_ID"))
        path = "output_audio.mp3"
        save(audio, path)
        return path
    else:
        credentials = json.loads(os.getenv("GOOGLE_TOKEN_JSON"))
        client = texttospeech.TextToSpeechClient.from_service_account_info(credentials)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Wavenet-D"
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        path = "output_audio.mp3"
        with open(path, "wb") as out:
            out.write(response.audio_content)
        return path
