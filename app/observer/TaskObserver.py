"""
@File: TaskObserver.py
@author: guoweiliang
@date: 2021/6/7
"""
from datetime import datetime
from itertools import groupby
from typing import List, Dict

from app.observer import mySignal
from app import scheduler, db, create_app
from app.models import Task, TaskCase, Testcase, CaseResult
from common.Log import log
import traceback

from core.notice.DIngtalkNotice import sendMsg

taskStartObserver = mySignal.signal("taskStartObserver")
taskCaseUpdateObserver = mySignal.signal("taskCaseUpdateObserver")


@taskStartObserver.connect
def updateNextTime(sender, **kwargs):
    """
    当task执行之后需要跟新下一次执行时间
    :param sender: 发送者
    :param kwargs: 参数
    :return:
    """
    taskName = kwargs.get("taskName")
    job = scheduler.get_job(taskName)
    # 表示job类型为date
    if not job:
        task: Task = Task.query.filter(Task.task_name == taskName).first()
        task.task_status = False
        db.session.add(task)
        db.session.commit()
        log.warn("【任务结束】观察者模式更新任务:{} 为关闭状态".format(taskName))

        # 发送钉钉消息 通过sender判断当前状态
        if sender == "end":
            log.info("执行发送钉钉消息代码")
            results: List[CaseResult] = CaseResult.query.filter(CaseResult.caseTask == task.id).all()
            failedCases: List[CaseResult] = list(filter(lambda res: res.caseFlag == False, results))
            authorFailCaseDict: Dict[str: List[str]] = {}
            for failItem in failedCases:
                case: Testcase = Testcase.query.filter(Testcase.id == failItem.caseId).first()
                if case:
                    # if case.author in authorFailCaseDict.keys():
                    #     authorFailCaseDict[case.author or "暂无创建者"].append(case.case_name)
                    # else:
                    #     authorFailCaseDict[case.author or "暂无创建者"] = []
                    # authorFailCaseDict[case.author or "暂无创建者"].append(case.case_name)
                    authorFailCaseDict.setdefault(case.author or "暂无创建者", []).append(case.case_name)

            ddContent = f"""#### 项目名: {taskName} \n#### 项目分支: test_using \n> | 创建人 | 失败用例 |\n| :----: | :----: |\n"""
            for key, value in authorFailCaseDict.items():
                ddContent += f"| {key} | &nbsp; &nbsp; &nbsp; &nbsp;  {value} | \n"
            sendMsg(title=taskName + "test_using执行报告", msg=ddContent)
    else:  # 表示是interval
        try:
            nextRuntime = job.next_run_time
            task: Task = Task.query.filter(Task.task_name == taskName).first()
            task.task_start = nextRuntime
            task.update_at = datetime.now()
            db.session.add(task)
            db.session.commit()
            log.info("【更新时间】观察者模式更新任务:{}时间成功".format(taskName))
        except AttributeError:
            log.error("【更新任务】出现错误：", str(traceback.format_exc()))


@taskCaseUpdateObserver.connect
def updateTaskCase(sender, **kwargs):
    """
    当任务关联的项目新增/删除case时执行
    kwargs:
        case id
        type: add/remove
    :return:
    """
    case = kwargs.get("caseId") or None
    # 删除case的处理逻辑
    if sender and sender == "remove":
        if not case:
            log.warn("【taskCaseUpdateObserver更新任务】未提供case id，无法更新对应任务的关联用例")
        else:
            case = int(case)
            testcase = Testcase.query.filter(Testcase.id == case).first()
            if testcase:
                if not Testcase.tasks:
                    log.info("【taskCaseUpdateObserver更新任务】当前case没有关联任务，不需要更新！")
                else:
                    for task in testcase.tasks:
                        task.task_cases.remove(testcase)
                        db.session.commit()
            else:
                log.error("【taskCaseUpdateObserver更新任务】id对应的用例不存在！")
    else:  # 新增case的处理逻辑
        pass
