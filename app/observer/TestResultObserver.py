"""
@File: TestResultObserver.py
@author: guoweiliang
@date: 2021/5/11
"""
import json

from common.Log import log
from . import mySignal
from app.models import CaseResult
from app import db, create_app
from datetime import datetime

upsertTestResult = mySignal.signal("upsertTestResult")


@upsertTestResult.connect
def upsertRecord(sender, **kwargs):
    """
    执行成功之后插入数据
    :param sender:
    :param kwargs:
    :return:
    """
    result = None

    # if sender == "success" or sender:
    if not kwargs.get("taskId"):
        result = CaseResult(caseId=kwargs.get("caseId"),
                            assertResult=json.dumps(kwargs.get("result"), ensure_ascii=False),
                            create_at=datetime.now(), caseTask=None, case_task_run_index=None, caseFlag=sender)
        log.info(f"【upsertTestResult】插入{kwargs.get('caseId')}非任务执行结果")
    else:
        result = CaseResult(caseId=kwargs.get("caseId"),
                            assertResult=json.dumps(kwargs.get("result"), ensure_ascii=False), caseFlag=sender,
                            create_at=datetime.now(),
                            caseTask=kwargs.get("taskId"), case_task_run_index=kwargs.get("taskRunIndex"))
        log.info(f"【upsertTestResult】插入case id:{kwargs.get('caseId')}任务执行结果")
    db.session.add(result)
    db.session.commit()
