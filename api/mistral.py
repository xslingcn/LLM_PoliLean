import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

MAX_NEW_TOKENS = int(os.getenv("RESPONSE_MAX_NEW_TOKENS"))
RESPONSE_PROMPT = os.getenv("RESPONSE_PROMPT")
API_KEY = os.getenv("MISTRAL_API_KEY")
ENDPOINT = os.getenv("MISTRAL_ENDPOINT")


def generate_response(model, input_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": input_text},
        ],
        "max_tokens": MAX_NEW_TOKENS,
    }
    response = requests.post(ENDPOINT, headers=headers, json=data, timeout=5000)
    if response.status_code == 200:
        response_data = response.json()
        generated_response = response_data["choices"][0]["message"]["content"]
        return generated_response.strip()
    else:
        print(f"Error: {response.status_code}", response.json())
        return ""
