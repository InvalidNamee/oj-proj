from flask import Flask, request, jsonify
from redis import Redis
import requests, json
from datetime import datetime
from config import REDIS_URL, QUEUE_KEY, SUB_HASH_PREFIX

app = Flask(__name__)
rds = Redis.from_url(REDIS_URL, decode_responses=True)


@app.post("/judger/<submission_id>")
def create_submission(submission_id):
    """
    提交代码（异步）
    body JSON:
      problem_id: int
      language: "python" | "cpp"
      source_code: string
      limitations?: { maxTime, maxMemory(MB), maxOutput(KB) }
      callback_url?: string
      callback_token?: string
    return:
      { submission_id }
    """
    data = request.get_json(silent=True) or {}
    problem_id = data.get("problem_id")
    language = data.get("language")
    source_code = data.get("source_code")
    limitations = data.get("limitations") or {}
    callback_url = data.get("callback_url")
    callback_token = data.get("callback_token")

    if not problem_id or not language or not source_code:
        return jsonify({"error": "missing problem_id / language / source_code"}), 400

    job = {
        "submission_id": submission_id,
        "problem_id": int(problem_id),
        "language": language,
        "source_code": source_code,
        "limitations": limitations,
        "callback_url": callback_url,
        "callback_token": callback_token,
        "created_at": datetime.now().isoformat()
    }

    # 初始状态
    sub_key = SUB_HASH_PREFIX + submission_id
    rds.hset(sub_key, mapping={
        "status": "queued",
        "result": "",
        "score": "0",
        "created_at": job["created_at"]
    })
    # 入队
    rds.rpush(QUEUE_KEY, json.dumps(job))
    return jsonify({"submission_id": submission_id}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
