
import os
import json
import traceback
from youtube_uploader import generate_and_upload

def check_secrets():
    try:
        openai_keys = json.loads(os.environ.get("OPENAI_API_KEYS", "[]"))
        elevenlabs_keys = json.loads(os.environ.get("ELEVENLABS_KEYS", "[]"))
        google_refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
        google_client_secret = json.loads(os.environ.get("GOOGLE_CLIENT_SECRET_JSON", "{}"))

        assert openai_keys and all(k.startswith("sk-") for k in openai_keys), "OPENAI_API_KEYS error"
        assert elevenlabs_keys, "ELEVENLABS_KEYS error"
        assert google_refresh_token and len(google_refresh_token) > 30, "GOOGLE_REFRESH_TOKEN error"
        assert google_client_secret.get("installed"), "GOOGLE_CLIENT_SECRET_JSON error"

        print("\n🎉 Secrets loaded successfully!\n")
    except Exception as e:
        print("\n🚨 Secret check failed:", e)
        raise

def notify_error(error_message):
    slack_url = os.environ.get("SLACK_WEBHOOK_URL")
    if slack_url:
        import requests
        requests.post(slack_url, json={"text": f":warning: YouTube AutoUploader Failed:\n{error_message}"})

if __name__ == "__main__":
    try:
        check_secrets()
        generate_and_upload()
    except Exception as err:
        error_trace = traceback.format_exc()
        print("\n🚨 Execution failed:\n", error_trace)
        notify_error(error_trace)
        raise
