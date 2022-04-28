"""
@File:views.py
@author:yangwuxie
@date: 2020/12/28
"""
from sqlalchemy import and_

from app import db
from app.utils.RequestParamsUtils import str2Dict
from common.Api import Api
from . import interface
from flask import jsonify, g, request
from app.users.auth import auth_token
from app.utils import notEmpty
from app.models import Interface, Project
from datetime import datetime
import requests


@interface.route('/addInterface', methods=['POST'])
@auth_token.login_required
def add_interface():
    user_id = g.flask_httpauth_user.get('id')
    request_params = request.form
    interface_name = request_params.get('interfaceName')
    projects_id = request_params.get("project")
    interface_url = request_params.get("interfacePath")
    interface_meth = request_params.get("interfaceMethod")
    interface_headers = request_params.get("interfaceHeader")
    interface_user_id = user_id
    interface_type = request_params.get("interfaceType")
    interface_param = request_params.get("interfaceParams")
    # 有内容为空
    # if not notEmpty(interface_name, interface_meth, interface_url, interface_headers):
    #     return jsonify({
    #         'code': 99999,
    #         'msg': "请求参数非空校验未通过，请检查参数！"
    #     })
    # headers传过来的参数可能是jsonString，需要处理成dict
    interface = Interface(interface_name=interface_name, interface_headers=interface_headers,
                          interface_meth=interface_meth,
                          interface_param=interface_param, interface_url=interface_url,
                          interface_user_id=interface_user_id,
                          projects_id=projects_id, interfacetype=interface_type)
    try:
        db.session.add(interface)
        db.session.commit()
        return jsonify({
            'code': 10000,
            'msg': '新增接口成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 99999,
            'msg': "新增接口失败，失败原因:{}".format(e)
        })


@interface.route("/editInterface", methods=['POST'])
@auth_token.login_required
def edit_interface():
    user_id = g.flask_httpauth_user.get('id')
    request_params = request.form
    interface_name = request_params.get('interfaceName')
    projects_id = request_params.get("project")
    interface_url = request_params.get("interfacePath")
    interface_meth = request_params.get("interfaceMethdod")
    interface_headers = request_params.get("interfaceHeader")
    interface_user_id = user_id
    interface_type = request_params.get("interfaceType")
    interface_param = request_params.get("interfaceParams")
    interface_id = request_params.get("interfaceId")
    # 有内容为空
    # if not notEmpty(interface_name, interface_meth, interface_url, interface_headers):
    #     return jsonify({
    #         'code': 99999,
    #         'msg': "请求参数非空校验未通过，请检查参数！"
    #     })
    interface = Interface.query.filter(Interface.id == interface_id).first()
    if not notEmpty(interface):
        return jsonify({
            'code': 99999,
            'msg': '编辑的接口不存在'
        })
    interface.interface_name = interface_name
    interface.projects_id = projects_id
    interface.interface_url = interface_url
    interface.interface_meth = interface_meth
    interface.interface_headers = interface_headers
    interface.interface_user_id = interface_user_id
    interface.interfacetype = interface_type
    interface.interface_param = interface_param
    try:
        db.session.add(interface)
        db.session.commit()
        return jsonify({
            'code': 10000,
            'msg': '编辑接口成功！'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 99999,
            'msg': "编辑接口失败，失败原因：{}".format(e)
        })


@interface.route('/allInterface', methods=['GET'])
@auth_token.login_required
def all_interface():
    """
    根据项目id获取接口列表
    请求参数projectId
    :return:
    """
    project_id = request.args.get('projectId')
    project = Project.query.filter(Project.id == project_id).first()
    if not notEmpty(project):
        return jsonify({
            'code': 99999,
            'msg': '项目不存在！',
            "data": {"list": None}
        })
    project_interface = list(map(lambda x: x.to_dict(), project.interface.all()))
    return jsonify({
        'code': 10000,
        'msg': 'success',
        'data': {
            "list": project_interface,
            "total": len(project_interface)
        }
    })


@interface.route("/interfaces", methods=['get'])
@auth_token.login_required
def all_interfaces():
    """
    直接返回全部接口数据
    :return:
    """
    requestParams = request.args
    page = int(requestParams.get("page"))
    pageSize = int(requestParams.get("pageSize"))
    pageInterface = Interface.query.offset((page - 1) * pageSize).limit(pageSize).all()
    interfaces = Interface.query.all()
    if len(pageInterface) == 0:
        return jsonify({
            "code": 99999,
            "msg": "暂无接口数据",
            "data": {"list": None}
        })
    interfaceList = list(map(lambda x: x.to_dict(), pageInterface))
    return jsonify({
        "code": 10000,
        "data": {
            "list": interfaceList,
            "total": len(interfaces)
        }
    })


