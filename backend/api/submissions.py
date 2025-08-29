import time, hmac, base64, hashlib, threading, requests
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, get_jwt
from exts import db
from models import ProblemModel, SubmissionModel, UserModel, ProblemSetModel
from decorators import role_required, ROLE_TEACHER
from modules.verify import can_submit

bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')

def _make_callback_token(submission_id: int, ttl_sec: int = 3600) -> str:
    ts = str(int(time.time()))
    payload = f"{submission_id}.{ts}"
    sig = hmac.new(current_app.config["CALLBACK_SECRET"].encode(), payload.encode(), hashlib.sha256).digest()
    return f"{payload}.{base64.urlsafe_b64encode(sig).decode()}"

def _verify_callback_token(token: str, submission_id: int, max_age_sec: int = 3600) -> bool:
    try:
        sid, ts, sig_b64 = token.split(".")
        if sid != str(submission_id):
            return False
        if int(time.time()) - int(ts) > max_age_sec:
            return False
        expected = hmac.new(current_app.config["CALLBACK_SECRET"].encode(), f"{sid}.{ts}".encode(), hashlib.sha256).digest()
        return hmac.compare_digest(expected, base64.urlsafe_b64decode(sig_b64.encode()))
    except Exception:
        return False

def _fire_and_forget_enqueue(url: str, payload: dict, timeout_sec: float = 3.0):
    def _send():
        try:
            requests.post(url, json=payload, timeout=timeout_sec)
        except Exception:
            pass
    threading.Thread(target=_send, daemon=True).start()

def submit_legacy(problem, data: dict):
    """
    提交传统题（单选、多选、填空、主观题）
    请求 JSON: { "user_answer": ... }
    返回: { "status": "AC/WA", "score": float }
    """
    user_id = get_jwt_identity()
    user_answer = data.get("user_answer")
    problem_set_id = data.get("problem_set_id")

    correct = problem.test_cases.get("answers", None)
    problem_type = problem.type

    score = 0
    status = "WA"

    if problem_type == "single":
        if user_answer == correct:
            score = 100
            status = "AC"
    elif problem_type == "multiple":
        # 多选要求集合完全匹配
        if isinstance(user_answer, list) and set(user_answer) == set(correct):
            score = 100
            status = "AC"
    elif problem_type == "fill":
        if isinstance(user_answer, list) and user_answer == correct:
            score = 100
            status = "AC"
    elif problem_type == "subjective":
        score = 100
        status = "AC"
    else:
        return jsonify({"error": "Unsupported problem type"}), 400

    # 写入提交记录
    submission = SubmissionModel(
        user_id=user_id,
        problem_id=problem.id,
        problem_set_id=problem_set_id,
        problem_type=problem_type,
        user_answer=user_answer,
        score=score,
        status=status,
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        "submission_id": submission.id,
        "status": submission.status,
        "score": submission.score,
    }), 201


def submit_coding(problem, data: dict):
    """
    1) 先入库一条 submission（queued）并立即返回 submission_id
    2) 后台异步把任务发给判题机
    """
    user_id = get_jwt_identity()

    language = data.get("language")
    source_code = data.get("source_code")
    problem_set_id = data.get("problem_set_id")

    if not language or not source_code:
        return jsonify({"error": "Missing language or source_code"}), 400

    problem = ProblemModel.query.get(problem.id)
    if not problem:
        return jsonify({"error": "Problem not found"}), 404

    # 1) 入库
    submission = SubmissionModel(
        user_id=user_id,
        problem_set_id=problem_set_id,
        problem_id=problem.id,
        problem_type="coding",
        user_answer=source_code,
        language=language,
        score=0,
        status="Pending",
    )
    db.session.add(submission)
    db.session.commit()

    # 2) 异步通知判题机
    callback_url = f"{current_app.config['PUBLIC_BASE_URL']}/submissions/{submission.id}"
    callback_token = _make_callback_token(submission.id)

    judge_payload = {
        "problem_id": problem.id,
        "language": language,
        "source_code": source_code,
        "limitations": problem.limitations,
        "callback_url": callback_url,
        "callback_token": callback_token
    }
    _fire_and_forget_enqueue(f"{current_app.config['JUDGE_SERVER']}/judger/{submission.id}", judge_payload, timeout_sec=3.0)

    # 立刻返回，前端可以开始轮询 /coding/submissions/<id>
    return jsonify({
        "submission_id": submission.id,
        "status": submission.status,
        "score": submission.score,
    }), 201


