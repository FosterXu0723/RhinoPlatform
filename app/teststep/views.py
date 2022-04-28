"""
@File:views.py
@author:yangwuxie
@date: 2021/01/13
"""
import importlib
import json

from sqlalchemy import and_

from flask import jsonify, request
from app import db
from app.models import TestStep, Interface, Testcase
from core.ExternalFunction import getFunctionMapping
from . import teststep
from app.utils import notEmpty
from app.users.auth import auth_token
from threading import Lock
from app.utils.RequestParamsUtils import str2Dict
from datetime import datetime

from ..observer.TestcaseObserver import testStepObserver
from ..utils.JsonTools import getExternalFunctionDescMap

"""
前端全局采用content-type：application/x-www-form-urlencoded解决跨域问题
返回steps按照case_step_index顺序排列
"""


@teststep.route('/add', methods=['POST'])
@auth_token.login_required
def add():
    """
    统一转json之后入库
    :return:
    """
    requestParam = request.form
    name = requestParam.get("stepName")
    index = int(requestParam.get("stepIndex"))
    caseId = int(requestParam.get("testcaseId"))
    apiId = int(requestParam.get("interfaceId")) if requestParam.get("interfaceId") else None
    path = requestParam.get("stepApiPath")
    method = requestParam.get("stepApiMeth")
    try:
        header = str2Dict(requestParam.get("stepApiHeader")) if requestParam.get("stepApiHeader") else \
            requestParam.get("stepApiHeader")
        data = str2Dict(requestParam.get("stepApiData")) if requestParam.get("stepApiData") else requestParam.get(
            "stepApiData")
        extract = str2Dict(requestParam.get("stepApiExtra")) if requestParam.get("stepApiExtra") else None
    except Exception as e:
        return jsonify({
            "code": 99999,
            "msg": "参数格式错误，请检查后再试"
        })
    if requestParam.get("stepApiAssert"):
        try:
            judge = json.loads(requestParam.get("stepApiAssert"))
        except Exception as e:
            judge = str2Dict(requestParam.get("stepApiAssert"))
    else:
        judge = None
    dependencyCase = requestParam.get("dependencyCase")
    try:
        dependencyCaseId = int(dependencyCase)
    except:
        if dependencyCase:
            dependencyCaseId = Testcase.query.filter(Testcase.case_name.like(f"%{dependencyCase}%")).order_by(
                Testcase.id.desc()).first().id
        else:
            dependencyCaseId = None
    if not notEmpty(caseId):
        return jsonify({
            "code": 99999,
            "msg": "参数缺失，用例id"
        })
    if notEmpty(Testcase.query.filter(Testcase.id == caseId).first()):
        if apiId:
            interface = Interface.query.filter(Interface.id == apiId).first()
            # 拿到api，优先api数据
            if interface:
                path = interface.interface_url
                method = interface.interface_meth
                header = interface.interface_headers
                data = interface.interface_param
                step = TestStep(step_name=name, case_step_index=index, testcase_id=caseId, interface_id=apiId,
                                step_api_path=path, step_api_method=method, step_api_header=header, step_api_data=data,
                                step_api_extract=extract, step_api_assert=judge, set_up_case=dependencyCaseId)
                try:
                    db.session.add(step)
                    db.session.commit()
                    return jsonify({
                        'code': 10000,
                        'msg': '提交casestep成功！'
                    })
                except:
                    db.session.rollback()
                    return jsonify({
                        "code": 99999,
                        'msg': '提交casestep失败！'
                    })
        #  未输入apiid，就以原始参数为准
        else:
            step = TestStep(step_name=name, case_step_index=index, testcase_id=caseId, interface_id=apiId,
                            step_api_path=path, step_api_method=method, step_api_header=header, step_api_data=data,
                            step_api_extract=extract, step_api_assert=judge, set_up_case=dependencyCaseId)
            try:
                db.session.add(step)
                db.session.commit()
                return jsonify({
                    'code': 10000,
                    'msg': '提交casestep成功！'
                })
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    "code": 99999,
                    'msg': '提交casestep失败！'
                })


@teststep.route('edit', methods=['POST'])
@auth_token.login_required
def editStep():
    requestParam = request.form
    id = requestParam.get("stepId")
    lock = Lock()
    lock.acquire()
    step: TestStep = TestStep.query.filter(TestStep.id == id).first()
    if not notEmpty(step):
        return jsonify({
            "code": 99999,
            'msg': "step不存在！"
        })
    name = requestParam.get("stepName")
    index = requestParam.get("stepIndex")
    caseId = requestParam.get("testcaseId")
    apiId = None if requestParam.get("interfaceId") == "" else requestParam.get("interfaceId")
    path = requestParam.get("stepApiPath")
    method = requestParam.get("stepApiMeth")
    header = str2Dict(requestParam.get("stepApiHeader")) if requestParam.get("stepApiHeader") else \
        requestParam.get("stepApiHeader")
    data = str2Dict(requestParam.get("stepApiData")) if requestParam.get("stepApiData") else requestParam.get(
        "stepApiData")
    extract = str2Dict(requestParam.get("stepApiExtra")) if requestParam.get("stepApiExtra") else None
    if requestParam.get("stepApiAssert"):
        try:
            judge = json.loads(requestParam.get("stepApiAssert"))
        except Exception as e:
            judge = str2Dict(requestParam.get("stepApiAssert"))
    else:
        judge = None
    dependencyCase = requestParam.get("dependencyCase")
    try:
        dependencyCaseId = int(dependencyCase)
    except:
        if dependencyCase:
            dependencyCaseId = Testcase.query.filter(Testcase.case_name.like(f"%{dependencyCase}%")).order_by(
                Testcase.id.desc()).first().id
        else:
            dependencyCaseId = None
    step.step_name = name
    step.case_step_index = index
    step.testcase_id = caseId
    step.set_up_case = dependencyCaseId
    api = None
    if apiId:
        api = Interface.query.filter(Interface.id == apiId).first()
    if notEmpty(api):
        step.step_api_path = api.interface_url
        step.step_api_method = api.interface_meth
        step.step_api_header = api.interface_headers
        step.step_api_data = api.interface_param
        step.step_api_extract = extract
        step.step_api_assert = judge
        try:
            db.session.add(step)
            db.session.commit()
            lock.release()
            return jsonify({
                "code": 10000,
                'msg': "编辑成功！"
            })
        except:
            db.session.rollback()
            lock.release()
            return jsonify({
                'code': 99999,
                'msg': "编辑失败！"
            })
    else:
        step.step_api_path = path
        step.step_api_method = method
        step.step_api_header = header
        step.step_api_data = data
        step.step_api_extract = extract
        step.step_api_assert = judge
        try:
            db.session.add(step)
            db.session.commit()
            lock.release()  # 执行失败释放锁
            return jsonify({
                "code": 10000,
                'msg': "编辑成功！"
            })
        except Exception as e:
            db.session.rollback()
            # 执行失败，也需要释放锁
            lock.release()
            return jsonify({
                'code': 99999,
                'msg': "编辑失败！"
            })


