# judge_worker_async.py
import os
import json
import redis
import requests
from judge import judge_submission
from config import REDIS_URL, QUEUE_KEY, WORKER_PROCESSES, BOX_ID_START

def worker_loop(worker_idx: int):
    box_id = (BOX_ID_START + worker_idx) % 1000
    rds = redis.from_url(REDIS_URL, decode_responses=True)

    print(f"[Worker {worker_idx}] start, box_id={box_id}")
    while True:
        # 阻塞等待任务
        _, raw = rds.blpop(QUEUE_KEY)
        task = json.loads(raw)

        submission_id = task["submission_id"]
        problem_id = task["problem_id"]
        source_code = task["source_code"]
        language = task["language"]
        limitations = task.get("limitations", {})

        print(f"[Worker {worker_idx}] Judging submission {submission_id}")
        
        callback_payload = {
            "status": "Judging",
            "score": 0,
            "detail": [],
            "finished_at": None,
            "callback_token": task.get("callback_token")
        }
        # 回调 Web
        try:
            resp = requests.put(task["callback_url"], json=callback_payload, timeout=10)
            resp.raise_for_status()
            print(f"[Worker {worker_idx}] Submission {submission_id} updated successfully")
        except Exception as e:
            print(f"[Worker {worker_idx}] Failed to update submission {submission_id}: {e}")

        try:
            result = judge_submission(
                box_id=box_id,
                problem_id=problem_id,
                language=language,
                source_code=source_code,
                limitations=limitations
            )
        except Exception as e:
            result = {
                "status": "IE",
                "score": 0,
                "cases": [],
                "finished_at": "",
                "extra": str(e)
            }

        # 组装回调数据
        callback_payload = {
            "status": result.get("status", "error"),
            "score": result.get("score", 0),
            "max_time": result.get("max_time", 0),
            "max_memory": result.get("max_memory", 0),
            "detail": result.get("cases", []),
            "finished_at": result.get("finished_at"),
            "callback_token": task.get("callback_token")  # 如果需要鉴权
        }

        # 回调 Web
        try:
            resp = requests.put(task["callback_url"], json=callback_payload, timeout=10)
            resp.raise_for_status()
            print(f"[Worker {worker_idx}] Submission {submission_id} updated successfully")
        except Exception as e:
            print(f"[Worker {worker_idx}] Failed to update submission {submission_id}: {e}")


def main():
    import multiprocessing as mp

    procs = []
    for i in range(WORKER_PROCESSES):
        p = mp.Process(target=worker_loop, args=(i,), daemon=True)
        p.start()
        procs.append(p)

    for p in procs:
        p.join()


if __name__ == "__main__":
    main()
