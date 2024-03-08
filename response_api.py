import json
import os
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv
from api import gemini, mistral, openai, claude

load_dotenv()

PROMPT = os.getenv("RESPONSE_PROMPT")
# RESPONSE_REPEAT = int(os.getenv("RESPONSE_REPEAT"))
RESPONSE_REPEAT = 3

TEMPLATE_PATH = "response/template.jsonl"


def generate_openai(statements):
    models = ["gpt-3.5-turbo-0125", "gpt-4-0125-preview"]
    for model in models:
        for statement in tqdm(statements, desc="Generating " + model):
            input_text = PROMPT.replace("<statement>", statement["statement"])
            statement["response"] = openai.generate_response(model, input_text)
        save_responses(model, statements)


def generate_mistral(statements):
    models = ["mistral-small-2402", "mistral-medium-2312", "mistral-large-2402"]
    for model in models:
        for statement in tqdm(statements, desc="Generating " + model):
            input_text = PROMPT.replace("<statement>", statement["statement"])
            statement["response"] = mistral.generate_response(model, input_text)
        save_responses(model, statements)


def generate_gemini(statements):
    models = ["gemini-pro"]  # February 2024 version
    for model in models:
        for statement in tqdm(statements, desc="Generating " + model):
            input_text = PROMPT.replace("<statement>", statement["statement"])
            statement["response"] = gemini.generate_response(model, input_text)
        save_responses(model, statements)


def generate_claude(statements):
    models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
    for model in models:
        for statement in tqdm(statements, desc="Generating " + model):
            input_text = PROMPT.replace("<statement>", statement["statement"])
            statement["response"] = claude.generate_response(model, input_text)
        save_responses(model, statements)


def save_responses(model_name, statements):
    formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    directory = "response/" + model_name + "/"
    file_path = directory + formatted_date + ".jsonl"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(statements, f, indent=4)


if __name__ == "__main__":
    statements = json.loads(open(TEMPLATE_PATH, "r", encoding="utf-8").read())

    for _ in tqdm(range(RESPONSE_REPEAT), desc="Iterating generations"):
        generate_openai(statements)
        generate_mistral(statements)
        # generate_gemini(statements)
        generate_claude(statements)
