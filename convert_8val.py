import json
from tqdm import tqdm

input_file_path = 'response/8value_js.jsonl'
output_file_path = 'response/template.jsonl'

transformed_data = []

if __name__ == "__main__":
    statement_file = json.loads(open(input_file_path, "r").read())

    for i in tqdm(range(len(statement_file))):
        transformed_entry = {
            "id": i,
            "statement": statement_file[i]["question"],
            "response": "",
            "effect": statement_file[i]["effect"],
            "stance": ""
        }
        transformed_data.append(transformed_entry)

    with open(output_file_path, 'w') as output_file:
        json_data = json.dumps(transformed_data, indent=4)
        output_file.write(json_data)
