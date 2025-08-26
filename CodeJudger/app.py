from flask import Flask, request, jsonify
from redis import Redis
import requests, json
from datetime import datetime
from config import REDIS_URL, QUEUE_KEY, SUB_HASH_PREFIX
import uuid

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


@app.post("/judger/self_test")
def self_test():
    print("wahaha")
    data = request.get_json(silent=True) or {}
    language = data.get("language")
    source_code = data.get("source_code")
    test_cases = data.get("test_cases")
    limitations = data.get("limitations") or {}
    callback_url = data.get("callback_url")
    callback_token = data.get("callback_token")

    if not language or not source_code or not test_cases:
        return jsonify({"error": "missing language / source_code / test_cases"}), 400

    submission_id = f"selftest_{uuid.uuid4().hex}"
    
    job = {
        "submission_id": submission_id,
        "language": language,
        "source_code": source_code,
        "limitations": limitations,
        "test_cases": test_cases,
        "callback_url": callback_url,
        "callback_token": callback_token,
        "created_at": datetime.now().isoformat()
    }
    
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

@app.get("/judger/self_test/<submission_id>")
def self_test_status(submission_id):
    """
    查询自测提交状态
    """
    sub_key = SUB_HASH_PREFIX + submission_id
    if not rds.exists(sub_key):
        return jsonify({"error": "submission not found"}), 404

    status = rds.hgetall(sub_key)
    # Redis 中可能存的是字符串，解析必要字段
    result = status.get("result")
    score = status.get("score")
    job_status = status.get("status")
    created_at = status.get("created_at")

    return jsonify({
        "submission_id": submission_id,
        "status": job_status,
        "score": float(score) if score else None,
        "result": json.loads(result) if result else None,
        "created_at": created_at
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
