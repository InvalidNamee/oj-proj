import os, json, time, hmac, base64, hashlib, threading, requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt
from exts import db
from models import LegacyProblemModel, CodingProblemModel, ProblemSetModel, SubmissionModel
from decorators import role_required, ROLE_TEACHER
from modules.legacy_judger import legacy_judger

bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')

@bp.post('/legacy/<int:problem_id>')
@role_required()
def submit_legacy(problem_id):
    """
    提交 Legacy 题目答案并判分
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    problem_set_id = data.get('problem_set_id')
    user_answers = data.get('user_answers')

    if not problem_id or user_answers is None:
        return jsonify({'error': 'Missing problem_id or user_answers'}), 400

    problem = LegacyProblemModel.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    # 判题
    score, status = legacy_judger(problem.problem_type, problem.answers, user_answers)

    # 保存提交
    submission = SubmissionModel(
        user_id=user_id,
        problem_set_id=problem_set_id,
        problem_id=problem_id,
        problem_type='legacy',
        user_answer=user_answers,
        score=score, # type: ignore
        status=status # pyright: ignore[reportCallIssue]
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'problem_id': problem_id,
        'problem_set_id': problem_set_id,
        'score': score,
        'status': status
    }), 201


JUDGE_SERVER = "http://127.0.0.1:8000"  # 判题机地址
PUBLIC_BASE_URL = "http://127.0.0.1:5000/api"
CALLBACK_SECRET = os.getenv("JUDGE_CALLBACK_SECRET", "change-me")

def _make_callback_token(submission_id: int, ttl_sec: int = 3600) -> str:
    ts = str(int(time.time()))
    payload = f"{submission_id}.{ts}"
    sig = hmac.new(CALLBACK_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    return f"{payload}.{base64.urlsafe_b64encode(sig).decode()}"

def _verify_callback_token(token: str, submission_id: int, max_age_sec: int = 3600) -> bool:
    try:
        sid, ts, sig_b64 = token.split(".")
        if sid != str(submission_id):
            return False
        if int(time.time()) - int(ts) > max_age_sec:
            return False
        expected = hmac.new(CALLBACK_SECRET.encode(), f"{sid}.{ts}".encode(), hashlib.sha256).digest()
        return hmac.compare_digest(expected, base64.urlsafe_b64decode(sig_b64.encode()))
    except Exception:
        return False

def _fire_and_forget_enqueue(url: str, payload: dict, timeout_sec: float = 3.0):
    def _send():
        try:
            requests.post(url, json=payload, timeout=timeout_sec)
        except Exception:
            # 这里可以写入日志或将任务放入重试队列
            pass
    threading.Thread(target=_send, daemon=True).start()


@bp.post("/coding/<int:problem_id>")
@role_required()
def submit_coding(problem_id):
    """
    1) 先入库一条 submission（queued）并立即返回 submission_id
    2) 后台异步把任务发给判题机
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    language = data.get("language")
    source_code = data.get("source_code")
    problem_set_id = data.get("problem_set_id")
    # client_limitations = data.get("limitations")  # 可选，覆盖题目默认限制

    if not language or not source_code:
        return jsonify({"error": "Missing language or source_code"}), 400

    problem = CodingProblemModel.query.get(problem_id)
    if not problem:
        return jsonify({"error": "Problem not found"}), 404

    # 取限制：客户端>题目默认
    effective_limits = problem.limitations or {}
    # if isinstance(client_limitations, dict):
    #     effective_limits.update(client_limitations)

    # 1) 入库
    submission = SubmissionModel(
        user_id=user_id,
        problem_set_id=problem_set_id,
        problem_id=problem_id,
        problem_type="coding",
        user_answer=source_code,
        score=0,
        status="Pending",
    )
    db.session.add(submission)
    db.session.commit()

    # 2) 异步通知判题机
    callback_url = f"{PUBLIC_BASE_URL}/submissions/{submission.id}"
    callback_token = _make_callback_token(submission.id)

    judge_payload = {
        "problem_id": problem_id,
        # 判题机应当自带该题目的测试数据；如果放 DB/对象存储，这里也可附 test_cases 描述
        "language": language,
        "source_code": source_code,
        "limitations": effective_limits,
        "callback_url": callback_url,
        "callback_token": callback_token
    }
    _fire_and_forget_enqueue(f"{JUDGE_SERVER}/judger/{submission.id}", judge_payload, timeout_sec=3.0)

    # 立刻返回，前端可以开始轮询 /coding/submissions/<id>
    return jsonify({
        "submission_id": submission.id,
        "status": submission.status
    }), 201


@bp.get("/<int:submission_id>")
@role_required()
def get_submission(submission_id):
    """
    提供给前端轮询查看当前判题进度/结果
    """
    s = SubmissionModel.query.get_or_404(submission_id)
    return jsonify({
        "submission_id": s.id,
        "problem_id": s.problem_id,
        "problem_set_id": s.problem_set_id,
        "status": s.status,
        "score": s.score,
        "extra": s.extra
    }), 200


@bp.put("/<int:submission_id>")
def judge_callback(submission_id):
    """
    判题机回调：更新 submission 状态/分数/详情
    - 判题机可多次回调：compiling/running -> 最终态（accepted/rejected/CE/RE/TLE/MLE）
    - 通过 callback_token 鉴权
    """
    data = request.get_json() or {}
    token = data.get("callback_token") or request.headers.get("X-Judge-Signature")

    if not token or not _verify_callback_token(token, submission_id):
        return jsonify({"error": "invalid callback token"}), 401

    s = SubmissionModel.query.get_or_404(submission_id)

    # 允许局部更新
    new_status = data.get("status")            # e.g., "running", "compile_error", "accepted", ...
    new_score = data.get("score")              # 0~100
    detail = data.get("detail")                # 字典：编译日志、样例结果、时间内存……
    finished_at = data.get("finished_at")      # 可选，ISO 时间串

    if new_status:
        s.status = new_status
    if isinstance(new_score, (int, float)):
        s.score = float(new_score)
    if detail is not None:
        # 建议把 detail 存成 JSON 字符串
        try:
            s.extra = detail
        except Exception:
            s.extra = str(detail)

    db.session.commit()
    return jsonify({"ok": True})