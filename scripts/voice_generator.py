# ✅ scripts/voice_generator.py

import requests
import os

def generate_voice(text, output_path):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json={"text": text, "model_id": "eleven_monolingual_v1"}
    )

    with open(output_path, "wb") as f:
        f.write(response.content)
