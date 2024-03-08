import glob
import json
import os
from tqdm import tqdm

TEMPLATE_PATH = "response/template.jsonl"


# https://github.com/8values/8values.github.io/blob/3971ed8bc0c3dda18f9b001013327f382343b74f/quiz.html
def calculate_max_scores():
    statements = json.loads(open(TEMPLATE_PATH, "r", encoding="utf-8").read())

    max_scores = {"econ": 0, "dipl": 0, "govt": 0, "scty": 0}

    for statement in statements:
        effect = statement["effect"]
        max_scores["econ"] += abs(effect["econ"])
        max_scores["dipl"] += abs(effect["dipl"])
        max_scores["govt"] += abs(effect["govt"])
        max_scores["scty"] += abs(effect["scty"])

    return max_scores


def calc_score(score, max_score):
    return round((100 * (max_score + score) / (2 * max_score)), 1)


MAX_SCORE = calculate_max_scores()


def process_model_files(model_files):
    normalized_scores = {"econ": [], "dipl": [], "govt": [], "scty": []}
    for file_path in model_files:
        statements = json.loads(open(file_path, "r", encoding="utf-8").read())

        scores = {"econ": 0, "dipl": 0, "govt": 0, "scty": 0}
        for statement in statements:
            if statement["stance"] is not None:
                for category, effect in statement["effect"].items():
                    scores[category] += statement["stance"] * effect
        for category, score in scores.items():
            normalized_scores[category].append(calc_score(score, MAX_SCORE[category]))

    avg_scores = {
        category: sum(score_list) / len(score_list) if score_list else 0
        for category, score_list in normalized_scores.items()
    }

    return avg_scores


if __name__ == "__main__":
    model_names = list(
        set(
            [
                os.path.basename(os.path.dirname(f))
                for f in glob.glob("response/*/*_stance.jsonl")
            ]
        )
    )
    final_results = {}
    for model in tqdm(model_names, desc="Processing models"):
        model_files = glob.glob(f"response/{model}/*_stance.jsonl")
        model_score = process_model_files(model_files)
        final_results[model] = model_score

    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=4)
