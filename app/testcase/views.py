"""
@File:views.py
@author:yangwuxie
@date: 2021/01/06
"""
import json
import os
import traceback
from datetime import datetime

import yaml
from flask import jsonify, request, Response, g
import ruamel.yaml
from flask_sqlalchemy import Pagination
from sqlalchemy import and_

from app.utils import notEmpty, BASEPATH
from common.Log import log
from core.HttpTestcaseStep import HttpTestcaseStep
from error_message import ParameterTypeOfDictException, RequestFailException
from . import testcase
from app.models import Testcase, TestStep, Project, User
from app import db
from app.users.auth import auth_token
from app.utils.BatchTranlateYml import yml2testcase, allYmlFile, getStep, getPath, _doReplace, _convert2PlatformJudge
from app.observer.TestResultObserver import upsertTestResult
from ..observer.TaskObserver import taskCaseUpdateObserver
from ..utils.JsonTools import getApiLogContent


@testcase.route('/add', methods=['POST'])
@auth_token.login_required
def addTestcase():
    login_user_id = g.flask_httpauth_user.get('id')
    requestParams = request.form
    projectId = requestParams.get("projectId")
    caseName = requestParams.get("caseName")
    module = requestParams.get("module")
    if not notEmpty(projectId):
        return jsonify({
            "code": 99999,
            "msg": "所属项目不能为空！"
        })
    author = User.query.filter(User.id == login_user_id).first().username
    case = Testcase(projects_id=projectId, case_name=caseName, module=module, create_at=datetime.now(), author=author)
    try:
        db.session.add(case)
        db.session.commit()
        return jsonify({
            'code': 10000,
            'msg': "新建case成功！",
            "data": {
                "list": case.to_dict()
            }
        })
    except:
        db.session.rollback()
        return jsonify({
            "code": 99999,
            "msg": "新建case失败"
        })


