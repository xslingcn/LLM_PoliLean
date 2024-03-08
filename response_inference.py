import json
import os
from datetime import datetime
import argparse
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv

load_dotenv()

RESPONSE_REPEAT = int(os.getenv("RESPONSE_REPEAT"))
MAX_NEW_TOKENS = int(os.getenv("RESPONSE_MAX_NEW_TOKENS"))
PROMPT = os.getenv("RESPONSE_PROMPT")

TEMPLATE_PATH = "response/template.jsonl"
MODELS_PATH = "response/models.jsonl"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"


def load_model_and_tokenizer(model_info):
    model_id = model_info["organization"] + "/" + model_info["name"]

    model_kwargs = {}
    if model_info["flash_attn"]:
        model_kwargs["attn_implementation"] = "flash_attention_2"
        model_kwargs["torch_dtype"] = torch.float16

    model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
    model.to(DEVICE)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    return tokenizer, model


def generate_responses(tokenizer, model, statements):
    responses = []
    for statement in tqdm(statements, desc="Generating"):
        input_text = PROMPT.replace("<statement>", statement["statement"])
        input_ids = tokenizer(input_text, return_tensors="pt").to(DEVICE)
        output = tokenizer.decode(
            model.generate(
                **input_ids,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )[0]
        )
        response = (
            output.replace(input_text, "")
            .replace("<bos>", "")
            .replace("<eos>", "")
            .replace("<s>", "")
            .replace("<|endoftext|>", "")
            .strip()
        )
        responses.append(response)
    return responses


def save_responses(model_name, statements):
    formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    directory = "response/" + model_name + "/"
    file_path = directory + formatted_date + ".jsonl"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(statements, f, indent=4)


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument(
        "-m", "--model", help="the language model of interest on HuggingFace"
    )
    argParser.add_argument(
        "-f",
        "--flash-attn",
        action="store_true",
        help="whether the model supports flash attention inference",
    )
    argParser.add_argument(
        "-d",
        "--device",
        default="cuda:0" if torch.cuda.is_available() else "cpu",
        help="device ID, -1 for CPU, >=0 for GPU ID",
    )
    args = argParser.parse_args()
    if args.device:
        DEVICE = args.device

    statements = json.loads(open(TEMPLATE_PATH, "r", encoding="utf-8").read())

    if args.model:
        model_info = {
            "organization": args.model[: args.model.find("/")],
            "name": args.model[args.model.find("/") + 1 :],
            "flash_attn": args.flash_attn,
        }
        model, tokenizer = load_model_and_tokenizer(model_info)
        responses = generate_responses(tokenizer, model, statements)
        for statement, response in zip(statements, responses):
            statement["response"] = response
        save_responses(model_info["name"], statements)
    else:
        models = json.loads(open(MODELS_PATH, "r", encoding="utf-8").read())
        model_pbar = tqdm(models)
        for model_info in model_pbar:
            model_pbar.set_description(f"Loading model: {model_info['name']}")
            tokenizer, model = load_model_and_tokenizer(model_info)
            model_pbar.set_description(f"Loading model: {model_info['name']}")
            for _ in tqdm(range(RESPONSE_REPEAT), desc="Iterating generations"):
                responses = generate_responses(tokenizer, model, statements)

                for statement, response in zip(statements, responses):
                    statement["response"] = response
                save_responses(model_info["name"], statements)
