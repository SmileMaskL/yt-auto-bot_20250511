import os
from google.cloud import texttospeech

def generate_voice(text: str) -> str:
    """
    Google Cloud TTS API를 사용해 음성 생성
    생성된 음성 파일 경로 반환
    """
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    audio_path = "output_audio.mp3"
    with open(audio_path, "wb") as out:
        out.write(response.audio_content)

    return audio_path
