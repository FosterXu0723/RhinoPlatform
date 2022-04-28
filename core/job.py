"""
@File: job.py
@author: guoweiliang
@date: 2021/5/8
"""
from apscheduler.triggers.combining import AndTrigger
from flask import current_app

from app import scheduler
from common.Log import log


# @scheduler.task(trigger="interval", id="test_job", seconds=3)
# def job():
#     log.info("start job!")


class APSchedule():

    def addJob(self, jobId, func, args, **kwargs):
        """
        添加任务
        :param jobId:job唯一标识
        :param func: 方法
        :param args:
        :param kwargs:
        :return:
        """
        jobDef = dict(kwargs)
        jobDef['id'] = jobId
        jobDef['func'] = func
        jobDef['args'] = args
        jobDef = self.fixJobDef(jobDef)
        self.removeJob(jobId)

    def fixJobDef(self, jobDef):
        """
        维修job工程
        :param jobDef:job definition
        :return:
        """
        if jobDef.get("trigger") == 'date':
            jobDef['run_date'] = jobDef.get('run_date') or None
        elif jobDef.get("trigger") == 'cron':
            jobDef['hour'] = jobDef.get('hour') or "*"
            jobDef['minute'] = jobDef.get('minute') or "*"
            jobDef['week'] = jobDef.get('week') or "*"
            jobDef['day'] = jobDef.get('day') or "*"
            jobDef['month'] = jobDef.get('month') or "*"
        elif jobDef.get('trigger') == 'interval':
            jobDef['seconds'] = jobDef.get('seconds') or "*"
        else:
            if jobDef.get("andTri"):
                jobDef['trigger'] = AndTrigger([jobDef.pop("andTri", None), ])
        return jobDef

    def removeJob(self, jobId, jobStore=None):
        """
        删除工程
        :param jobId:
        :param jobStore:
        :return:
        """
        scheduler.remove_job(jobId, jobstore=jobStore)

    def resumeJob(self, jobId, jobStore=None):
        """
        恢复工程
        :param jobId:
        :param jobStore:
        :return:
        """
        scheduler.resume_job(id == jobId, jobstore=jobStore)
