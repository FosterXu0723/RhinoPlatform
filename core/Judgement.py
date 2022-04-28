"""
@File:Judgement.py
@author:yangwuxie
@date: 2021/01/21
"""
import json
import operator
from typing import Dict, AnyStr, overload
from requests import Response
import ast

from app.utils.JsonTools import unest
from app.utils.RequestParamsUtils import str2Dict
from enum import Enum
from common.Log import log
from error_message import EnumKeyNotFoundException, JudgeMethodNotAllowedException
from collections import OrderedDict


class Judgement(object):

    def __init__(self, exception: Dict, respContent: Response):
        self.exception = exception
        self.resp = respContent
        self.vtDict = self.getValueTypeDict()

    def doJudge(self):
        """
        断言方法，当又一个断言失败则把case标记成失败
        :return: 断言的内容，断言的状态
        """
        judgeResult = []
        judgeFlag = True
        for waitJudge, typeInstance in self.vtDict.items():
            log.info(f"【断言】断言类型为:{typeInstance},断言内容为:{waitJudge}")
            if isinstance(typeInstance, DbAssertImpl):
                # 将db对象赋值给db类型校验对象
                setattr(typeInstance, "db", self.db)
            judgeResult.append(typeInstance.judge(waitJudge, self.resp))
        for assertResult in judgeResult:
            if operator.contains(assertResult, "断言失败"):
                judgeFlag = False
                break
        return judgeResult, judgeFlag

    def getValueTypeDict(self) -> OrderedDict:
        """
        获取断言内容和断言对象函数
        :return: 断言内容-断言对象
        """
        exceptionValueTypeDict = OrderedDict()
        for key in self.exception.keys():
            try:
                # 当类型为db的时候，self.expect的value为dict类型，需要特殊处理一下
                exceptionValueTypeDict[str(self.exception[key])] = TypeEnum.getTypeInstance(key)
            except Exception as e:
                log.error(f"提供的断言类型不支持！{e}")
                raise JudgeMethodNotAllowedException("断言类型暂不支持！")
        return exceptionValueTypeDict


class JudgeType(object):

    def judge(self, expect, result):
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class JudgeInImpl(JudgeType):

    def judge(self, expect: AnyStr, result: Response):
        """
        兼容断言多个字段的情况
        :param expect: 单个str或多个str，str,str
        :param result:
        :return:
        """
        waitJudgeList = expect.split(",")
        if len(waitJudgeList) == 1:
            if expect.strip() in result.text:
                log.info(f"响应内容中存在{expect}，断言成功")
                return f'响应内容中存在{expect}，断言成功'
            else:
                log.error(f"响应内容中存在{expect},断言失败")
                return f"响应内容中存在{expect}，断言失败"
        # 断言内容为多个
        judgeResultMap = {}
        for judge in waitJudgeList:
            judgeResultMap[judge] = True if judge.strip() in result.text else False
        judgeFailedList = []
        if operator.contains(judgeResultMap.values(), False):
            for key, value in judgeResultMap.items():
                if not judgeResultMap[key]:
                    judgeFailedList.append(key)
            log.error(f"响应内容中存在{judgeFailedList}，断言失败")
            return f"响应内容中存在{judgeFailedList}，断言失败！"
        else:
            log.info(f"响应内容中存在{waitJudgeList}，断言成功")
            return f"响应内容中存在{waitJudgeList}，断言成功"


class JudgeNotInImpl(JudgeType):

    def judge(self, expect: AnyStr, result: Response):
        return f'响应内容中不存在{expect}，断言成功' if expect.strip() not in result.text else f"响应内容中不存在{expect}，断言失败"


