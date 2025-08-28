@bp.get('/<int:pid>/test_cases/download')
@role_required(ROLE_TEACHER)
def download_test_cases(pid):
    """
    下载测试用例
    """
    try:
        memory_file = pack_test_cases(pid)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    return send_file(
        memory_file,
        as_attachment=True,
        download_name=f"test_cases_{pid}.zip",
        mimetype="application/zip"
    )