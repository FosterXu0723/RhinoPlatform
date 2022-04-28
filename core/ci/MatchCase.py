"""
@File: MatchCase.py
@author: yangwuxie
@date: 2021/9/6
"""
from typing import List
from app import create_app, db
from app.models import TestStep, Task, Testcase
from app import scheduler
from app.task.tasks import taskCase
from datetime import datetime, timedelta
from .ProgramEnum import ProgramEnum
import sys


def matchApi(program: str) -> List[TestStep]:
    """
    根据工程匹配api，需要将工程名称转换成正常路由中使用的名称
    :param program: 工程名称
    :return: 返回跟当前program有关联的接口列表
    """
    upperStr = program.strip().upper() if program is not None else ""
    if upperStr not in ProgramEnum.__members__.keys():
        return []
    while create_app().app_context():
        relationApi = []
        allApi = TestStep.query.filter(TestStep.delete_at == None).all()
        collectionApis = iter(allApi)
        while True:
            try:
                step: TestStep = next(collectionApis)
                reqPath = step.step_api_path
                if ProgramEnum.get(upperStr) in reqPath.split("/"):
                    # 过滤无效case
                    if filterCase(Testcase.query.filter(Testcase.id == step.testcase_id).first()):
                        relationApi.append(step)
                else:
                    continue
            except StopIteration:
                break
        return relationApi


def filterCase(case):
    if not case:  # 入参为空直接返回False
        return False
    return case.open_status == 1


def matchCase(apiList: List) -> List:
    """
    根据api匹配case
    :param apiList: 获取到的关联工程的api
    :return: 与工程相关联的case id组成的集合
    """
    if not isinstance(apiList, (list, tuple)):
        return []
    res = [st.testcase_id for st in apiList]
    return list(set(res))


def addOnceTask(caseIds: List[int], program: str):
    """
    新增一次性任务
    :return:
    """
    taskName = program + datetime.now().strftime("%Y%m%d%H%M")
    # 外层的flask应用已经启动scheduler，这边不再次启动scheduler的时候，会被scheduler底层认为当前是stop状态，导致job无法正常录入
    # if self.state == STATE_STOPPED:   所以这边手动启动一下
    scheduler.start()
    scheduler.add_job(id=taskName, func=taskCase, trigger="date",
                      run_date=(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
                      replace_existing=True,
                      kwargs={"caseIds": caseIds, "taskName": taskName})
    task = Task(task_name=taskName, task_type="date", task_start=scheduler.get_job(taskName).next_run_time)
    try:
        db.session.add(task)
        db.session.commit()
    except:
        db.session.rollback()


def main(programName):
    """
    触发执行task
    :param programName: 项目名称
    :return:
    """
    caseIds = matchCase(matchApi(programName))
    addOnceTask(caseIds=caseIds, program=programName)


if __name__ == '__main__':
    # if len(sys.argv[1:]) != 1:
    #     print('只支持一个参数')
    # else:
    #     main(sys.argv[1])
    pass