@teststep.route("/caseStep", methods=["get"])
@auth_token.login_required
def caseStep():
    requestParams = request.args
    caseId = int(requestParams.get("caseId")) or None
    if caseId:
        step = TestStep.query.filter(and_(TestStep.testcase_id == caseId, TestStep.delete_at == None)).order_by(
            TestStep.case_step_index.asc()).all()
        if len(step) == 0:
            return jsonify({
                "code": 10000,
                'msg': "当前用例没有step",
                "data": {
                    "list": None,
                    "total": 0
                }
            })
        else:
            return jsonify({
                "code": 10000,
                "msg": "success",
                "data": {
                    "list": list(map(lambda x: x.to_dict(), step)),
                    "total": len(step)
                }
            })
    else:
        return jsonify({
            "code": 99999,
            "msg": "缺少参数caseId",
            "data": {
                "list": None,
                "total": 0
            }
        })


@teststep.route('/deleteStep', methods=["post"])
@auth_token.login_required
def deleteStep():
    """
    逻辑删除step
    删除step需要同步更新同属case的step_index，step_index在执行/交换step顺序的时候会用到
    :return: Response
    """
    stepId = request.form.get("stepId")
    if not stepId:
        return jsonify({
            "code": 99999,
            "msg": "参数缺失",
            "data": None
        })
    else:
        try:
            step: TestStep = TestStep.query.filter(and_(TestStep.id == int(stepId), TestStep.delete_at == None)).first()
            if not step:
                return jsonify({
                    "code": 99999,
                    "msg": "该step不存在！",
                    "data": None
                })
            caseId = step.testcase_id
            step.delete_at = datetime.now()
            try:
                db.session.add(step)
                db.session.commit()
                return jsonify({
                    "code": 10000,
                    "msg": "success",
                    "data": None
                })
            except:
                db.session.rollback()
            finally:
                testStepObserver.send("deleteStep", caseId=caseId)
        except:
            pass


@teststep.route('/exchange', methods=["post"])
def exchange():
    """
    调整顺序
    :param caseId: 用例id
    :param stepId: 步骤id
    :param behavior: 行为，up/down
    :return:
    """
    params = request.form
    caseId = int(params.get("caseId")) or None
    stepId = int(params.get("stepId")) or None
    behavior: str = params.get("beh") or None
    if not notEmpty(caseId, stepId, behavior):
        return jsonify({
            "code": 99999,
            "msg": f"参数缺失，caseId:{caseId},stepId:{stepId}, behavior:{behavior}"
        })
    # 获取case的steps，根据step index顺序返回
    Tstep = TestStep.query.filter(and_(TestStep.testcase_id == caseId, TestStep.delete_at == None)).order_by(
        TestStep.case_step_index.asc()).all()
    linkList = [step.id for step in Tstep]
    if not stepId in linkList:
        return jsonify({
            "code": 99998,
            "msg": f"case中未找到step:{stepId}"
        })
    if behavior.strip().lower() == "up":
        # 表示当前用例需要往前调整,那么 step index减小
        step = linkList.index(stepId)
        currentStep: TestStep = TestStep.query.filter(TestStep.id == stepId).first()
        # next step的stepIndex增加
        nextStepId = linkList[step - 1]
        nextStep: TestStep = TestStep.query.filter(TestStep.id == nextStepId).first()
        currentStep.case_step_index, nextStep.case_step_index = nextStep.case_step_index, currentStep.case_step_index
    elif behavior.strip().lower() == "down":
        # 表示当前用例需要往前调整,那么 step index减小
        step = linkList.index(stepId)
        currentStep: TestStep = TestStep.query.filter(TestStep.id == stepId).first()
        # next step的stepIndex增加
        nextStepId = linkList[step + 1]
        nextStep: TestStep = TestStep.query.filter(TestStep.id == nextStepId).first()
        currentStep.case_step_index, nextStep.case_step_index = nextStep.case_step_index, currentStep.case_step_index
    try:
        db.session.add(currentStep)
        db.session.add(nextStep)
        db.session.commit()
        return jsonify({
            "code": 10000,
            "msg": "success"
        })
    except:
        db.session.rollback()
        return jsonify({
            "code": 99999,
            "msg": "更新失败"
        })


@teststep.route("/externalFunction", methods=["get"])
def getFunction():
    return jsonify({
        "code": "10000",
        "msg": "success",
        "data": getExternalFunctionDescMap()
    })
