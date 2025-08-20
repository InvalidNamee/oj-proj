import os
import json
import signal
import multiprocessing as mp
from redis import Redis
from config import REDIS_URL, QUEUE_KEY, SUB_HASH_PREFIX, WORKER_PROCESSES, BOX_ID_START
from judge import judge_submission

def worker_loop(worker_idx: int):
    """
    每个 worker 绑定一个独立 box-id
    """
    box_id = (BOX_ID_START + worker_idx) % 1000  # ensure 0..999
    rds = Redis.from_url(REDIS_URL, decode_responses=True)

    print(f"[worker {worker_idx}] start, box-id={box_id}")
    while True:
        _, job_json = rds.blpop(QUEUE_KEY)  # 阻塞等待
        job = json.loads(job_json)

        sub_id = job["submission_id"]
        sub_key = SUB_HASH_PREFIX + sub_id
        try:
            rds.hset(sub_key, mapping={"status": "running"})

            result = judge_submission(
                box_id=box_id,
                problem_id=job["problem_id"],
                language=job["language"],
                source_code=job["source_code"],
                limitations=job.get("limitations") or {}
            )

            rds.hset(sub_key, mapping={
                "status": result["status"],
                "score": str(result.get("score", 0)),
                "result": json.dumps(result, ensure_ascii=False),
                "finished_at": result.get("finished_at", "")
            })
        except Exception as e:
            rds.hset(sub_key, mapping={
                "status": "system_error",
                "score": "0",
                "result": json.dumps({"message": str(e)}, ensure_ascii=False)
            })

def main():
    procs = []
    # 优雅退出
    def shutdown(signum, frame):
        for p in procs:
            if p.is_alive():
                p.terminate()
        for p in procs:
            p.join()
        print("workers stopped")
        os._exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    for i in range(WORKER_PROCESSES):
        p = mp.Process(target=worker_loop, args=(i,), daemon=True)
        p.start()
        procs.append(p)

    # 主进程等待
    for p in procs:
        p.join()

if __name__ == "__main__":
    main()
