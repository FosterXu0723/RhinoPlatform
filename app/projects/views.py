# 作者       ：yangwuxie
# 创建时间   ：2020/11/27 11:20
import json

from flask import session, jsonify, request, g, signals
from app import db
from app.models import User, Project, ProjectEnv
from app.projects import projects
from app.users.auth import auth_token
from app.utils import notEmpty


@projects.route("/addProject", methods=['POST'])
@auth_token.login_required
def create_project():
    login_user_id = g.flask_httpauth_user.get('id')
    request_data = json.loads(request.get_data().decode("utf-8"))
    # 新增project
    project_name = request_data.get("projectName")
    project_desc = request_data.get("projectDesc")
    project_status = request_data.get("projectStatus")
    project_modules = request_data.get("modules")
    if project_status == "true":
        project_status = True
    else:
        project_status = False
    if project_name == '' or project_name is None:
        return jsonify({
            'code': 99999,
            'msg': '项目名称不能为空！'
        })
    if project_name in list(map(lambda x: x.project_name, Project.query.all())):
        return jsonify({
            "code": 99999,
            'msg': '存在相同名称项目！新建失败'
        })
    # 实例化Project对象
    if len(project_modules) == 0:
        project = Project(project_name=project_name, project_user_id=login_user_id, project_desc=project_desc,
                      status=project_status)
    else:
        modules = ",".join([key.get("value") for key in project_modules])
        project = Project(project_name=project_name, project_user_id=login_user_id, project_desc=project_desc,
                          status=project_status, module=modules)
    data = {
        "projectName": project_name,
        "projectDesc": project_desc
    }
    # 事务提交失败，回滚，可以减少id被空占的情况
    try:
        db.session.add(project)
        db.session.commit()
        return jsonify({"code": 10000, "data": data, "msg": "新建项目成功"})
    except:
        db.session.rollback()
        return jsonify({"code": 99999, "msg": "数据插入失败"})


@projects.route("/editProject", methods=['POST'])
@auth_token.login_required
def edit_project():
    # 拿到当前登录的userid
    login_user_id = g.flask_httpauth_user.get('id')
    request_data = json.loads(request.get_data().decode("utf-8"))
    project_name = request_data.get("projectName")
    project_status = request_data.get('projectStatus')
    project_desc = request_data.get('projectDesc')
    project_id = request_data.get('id')
    module = request_data.get("modules")
    if project_name is None or project_name == '':
        return jsonify({
            'code': 99999,
            'msg': '项目名称不能为空'
        })
    if project_name in list(map(lambda x: x.project_name, Project.query.filter(Project.id != project_id).all())):
        return jsonify({
            'code': 99999,
            'msg': '已经存在相同名称的项目！'
        })
    # 更新内容
    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return jsonify({
            'code': 99999,
            'msg': '项目不存在'
        })
    project.project_name = project_name
    project.project_desc = project_desc
    project.status = project_status
    if len(module) == 0:
        project.module = ""
    else:
        project.module = ",".join([key.get("value") for key in module])
    try:
        db.session.add(project)
        db.session.commit()
    except:
        db.session.rollback()
    data = {
        "projectName": project_name,
        "userId": login_user_id,
    }
    return jsonify({"code": 10000, "data": data, "msg": "编辑项目成功"})


@projects.route('/deleteProject', methods=['POST'])
@auth_token.login_required
def delete_project():
    # 拿到当前登录的userid
    login_user_id = g.flask_httpauth_user.get('id')
    project_id = request.form.get("projectId")
    project = Project.query.filter_by(id=project_id).first()
    if not project:
        data = {
            "code": 99999,
            "msg": "项目不存在！！"
        }
        return jsonify(data)
    db.session.delete(project)
    data = {
        "code": 10000,
        "msg": "删除项目成功"
    }
    return jsonify(data)


@projects.route("/allProject", methods=['GET'])
@auth_token.login_required
def add_project():
    """
    所有项目接口
    :return: 返回所有项目
    """
    projects = Project.query.order_by(Project.id.desc()).all()
    if len(projects) == 0:
        return jsonify({
            "code": 99999,
            "msg": "没有项目存在"
        })
    project_data = []
    for project in projects:
        project_data.append(project.to_dict())
    return jsonify({"code": 10000, "data": {
        "list": project_data
    }, "msg": "success"})


