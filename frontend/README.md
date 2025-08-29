ㅤ: 08-29 09:34:24
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

ㅤ: 08-29 09:34:35
patch /api/submissions/problem/题号