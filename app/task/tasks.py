"""
@File: tasks.py
@author: guoweiliang
@date: 2021/5/28
"""
import re

from app.observer.TaskObserver import taskStartObserver
from app import db, create_app
from app.models import Project, Testcase, TestStep, TaskResult, Task, ProjectEnv, CaseResult
from sqlalchemy import and_

from app.observer.TestResultObserver import upsertTestResult
from app.observer.HomeView_Observer import homeviewResult
from core.HttpTestcaseStep import HttpTestcaseStep
from common.Log import log

from app.observer.resultReportObserver import resultReportObserver

import time

"""
任务文件
当前文件没有一个app存在，出现报错No application found. Either work inside a view function or push an application context.
可以通过使用app.app_context解决app的上下文环境
"""

taskApp = create_app()


def taskCase(**kwargs: dict):
    """
    执行case
    :param kwargs: caseIds或者 projectId
        caseIds需要处理成list
    :return:
    """

    with taskApp.app_context():
        log.info("【任务开始】开始执行定时任务{}".format(kwargs.get("taskName")))
        task: Task = Task.query.filter(Task.task_name == kwargs.get("taskName")).first()

        # 观察者模式发送消息，更新下次执行时间
        taskStartObserver.send("start", taskName=kwargs.get("taskName"))

        # 根据TaskResult的name判断第几次执行
        taskRt: CaseResult = CaseResult.query.filter(CaseResult.caseTask == task.id).order_by(
            CaseResult.case_task_run_index.desc()).first()
        if not taskRt or not taskRt.case_task_run_index:  # 表示第一次执行任务
            taskIndex = 1
        else:
            taskIndex = taskRt.case_task_run_index + 1
        # 判断携带的参数是什么
        if kwargs.get("projectId"):
            first: Project = Project.query.filter(
                and_(Project.id == int(kwargs.get("projectId")), Project.status == True)).first()
            testcases = Testcase.query.filter(
                and_(Testcase.projects_id == first.id, Testcase.open_status == True)).all()
        else:
            # 表示写入的是caseIds
            testcases = list(
                map(lambda x: Testcase.query.filter(and_(Testcase.id == x), Testcase.open_status == True).first(),
                    map(lambda caseId: int(caseId), kwargs.get("caseIds"))))
        iterCases = iter(testcases)
        successTotal = 0
        failTotal = 0

        #  采用迭代器的方式
        while True:
            try:

                case: Testcase = next(iterCases)
                # 获取当前case的所属执行环境
                env: ProjectEnv = Project.query.filter(Project.id == case.projects_id).first().env.first()
                caseSuccessFlag = True  # case执行成功标识
                caseSteps = case.steps.all()
                # 记录步骤的断言结果
                stepAssertDict = dict()
                # 循环执行用例的step, 循环结束表示case执行完成
                for step in caseSteps:
                    if step.set_up_case:  # 步骤的前置依赖，全都是依赖于case
                        # 执行依赖
                        dependencyCaseId = step.set_up_case
                        dependencyCaseSteps = TestStep.query.filter(
                            and_(TestStep.testcase_id == dependencyCaseId, TestStep.delete_at == None)).all()
                        if len(dependencyCaseSteps) > 0:  # 当依赖用例大于0的时候执行
                            dependencyProjectId = Testcase.query.filter(
                                Testcase.id == dependencyCaseId).first().projects_id
                            dependencyEnv = Project.query.filter_by(
                                id=dependencyProjectId).first().env.first().to_dict()
                            # 循环执行依赖case的step
                            for dependencyStep in dependencyCaseSteps:
                                dependencyStepResult, dependencyStepFlag = HttpTestcaseStep(dependencyStep).execute(
                                    dependencyEnv.to_dict())
                                if not dependencyStepFlag:  # 依赖用例的断言失败
                                    caseSuccessFlag = False
                                    # 执行失败直接跳过用例执行
                                    break
                    # 执行step
                    judgeResult, judgeFlag = HttpTestcaseStep(step).execute(env.to_dict())
                    stepAssertDict[step.id] = judgeResult
                    if not judgeFlag:
                        # 执行失败
                        caseSuccessFlag = False
                        # failTotal = failTotal + 1
                        break

                # 循环结束之后再去统计case执行情况
                if caseSuccessFlag:
                    successTotal += 1
                else:
                    failTotal += 1

                upsertTestResult.send(caseSuccessFlag, caseId=case.id, result=stepAssertDict, taskId=task.id,
                                      taskRunIndex=taskIndex)
            except StopIteration:
                # 统计，计算成功率
                log.info("case执行完毕，统计结果！")
                total = successTotal + failTotal
                # todo total为0 的情况
                passRate = successTotal / total
                passRate = round(passRate, 1)

                # 观察者模式发送消息，更新下次执行时间
                taskStartObserver.send("end", taskName=kwargs.get("taskName"))
                # todo first参数在这边作用于里面拿不到
                log.info('成功数为 {}  失败数为 {} 通过率为 {}  总数为 {}'.format(successTotal, failTotal, passRate, total))
                homeviewResult.send(caseSuccessFlag, projectId=first.id, projectName=first.project_name,
                                    taskId=task.id,
                                    taskName=task.task_name, successTotal=successTotal, failTotal=failTotal,
                                    total=total,
                                    passRate=passRate)

                break


        resultReportObserver.send(taskRunIndex=taskIndex, taskId=task.id)

if __name__ == '__main__':
    taskCase(caseIds=[2,3,4,5], taskName="dalaran202110181456")
