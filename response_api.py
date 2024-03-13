import json
import os
import argparse
from tqdm import tqdm
from dotenv import load_dotenv
from api import gemini, mistral, openai, claude
from response_inference import save_responses

load_dotenv()

PROMPT = os.getenv("RESPONSE_PROMPT")
RESPONSE_REPEAT = int(os.getenv("RESPONSE_REPEAT"))

TEMPLATE_PATH = "test/template.jsonl"


platforms = {
    "openai": {
        "models": openai.MODELS,
        "generate_func": openai.generate_response,
    },
    "mistral": {
        "models": mistral.MODELS,
        "generate_func": mistral.generate_response,
    },
    "gemini": {
        "models": gemini.MODELS,
        "generate_func": gemini.generate_response,
    },
    "claude": {
        "models": claude.MODELS,
        "generate_func": claude.generate_response,
    },
}


if __name__ == "__main__":
    argParser = argparse.ArgumentParser(description="Test various language models.")
    argParser.add_argument(
        "-p",
        "--platform",
        choices=platforms.keys(),
        help="the platform to test. Available platforms and models:\n"
        + ", ".join(
            f"{platform}: [{', '.join(info['models'])}]"
            for platform, info in platforms.items()
        ),
    )
    argParser.add_argument(
        "-m",
        "--model",
        help="the language model of interest on the given platform. If not specified, all available models will be tested.",
    )
    args = argParser.parse_args()
    platform = args.platform
    model = args.model

    statements = json.loads(open(TEMPLATE_PATH, "r", encoding="utf-8").read())

    if platform:
        platforms_to_process = {platform: platforms[platform]}
    else:
        platforms_to_process = platforms

    for platform, info in platforms_to_process.items():
        models_to_process = [model] if model else info["models"]
        for mdl in models_to_process:
            for statement in tqdm(statements, desc=f"{platform}: Generating {mdl}"):
                input_text = PROMPT.replace("<statement>", statement["statement"])
                statement["response"] = info["generate_func"](mdl, input_text)
            save_responses(mdl, statements)
