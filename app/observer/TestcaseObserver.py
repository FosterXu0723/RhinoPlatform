"""
@File: TestcaseObserver.py
@author: guoweiliang
@date: 2021/8/6
"""
from sqlalchemy import and_
from app import db
from app.models import TestStep
from app.observer import mySignal

testStepObserver = mySignal.signal("testStepObserver")


@testStepObserver.connect
def updateCaseStepIndex(sender, **kwargs):
    """
    step被删除之后，异步处理同case的step index
    :param sender:
    :param kwargs:
    :return:
    """
    caseId = kwargs.get("caseId")
    steps = TestStep.query.filter(and_(TestStep.testcase_id == caseId, TestStep.delete_at == None)).order_by(
        TestStep.case_step_index.asc()).all()
    if len(steps) == 0:
        return
    else:
        # 重写case中的step index
        stepIndex = 1
        chainStep = []
        for step in steps:
            step.case_step_index = stepIndex
            stepIndex += 1
            chainStep.append(step)
        db.session.add_all(chainStep)
        db.session.commit()