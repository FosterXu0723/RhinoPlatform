# date:  2021/6/11
#  Author:  jinmu
#  Description:

from app.observer import mySignal
from app.models import ReportResult
from app.models import CaseResult
from app import db

resultReportObserver = mySignal.signal("upsertTaskResult")
from sqlalchemy import func
from common.Log import log


@resultReportObserver.connect
def resultInsert(sender, **kwargs):
    '''
    task执行完成后，统计并插入报告结果表
    :param sender:
    :param kwargs:
    :return:
    '''
    taskId = kwargs.get("taskId")
    case_task_run_index = kwargs.get("taskRunIndex")
    reportName = str(taskId) + '任务第' + str(case_task_run_index) + '次执行测试报告'
    totalCount = CaseResult.query.filter(CaseResult.caseTask == taskId,
                                         CaseResult.case_task_run_index == case_task_run_index).count()
    passCount = CaseResult.query.filter(CaseResult.caseTask == taskId,
                                        CaseResult.case_task_run_index == case_task_run_index,
                                        CaseResult.caseFlag == '1').count()
    failCount = CaseResult.query.filter(CaseResult.caseTask == taskId,
                                        CaseResult.case_task_run_index == case_task_run_index,
                                        CaseResult.caseFlag == '0').count()
    data = ReportResult(reportName=reportName, totalCount=totalCount, passCount=passCount,
                        failCount=failCount, taskId=taskId)
    try:
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        log.info('插入数据库失败-{}'.format(e))
        db.session.rollback()
