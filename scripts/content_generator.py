import openai
import os

def generate_script():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = "오늘의 인기있는 주제에 대해 YouTube Shorts 스크립트를 만들어줘."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content'].strip()
