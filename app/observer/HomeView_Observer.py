"""
@File: HomeView_Observer.py
@author: xiaoyicai
@date: 2021/6/11
"""
from common.Log import log
from . import mySignal
from app.models import HomeView
from app import db, create_app

homeviewResult = mySignal.signal('homeviewResult')


@homeviewResult.connect
def homeview(sender, **kwargs):
    log.info('开始插入数据---------------------------------------------')
    log.info(f"任务参数{sender},{kwargs}")
    # if sender or sender == "success":

    if kwargs.get("taskId"):
        result = HomeView(projectId=kwargs.get('projectId'), projectName=kwargs.get('projectName'),
                          taskId=kwargs.get('taskId'),
                          taskName=kwargs.get('taskName'), successTotal=kwargs.get('successTotal'),
                          failTotal=kwargs.get('failTotal'),
                          total=kwargs.get('total'), passRate=kwargs.get('passRate'))

        log.info('【homeviewResult】插入任务:{} {}的统计结果'.format(kwargs.get('taskId'), kwargs.get('taskName')))
        try:
            db.session.add(result)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
