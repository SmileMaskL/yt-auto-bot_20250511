import os
import openai
import requests
import ffmpeg

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEYS_BASE64")

openai.api_key = OPENAI_API_KEY

def generate_script():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "수익이 많이 날 흥미로운 유튜브 스크립트를 작성해줘. 90초 분량으로."},
            {"role": "user", "content": "오늘의 흥미로운 주제로 유튜브 콘텐츠를 만들어줘."}
        ]
    )
    return response.choices[0].message.content.strip()

def text_to_speech(text, output_path):
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
        }
    )
    with open(output_path, "wb") as f:
        f.write(response.content)

def combine_audio_and_video(audio_path, image_path, output_path):
    ffmpeg.input(image_path, loop=1, framerate=1).output(
        audio_path,
        output_path,
        vcodec='libx264',
        acodec='aac',
        shortest=None,
        pix_fmt='yuv420p'
    ).overwrite_output().run()

def main():
    os.makedirs("output", exist_ok=True)
    script = generate_script()
    with open("output/script.txt", "w") as f:
        f.write(script)
    audio_path = "output/narration.mp3"
    text_to_speech(script, audio_path)
    combine_audio_and_video(audio_path, "input/thumbnail.jpg", "output/video.mp4")

if __name__ == "__main__":
    main()
