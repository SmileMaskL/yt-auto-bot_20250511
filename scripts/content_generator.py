import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script():
    prompt = "오늘의 흥미로운 유튜브 쇼츠 주제를 알려줘."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
