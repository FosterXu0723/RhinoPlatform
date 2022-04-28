# !/usr/bin/python
# encoding: utf-8
"""
@File:BatchTranlateYml.py
@author:yangwuxie
@date: 2021/03/18
"""

import argparse
import ast
import operator
import re
import sys
from enum import Enum
from ruamel import yaml
import yaml
import os
import asyncio
from app import db
from app.models import Testcase, TestStep

from common.Log import log
from error_message import JudgeMethodNotAllowedException, TransferException

"""
    批量转化yml文件
"""

_assetToJudgeMap = {"assert_kes_value": "assertEquals",
                    "expected_code": "assertEquals",
                    "assert_key_exists": "assertIn",
                    "assert_in_text": "assertIn",
                    "assert_db": "assertDb"}


class AssertTypeEnum(Enum):
    ASSERT_KES_VALUE = "assert_kes_value"
    EXPECTED_CODE = "expected_code"
    ASSERT_KEY_EXISTS = "assert_key_exists"
    ASSERT_IN_TEXT = "assert_in_text"

    @staticmethod
    def getMapValue(key):
        return _assetToJudgeMap[key]


def yml2testcase(ymlFile):
    """
    yml转换成testcase
    :param ymlFile: 原用例文件
    :return:
    """
    with open(ymlFile, "r",encoding='utf-8') as f:
        log.info("开始读取文件:{}".format(ymlFile))
        yamlData: dict = next(yaml.load_all(f))
        # 表示当前yaml中记录了多条case
        for case in yamlData:
            log.info("开始解析用例内容:{}".format(case))
            caseData = yamlData.get(case)
            # headersparamsvalue
            headersValue = caseData.get("headersparamsvalue")
            # dataparamsvalue
            dataValue = caseData.get("dataparamsvalue")
            # 实例化Testcase
            testcase = Testcase()
            testcase.case_name = caseData.get("casename")
            # 项目名称默认给1
            testcase.projects_id = 1
            log.info("生成Testcase实例{}".format(testcase.to_dict()))

            try:
                db.session.add(testcase)
                db.session.commit()
            except Exception:
                db.session.rollback()
                # 回滚之后剩余step也不需要写入
                log.error(f"{caseData} 组装用例写入db失败，跳过当前case")
                continue
            # 实例化TestStep
            steps = iter(getStep(caseData))
            stepIndex = 1
            while True:
                try:
                    step = next(steps)
                    # 不能根据testcase.casename获取上面新建的testcase，只能通过获取最新id的Testcase
                    first: Testcase = Testcase.query.order_by(Testcase.id.desc()).limit(1).first()
                    testStep = TestStep()
                    testStep.case_step_index = stepIndex
                    testStep.step_name = step.get("name")
                    general = step.get("general")
                    testStep.step_api_path = getPath(general.get("path"))
                    testStep.step_api_method = general.get("method")
                    testStep.step_api_header = _doReplace(step.get("headers"), headersValue)
                    testStep.step_api_data = _doReplace(step.get("data"), dataValue)
                    testStep.step_api_extract = step.get("extract")
                    testStep.step_api_assert = _convert2PlatformJudge(step.get("validate"))
                    testStep.testcase_id = first.id
                    log.info("生成testtep实例{}".format(testStep.to_dict()))
                    stepIndex += 1  # step index需要变化
                    try:
                        db.session.add(testStep)
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                        log.error(f"{step} 组装step写入db失败，跳过当前step")
                        continue
                except StopIteration:
                    log.info("转换完毕！")
                    break


def allYmlFile(rootPath, fileList=None, dirList=None):
    """
    path下全部文件
    :param rootPath:文件夹目录
    :param fileList:文件list
    :param dirList:
    :return:
    """
    dirOrFiles = os.listdir(rootPath)
    for dirFile in dirOrFiles:
        dirFilePath = os.path.join(rootPath, dirFile)
        if os.path.isdir(dirFilePath):
            dirList.append(dirFilePath)
            allYmlFile(dirFilePath, fileList, dirList)
        else:
            fileList.append(dirFilePath)
    return fileList


def getStep(content: dict) -> list:
    """
    返回step Date
    :param content:
    :return:
    """
    resultList = []
    for key, value in content.items():
        if operator.contains(key, "step"):
            resultList.append(value)
    return resultList


def getPath(fullUrl: str):
    """
    从全路径中获取API path
    :param fullUrl:
    :return:
    """
    if not fullUrl.startswith("https") or not fullUrl.startswith("http"):
        return fullUrl
    from urllib.parse import urlparse
    return urlparse(fullUrl).path


