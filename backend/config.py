import  os

JWT_SECRET_KEY = "your-secretkey"
# 这里是数据的相关配置
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "Pswd^123"
DATABASE = "ojproj"
SQLALCHEMY_DATABASE_URI = (f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4")

# 这里是判题机
# JUDGE_SERVER = "http://127.0.0.1:8000"  # 判题机地址
# PUBLIC_BASE_URL = "http://127.0.0.1:5000/api"

JUDGE_SERVER = "http://121.249.151.214:8000"  # 判题机地址
PUBLIC_BASE_URL = "http://172.24.61.145:5001/api"
CALLBACK_SECRET = os.getenv("JUDGE_CALLBACK_SECRET", "change-me")

# 这里是 openai
OPENAI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_BASE_URL = "https://gemini.invalidnamee.dpdns.org"
GEN_PROBLEM_PROMPT = """
You are an online judge problem generator. 
Generate a programming problem strictly in JSON format.

⚠️ Requirements:
1. Output only valid JSON, no extra text.
2. The JSON must follow this schema:
{
  "problem": {
    "limitations": {
      "maxTime": ...(default 1.0),
      "maxMemory": ...(default 256),
    }
    "description": "...",
    "input_format": "...",
    "output_format": "...",
    "sample_input": "...",
    "sample_output": "...",
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
4. The reference_solution must be correct and solve the problem.
"""