@projects.route("/getProjects", methods=['GET', 'POST'])
@auth_token.login_required
def get_projects():
    """
    根据页码返回数据
    :return:
    """
    page = int(request.form.get("page"))
    pageSize = int(request.form.get("pageSize"))
    projects = Project.query.order_by(Project.id.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    totalProject = len(Project.query.all())
    if len(projects) == 0:
        return jsonify({
            'code': 99999,
            "msg": "当前没有项目！"
        })
    data = {}
    projectList = []
    for project in projects:
        projectList.append(project.to_dict())
    # 必须返回dict类型
    data['list'] = projectList
    return jsonify({'code': 10000, 'msg': 'success', 'data': data, 'total': totalProject})


@projects.route("/addEnv", methods=["POSt"])
@auth_token.login_required
def add_project_env():
    """
    新增http配置
    :return:
    """
    params = request.form
    projectId = params.get("projectId")
    envName = params.get("projectEnvName")
    envHttpBaseUrl = params.get("projectHost")
    commonHeader = params.get("projectHeader")
    database = params.get("projectDbName")
    dbHost = params.get("projectDbUrl")
    dbPort = params.get("projectDbPort")
    dbType = params.get("projectDbType")
    dbUser = params.get("projectDbUser")
    dbPassword = params.get("projectDbPassword")
    env = ProjectEnv(env_name=envName, host=envHttpBaseUrl, header=commonHeader, project=projectId, database=database,
                     db_host=dbHost, db_type=dbType, db_port=dbPort, db_password=dbPassword, db_user=dbUser)
    try:
        db.session.add(env)
        db.session.commit()
        return jsonify({
            "code": 10000,
            "msg": "提交成功"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 99999,
            "msg": "提交失败"
        })


@projects.route('/editEnv', methods=["POST"])
@auth_token.login_required
def edit_project_env():
    """
    编辑http配置
    :return:
    """
    params = request.form
    projectId = params.get("projectId")
    envName = params.get("projectEnvName")
    envHttpBaseUrl = params.get("projectHost")
    commonHeader = params.get("projectHeader")
    database = params.get("projectDbName")
    dbHost = params.get("projectDbUrl")
    dbPort = params.get("projectDbPort")
    dbType = params.get("projectDbType")
    dbUser = params.get("projectDbUser")
    dbPassword = params.get("projectDbPassword")
    env = ProjectEnv.query.filter(ProjectEnv.project == projectId).first()
    if not notEmpty(env):
        return jsonify({
            "code": 99999,
            "msg": "当前配置的环境不存在！"
        })
    env.project = projectId
    env.env_name = envName
    env.host = envHttpBaseUrl
    env.header = commonHeader
    env.database = database
    env.db_host = dbHost
    env.db_port = dbPort
    env.db_type = dbType
    env.db_user = dbUser
    env.db_password = dbPassword
    try:
        db.session.add(env)
        db.session.commit()
        return jsonify({
            "code": 10000,
            "msg": "提交成功"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 99999,
            "msg": "提交失败"
        })


@projects.route("/getEnv", methods=["POSt"])
def get_env():
    requestParam = request.form
    projectId = requestParam.get("projectId")
    env = ProjectEnv.query.filter(ProjectEnv.project == projectId).first()
    if notEmpty(env):
        return jsonify({
            "code": 10000,
            "msg": "success",
            "data": env.to_dict()
        })
    else:
        return jsonify({
            "code": 99999,
            "msg": "当前项目没有对应的环境"
        })


@projects.route("/getModules", methods=["get"])
def get_modules():
    pro_id = request.args.get("projectId")
    pro = Project.query.filter(Project.id == pro_id).first()
    if pro is not None:
        return jsonify({
            "code": 10000,
            "msg": "success",
            "data": pro.to_dict().get("modules")
        })
    else:
        return jsonify({
            "code": 99999,
            "msg": "project 不存在",
            "data": None
        })
