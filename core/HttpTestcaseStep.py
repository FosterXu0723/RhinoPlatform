"""
@File:HttpTestcaseStep.py
@author:yangwuxie
@date: 2021/01/05
"""
import json
import operator
from json import JSONDecodeError

from app.models import TestStep
from app.utils import notEmpty
from app.utils.DbQuery import DbQuery
from core.RequestClient import Client
from core.Judgement import Judgement
from common.Log import log
from error_message import RequestFailException

"""
api  testcase（teststep（api））执行的时候调用
写入数据库的时候不需要调用这边的东西
会有相对应的模型负责写入
执行用例的时候调用这边
"""


class HttpTestcaseStep(Client):
    """
    用例步骤类
    """

    def __init__(self, caseStep: TestStep):
        super().__init__(caseStep)

    def execute(self, env) -> set:
        """
        执行http请求
        :param env: 请求环境
        :return: 返回断言结果，和通过状态
        """
        try:
            self.setUpRequest()
            if operator.eq(str(self.method).lower(), "get"):
                log.info(f"【执行接口请求】 url:{self.path}， data:{self.data}， header:{self.header}")
                resp = self.get(url=env.get("projectHost") + self.path.strip(), params=self.data, header=self.header)
            else:
                log.info(f"【执行接口请求】 url:{self.path}， data:{self.data}， header:{self.header}")
                resp = self.post(url=env.get("projectHost") + self.path.strip(), params=self.data, header=self.header)
            try:
                self.doExtract(json.loads(resp.text))
                log.info("【响应内容】:{}".format(resp.text))
                log.info("【提取参数】:{}".format(self.extract or "暂无"))
                if self.ast:
                    judge = Judgement(self.ast, resp)
                    # 当需要对db做校验的时候才执行
                    if not hasattr(judge, "db") and "assertDb" in self.ast:
                        setattr(judge, "db", DbQuery(host=env.get("projectDbUrl"),
                                                     user=env.get("projectDbUser"),
                                                     pwd=env.get("projectDbPassword"),
                                                     db=env.get("projectDbName"),
                                                     port=env.get("projectDbPort")
                                                     ))

                    return judge.doJudge()
                else:
                    return ["该step暂未设置断言内容，默认通过"], True
            except (JSONDecodeError, TypeError, AttributeError):  # 处理status_code不等于200的情况
                return ["请求出现异常，"], False
        except RequestFailException:
            return [], False


    def setUpRequest(self):
        """
        前置处理
        :return:
        """
        if self._isContainsFunc(self.header) or self._checkReplace(self.header):
            self.header = self.doReplace(self.header)
            self.header = self.proccessExternalFunc(self.header)
        if self._isContainsFunc(self.data) or self._checkReplace(self.data):
            self.data = self.doReplace(self.data)
            self.data = self.proccessExternalFunc(self.data)
