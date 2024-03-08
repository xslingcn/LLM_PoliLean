import time
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

MAX_NEW_TOKENS = int(os.getenv("RESPONSE_MAX_NEW_TOKENS"))
API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT = os.getenv("OPENAI_ENDPOINT")
STANCE_PROMPT = os.getenv("STANCE_PROMPT")


def generate_response(model, input_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": input_text},
        ],
        "max_tokens": MAX_NEW_TOKENS,
    }
    response = requests.post(ENDPOINT, headers=headers, json=data, timeout=5000)
    response_data = response.json()
    if response.status_code == 200 and len(response_data["choices"]) > 0:
        generated_response = response_data["choices"][0]["message"]["content"]
        return generated_response.strip()
    else:
        print(f"Error: {response.status_code}, data: {response_data}")
        time.sleep(5)
        return generate_response(model, input_text)


def stance_detection(query):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    message = STANCE_PROMPT + json.dumps(query, indent=4)
    data = {
        "model": "gpt-4-0125-preview",
        "messages": [
            {"role": "system", "content": message},
        ],
        "response_format": {"type": "json_object"},
    }
    response = requests.post(ENDPOINT, headers=headers, json=data, timeout=5000)
    response_data = response.json()
    if response.status_code == 200 and len(response_data["choices"]) > 0:
        content = response_data["choices"][0]["message"]["content"]
        stances = json.loads(content)
        return stances
    else:
        print(f"Error: {response.status_code}, data: {response_data}")
        time.sleep(5)
        return stance_detection(query)
