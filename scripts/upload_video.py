import argparse
import os
import pickle
import json
import ffmpeg
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from elevenlabs import generate

def generate_voice(text, voice_id, api_key, output_path):
    audio = generate(
        text=text,
        voice=voice_id,
        model='eleven_multilingual_v1',
        api_key=api_key
    )
    with open(output_path, 'wb') as f:
        f.write(audio)

def combine_audio_video(video_path, audio_path, output_path):
    input_video = ffmpeg.input(video_path)
    input_audio = ffmpeg.input(audio_path)
    ffmpeg.output(input_video.video, input_audio.audio, output_path, vcodec='copy', acodec='aac').run(overwrite_output=True)

def upload_video(file, title, description, category, keywords, privacy_status):
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    with open("credentials.json") as f:
        creds_data = json.load(f)

    flow = InstalledAppFlow.from_client_config(creds_data, scopes)
    creds = flow.run_local_server(port=0)

    with open("token.json", "wb") as token:
        pickle.dump(creds, token)

    youtube = build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": keywords.split(","),
            "categoryId": category
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media_file = MediaFileUpload(file)

    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    ).execute()

    print(f"Video uploaded: https://www.youtube.com/watch?v={response['id']}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--description', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--keywords', required=True)
    parser.add_argument('--privacy_status', required=True)
    args = parser.parse_args()

    narration_text = "이것은 자동 생성된 영상의 나레이션입니다."
    voice_output_path = "output/narration.mp3"
    video_input_path = "input/video.mp4"
    video_output_path = args.file

    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    generate_voice(narration_text, voice_id, api_key, voice_output_path)
    combine_audio_video(video_input_path, voice_output_path, video_output_path)
    upload_video(video_output_path, args.title, args.description, args.category, args.keywords, args.privacy_status)

if __name__ == "__main__":
    main()
