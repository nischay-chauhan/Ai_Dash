import os
import requests

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"  

def call_groq_insights(prompt: str, model: str = "gpt-oss"):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a data insights assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_output_tokens": 500
    }
    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    resp = response.json()
    return resp["choices"][0]["message"]["content"]
