import time
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

MAX_NEW_TOKENS = int(os.getenv("RESPONSE_MAX_NEW_TOKENS"))
RESPONSE_PROMPT = os.getenv("RESPONSE_PROMPT")
API_KEY = os.getenv("CLAUDE_API_KEY")
ENDPOINT = os.getenv("CLAUDE_ENDPOINT")


def generate_response(model, input_text):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": input_text},
        ],
        "max_tokens": MAX_NEW_TOKENS,
    }
    response = requests.post(ENDPOINT, headers=headers, json=data, timeout=5000)
    response_data = response.json()
    if response.status_code == 200 and len(response_data["content"]) > 0:
        generated_response = response_data["content"][0]["text"]
        return generated_response.strip()
    else:
        print(f"Error: {response.status_code}, data: {response_data}")
        time.sleep(5)
        return generate_response(model, input_text)
