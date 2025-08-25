def legacy_judger(problem_type, answers, user_answers):
    if problem_type == 'single':
        # 单选
        if answers == user_answers:
            return 100, "AC"
        else:
            return 0, "WA"
    elif problem_type == 'multiple':
        # 多选
        if answers == user_answers:
            return 100, "AC"
        elif set(user_answers).issubset(set(answers)):
            return 1, "WA"
        else:
            return 0, "WA"
    elif problem_type == 'fill':
        if answers == user_answers:
            return 100, "AC"
        else:
            return 0, "WA"
    else:
        return 0, "WA"