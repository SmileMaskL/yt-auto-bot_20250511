# 에러 알림 기능 (이메일/Slack)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_error_notification(error_message):
    client = WebClient(token=os.environ['SLACK_API_TOKEN'])
    try:
        response = client.chat_postMessage(
            channel='#your-channel-id',
            text=f"❗ Error in YouTube Automation: {error_message}"
        )
    except SlackApiError as e:
        print(f"Error sending message to Slack: {e.response['error']}")