@testcase.route('/editCase', methods=['POST'])
@auth_token.login_required
def editCase():
    requestParams = request.form
    caseId = requestParams.get("caseId")
    module = requestParams.get("module")
    case = Testcase.query.filter(Testcase.id == caseId).first()
    if not notEmpty(case):
        return jsonify({
            "code": 99999,
            'msg': "case不存在！"
        })
    case.projects_id = requestParams.get("projectId")
    case.case_name = requestParams.get("caseName")
    case.module = module
    try:
        db.session.add(case)
        db.session.commit()
        return jsonify({
            "code": 10000,
            "msg": "编辑成功！",
            "data": {
                "list": case.to_dict()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 99999,
            "msg": "编辑失败！"
        })


@testcase.route("/pageCase", methods=["get"])
@auth_token.login_required
def all():
    """
    pageCase需要带上查询条件
    :return:
    """
    requestParams = request.args
    page = int(requestParams.get("page"))
    pageSize = int(requestParams.get("pageSize"))
    caseName = requestParams.get("caseName")
    author = requestParams.get("author").strip() or None
    try:
        # 存在projectId
        projectId = int(requestParams.get("projectId"))
        if caseName:  # 存在两个条件
            pageCase: Pagination = Testcase.query.filter(
                and_(Testcase.case_name.like(f"%{caseName}%"), Testcase.projects_id == projectId,
                     Testcase.author == author, Testcase.open_status == True)).order_by(
                Testcase.id.desc()).paginate(
                page, pageSize) if author else Testcase.query.filter(
                and_(Testcase.case_name.like(f"%{caseName}%"), Testcase.projects_id == projectId,
                     Testcase.open_status == True)).order_by(Testcase.id.desc()).paginate(page, pageSize)
        else:  # 存在projectId搜索条件
            pageCase: Pagination = Testcase.query.filter(
                and_(Testcase.projects_id == projectId, Testcase.open_status == True,
                     Testcase.author == author)).order_by(Testcase.id.desc()).paginate(page, pageSize) if author else \
                Testcase.query.filter(and_(Testcase.projects_id == projectId, Testcase.open_status == True)).order_by(
                    Testcase.id.desc()).paginate(page, pageSize)
    except ValueError:  # 不存在projectId
        if not caseName:
            pageCase: Pagination = Testcase.query.filter(Testcase.open_status == True,
                                                         Testcase.author == author).order_by(
                Testcase.id.desc()).paginate(page, pageSize) if author else Testcase.query.filter(
                Testcase.open_status == True).order_by(
                Testcase.id.desc()).paginate(page, pageSize)
        else:
            pageCase: Pagination = Testcase.query.filter(
                and_(Testcase.case_name.like(f"%{caseName}%"), Testcase.open_status == True,
                     Testcase.author == author)).order_by(Testcase.id.desc()).paginate(page, pageSize) if author else \
                Testcase.query.filter(
                    and_(Testcase.case_name.like(f"%{caseName}%"), Testcase.open_status == True)).order_by(
                    Testcase.id.desc()).paginate(page, pageSize)
    if len(pageCase.items) == 0:
        return jsonify({
            "code": 99999,
            "msg": "暂无用例",
            "data": {
                "list": None,
                "total": 0
            }
        })
    return jsonify({
        "code": 10000,
        "msg": "success",
        "data": {
            "list": list(map(lambda x: x.to_dict(), pageCase.items)),
            "total": pageCase.total
        }
    })


@testcase.route("/execute", methods=["post"])
@auth_token.login_required
def execute():
    """
    执行用例
    :parameter: caseId 拿到caseId，获取stepId执行step
    :return:
    """
    caseId = request.form.get("caseId")
    case: Testcase = Testcase.query.filter(Testcase.id == caseId).first()
    if not case:
        return jsonify({
            "code": 99999,
            "msg": "未找到该caseId对应的用例"
        })
    steps = TestStep.query.filter(and_(TestStep.testcase_id == caseId, TestStep.delete_at == None)).order_by(
        TestStep.case_step_index.asc()).all()
    if len(steps) == 0:
        return jsonify({
            "code": 99999,
            "msg": "case没有step"
        })
    projectId = Testcase.query.filter(Testcase.id == caseId).first().projects_id
    env = Project.query.filter_by(id=projectId).first().env.first()
    if not env:
        return jsonify({
            "code": 99999,
            "msg": f"当前case对应的项目暂未设置所属环境！，请检查后再试"
        })
    envDict = env.to_dict()
    iterStep = iter(steps)
    # 返回断言的内容
    executeResultMap = {}
    caseIndex = 0
    while True:
        try:
            caseIndex += 1
            step: TestStep = next(iterStep)
            if step.set_up_case:  # 步骤的前置依赖，全都是依赖于case
                # 执行依赖
                dependencyCaseId = step.set_up_case
                dependencyCaseSteps = TestStep.query.filter(
                    and_(TestStep.testcase_id == dependencyCaseId, TestStep.delete_at == None)).order_by(
                    TestStep.case_step_index.asc()).all()
                if len(dependencyCaseSteps) == 0:  # 当依赖case的step为0时，log抛出错误，然后继续
                    log.error(f"{step.step_name}的依赖用例:{dependencyCaseId},查询不到step，跳过执行")
                else:  # 执行依赖用例
                    dependencyProjectId = Testcase.query.filter(Testcase.id == dependencyCaseId).first().projects_id
                    dependencyEnv = Project.query.filter_by(id=dependencyProjectId).first().env.first().to_dict()
                    for dependencyStep in dependencyCaseSteps:
                        dependencyStepResult, dependencyStepFlag = HttpTestcaseStep(dependencyStep).execute(
                            dependencyEnv)
                        if not dependencyStepFlag:  # 依赖用例的断言失败
                            # 执行失败，统计结果
                            case.case_run_total += 1
                            case.case_last_runtime = datetime.now()
                            try:
                                db.session.add(case)
                                db.session.commit()
                                return jsonify({
                                    "code": 99999,
                                    "msg": f"{step.step_name} 的依赖用例 {dependencyCaseId} 断言失败，断言内容为{dependencyStepResult}"
                                })
                            except:
                                db.session.rollback()
            judgeResult, judgeFlag = HttpTestcaseStep(step).execute(envDict)
            if step.tear_down_case:  # 步骤的后置依赖，全都是依赖于case
                pass
            executeResultMap[step.id] = judgeResult
            # 断言失败，直接返回，流程结束
            if not judgeFlag:
                case.case_run_total += 1
                case.case_last_runtime = datetime.now()
                db.session.commit()
                upsertTestResult.send(False, result=executeResultMap, caseId=caseId)
                return jsonify({
                    "code": 99999,
                    "msg": f"用例id:{caseId},第{caseIndex}步断言失败！{judgeResult}",
                })
        # 拿到StopIteration表示iter执行完毕
        except StopIteration:
            # 执行成功，更新passTotal和runTotal，runtime
            case.case_pass_total += 1
            case.case_run_total += 1
            case.case_last_runtime = datetime.now()
            db.session.add(case)
            db.session.commit()
            # 执行成功之后发送信号，插入执行记录
            upsertTestResult.send(True, result=executeResultMap, caseId=caseId)
            return jsonify({
                "code": 10000,
                "msg": "用例执行成功",
                "data": executeResultMap
            })
        except ParameterTypeOfDictException as e:
            # 执行报错，新增case failure
            case.case_run_total += 1
            case.case_last_runtime = datetime.now()
            db.session.commit()
            upsertTestResult.send(False, result=executeResultMap, caseId=caseId)
            return jsonify({
                "code": 999991,
                "msg": f"用例执行失败:{e}"
            })
        except RequestFailException as e:
            # 执行报错，新增case failure
            case.case_run_total += 1
            case.case_last_runtime = datetime.now()
            db.session.commit()
            upsertTestResult.send(False, result=executeResultMap, caseId=caseId)
            return jsonify({
                "code": 999992,
                "msg": f"用例执行失败{e}"
            })
        except Exception as e:
            # 执行报错，新增case failure
            case.case_run_total += 1
            case.case_last_runtime = datetime.now()
            db.session.commit()
            upsertTestResult.send(False, result=executeResultMap, caseId=caseId)
            return jsonify({
                "code": 999993,
                "msg": f"用例执行失败{e}"
            })


@testcase.route("/ymlCase", methods=['post'])
@auth_token.login_required
def uploadYmlStream():
    """
    yml转用例接口
    :return:
    """
    login_user_id = g.flask_httpauth_user.get('id')
    requestData = request.form.get("ymlData")
    startIndex = requestData.index("testcase1")
    effectiveStr = requestData[startIndex:]
    try:
        # 设置允许key重复
        yml = ruamel.yaml.YAML()
        yml.allow_duplicate_keys = True
        load = yml.load(effectiveStr)
        if not isinstance(load, dict):
            return jsonify({
                "code": 99999,
                "msg": "请检查yml格式，当前版本限制一次一个case！"
            })
        caseData = load.get("testcase1")
        # 获取header内容，headersparamsvalue
        headersValue = caseData.get("headersparamsvalue")
        # 用例所属模块
        module = caseData.get("module") or None
        # 获取data内容，dataparamsvalue
        dataValue = caseData.get("dataparamsvalue")
        # 实例化Testcase
        testcase = Testcase()
        testcase.case_name = caseData.get("casename")
        testcase.projects_id = int(caseData.get('projectid'))
        testcase.module = module
        testcase.author = User.query.filter(User.id == login_user_id).first().username
        testcase.create_at = datetime.now()
        try:
            db.session.add(testcase)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify({
                "code": 99999,
                "msg": "yml转case，case写入失败！"
            })
        # 实例化TestStep
        steps = iter(getStep(caseData))
        stepIndex = 1
        while True:
            try:
                step = next(steps)
                # 不能根据testcase.casename获取上面新建的testcase，只能通过获取最新id的Testcase
                first: Testcase = Testcase.query.order_by(Testcase.id.desc()).limit(1).first()
                testStep = TestStep()
                testStep.case_step_index = stepIndex
                testStep.step_name = step.get("name")
                general = step.get("general")
                testStep.step_api_path = getPath(general.get("path"))
                testStep.step_api_method = general.get("method")
                # orderedDict转换成dict
                testStep.step_api_header = _doReplace(json.loads(json.dumps(step.get("headers"))), headersValue)
                testStep.step_api_data = _doReplace(json.loads(json.dumps(step.get("data"))), dataValue)
                extract = step.get("extract") or None
                if extract:
                    testStep.step_api_extract = json.loads(json.dumps(extract))
                else:
                    testStep.step_api_extract = None
                validate = step.get("validate") or None
                if validate:
                    testStep.step_api_assert = _convert2PlatformJudge(json.loads(json.dumps(validate)))
                else:
                    testStep.step_api_assert = None
                testStep.testcase_id = first.id
                try:
                    db.session.add(testStep)
                    db.session.commit()
                    # 前边的执行没问题
                    stepIndex += 1
                except Exception:
                    db.session.rollback()
                    return jsonify({
                        "code": 99999,
                        "msg": "yml转case，step写入失败"
                    })
            except StopIteration:
                return jsonify({
                    "code": 10000,
                    "msg": "Success"
                })
    except Exception as e:
        return jsonify({
            "code": 99999,
            "msg": "yml字符转python对象失败！{}".format(e)
        })


@testcase.route("/query", methods=["post"])
def query():
    """
    查询依赖用例
    :return: step中的extract字段
    """
    requestForm = request.form
    try:
        caseId = int(requestForm.get("params"))
        steps = Testcase.query.filter(Testcase.id == caseId).first().steps.all()
        if len(steps) == 0:
            return jsonify({
                "code": 99999,
                "msg": "查询无果，要不考虑换个依赖用例？"
            })
        extractList = [step.step_api_extract for step in steps]
        return jsonify({
            "code": 10000,
            "msg": "success",
            "data": extractList
        })
    except:
        caseName = requestForm.get("params")
        if not caseName:
            return jsonify({
                "code": 99999,
                "msg": "没有参数你想查询啥玩意儿？"
            })
        steps = Testcase.query.filter(Testcase.case_name.like(f"%{caseName}%")).order_by(
            Testcase.id.desc()).first().steps.all()
        if len(steps) == 0:
            return jsonify({
                "code": 99999,
                "msg": "查询无果，要不考虑换个依赖用例？"
            })
        extractList = [step.step_api_extract for step in steps]
        return jsonify({
            "code": 10000,
            "msg": "success",
            "data": extractList
        })


@testcase.route("/backdoor/initCase", methods=['get'])
def backdoor():
    """
    批量处理yml文件后门接口
    :return:
    """
    args = request.args
    user = args.get("username")
    if user != "admin":
        return jsonify({
            "code": 99999,
            "msg": "failed"
        })
    filePath = os.path.join(os.path.abspath("."), 'test_data')
    try:
        for file in allYmlFile(filePath, [], []):
            if file.endswith('yml') or file.endswith("yaml"):
                yml2testcase(file)
    except Exception as e:
        return jsonify({
            "code": 99999,
            "msg": "初始化case失败{}".format(e)
        })
    return jsonify({
        "code": 10000,
        "msg": "初始化成功"
    })


@testcase.route("/calculate", methods=["get"])
def calculate():
    """
    数据统计
    :return:
    """
    pass


@testcase.route("/search", methods=["get"])
@auth_token.login_required
def search():
    """
    查询用例
    :return:
    """
    queryParams = request.args
    caseName = queryParams.get("caseName")
    author = queryParams.get("author").strip() or None
    try:
        # 存在项目搜索条件
        projectId = int(queryParams.get("projectId"))
        cases = Testcase.query.filter(
            and_(Testcase.case_name.like(f"%{caseName}%"), Testcase.projects_id == projectId,
                 Testcase.author == author)).all()
        if len(cases) == 0:
            return jsonify({
                "code": 99999,
                "msg": "暂无数据",
                "data": {
                    "list": None,
                    "total": 0
                }
            })
    except ValueError:
        # 不存在项目搜索条件
        cases = Testcase.query.filter(and_(Testcase.case_name.like(f"%{caseName}%"), Testcase.author == author)).all()
        if len(cases) == 0:
            return jsonify({
                "code": 99999,
                "msg": "暂无数据",
                "data": {
                    "list": None,
                    "total": 0
                }
            })
    return jsonify({
        "code": 10000,
        "msg": "success",
        "data": {
            "list": list(map(lambda x: x.to_dict(), cases)),
            "total": len(cases)
        }
    })


@testcase.route("/close", methods=["post"])
@auth_token.login_required
def close():
    case = request.form.get("caseId")
    tcase: Testcase = Testcase.query.filter(Testcase.id == int(case)).first()
    if not tcase:
        return jsonify({
            "code": 99999,
            "msg": "该用例不存在！"
        })
    try:
        tcase.open_status = False
        db.session.add(tcase)
        db.session.commit()
        return jsonify({
            "code": 10000,
            "msg": "success"
        })
    except Exception:
        log.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({
            "code": 99999,
            "msg": "关闭用例失败！"
        })
    finally:
        taskCaseUpdateObserver.send("remove", caseId=case)


@testcase.before_request
def before_request():
    """
    执行请求之前的处理
    :return:
    """
    # 在执行execute接口的时候在log文件中新增一个标记
    if request.path == '/testcase/execute' and request.method.upper() == "POST":
        log.info("**************execute start******************")
    pass


@testcase.after_request
def afterRequest(response: Response) -> Response:
    """
    执行完成请求之后的处理
    返回执行过程中产生的日志
    执行完视图函数之后返回客户端之前
    :return: response
    """
    if request.path == "/testcase/execute" and request.method.upper() == "POST":
        # 执行记录日志的功能,获取start-end之间的日志内容
        log.info("**************execute end******************")
        logContent = getApiLogContent(os.path.join(BASEPATH, "logs/platform.log"))
        data = json.loads(response.get_data(as_text=True))
        data['log'] = logContent
        response.set_data(json.dumps(data))
    return response
