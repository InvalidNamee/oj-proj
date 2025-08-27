import os

JWT_SECRET_KEY = "your-secretkey"
# 这里是数据的相关配置
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "Pswd^123"
DATABASE = "ojproj"
SQLALCHEMY_DATABASE_URI = (f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4")

# 这里是判题机
JUDGE_SERVER = "http://127.0.0.1:8000"  # 判题机地址
PUBLIC_BASE_URL = "http://127.0.0.1:5000/api"

# JUDGE_SERVER = "http://121.249.151.214:8000"  # 判题机地址
# PUBLIC_BASE_URL = "http://172.24.61.145:5001/api"
CALLBACK_SECRET = os.getenv("JUDGE_CALLBACK_SECRET", "change-me")

# 这里是 openai
OPENAI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_BASE_URL = "https://gemini.invalidnamee.dpdns.org"
OPENAI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
GEN_PROBLEM_PROMPT = """
You are an online judge problem generator. 
Generate a programming problem strictly in JSON format.

Requirements:
1. Output only valid JSON, no extra text.
2. The JSON must follow this schema:
{
  "problem": {
    "limitations": {
      "maxTime": ...(default 1.0),
      "maxMemory": ...(default 256),
    }
    "title": "..."
    "description": "...",
    "input_format": "...",
    "output_format": "...",
    "samples": [
      {
        "id": 1,
        "input": "...",
        "output": ",,,",
      }
      ...
    ]
    "notes": "..."
  },
  "test_cases": [
    {"id": 1, "input": "...", "output": "..."},
    {"id": 2, "input": "...", "output": "..."},
    {"id": 3, "input": "...", "output": "..."}
  ],
  "reference_solution": {
    "language": "python",
    "code": "def main():\\n    ...\\n"
  }
}

3. Test cases must cover basic, edge, and large inputs.
4. Each individual test case input and output must be small (do not exceed a few lines of text).
5. All inputs and outputs must be plain text (no binary or special encodings, test_cases like " ".join(["-1000" for _ in range(1000)] are not allowed).
6. The reference_solution must be correct and solve the problem.
"""