@interface.route('/deleteInterface', methods=['POST'])
@auth_token.login_required
def delete_api():
    params_json = request.form
    int_id = params_json.get('interfaceId')
    api = Interface.query.filter(and_(Interface.id == int_id, Interface.delete_at == None)).first()
    if not api:
        return jsonify({
            'code': 99999,
            'msg': '接口不存在！',
            "data": {"list": None}
        })
    #  逻辑删除
    try:
        api.delete_at = datetime.now()
        db.session.add(api)
        db.session.commit()
    except:
        db.session.rollback()


@interface.route('/getApi', methods=['get'])
@auth_token.login_required
def get_api():
    params = request.args
    projectId = params.get("projectId")
    interfaceName = params.get('interfaceName')
    if projectId == "" and interfaceName == "":
        interfaces = Interface.query.all()
        if len(interfaces) == 0:
            return jsonify({
                "code": 99999,
                "msg": "暂无接口数据",
                "data": {'list': None}
            })
        interfaceList = list(map(lambda x: x.to_dict(), interfaces))
        return jsonify({
            "code": 10000,
            "msg": "查询成功",
            "data": {
                "list": interfaceList,
                "total": len(interfaceList)
            }
        })
    if projectId == "" and interfaceName != "":
        interface = Interface.query.filter(Interface.interface_name == interfaceName).first()
        if not notEmpty(interface):
            return jsonify({
                "code": 99999,
                "msg": "暂无接口数据",
                "data": {'list': None}
            })
        return jsonify({
            'code': 100000,
            'msg': "查询成功",
            "data": {'list': interface.to_dict(), "total": len(interface)}
        })
    if projectId != "" and interfaceName == "":
        project = Project.query.filter(Project.id == projectId).first()
        if not notEmpty(project):
            return jsonify({
                'code': 99999,
                'msg': '项目不存在！',
                "data": {"list": None}
            })
        project_interface = list(map(lambda x: x.to_dict(), project.interface.all()))
        return jsonify({
            'code': 10000,
            'msg': 'success',
            'data': {
                "list": project_interface,
                "total": len(project_interface)
            }
        })
    if projectId != "" and interfaceName != "":
        project = Project.query.filter(Project.id == projectId).first()
        if not notEmpty(project):
            return jsonify({
                'code': 99999,
                'msg': '项目不存在！',
                "data": {"list": None}
            })
        project_interface = list(map(lambda x: x.to_dict(), project.interface.all()))
        for interface in project_interface:
            if interface['interfaceName'] == interfaceName:
                return jsonify({
                    "code": 10000,
                    "msg": "查询成功",
                    "data": {
                        'list': interface.to_dict()
                    }
                })
        return jsonify({
            "code": 99999,
            "msg": "查询不到该接口",
            "data": {
                'list': None
            }
        })


@interface.route("/execute", methods=["POST"])
@auth_token.login_required
def execute():
    params = request.form
    apiId = params.get("interfaceId")
    api: Interface = Interface.query.filter(Interface.id == apiId).first()
    projectId = api.projects_id
    try:
        envDict = Project.query.filter(Project.id == projectId).first().env.first().to_dict()
    except Exception as e:
        return jsonify({
            "code": 99999,
            "msg": "环境缺失，请求失败"
        })
    if notEmpty(api):
        apiPath = "/" + api.interface_url if not api.interface_url.startswith("/") else api.interface_url
        apiHeader = api.interface_headers if isinstance(api.interface_headers, dict) else str2Dict(
            api.interface_headers)
        apiParams = api.interface_param if isinstance(api.interface_param, dict) else str2Dict(api.interface_param)
        apiMethod = api.interface_meth or "get"
        apiName = api.interface_name
        projectHost = envDict['projectHost'] or None
        projectHeader = envDict['projectHeader'] if isinstance(envDict['projectHeader'], dict) else str2Dict(
            envDict['projectHeader'])
        requestUrl = projectHost + apiPath
        # projectHeader.update(apiHeader)
        response = Api(url=requestUrl, method=apiMethod, params=apiParams, headers=projectHeader).execute()
        try:
            # 执行成功，表示请求成功
            return jsonify({
                'code': 10000,
                'msg': "请求成功",
                "data": {
                    "statusCode": response.status_code,
                    "response": response.text
                }
            })
        except Exception as e:
            # request failed
            return jsonify({
                'code': 99999,
                'msg': "请求失败！",
                'data': response
            })
    return jsonify({
        "code": 99999,
        "msg": "接口不存在"
    })
