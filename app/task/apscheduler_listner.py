"""
@File: apscheduler_listner.py
@author: guoweiliang
@date: 2022/2/8
"""
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.triggers.cron import CronTrigger


def error_listener():
    pass


class MyTrigger(CronTrigger):


    @classmethod
    def from_crontab(cls, expr, timezone=None):
        values = expr.split()
        if len(values) != 7:
            raise ValueError('Wrong number of fields; got {}, expected 7'.format(len(values)))

        return cls(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                   year=values[6], timezone=timezone)
