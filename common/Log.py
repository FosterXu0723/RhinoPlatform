"""
@File:Log.py
@author:yangwuxie
@date: 2021/01/21
"""
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


class Log(object):

    def __init__(self):
        if sys.platform == 'darwin' or sys.platform == 'linux':
            self.log_path = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'logs')
            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)
        else:
            self.log_path = os.path.join(os.path.split(os.path.dirname(__file__))[0].replace("/", "\\"), 'logs')
        self.logFileName = "platform.log"


    def getLogger(self):
        log = logging.getLogger("platform")
        if not log.handlers:
            log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
            formatter = logging.Formatter(log_fmt)
            log_file_handler = TimedRotatingFileHandler(
                filename=os.path.join(self.log_path, self.logFileName), when="D", interval=1,
                backupCount=14)
            log_file_handler.setFormatter(formatter)
            logging.basicConfig(level=logging.DEBUG)
            log.addHandler(log_file_handler)
            return log

    def getErrorLogger(self):
        log = logging.getLogger("platform.error")
        if not log.handlers:
            log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
            formatter = logging.Formatter(log_fmt)
            log_file_handler = TimedRotatingFileHandler(
                filename=os.path.join(self.log_path, "error.log"), when="D", interval=1,
                backupCount=14)
            log_file_handler.setFormatter(formatter)
            logging.basicConfig(level=logging.DEBUG)
            log.addHandler(log_file_handler)
            return log


log = Log().getLogger()

errorLog = Log().getErrorLogger()
if __name__ == '__main__':
    log.info('test11')

