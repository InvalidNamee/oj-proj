from flask import Flask, request, jsonify
from redis import Redis
import uuid
import json
from datetime import datetime
from config import REDIS_URL, QUEUE_KEY, SUB_HASH_PREFIX

app = Flask(__name__)
rds = Redis.from_url(REDIS_URL, decode_responses=True)

@app.post("/submissions")
def create_submission():
    """
    提交代码（异步）
    body JSON:
      problem_id: int
      language: "python" | "cpp"
      source_code: string
      limitations?: { maxTime, maxMemory(MB), maxOutput(KB) }
    return:
      { submission_id }
    """
    data = request.get_json(silent=True) or {}
    problem_id = data.get("problem_id")
    language = data.get("language")
    source_code = data.get("source_code")
    limitations = data.get("limitations") or {}

    if not problem_id or not language or not source_code:
        return jsonify({"error": "missing problem_id / language / source_code"}), 400

    submission_id = str(uuid.uuid4())
    job = {
        "submission_id": submission_id,
        "problem_id": int(problem_id),
        "language": language,
        "source_code": source_code,
        "limitations": limitations,
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


@app.get("/submissions/<submission_id>")
def get_submission(submission_id):
    """
    查询提交状态
    """
    sub_key = SUB_HASH_PREFIX + submission_id
    if not rds.exists(sub_key):
        return jsonify({"error": "submission not found"}), 404

    data = rds.hgetall(sub_key)
    # 尝试把 result 从 JSON 还原
    result = data.get("result")
    try:
        result = json.loads(result) if result else None
    except Exception:
        pass

    return jsonify({
        "submission_id": submission_id,
        "status": data.get("status"),
        "score": float(data.get("score", "0")),
        "result": result,
        "created_at": data.get("created_at"),
        "finished_at": data.get("finished_at")
    }), 200


if __name__ == "__main__":
    # 仅测试用途：生产建议走 WSGI（gunicorn/uwsgi 等）
    app.run(host="0.0.0.0", port=8000, debug=True)
