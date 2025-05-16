import os
import openai
from scripts.api_manager import rotate_openai_key

def generate_script(topic):
    rotate_openai_key()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"{topic}에 대한 유튜브 스크립트를 작성해줘."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