def _convert2PlatformJudge(assertion: dict) -> dict:
    """
    将API自动化框架中的断言转化成平台能够识别的断言
    :param assertion:
    :return: judgement
    assert_kes_value -> assertEquals: {key:value,key:value}
    expected_code -> assertEquals: statusCode=200
    assert_key_exists -> assertIn: str,str,str
    """
    judgementMap = {}
    log.info(f"{assertion}")
    for key, value in assertion.items():
        if operator.eq(key, AssertTypeEnum.ASSERT_KEY_EXISTS.value):
            judgementMap[AssertTypeEnum.getMapValue(key)] = value
        elif operator.eq(key, AssertTypeEnum.ASSERT_KES_VALUE.value):
            # 拿到的失败list<dict>的形式，需要转换成str
            _map = {}
            for item in value:
                _map.update(item)
            judgementMap[AssertTypeEnum.getMapValue(key)] = str(_map)
        elif operator.eq(key, AssertTypeEnum.EXPECTED_CODE.value):
            _scDict = {"statusCode": value}
            if AssertTypeEnum.getMapValue(AssertTypeEnum.ASSERT_KES_VALUE.value) not in judgementMap.keys():
                judgementMap[AssertTypeEnum.getMapValue(key)] = str(_scDict)
            # 表示已经存在assertEquals
            else:
                extendDict: dict = ast.literal_eval(judgementMap[AssertTypeEnum.getMapValue(key)])
                extendDict.update(_scDict)
                judgementMap[AssertTypeEnum.getMapValue(key)] = str(extendDict)
        elif operator.eq(key, AssertTypeEnum.ASSERT_IN_TEXT.value):
            if AssertTypeEnum.getMapValue(AssertTypeEnum.ASSERT_IN_TEXT.value) not in judgementMap.keys():
                judgementMap[AssertTypeEnum.getMapValue(key)] = value
            else:
                judgementMap[AssertTypeEnum.getMapValue(key)] += ","
                judgementMap[AssertTypeEnum.getMapValue(key)] += value
        else:
            if key not in _assetToJudgeMap.keys():
                _keyValues = {key: value}
                if AssertTypeEnum.getMapValue(AssertTypeEnum.ASSERT_KES_VALUE.value) not in judgementMap.keys():
                    judgementMap[AssertTypeEnum.getMapValue(AssertTypeEnum.ASSERT_KES_VALUE.value)] = str(_keyValues)
                # 表示已经存在assertEquals
                else:
                    extendDict: dict = ast.literal_eval(judgementMap[AssertTypeEnum.getMapValue(
                        AssertTypeEnum.ASSERT_KES_VALUE.value)])
                    extendDict.update(_keyValues)
                    judgementMap[AssertTypeEnum.getMapValue(AssertTypeEnum.ASSERT_KES_VALUE.value)] = str(extendDict)
    return judgementMap


def _convertMap2Str(content: dict) -> str:
    """
    转换dict为特定格式的内容
    :param content:
    :return:
    """
    _str = ""
    iterator = iter(content.keys())
    while True:
        try:
            key = next(iterator)
            _str += "{}={}".format(key, content.get(key))
            _str += "&"
        except StopIteration:
            copyStr = _str.rstrip("&")
            return copyStr


def doTranslate():
    loop = asyncio.get_event_loop()
    taskList = [asyncio.ensure_future(yml2testcase(file) for file in allYmlFile(""))]
    loop.run_until_complete(asyncio.wait(taskList))


def _doReplace(content, globalVars: dict):
    """
    替换参数处理，${test},把yml文件中的headers方法直接用到数据中，不再对headersparamsvalue做流程上的兼容
    :param content: 待处理参数 包含${}符号
    :param globalVars: paramsValue字段
    :return: 处理过后的内容，并且转为dict
    """
    if not globalVars or len(globalVars) == 0:
        return content
    pattern = r'\$\{.*?\}'
    json_str = str(content)
    if not _check(content):
        return content
    match_list = re.findall(pattern, json_str)
    if len(match_list) == 0:
        return eval(json_str)
    for match in match_list:
        is_change = False
        for key in globalVars.keys():
            if is_change:
                break
            dest_str_value = ""
            # 是否包含key
            if not match.__contains__(key):
                continue
            # 判断是否为str，re.sub中需要参数str
            if not isinstance(globalVars[key], str):
                dest_str_value = str(globalVars[key])
            else:
                dest_str_value = globalVars[key]
            json_str = re.sub(pattern, dest_str_value, json_str, 1)
            is_change = True
    return eval(json_str)


def _check(content):
    """
    判断存在占位符 ${}
    :return:
    """
    if not isinstance(content, str):
        try:
            if '${' in str(content):
                return True
            else:
                return False
        except Exception as e:
            raise TransferException("类型转换失败！")


def testDataFile():
    import os
    return os.path.join(os.path.abspath("../.."), 'test_data')


def sysCommond():
    """
    通过命令行执行批量转换任务
    :return:
    """
    parser = argparse.ArgumentParser(description="批量转化yml")
    parser.add_argument("-path", "-p", help="文件夹path属性，必填")
    args = parser.parse_args()
    if len(args) <= 1:
        parser.error("缺少参数")
    path = args[-1]
    # for file in allYmlFile(path):
    #     yml2testcase(file)


if __name__ == '__main__':
    yml2testcase('index.yml')
