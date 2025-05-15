from scripts.notifier import send_notification

def handle_error(e):
    send_notification(f"❌ 오류 발생: {str(e)}")
