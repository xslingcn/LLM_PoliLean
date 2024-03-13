# LLM PoliLean
This tool is designed to facilitate the easy testing of Large Language Models for political leanings. The provided questionnaire and score computing is integrated with [8 Values](https://github.com/8values/8values.github.io). It supports both local inference models and API-based commercial models.

## Usage
### 1. Prepare Environment

A conda environment file is provided and can be used via:
```bash
conda env create -f environment.yml
conda activate polilean
```
This will create and activate a virtual environment called `polilean`, which includes all needed packages.

### 2. Configuration

The `.env` file contains several configuration options. Copy the example file to `.env` and edit the items.
```bash
cp .env.example .env
```
- `TEMPLATE_PATH`: The path of the questionnaire template. Deafult: `response/template.jsonl`
- `RESPONSE_REPEAT`: The number of times to repeat the generation for each model. Default: `5`
- `RESPONSE_MAX_NEW_TOKENS`: The maximum number of new tokens to generate. Default: `100`
- `RESPONSE_PROMPT`: The prompt template used for generating responses to political statements. Default: `"Please respond to the following statement: <statement>\nYour response:"`
> Note: LMs are highly sensitive to prompts, so changing the prompt template may greatly vary the test results.

API endpoints and keys for various LLM platforms:

- `OPENAI_ENDPOINT`: The API endpoint for OpenAI's completion service. Default: `https://api.openai.com/v1/chat/completions`
- `OPENAI_API_KEY`: The API key for OpenAI.
- `MISTRAL_ENDPOINT`: The API endpoint for Mistral's chat completion service. Default: `https://api.mistral.ai/v1/chat/completions`
- `MISTRAL_API_KEY`: The API key for Mistral
- `GEMINI_ENDPOINT`: The API endpoint for Google's Gemini model. Default: `https://generativelanguage.googleapis.com/v1beta`
- `GEMINI_API_KEY`: The API key for Google Cloud.
- `CLAUDE_ENDPOINT`: The API endpoint for Anthropic's Claude model. Default: `https://api.anthropic.com/v1/messages`
- `CLAUDE_API_KEY`: The API key for Claude.

Remember to replace the placeholders with your actual API keys and adjust the number of repeats or token limits as needed for your testing environment.

### 3. Generate Response (Inference)

`response_inference.py` allows you to test models via local inference. It loads model via [Hugging Face Transformers](https://huggingface.co/docs/transformers/v4.38.2/en/llm_tutorial). Here's how you can run the script:
```bash
python response_inference.py --model <model_name> [--flash-attn] [--device <device_id>]
```
- `-m`, `--model`: Specify the model you want to use from HuggingFace. This should be the full identifier of the model on HuggingFace's Model Hub, e.g., `google/gemma-2b-it`.
- `-f`, `--flash-attn`: If your model supports flash attention inference, include this flag to enable it.
- `-d`, `--device`: Choose the device for running the inference. Use -1 for CPU or specify a GPU ID (e.g., 0 for cuda:0). By default, it will use a GPU if available.

#### Configuring Models for Batch Testing
If no argument is given, the script automatically loads `models.jsonl` and run the batch testing. Each object in the file represents a model configuration in JSON format, with the following fields:

- `organization`: The organization or user name on HuggingFace hosting the model, e.g., `google`.
- `name`: The specific model checkpoint (name) you wish to use, e.g., `gemma-2b-it`.
- `flash_attn`: A boolean indicating whether the model supports flash attention inference acceleration.
Example entry in models.jsonl:
```json
{
    "organization": "meta-llama",
    "name": "Llama-2-7b-chat-hf",
    "flash_attn": true
}
```
> If you're unsure whether your model supports flash attention inference, check [here](https://github.com/huggingface/text-generation-inference/tree/main/server/text_generation_server/models).

### 4. Generate Response (API)
`response_api.py` enables testing models through API requests, this enables testing for commercial models like `Claude-3`. Make sure you have configured the API key for corresponding platform, then you can execute the script by:
```bash
python response_api.py --platform <platform_name> [--model <model_name>]
```
- `-p`, `--platform`: Specify the platform to test. This script supports a variety of platforms, each hosting different models. Available platforms and their respective models include:
    - `openai`: `gpt-3.5-turbo-0125`, `gpt-4-0125-preview`
    - `mistral`: `mistral-small-2402`, `mistral-medium-2312`, `mistral-large-2402`
    - `gemini`: `gemini-pro`
    - `claude`: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- `-m`, `--model`: Specify the language model of interest on the chosen platform. If not specified, all available models will be tested.

If no argument is given, the script will automatically iterate over all coded platforms and available models.
> For the above platforms, if future new models are introduced, you can test them with the `-m` argument even they're not included in the list. (as long as the API protocol is not breakingly changed)

### 5. Stance Detection
This step you'll use `GPT-4` to determine whether the response agree or disagree with the statement. You can use the script by:
```bash
python stance_detection.py [--directory <directory_name>] [--suffix <file_suffix>]
```
- `-d`, `--directory`: This allows you to specify which subdirectory within the `response` folder containing the targeting response `.jsonl` files for stance detection. This should be a model name if they're generated by previous steps. If not specified, all `.jsonl` files under the `response` folder will be tested.

    Example usage:
    ```bash
    python stance_detection.py --directory Llama-2-7b-chat-hf
    ```
- `-s`, `--suffix`: Use this parameter to define a suffix for the name of the new combined file created after processing. If not specified, the original files will be directly replaced. This is useful for keeping the original files unchanged while saving the processed results in a new file.
    Example usage:
    ```bash
    python stance_detection.py --suffix _stance
    ```

### 6. Compute Score
The `compute_score.py` is used for processing .jsonl files to compute and aggregate scores:
```bash
python compute_score.py [--suffix <file_suffix>] [--json] [--csv]
```
- `-s`, `--suffix`: Specifies the suffix of the file names to be processed. If not specified, all .jsonl files under the `response` directory will be processed. E.g., `_stance`.
- `-j`, `--json`: Enables saving the computed scores and results to a JSON file. 
- `-c`, `--csv`: Enables saving the computed scores and results to a CSV file. 
> If neither `--json` nor `--csv` is specified, the results will default to being saved in a JSON file at `results/scores.jsonl`.

## License
This project is open-sourced under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) License. Feel free to use, modify, and distribute it as you see fit.