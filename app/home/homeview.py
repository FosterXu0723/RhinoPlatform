"""
    :author: xiaoyicai.
    :date: 2021/05/09.
    :use: 首页的接口
"""
# from app.models import Project, Testcase
from . import home_view
from flask import jsonify
from app.users.auth import auth_token
from app.model.homeviews import *
from app.models import Project


# projects项目映射关系
@home_view.route('/options', methods=['GET'])
@auth_token.login_required
def options():
    projects = db.session.execute("select id,project_name from projects  ")
    # return len(list(projects))
    res = query_util.result_to_dict(projects)

    return jsonify({"code": 10000, "items": res, "msg": "success"})


# 项目总数和用例总数和定时任务总数
@home_view.route('/total', methods=['GET'])
@auth_token.login_required
def get_total_():
    return jsonify({"code": 10000, "items": get_total(), "msg": "success"})


# 本周新增用例数
@home_view.route('/case/week', methods=['GET'])
@auth_token.login_required
def get_case_by_week_():
    return jsonify({"code": 10000, "data": {
        "total": get_case_by_week()
    }, "msg": "success"})


# 每周每个项目新增用例数
@home_view.route('/case/week_project', methods=['GET'])
@auth_token.login_required
def get_case_week_project_():
    return jsonify({"code": 10000, "data": {
        "items": get_case_by_week_project()
    }, "msg": "success"})


@home_view.route('/today', methods=['GET'])
@auth_token.login_required
def get_today_():
    return jsonify({"code": 10000, "data": {
        "items": today()
    }, "msg": "success"})


@home_view.route('/caseTop', methods=['GET'])
@auth_token.login_required
def get_case_top():
    # res = caseTop()
    if caseTop() != 1:

        run_top, pass_rate_top = caseTop()
        return jsonify({"code": 10000, "data": {
            "pass_rate_top": pass_rate_top,
            "run_top": run_top
        }, "msg": "success"})
    else:
        return jsonify({"code": 10000, "data": {

        }, "msg": "success"})


@home_view.route('/project/<pid>', methods=['GET'])
@auth_token.login_required
def get_projectdata(pid):
    # project: Project = Project.query.filter_by(id=pid).first()
    # if not project:
    #     return jsonify({"code": 9999, "data": None, "msg": '暂无工程数据'})
    return jsonify({"code": 10000, "data": {"items": get_project_data(pid)}, "msg": "success"})
