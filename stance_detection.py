import glob
import json
import os
import argparse
from tqdm import tqdm
from dotenv import load_dotenv
from api import openai

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
    argParser = argparse.ArgumentParser(description="Stance detection with GPT-4.")
    argParser.add_argument(
        "-d",
        "--directory",
        choices=[
            os.path.basename(os.path.normpath(folder))
            for folder in glob.glob("response/*/")
        ],
        help="the directory containing the targeting response files. If not specified, all `.jsonl` files under `response` folder will be tested.",
    )
    argParser.add_argument(
        "-s",
        "--suffix",
        default="",
        help="the file name suffix of the new combined file. If not specified, the original file will be directly replaced.",
    )
    args = argParser.parse_args()
    directory = args.directory
    suffix = args.suffix

    if directory:
        jsonl_files = glob.glob(f"response/{directory}/*.jsonl")
    else:
        jsonl_files = glob.glob("response/*/*.jsonl")

    for file_path in tqdm(jsonl_files, desc="Detecting stances"):
        statements = json.loads(open(file_path, "r", encoding="utf-8").read())

        query = prepare_input(statements)
        stances = openai.stance_detection(query)
        updated_statements = update_stance(statements, stances)

        new_file_path = file_path.replace(".jsonl", f"{suffix}.jsonl")
        with open(new_file_path, "w", encoding="utf-8") as f:
            json.dump(updated_statements, f, indent=4)