@bp.post('/self_check')
@role_required()
def self_check():
    data = request.get_json()
    language = data.get('language')
    source_code = data.get('source_code')
    test_cases = data.get('test_cases')
    limitations = data.get('limitations', {})

    if not language or not source_code or not test_cases:
        return jsonify({"error": "missing language / source_code / test_cases"}), 400

    submission_id = None

    # 转发给判题机
    try:
        resp = requests.post(
            f"{current_app.config['JUDGE_SERVER']}/judger/self_test",
            json={
                "language": language,
                "source_code": source_code,
                "test_cases": test_cases,
                "limitations": limitations,
                "callback_url": None,  # 这里不需要回调
            },
            timeout=5
        )
        if resp.status_code != 202:
            return jsonify({"error": "judger rejected request"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"submission_id": resp.json().get("submission_id")}), 202


@bp.get('/self_check/<submission_id>')
@role_required()
def get_self_check(submission_id):
    resp = requests.get(f"{current_app.config['JUDGE_SERVER']}/judger/self_test/{submission_id}")
    return jsonify(resp.json()), resp.status_code


@bp.post("/<int:problem_id>")
@role_required()
def submit_problem(problem_id):
    user = UserModel.query.get_or_404(get_jwt_identity())
    problem = ProblemModel.query.get_or_404(problem_id)
    data = request.get_json() or {}
    problem_set = None
    if data.get("problem_set_id"):
        problem_set = ProblemSetModel.query.get_or_404(data.get("problem_set_id"))
    if not can_submit(user, problem_set):
        return jsonify({'error': 'Permission denied'}), 403
    if problem.type == "coding":
        return submit_coding(problem, data)
    else:
        return submit_legacy(problem, data)
    
@bp.patch("/<int:submission_id>")
@role_required()
def rejudge(submission_id):
    submission = SubmissionModel.query.get_or_404(submission_id)
    problem = ProblemModel.query.get_or_404(submission.problem_id)
    language = submission.language
    source_code = submission.user_answer
    limitations = problem.limitations

    if not language or not source_code:
        return jsonify({"error": "Missing language or source_code"}), 400

    problem = ProblemModel.query.get_or_404(problem.id)

    # 1) 入库
    submission.status = "Pending"
    submission.score = 0.0
    submission.max_time = None
    submission.max_memeory = None
    submission.extra = None
    db.session.commit()

    # 2) 异步通知判题机
    callback_url = f"{current_app.config['PUBLIC_BASE_URL']}/submissions/{submission.id}"
    callback_token = _make_callback_token(submission.id)

    judge_payload = {
        "problem_id": problem.id,
        "language": language,
        "source_code": source_code,
        "limitations": limitations,
        "callback_url": callback_url,
        "callback_token": callback_token
    }
    _fire_and_forget_enqueue(f"{current_app.config['JUDGE_SERVER']}/judger/{submission.id}", judge_payload, timeout_sec=3.0)

    # 立刻返回，前端可以开始轮询 /coding/submissions/<id>
    return jsonify({
        "submission_id": submission.id,
        "status": submission.status,
        "score": submission.score,
    }), 201
    
