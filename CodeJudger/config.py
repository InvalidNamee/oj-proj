import os

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_KEY = os.getenv("QUEUE_KEY", "judge:queue")
SUB_HASH_PREFIX = os.getenv("SUB_HASH_PREFIX", "judge:sub:")  # 状态存储 hash 前缀

# 并发
WORKER_PROCESSES = int(os.getenv("WORKER_PROCESSES", "4"))   # worker 进程数
BOX_ID_START = int(os.getenv("BOX_ID_START", "100"))         # isolate box-id 起始（避免冲突）
# 注意：同一台机所有进程的 box-id 必须唯一，且在 0..999 范围内

# 判题限制（可在题目 limitations 里覆盖）
DEFAULT_TIME_LIMIT = float(os.getenv("DEFAULT_TIME_LIMIT", "2.0"))    # seconds
DEFAULT_MEM_LIMIT_MB = int(os.getenv("DEFAULT_MEM_LIMIT_MB", "256"))  # MB
DEFAULT_OUTPUT_LIMIT_KB = int(os.getenv("DEFAULT_OUTPUT_LIMIT_KB", "4096"))  # isolate write-fs 上限

# 题目数据目录
PROJECT_ROOT = os.path.dirname(os.getcwd())
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
