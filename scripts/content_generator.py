import os
import openai
import requests
import ffmpeg

# API 키 불러오기
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
OPENAI_API_KEYS = os.getenv("OPENAI_API_KEYS")

openai.api_key = OPENAI_API_KEY

def generate_script():
    print("🎬 ChatGPT로 스크립트 생성 중...")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "수익이 많이 날 흥미로운 유튜브 스크립트를 작성해줘. 90초 분량으로."},
            {"role": "user", "content": "오늘의 흥미로운 주제로 유튜브 콘텐츠를 만들어줘."}
        ]
    )
    return response.choices[0].message.content.strip()

def text_to_speech(text, output_path):
    print("🔊 ElevenLabs로 음성 생성 중...")
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
    print("🎞️ 오디오와 썸네일 영상 결합 중...")
    ffmpeg.input(image_path, loop=1, framerate=1).output(
        output_path,
        audio_path,
        vcodec='libx264',
        acodec='aac',
        shortest=None,
        pix_fmt='yuv420p'
    ).overwrite_output().run()

def main():
    os.makedirs("output", exist_ok=True)

    # 스크립트 생성
    script = generate_script()
    with open("output/script.txt", "w") as f:
        f.write(script)

    # 음성 생성
    audio_path = "output/narration.mp3"
    text_to_speech(script, audio_path)

    # 영상 생성 (input/thumbnail.jpg 필요)
    combine_audio_and_video(audio_path, "input/thumbnail.jpg", "output/video.mp4")

    print("✅ 영상 생성 완료!")

if __name__ == "__main__":
    main()