@bp.patch("/problem/<int:problem_id>")
@role_required(ROLE_TEACHER)
def rejudge_problem(problem_id):
    """
    重判指定 problem_id 下的所有提交记录
    """
    problem = ProblemModel.query.get_or_404(problem_id)
    submissions = SubmissionModel.query.filter_by(problem_id=problem_id).all()
    for submission in submissions:
        language = submission.language
        source_code = submission.user_answer
        limitations = problem.limitations

        if not language or not source_code:
            continue  # 跳过无效记录

        # 入库
        submission.status = "Pending"
        submission.score = 0.0
        submission.max_time = None
        submission.max_memory = None
        submission.extra = None

        # 异步通知判题机
        callback_url = f"{current_app.config['PUBLIC_BASE_URL']}/submissions/{submission.id}"
        callback_token = _make_callback_token(submission.id)
        judge_payload = {
            "problem_id": problem.id,
            "language": language,
            "source_code": source_code,
            "limitations": limitations,
            "callback_url": callback_url,
            "callback_token": callback_token
        }
        _fire_and_forget_enqueue(
            f"{current_app.config['JUDGE_SERVER']}/judger/{submission.id}",
            judge_payload,
            timeout_sec=3.0
        )
    db.session.commit()
    return jsonify({"ok": True, "rejudged": len(submissions)})

@bp.get("/<int:submission_id>/status")
@role_required()
def get_submission_status(submission_id):
    """
    轮询查看判题进度/结果（轻量）
    """
    s = SubmissionModel.query.get_or_404(submission_id)
    return jsonify({
        "status": s.status,
        "score": s.score
    }), 200
    

@bp.get("/<int:submission_id>")
@role_required()
def get_submission(submission_id):
    """
    详情页
    """
    s = SubmissionModel.query.get_or_404(submission_id)
    login_type = get_jwt()['login_type']
    if login_type == 'student' and s.user.id != int(get_jwt_identity()):
        return jsonify({'error': 'Permission denied'}), 403
    return jsonify({
        "submission_id": s.id,
        "user": {
            "id": s.user.id,
            "username": s.user.username,  
        },
        "problem_id": s.problem_id,
        "problem_set_id": s.problem_set_id,
        "problem_type": s.problem_type,
        "language": s.language,
        "max_time": s.max_time,
        "max_memory": s.max_memory,
        "status": s.status,
        "user_answer": s.user_answer,
        "score": s.score,
        "extra": s.extra,
        "time_stamp": s.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
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
    new_status = data.get("status")
    new_score = data.get("score")
    max_time = data.get("max_time")
    max_memory = data.get("max_memory")
    detail = data.get("detail")
    # finished_at = data.get("finished_at")

    if new_status:
        s.status = new_status
    if max_time:
        s.max_time = max_time
    if max_memory:
        s.max_memory = max_memory
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


@bp.get("/")
@role_required()
def list_submissions():
    """
    获取提交记录列表
    可选参数：
        user_id: 用户ID（不传则为当前用户，管理员可看所有）
        problem_id: 题目ID
        problem_set_id: 题集ID
        page: 页码（默认1）
        per_page: 每页条数（默认20）
    """

    # 过滤条件
    query = SubmissionModel.query

    user_id = request.args.get("user_id", type=int)
    if user_id:
        query = query.filter_by(user_id=user_id)

    problem_id = request.args.get("problem_id", type=int)
    if problem_id:
        query = query.filter_by(problem_id=problem_id)

    problem_set_id = request.args.get("problem_set_id", type=int)
    if problem_set_id:
        query = query.filter_by(problem_set_id=problem_set_id)

    # 分页
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = query.order_by(SubmissionModel.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [
            {
                "submission_id": s.id,
                "user": {
                  "id": s.user.id,
                  "username": s.user.username,  
                },
                "problem_id": s.problem_id,
                "problem_set_id": s.problem_set_id,
                "problem_type": s.problem_type,
                "language": s.language,
                "max_time": s.max_time,
                "max_memory": s.max_memory,
                "status": s.status,
                "score": s.score,
                "time_stamp": s.time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
            } for s in pagination.items
        ],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page
    })