class JudgeEqualsImpl(JudgeType):

    def judge(self, expect: dict, result: Response):
        """
        采用dict的形式
        :param expect:
        :param result:
        :return:
        """
        judgeResultList = []
        try:
            exceptionDict = ast.literal_eval(expect)
            for key, value in exceptionDict.items():
                if operator.eq(key, "statusCode"):
                    if exceptionDict.get(key) == result.status_code:
                        log.info("响应状态码断言成功！")
                        continue
                    else:
                        log.error("响应状态码断言失败！")
                        return f"{result.text} 对应的状态码不等于预期"
                try:
                    resValue = unest(result.json(), key)
                    if value == resValue or value.lower() == resValue.lower():
                        log.info(f'{key}:{value}断言成功')
                        judgeResultList.append(f'{key}:{value}断言成功')
                    else:
                        log.error(f"{key}:{value}断言失败")
                        return f"{key}:{value}断言失败"
                except:
                    log.error(f'接口响应中找不到{key}')
                    return f"断言失败，接口响应中找不到{key}"
        except Exception as e:
            strDict = str2Dict(expect)
            for key, value in strDict.items():
                if operator.eq(key, "statusCode"):
                    if strDict.get(key) == result.status_code:
                        log.info("响应状态码断言成功！")
                        continue
                    else:
                        log.error("响应状态码断言失败！")
                        return f"{result.text} 对应的状态码不等于预期"
                try:
                    resValue = unest(json.loads(result.text), key)
                    if value == resValue:
                        log.info(f'{key}:{value}断言成功')
                        judgeResultList.append(f'{key}:{value}断言成功')
                    else:
                        log.error(f"{key}:{value}断言失败")
                        return f"{key}:{value}断言失败"
                except:
                    log.error(f'接口响应中找不到{key}')
                    return f"断言失败，接口响应中找不到{key}"
        return "、".join(judgeResultList)


class JudgeNotEqualsImpl(JudgeType):

    def judge(self, expect: AnyStr, result: Response):
        """
        断言不等于
        :param expect: key:value,key=value
        :param result:
        :return:
        """
        try:
            exceptionDict = ast.literal_eval(expect)
            for key, value in exceptionDict.items():
                realValue = unest(result.json(), key)
                if not realValue:
                    log.warn(f"响应:{result.text}中不存在要检查的key:{key}")
                if value != realValue:
                    log.info(f"{key}:{value}断言成功")
                    return f"{key}:{value}断言成功"
                else:
                    log.error(f"{key}:{value}断言失败")
                    return f"{key}:{value}断言失败"
        except Exception:
            exceptionDict = str2Dict(expect)
            for key, value in exceptionDict.items():
                realValue = eval(result.text).get(key)
                if not realValue:
                    log.warn(f"响应:{result.text}中不存在要检查的key:{key}")
                if value != realValue:
                    log.info(f"{key}:{value}断言成功")
                    return f"{key}:{value}断言成功"
                else:
                    log.error(f"{key}:{value}断言失败")
                    return f"{key}:{value}断言失败"


class DbAssertImpl(JudgeType):
    """
    查询db，断言结果，查询到内容->断言成功 没有查询到内容->断言失败
    """

    def judge(self, expect: AnyStr, result: Response):
        if not hasattr(self, "db"):
            raise AttributeError("db对象不存在！")
        try:
            expectDict = ast.literal_eval(expect)
        except:
            expectDict = str2Dict(expect)
        finally:
            res = self.db.query(expectDict)
            if res == 0:
                return "db 断言失败"
            else:
                return "db 断言成功"


class TypeEnum(Enum):
    """
    断言类型和断言对象枚举
    """
    assertIn = JudgeInImpl()
    assertNotIn = JudgeNotInImpl()
    assertEquals = JudgeEqualsImpl()
    assertNotEquals = JudgeNotEqualsImpl()
    assertDb = DbAssertImpl()

    @staticmethod
    def getTypeInstance(typeName):
        """
        根据断言类型获取的断言对象
        :param typeName: 断言类型名称
        :return: 断言对象
        """
        try:
            instance = TypeEnum.__members__[typeName].value
            return instance
        except Exception:
            raise EnumKeyNotFoundException()
