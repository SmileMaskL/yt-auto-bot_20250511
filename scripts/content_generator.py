# ✅ scripts/content_generator.py

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content
