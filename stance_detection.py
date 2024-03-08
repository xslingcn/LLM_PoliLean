import glob
import json
import os
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv
from api import gemini, mistral, openai, claude

load_dotenv()

PROMPT = os.getenv("STANCE_PROMPT")

TEMPLATE_PATH = "response/template.jsonl"


def prepare_input(statements):
    extracted = []
    for line in statements:
        extracted_obj = {
            "id": line["id"],
            "statement": line["statement"],
            "response": line["response"],
        }
        extracted.append(extracted_obj)
    return extracted


def update_stance(statements, stances):
    for item in statements:
        item_id = str(item["id"])
        if item_id in stances:
            item["stance"] = stances[item_id]
    return statements


if __name__ == "__main__":
    # jsonl_files = glob.glob("response/*/*.jsonl")
    jsonl_files = glob.glob("response/gemini-pro/*.jsonl")

    for file_path in tqdm(jsonl_files, desc="Detecting stances"):
        statements = json.loads(open(file_path, "r", encoding="utf-8").read())

        query = prepare_input(statements)
        stances = openai.stance_detection(query)
        updated_statements = update_stance(statements, stances)

        new_file_path = file_path.replace(".jsonl", "_stance.jsonl")
        with open(new_file_path, "w", encoding="utf-8") as f:
            json.dump(updated_statements, f, indent=4)
