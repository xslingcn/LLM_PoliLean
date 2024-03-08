import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

MAX_NEW_TOKENS = int(os.getenv("RESPONSE_MAX_NEW_TOKENS"))
RESPONSE_PROMPT = os.getenv("RESPONSE_PROMPT")
API_KEY = os.getenv("GEMINI_API_KEY")
ENDPOINT = os.getenv("GEMINI_ENDPOINT")


def generate_response(model, input_text):
    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [{"parts": [{"text": input_text}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
        # "generationConfig": {
        #     "maxOutputTokens": MAX_NEW_TOKENS,    # Gemini is broken with the maxOutputTokens parameter
        # },
    }

    url = f"{ENDPOINT}/models/{model}:generateContent?key={API_KEY}"
    response = requests.post(url, headers=headers, json=data, timeout=5000)
    if response.status_code == 200:
        response_data = response.json()
        generated_response = response_data["candidates"][0]["content"]["parts"][0][
            "text"
        ]
        return generated_response.strip()
    else:
        print(f"Error: {response.status_code}")
        time.sleep(5)
        return generate_response(model, input_text)
