from flask import Blueprint, request, jsonify
from decorators import role_required, ROLE_TEACHER
from config import OPENAI_API_KEY, GEN_PROBLEM_PROMPT, OPENAI_BASE_URL, OPENAI_MODELS
import re
from openai import OpenAI
import json

bp = Blueprint("gemini", __name__, url_prefix="/api/gemini")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

def clean_json_output(text: str) -> str:
    """
    Remove markdown code fences (``` or ```json).
    """
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)
    return text.strip()


def generate_problem_from_llm(user_request: str, model: str="gemini-2.5-flash-lite"):
    messages = [
        {"role": "system", "content": GEN_PROBLEM_PROMPT},
        {"role": "user", "content": f"User request: {user_request}"}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )
    raw_output = response.choices[0].message.content
    print(raw_output)
    cleaned = clean_json_output(raw_output)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(f"Model output is not valid JSON:\n{cleaned}")


@bp.post("/generate_problem")
@role_required(ROLE_TEACHER)
def generate_problem():
    data = request.get_json()
    user_request = data.get("prompt")
    model = data.get("model") or "gemini-2.5-flash-lite"
    if not user_request:
        return jsonify({"error": "Missing 'prompt'"}), 400
    
    if model not in OPENAI_MODELS:
        return jsonify({"error": "Invalid model name"}), 400

    try:
        result = generate_problem_from_llm(user_request)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
